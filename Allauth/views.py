from django.shortcuts import render
from django.http import JsonResponse
from knox.models import AuthToken
from database.models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import generics,permissions
from django_filters.rest_framework import DjangoFilterBackend 
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from rest_framework.parsers import JSONParser,MultiPartParser,FileUploadParser,FormParser
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import generics, status
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated , AllowAny,IsAdminUser
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from drf_extra_fields.fields import Base64ImageField
from datetime import datetime, timedelta
from django.db.models import Count
from adminportal.serializers import *
from adminportal.permissions import *
from healthworker.permissions import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from adminportal.permissions import IsMOH
from django.contrib.auth.hashers import check_password
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q


class GetDailyCountOfSurvey(generics.GenericAPIView):
    # serializer_class = AreaSerialzier
    # permission_classes = [IsAuthenticated]

    def get(self, request ,id):
        today = datetime.now().date()

        # Count familyHeadDetails objects for today
        familydailycount = familyHeadDetails.objects.filter(created_date__date=today).count()        # data = area.objects.filter(healthPost__id= id )
        familyMemberdailycount = familyMembers.objects.filter(created_date__date=today).count()        # data = area.objects.filter(healthPost__id= id )

        # serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":{"familydailycount":familydailycount,"familyMemberdailycount":familyMemberdailycount}} , status= 200)



class GetLabTestDashboardCount(generics.GenericAPIView):
    # serializer_class = AreaSerialzier
    # permission_classes = [IsAuthenticated]

    def get(self, request ,id):
        today = datetime.now().date()

        # Count familyHeadDetails objects for today
        testOpintmentDaily = PatientPathlab.objects.filter(created_date__date=today,PatientSampleTaken=False).count()        # data = area.objects.filter(healthPost__id= id )
        dailyTestReceived = PatientPathlab.objects.filter(created_date__date=today).count()        # data = area.objects.filter(healthPost__id= id )
        testResultAwaited = PatientPathlab.objects.filter(created_date__date=today,PatientSampleTaken=True,isCompleted=False).count()        # data = area.objects.filter(healthPost__id= id )
        citizenRejectedLabTestCount = PatientPathlab.objects.filter(citizenRejectedLabTest=True,isCompleted=False).count()        # data = area.objects.filter(healthPost__id= id )



        # familyMemberdailycount = familyMembers.objects.filter(created_date__date=today).count()        # data = area.objects.filter(healthPost__id= id )

        # serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":{"testOpintmentDaily":testOpintmentDaily,"dailyTestReceived":dailyTestReceived,"testResultAwaited":testResultAwaited,"citizenRejectedLabTestCount":citizenRejectedLabTestCount}} , status= 200)


class GetDashboardThree(generics.GenericAPIView):
    # serializer_class = AreaSerialzier
    # permission_classes = [IsAuthenticated]

    def get(self, request ,id):
        today = datetime.now().date()

        # Count familyHeadDetails objects for today
        PrimaryConsultancyCount = PrimaryConsultancy.objects.all().count()        # data = area.objects.filter(healthPost__id= id )
        SecondaryConsultancyCount = SecondaryConsultancy.objects.all().count()        # data = area.objects.filter(healthPost__id= id )
        TertiaryConsultancyCount = TertiaryConsultancy.objects.all().count()        # data = area.objects.filter(healthPost__id= id )

        # familyMemberdailycount = familyMembers.objects.filter(created_date__date=today).count()        # data = area.objects.filter(healthPost__id= id )

        # serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":{"PrimaryConsultancyCount":PrimaryConsultancyCount,"SecondaryConsultancyCount":SecondaryConsultancyCount,"TertiaryConsultancyCount":TertiaryConsultancyCount}} , status= 200)


class AddlabtestdeatilsAPI(generics.GenericAPIView):
    serializer_class = Addlabtestserializer
    parser_classes = [MultiPartParser]

    def post(self , request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                    "status": "success",
                    "message": "Successfully added.",
                    "data": serializer.data,
                })
        else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)


class GetWardListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]
    serializer_class = WardSerialzier
    queryset = ward.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("wardName",)

class GethealthPostNameListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]
    serializer_class = healthPostSerializer
    # queryset = healthPost.objects.all()
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ("ward__id",)


    def get(self, request ,id):
        data = healthPost.objects.filter(ward__id= id )
        serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":serializer,} , status= 200)


class GetHealthPostAreasAPI(generics.GenericAPIView):
    serializer_class = AreaSerialzier
    
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]

    def get(self, request ,id):
        data = area.objects.filter(healthPost__id = id )
        serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":serializer,} , status= 200)
    


