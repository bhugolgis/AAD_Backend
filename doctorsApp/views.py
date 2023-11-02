from django.shortcuts import render
from rest_framework import generics, permissions
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from database.models import *
from doctorsApp.serializers import *
from rest_framework.permissions import IsAuthenticated , AllowAny

from rest_framework.pagination import PageNumberPagination


from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

class IsAllowedGroup(permissions.BasePermission):
    allowed_groups = ['amo', 'mo']  # Replace with the names of your allowed groups



class LabTestSuggestedCreateView(generics.GenericAPIView):
    serializer_class = PatientsPathlabSerializer
    permission_classes = (IsAuthenticated, IsAllowedGroup)
    # permission_classes = [IsAuthenticated]



    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}

        if serializer.is_valid():
            patient_family_member_id = request.data.get('patientFamilyMember')
            lab_test_suggested = request.data.get('LabTestSuggested')

            # Check if lab tests already added for the patient
            check_user_exists = PatientPathlab.objects.filter(patientFamilyMember_id=patient_family_member_id)
            
            if check_user_exists:
                return Response({
                    "status": "success",
                    "message": "Already added lab tests for the patient.",
                })

            # Create a new instance of PatientsPathlab
            insert_lab_test = PatientPathlab.objects.create(
                patientFamilyMember_id=patient_family_member_id,
                LabTestSuggested=lab_test_suggested,
                suggested_by_doctor=request.user
            )

            return Response({
                "status": "success",
                "message": "Lab tests added successfully.",
            })

        return Response({
            "status": "error",
            "message": serializer.errors,
        })
        


        

# class ListPatientsPathlabView(generics.ListAPIView):
#     serializer_class = ListPatientsPathlabSerializer

#     def get_queryset(self):
#         suggested_by_doctor_id = self.request.query_params.get('suggested_by_doctor_id', None)
#         patient_family_member_id = self.request.query_params.get('patient_family_member_id', None)

#         queryset = PatientsPathlab.objects.all()

#         if suggested_by_doctor_id is not None:
#             queryset = queryset.filter(suggested_by_doctor_id=suggested_by_doctor_id)
        
#         if patient_family_member_id is not None:
#             queryset = queryset.filter(patientFamilyMember_id=patient_family_member_id)

#         return queryset
from django_filters.rest_framework import DjangoFilterBackend


class ListPatientsPathlabView(generics.ListAPIView):
    serializer_class = ListPatientsPathlabSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_class = PatientsPathlabFilter
    # area = django_filters.CharFilter(field_name='', lookup_expr='exact')
    fields = ['patientFamilyMember__familyHead__area', 'suggested_by_doctor', 'LabTestSuggested', 'PatientSampleTaken', 'PathLab', 'ReportCheckByDoctor', 'LabTestReport', 'doctorRemarks', 'PathLabRemarks', 'response_date', 'created_date', 'isCompleted']

    def get_queryset(self):
        return PatientPathlab.objects.all()
    
    
    
    
@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def FamilyHeadList(request):
    pagination = PageNumberPagination()
    pagination.page_size = 10

    # Determine user's group (if authenticated)
    group = None
    if request.user.is_authenticated:
        group = request.user.groups.values_list("name", flat=True).first()

    # Filter family head details based on user's group (if authenticated)
    if group == "amo" and request.user.is_authenticated:
        comDet = familyHeadDetails.objects.filter(area__healthPost_id=request.user.health_Post_id)
    elif group == "mo" and request.user.is_authenticated:
        comDet = familyHeadDetails.objects.filter(area__dispensary_id=request.user.dispensary_id)
    else:
        comDet = familyHeadDetails.objects.all()

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)

    # Serialize the paginated queryset
    serializer = ListFamilyHeadDetailsSerializer(page_queryset, many=True)

    # Return the paginated response
    return pagination.get_paginated_response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})



from django.shortcuts import get_object_or_404

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewFamilyDetails(request, pk):
    comDet = get_object_or_404(familyHeadDetails, id=int(pk))
    serializer = FamilyHeadDetailsSerializer(comDet)
    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})



@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def PatientsForPrimaryDoctorList(request):
    pagination = PageNumberPagination()
    pagination.page_size = 10
    
    comDet = familyHeadDetails.objects.filter(user__health_Post=request.user.health_Post)

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)
    
    # Serialize the paginated queryset
    serializer = ListFamilyHeadDetailsSerializer(page_queryset, many=True)
    
    # Return the paginated response
    return pagination.get_paginated_response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})    # return Response({"status":"success","message":"Successfully Fetched","data":serializer.data})

    
    