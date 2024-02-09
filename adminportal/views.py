from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import Group
from rest_framework.response import Response
from database.models import *
from .serializers import *
from Allauth.serializers import RegisterSerializer
from rest_framework import status
from .permissions import *
from rest_framework.permissions import IsAuthenticated
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
from excel_response import ExcelResponse
from datetime import datetime
from rest_framework.decorators import api_view
from doctorsApp.permissions import IsMO


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
            if "newpassword" in  serializer.validated_data:
                instance.set_password(serializer.validated_data.get("newpassword"))
                instance.save()
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

class DownloadHealthpostwiseUserList(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsSupervisor ]

    def add_headers(self, sheet, *args):
        for header in range(len(args)):
            if isinstance(args[header],dict):
                start_column = 1
                for title,size in args[header].items():
                    end_column = start_column + (size-1)
                    sheet.merge_cells(start_row=header+1,start_column=start_column,
                                      end_row=header+1, end_column=end_column)
                    sheet.cell(row=header+1, column=start_column, value=title)
                    start_column = end_column + 1
            else:
                sheet.append(args[header])
        return sheet

    def unpack_list(self, data):
        val = ""
        if len(data) == 1:
            val = data[0]
        elif len(data) > 1:
            for i in data:
                val = val + i + ", "
        return val

    def unpack_survey_data(self, survey_data):
        collected_data = []

        for data in survey_data.values():
            for answers in data:
                answer = answers.get("answer",None)
                collected_data.append(self.unpack_list(answer))

        return collected_data

    def get(self, request, id, *args, **kwargs):
        try:
            healthpost = healthPost.objects.get(pk=id)
        except healthPost.DoesNotExist:
            return Response({
                "message":"No Health post exists with ID %d"%(id),
                "status":"error"
            } , status=400)
        healthpost_related_user = familyMembers.objects.filter(area__healthPost=healthpost)
        today = datetime.today().strftime('%d-%m-%Y')
        healthpost_name = healthpost.healthPostName

        if not healthpost_related_user:
            return Response({
                "message":"No data found for healthpost %s"%(healthpost_name),
                "status":"error"
            } , status=400)

        familyMember = healthpost_related_user.last()
        questionnaire = familyMember.Questionnaire
        parts_dict = {}
        questions_list = []
        for part,questions in questionnaire.items():
            parts_dict[part] = len(questions)
            for question in questions:
                questions_list.append(question.get("question",None))

        column_list = ['Name', 'Gender', 'Age', 'Mobile No', "Address" ,'Aadhar Card', 'Abha ID',
                       'Blood Collection Location', 'Family Head', 'ANM/Coordinator', 'ANM/Coordinator Mobile Number' , 'Survey Date',
                       'BMI', 'Blood Pressure', 'Height', 'Pulse', 'Weight', 'Test Assigned',
                       'Report', 'Area', 'General Status', 'ASHA/CHV', 'ASHA/CHV Mobile Number' , 'Vulnerable',
                       'Vulnerable Reason', 'Relationship', 'Random Blood Sugar']

        header1 = {'Citizen Details':len(column_list),
                   'Survey':len(questions_list)}
        header2 = {'':len(column_list),**parts_dict}
        header3 = column_list + questions_list

        data_list = []
        for family_member in  healthpost_related_user:
            citizen_details = [family_member.name, family_member.gender, family_member.age, family_member.mobileNo, family_member.familyHead.address,
                               family_member.aadharCard, family_member.abhaId,
                               family_member.bloodCollectionLocation, family_member.familyHead.name,
                               family_member.familySurveyor.name, family_member.familySurveyor.phoneNumber , family_member.created_date.strftime('%d/%m/%Y'), family_member.BMI,
                               family_member.bloodPressure, family_member.height, family_member.pulse,
                               family_member.weight, family_member.bool_transform("isLabTestAdded"),
                               family_member.bool_transform("isLabTestReportGenerated"), family_member.area.areas,
                               family_member.generalStatus, family_member.ASHA_CHV.name, family_member.ASHA_CHV.phoneNumber,
                               family_member.bool_transform("vulnerable"), family_member.vulnerable_reason, family_member.relationship,
                               family_member.randomBloodSugar]
            survey_data = self.unpack_survey_data(family_member.Questionnaire)
            aggregated_data = citizen_details + survey_data
            data_list.append(aggregated_data)

        wb = openpyxl.Workbook()
        ws = wb.active
        self.add_headers(ws, header1, header2, header3)
        for row in data_list:
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(healthpost_name+"_data_"+today)
        wb.save(response)
        return response

class DownloadWardwiseUserList(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsSupervisor ]

    def add_headers(self, sheet, *args):
        for header in range(len(args)):
            if isinstance(args[header],dict):
                start_column = 1
                for title,size in args[header].items():
                    end_column = start_column + (size-1)
                    sheet.merge_cells(start_row=header+1,start_column=start_column,
                                      end_row=header+1, end_column=end_column)
                    sheet.cell(row=header+1, column=start_column, value=title)
                    start_column = end_column + 1
            else:
                sheet.append(args[header])
        return sheet

    def unpack_list(self, data):
        val = ""
        if len(data) == 1:
            val = data[0]
        elif len(data) > 1:
            for i in data:
                val = val + i + ", "
        return val

    def unpack_survey_data(self, survey_data):
        collected_data = []

        for data in survey_data.values():
            for answers in data:
                answer = answers.get("answer",None)
                collected_data.append(self.unpack_list(answer))

        return collected_data

    def get(self, request, id, *args, **kwargs):
        try:
            ward_obj = ward.objects.get(pk=id)
        except ward.DoesNotExist:
            return Response({
                "message":"No Ward exists with ID %d"%(id),
                "status":"error"
            } , status=400)
        # ward_related_user = familyMembers.objects.filter(familySurveyor__userSections__healthPost__ward=ward_obj)
        ward_related_user = familyMembers.objects.filter(area__healthPost__ward=ward_obj)
        today = datetime.today().strftime('%d-%m-%Y')
        ward_name = ward_obj.wardName

        if not ward_related_user:
            return Response({
                "message":"No data found for ward %s"%(ward_name),
                "status":"error"
            } , status= 400)

        familyMember = ward_related_user.last()
        questionnaire = familyMember.Questionnaire
        parts_dict = {}
        questions_list = []
        for part,questions in questionnaire.items():
            parts_dict[part] = len(questions)
            for question in questions:
                questions_list.append(question.get("question",None))

        column_list = ['Name', 'Gender', 'Age', 'Mobile No', "Address" ,'Aadhar Card', 'Abha ID',
                       'Blood Collection Location', 'Family Head', 'ANM/Coordinator', 'ANM/Coordinator Mobile Number' , 'Survey Date',
                       'BMI', 'Blood Pressure', 'Height', 'Pulse', 'Weight', 'Test Assigned',
                       'Report', 'Area', 'General Status', 'ASHA/CHV', 'ASHA/CHV Mobile Number' , 'Vulnerable',
                       'Vulnerable Reason', 'Relationship', 'Random Blood Sugar']

        header1 = {'Citizen Details':len(column_list),
                   'Survey':len(questions_list)}
        header2 = {'':len(column_list),**parts_dict}
        header3 = column_list + questions_list

        data_list = []
        for family_member in  ward_related_user:
            citizen_details = [family_member.name, family_member.gender, family_member.age, family_member.mobileNo, family_member.familyHead.address,
                               family_member.aadharCard, family_member.abhaId,
                               family_member.bloodCollectionLocation, family_member.familyHead.name,
                               family_member.familySurveyor.name, family_member.familySurveyor.phoneNumber , family_member.created_date.strftime('%d/%m/%Y'), family_member.BMI,
                               family_member.bloodPressure, family_member.height, family_member.pulse,
                               family_member.weight, family_member.bool_transform("isLabTestAdded"),
                               family_member.bool_transform("isLabTestReportGenerated"), family_member.area.areas,
                               family_member.generalStatus, family_member.ASHA_CHV.name, family_member.ASHA_CHV.phoneNumber,
                               family_member.bool_transform("vulnerable"), family_member.vulnerable_reason, family_member.relationship,
                               family_member.randomBloodSugar]


            survey_data = self.unpack_survey_data(family_member.Questionnaire)
            aggregated_data = citizen_details + survey_data
            data_list.append(aggregated_data)

        wb = openpyxl.Workbook()
        ws = wb.active
        self.add_headers(ws, header1, header2, header3)
        for row in data_list:
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format("Ward_"+ward_name+"_data_"+today)
        wb.save(response)
        return response

