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
                print(serializer.validated_data.get("userSections"))
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
                print(key , value)
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
                                            section__healthPost__ward__wardName = ward_name , groups__name = group ).order_by("-created_date")

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
    parser_classes = [MultiPartParser]


    def patch(self, request, pk):
        try:
            instance = CustomUser.objects.get(pk=pk)
        except:
            return Response({'status': 'error',
                            'message': 'deatils not found'}, status=400)
        
        serializer = self.get_serializer(instance , data = request.data , partial = True )
        print(serializer.Meta.fields)
        if serializer.is_valid():
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
    
        if group == 'mo':
            queryset = self.model.objects.filter(groups__name = group , dispensary__ward__wardName = ward_name ).order_by("-created_date")
        else:
            queryset = self.model.objects.filter(groups__name = group , section__healthPost__ward__wardName = ward_name).order_by("-created_date")

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
        queryset = self.model.objects.filter(groups__name = group  , section__healthPost__ward__id = ward_id).order_by("-created_date")
   
        search_terms = self.request.query_params.get('search', None)
        if search_terms:
            queryset = queryset.filter(Q(section__healthPost__ward__wardName__icontains=search_terms)|
                                        Q(username__icontains=search_terms) |
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
    def get(self, request, *args, **kwargs):

       
        today = timezone.now().date() 
        ward = request.user.ward_id
        total_citizen_count = self.get_queryset().filter(familySurveyor__section__healthPost__ward__id = request.user.ward_id  ).count()
        todays_citizen_count  = self.get_queryset().filter(familySurveyor__section__healthPost__ward__id = request.user.ward_id , created_date__day= today.day).count()
        total_cbac_count = self.get_queryset().filter(familySurveyor__section__healthPost__ward__id = request.user.ward_id  , age__gte = 30 , cbacRequired = True).count()
        partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__section__healthPost__ward__id =  request.user.ward_id).count()
        total_family_count = self.FamilySurvey_count.filter(user__section__healthPost__ward__id = request.user.ward_id).count()
        citizen_above_60 =  self.get_queryset().filter(familySurveyor__section__healthPost__ward__id = request.user.ward_id  , age__gte = 60 ).count()
        citizen_above_30 =  self.get_queryset().filter(familySurveyor__section__healthPost__ward__id = request.user.ward_id  , age__gte = 30 ).count()
        today_family_count = self.FamilySurvey_count.filter(user__section__healthPost__ward__id = request.user.ward_id , created_date__day = today.day ).count()

        return Response({
            'total_count' : total_citizen_count ,
            'todays_count' : todays_citizen_count ,
            'partial_survey_count'  : partial_survey_count ,
            'total_family_count' : total_family_count ,
            'today_family_count' : today_family_count,
            'total_cbac_count' : total_cbac_count ,
            'citizen_above_60' : citizen_above_60,
            'citizen_above_30' : citizen_above_30, } , status= 200)
            
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
 
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def MoHDashboard(request):

    # wardId = request.GET.get('wardId')
    healthPostId = request.GET.get('healthPostId')
    UserId = request.GET.get('UserId')
    gender = request.GET.get('gender')
    # female = request.GET.get('female')
    # Determine user's group (if authenticated)
    
    group = None
    if request.user.is_authenticated:
        group = request.user.groups.values_list("name", flat=True).first()
        data = {}
        wardId =  request.user.ward.id
        if gender:
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender=gender).count()
            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
   
            data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()

            if healthPostId:
                    #Data For  Ward and HealthPost Filter
                data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId ).count()
                data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender=gender,area__healthPost_id=healthPostId).count()
                data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["NoOfAbhaIdGenerated"] = 0
                data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
    
                data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

                data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                
            if UserId:
                    #Data For  Ward and HealthPost Filter and User Id Filter
                data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,user_id=UserId ).count()
                data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender=gender,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["NoOfAbhaIdGenerated"] = 0
                data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
    
                data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

                data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
        else:
            #Data For Only Ward Filter
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__healthPost__ward_id  =wardId).count()
   
            data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__healthPost__ward_id  =wardId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__healthPost__ward_id  =wardId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",familyHead__area__healthPost__ward_id  =wardId).count()

            if healthPostId:
                    #Data For  Ward and HealthPost Filter
                data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId ).count()
                data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["NoOfAbhaIdGenerated"] = 0
                data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
    
                data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

                data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
                
            if UserId:
                    #Data For  Ward and HealthPost Filter and User Id Filter
                data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,user_id=UserId ).count()
                data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["NoOfAbhaIdGenerated"] = 0
                data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
    
                data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

                data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
                data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
        

        return Response({
            'status': 'success',
            'message': 'Successfully Fetched',
            'data': data,
        })