class updateAreaAPI(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]
    serializer_class = UpdateAreaSerializer

    def patch(self, request ,id):
        try:
            instance = area.objects.get(id= id )
        except:
            return Response({
                "status":"error",
                "message" : 'area ID not found',
            } , status=400)
        serializer = self.get_serializer(instance , data= request.data , partial = True)
        if serializer.is_valid():
            serializer.save()

            return Response({ "status":"success",
                    "message" : 'data updated successfully',} , status= 200)
        
        else:
            key, value = list(serializer.errors.items())[0]
            error_message = value[0]
            return Response({'message': error_message, 
                            'status' : 'error'}, status=400)
    
class GetWardAreasAPI(generics.ListAPIView):
    serializer_class = AreaSerialzier
    pagination_class = LimitOffsetPagination
    model = serializer_class.Meta.model
    filter_backends = (filters.SearchFilter,)
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]


    def get_queryset(self ):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        wardName = self.kwargs.get('wardName')
        queryset = self.model.objects.filter(healthPost__ward__wardName= wardName )
        search_terms = self.request.query_params.get('search', None)
        if search_terms:
            queryset = queryset.filter(healthPost__healthPostName__icontains=search_terms)
                                       

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

     
    
class GetSectionListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]
    serializer_class = sectionSerializer

    def get(self, request ,id):
        data = section.objects.filter(healthPost__id= id )
        serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":serializer,} , status= 200)
    


class updateSectionAPI(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]
    serializer_class = UpdateSectionSerializer

    def patch(self, request ,id):
        try:
            instance = section.objects.get(id= id )
        except:
            return Response({
                "status":"error",
                "message" : 'section ID not found',
            } , status=400)
        serializer = self.get_serializer(instance , data= request.data , partial = True)
        if serializer.is_valid():
            serializer.save()

            return Response({ "status":"success",
                    "message" : 'data updated successfully',} , status= 200)
        
        else:
            key, value = list(serializer.errors.items())[0]
            error_message = value[0]
            return Response({'message': error_message, 
                            'status' : 'error'}, status=400)
    

class GetWardSectionListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker | IsMOH | IsCHV_ASHA]
    serializer_class = sectionSerializer
    pagination_class = LimitOffsetPagination
    model = serializer_class.Meta.model
    filter_backends = (filters.SearchFilter,)
  
    

    def get_queryset(self ):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        # group = self.kwargs.get('group')
        wardName = self.kwargs.get('wardName')
        # print(group , wardName)
        # ward_id= self.request.user.ward.id
        queryset = self.model.objects.filter(healthPost__ward__wardName= wardName )
   
        search_terms = self.request.query_params.get('search', None)
        if search_terms:
            queryset = queryset.filter(healthPost__healthPostName__icontains=search_terms)
                                       

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



class GetDispensaryListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated , IsAdmin | IsHealthworker ]
    serializer_class = getDispensarySerializer
    # queryset = dispensary.objects.filter()
    model = serializer_class.Meta.model
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ("ward__wardName", "dispensaryName" )

    def get_queryset(self):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        id = self.kwargs.get('id')
        queryset = self.model.objects.filter(ward__id = id)

        return queryset

