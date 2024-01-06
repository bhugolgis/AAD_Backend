from rest_framework import generics
from rest_framework.response import Response
from database.models import *
from .serializer import *
from django.contrib.gis.geos import Point 
from rest_framework import status
from rest_framework.parsers import MultiPartParser , JSONParser
from rest_framework.permissions import IsAuthenticated
import random
from .permissions import IsHealthworker , IsCHV_ASHA
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import filters
from django.utils import timezone
from openpyxl import load_workbook 
from django.contrib.auth.models import Group 
from django.db.models import Q


class verifyMobileNumber(APIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    def get(self , request ,mobileNo):
        """
        The function checks if a given mobile number already exists in the database and returns a
        response indicating whether it exists or not.
        
        :param request: The request object contains information about the current HTTP request, such as
        the headers, body, and method
        :param mobileNo: The mobileNo parameter is the mobile number that is being checked for existence
        in the familyHeadDetails and CustomUser models
        :return: a Response object with a status and message. If the mobile number already exists in
        either the familyHeadDetails or CustomUser models, it returns an error message with a status
        code of 400. Otherwise, it returns a success message with a status code of 200.
        """
        family_head = familyHeadDetails.objects.filter( mobileNo = mobileNo).exists()
        user = CustomUser.objects.filter(phoneNumber = mobileNo).exists()
        if family_head or user:
            return Response({'status' : 'error' ,
                            'message' : 'Mobile Number Already exist' } , status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status' : 'success' ,
                            'message' : 'verify successfully' } , status= status.HTTP_200_OK)
            
class veirfyaadharCard(APIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    def get(self , request ,aadharCard):
        """
        The function checks if a given Aadhar Card number already exists in the database and returns a
        response accordingly.
        
        :param request: The request object contains information about the current HTTP request, such as
        the headers, method, and body
        :param aadharCard: The parameter "aadharCard" is the Aadhar card number that is being passed to
        the function. It is used to check if a family member with the same Aadhar card number already
        exists in the database
        :return: The code is returning a response in the form of a dictionary. If the data exists, it
        returns a response with a status of 'error' and a message stating that the Aadhar Card already
        exists. If the data does not exist, it returns a response with a status of 'success' and a
        message stating that the verification was successful.
        """
        data = familyMembers.objects.filter( aadharCard = aadharCard).exists()
        if data:
            return Response({'status' : 'error' ,
                            'message' : 'Aadhar Card Already exist' } , status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status' : 'success' ,
                            'message' : 'verify successfully' } , status= status.HTTP_200_OK)
        
class verifyabhaId(APIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    def get(self , request ,abhaId):
        """
        The function checks if a given abhaId already exists in the familyMembers table and returns a
        response indicating whether it exists or not.
        
        """
        data = familyMembers.objects.filter( abhaId = abhaId).exists()
        if data:
            return Response({'status' : 'error' ,
                            'message' : 'ABHA-ID Already exist' } , status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status' : 'success' ,
                            'message' : 'verify successfully' } , status= status.HTTP_200_OK)

class PostSurveyForm(generics.GenericAPIView):
    serializer_class = PostSurveyFormSerializer
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    parser_classes = [JSONParser]

    def post(self , request , *args , **kwargs):
        """
        The above function is a view function in Django that handles the POST request for saving data,
        including validating and saving the data, generating a family ID, and returning a response.
        
        """
        serializer = self.get_serializer(data = request.data)
        # print(serializer)
        if serializer.is_valid():
            try:
                lat = float(serializer.validated_data['latitude'] , None)
                long = float(serializer.validated_data['longitude'] , None)
                location = Point(long, lat, srid=4326)
            except:
                location = None

            user =  request.user
            ward =  (user.section.healthPost.ward.wardName).replace(" ","")
            familyId = 'F-{ward}-{num}'.format(ward = ward, num = random.randint(0000000 , 9999999))
            serializer.save(location = location , familyId = familyId ,user = user )
            return Response ({'status' : 'success' ,
                            'message' : 'data saved successfully' } , status= status.HTTP_200_OK)
        else:
            key, value =list(serializer.errors.items())[0]
            try:
                key , value = list(value[0].items())[0]
                error_message =  str(value[0])
            except Exception as e:
                try:
                     error_message = str(key) + " ," +str(value[0])
                except:
                    key , value = list(value[1].items())[0]
                    error_message = str(key) + " ," +str(value[0])
     
            return Response({'status': 'error', 
                            'message' :error_message} , status = status.HTTP_400_BAD_REQUEST)


