from rest_framework import generics, permissions
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from database.models import *
from doctorsApp.serializers import *
from rest_framework.permissions import IsAuthenticated 
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
import requests
from pathlab.serializers import * 
from .permissions import IsMO
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination



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
            check_user_exists = PatientsPathlabrecords.objects.filter(patientFamilyMember_id= patient_family_member_id)
            
            if check_user_exists:
                return Response({
                    "status": "success",
                    "message": "Already added lab tests for the patient.",
                } , status=status.HTTP_400_BAD_REQUEST)

            # Create a new instance of PatientsPathlab
            updateFmailyMember = familyMembers.objects.filter(id = patient_family_member_id)
            updateFmailyMember.update(isLabTestAdded = True,isSampleCollected=True)
            # updateFamilyHead = familyHeadDetails.objects.filter(id =updateFmailyMember[0].familyHead_id ).update(isLabTestAdded = True)
            
            insert_lab_test = PatientsPathlabrecords.objects.create(
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
        


        

class ListPatientsPathlabView(generics.ListAPIView):
    serializer_class = ListPatientsPathlabSerializer

    def get_queryset(self):
        suggested_by_doctor_id = self.request.query_params.get('suggested_by_doctor_id', None)
        patient_family_member_id = self.request.query_params.get('patient_family_member_id', None)

        queryset = PatientsPathlabrecords.objects.all()

        if suggested_by_doctor_id is not None:
            queryset = queryset.filter(suggested_by_doctor_id=suggested_by_doctor_id)
        
        if patient_family_member_id is not None:
            queryset = queryset.filter(patientFamilyMember_id=patient_family_member_id)

        return queryset



class ListPatientsPathlabView(generics.ListAPIView):
    serializer_class = ListPatientsPathlabSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_class = PatientsPathlabFilter
    # area = django_filters.CharFilter(field_name='', lookup_expr='exact')
    fields = ['patientFamilyMember__familyHead__area', 'suggested_by_doctor', 'LabTestSuggested', 'PatientSampleTaken', 'PathLab', 'ReportCheckByDoctor', 'LabTestReport', 'doctorRemarks', 'PathLabRemarks', 'response_date', 'created_date', 'isCompleted']

    def get_queryset(self):
        # queryset = PatientPathlab.objects.select_related('patientFamilyMember__family_head_member')
        # return PatientPathlab.objects.all()
        return PatientsPathlabrecords.objects.select_related('patientFamilyMember__familyHead')
    
    
from django.shortcuts import get_object_or_404

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewPatientsLabTestViewDetails(request, pk):
    comDet = get_object_or_404(PatientsPathlabrecords, patientFamilyMember_id=int(pk))
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
        comDet = familyHeadDetails.objects.filter(area__healthPost_id=request.user.health_Post_id).order_by("-created_date")
    elif group == "mo" and request.user.is_authenticated:
        comDet = familyHeadDetails.objects.filter(area__dispensary_id=request.user.dispensary_id).order_by("-created_date")
    else:
        comDet = familyHeadDetails.objects.all().order_by("-created_date")

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)

    # Serialize the paginated queryset
    serializer = ListFamilyHeadDetailsSerializer(page_queryset, many=True)
    data = {'status': 'success',
        'message': 'Successfully Feteched',
        
        'data': serializer.data  # Include serialized data in the response
    }