class InsertAmoAPI(generics.GenericAPIView):
    serializer_class = AMoRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = InsertAmoSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='amo')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InsertPrimaryHealthCareDoctorAPI(generics.GenericAPIView):
    serializer_class = PrimaryHealthCareRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = ViewPrimaryHealthCareSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='PrimaryHealthCareDoctor')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertSpecialityHealthCareDoctorAPI(generics.GenericAPIView):
    serializer_class = SpecialityHealthCareRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = ViewSpecialHealthCareSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='SpecialityHealthCareDoctor')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertMedicalCollegeHealthCareDoctorAPI(generics.GenericAPIView):
    serializer_class = MedicalCollegeHealthCareRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = ViewMedicalCollegeSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='MedicalCollegeHealthCareDoctor')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertMoAPI(generics.GenericAPIView):
    serializer_class = MoRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = InsertAmoSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='mo')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertphccAPI(generics.GenericAPIView):
    serializer_class = HccRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = ViewPrimaryHealthCareSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='phcc')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertshccAPI(generics.GenericAPIView):
    serializer_class = HccRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = ViewPrimaryHealthCareSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='shcc')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertthccAPI(generics.GenericAPIView):
    serializer_class = HccRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = ViewPrimaryHealthCareSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='thcc')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertSupervisorAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = RegisterSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='supervisor')
                user.groups.add(group)

                return Response({
                    "status": "success",
                    "message": "Successfully Registered.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertHealthWorkerAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = RegisterSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='healthworker')
                user.groups.add(group)
                addSupervisor = CustomUser.objects.filter(id= user.id).update(supervisor_id = request.user.id)

                return Response({
                    "status": "success",
                    "message": "Successfully Inserted.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class InsertCHV_ASHA_API(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = RegisterSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='CHV/ASHA')
                user.groups.add(group)
                addSupervisor = CustomUser.objects.filter(id= user.id).update(supervisor_id = request.user.id)

                return Response({
                    "status": "success",
                    "message": "Successfully Inserted.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InsertPhlebotomistAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                customuser = serializer.validated_data
                data = RegisterSerializer(customuser, context=self.get_serializer_context()).data

                group = Group.objects.get(name='phlebotomist')
                user.groups.add(group)
                addSupervisor = CustomUser.objects.filter(id= user.id).update(supervisor_id = request.user.id)

                return Response({
                    "status": "success",
                    "message": "Successfully Inserted.",
                    "data": data,
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                "status": "error",
                "message": "Error in Field " + str(ex),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class InsertUsers(generics.GenericAPIView):
#     # permission_classes = [permissions.IsAuthenticated,]
#     serializer_class = AddUserSerializer
#     parser_classes = [MultiPartParser]


#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         # print(request.data["name"], request.data)
        
#         try:
#             if serializer.is_valid():
#                 group = Group.objects.get(name=serializer.validated_data.get("group"))
                
#                 user = serializer.save()
#                 customuser = serializer.validated_data
#                 data = RegisterSerializer(customuser, context=self.get_serializer_context()).data
#                 user.groups.add(group)
                
#                 addSupervisor = CustomUser.objects.filter(id= user.id).update(supervisor_id = request.user.id)

#                 return Response({
#                     "status": "success",
#                     "message": "Successfully Inserted.",
#                     "data": data,
#                 })
#             else:
#                 return Response({
#                     "status": "error",
#                     "message": "Validation error",
#                     "errors": serializer.errors,
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as ex:
#             return Response({
#                 "status": "error",
#                 "message": "Error in Field " + str(ex),
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




phoneregex = r'^[6-9]\d{9}$'
emailregex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
import re
def checkemail(email):
 
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(emailregex, email)):
        # print("Valid Email")
        return True
    else:
        # print("Invalid Email")
        return False

def checkphone(phone):
 
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(phoneregex, phone)):
        # print("Valid Phonenumber")
        return True
 
    else:
        # print("Invalid Email")
        return False

@swagger_auto_schema(method='POST', request_body=SendEmailOrPhoneSerializer)
@api_view(['Post'])
# @permission_classes((IsAuthenticated, ))
def SendOtp(request):
    # comDet = EligibilityInfo.objects.get(user_id=request.user.id)
    chkString = request.data["phoneNumber"]
    if checkphone(chkString):
        chkemailExist = CustomUser.objects.filter(phoneNumber =request.data["phoneNumber"])
        if chkemailExist:
            # pass
            userdata={}
            userdata["name"] = chkemailExist[0].name
            userdata["phoneNumber"] = chkemailExist[0].phoneNumber
            import string
           

            random = "0000"
            # random =  ''.join(choice(chars) for _ in range(4))
            userdata["otp"] = random
            checkInOtp = sendOtp.objects.filter(registerUser_id = chkemailExist[0].id)
            if checkInOtp:
                updateOTP = sendOtp.objects.filter(registerUser_id = chkemailExist[0].id).update(otp = random)
                # otpsendstatus = ForgotPasswordEmail(userdata)
                return Response({"status":"sucess","message":"OTP Sent on Registered Phone Number"})

            else:
                saveOtp = sendOtp(otp = random,registerUser_id = chkemailExist[0].id)
                saveOtp.save()
                # otpsendstatus = ForgotPasswordEmail(userdata)
                return Response({"status":"sucess","message":"OTP Sent on Registered Phone Number."})

        else:
            return Response({"status":"error","message":"User Not Registered With this Phone Number."})


    else:
        # if checkphone(chkString):
        #     pass
        # else:
        #     print("invalid Phone Number")
        return Response({"status":"error","message":"Invalid Phone Number."})




class CheckOtp(generics.GenericAPIView):
    serializer_class = NewForgotPasswordSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # customuser = serializer.validated_data
            checkUserExists = CustomUser.objects.filter(phoneNumber=request.data["phoneNumber"])
            if checkUserExists:
                userExists =  CustomUser.objects.get(id = checkUserExists[0].id)

                _, token = AuthToken.objects.create(userExists)
                checkOtp  = sendOtp.objects.filter(registerUser_id =checkUserExists[0].id,otp = request.data["otp"])
                if checkOtp:
                        
                    return Response({
                        "status":"success",
                        "message" : "User is Valid ,Please Set Your Password",
                        "token":token
                        })
                else:
                    return Response({
                    "status":"error",
                    "message":"Invalid Otp."
                
                    })

            else:
                return Response({
                    "status":"error",
                    "message":"User Not Found."
                    })
        else:

            return Response({
                "status":"error",
                "message":serializer.errors
             
                })              



class LoginWithOtp(generics.GenericAPIView):
    serializer_class = NewForgotPasswordSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        data ={}
        if serializer.is_valid():
            # customuser = serializer.validated_data
            checkUserExists = CustomUser.objects.filter(phoneNumber=serializer.validated_data('phoneNumber'))
            if checkUserExists:
                userExists =  CustomUser.objects.get(id = checkUserExists[0].id)

                _, token = AuthToken.objects.create(userExists)
                checkOtp  = sendOtp.objects.filter(registerUser_id =checkUserExists[0].id,otp = request.data["otp"])
                if checkOtp:
                    data = ViewSupervisorSerializer(userExists,context=self.get_serializer_context()).data
                # data["user_group"] = "healthworker"

                    data["user_group"]  = userExists.groups.values_list('name', flat=True)[0]
                    DeleteOtp  = sendOtp.objects.filter(registerUser_id =checkUserExists[0].id,otp = request.data["otp"]).delete()

                    return Response({
                        "status":"success",
                        "message" : "Login Successfully",
                        "data":data,
                        "token":token
                        })
                else:
                    return Response({
                    "status":"error",
                    "message":"Invalid Otp."
                    })

            else:
                return Response({
                    "status":"error",
                    "message":"User Not Found."
                    })
        else:

            return Response({
                "status":"error",
                "message":serializer.errors
             
                })              




class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("newpassword"))
            self.object.save()

            sendOtp.objects.filter(registerUser_id = self.request.user.id).delete()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully'
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserGroupFilterView(generics.ListAPIView):
    """
    Retrieve a list of users based on their group membership.
    ---
    parameters:
      - name: group
        in: query
        description: Group name for filtering users.
        required: false
        type: string
    """
    serializer_class = ViewSupervisorSerializer
    
    def get_queryset(self):
        group_name = self.request.query_params.get('group')
        if group_name:
            return CustomUser.objects.filter(groups__name=group_name)
        return CustomUser.objects.all()







# Create your views here.
class CustomLoginAPI(generics.GenericAPIView):

    
    serializer_class = LoginSerializer
    parser_classes = [MultiPartParser]

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customuser = serializer.validated_data
            _, token = AuthToken.objects.create(customuser)
            status = CustomUser.objects.filter(id=customuser.id)
 
            groups=customuser.groups.values_list('name',flat = True)
            data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
            # print(groups)
            if groups[0] =="supervisor":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "supervisor"
            elif groups[0] =="healthworker":
                if status[0].otpChecked==False:
                    return Response({
                    "status":"error",
                    "message":"Phone Number not Verified"
                
                    })
                    
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "healthworker"
                
            elif groups[0] =="amo":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "amo"
            elif groups[0] =="mo":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "mo"

            elif groups[0] =="PrimaryHealthCareDoctor":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "PrimaryHealthCareDoctor"
                
            elif groups[0] =="SpecialityHealthCareDoctor":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "SpecialityHealthCareDoctor"

            elif groups[0] =="MedicalCollegeHealthCareDoctor":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "MedicalCollegeHealthCareDoctor"

            else:

                data = AdminSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "admin"


  
            return Response({
                "status":"success",
                "message" : "Login Successfully",
                "data":data,
                "token":token
                })
        else:

            return Response({
                "status":"error",
                "message":serializer.errors["non_field_errors"][0]
             
                } , status=400 )
        
class AddWardAPI(generics.GenericAPIView):
    serializer_class = AddwardSerializer
    parser_classes = [MultiPartParser]
    def post(self , request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Saved successfully',
                'status': 'success',
            } ,status=201)
        else:
            return Response({
                'message': serializer.errors,
                'status': 'error' ,
            } , status=400)
        

class AddDispensaryAPI(generics.GenericAPIView):
    serializer_class = AddDispensarySerializer
    parser_classes = [MultiPartParser]
    def post(self , request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Saved successfully',
                'status': 'success',
            } ,status=201)
        else:
            return Response({
                'message': serializer.errors,
                'status': 'error' ,
            } , status=400)

class AddHealthPostAPI(generics.GenericAPIView):
    serializer_class = AddHealthPostSerializer
    parser_classes = [MultiPartParser]
    def post(self , request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Saved successfully',
                'status': 'success',
            } ,status=201)
        else:
            return Response({
                'message': serializer.errors,
                'status': 'error' ,
            } , status=400)
        
class AddsectionAPI(generics.GenericAPIView):
    serializer_class = AddSectionSerializer
    parser_classes = [MultiPartParser]
    def post(self , request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Saved successfully',
                'status': 'success',
            } ,status=201)
        else:
            return Response({
                'message': serializer.errors,
                'status': 'error' ,
            } , status=400)

# class GetArea

class AddAreaAPI(generics.GenericAPIView):
    serializer_class = AddAreaSerializer
    parser_classes = [MultiPartParser]
    def post(self , request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Saved successfully',
                'status': 'success',
            } ,status=201)
        else:
            return Response({
                'message': serializer.errors,
                'status': 'error' ,
            } , status=400)  


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request):
        # try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user_data = serializer.validated_data
                group = user_data.groups.values_list("name", flat=True)[0]
                if serializer is not None:
                    try:
                        token = AuthToken.objects.filter(user=serializer.validated_data)
                        if group != 'admin':
                            token.delete()
                    except AuthToken.DoesNotExist:
                        pass
                    _, token = AuthToken.objects.create(serializer.validated_data)
                    if user_data.is_active:
                        if group == 'healthworker':
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'email': user_data.emailId,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'section_id' : user_data.section_id,
                                'ward' : user_data.section.healthPost.ward.wardName ,
                                'healthPostName' : user_data.section.healthPost.healthPostName,
                                'healthPostID' : user_data.section.healthPost.id,
                                'Group': group

                            }, status=200)                 
                        elif group == "phlebotomist":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'email': user_data.emailId,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'Group': group}, status=200)                   
                        elif group == "supervisor":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'email': user_data.emailId,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'Group': group}, status=200)                     
                        elif group == "amo":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'email': user_data.emailId,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'healthPostName' : user_data.health_Post.healthPostName,
                                'healthPostID' : user_data.health_Post.id,
                            

                                'Group': group}, status=200)
                        elif group == "mo":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'dispensaryId':user_data.dispensary.id,
                                'dispensaryName':user_data.dispensary.dispensaryName,
                                'Group': group}, status=200)            
                        elif group == "phcc":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'healthCareName':user_data.HealthCareCenters.healthCareName,
                                'HhealthcareAddress':user_data.HealthCareCenters.HhealthcareAddress,
                                'healthCareContactNumber':user_data.HealthCareCenters.healthCareContactNumber,
                                'healthCareType':user_data.HealthCareCenters.healthCareType[0],

                                # 'sectionId':user_data.section.id,
                                # 'sectionName':user_data.section.sectionName,
                                'Group': group}, status=200)
                        elif group == "shcc":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'healthCareName':user_data.HealthCareCenters.healthCareName,
                                'HhealthcareAddress':user_data.HealthCareCenters.HhealthcareAddress,
                                'healthCareContactNumber':user_data.HealthCareCenters.healthCareContactNumber,
                                'healthCareType':user_data.HealthCareCenters.healthCareType[0],

                                'Group': group}, status=200)
                        elif group == "thcc":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'healthCareName':user_data.HealthCareCenters.healthCareName,
                                'HhealthcareAddress':user_data.HealthCareCenters.HhealthcareAddress,
                                'healthCareContactNumber':user_data.HealthCareCenters.healthCareContactNumber,
                                'healthCareType':user_data.HealthCareCenters.healthCareType[0],
                                'Group': group}, status=200)                        
                        elif group == "Family Head":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'Group': group
                                
                            })
                        elif group == "admin":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'Group': group
             
                            })
                        elif group == "MOH":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'ward_id' : user_data.ward.id ,
                                'ward_name' : user_data.ward.wardName,
                                'Group': group
                            
                        })
                        elif group == "CHV-ASHA":
                            return Response({
                                'message': 'Login successful',
                                'Token': token,
                                'status': 'success',
                                'id': user_data.id,
                                'name' : user_data.name,         
                                'username': user_data.username,
                                'phoneNumber' : user_data.phoneNumber,
                                'section_id' : user_data.section_id,
                                'ward' : user_data.section.healthPost.ward.wardName ,
                                'healthPostName' : user_data.section.healthPost.healthPostName,
                                'healthPostID' : user_data.section.healthPost.id,
                                'Group': group
                            
                        })
                    else:
                        return Response({'status': 'error' ,
                                         'message': 'Your account is disabled'} , status=401)

            else:
                key, value = list(serializer.errors.items())[0]
                error_message = value[0]
                return Response({'message': error_message, 
                                'status' : 'error'}, status=400)
        # except:
        #     return Response({
        #         'message': 'Invalid Credentials',
        #         'status': 'failed'}, status=400)
            
            
            
