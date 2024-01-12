from django.shortcuts import render
from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import Group
from rest_framework.response import Response
from database.models import *
from .serializers import *
from Allauth.serializers import RegisterSerializer
from rest_framework import status
from .permissions import *
from rest_framework.permissions import IsAuthenticated , AllowAny,IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from Allauth.serializers import *
from django.db.models import Q
import openpyxl
from django.http import HttpResponse
from django.utils import timezone
# Create your views here.
from .permissions import IsSupervisor

class PostUserGroupResquest(generics.GenericAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = UpdateSerializer 
    def post(self, request ,  *args, **kwargs):
        serializer = self.get_serializer(data = request.data )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'request raise successfully' 
            })
        else:
            return Response(serializer.errors)

class GetGroupList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated , IsSupervisor ]
    serializer_class = GroupListSerializer
    def get(self, request):
        group_list = Group.objects.all()
        serializer = self.get_serializer(group_list , many = True).data
        return Response({'group_list': serializer})

class GetGroupRequestList(generics.ListAPIView):
    serializer_class = GetGroupRequestListSerializer
    permission_classes = [IsAuthenticated , IsAdmin | IsMOH]
    pagination_class = LimitOffsetPagination
    model = serializer_class.Meta.model
    filter_backends = (filters.SearchFilter,)


    def get_queryset(self):
        queryset = self.model.objects.filter( status=False   )

        search_terms = self.request.query_params.get('search', None )
        if search_terms:
            queryset = queryset.filter(
                Q(user__name__icontains=search_terms) |
                Q(username__icontains=search_terms) |
                Q(phoneNumber__icontains=search_terms) )
            
        return queryset
    
    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'status': 'success',
                                                'message': 'Data fetched successfully',
                                                'data': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 
                        'message': 'Data fetched successfully', 
                        'data': serializer.data})

class updateUserGroupRequest(generics.GenericAPIView):
    serializer_class = UpdateGroupRequest
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated , IsAdmin]


    def patch(self, request ,  id ,  *args, **kwargs):
        try:
            instance = UserApprovalRecords.objects.get(id=id)
        except:
            return Response({'status': 'error',
                            'message': 'deatils not found'}, status=400)
        serializer = self.get_serializer(instance , data = request.data , partial = True )
        if serializer.is_valid():
            serializer.save()
            return Response({"status" : "success" , 
                            "message" : "User group updated successfully"
                    },status=status.HTTP_201_CREATED)
        else:
            key, value = list(serializer.errors.items())[0]
            error_message = value[0]
            return Response({'message': error_message, 
                            'status' : 'error'}, status=400)

class UserCountsAPI(APIView):
    # permission_classes = [ IsAuthenticated, IsAdmin]
    def get(self, request, *args, **kwargs):
        all = CustomUser.objects.all()
        CHV_ASHA_count = all.filter(groups__name='CHV-ASHA').count()
        MO_count = all.filter(groups__name='mo').count()
        ANM_count = all.filter(groups__name='healthworker').count()
        return Response({
            'CHV_ASHA_count' : CHV_ASHA_count , 
            'MO_count' : MO_count , 
            'ANM_count' : ANM_count
        } , status = 200)
        
class InsertUsersByadmin(generics.GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated,]
    serializer_class = AddUserSerializer
    # parser_classes = [MultiPartParser]
    permission_classes = (IsAuthenticated , IsAdmin | IsSupervisor | IsMOH)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(serializer)
        try:
            if serializer.is_valid():
                
                group = Group.objects.get(name=serializer.validated_data.get("group"))
                
                user = serializer.save(is_active = True)
                customuser = serializer.validated_data
                data = RegisterSerializer(customuser, context=self.get_serializer_context()).data
                user.groups.add(group)
                addSupervisor = CustomUser.objects.filter(id= user.id).update(created_by_id = request.user.id)
                return Response({
                    "status": "success",
                    "message": "Successfully Inserted.",
                    "data": data,
                })
            else:
                key, value = list(serializer.errors.items())[0]
                # print(key , value)
                error_message = key + " ,"  + value[0]
                return Response({
                    "status": "error",
                    "message": error_message,
                  
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetDeactivatedUserList(generics.ListAPIView):
    permission_classes = [IsAuthenticated , IsAdmin]
    pagination_class = LimitOffsetPagination
    serializer_class = GetDeactivatedUserListSerializer
    model = serializer_class.Meta.model
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        ward_name = self.kwargs.get('ward_name')
        group = self.kwargs.get('group')

        queryset = self.model.objects.filter( is_active=False  , created_by__groups__name = 'MOH' , 
                                            userSections__healthPost__ward__wardName = ward_name , groups__name = group ).order_by("-created_date")

        search_terms = self.request.query_params.get('search', None )
        if search_terms:
            queryset = queryset.filter(
                Q(name__icontains=search_terms) |
                Q(username__icontains=search_terms) |
                Q(phoneNumber__icontains=search_terms) |
                Q(health_Post__healthPostName__icontains=search_terms) |
                Q(userSections__healthPost__healthPostName__icontains=search_terms) )
            
        return queryset
    
    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'status': 'success',
                                                'message': 'Data fetched successfully',
                                                'data': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 
                        'message': 'Data fetched successfully', 
                        'data': serializer.data})
    