class DownloadAllWardUserList(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsSupervisor ]

    def add_headers(self, sheet, *args):
        for header in range(len(args)):
            if isinstance(args[header],dict):
                start_column = 1
                for title,size in args[header].items():
                    end_column = start_column + (size-1)
                    sheet.merge_cells(start_row=header+1,start_column=start_column,
                                      end_row=header+1, end_column=end_column)
                    sheet.cell(row=header+1, column=start_column, value=title)
                    start_column = end_column + 1
            else:
                sheet.append(args[header])
        return sheet

    def unpack_list(self, data):
        val = ""
        if len(data) == 1:
            val = data[0]
        elif len(data) > 1:
            for i in data:
                val = val + i + ", "
        return val

    def unpack_survey_data(self, survey_data):
        collected_data = []

        for data in survey_data.values():
            for answers in data:
                answer = answers.get("answer",None)
                collected_data.append(self.unpack_list(answer))

        return collected_data

    def get(self, request, *args, **kwargs):

        ward_related_user = familyMembers.objects.all()
        today = datetime.today().strftime('%d-%m-%Y')

        familyMember = ward_related_user.last()
        questionnaire = familyMember.Questionnaire
        parts_dict = {}
        questions_list = []
        for part,questions in questionnaire.items():
            parts_dict[part] = len(questions)
            for question in questions:
                questions_list.append(question.get("question",None))

        column_list = ['Name', 'Gender', 'Age', 'Mobile No', 'Address', 'Aadhar Card', 'Abha ID',
                       'Blood Collection Location', 'Family Head', 'ANM/Coordinator', 'ANM/Coordinator Mobile Number' , 'Survey Date',
                       'BMI', 'Blood Pressure', 'Height', 'Pulse', 'Weight', 'Test Assigned',
                       'Report', 'Area', 'General Status', 'ASHA/CHV', 'ASHA/CHV Mobile Number' , 'Vulnerable',
                       'Vulnerable Reason', 'Relationship', 'Random Blood Sugar']

        header1 = {'Citizen Details':len(column_list),
                   'Survey':len(questions_list)}
        header2 = {'':len(column_list),**parts_dict}
        header3 = column_list + questions_list

        data_list = []
        for family_member in  ward_related_user:
            citizen_details = [family_member.name, family_member.gender, family_member.age, family_member.mobileNo, family_member.familyHead.address ,
                               family_member.aadharCard, family_member.abhaId,
                               family_member.bloodCollectionLocation, family_member.familyHead.name,
                               family_member.familySurveyor.name, family_member.familySurveyor.phoneNumber , family_member.created_date.strftime('%d/%m/%Y %I:%M:%S %p'), family_member.BMI,
                               family_member.bloodPressure, family_member.height, family_member.pulse,
                               family_member.weight, family_member.bool_transform("isLabTestAdded"),
                               family_member.bool_transform("isLabTestReportGenerated"), family_member.area.areas,
                               family_member.generalStatus, family_member.ASHA_CHV.name, family_member.ASHA_CHV.phoneNumber ,
                               family_member.bool_transform("vulnerable"), family_member.vulnerable_reason, family_member.relationship,
                               family_member.randomBloodSugar]
            survey_data = self.unpack_survey_data(family_member.Questionnaire)
            aggregated_data = citizen_details + survey_data
            data_list.append(aggregated_data)

        wb = openpyxl.Workbook()
        ws = wb.active
        self.add_headers(ws, header1, header2, header3)
        for row in data_list:
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format("All_Ward_data_"+today)
        wb.save(response)
        return response

