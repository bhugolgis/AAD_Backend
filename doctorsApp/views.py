from django.shortcuts import render
from rest_framework import generics, permissions
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from database.models import *
from doctorsApp.serializers import *
from rest_framework.permissions import IsAuthenticated , AllowAny

from rest_framework.pagination import PageNumberPagination

from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
            updateFmailyMember = familyMembers.objects.filter(id = patient_family_member_id)
            updateFmailyMember.update(isLabTestAdded = True)
            # updateFamilyHead = familyHeadDetails.objects.filter(id =updateFmailyMember[0].familyHead_id ).update(isLabTestAdded = True)
            
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
        # queryset = PatientPathlab.objects.select_related('patientFamilyMember__family_head_member')
        # return PatientPathlab.objects.all()
        return PatientPathlab.objects.select_related('patientFamilyMember__familyHead')
    
    
from django.shortcuts import get_object_or_404

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewPatientsLabTestViewDetails(request, pk):
    comDet = get_object_or_404(PatientPathlab, patientFamilyMember_id=int(pk))
    serializer = PatientPathlabSerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewPatientsMedicalOffConsultancyView(request, pk):
    comDet = get_object_or_404(MedicalOfficerConsultancy, MoPatientsConsultancy_id=int(pk))
    serializer = MedicalOfficerConsultancySerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})





    
    
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
    return pagination.get_paginated_response(serializer.data)



from django.shortcuts import get_object_or_404

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewFamilyDetails(request, pk):
    comDet = get_object_or_404(familyHeadDetails, id=int(pk))
    serializer = FamilyHeadDetailsSerializer(comDet)
    testData  = serializer.data
    testData["family_head_member"][0]["test"]="45646546546456"
    print(testData["family_head_member"][0]["test"])
    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})



@swagger_auto_schema(
    method='post',
    request_body=MedicalOfficerAdviceSerializer,
    manual_parameters=[
        openapi.Parameter(
            'patients_id',
            openapi.IN_PATH,
            description='Patient ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ]
)
@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def medicalOfficerAdviceView(request, patients_id):
    
        # Retrieve the instance you want to update
    medical_officer_consultancy = MedicalOfficerConsultancy.objects.filter(MoPatientsConsultancy_id=patients_id,isCompleted=True)
    if medical_officer_consultancy.exists():
        
        return Response({"error": "Patient Already Attended"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Deserialize the data from the request
        serializer = MedicalOfficerAdviceSerializer(instance=medical_officer_consultancy, data=request.data)

        if serializer.is_valid():
            # Save the updated data
            serializer.save()
            # addInPrimary = PrimaryConsultancy(PriPatientsConsultancy_id = patients_id,ReferByMedicalOfficer_id = request.user.id)
            # addInPrimary.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='post',
    request_body=MedicalOfficerReferalAdviceSerializer,
    manual_parameters=[
        openapi.Parameter(
            'patients_id',
            openapi.IN_PATH,
            description='Patient ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ]
)
@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def medicalOfficerReferalAdviceView(request, patients_id):
    
        # Retrieve the instance you want to update
    medical_officer_consultancy = MedicalOfficerConsultancy.objects.filter(MoPatientsConsultancy_id=patients_id,isCompleted=True)
    if medical_officer_consultancy.exists():
        
        return Response({"error": "Patient Already Attended"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        patientsPathLabReport = request.data["patientsPathLabReport"]
        PriDoctor_name = request.data["PriDoctor_name"]
        referedTo = request.data["referedTo"]
        Prispecialization = request.data["Prispecialization"]

        addInPrimary = PrimaryConsultancy(PriassignedDoctor_id = referedTo ,PriPatientsConsultancy_id = patients_id,ReferByMedicalOfficer_id = request.user.id,PriPatientsPathReport_id =patientsPathLabReport,PriDoctor_name = PriDoctor_name,Prispecialization=Prispecialization,  )
        addInPrimary.save()
        updateStatus = MedicalOfficerConsultancy.objects.filter(MoPatientsConsultancy_id=patients_id).update(isCompleted=True)

        return Response({"status": "success","message":"Successfully Patient Refer to Primary Health Care Doctor."}, status=status.HTTP_200_OK)







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

    
    
    
    

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewFamilyMemberView(request, pk):
    comDet = get_object_or_404(familyMembers, id=int(pk))
    serializer = FamilyMemberDetailsSerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewMedicalOfficerConsaltancyView(request, patients_id):
    comDet = get_object_or_404(MedicalOfficerConsultancy, MoPatientsConsultancy_id=int(patients_id))
    serializer = MedicalOfficerConsultancySerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewPrimaryConsultancyView(request, patients_id):
    comDet = get_object_or_404(PrimaryConsultancy, PriPatientsConsultancy_id=int(patients_id))
    serializer = PrimaryConsultancySerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewSecondaryConsultancyView(request, patients_id):
    comDet = get_object_or_404(SecondaryConsultancy, SecPatientsConsultancy_id=int(patients_id))
    serializer = SecondaryConsultancySerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})



@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewTertiaryConsultancyView(request, patients_id):
    comDet = get_object_or_404(TertiaryConsultancy, TerPatientsConsultancy_id=int(patients_id))
    serializer = TertiaryConsultancySerializer(comDet)
    testData  = serializer.data

    return Response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})




@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def PatientsForPrimaryDoctorList(request):
    pagination = PageNumberPagination()
    pagination.page_size = 10
    
    comDet = PrimaryConsultancy.objects.filter(PriassignedDoctor_id=request.user.id)

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)
    
    # Serialize the paginated queryset
    serializer = ListPrimaryConsultancyPatientsSerializer(page_queryset, many=True)
    
    # Return the paginated response
    return pagination.get_paginated_response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})    # return Response({"status":"success","message":"Successfully Fetched","data":serializer.data})


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def PatientsForSecondaryDoctorList(request):
    pagination = PageNumberPagination()
    pagination.page_size = 10
    
    comDet = SecondaryConsultancy.objects.filter(SecSecassignedDoctor_id=request.user.id)

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)
    
    # Serialize the paginated queryset
    serializer = ListSecondaryConsultancyPatientsSerializer(page_queryset, many=True)
    
    # Return the paginated response
    return pagination.get_paginated_response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})    # return Response({"status":"success","message":"Successfully Fetched","data":serializer.data})



@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def PatientsForTertairyDoctorList(request):
    pagination = PageNumberPagination()
    pagination.page_size = 10
    
    comDet = TertiaryConsultancy.objects.filter(TerassignedDoctor_id=request.user.id)

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)
    
    # Serialize the paginated queryset
    serializer = ListTertiaryConsultancyPatientsSerializer(page_queryset, many=True)
    
    # Return the paginated response
    return pagination.get_paginated_response({"status": "success", "message": "Successfully Fetched", "data": serializer.data})    # return Response({"status":"success","message":"Successfully Fetched","data":serializer.data})
