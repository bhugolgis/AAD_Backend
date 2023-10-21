from rest_framework import generics
from rest_framework.response import Response
from database.models import *
from .serializer import *
from django.contrib.gis.geos import Point 
from rest_framework import status
from rest_framework.parsers import MultiPartParser , JSONParser
from rest_framework.permissions import IsAuthenticated
import random
from .permissions import IsHealthworker
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import filters
from django.utils import timezone
from openpyxl import load_workbook 
from django.contrib.auth.models import Group 


class verifyMobileNumber(APIView):
    permission_classes = (IsAuthenticated , IsHealthworker)
    def get(self , request ,mobileNo):
        family_head = familyHeadDetails.objects.filter( mobileNo = mobileNo).exists()
        user = CustomUser.objects.filter(phoneNumber = mobileNo).exists()
        if family_head or user:
            return Response({'status' : 'error' ,
                            'message' : 'Mobile Number Already exist' } , status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status' : 'success' ,
                            'message' : 'verify successfully' } , status= status.HTTP_200_OK)
            
class veirfyaadharCard(APIView):
    permission_classes = (IsAuthenticated, IsHealthworker)
    def get(self , request ,aadharCard):
        data = familyMembers.objects.filter( aadharCard = aadharCard).exists()
        if data:
            return Response({'status' : 'error' ,
                            'message' : 'Aadhar Card Already exist' } , status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status' : 'success' ,
                            'message' : 'verify successfully' } , status= status.HTTP_200_OK)
        
class verifyabhaId(APIView):
    permission_classes = (IsAuthenticated , IsHealthworker)
    def get(self , request ,abhaId):
        data = familyMembers.objects.filter( abhaId = abhaId).exists()
        if data:
            return Response({'status' : 'error' ,
                            'message' : 'ABHA-ID Already exist' } , status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status' : 'success' ,
                            'message' : 'verify successfully' } , status= status.HTTP_200_OK)

class PostSurveyForm(generics.GenericAPIView):
    serializer_class = PostSurveyFormSerializer
    permission_classes = (IsAuthenticated , IsHealthworker)
    parser_classes = [JSONParser]

    def post(self , request , *args , **kwargs):
        """
        The above function is a view function in Django that handles the POST request for saving data,
        including validating and saving the data, generating a family ID, and returning a response.
        
        """
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            try:
                lat = float(serializer.validated_data['latitude'])
                long = float(serializer.validated_data['longitude'])
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
            print(serializer.errors)
            print(error_message)
            return Response({'status': 'error',
                            'message' :error_message} , status = status.HTTP_400_BAD_REQUEST)


# The class `GetFamilyHeadList` is a generic ListAPIView that retrieves a list of family head details
# and allows filtering by mobile number, name, and family ID.
class GetFamilyHeadList(generics.ListAPIView):
    permission_classes = (IsAuthenticated , IsHealthworker)
    serializer_class = GetFamilyHeadListSerialzier
    filter_backends = (filters.SearchFilter,)
    search_fields = ['mobileNo', 'name', 'familyId']

    def get_queryset(self):
        # Filter the queryset based on the currently logged-in user
        queryset = familyHeadDetails.objects.filter(user=self.request.user)
        return queryset

class GetPartiallyInsertedRecord(generics.ListAPIView):
    permission_classes =(IsAuthenticated , IsHealthworker)
    serializer_class = GetFamilyHeadListSerialzier
    filter_backends = (filters.SearchFilter,)
     
    search_fields = ['mobileNo'  , 'name' , 'familyId' ]
    def get_queryset(self):
        # Filter the queryset based on the currently logged-in user
        queryset = familyHeadDetails.objects.filter(partialSubmit = True , user=self.request.user)
        return queryset

class PostFamilyDetails(generics.GenericAPIView):
    serializer_class = postFamilyMemberDetailSerializer
    permission_classes = (IsAuthenticated , IsHealthworker)
    # parser_classes = [MultiPartParser]
    def post(self , request , *args , **kwargs):
        """
        This function saves data from a serializer and returns a success message if the data is valid,
        or an error message if the data is invalid.
        """
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            get_last_memberId = familyMembers.objects.filter(familyHead_id = serializer.validated_data['familyHead']).last()
            if get_last_memberId:
                last_member_id = get_last_memberId.memberId
                last_member_id_parts = last_member_id.split("-")
                
                # Extract the numeric part of the member ID and increment it by 1
                numeric_part = int(last_member_id_parts[-1])
                new_numeric_part = numeric_part + 1

                # Construct the new member ID with the incremented numeric part
                new_member_id = "-".join(last_member_id_parts[:-1]) + "-" + str(new_numeric_part).zfill(2)
                print(new_member_id)
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
    permission_classes = (IsAuthenticated , IsHealthworker)
    serializer_class = GetFamilyMemberDetailSerializer  
    filter_backends = (filters.SearchFilter,)
    search_fields = ['familyHead__familyId' , 'familyHead__mobileNo' , 'familyHead__name' , 'memberId'  ]

    def get_queryset(self):
        # Filter the queryset based on the currently logged-in user
        queryset = familyMembers.objects.filter(familySurveyor=self.request.user)
        return queryset


class UpdateFamilyDetails(generics.GenericAPIView):

    serializer_class = UpdateFamilyMemberDetailSerializer
    permission_classes = (IsAuthenticated , IsHealthworker)
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
    permission_classes = (IsAuthenticated , IsHealthworker)
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
        
        partial_survey_count = self.FamilySurvey_count.filter(partialSubmit = True , user = request.user).count()
        total_family_count = self.FamilySurvey_count.filter(user = request.user).count()
        today_family_count = self.FamilySurvey_count.filter(user = request.user , created_date__day = today.day ).count()

        return Response({
            'total_count' : total_citizen_count ,
            'todays_count' : todays_citizen_count ,
            'partial_survey_count'  : partial_survey_count ,
            'total_family_count' : total_family_count ,
            'today_family_count' : today_family_count
        } , status= status.HTTP_200_OK )
    
    
class GetCitizenList(generics.ListAPIView):
    serializer_class = GetCitizenListSerializer
    model = serializer_class.Meta.model
    permission_classes = (IsAuthenticated , IsHealthworker)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['familyHead__familyId' , 'familyHead__mobileNo' , 'familyHead__name' , 'memberId' , 'name' , 'mobileNo' ]
    paginate_by = 100
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
        

class GetFamilyList(generics.ListAPIView):
    serializer_class = GetFamilyHeadListSerialzier
    model = serializer_class.Meta.model
    permission_classes = (IsAuthenticated , IsHealthworker)
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
    permission_classes =(IsAuthenticated , IsHealthworker)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['bloodCollectionLocation']



class DumpExcelInsertxlsx(generics.GenericAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = DumpExcelSerializer

    def post(self, request, format=None):
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
                                                      password=row[2], phoneNumber=row[3],section_id=row[4] )
                group = Group.objects.get(name = 'healthworker')
                user.groups.add(group)
                        
            return Response({'message' : 'File Uploaded Successfully and users created !!' , 
                            'status' :"success"} , status= status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'message' : 'Something Went wrong please check you File', 
                             'error' : str(e),
                            'status' :"success"} , status= status.HTTP_400_BAD_REQUEST)