class DownloadDispensarywiseUserList(generics.GenericAPIView):

    # permission_classes = [IsAuthenticated , IsMO ]

    def add_headers(self, sheet, *args):
        for header in range(len(args)):
            if isinstance(args[header],dict):
                start_column = 1
                for title,size in args[header].items():

                    end_column = start_column + (size-1)
                    sheet.merge_cells(start_row=header+1,start_column=start_column,
                                      end_row=header+1, end_column=end_column)
                    sheet.cell(row=header+1, column=start_column, value=title)
                    start_column = end_column + 1
            else:
                sheet.append(args[header])
        return sheet

    def unpack_list(self, data):
        val = ""
        if len(data) == 1:
            val = data[0]
        elif len(data) > 1:
            for i in data:
                val = val + i + ", "
        return val

    def unpack_survey_data(self, survey_data):
        collected_data = []

        for data in survey_data.values():
            for answers in data:
                answer = answers.get("answer",None)
                collected_data.append(self.unpack_list(answer))

        return collected_data

    def get(self, request ,id, *args, **kwargs):
        try:
            dispensary_obj = dispensary.objects.get(pk=id)
        except dispensary.DoesNotExist:
            return Response({
                "message":"No Dispensary exists with ID %d"%(id),
                "status":"error"
            } , status=400)
        dispensary_related_user = familyMembers.objects.filter(area__dispensary=dispensary_obj)
        today = datetime.today().strftime('%d-%m-%Y')
        dispensary_name = dispensary_obj.dispensaryName

        if not dispensary_related_user:
            return Response({
                "message":"No data found for dispensary %s"%(dispensary_name),
                "status":"error"
            } , status=400)

        familyMember = dispensary_related_user.last()
        questionnaire = familyMember.Questionnaire
        parts_dict = {}
        questions_list = []
        for part,questions in questionnaire.items():
            parts_dict[part] = len(questions)
            for question in questions:
                questions_list.append(question.get("question",None))

        column_list = ['Name', 'Gender', 'Age', 'Mobile No', 'Address', 'Aadhar Card', 'Abha ID',
                       'Blood Collection Location', 'Family Head', 'ANM/Coordinator', 'ANM/Coordinator Mobile Number' , 'Survey Date',
                       'BMI', 'Blood Pressure', 'Height', 'Pulse', 'Weight', 'Test Assigned',
                       'Report', 'Area', 'General Status', 'ASHA/CHV', 'ASHA/CHV Mobile Number' , 'Vulnerable',
                       'Vulnerable Reason', 'Relationship', 'Random Blood Sugar']

        header1 = {'Citizen Details':len(column_list),
                   'Survey':len(questions_list)}
        header2 = {'':len(column_list),**parts_dict}
        header3 = column_list + questions_list

        data_list = []
        for family_member in  dispensary_related_user:
            citizen_details = [family_member.name, family_member.gender, family_member.age, family_member.mobileNo, family_member.familyHead.address ,
                               family_member.aadharCard, family_member.abhaId,
                               family_member.bloodCollectionLocation, family_member.familyHead.name,
                               family_member.familySurveyor.name, family_member.familySurveyor.phoneNumber , family_member.created_date.strftime('%d/%m/%Y'), family_member.BMI,
                               family_member.bloodPressure, family_member.height, family_member.pulse,
                               family_member.weight, family_member.bool_transform("isLabTestAdded"),
                               family_member.bool_transform("isLabTestReportGenerated"), family_member.area.areas,
                               family_member.generalStatus, family_member.ASHA_CHV.name, family_member.ASHA_CHV.phoneNumber ,
                               family_member.bool_transform("vulnerable"), family_member.vulnerable_reason, family_member.relationship,
                               family_member.randomBloodSugar]
            survey_data = self.unpack_survey_data(family_member.Questionnaire)
            aggregated_data = citizen_details + survey_data
            data_list.append(aggregated_data)

        wb = openpyxl.Workbook()
        ws = wb.active
        self.add_headers(ws, header1, header2, header3)
        for row in data_list:
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(dispensary_name+"_data_"+today)
        wb.save(response)
        return response

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
            total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__ward__id = request.user.ward_id , familySurveyor__userSections__healthPost__id = healthpost_id ,  isAbhaCreated = True ).count()
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
            total_ent_disorder = 0 
            total_asthama = 0 

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
                ent_disorder = 0 
                Alzheimers = 0 
                asthama = 0 
                for question in part_b[16:17]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent_disorder += 1
                        break
                for question in part_b[1:10]:
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

                for question in part_b[40:44]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        Alzheimers  += 1
                        break
                for question in part_b[:1]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        asthama += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_disorder += ent_disorder
                total_Alzheimers += Alzheimers
                total_asthama += asthama

        else:
            today = timezone.now().date()
            ward = request.user.ward_id
            total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__ward__id = request.user.ward_id , isAbhaCreated = True ).count()
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
            total_ent_disorder = 0 
            total_asthama = 0 

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
                ent_disorder = 0 
                Alzheimers = 0 
                asthama = 0 
                for question in part_b[16:17]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent_disorder += 1
                        break
                for question in part_b[1:10]:
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

                for question in part_b[40:44]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        Alzheimers  += 1
                        break
                for question in part_b[:1]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        asthama += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_disorder += ent_disorder
                total_Alzheimers += Alzheimers
                total_asthama += asthama

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
            'total_AbhaCreated' : total_AbhaCreated , 
            "male" : male,
            "female" : female,
            "transgender" : transgender,
            'diabetes' : total_diabetes,
            'hypertension' : hypertension ,
            'oral_Cancer' : total_oral_cancer ,
            'cervical_cancer' : total_cervical_cancer ,
            'copd' : total_COPD_count,
            'eye_disorder' : total_eye_problem ,
            'ent_disorder' : total_ent_disorder ,
            'asthama' : total_asthama ,
            'Alzheimers' : total_Alzheimers ,
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