#     # Return the paginated response
#     return pagination.get_paginated_response(data)

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def FamilyHeadList(request):
    pagination = PageNumberPagination()
    pagination.page_size = 150

    # Determine user's group (if authenticated)
    group = None
    if request.user.is_authenticated:
        group = request.user.groups.values_list("name", flat=True).first()

    # Filter family head details based on user's group (if authenticated)
    if group == "amo" and request.user.is_authenticated:
        comDet = familyHeadDetails.objects.filter(area__healthPost_id=request.user.health_Post_id).order_by("-created_date")
    elif group == "mo" and request.user.is_authenticated:
        comDet = familyHeadDetails.objects.filter(area__dispensary_id=request.user.dispensary_id).order_by("-created_date")
    else:
        comDet = familyHeadDetails.objects.all().order_by("-created_date")

    # Paginate the queryset
    page_queryset = pagination.paginate_queryset(comDet, request)

    # Serialize the paginated queryset
    serializer = ListFamilyHeadDetailsSerializer(page_queryset, many=True)

    # Manually create the paginated response data
    paginated_data = serializer.data

    # Manually create the response data
    data = {
        'status': 'success',
        'message': 'Successfully Fetched',
        'count': comDet.count(),  # Total number of objects (not just the paginated ones)
        'next': pagination.get_next_link(),  # Link to the next page (if applicable)
        'previous': pagination.get_previous_link(),  # Link to the previous page (if applicable)
        'data': paginated_data,  # Include serialized data for the current page
    }

    return Response(data)



from django.shortcuts import get_object_or_404

@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def ViewFamilyDetails(request, pk):
    comDet = get_object_or_404(familyHeadDetails, id=int(pk))
    serializer = FamilyHeadDetailsSerializer(comDet)
    testData  = serializer.data
    # Create a new dictionary with "status" key at the beginning
    response_data = {'status': 'success',"message":"Successfully Feteched."}

    # Update the dictionary with the serialized data
    response_data.update(serializer.data)
    return Response(response_data)

from rest_framework import filters

class ViewFamilysDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsMO)
    serializer_class = FamilyMemberDetailsSerializer  
    pagination_class = LimitOffsetPagination 
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ['name' , 'mobileNo' , "familyHead__mobileNo" ]

    def get_queryset(self , id ):
        # Filter the queryset based on the currently logged-in user
        queryset = familyMembers.objects.filter(area__dispensary_id= self.request.user.dispensary_id , familyHead__id = id ).order_by("-created_date")
     
        search_terms = self.request.query_params.get('search', None )
        if search_terms:
            queryset = queryset.filter(
                Q(name__icontains=search_terms) |
                Q(mobileNo__icontains=search_terms)|
                Q(familyHead__mobileNo__icontains=search_terms) )
        return queryset
    

    def get(self, request, id , *args, **kwargs):

        queryset = self.get_queryset(id)
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
    


class GetAllFamilysDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsMO)
    serializer_class = FamilyMemberDetailsSerializer 
    pagination_class = LimitOffsetPagination 
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ['name' , 'mobileNo'  ]

    def get_queryset(self  ):
        # Filter the queryset based on the currently logged-in user
        queryset = familyMembers.objects.filter(area__dispensary_id = self.request.user.dispensary_id ).order_by("-created_date")


        search_terms = self.request.query_params.get('search', None )
        if search_terms:
            queryset = queryset.filter(
                Q(name__icontains=search_terms) |
                Q(mobileNo__icontains=search_terms)|
                Q(familyHead__mobileNo__icontains=search_terms) )
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
    return pagination.get_paginated_response({"status": "success",
                                               "message": "Successfully Fetched",
                                                "data": serializer.data})    # return Response({"status":"success","message":"Successfully Fetched","data":serializer.data})

    
    
    
    

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



@api_view(['GET'])
def labTestsList(request):
    # Get the 'testName' parameter from the query string, if provided
    test_name = request.GET.get('testName', None)

    # Filter lab tests based on the provided 'testName'
    if test_name:
        lab_tests = LabTests.objects.filter(testName__icontains=test_name)
    else:
        lab_tests = LabTests.objects.all()

    # Serialize the queryset
    serializer = LabTestsSerializer(lab_tests, many=True)
    
    responsedata = {"status":"success",
                    "message":"Successfully Fetched"}
    responsedata["data"]=serializer.data    
    
    # Return the serialized data as the API response
    return Response(responsedata)