class InsertUsersByMOH(generics.GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated,]
    serializer_class = AddUserByMOHSerializer
    # parser_classes = [MultiPartParser]
    permission_classes = (IsAuthenticated , IsMOH)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
       
        try:
            if serializer.is_valid():
                group = Group.objects.get(name=serializer.validated_data.get("group"))
                
                user = serializer.save()
                customuser = serializer.validated_data
                data = RegisterSerializer(customuser, context=self.get_serializer_context()).data
                user.groups.add(group)
                
                addSupervisor = CustomUser.objects.filter(id= user.id).update(created_by_id = request.user.id)
                return Response({
                    "status": "success",
                    "message": "Successfully Inserted.",
                    "data": data,
                })
            else:
                key, value = list(serializer.errors.items())[0]
                error_message = value[0]
                return Response({
                    "status": "error",
                    "message": error_message,
                  
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserDetails(generics.GenericAPIView):
    serializer_class  = UpdateUsersDetailsSerializer
    permission_classes = (IsAuthenticated , IsAdmin | IsSupervisor | IsMOH)
    # parser_classes = [MultiPartParser]


    def patch(self, request, pk):
        # print(request.data)
        try:
            instance = CustomUser.objects.get(pk=pk)
        except:
            return Response({'status': 'error',
                            'message': 'deatils not found'}, status=400)
        
        serializer = self.get_serializer(instance , data = request.data , partial = True )
        # print(serializer)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            return Response({"status" : "success" , 
                            "message" : "User details updated successfully"
                    },status=status.HTTP_201_CREATED)
        else:
            key, value = list(serializer.errors.items())[0]
            error_message = value[0]
            return Response({'message': error_message, 
                            'status' : 'error'}, status=400)
        
class deleteUser(generics.GenericAPIView):
    serializer_class = DeleteUserSerializer
    permission_classes = (IsAuthenticated , IsAdmin | IsSupervisor)

    def delete(self, request, id , *args, **kwargs):
        try:
            instance = CustomUser.objects.get(pk=id).delete()
            return Response({'status': 'success', 'message' : 'user deleted'}, status= status.HTTP_200_OK)
        except:
            return Response({'status': 'error',
                            'message': 'deatils not found'}, status=400)
    
class AdminChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    # model = CustomUser
    # permission_classes = (IsAuthenticated)
    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        try:
            obj = CustomUser.objects.get(id = id)
        except:
            return Response({'status': 'error',
                'message': 'user details not found'
            }, status= status.HTTP_400_BAD_REQUEST)
        return obj

    def update(self , request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("newpassword"))
            self.object.save()

            # sendOtp.objects.filter(registerUser_id = self.request.user.id).delete()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully'
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class userListAPI(generics.ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = CustomUserSerializer
    model = serializer_class.Meta.model
    # permission_classes = (IsAuthenticated , IsAdmin)
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self ):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        group = self.kwargs.get('group')
        
        ward_name = self.kwargs.get('ward_name')
        # section = self.model.objects.filter(groups__name = group, userSections__id = 239)
        # for i  in section:
        #     print(i.name)
        if group == 'mo':
            queryset = self.model.objects.filter(groups__name = group , dispensary__ward__wardName = ward_name ).order_by("-created_date")
        else:
            # queryset = self.model.objects.filter(groups__name = group , section__healthPost__ward__wardName = ward_name).order_by("-created_date")
            queryset = self.model.objects.filter(groups__name = group , userSections__healthPost__ward__wardName = ward_name).order_by("-created_date").distinct()

        search_terms = self.request.query_params.get('search', None )
        if search_terms:
            queryset = queryset.filter(
                Q(name__icontains=search_terms) |
                Q(username__icontains=search_terms) |
                Q(phoneNumber__icontains=search_terms) |
                Q(health_Post__healthPostName__icontains=search_terms) |
                Q(section__healthPost__healthPostName__icontains=search_terms) )
            
        return queryset
     
    def get(self, request, *args, **kwargs):
        
        queryset = self.get_queryset( )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'status': 'success',
                                                'message': 'Data fetched successfully',
                                                'data': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success',
                        'message': 'Data fetched successfully', 
                        'data': serializer.data})
    
class GetWardWiseSUerList(generics.ListAPIView):
    permission_classes = [IsAuthenticated ,IsMOH]
    pagination_class = LimitOffsetPagination
    serializer_class = CustomUserSerializer
    model = serializer_class.Meta.model
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        group = self.kwargs.get('group')
        # wardName = self.kwargs.get('ward')
        # print(group , wardName)
        ward_id= self.request.user.ward.id
        queryset = self.model.objects.filter(groups__name = group  , userSections__healthPost__ward__id = ward_id).order_by("-created_date").distinct()
   
        search_terms = self.request.query_params.get('search', None)
        if search_terms:
            queryset = queryset.filter(Q(section__healthPost__ward__wardName__icontains=search_terms)|
                                        Q(userSections__icontains=search_terms) |
                                        Q(phoneNumber__icontains=search_terms) |
                                        Q(health_Post__healthPostName__icontains=search_terms))
                                       
        return queryset
    
    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
     
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'status': 'success',
                                                'message': 'Data fetched successfully',
                                                'data': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success',
                        'message': 'Data fetched successfully', 
                        'data': serializer.data})