class MOHDashboardExportView(generics.GenericAPIView):

    permission_classes = ( IsAuthenticated , IsMOH )
    FamilySurvey_count = familyHeadDetails.objects.all()
    CustomUser_queryset = CustomUser.objects.all()

    def add_headers(self, sheet, *args):
        for header in range(len(args)):
            if isinstance(args[header],dict):
                start_column = 1
                for title,size in args[header].items():
                    end_column = start_column + (size-1)
                    sheet.merge_cells(start_row=header+1,start_column=start_column,
                                      end_row=header+1, end_column=end_column)
                    sheet.cell(row=header+1, column=start_column, value=title)
                    start_column = end_column + 1
            else:
                sheet.append(args[header])
        return sheet

    def get_queryset(self ):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        queryset = familyMembers.objects.all()

        return queryset

    def get(self, request, *args, **kwargs):

        healthpost_id = self.request.query_params.get('healthpost_id', None)
        wardId = self.request.query_params.get('wardId', None)
        
        data_list = [['ward Name' , 'Health Post Name' , "ANM/Co-ordinator" , "ANM Mobile number" ,'Families Enrolled'  , 'Citizens Enrolled' , 'CBAC Filled' , 
                    'Citizens 60 years + enrolled', 'Citizens 30 years + enrolled' , "Males Enrolled" ,  "Females Enrolled" ,  "Transgender Enrolled",
                    "ABHA ID Generated" , 'Diabetes' , 'Hypertension' ,  'Oral Cancer' , 'Cervical cancer' , 'COPD' , 'Eye Disorder' ,
                    'ENT Disorder' ,  'Asthma' , 'Alzheimers' ,  'TB' , 'Breast cancer' , 'Other Communicable' , 
                    'Blood collected at home' , 'blood collected at center' , 'Blood Collection Denied By AMO' ,  'Blood Collection Denied By Citizen',
                    'Total Reports Generated' , 'Tests Assigned' , 
                    'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment' , 
                    'Referral to HBT polyclinic for Physician consultation',
                    'Referral to Peripheral Hospital / Special Hospital for management of Complication',
                    'Referral to Medical College for management of Complication',
                    'Referral to Private facility',
                    'Vulnerable Citizen' ]]
        
        header1 = {'Citizen Details':len(data_list[0][0:13]) ,'Dieases Suspected': len(data_list[0][13:25]),
                   'Blood Collection' : len(data_list[0][25:31]) , 'Referrals' : len(data_list[0][31:]) }


        if healthpost_id:
            try:
                healthpost = healthPost.objects.get(pk=healthpost_id)
            except healthPost.DoesNotExist:
                return Response({
                    "message":"No Health post exists with ID %d"%(id),
                    "status":"error"
                } , status= 400 )
            healthpost_related_user = familyMembers.objects.filter(familySurveyor__userSections__healthPost=healthpost)
            today = datetime.today().strftime('%d-%m-%Y')
            healthpost_name = healthpost.healthPostName

            if not healthpost_related_user:
                return Response({
                    "message":"No data found for healthpost %s"%(healthpost_name),
                    "status":"error"} , status = 400)
            ANM_list = CustomUser.objects.filter(groups__name = "healthworker" , userSections__healthPost__id = healthpost_id)
            for anm in ANM_list:

                total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , isAbhaCreated = True , familySurveyor = anm ).count()  
                
                total_family_count = self.FamilySurvey_count.filter( user__userSections__healthPost__id = healthpost_id ,  user = anm ).count()
          
                total_citizen_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , familySurveyor = anm ).count()
                total_cbac_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id,age__gte = 30 , cbacRequired = True , familySurveyor = anm).count()
                male =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , gender = "M" , familySurveyor = anm ).count()
                female =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , gender = "F" , familySurveyor = anm ).count()
                transgender =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, gender = "O" , familySurveyor = anm ).count()
                citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 60 , familySurveyor = anm).count()
                citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 30 , familySurveyor = anm).count()

                total_vulnerabel = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , vulnerable = True , familySurveyor = anm).count()
                
                blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Home' , familySurveyor = anm).count()
                blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Center', familySurveyor = anm).count()
                denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, deniedBy = 'AMO', familySurveyor = anm).count()
                denieded_by_mo_individual = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, deniedBy = 'Individual Itself', familySurveyor = anm).count()
                Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id,familySurveyor = anm, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
                Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, familySurveyor = anm,referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
                Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, familySurveyor = anm ,  referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
                Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, familySurveyor = anm ,  referels__choice = 'Referral to Medical College for management of Complication').count()
                Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, familySurveyor = anm ,  referels__choice = 'Referral to Private facility').count()
                hypertension = self.get_queryset().filter(  familySurveyor__userSections__healthPost__id = healthpost_id , familySurveyor = anm , bloodPressure__gte = 140).count()

                total_LabTestAdded = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, familySurveyor = anm , isLabTestAdded = True).count()
                TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, familySurveyor = anm ,  isLabTestReportGenerated = True).count()
                
                Questionnaire_queryset = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , familySurveyor = anm , Questionnaire__isnull=False)
                total_tb_count = 0
                total_diabetes = 0
                total_breast_cancer = 0 
                total_oral_cancer = 0 
                total_cervical_cancer =0
                total_COPD_count = 0 
                toatal_communicable  = 0 
                total_eye_problem = 0 
                total_Alzheimers = 0 
                total_ent_disorder = 0 
                total_asthama = 0 
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
                    ent_disorder = 0 
                    Alzheimers = 0 
                    asthama = 0 
                    for question in part_b[16:17]:
                        answer = question.get('answer', [])
                        if answer and len(answer) > 0:
                            ent_disorder += 1
                            break
                    for question in part_b[1:10]:
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

                    for question in part_b[40:44]:
                        answer = question.get('answer', [])
                        if answer and len(answer) > 0:
                            Alzheimers  += 1
                            break
                    for question in part_b[:1]:
                        answer = question.get('answer', [])
                        if answer and len(answer) > 0:
                            asthama += 1
                            break

                    total_tb_count += tb_count
                    total_diabetes += diabetes
                    total_breast_cancer += breast_cancer
                    total_oral_cancer += oral_cancer
                    total_cervical_cancer += cervical_cancer
                    total_COPD_count += COPD
                    toatal_communicable += communicable
                    total_eye_problem += eye_problem
                    total_ent_disorder += ent_disorder
                    total_Alzheimers += Alzheimers
                    total_asthama += asthama



                data_list.append([ healthpost.ward.wardName , healthpost.healthPostName , anm.name , anm.phoneNumber ,
                                total_family_count ,
                                total_citizen_count ,
                                total_cbac_count , 
                                citizen_above_60 ,
                                citizen_above_30 ,
                                male ,
                                female ,
                                transgender ,
                                total_AbhaCreated , 
                                total_diabetes , hypertension , total_oral_cancer , total_cervical_cancer , total_COPD_count , total_eye_problem , total_ent_disorder , 
                                total_asthama, total_Alzheimers, total_tb_count ,total_breast_cancer , toatal_communicable , 
                                blood_collected_home , blood_collected_center ,  denieded_by_mo_count  ,  denieded_by_mo_individual , TestReportGenerated , total_LabTestAdded,
                                Referral_choice_Referral_to_Mun_Dispensary ,
                                Referral_choice_Referral_to_HBT_polyclinic,
                                Referral_choice_Referral_to_Peripheral_Hospital,
                                Referral_choice_Referral_to_Medical_College ,
                                Referral_choice_Referral_to_Private_facility,
                                total_vulnerabel
                                            ])
                wb = openpyxl.Workbook()
                ws = wb.active
                self.add_headers(ws, header1 )
                for row in data_list:
                    # print(row)
                    ws.append(row)

        
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(healthpost_name+"_data_"+today)
            wb.save(response)
            return response 
        elif wardId:
            try:
                ward_name = ward.objects.get(pk=wardId)
            except ward.DoesNotExist:
                return Response({
                    "message":"No ward exists with ID %d"%(wardId),
                    "status":"error"
                })
            ward_related_user = familyMembers.objects.filter(familySurveyor__userSections__healthPost__ward__id=wardId)
            today = datetime.today().strftime('%d-%m-%Y')

            if not ward_related_user:
                return Response({
                    "message":"No data found for ward %s"%(ward_name.wardName),
                    "status":"error"
                })
        
            health__post = healthPost.objects.filter(ward__id = wardId)

            for healthpost_id in health__post:
                ANM_list = CustomUser.objects.filter(groups__name = "healthworker" , userSections__healthPost__id = healthpost_id.id).order_by("name")
                for anms in ANM_list:
                    
                    total_AbhaCreated = self.get_queryset().filter( familySurveyor__id = anms.id  , isAbhaCreated = True ).count()
                    
                    total_family_count = self.FamilySurvey_count.filter( user__id = anms.id ).count()
                    total_citizen_count = self.get_queryset().filter( familySurveyor__id = anms.id ).count()
                    
                    total_cbac_count = self.get_queryset().filter( familySurveyor__id = anms.id  ,age__gte = 30 , cbacRequired = True).count()
                    male =  self.get_queryset().filter( familySurveyor__id = anms.id  , gender = "M" ).count()
                    female =  self.get_queryset().filter( familySurveyor__id = anms.id   , gender = "F" ).count()
                    transgender =  self.get_queryset().filter( familySurveyor__id = anms.id  , gender = "O" ).count()
                    citizen_above_60 =  self.get_queryset().filter(familySurveyor__id = anms.id  , age__gte = 60 ).count()
                    citizen_above_30 =  self.get_queryset().filter(familySurveyor__id = anms.id  , age__gte = 30 ).count()

                    total_vulnerabel = self.get_queryset().filter( familySurveyor__id = anms.id   , vulnerable = True).count()
                    
                    blood_collected_home = self.get_queryset().filter(familySurveyor__id = anms.id  , bloodCollectionLocation = 'Home').count()
                    blood_collected_center = self.get_queryset().filter(familySurveyor__id = anms.id  , bloodCollectionLocation = 'Center').count()
                    denieded_by_mo_count = self.get_queryset().filter(familySurveyor__id = anms.id  , deniedBy = 'AMO').count()
                    denieded_by_mo_individual = self.get_queryset().filter( familySurveyor__id = anms.id  , deniedBy = 'Individual Itself').count()
                    Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__id = anms.id  , referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
                    Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__id = anms.id  , referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
                    Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( familySurveyor__id = anms.id  , referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
                    Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( familySurveyor__id = anms.id  , referels__choice = 'Referral to Medical College for management of Complication').count()
                    Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( familySurveyor__id = anms.id  , referels__choice = 'Referral to Private facility').count()
                    hypertension = self.get_queryset().filter(  familySurveyor__id = anms.id   ,bloodPressure__gte = 140).count()

                    total_LabTestAdded = self.get_queryset().filter( familySurveyor__id = anms.id  ,isLabTestAdded = True).count()
                    TestReportGenerated = self.get_queryset().filter(familySurveyor__id = anms.id  , isLabTestReportGenerated = True).count()
                    Questionnaire_queryset = self.get_queryset().filter( familySurveyor__id = anms.id   , Questionnaire__isnull=False)
                    total_tb_count = 0
                    total_diabetes = 0
                    total_breast_cancer = 0 
                    total_oral_cancer = 0 
                    total_cervical_cancer =0
                    total_COPD_count = 0 
                    toatal_communicable  = 0 
                    total_eye_problem = 0 
                    total_Alzheimers = 0 
                    total_ent_disorder = 0 
                    total_asthama = 0 
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
                        ent_disorder = 0 
                        Alzheimers = 0 
                        asthama = 0 
                        for question in part_b[16:17]:
                            answer = question.get('answer', [])
                            if answer and len(answer) > 0:
                                ent_disorder += 1
                                break
                        for question in part_b[1:10]:
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

                        for question in part_b[40:44]:
                            answer = question.get('answer', [])
                            if answer and len(answer) > 0:
                                Alzheimers  += 1
                                break
                        for question in part_b[:1]:
                            answer = question.get('answer', [])
                            if answer and len(answer) > 0:
                                asthama += 1
                                break

                        total_tb_count += tb_count
                        total_diabetes += diabetes
                        total_breast_cancer += breast_cancer
                        total_oral_cancer += oral_cancer
                        total_cervical_cancer += cervical_cancer
                        total_COPD_count += COPD
                        toatal_communicable += communicable
                        total_eye_problem += eye_problem
                        total_ent_disorder += ent_disorder
                        total_Alzheimers += Alzheimers
                        total_asthama += asthama

                    data_list.append([ healthpost_id.ward.wardName , healthpost_id.healthPostName ,  anms.name , anms.phoneNumber  ,  
                            total_family_count ,
                            total_citizen_count ,
                            total_cbac_count , 
                            citizen_above_60 ,
                            citizen_above_30 ,
                            male ,
                            female ,
                            transgender ,
                            total_AbhaCreated , 
                            total_diabetes , hypertension , total_oral_cancer , total_cervical_cancer , total_COPD_count , total_eye_problem , total_ent_disorder , 
                            total_asthama, total_Alzheimers, total_tb_count ,total_breast_cancer , toatal_communicable , 
                            blood_collected_home , blood_collected_center ,  denieded_by_mo_count  ,  denieded_by_mo_individual , TestReportGenerated , total_LabTestAdded,
                            Referral_choice_Referral_to_Mun_Dispensary ,
                            Referral_choice_Referral_to_HBT_polyclinic,
                            Referral_choice_Referral_to_Peripheral_Hospital,
                            Referral_choice_Referral_to_Medical_College ,
                            Referral_choice_Referral_to_Private_facility,
                            total_vulnerabel
                                        ])
                    
                        
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    self.add_headers(ws, header1 )
                    for row in data_list:
                        ws.append(row)

        
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(ward_name.wardName+"_data_"+today)
            wb.save(response)
            return response 
        else:
            return Response({'status': 'error',
                              'message': "please select Ward or Health Post"} , status = 400)
        
class  AdminDashboardView(generics.GenericAPIView): 
    permission_classes= (IsAuthenticated , IsAdmin)
    queryset = familyMembers.objects.all()
    FamilySurvey_count = familyHeadDetails.objects.all()
    CustomUser_queryset = CustomUser.objects.all()

    def get(self, request ,  *args, **kwargs):
        healthpost_id = self.request.query_params.get('healthpost_id', None)
        wardId = self.request.query_params.get('wardId', None)

        CHV_ASHA_count = self.CustomUser_queryset.filter(groups__name='CHV-ASHA').count()
        MO_count = self.CustomUser_queryset.filter(groups__name='mo').count()
        ANM_count = self.CustomUser_queryset.filter(groups__name='healthworker').count()

        if healthpost_id:

            today = timezone.now().date()
            total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__ward__id = wardId, isAbhaCreated = True ).count()
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

            total_LabTestAdded = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id ,  isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , isLabTestReportGenerated = True).count()

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
            total_ent_disorder = 0 
            total_asthama = 0 

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
                ent_disorder = 0 
                Alzheimers = 0 
                asthama = 0 
                for question in part_b[16:17]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent_disorder += 1
                        break
                for question in part_b[1:10]:
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

                for question in part_b[40:44]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        Alzheimers  += 1
                        break
                for question in part_b[:1]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        asthama += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_disorder += ent_disorder
                total_Alzheimers += Alzheimers
                total_asthama += asthama
        elif wardId :

            today = timezone.now().date()
            total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__ward__id = wardId, isAbhaCreated = True ).count()
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
            total_ent_disorder = 0 
            total_asthama = 0 

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
                ent_disorder = 0 
                Alzheimers = 0 
                asthama = 0 
                for question in part_b[16:17]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent_disorder += 1
                        break
                for question in part_b[1:10]:
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

                for question in part_b[40:44]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        Alzheimers  += 1
                        break
                for question in part_b[:1]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        asthama += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_disorder += ent_disorder
                total_Alzheimers += Alzheimers
                total_asthama += asthama
        else:
            today = timezone.now().date()
            total_AbhaCreated = self.get_queryset().filter(isAbhaCreated = True ).count()
            total_citizen_count = self.get_queryset().count()
            todays_citizen_count  = self.get_queryset().filter(created_date__day= today.day).count()
            total_cbac_count = self.get_queryset().filter( age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True ).count()
            total_family_count = self.FamilySurvey_count.count()
            male =  self.get_queryset().filter( gender = "M" ).count()
            female =  self.get_queryset().filter(gender = "F" ).count()
            transgender =  self.get_queryset().filter( gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter( age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter( age__gte = 30 ).count()
            today_family_count = self.FamilySurvey_count.filter( created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter(vulnerable = True).count()
            vulnerabel_70_Years = self.get_queryset().filter( vulnerable_choices__choice = '70+ Years').count()
            vulnerabel_Physically_handicapped = self.get_queryset().filter( vulnerable_choices__choice = 'Physically Handicapped').count()
            vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter( vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
            vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter( vulnerable_choices__choice = 'Elderly and alone at home').count()
            vulnerabel_any_other_reason = self.get_queryset().filter(vulnerable_choices__choice = 'Any other reason').count()

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
            total_ent_disorder = 0 
            total_asthama = 0 

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
                ent_disorder = 0 
                Alzheimers = 0 
                asthama = 0 
                for question in part_b[16:17]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent_disorder += 1
                        break
                for question in part_b[1:10]:
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

                for question in part_b[40:44]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        Alzheimers  += 1
                        break
                for question in part_b[:1]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        asthama += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_disorder += ent_disorder
                total_Alzheimers += Alzheimers
                total_asthama += asthama

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
            'total_AbhaCreated' : total_AbhaCreated , 
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
            'ent_disorder' : total_ent_disorder ,
            'asthama' : total_asthama ,
            'Alzheimers' : total_Alzheimers ,
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

class AdminDashboardExportView(generics.GenericAPIView):
    permission_classes= (IsAuthenticated , IsAdmin)
    FamilySurvey_count = familyHeadDetails.objects.all().order_by('user__userSections__healthPost__ward')
    queryset = familyMembers.objects.all()
    health_Posts = healthPost.objects.all().order_by('ward')


    def add_headers(self, sheet, *args):
        for header in range(len(args)):
            if isinstance(args[header],dict):
                start_column = 1
                for title,size in args[header].items():
                    end_column = start_column + (size-1)
                    sheet.merge_cells(start_row=header+1,start_column=start_column,
                                      end_row=header+1, end_column=end_column)
                    sheet.cell(row=header+1, column=start_column, value=title)
                    start_column = end_column + 1
            else:
                sheet.append(args[header])
        return sheet

    def get(self , request ):
        healthpost_id = self.request.query_params.get('healthpost_id', None)
        wardId = self.request.query_params.get('wardId', None)

        data_list = [['ward Name' , 'Health Post Name' , 'Families Enrolled'  , 'Citizens Enrolled' , 'CBAC Filled' ,
                    'Citizens 60 years + enrolled', 'Citizens 30 years + enrolled' , "Males Enrolled" ,  "Females Enrolled" ,  "Transgender Enrolled",
                    "ABHA ID Generated" , 'Diabetes' , 'Hypertension' ,  'Oral Cancer' , 'Cervical cancer' , 'COPD' , 'Eye Disorder' ,
                    'ENT Disorder' ,  'Asthma' , 'Alzheimers' ,  'TB' , 'Breast cancer' , 'Other Communicable' ,
                    'Blood collected at home' , 'blood collected at center' , 'Blood Collection Denied By AMO' ,  'Blood Collection Denied By Citizen',
                    'Total Reports Generated' , 'Tests Assigned' ,
                    'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment' ,
                    'Referral to HBT polyclinic for Physician consultation',
                    'Referral to Peripheral Hospital / Special Hospital for management of Complication',
                    'Referral to Medical College for management of Complication',
                    'Referral to Private facility',
                    'Vulnerable Citizen' ]]

        header1 = {'Citizen Details':len(data_list[0][0:11]) ,'Dieases Suspected': len(data_list[0][11:23]),
                   'Blood Collection' : len(data_list[0][23:29]) , 'Referrals' : len(data_list[0][29:]) }

        if healthpost_id:
            try:
                healthpost = healthPost.objects.get(pk=healthpost_id)
            except healthPost.DoesNotExist:
                return Response({
                    "message":"No Health post exists with ID %d"%(id),
                    "status":"error"
                })
            healthpost_related_user = familyMembers.objects.filter(familySurveyor__userSections__healthPost=healthpost)
            today = datetime.today().strftime('%d-%m-%Y')
            healthpost_name = healthpost.healthPostName

            if not healthpost_related_user:
                return Response({
                    "message":"No data found for healthpost %s"%(healthpost_name),
                    "status":"error"
                })
            total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id  , isAbhaCreated = True ).count()
            total_family_count = self.FamilySurvey_count.filter( user__userSections__healthPost__id = healthpost_id ).count()
            total_citizen_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id ).count()
            total_cbac_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id,age__gte = 30 , cbacRequired = True).count()
            partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__id = healthpost_id).count()
            male =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , gender = "M" ).count()
            female =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , gender = "F" ).count()
            transgender =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, gender = "O" ).count()
            citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 60 ).count()
            citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, age__gte = 30 ).count()
            # today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__id = health_Post.id ,created_date__day = today.day ).count()

            total_vulnerabel = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id , vulnerable = True).count()

            blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Home').count()
            blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, bloodCollectionLocation = 'Center').count()
            denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, deniedBy = 'AMO').count()
            denieded_by_mo_individual = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, deniedBy = 'Individual Itself').count()
            Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
            Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
            Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
            Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Medical College for management of Complication').count()
            Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id, referels__choice = 'Referral to Private facility').count()
            hypertension = self.get_queryset().filter(  familySurveyor__userSections__healthPost__id = healthpost_id ,bloodPressure__gte = 140).count()

            total_LabTestAdded = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id,isLabTestAdded = True).count()
            TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id, isLabTestReportGenerated = True).count()
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
            total_ent_disorder = 0 
            total_asthama = 0 
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
                ent_disorder = 0 
                Alzheimers = 0 
                asthama = 0 
                for question in part_b[16:17]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        ent_disorder += 1
                        break
                for question in part_b[1:10]:
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

                for question in part_b[40:44]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        Alzheimers  += 1
                        break
                for question in part_b[:1]:
                    answer = question.get('answer', [])
                    if answer and len(answer) > 0:
                        asthama += 1
                        break

                total_tb_count += tb_count
                total_diabetes += diabetes
                total_breast_cancer += breast_cancer
                total_oral_cancer += oral_cancer
                total_cervical_cancer += cervical_cancer
                total_COPD_count += COPD
                toatal_communicable += communicable
                total_eye_problem += eye_problem
                total_ent_disorder += ent_disorder
                total_Alzheimers += Alzheimers
                total_asthama += asthama

            data_list.append([ healthpost.ward.wardName , healthpost.healthPostName ,
                    total_family_count ,
                    total_citizen_count ,
                    total_cbac_count , 
                    citizen_above_60 ,
                    citizen_above_30 ,
                    male ,
                    female ,
                    transgender ,
                    total_AbhaCreated , 
                    total_diabetes , hypertension , total_oral_cancer , total_cervical_cancer , total_COPD_count , total_eye_problem , total_ent_disorder , 
                    total_asthama, total_Alzheimers, total_tb_count ,total_breast_cancer , toatal_communicable , 
                    blood_collected_home , blood_collected_center ,  denieded_by_mo_count  ,  denieded_by_mo_individual , TestReportGenerated , total_LabTestAdded,
                    Referral_choice_Referral_to_Mun_Dispensary ,
                    Referral_choice_Referral_to_HBT_polyclinic,
                    Referral_choice_Referral_to_Peripheral_Hospital,
                    Referral_choice_Referral_to_Medical_College ,
                    Referral_choice_Referral_to_Private_facility,
                    total_vulnerabel
                                ])
            wb = openpyxl.Workbook()
            ws = wb.active
            self.add_headers(ws, header1 )
            for row in data_list:
                # print(row)
                ws.append(row)


            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(healthpost_name+"_data_"+today)
            wb.save(response)
            return response

        elif wardId:

            try:
                ward_name = ward.objects.get(pk=wardId)
                # print(ward_name)
            except ward.DoesNotExist:
                return Response({
                    "message":"No ward exists with ID %d"%(id),
                    "status":"error"
                })
            ward_related_user = familyMembers.objects.filter(familySurveyor__userSections__healthPost__ward__id=wardId)
            # print(ward_related_user)
            today = datetime.today().strftime('%d-%m-%Y')
            # ward_name = ward_related_user.wardName

            if not ward_related_user:
                return Response({
                    "message":"No data found for ward %s"%(ward_name.wardName),
                    "status":"error"
                })
            for i in ward_related_user:


                health__post = healthPost.objects.filter(ward__id = i.familySurveyor.userSections.all()[0].healthPost.ward.id ).order_by("ward")
             
              
                for healthpost_id in health__post:
                    
                    total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__id= healthpost_id.id  , isAbhaCreated = True ).count()
                    total_family_count = self.FamilySurvey_count.filter( user__userSections__healthPost__id = healthpost_id.id ).count()
                    total_citizen_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id ).count()
                    total_cbac_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id,age__gte = 30 , cbacRequired = True).count()
                    male =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id, gender = "M" ).count()
                    female =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id , gender = "F" ).count()
                    transgender =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id, gender = "O" ).count()
                    citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, age__gte = 60 ).count()
                    citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, age__gte = 30 ).count()

                    total_vulnerabel = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id , vulnerable = True).count()

                    blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, bloodCollectionLocation = 'Home').count()
                    blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, bloodCollectionLocation = 'Center').count()
                    denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, deniedBy = 'AMO').count()
                    denieded_by_mo_individual = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id, deniedBy = 'Individual Itself').count()
                    Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
                    Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
                    Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id, referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
                    Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id, referels__choice = 'Referral to Medical College for management of Complication').count()
                    Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id, referels__choice = 'Referral to Private facility').count()
                    hypertension = self.get_queryset().filter(  familySurveyor__userSections__healthPost__id = healthpost_id.id ,bloodPressure__gte = 140).count()

                    total_LabTestAdded = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id,isLabTestAdded = True).count()
                    TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = healthpost_id.id, isLabTestReportGenerated = True).count()
                    Questionnaire_queryset = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = healthpost_id.id , Questionnaire__isnull=False)
                    total_tb_count = 0
                    total_diabetes = 0
                    total_breast_cancer = 0 
                    total_oral_cancer = 0 
                    total_cervical_cancer =0
                    total_COPD_count = 0 
                    toatal_communicable  = 0 
                    total_eye_problem = 0 
                    total_Alzheimers = 0 
                    total_ent_disorder = 0 
                    total_asthama = 0 
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
                        ent_disorder = 0 
                        Alzheimers = 0 
                        asthama = 0 
                        for question in part_b[16:17]:
                            answer = question.get('answer', [])
                            if answer and len(answer) > 0:
                                ent_disorder += 1
                                break
                        for question in part_b[1:10]:
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

                        for question in part_b[40:44]:
                            answer = question.get('answer', [])
                            if answer and len(answer) > 0:
                                Alzheimers  += 1
                                break
                        for question in part_b[:1]:
                            answer = question.get('answer', [])
                            if answer and len(answer) > 0:
                                asthama += 1
                                break

                        total_tb_count += tb_count
                        total_diabetes += diabetes
                        total_breast_cancer += breast_cancer
                        total_oral_cancer += oral_cancer
                        total_cervical_cancer += cervical_cancer
                        total_COPD_count += COPD
                        toatal_communicable += communicable
                        total_eye_problem += eye_problem
                        total_ent_disorder += ent_disorder
                        total_Alzheimers += Alzheimers
                        total_asthama += asthama

                    data_list.append([ healthpost_id.ward.wardName , healthpost_id.healthPostName ,
                            total_family_count ,
                            total_citizen_count ,
                            total_cbac_count , 
                            citizen_above_60 ,
                            citizen_above_30 ,
                            male ,
                            female ,
                            transgender ,
                            total_AbhaCreated , 
                            total_diabetes , hypertension , total_oral_cancer , total_cervical_cancer , total_COPD_count , total_eye_problem , total_ent_disorder , 
                            total_asthama, total_Alzheimers, total_tb_count ,total_breast_cancer , toatal_communicable , 
                            blood_collected_home , blood_collected_center ,  denieded_by_mo_count  ,  denieded_by_mo_individual , TestReportGenerated , total_LabTestAdded,
                            Referral_choice_Referral_to_Mun_Dispensary ,
                            Referral_choice_Referral_to_HBT_polyclinic,
                            Referral_choice_Referral_to_Peripheral_Hospital,
                            Referral_choice_Referral_to_Medical_College ,
                            Referral_choice_Referral_to_Private_facility,
                            total_vulnerabel
                                        ])
                wb = openpyxl.Workbook()
                ws = wb.active
                self.add_headers(ws, header1 )
                for row in data_list:
                    ws.append(row)


                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format("Ward_"+ward_name.wardName+"_data_"+today)
                wb.save(response)
                return response
        else:
            for health_Post in self.health_Posts:
                today = datetime.today().strftime('%d-%m-%Y')

                total_AbhaCreated = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id , isAbhaCreated = True ).count()
                total_family_count = self.FamilySurvey_count.filter( user__userSections__healthPost__id = health_Post.id ).count()
                total_citizen_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id ).count()
                total_cbac_count = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id,age__gte = 30 , cbacRequired = True).count()
                partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user__userSections__healthPost__id = health_Post.id).count()
                male =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id , gender = "M" ).count()
                female =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id , gender = "F" ).count()
                transgender =  self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id, gender = "O" ).count()
                citizen_above_60 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, age__gte = 60 ).count()
                citizen_above_30 =  self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, age__gte = 30 ).count()
                # today_family_count = self.FamilySurvey_count.filter(user__userSections__healthPost__id = health_Post.id ,created_date__day = today.day ).count()

                total_vulnerabel = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id , vulnerable = True).count()
                vulnerabel_70_Years = self.get_queryset().filter( vulnerable_choices__choice = '70+ Years').count()
                vulnerabel_Physically_handicapped = self.get_queryset().filter( vulnerable_choices__choice = 'Physically Handicapped').count()
                vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
                vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter( vulnerable_choices__choice = 'Elderly and alone at home').count()
                vulnerabel_any_other_reason = self.get_queryset().filter( vulnerable_choices__choice = 'Any other reason').count()

                blood_collected_home = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, bloodCollectionLocation = 'Home').count()
                blood_collected_center = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, bloodCollectionLocation = 'Center').count()
                denieded_by_mo_count = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, deniedBy = 'AMO').count()
                denieded_by_mo_individual = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id, deniedBy = 'Individual Itself').count()
                Referral_choice_Referral_to_Mun_Dispensary = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
                Referral_choice_Referral_to_HBT_polyclinic = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
                Referral_choice_Referral_to_Peripheral_Hospital = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id, referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
                Referral_choice_Referral_to_Medical_College = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id, referels__choice = 'Referral to Medical College for management of Complication').count()
                Referral_choice_Referral_to_Private_facility = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id, referels__choice = 'Referral to Private facility').count()
                hypertension = self.get_queryset().filter(  familySurveyor__userSections__healthPost__id = health_Post.id ,bloodPressure__gte = 140).count()

                total_LabTestAdded = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id,isLabTestAdded = True).count()
                TestReportGenerated = self.get_queryset().filter(familySurveyor__userSections__healthPost__id = health_Post.id, isLabTestReportGenerated = True).count()
                Questionnaire_queryset = self.get_queryset().filter( familySurveyor__userSections__healthPost__id = health_Post.id , Questionnaire__isnull=False)
                total_tb_count = 0
                total_diabetes = 0
                total_breast_cancer = 0 
                total_oral_cancer = 0 
                total_cervical_cancer =0
                total_COPD_count = 0 
                toatal_communicable  = 0 
                total_eye_problem = 0 
                total_Alzheimers = 0 
                total_ent_disorder = 0 
                total_asthama = 0 
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
                    ent_disorder = 0 
                    Alzheimers = 0 
                    asthama = 0 
                    for question in part_b[16:17]:
                        answer = question.get('answer', [])
                        if answer and len(answer) > 0:
                            ent_disorder += 1
                            break
                    for question in part_b[1:10]:
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

                    for question in part_b[40:44]:
                        answer = question.get('answer', [])
                        if answer and len(answer) > 0:
                            Alzheimers  += 1
                            break
                    for question in part_b[:1]:
                        answer = question.get('answer', [])
                        if answer and len(answer) > 0:
                            asthama += 1
                            break

                    total_tb_count += tb_count
                    total_diabetes += diabetes
                    total_breast_cancer += breast_cancer
                    total_oral_cancer += oral_cancer
                    total_cervical_cancer += cervical_cancer
                    total_COPD_count += COPD
                    toatal_communicable += communicable
                    total_eye_problem += eye_problem
                    total_ent_disorder += ent_disorder
                    total_Alzheimers += Alzheimers
                    total_asthama += asthama

                data_list.append([ health_Post.ward.wardName , health_Post.healthPostName ,
                        total_family_count ,
                        total_citizen_count ,
                        total_cbac_count , 
                        citizen_above_60 ,
                        citizen_above_30 ,
                        male ,
                        female ,
                        transgender ,
                        total_AbhaCreated , 
                        total_diabetes , hypertension , total_oral_cancer , total_cervical_cancer , total_COPD_count , total_eye_problem , total_ent_disorder , 
                        total_asthama, total_Alzheimers, total_tb_count ,total_breast_cancer , toatal_communicable , 
                        blood_collected_home , blood_collected_center ,  denieded_by_mo_count  ,  denieded_by_mo_individual , TestReportGenerated , total_LabTestAdded,
                        Referral_choice_Referral_to_Mun_Dispensary ,
                        Referral_choice_Referral_to_HBT_polyclinic,
                        Referral_choice_Referral_to_Peripheral_Hospital,
                        Referral_choice_Referral_to_Medical_College ,
                        Referral_choice_Referral_to_Private_facility,
                        total_vulnerabel
                                    ])

            wb = openpyxl.Workbook()
            ws = wb.active
            self.add_headers(ws, header1 )
            for row in data_list:
                # print(row)
                ws.append(row)


            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format("All_Ward_data_"+today)
            wb.save(response)
            return response