class LIMSBookPatientAPI(generics.GenericAPIView):

    serializer_class = BookPatientSerializer
    # parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated ,IsMO]

    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        try:
            instance = familyMembers.objects.get(pk=request.data["id"])
        except:
            return Response({'status': 'error',
                            'message': 'Family Member details not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            pathlab_instance = PatientsPathlabrecords.objects.filter(patientFamilyMember=request.data["id"]).exists()
            if pathlab_instance:
                return Response({'status': 'error', 
                                    'message': "patient already book an appointment"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'status': 'error',
                            'message': 'Family Member details not found'}, status=status.HTTP_400_BAD_REQUEST)


        if serializer.is_valid():
            url= "http://ilis.krsnaadiagnostics.com/api/KDL_LIS_APP_API/BookPatient"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json'}

            payload = json.dumps({
                "authKey": "05436EFE3826447DBE720525F78A9EEDBMC",
                "CentreID": "112084",
                "RegisteredDate": serializer.validated_data.get('RegisteredDate'),
                "PRNNo": serializer.validated_data.get('PRNNo'),
                "PatientCategory": serializer.validated_data.get('PatientCategory'),
                "PatientType": serializer.validated_data.get('PatientType'),
                "RefDrCode": serializer.validated_data.get('RefDrCode'),
                "refDrName":serializer.validated_data.get('refDrName'),
                "RefLabCode": serializer.validated_data.get('RefLabCode'),
                "PatientName": serializer.validated_data.get('PatientName'),
                "Age": serializer.validated_data.get('Age'),
                "BirthDate": serializer.validated_data.get('BirthDate'),
                "PaymentAmount":serializer.validated_data.get('PaymentAmount'),
                "CreatedBy": serializer.validated_data.get('CreatedBy'),
                "AgeUnit": serializer.validated_data.get('AgeUnit'),
                "Gender": serializer.validated_data.get('Gender'),
                "PatientAddress": serializer.validated_data.get('PatientAddress'),
                "IdentityNumber": serializer.validated_data.get('IdentityNumber'),
                "MobileNumber": serializer.validated_data.get('MobileNumber'),
                "HisUniquePatientCode": serializer.validated_data.get('HisUniquePatientCode'),
                "HisHospitalRefNo": serializer.validated_data.get('HisHospitalRefNo'),
                "Booking_TestDetails": serializer.validated_data.get('Booking_TestDetails'),})

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = json.loads(response.content)
                if response_data.get("hisResult" , True):
                    pathlab_serializer = PostResponseLIMSAPISerialzier(data = {
                        "patientFamilyMember" : request.data["id"] , 
                        "bookingVisitID" : response_data.get("bookingVisitID") ,
                        "puid" : response_data.get("puid") ,
                        "patientID" : response_data.get("patientID") ,
                        "CentreID" : serializer.validated_data.get("RefLabCode") ,
                        "LabTestSuggested" : serializer.validated_data.get('Booking_TestDetails') , 
                        "centerName" : serializer.validated_data.get('centerName')
                    }  )
                    if pathlab_serializer.is_valid():
                        pathlab_serializer.save()
                        return Response(json.loads(response.content) , status=response.status_code)
                    else:
                        # key, value =list(serializer.errors.items())[0]
                        # error_message = key+" , "+ value[0]
                        return Response({"status" : "error" ,
                                        "message" : pathlab_serializer.errors}, status= 400) 
                else:
                    mesaage = response_data.get("hisMessage")
                    return Response({"status" : "error" ,
                                        "message" : mesaage}, status= 400)
            else:
                return Response(json.loads(response.content) , status=response.status_code) 
            
        else:
            key, value = list(serializer.errors.items())[0]
            print(key , value)
            error_message = key+" , "+ value[0]
            return Response({'message': error_message, 
                            'status' : 'error'}, status=400)
        

class LIMSPatientRegisterAPI(generics.GenericAPIView):
    serializer_class = LIMSPatientRegisterSerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url = "https://kdl.techjivaaindia.in/api/LISMobileAPP_API/LIS_RegisterPatient"

            payload = json.dumps({
            "adharcard": serializer.validated_data.get('adharcard'),
            "acceptTermConditionPrivacyPolicy": "True",
            "addressType": "Home",
            "age" : serializer.validated_data.get('age'),
            "ageUnit": "Y",
            "authKey": "E0DE107A7CA04A6CA7FBB6DAE89B4F3A",
            "birthdate": serializer.validated_data.get('birthdate'),
            "bloodgroup": serializer.validated_data.get('bloodgroup'),
            "emailid": serializer.validated_data.get('emailid'),
            "gender": serializer.validated_data.get('gender'),
            "labID": serializer.validated_data.get('labID'),
            "mobileno": serializer.validated_data.get('mobileno'),
            "name": serializer.validated_data.get('name'),
            "pincode": serializer.validated_data.get('pincode'),
            "registerById": "self",
            "registerByName" :serializer.validated_data.get('name'),
            "title" : serializer.validated_data.get('title'),
            "userIdProof": "Aadhaar No.",
            })

            print(payload)
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',}
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = json.loads(response.content)
                print(response_data)
                return Response(json.loads(response.content) , status=response.status_code)
        

        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
    


class LIMSHomeBookPatientAPI(generics.GenericAPIView):

    serializer_class = HomeBookPatientSerializer
    # parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated ,IsMO]

    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        try:
            instance = familyMembers.objects.get(pk=request.data["id"])
        except:
            return Response({'status': 'error',
                            'message': 'Family Member details not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            pathlab_instance = PatientsPathlabrecords.objects.filter(patientFamilyMember=request.data["id"]).exists()
            if pathlab_instance:
                return Response({'status': 'error', 
                                    'message': "patient already book an appointment"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'status': 'error',
                            'message': 'Family Member details not found'}, status=status.HTTP_400_BAD_REQUEST)


        if serializer.is_valid():
            url= "https://android.techjivaaindia.in/KRASNA/BookAppointmentV2"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json'}

            payload = json.dumps({
                "authKey": "E0DE107A7CA04A6CA7FBB6DAE89B4F3A",
                "CentreID": "112084",
                "BookingFrom": "ANDROID" , 
                "bookingVisitID": "NAN",
                "deviceId": "",
                "HomeCollectionflag": "1",
                "OfferDiduction": "0",
                "OfflinePaid": "0",
                "OnlinePaid": "0",
                "PatientId": "NAN",
                "PaymentType": "offline",
                "TotalFees": "0",
                "Trans_String": "NAN",
                "TransactionId": "NAN",
                "TransactionreferenceID": "NAN",
                "TransactionStatus": "NAN",
                "PromoCode": "",
                "BookingDate": serializer.validated_data.get('BookingDate'),
                "slots": serializer.validated_data.get('slots'),
                "CollectionAddress": serializer.validated_data.get('CollectionAddress'),
                "labaddress": serializer.validated_data.get('labaddress'),
                "TransactionForId": serializer.validated_data.get('TransactionForId'),
                "latitude": serializer.validated_data.get('latitude'),
                "UserId" : serializer.validated_data.get('UserId'),
                "longitude":serializer.validated_data.get('longitude'),
                "note": serializer.validated_data.get('CreatedBy'),
                "PatientAge": serializer.validated_data.get('PatientAge'),
                "patientMobile": serializer.validated_data.get('patientMobile'),
                "patientname": serializer.validated_data.get('patientname'),
                "PatientUid": serializer.validated_data.get('PatientUid'),
                "pincode": serializer.validated_data.get('pincode'),
                "Booking_TestDetails": serializer.validated_data.get('Booking_TestDetails'),
                
                })

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = json.loads(response.content)
                pathlab_serializer = PostResponseHomeLIMSAPISerialzier(data = {
                    "patientFamilyMember" : request.data["id"] , 
                    "transactionid" : response_data.get("transactionid") ,
                    "LabTestSuggested" : serializer.validated_data.get('Booking_TestDetails') , 

                }  )
                if pathlab_serializer.is_valid():
                    pathlab_serializer.save()
                    return Response(json.loads(response.content) , status=response.status_code)
                else:
                    # key, value =list(serializer.errors.items())[0]
                    # error_message = key+" , "+ value[0]
                    return Response({"status" : "error" ,
                                    "message" : pathlab_serializer.errors}, status= 400) 
            else:
                return Response(json.loads(response.content) , status=response.status_code) 
            
        else:
            key, value = list(serializer.errors.items())[0]
            print(key , value)
            error_message = key+" , "+ value[0]
            return Response({'message': error_message, 
                            'status' : 'error'}, status=400)
        



@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def MoDashboard(request):

    # wardId = request.GET.get('wardId')
    areaId = request.GET.get('areaId')
    # UserId = request.GET.get('UserId')
    gender = request.GET.get('gender')
    # female = request.GET.get('female')
    # Determine user's group (if authenticated)
    
    group = None
    if request.user.is_authenticated:
        group = request.user.groups.values_list("name", flat=True).first()
        data = {}
        dispensaryId =  request.user.dispensary.id
        if gender:
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area__dispensary_id  =dispensaryId).count()
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area__dispensary_id  =dispensaryId).count()
            data["NoOfTestsAssignmentPending"] = familyMembers.objects.filter( isLabTestAdded = False,familyHead__area__dispensary_id  =dispensaryId).count()
            data["NoOfTestsAssigned"] = familyMembers.objects.filter( isLabTestAdded = True,familyHead__area__dispensary_id  =dispensaryId).count()

            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area__dispensary_id  =dispensaryId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area__dispensary_id  =dispensaryId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area__dispensary_id  =dispensaryId).count()


            if areaId:
                    #Data For  Ward and HealthPost Filter
                # data["NoOfFamilyEnrolled"] = familyHeadDetails.objects.filter(area_id  =areaId,area__dispensary_id  =dispensaryId).count()
                # data["NoOfCitizenEnrolled"] = familyMembers.objects.filter(familyHead__area_id  =areaId,gender=gender,familyHead__area__dispensary_id  =dispensaryId).count()
                # data["NoOfPersonMoreThan30"] = familyMembers.objects.filter(age__gte = 30,age__lt = 60,gender=gender,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()
                data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,gender=gender,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()
                # data["NoOfAbhaIdGenerated"] = 0
                data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,gender=gender,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()
                data["NoOfTestsAssignmentPending"] = familyMembers.objects.filter( isLabTestAdded = False,familyHead__area__dispensary_id  =dispensaryId).count()
                data["NoOfTestsAssigned"] = familyMembers.objects.filter( isLabTestAdded = True,familyHead__area__dispensary_id  =dispensaryId).count()
        

                data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",gender=gender,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()

                data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,gender=gender,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()

                data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",gender=gender,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()

        else:
            data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area__dispensary_id  =dispensaryId).count()
            # data["NoOfAbhaIdGenerated"] = 0
            data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area__dispensary_id  =dispensaryId).count()
            data["NoOfTestsAssignmentPending"] = familyMembers.objects.filter( isLabTestAdded = False,familyHead__area__dispensary_id  =dispensaryId).count()
            data["NoOfTestsAssigned"] = familyMembers.objects.filter( isLabTestAdded = True,familyHead__area__dispensary_id  =dispensaryId).count()

            data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area__dispensary_id  =dispensaryId).count()
            data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area__dispensary_id  =dispensaryId).count()

            data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area__dispensary_id  =dispensaryId).count()

            if areaId:
                data["NoOfPersonMoreThan60"] = familyMembers.objects.filter(age__gte = 60,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()
                data["NoOfCBACFilled"] = familyMembers.objects.filter(cbacRequired = True,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()
                data["NoOfTestsAssignmentPending"] = familyMembers.objects.filter( isLabTestAdded = False,familyHead__area__dispensary_id  =dispensaryId).count()
                data["NoOfTestsAssigned"] = familyMembers.objects.filter( isLabTestAdded = True,familyHead__area__dispensary_id  =dispensaryId).count()

                data["BloodCollectedAtHome"] = familyMembers.objects.filter(bloodCollectionLocation = "Home",familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()
                data["TotalReportGenerated"] = familyMembers.objects.filter(isLabTestReportGenerated = True,familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()

                data["BloodCollectedAtCenter"] = familyMembers.objects.filter(bloodCollectionLocation = "Center",familyHead__area_id  =areaId,familyHead__area__dispensary_id  =dispensaryId).count()

        return Response({
            'status': 'success',
            'message': 'Successfully Fetched',
            'data': data,
        })
