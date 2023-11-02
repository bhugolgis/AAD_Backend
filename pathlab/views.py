from django.shortcuts import render
from rest_framework import generics
from database.models import *
from .serializers import * 
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .pagination import LimitsetPagination
from rest_framework import status
from healthworker.permissions import Isphlebotomist




class GetCitizenBasicDetailsAPI(generics.ListAPIView):
    pagination_class = LimitsetPagination
    permission_classes = (IsAuthenticated , Isphlebotomist )
    serializer_class = GetCitizenBasicDetailsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['mobileNo' ,'name' , 'memberId']

    def get_queryset(self):
        queryset = familyMembers.objects.filter(area__healthPost_id = self.request.user.health_Post.id  , bloodCollectionLocation__in = ["center", "Home"])
    
        return queryset 
  



# Create your views here.
class GetPhleboFamilyMembersDetails(generics.ListAPIView):
    pagination_class = LimitsetPagination
    permission_classes = (IsAuthenticated , Isphlebotomist )
    # queryset = familyMembers.objects.filter( bloodCollectionLocation = "Center")
    serializer_class = GetPhleboFamilyMemberDetailSerializer  
    filter_backends = (filters.SearchFilter,)
    search_fields = ['mobileNo' ,'name' , 'memberId' , 'id' ]

    def get_queryset(self):
        queryset = familyMembers.objects.filter(area__healthPost_id = self.request.user.health_Post.id ,  bloodCollectionLocation__in = ["center", "Home"])
    
        return queryset 


# class PostBloodTestReport(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = PostBloodTestReportSerialzier
#     parser_classes = [MultiPartParser]

#     def post(self , request):
#         serializer = self.get_serializer(data = request.data)
#         if serializer.is_valid():
#             serializer.save(user = request.user)
#             return Response({'status' : 'success' , 
#                              'message' : 'data saved successfully'} , status= 200)
#         else:
#             key, value =list(serializer.errors.items())[0]
#             error_message = key+" , "+ value[0]
#             return Response({"status" : "error" ,
#                              "message" : error_message}, status= 400)
        


class GetPatientsDetailsAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  
    filter_backends = (filters.SearchFilter,)
    serializer_class = GetPatientsDetailsAPISerialzier
    # queryset = PatientsPathlab.objects.filter(patientFamilyMember =  )
    search_fields = ['patientFamilyMember__mobileNo' ,'patientFamilyMember__name' , 'patientFamilyMember__memberId' , 
                     'patientFamilyMember__id' , 'bookingVisitID' , 'patientID']

    def get(self , request, id):
        try:
            instance = PatientPathlab.objects.get(patientFamilyMember__id=id)
        except:
            return Response({'status': 'error',
                           'message': 'deatils not found'}, status=400)
        serializer = self.get_serializer(instance).data
        return Response({'status' :'success', 
                        'message' : 'data fetched successfully', 
                        'data' : serializer}, status=status.HTTP_200_OK)



class PostResponseLIMSAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated , Isphlebotomist]
    serializer_class = PostResponseLIMSAPISerialzier
    parser_classes = [MultiPartParser]
    def patch(self , request , id ):
        try:
            instance = PatientPathlab.objects.get(pk=id)
        except:
            return Response({'status': 'error',
                            'message': 'deatils not found'}, status=400)
        serializer = self.get_serializer(instance , data = request.data , partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status' :'success', 
                            'message' : 'data saved successfully'}, status= status.HTTP_201_CREATED)
        else:
            key, value =list(serializer.errors.items())[0]
            error_message = key+" , "+ value[0]
            return Response({"status" : "error" ,
                             "message" : error_message}, status= 400)
        



        



