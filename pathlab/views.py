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
        """
        The function `get_queryset` filters the `familyMembers` objects based on the health post and
        blood collection location.
        :return: a queryset of family members who belong to the health post of the currently logged in
        user and whose blood collection location is either "center" or "Home".
        """
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
        """
        The function `get_queryset` filters the `familyMembers` objects based on the health post and
        blood collection location.
        :return: a queryset of family members who belong to a specific health post and have their blood
        collection location set to either "center" or "Home".
        """
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
        """
        The function retrieves a PatientPathlab instance based on the provided id and returns a response
        with the serialized data.
        
        """
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
        """
        The function `patch` updates a specific instance of the `PatientPathlab` model with the provided
        data and returns a success message if the update is successful, or an error message if there are
        any validation errors.
    
        """
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
        



        



