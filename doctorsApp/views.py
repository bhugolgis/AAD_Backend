from django.shortcuts import render
from rest_framework import generics, permissions
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from database.models import PatientPathlab
from doctorsApp.serializers import PatientsPathlabSerializer,ListPatientsPathlabSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny

from rest_framework.pagination import PageNumberPagination

class IsAllowedGroup(permissions.BasePermission):
    allowed_groups = ['AMO', 'MO']  # Replace with the names of your allowed groups



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