class GetCoordPassword(generics.GenericAPIView):
    serializer_class = CoordPasswordSerializer
    def get(self, request, *args, **kwargs):
        
        query = CustomUser.objects.filter(groups__name = 'healthworker')  
        lis = [] 
        for i in query:
            if check_password('Ncdcoord@123' , i.password):
                # i.set_password('Ncdanm@123')
                var = lis.append(i.phoneNumber) 

                # serializer = self.get_serializer( i , many = True ).data
        # print(lis)
        return Response(None)     
            
            
# class PrimaryHealthCareCentersView(generics.ListCreateAPIView):
#     queryset = PrimaryHealthCareCenters.objects.all()
#     serializer_class = PrimaryHealthCareCentersSerializer
#     permission_classes = [IsAdminUser]

# class PrimaryHealthCareCentersDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = PrimaryHealthCareCenters.objects.all()
#     serializer_class = PrimaryHealthCareCentersSerializer
#     permission_classes = [IsAdminUser]

# class SpecialityHealthCareCentersView(generics.ListCreateAPIView):
#     queryset = SpecialityHealthCareCenters.objects.all()
#     serializer_class = SpecialityHealthCareCentersSerializer
#     permission_classes = [IsAdminUser]

# class SpecialityHealthCareCentersDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = SpecialityHealthCareCenters.objects.all()
#     serializer_class = SpecialityHealthCareCentersSerializer
#     permission_classes = [IsAdminUser]