# class GetAllUserDetails(generics.GenericAPIView):
#     def get(self , request , id  ):
#         data = {'wards': []}
    
#         wards = ward.objects.filter(pk = id ).order_by("wardName")
    
#         for w in wards:
#             wrd = {'ward': w.wardName, 'healthPosts': []}
    
#             health_posts = healthPost.objects.filter(ward=w)
#             for hp in health_posts:
#                 areaData = area.objects.filter(healthPost_id = hp.id).values("areas")
#                 areaList =  [item["areas"] for item in areaData]
#                 health_post_info = {'healthPost': hp.healthPostName,'areaList':areaList, 'sections': []}
    
#                 sections = section.objects.filter(healthPost=hp)
#                 for sec in sections:
#                     section_info = {'sectionName': sec.sectionName, 'anms': [],}
    
#                     # ANMs
#                     # anms = CustomUser.objects.filter(section_id=sec.id, groups__name="healthworker")
#                     anms = CustomUser.objects.filter(userSections__in=[sec], groups__name="healthworker")
    
#                     for anm in anms:
#                         anm_info = {'anmName': anm.name, 'chvs': []}
    
#                         # CHVs under the ANM
#                         chvs = CustomUser.objects.filter(ANM_id = anm.id,groups__name="CHV-ASHA")
#                         for chv in chvs:
#                             chv_info = {'chvName': chv.name}
#                             anm_info['chvs'].append(chv_info)
    