class  MOHDashboardView(generics.GenericAPIView):
    permission_classes= (IsAuthenticated , IsMOH)
    queryset = familyMembers.objects.all()
    FamilySurvey_count = familyHeadDetails.objects.all()
    CustomUser_queryset = CustomUser.objects.all()


    def get(self, request ,  *args, **kwargs):
        healthpost_id = self.request.query_params.get('healthpost_id', None)

        CHV_ASHA_count = self.CustomUser_queryset.filter(userSections__healthPost__ward__id = request.user.ward_id ,groups__name='CHV-ASHA').count()
        MO_count = self.CustomUser_queryset.filter(userSections__healthPost__ward__id = request.user.ward_id,groups__name='mo').count()
        ANM_count = self.CustomUser_queryset.filter(userSections__healthPost__ward__id = request.user.ward_id ,groups__name='healthworker').count()
        
        if healthpost_id:
            
            today = timezone.now().date() 
            total_citizen_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id =  request.user.ward_id , familySurveyor__userSections__healthPost__id = healthpost_id ).count()
            todays_citizen_count  = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id , familySurveyor__userSections__healthPost__id = healthpost_id , created_date__day= today.day).count()
            total_cbac_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , familySurveyor__userSections__healthPost__id = healthpost_id,age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__ward__id =  request.user.ward_id, user__userSections__healthPost__id = healthpost_id).count()
            total_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id , user__userSections__healthPost__id = healthpost_id).count()
            male =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , familySurveyor__userSections__healthPost__id = healthpost_id , gender = "M" ).count()
            female =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , familySurveyor__userSections__healthPost__id = healthpost_id , gender = "F" ).count()
            transgender =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , familySurveyor__userSections__healthPost__id = healthpost_id, gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  ,familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  ,familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 30 ).count()
            today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id ,user__userSections__healthPost__id = healthpost_id ,created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable = True).count()
            vulnerabel_70_Years = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = '70+ Years').count()
            vulnerabel_Physically_handicapped = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Physically Handicapped').count()
            vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
            vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Elderly and alone at home').count()
            vulnerabel_any_other_reason = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Any other reason').count()

            blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id ,familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Home').count()
            blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id ,familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Center').count()
            denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id ,familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'AMO').count()
            denieded_by_mo_individual = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, familySurveyor__userSections__healthPost__id = healthpost_id,bloodCollectionLocation = 'Individual Itself').count()
            Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id,familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
            Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id ,familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
            Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
            Referral_choice_Referral_to_Medical_College = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Medical College for management of Complication').count()
            Referral_choice_Referral_to_Private_facility = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Private facility').count()
            hypertension = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id ,  familySurveyor__userSections__healthPost__id = healthpost_id ,bloodPressure__gte = 140).count()

            total_LabTestAdded = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id  , isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , isLabTestReportGenerated = True).count()

            Questionnaire_queryset = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id ,  familySurveyor__userSections__healthPost__id = healthpost_id , Questionnaire__isnull=False)
            total_tb_count = 0
            total_diabetes = 0
            total_breast_cancer = 0 
            total_oral_cancer = 0 
            total_cervical_cancer =0
            total_COPD_count = 0 
            toatal_communicable  = 0 
            total_eye_problem = 0 
            total_Alzheimers = 0 
            total_ent_problem = 0
            
            for record in Questionnaire_queryset:
                part_e = record.Questionnaire.get(('part_e' , []))
                communicable = 0 
                for question in part_e[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        communicable += 1
                        break
                
            for record in Questionnaire_queryset:
                part_c =  record.Questionnaire.get('part_c', []) 
                COPD = 0 
                for question in part_c[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        COPD += 1
                        break
            for record in Questionnaire_queryset:
                part_b = record.Questionnaire.get('part_b', []) 
                tb_count = 0
                diabetes = 0 
                breast_cancer = 0 
                oral_cancer = 0
                cervical_cancer = 0
                eye_problem = 0
                ent = 0 
                for question in part_b[:10]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        tb_count += 1
                        break
                for question in part_b[12:16]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        eye_problem += 1
                        break
                for question in part_b[10:12]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        diabetes += 1
                        break
                for question in part_b[33:36]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        breast_cancer += 1
                        break
                for question in part_b[18:25]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        oral_cancer += 1
                        break

                for question in part_b[36:40]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        cervical_cancer += 1
                        break

                for question in part_b[22:23]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_problem += ent

        else:
            today = timezone.now().date() 
            ward = request.user.ward_id
            total_citizen_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  ).count()
            todays_citizen_count  = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id , created_date__day= today.day).count()
            total_cbac_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__ward__id =  request.user.ward_id).count()
            total_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id).count()
            male =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "M" ).count()
            female =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "F" ).count()
            transgender =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 30 ).count()
            today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id , created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable = True).count()
            vulnerabel_70_Years = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = '70+ Years').count()
            vulnerabel_Physically_handicapped = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Physically Handicapped').count()
            vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
            vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Elderly and alone at home').count()
            vulnerabel_any_other_reason = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Any other reason').count()

            blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodCollectionLocation = 'Home').count()
            blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodCollectionLocation = 'Center').count()
            denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodCollectionLocation = 'AMO').count()
            denieded_by_mo_individual = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, bloodCollectionLocation = 'Individual Itself').count()
            Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
            Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
            Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
            Referral_choice_Referral_to_Medical_College = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, referels__choice = 'Referral to Medical College for management of Complication').count()
            Referral_choice_Referral_to_Private_facility = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, referels__choice = 'Referral to Private facility').count()
            hypertension = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodPressure__gte = 140).count()

            total_LabTestAdded = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id  , isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , isLabTestReportGenerated = True).count()
            
            Questionnaire_queryset = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id  , Questionnaire__isnull=False)
            total_tb_count = 0
            total_diabetes = 0
            total_breast_cancer = 0 
            total_oral_cancer = 0 
            total_cervical_cancer =0
            total_COPD_count = 0 
            toatal_communicable  = 0 
            total_eye_problem = 0 
            total_Alzheimers = 0 
            total_ent_problem = 0 
            
            for record in Questionnaire_queryset:
                part_e = record.Questionnaire.get(('part_e' , []))
                communicable = 0 
                for question in part_e[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        communicable += 1
                        break
                
            for record in Questionnaire_queryset:
                part_c =  record.Questionnaire.get('part_c', []) 
                COPD = 0 
                for question in part_c[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        COPD += 1
                        break
            for record in Questionnaire_queryset:
                part_b = record.Questionnaire.get('part_b', []) 
                tb_count = 0
                diabetes = 0 
                breast_cancer = 0 
                oral_cancer = 0
                cervical_cancer = 0
                eye_problem = 0
                ent = 0 
                for question in part_b[:10]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        tb_count += 1
                        break
                for question in part_b[12:16]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        eye_problem += 1
                        break
                for question in part_b[10:12]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        diabetes += 1
                        break
                for question in part_b[33:36]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        breast_cancer += 1
                        break
                for question in part_b[18:25]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        oral_cancer += 1
                        break

                for question in part_b[36:40]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        cervical_cancer += 1
                        break

                for question in part_b[22:23]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_problem += ent

        return Response({
            'CHV_ASHA_count' : CHV_ASHA_count , 
            'MO_count' : MO_count , 
            'ANM_count' : ANM_count , 
            'total_count' : total_citizen_count ,
            'todays_count' : todays_citizen_count ,
            'partial_survey_count' : partial_survey_count ,
            'total_family_count' : total_family_count ,
            'today_family_count' : today_family_count,
            'total_cbac_count' : total_cbac_count ,
            'citizen_above_60' : citizen_above_60,
            'citizen_above_30' : citizen_above_30,
            'TestReportGenerated' : TestReportGenerated,
            'total_LabTestAdded' : total_LabTestAdded,
            "male" : male,
            "female" : female,
            "transgender" : transgender,
            'diabetes' : total_diabetes,
            'hypertension' : hypertension ,
            'oral_Cancer' : total_oral_cancer ,
            'cervical_cancer' : total_cervical_cancer ,
            'copd' : total_COPD_count,
            'eye_disorder' : total_eye_problem , 
            'ent_disorder' : total_ent_problem , 
            'asthama' : 0 ,
            'Alzheimers' : 0 ,
            'tb' : total_tb_count ,
            'breast_cancer' : total_breast_cancer,
            'other_communicable_dieases' : toatal_communicable ,
            'blood_collected_home' : blood_collected_home , 
            'blood_collected_center' : blood_collected_center ,
            'denieded_by_mo_count' : denieded_by_mo_count , 
            'denieded_by_mo_individual' : denieded_by_mo_individual ,
            'Referral_choice_Referral_to_Mun_Dispensary' : Referral_choice_Referral_to_Mun_Dispensary ,
            'Referral_choice_Referral_to_HBT_polyclinic': Referral_choice_Referral_to_HBT_polyclinic ,
            'Referral_choice_Referral_to_Peripheral_Hospital': Referral_choice_Referral_to_Peripheral_Hospital ,
            'Referral_choice_Referral_to_Medical_College': Referral_choice_Referral_to_Medical_College ,
            'Referral_choice_Referral_to_Private_facility': Referral_choice_Referral_to_Private_facility ,
            'total_vulnerabel' : total_vulnerabel , 
            'vulnerabel_70_Years' : vulnerabel_70_Years , 
            'vulnerabel_Physically_handicapped' : vulnerabel_Physically_handicapped , 
            'vulnerabel_completely_paralyzed_or_on_bed' : vulnerabel_completely_paralyzed_or_on_bed , 
            'vulnerabel_elderly_and_alone_at_home' : vulnerabel_elderly_and_alone_at_home , 
            'vulnerabel_any_other_reason' : vulnerabel_any_other_reason , 
                
                } , status= 200)
            
class DownloadHealthpostwiseUserList(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsSupervisor ]

    def get(self, request, id ,  *args, **kwargs ,):
        data_list = [['name','memberId', 'mobileNo','gender' , 'Age', 'familyHead', 'familySurveyor',
                      'aadharCard', 'abhaId' , 'bloodCollectionLocation' , 'CBAC_Score' , 'Survey Date' , 'Status' , 'DeniedBy' ]]

        healthpost_related_user = familyMembers.objects.filter(familySurveyor__section__healthPost__id = id)
        for i in  healthpost_related_user:
            data_list.append([
                i.name , i.memberId ,  i.mobileNo, i.gender , i.age , i.familyHead.name , i.familySurveyor.name ,
                 i.aadharCard , i.abhaId , i.bloodCollectionLocation , i.cbacScore , i.created_date.strftime('%d/%m/%Y %I:%M:%S %p'),
                i.generalStatus , i.deniedBy
            ])

        wb = openpyxl.Workbook()
        ws = wb.active
        for row in data_list:   
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
        wb.save(response)
        return response
    
class DownloadWardwiseUserList(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsSupervisor ]

    def get(self, request, id ,  *args, **kwargs ,):
        data_list = [['name','memberId', 'mobileNo','gender' , 'Age', 'familyHead', 'familySurveyor',
                      'aadharCard', 'abhaId' , 'bloodCollectionLocation' , 'CBAC_Score' , 'Survey Date' , 'Status' , 'DeniedBy' ]]

        healthpost_related_user = familyMembers.objects.filter(familySurveyor__section__healthPost__ward__id = id)
        
        for i in  healthpost_related_user:
            data_list.append([
                i.name , i.memberId ,  i.mobileNo, i.gender , i.age , i.familyHead.name , i.familySurveyor.name ,
                 i.aadharCard , i.abhaId , i.bloodCollectionLocation , i.cbacScore , i.created_date.strftime('%d/%m/%Y %I:%M:%S %p'),
                i.generalStatus , i.deniedBy
            ])

        wb = openpyxl.Workbook()
        ws = wb.active
        for row in data_list:   
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'
        wb.save(response)
        return response
    
class DownloadDispensarywiseUserList(generics.GenericAPIView):

    # permission_classes = [IsAuthenticated , IsAdmin | IsSupervisor ]

    def get(self, request, id ,  *args, **kwargs ,):
        data_list = [['name','memberId', 'mobileNo','gender' , 'Age', 'familyHead', 'familySurveyor',
                      'aadharCard', 'abhaId' , 'bloodCollectionLocation' , 'CBAC_Score' , 'Survey Date' , 'Status' , 'DeniedBy' ]]

        healthpost_related_user = familyMembers.objects.filter(familySurveyor__dispensary__id = id)
        dispensary_name = dispensary.objects.get(id = id )
        
        for i in  healthpost_related_user:
            dispensary_name = i.familySurveyor.dispensary.dispensaryName
            data_list.append([
                i.name , i.memberId ,  i.mobileNo, i.gender , i.age , i.familyHead.name , i.familySurveyor.name ,
                 i.aadharCard , i.abhaId , i.bloodCollectionLocation , i.cbacScore , i.created_date.strftime('%d/%m/%Y %I:%M:%S %p'),
                i.generalStatus , i.deniedBy , 
            ])

        wb = openpyxl.Workbook()
        ws = wb.active
        for row in data_list:   
            ws.append(row)
        
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{dispensary_name.dispensaryName}.xlsx"'
        wb.save(response)
        return response
 

from excel_response import ExcelResponse

class MOHDashboardExportView(generics.GenericAPIView):
    
    permission_classes = ( IsAuthenticated , IsMOH )
    FamilySurvey_count = familyHeadDetails.objects.all()
    CustomUser_queryset = CustomUser.objects.all()

    def get_queryset(self ):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        queryset = familyMembers.objects.all()
        
        return queryset

    def get(self, request, *args, **kwargs):
        
        today = timezone.now().date() 
        ward = request.user.ward.id
        total_citizen_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward.id  ).count()

        todays_citizen_count  = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id =  request.user.ward.id , created_date__day= today.day).count()
        total_cbac_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id =  request.user.ward.id , age__gte = 30 , cbacRequired = True).count()
        partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__ward__id =   request.user.ward.id).count()
        total_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id =  request.user.ward.id).count()
        male =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id =  request.user.ward.id  , gender = "M" ).count()
        female =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "F" ).count()
        transgender =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "O" ).count()
        citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 60 ).count()
        citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 30 ).count()
        today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id , created_date__day = today.day ).count()

        total_vulnerabel = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable = True).count()
        vulnerabel_70_Years = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = '70+ Years').count()
        vulnerabel_Physically_handicapped = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Physically Handicapped').count()
        vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
        vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Elderly and alone at home').count()
        vulnerabel_any_other_reason = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Any other reason').count()

        blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodCollectionLocation = 'Home').count()
        blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodCollectionLocation = 'Center').count()
        denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodCollectionLocation = 'AMO').count()
        denieded_by_mo_individual = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, bloodCollectionLocation = 'Individual Itself').count()
        Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
        Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
        Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
        Referral_choice_Referral_to_Medical_College = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, referels__choice = 'Referral to Medical College for management of Complication').count()
        Referral_choice_Referral_to_Private_facility = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id, referels__choice = 'Referral to Private facility').count()
        hypertension = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , bloodPressure__gte = 140).count()

        total_LabTestAdded = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id  , isLabTestAdded = True).count()
        TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , isLabTestReportGenerated = True).count()
        
        Questionnaire_queryset = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id  , Questionnaire__isnull=False)

        total_tb_count = 0
        total_diabetes = 0
        total_breast_cancer = 0 
        total_oral_cancer = 0 
        total_cervical_cancer =0
        total_COPD_count = 0 
        toatal_communicable  = 0 
        total_eye_problem = 0 
        total_Alzheimers = 0 
        total_ent_problem = 0 
        
        for record in Questionnaire_queryset:
            part_e = record.Questionnaire.get(('part_e' , []))
            communicable = 0 
            for question in part_e[0:]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    communicable += 1
                    break
            
        for record in Questionnaire_queryset:
            part_c =  record.Questionnaire.get('part_c', []) 
            COPD = 0 
            for question in part_c[0:]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    COPD += 1
                    break
        for record in Questionnaire_queryset:
            part_b = record.Questionnaire.get('part_b', []) 
            tb_count = 0
            diabetes = 0 
            breast_cancer = 0 
            oral_cancer = 0
            cervical_cancer = 0
            eye_problem = 0
            ent = 0 
            for question in part_b[:10]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    tb_count += 1
                    break
            for question in part_b[12:16]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    eye_problem += 1
                    break
            for question in part_b[10:12]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    diabetes += 1
                    break
            for question in part_b[33:36]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    breast_cancer += 1
                    break
            for question in part_b[18:25]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    oral_cancer += 1
                    break

            for question in part_b[36:40]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    cervical_cancer += 1
                    break

            for question in part_b[22:23]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    ent += 1
                    break

            total_tb_count += tb_count
            total_diabetes += diabetes
            total_breast_cancer += breast_cancer
            total_oral_cancer += oral_cancer
            total_cervical_cancer += cervical_cancer
            total_COPD_count += COPD
            toatal_communicable += communicable
            total_eye_problem += eye_problem
            total_ent_problem += ent

        data = [
            {
                'Total Count': total_citizen_count,
                'Todays Count': todays_citizen_count,
                'Partial Survey Count': partial_survey_count,
                'Total Family Count': total_family_count,
                'Today Family Count': today_family_count,
                'Total CBAC Count': total_cbac_count,
                'Citizen Above 60': citizen_above_60,
                'Citizen Above 30': citizen_above_30,
                'total LabTestAdded' : total_LabTestAdded,
                'TestReportGenerated' : TestReportGenerated,
                'Male': male,
                'Female': female,
                'Transgender': transgender,
                'Diabetes': total_diabetes,
                'Hypertension': hypertension,
                'Oral Cancer': total_oral_cancer,
                'Cervical Cancer': total_cervical_cancer,
                'COPD': total_COPD_count,
                'Eye Problem': total_eye_problem,
                'Asthma': 0,
                'Alzheimers': 0,
                'TB': total_tb_count,
                'Breast Cancer': total_breast_cancer,
                'Communicable': toatal_communicable,
                'Blood Collected Home': blood_collected_home,
                'Blood Collected Center': blood_collected_center,
                'Denied by MO Count': denieded_by_mo_count,
                'Denied by MO Individual': denieded_by_mo_individual,
                'Referral choice Referral to Mun Dispensary': Referral_choice_Referral_to_Mun_Dispensary,
                'Referral_choice_Referral_to_HBT_polyclinic': Referral_choice_Referral_to_HBT_polyclinic,
                'Referral_choice_Referral_to_Peripheral_Hospital': Referral_choice_Referral_to_Peripheral_Hospital,
                'Referral_choice_Referral_to_Medical_College': Referral_choice_Referral_to_Medical_College,
                'Referral_choice_Referral_to_Private_facility': Referral_choice_Referral_to_Private_facility,
                'Total Vulnerable': total_vulnerabel,
                'Vulnerable 70+ Years': vulnerabel_70_Years,
                'Vulnerable Physically Handicapped': vulnerabel_Physically_handicapped,
                'Vulnerable Completely Paralyzed or On Bed': vulnerabel_completely_paralyzed_or_on_bed,
                'Vulnerable Elderly and Alone at Home': vulnerabel_elderly_and_alone_at_home,
                'Vulnerable Any Other Reason': vulnerabel_any_other_reason,
            }
        ]


        response = ExcelResponse(data, status=200)
        response['Content-Disposition'] = 'attachment; filename="moh_dashboard_data.xlsx"'
        # Use DjangoExcelResponse to export the data in Excel format
        return response
    