# class MedicalCollegeHealthCareCentersView(generics.ListCreateAPIView):
#     queryset = MedicalCollegeHealthCareCenters.objects.all()
#     serializer_class = MedicalCollegeHealthCareCentersSerializer
#     permission_classes = [IsAdminUser]

# class MedicalCollegeHealthCareCentersDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = MedicalCollegeHealthCareCenters.objects.all()
#     serializer_class = MedicalCollegeHealthCareCentersSerializer
#     permission_classes = [IsAdminUser]

         
            

class HealthCareCentersList(APIView):
    # @swagger_auto_schema(
    #     request_body=HealthCareCentersSerializer,
    #     responses={200: HealthCareCentersSerializer(many=True)}
    # )
    def get(self, request):
        healthcare_centers = HealthCareCenters.objects.all()
        serializer = HealthCareCentersSerializer(healthcare_centers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=HealthCareCentersSerializer,
        responses={201: HealthCareCentersSerializer()}
    )
    def post(self, request):
        serializer = HealthCareCentersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class HealthCareCentersDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return HealthCareCenters.objects.get(pk=pk)
#         except HealthCareCenters.DoesNotExist:
#             raise Http404
        

    def get(self, request, pk):
        healthcare_center = self.get_object(pk)
        serializer = HealthCareCentersSerializer(healthcare_center)
        return Response(serializer.data)

    def put(self, request, pk):
        healthcare_center = self.get_object(pk)
        serializer = HealthCareCentersSerializer(healthcare_center, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        healthcare_center = self.get_object(pk)
        healthcare_center.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
            


# Admin Portal API's
class GetCHV_ASHA_list(generics.GenericAPIView):
    serializer_class = CHV_ASHA_Serializer
    def get(self , request , id):
        try:
            user_list = CustomUser.objects.filter(ANM = id , groups__name = 'CHV-ASHA')
        except:
            return Response({
                'status': 'error' ,
                'message' : 'User ID is not found'
            } , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user_list , many = True).data
        return Response({
                'status': 'success' ,
                'message' : 'data fetched successfully',
                'data': serializer} , status=status.HTTP_200_OK)
    