#                         section_info['anms'].append(anm_info)
    
#                     health_post_info['sections'].append(section_info)
    
#                 wrd['healthPosts'].append(health_post_info)
    
#             data['wards'].append(wrd)
    
#         return Response({
#             'status': 'success',
#             'message': 'Successfully Fetched',
#             'data': data,
#         })
    

class GetAllUserDetails(generics.GenericAPIView):
    def get(self , request  ):
        data = {'wards': []}
    
        wards = ward.objects.all().order_by("wardName")
    
        for w in wards:
            wrd = {'ward': w.wardName, 'healthPosts': []}
    
            health_posts = healthPost.objects.filter(ward=w)
            for hp in health_posts:
                areaData = area.objects.filter(healthPost_id = hp.id).values("areas")
                areaList =  [item["areas"] for item in areaData]
                health_post_info = {'healthPost': hp.healthPostName,'areaList':areaList, 'sections': []}
    
                sections = section.objects.filter(healthPost=hp)
                for sec in sections:
                    section_info = {'sectionName': sec.sectionName, 'anms': [],}
    
                    # ANMs
                    # anms = CustomUser.objects.filter(section_id=sec.id, groups__name="healthworker")
                    anms = CustomUser.objects.filter(userSections__in=[sec], groups__name="healthworker")
    
                    for anm in anms:
                        anm_info = {'anmName': anm.name, 'chvs': []}
    
                        # CHVs under the ANM
                        chvs = CustomUser.objects.filter(ANM_id = anm.id,groups__name="CHV-ASHA")
                        for chv in chvs:
                            chv_info = {'chvName': chv.name}
                            anm_info['chvs'].append(chv_info)
    
                        section_info['anms'].append(anm_info)
    
                    health_post_info['sections'].append(section_info)
    
                wrd['healthPosts'].append(health_post_info)
    
            data['wards'].append(wrd)
    
        return Response({
            'status': 'success',
            'message': 'Successfully Fetched',
            'data': data,
        })