class  AdminDashboardView(generics.GenericAPIView):
    permission_classes= (IsAuthenticated , IsAdmin)
    queryset = familyMembers.objects.all()
    FamilySurvey_count = familyHeadDetails.objects.all()
    CustomUser_queryset = CustomUser.objects.all()


    def get(self, request ,  *args, **kwargs):
        healthpost_id = self.request.query_params.get('healthpost_id', None)
        wardId = self.request.query_params.get('wardId', None)
        

        CHV_ASHA_count = self.CustomUser_queryset.filter(userSections__healthPost__ward__id = request.user.ward_id ,groups__name='CHV-ASHA').count()
        MO_count = self.CustomUser_queryset.filter(userSections__healthPost__ward__id = request.user.ward_id,groups__name='mo').count()
        ANM_count = self.CustomUser_queryset.filter(userSections__healthPost__ward__id = request.user.ward_id ,groups__name='healthworker').count()
        
        if healthpost_id:
            
            today = timezone.now().date() 
            total_citizen_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id ).count()
            todays_citizen_count  = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , created_date__day= today.day).count()
            total_cbac_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id,age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__id = healthpost_id).count()
            total_family_count = self.FamilySurvey_count.filter( user__userSections__healthPost__id = healthpost_id).count()
            male =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , gender = "M" ).count()
            female =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , gender = "F" ).count()
            transgender =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 30 ).count()
            today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__id = healthpost_id ,created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter( vulnerable = True).count()
            vulnerabel_70_Years = self.get_queryset().filter( vulnerable_choices__choice = '70+ Years').count()
            vulnerabel_Physically_handicapped = self.get_queryset().filter( vulnerable_choices__choice = 'Physically Handicapped').count()
            vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
            vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter( vulnerable_choices__choice = 'Elderly and alone at home').count()
            vulnerabel_any_other_reason = self.get_queryset().filter( vulnerable_choices__choice = 'Any other reason').count()

            blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Home').count()
            blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Center').count()
            denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'AMO').count()
            denieded_by_mo_individual = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id,bloodCollectionLocation = 'Individual Itself').count()
            Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
            Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
            Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
            Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Medical College for management of Complication').count()
            Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Private facility').count()
            hypertension = self.get_queryset().filter(  familySurveyor__userSections__healthPost__id = healthpost_id ,bloodPressure__gte = 140).count()

            total_LabTestAdded = self.get_queryset().filter( isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter( isLabTestReportGenerated = True).count()

            Questionnaire_queryset = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , Questionnaire__isnull=False)
            total_tb_count = 0
            total_diabetes = 0
            total_breast_cancer = 0 
            total_oral_cancer = 0 
            total_cervical_cancer =0
            total_COPD_count = 0 
            toatal_communicable  = 0 
            total_eye_problem = 0 
            total_Alzheimers = 0 
            total_ent_problem = 0 
            
            for record in Questionnaire_queryset:
                part_e = record.Questionnaire.get(('part_e' , []))
                communicable = 0 
                for question in part_e[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        communicable += 1
                        break
                
            for record in Questionnaire_queryset:
                part_c =  record.Questionnaire.get('part_c', []) 
                COPD = 0 
                for question in part_c[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        COPD += 1
                        break
            for record in Questionnaire_queryset:
                part_b = record.Questionnaire.get('part_b', []) 
                tb_count = 0
                diabetes = 0 
                breast_cancer = 0 
                oral_cancer = 0
                cervical_cancer = 0
                eye_problem = 0
                ent =0
                for question in part_b[:10]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        tb_count += 1
                        break
                for question in part_b[12:16]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        eye_problem += 1
                        break
                for question in part_b[10:12]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        diabetes += 1
                        break
                for question in part_b[33:36]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        breast_cancer += 1
                        break
                for question in part_b[18:25]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        oral_cancer += 1
                        break

                for question in part_b[36:40]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        cervical_cancer += 1
                        break
                for question in part_b[22:23]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_problem += ent
        elif wardId :
            today = timezone.now().date() 
            total_citizen_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = wardId ).count()
            todays_citizen_count  = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = wardId, created_date__day= today.day).count()
            total_cbac_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = wardId  ,age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__ward__id =  wardId).count()
            total_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = wardId).count()
            male =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = wardId , gender = "M" ).count()
            female =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id =wardId  , gender = "F" ).count()
            transgender =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = wardId ,  gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id =wardId  , age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = wardId , age__gte = 30 ).count()
            today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = wardId  ,created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , vulnerable = True).count()
            vulnerabel_70_Years = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId, vulnerable_choices__choice = '70+ Years').count()
            vulnerabel_Physically_handicapped = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  =wardId , vulnerable_choices__choice = 'Physically Handicapped').count()
            vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
            vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , vulnerable_choices__choice = 'Elderly and alone at home').count()
            vulnerabel_any_other_reason = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId, vulnerable_choices__choice = 'Any other reason').count()

            blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , bloodCollectionLocation = 'Home').count()
            blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  =wardId , bloodCollectionLocation = 'Center').count()
            denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , bloodCollectionLocation = 'AMO').count()
            denieded_by_mo_individual = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId, bloodCollectionLocation = 'Individual Itself').count()
            Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  =wardId,referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
            Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId ,referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
            Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId, referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
            Referral_choice_Referral_to_Medical_College = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId, referels__choice = 'Referral to Medical College for management of Complication').count()
            Referral_choice_Referral_to_Private_facility = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId, referels__choice = 'Referral to Private facility').count()
            hypertension = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId,  bloodPressure__gte = 140).count()

            total_LabTestAdded = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  =wardId , isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , isLabTestReportGenerated = True).count()

            Questionnaire_queryset = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = wardId , Questionnaire__isnull=False)
            total_tb_count = 0
            total_diabetes = 0
            total_breast_cancer = 0 
            total_oral_cancer = 0 
            total_cervical_cancer =0
            total_COPD_count = 0 
            toatal_communicable  = 0 
            total_eye_problem = 0 
            total_Alzheimers = 0 
            total_ent_problem = 0 
            
            for record in Questionnaire_queryset:
                part_e =  record.Questionnaire.get('part_c', []) 
                communicable = 0 
                for question in part_e[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        communicable += 1
                        break
                
            for record in Questionnaire_queryset:
                part_c =  record.Questionnaire.get('part_c', []) 
                COPD = 0 
                for question in part_c[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        COPD += 1
                        break
            for record in Questionnaire_queryset:
                part_b = record.Questionnaire.get('part_b', []) 
                tb_count = 0
                diabetes = 0 
                breast_cancer = 0 
                oral_cancer = 0
                cervical_cancer = 0
                eye_problem = 0
                ent = 0 
                for question in part_b[:10]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        tb_count += 1
                        break
                for question in part_b[12:16]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        eye_problem += 1
                        break
                for question in part_b[10:12]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        diabetes += 1
                        break
                for question in part_b[33:36]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        breast_cancer += 1
                        break
                for question in part_b[18:25]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        oral_cancer += 1
                        break

                for question in part_b[36:40]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        cervical_cancer += 1
                        break

                for question in part_b[22:23]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_problem += ent
            

        else:
            today = timezone.now().date() 
            ward = request.user.ward_id
            total_citizen_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  ).count()
            todays_citizen_count  = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id , created_date__day= today.day).count()
            total_cbac_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__ward__id =  request.user.ward_id).count()
            total_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id).count()
            male =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "M" ).count()
            female =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "F" ).count()
            transgender =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id = request.user.ward_id  , age__gte = 30 ).count()
            today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__ward__id = request.user.ward_id , created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable = True).count()
            vulnerabel_70_Years = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = '70+ Years').count()
            vulnerabel_Physically_handicapped = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Physically Handicapped').count()
            vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
            vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Elderly and alone at home').count()
            vulnerabel_any_other_reason = self.get_queryset().filter(familySurveyor__userSections__healthPost__ward__id  = request.user.ward_id , vulnerable_choices__choice = 'Any other reason').count()

            blood_collected_home = self.get_queryset().filter(bloodCollectionLocation = 'Home').count()
            blood_collected_center = self.get_queryset().filter(bloodCollectionLocation = 'Center').count()
            denieded_by_mo_count = self.get_queryset().filter( bloodCollectionLocation = 'AMO').count()
            denieded_by_mo_individual = self.get_queryset().filter( bloodCollectionLocation = 'Individual Itself').count()
            Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter( referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
            Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter( referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
            Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
            Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( referels__choice = 'Referral to Medical College for management of Complication').count()
            Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( referels__choice = 'Referral to Private facility').count()
            hypertension = self.get_queryset().filter( bloodPressure__gte = 140).count()

            total_LabTestAdded = self.get_queryset().filter( isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter(isLabTestReportGenerated = True).count()
            
            Questionnaire_queryset = self.get_queryset().filter(Questionnaire__isnull=False)
            total_tb_count = 0
            total_diabetes = 0
            total_breast_cancer = 0 
            total_oral_cancer = 0 
            total_cervical_cancer =0
            total_COPD_count = 0 
            toatal_communicable  = 0 
            total_eye_problem = 0 
            total_Alzheimers = 0 
            total_ent_problem = 0 
            
            for record in Questionnaire_queryset:
                part_e = record.Questionnaire.get('part_e', []) 
                communicable = 0 
                for question in part_e[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        communicable += 1
                        break
                
            for record in Questionnaire_queryset:
                part_c =  record.Questionnaire.get('part_c', []) 
                COPD = 0 
                for question in part_c[0:]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        COPD += 1
                        break
            for record in Questionnaire_queryset:
                part_b = record.Questionnaire.get('part_b', []) 
                tb_count = 0
                diabetes = 0 
                breast_cancer = 0 
                oral_cancer = 0
                cervical_cancer = 0
                eye_problem = 0
                ent = 0 
                for question in part_b[:10]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        tb_count += 1
                        break
                for question in part_b[12:16]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        eye_problem += 1
                        break
                for question in part_b[10:12]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        diabetes += 1
                        break
                for question in part_b[33:36]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        breast_cancer += 1
                        break
                for question in part_b[18:25]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        oral_cancer += 1
                        break

                for question in part_b[36:40]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        cervical_cancer += 1
                        break

                for question in part_b[22:23]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_problem += ent

        return Response({
            'CHV_ASHA_count' : CHV_ASHA_count , 
            'MO_count' : MO_count , 
            'ANM_count' : ANM_count , 
            'total_count' : total_citizen_count ,
            'todays_count' : todays_citizen_count ,
            'partial_survey_count' : partial_survey_count ,
            'total_family_count' : total_family_count ,
            'today_family_count' : today_family_count,
            'total_cbac_count' : total_cbac_count ,
            'citizen_above_60' : citizen_above_60,
            'citizen_above_30' : citizen_above_30,
            'TestReportGenerated' : TestReportGenerated,
            'total_LabTestAdded' : total_LabTestAdded,
            "male" : male,
            "female" : female,
            "transgender" : transgender,
            'diabetes' : total_diabetes,
            'hypertension' : hypertension ,
            'oral_Cancer' : total_oral_cancer ,
            'cervical_cancer' : total_cervical_cancer ,
            'copd' : total_COPD_count,
            'eye_disorder' : total_eye_problem , 
            'ent_disorder' : total_ent_problem , 
            'asthama' : 0 ,
            'Alzheimers' : 0 ,
            'tb' : total_tb_count ,
            'breast_cancer' : total_breast_cancer,
            'other_communicable_dieases' : toatal_communicable ,
            'blood_collected_home' : blood_collected_home , 
            'blood_collected_center' : blood_collected_center ,
            'denieded_by_mo_count' : denieded_by_mo_count , 
            'denieded_by_mo_individual' : denieded_by_mo_individual ,
            'Referral_choice_Referral_to_Mun_Dispensary' : Referral_choice_Referral_to_Mun_Dispensary ,
            'Referral_choice_Referral_to_HBT_polyclinic': Referral_choice_Referral_to_HBT_polyclinic ,
            'Referral_choice_Referral_to_Peripheral_Hospital': Referral_choice_Referral_to_Peripheral_Hospital ,
            'Referral_choice_Referral_to_Medical_College': Referral_choice_Referral_to_Medical_College ,
            'Referral_choice_Referral_to_Private_facility': Referral_choice_Referral_to_Private_facility ,
            'total_vulnerabel' : total_vulnerabel , 
            'vulnerabel_70_Years' : vulnerabel_70_Years , 
            'vulnerabel_Physically_handicapped' : vulnerabel_Physically_handicapped , 
            'vulnerabel_completely_paralyzed_or_on_bed' : vulnerabel_completely_paralyzed_or_on_bed , 
            'vulnerabel_elderly_and_alone_at_home' : vulnerabel_elderly_and_alone_at_home , 
            'vulnerabel_any_other_reason' : vulnerabel_any_other_reason , 
                
                } , status= 200)