# The class `GetFamilyHeadList` is a generic ListAPIView that retrieves a list of family head details
# and allows filtering by mobile number, name, and family ID.
class GetFamilyHeadList(generics.ListAPIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    serializer_class = GetFamilyHeadListSerialzier
    filter_backends = (filters.SearchFilter,)
    search_fields = ['mobileNo', 'name', 'familyId']

    def get_queryset(self):
        # Filter the queryset based on the currently logged-in user
        queryset = familyHeadDetails.objects.filter(user=self.request.user)
        return queryset

class GetPartiallyInsertedRecord(generics.ListAPIView):
    permission_classes =(IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    serializer_class = GetFamilyHeadListSerialzier
    filter_backends = (filters.SearchFilter,)
     
    search_fields = ['mobileNo'  , 'name' , 'familyId' ]
    def get_queryset(self):
        # Filter the queryset based on the currently logged-in user
        queryset = familyHeadDetails.objects.filter(partialSubmit = True , user=self.request.user)
        return queryset

class PostFamilyDetails(generics.GenericAPIView):
    serializer_class = postFamilyMemberDetailSerializer
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    def post(self , request , *args , **kwargs):
        """
        This function saves data from a serializer and returns a success message if the data is valid,
        or an error message if the data is invalid.
        """
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            # print(serializer.validated_data)
            get_last_memberId = familyMembers.objects.filter(familyHead_id = serializer.validated_data['familyHead']).last()
            if get_last_memberId:
                last_member_id = get_last_memberId.memberId
                last_member_id_parts = last_member_id.split("-")
                
                numeric_part = int(last_member_id_parts[-1])
                new_numeric_part = numeric_part + 1

                new_member_id = "-".join(last_member_id_parts[:-1]) + "-" + str(new_numeric_part).zfill(2)
            else:
                new_member_id = "F-F/S-7145623-01"  
            serializer.save(familySurveyor = request.user  , memberId = new_member_id)
            return Response ({'status' : 'success' ,
                            'message' : 'data saved successfully' } , status= status.HTTP_200_OK)
        else:
            key, value =list(serializer.errors.items())[0]
            error_message = key+" , "+ value[0]
            return Response({"status" : "error" ,
                             "message" : error_message} , status= status.HTTP_400_BAD_REQUEST)
        

# The class `GetFamilyMembersDetails` is a generic ListAPIView that retrieves details of family
# members and allows filtering based on family ID, mobile number, and name.
class GetFamilyMembersDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    serializer_class = GetFamilyMemberDetailSerializer  
    filter_backends = (filters.SearchFilter,)
    search_fields = ['familyHead__familyId' , 'familyHead__mobileNo' , 'familyHead__name' , 'memberId'  ]

    def get_queryset(self):
        # Filter the queryset based on the currently logged-in user
        queryset = familyMembers.objects.filter(familySurveyor=self.request.user)
        return queryset


class UpdateFamilyDetails(generics.GenericAPIView):

    serializer_class = UpdateFamilyMemberDetailSerializer
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    # parser_classes = [MultiPartParser]

    def patch(self , request , id , *args , **kwargs):
        """
        The function `patch` updates an instance of the `familyMembers` model with the provided `id`
        using the data from the `request`, and returns a success message if the update is successful, or
        an error message if there are any validation errors.
        """
        try:
            instance = familyMembers.objects.get(id =id)
        except:
            return Response({'status': 'error',
                             'message': 'caseNumber ID is not found'}, status=400)

        serializer = self.get_serializer( instance , data = request.data , partial = True)
        if serializer.is_valid():
            serializer.save(familySurveyor = request.user )
            return Response ({'status' : 'success' ,
                            'message' : 'data saved successfully' } , status= status.HTTP_200_OK)
        else:
            key, value =list(serializer.errors.items())[0]
            error_message = key+" , "+ value[0]
            return Response({"status" : "error" ,
                             "message" : error_message} , status= status.HTTP_400_BAD_REQUEST)
        
        
class GetSurveyorCountDashboard(generics.GenericAPIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    queryset = familyMembers.objects.all()
    FamilySurvey_count = familyHeadDetails.objects.all()
    serializer_class = GetFamilyMemberDetailSerializer
    def get(self , request ,  *args , **kwargs ):
        """
        This function returns various counts related to citizen and family surveys for a specific user.
        """
        today = timezone.now().date() 
        total_citizen_count = self.get_queryset().filter(familySurveyor = request.user).count()
        todays_citizen_count  = self.get_queryset().filter(familySurveyor = request.user , created_date__day= today.day).count()
        total_cbac_count = self.get_queryset().filter(familySurveyor = request.user , age__gte = 30 , cbacRequired = True).count()
        partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user = request.user).count()
        total_family_count = self.FamilySurvey_count.filter(user = request.user).count()
        citizen_above_60 =  self.get_queryset().filter(familySurveyor = request.user , age__gte = 60 ).count()
        citizen_above_30 =  self.get_queryset().filter(familySurveyor = request.user , age__gte = 30 ).count()
        today_family_count = self.FamilySurvey_count.filter(user = request.user , created_date__day = today.day ).count()
        blood_collected_home = self.get_queryset().filter(familySurveyor = request.user , bloodCollectionLocation = 'Home').count()
        blood_collected_center = self.get_queryset().filter(familySurveyor = request.user , bloodCollectionLocation = 'Center').count()
        denieded_by_mo_count = self.get_queryset().filter(familySurveyor = request.user , bloodCollectionLocation = 'AMO').count()
        denieded_by_mo_individual = self.get_queryset().filter(familySurveyor = request.user , bloodCollectionLocation = 'Individual Itself').count()
        Referral_choice_further_management = self.get_queryset().filter(familySurveyor =request.user , referels__choice = 'Referral to Mun. Dispensary / HBT for Blood Test / Confirmation / Treatment').count()
        Referral_choice_suspect_symptoms = self.get_queryset().filter(familySurveyor =request.user , referels__choice = 'Referral to HBT polyclinic for physician consultation').count()
        Referral_choice_diagnosis = self.get_queryset().filter(familySurveyor =request.user , referels__choice = 'Referral to Peripheral Hospital / Special Hospital for management of Complication').count()
        Referral_choice_co_morbid_investigation = self.get_queryset().filter(familySurveyor =request.user , referels__choice = 'Referral to Medical College for management of Complication').count()
        Referral_choice_Collection_at_Dispensary = self.get_queryset().filter(familySurveyor =request.user , referels__choice = 'Referral to Private facility').count()
        hypertension = self.get_queryset().filter(familySurveyor = request.user , bloodPressure__gte = 140).count()
        
        total_vulnerabel = self.get_queryset().filter(familySurveyor = request.user , vulnerable = True).count()
        vulnerabel_70_Years = self.get_queryset().filter(familySurveyor = request.user , vulnerable_choices__choice = '70+ Years').count()
        vulnerabel_Physically_handicapped = self.get_queryset().filter(familySurveyor = request.user , vulnerable_choices__choice = 'Physically Handicapped').count()
        vulnerabel_completely_paralyzed_or_on_bed = self.get_queryset().filter(familySurveyor = request.user , vulnerable_choices__choice = 'Completely Paralyzed or On bed').count()
        vulnerabel_elderly_and_alone_at_home = self.get_queryset().filter(familySurveyor = request.user , vulnerable_choices__choice = 'Elderly and alone at home').count()
        vulnerabel_any_other_reason = self.get_queryset().filter(familySurveyor = request.user , vulnerable_choices__choice = 'Any other reason').count()

        Questionnaire_queryset = self.get_queryset().filter(familySurveyor =request.user , Questionnaire__isnull=False)
        total_tb_count = 0
        total_diabetes = 0
        total_breast_cancer = 0 
        total_oral_cancer = 0 
        total_cervical_cancer =0
        total_COPD_count = 0 
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
            for question in part_b[:10]:
                answer = question.get('answer', [])
                if answer and len(answer) > 0:
                    tb_count += 1
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

            total_tb_count += tb_count
            total_diabetes += diabetes
            total_breast_cancer += breast_cancer
            total_oral_cancer += oral_cancer
            total_cervical_cancer += cervical_cancer
            total_COPD_count += COPD

        return Response({
            'total_count' : total_citizen_count ,
            'todays_count' : todays_citizen_count ,
            'partial_survey_count'  : partial_survey_count ,
            'total_family_count' : total_family_count ,
            'today_family_count' : today_family_count,
            'total_cbac_count' : total_cbac_count ,
            'citizen_above_60' : citizen_above_60,
            'citizen_above_30' : citizen_above_30 ,
            'diabetes' : total_diabetes,
            'hypertension' : hypertension ,
            'oral_Cancer' : total_oral_cancer ,
            'cervical_cancer' : total_cervical_cancer ,
            'copd' : total_COPD_count,
            'asthama' : 0 ,
            'tb' : total_tb_count ,
            'breast_cancer' : total_breast_cancer , 
            'communicable' : 1 ,
            'blood_collected_home' : blood_collected_home , 
            'blood_collected_center' : blood_collected_center ,
            'denieded_by_mo_count' : denieded_by_mo_count , 
            'denieded_by_mo_individual' : denieded_by_mo_individual ,
            'Referral_choice_further_management' : Referral_choice_further_management ,
            'Referral_choice_suspect_symptoms': Referral_choice_suspect_symptoms ,
            'Referral_choice_diagnosis': Referral_choice_diagnosis ,
            'Referral_choice_co_morbid_investigation': Referral_choice_co_morbid_investigation ,
            'Referral_choice_Collection_at_dispensary': Referral_choice_Collection_at_Dispensary ,
            'total_vulnerabel' : total_vulnerabel , 
            'vulnerabel_70_Years' : vulnerabel_70_Years , 
            'vulnerabel_Physically_handicapped' : vulnerabel_Physically_handicapped , 
            'vulnerabel_completely_paralyzed_or_on_bed' : vulnerabel_completely_paralyzed_or_on_bed , 
            'vulnerabel_elderly_and_alone_at_home' : vulnerabel_elderly_and_alone_at_home , 
            'vulnerabel_any_other_reason' : vulnerabel_any_other_reason , 

            } , status= status.HTTP_200_OK )
    
class GetCitizenList(generics.ListAPIView):
    serializer_class = GetCitizenListSerializer
    model = serializer_class.Meta.model
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['familyHead__familyId' , 'familyHead__mobileNo' , 'familyHead__name' , 'memberId' , 'name' , 'mobileNo' ]

    def get_queryset(self ):
        """
        The function returns a queryset of all objects ordered by their created date in descending order.
        """
        queryset = self.model.objects.all()
        return queryset.order_by('-created_date')
    
    def get(self , request , choice):
        """
        The function `get` retrieves data based on the user's choice of either "Today", "All", or
        "Partially".
        :param request: The `request` parameter is an object that represents the HTTP request made by the
        client. It contains information such as the user making the request, the method used (GET, POST,
        etc.), and any data or parameters sent with the request
        :param choice: The `choice` parameter is a string that determines the type of data to be fetched.
        It can have three possible values: "Today", "All", or "Partially"
        :return: a Response object with a message, status, and data. The message indicates that the data
        was fetched successfully, the status indicates the success status, and the data contains the
        serialized queryset. The status code of the response is HTTP 200 OK.
        """

        if choice == 'Today':
            today = timezone.now().date() 
            queryset = self.model.objects.filter(familySurveyor = request.user , created_date__day = today.day)
            serializer = self.get_serializer(queryset , many = True ).data
            return Response(serializer , status= status.HTTP_200_OK)
    
        elif choice == 'All':
            total_list = self.get_queryset().filter(familySurveyor = request.user)
            serializer = self.get_serializer(total_list , many = True ).data
            return Response(serializer  , status= status.HTTP_200_OK)
        
        elif choice == 'Partially':
            queryset = familyHeadDetails.objects.filter(partialSubmit = True , user = request.user)
            serializer = GetFamilyHeadListSerialzier(queryset , many = True ).data
            return Response({ serializer } , status= status.HTTP_200_OK)
        

class getReferelOptionList(generics.ListAPIView):
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    serializer_class = getReferelOptionListSerialzier
    model = serializer_class.Meta.model
    queryset = model.objects.all()

class getvulnerableOptionList(generics.ListAPIView):
    serializer_class = getvulnerableOptionListSerialzier
    model = serializer_class.Meta.model
    queryset = model.objects.all()

class GetFamilyList(generics.ListAPIView):
    serializer_class = GetFamilyHeadListSerialzier
    model = serializer_class.Meta.model
    permission_classes = (IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['familyHead__familyId' , 'familyHead__mobileNo' , 'familyHead__name' , 'memberId' , 'name' , 'mobileNo' ]
    paginate_by = 100

    def get_queryset(self ):
        queryset = self.model.objects.all()
        return queryset.order_by('-created_date')
    
    def get(self , request , choice):
        """
        The function `get` retrieves data based on the user's choice of either "Today" or "All" and
        returns a response with the fetched data.
        
        :param request: The `request` parameter is an object that represents the HTTP request made by
        the client. It contains information such as the request method (GET, POST, etc.), headers, user
        authentication, and query parameters
        :param choice: The `choice` parameter is used to determine the type of data to fetch. It can
        have two possible values: "Today" or "All"
        :return: The code is returning a response object with a message, status, and data. The message
        indicates that the data was fetched successfully, the status indicates success, and the data
        contains the serialized queryset. The status code of the response is 200 (OK).
        """

        if choice == 'Today':
            today = timezone.now().date() 
            queryset = self.model.objects.filter(user = request.user , created_date__day = today.day)
            serializer = self.get_serializer(queryset , many = True ).data
            return Response( serializer  , status= status.HTTP_200_OK)
    
        elif choice == 'All':
            total_list = self.get_queryset().filter(user = request.user)
            serializer = self.get_serializer(total_list , many = True ).data
            return Response( serializer , status= status.HTTP_200_OK)
        
# The above class is a generic ListAPIView that retrieves blood collection details for family members,
# with search functionality based on the blood collection location.
class GetBloodCollectionDetail(generics.ListAPIView):
    queryset = familyMembers.objects.all()
    serializer_class = GetCitizenListSerializer
    permission_classes =(IsAuthenticated , IsHealthworker | IsCHV_ASHA)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['bloodCollectionLocation']
# The `DumpExcelInsertxlsx` class is a view in a Django REST framework API that handles the uploading
# of an Excel file, parses the data, and creates users in the database based on the data in the Excel
# file.
class DumpExcelInsertxlsx(generics.GenericAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = DumpExcelSerializer

    def post(self, request, format=None):
        """
        The above function is a Django view that handles the uploading of an Excel file, reads the data
        from the file, and creates user objects in the database based on the data.
        
        :param request: The `request` parameter is an object that contains information about the current
        HTTP request. It includes details such as the request method (GET, POST, etc.), headers, body,
        and any uploaded files
        :param format: The `format` parameter is used to specify the desired format of the response. In
        this case, it is set to `None`, which means that the format will be determined automatically
        based on the request
        :return: The code is returning a response object with a JSON payload. The payload contains a
        "message" field indicating the status of the operation ("File Uploaded Successfully and users
        created !!" or "Something Went wrong please check you File"), an "error" field containing the
        error message if an exception occurred, and a "status" field indicating the status of the
        operation ("success" or "error"). The status
        """
        try:
            if 'excel_file' not in request.FILES:
                return Response({"status": "error", "message": "No file uploaded."}, status=400)
            excel_file = request.FILES["excel_file"]
    
            if excel_file.size == 0 or excel_file.name.endswith(".xlsx") != True:
                return Response({"status": "error",
                                "message": "only .xlsx file is supported."},
                                status=400)

            workbook = load_workbook(filename=excel_file)
            sheet_name = workbook.sheetnames[0]
            worksheet = workbook[sheet_name]
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                already_exist = CustomUser.objects.filter(username =row[1] , phoneNumber=row[3]  ).exists()
                if already_exist:
                    continue
                user = CustomUser.objects.create_user(name = row[0] , username=row[1],
                                                      password=row[2], phoneNumber=row[3],section_id=row[4])
                group = Group.objects.get(name = 'CHV-ASHA')
                user.groups.add(group)
                        
            return Response({'message' : 'File Uploaded Successfully and users created !!' , 
                            'status' :"success"} , status= status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'message' : 'Something Went wrong please check you File', 
                             'error' : str(e),
                            'status' :"error"} , status= status.HTTP_400_BAD_REQUEST)