# @permission_classes((IsAuthenticated,))
@api_view(['GET'])
def AdminDashboard(request):

    wardId = request.GET.get('wardId')
    healthPostId = request.GET.get('healthPostId')
    UserId = request.GET.get('UserId')
    gender = request.GET.get('gender')
    # female = request.GET.get('female')
    # Determine user's group (if authenticated)
    
    # group = None
    # if request.user.is_authenticated:
    #     group = request.user.groups.values_list("name", flat=True).first()
    data = {}
    data["TotalMoCount"] = CustomUser.objects.filter(groups__id=12).count()
    data["TotalChvAshaCount"] = CustomUser.objects.filter(groups__id=13).count()
    data["TotalHealthWorkerCount"] = CustomUser.objects.filter(groups__id=4).count()

    # wardId =  request.user.ward.id
    if gender:
        data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.all().count()
        data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(gender=gender).count()
        data["NoOfMaleEnrolled"] = familyMembers.objects.filter(gender="M").count()
        data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(gender="F").count()

        data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender).count()
        data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender).count()
        data["NoOfAbhaIdGenerated"] = 0
        data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender).count()

        # data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender).count()
        data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,gender=gender).count()

        data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender).count()
        data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender).count()

        data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender).count()
        data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender).count()
        data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender).count()

        if wardId:
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender=gender).count()
            data["NoOfMaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="M").count()
            data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="F").count()


            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()

            # data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()

            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender,familyHead__area__healthPost__ward_id  =wardId).count()

        if healthPostId:
            #Data For  Ward and HealthPost Filter
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender=gender,area__healthPost_id=healthPostId).count()

            data["NoOfMaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="M",area__healthPost_id=healthPostId).count()
            data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="F",area__healthPost_id=healthPostId).count()


            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

            # data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            
        if UserId:
            #Data For  Ward and HealthPost Filter and User Id Filter
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,user_id=UserId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender=gender,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoOfMaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="M",area__healthPost_id=healthPostId,user_id=UserId).count()
            data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="F",area__healthPost_id=healthPostId,user_id=UserId).count()

           
            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

            # data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",gender=gender,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

    else:
        #Data For Only Ward Filter
        data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.all().count()
        data["NoOfCitizenEnrolled"] = familyMembers.objects.all().count()
        data["NoOfMaleEnrolled"] = familyMembers.objects.filter(gender="M").count()
        data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(gender="F").count()

        data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60).count()
        data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60).count()
        data["NoOfAbhaIdGenerated"] = 0
        data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True).count()

        data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True).count()
        data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True).count()

        data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home").count()
        data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True).count()

        data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center").count()
        data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required").count()
        data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied").count()

        if wardId:
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId).count()

            data["NoOfMaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="M").count()
            data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="F").count()


            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__healthPost__ward_id  =wardId).count()

            # data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,familyHead__area__healthPost__ward_id  =wardId).count()
            data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,familyHead__area__healthPost__ward_id  =wardId).count()


            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__healthPost__ward_id  =wardId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__healthPost__ward_id  =wardId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",familyHead__area__healthPost__ward_id  =wardId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",familyHead__area__healthPost__ward_id  =wardId).count()

        if healthPostId:
            #Data For  Ward and HealthPost Filter
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoOfMaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="M",area__healthPost_id=healthPostId).count()
            data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="F",area__healthPost_id=healthPostId).count()

            
            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

            # data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId).count()
            
        if UserId:
            #Data For  Ward and HealthPost Filter and User Id Filter
            data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,user_id=UserId ).count()
            data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            
            data["NoOfMaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="M",area__healthPost_id=healthPostId,user_id=UserId).count()
            data["NoOfFemaleEnrolled"] = familyMembers.objects.filter(familyHead__area__healthPost__ward_id  =wardId,gender="F",area__healthPost_id=healthPostId,user_id=UserId).count()

            
            
            data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

            data["NoOfBloodCollected"] = familyMembers.objects.filter(isSampleCollected = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["NoLabTestAdded"] = familyMembers.objects.filter(isLabTestAdded = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["BloodCollecttionDeniedByAmo"] = familyMembers.objects.filter(bloodCollectionLocation = "Not Required",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
            data["BloodCollecttionDeniedByIndividual"] = familyMembers.objects.filter(bloodCollectionLocation = "Denied",familyHead__area__healthPost__ward_id  =wardId,area__healthPost_id=healthPostId,familyHead__user_id=UserId).count()
    

    return Response({
        'status': 'success',
        'message': 'Successfully Fetched',
        'data': data,
    })


