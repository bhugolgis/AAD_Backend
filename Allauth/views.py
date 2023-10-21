from django.shortcuts import render
from django.http import JsonResponse
from knox.models import AuthToken
from database.models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import generics,permissions
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from rest_framework.parsers import JSONParser,MultiPartParser,FileUploadParser,FormParser
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import generics, status
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated , AllowAny
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from drf_extra_fields.fields import Base64ImageField
from datetime import datetime, timedelta
from django.db.models import Count


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
        testOpintmentDaily = PatientsPathlab.objects.filter(created_date__date=today,PatientSampleTaken=False).count()        # data = area.objects.filter(healthPost__id= id )
        dailyTestReceived = PatientsPathlab.objects.filter(created_date__date=today).count()        # data = area.objects.filter(healthPost__id= id )
        testResultAwaited = PatientsPathlab.objects.filter(created_date__date=today,PatientSampleTaken=True,isCompleted=False).count()        # data = area.objects.filter(healthPost__id= id )
        citizenRejectedLabTestCount = PatientsPathlab.objects.filter(citizenRejectedLabTest=True,isCompleted=False).count()        # data = area.objects.filter(healthPost__id= id )



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





class GetWardListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WardSerialzier
    queryset = ward.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("wardName",)

class GethealthPostNameListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = healthPostSerializer
    queryset = healthPost.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("ward__id", "healthPostName")


class GetHealthPostAreasAPI(generics.GenericAPIView):
    serializer_class = AreaSerialzier
    permission_classes = [IsAuthenticated]

    def get(self, request ,id):
        data = area.objects.filter(healthPost__id= id )
        serializer = self.get_serializer(data , many = True).data

        return Response({ "status":"success",
                "message" : 'data feteched successfully',
                "data":serializer,} , status= 200)
    
class GetSectionListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = sectionSerializer
    queryset = section.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("healthPost__id", "sectionName")



class InsertAmoAPI(generics.GenericAPIView):
    serializer_class = AMoRegisterSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data["name"], request.data)
        
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
            from random import choice
            chars = string.digits
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

            return Response({"status":"sucess","message":"OTP Sent on Registered Phone Number."})

        else:
            return Response({"status":"error","message":"User Not Registered With this Phone Number."})

        return Response({"status":"sucess","message":"OTP Sent on Registered Phone Number."})

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


# class UserGroupFilterView(generics.ListAPIView):
#     serializer_class = ViewSupervisorSerializer
    
#     def get_queryset(self):
#         group_name = self.request.query_params.get('group')
#         if group_name:
#             return CustomUser.objects.filter(groups__name=group_name)
#         return CustomUser.objects.all()

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
                
            if groups[0] =="amo":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "amo"
            if groups[0] =="mo":
                data = ViewSupervisorSerializer(customuser,context=self.get_serializer_context()).data
                data["user_group"] = "mo"

            # elif groups[0] =="regionalManager":
            #     data = RmSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "regionalManager"
            # elif groups[0] =="cgm":
            #     verticalId = Verticals.objects.filter(VerticalName = customuser.departmenName)
            #     print(customuser.departmenName,"********")

            #     data = RmSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "cgm"
            #     data["VerticalId"] = verticalId[0].id
            
            # elif groups[0] =="scrutinyClerk":
            #     data = ListScrutinyClerkregisterSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "scrutinyClerk"

            # elif groups[0] =="bankOfficial":
            #     data = ListbankOfficialSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "bankOfficial"

            # elif groups[0] =="MahaPreitOfficeAdmin":
            #     data = ListMahaPreitOfficeAdminSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "MahaPreitOfficeAdmin"

            # elif groups[0] =="MPBCDCOfficeAdmin":
            #     data = ListMPBCDCOfficeAdminSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "MPBCDCOfficeAdmin"


            # elif groups[0] =="MPBCDC_MD":
            #     data = ListmpbcdcMDSerializer(customuser,context=self.get_serializer_context()).data
            #     data["user_group"] = "MPBCDC_MD"


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
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user_data = serializer.validated_data
                group = user_data.groups.values_list("name", flat=True)[0]
                if serializer is not None:
                    try:
                        token = AuthToken.objects.filter(user=serializer.validated_data)
                        token.delete()
                    except AuthToken.DoesNotExist:
                        pass
                    _, token = AuthToken.objects.create(serializer.validated_data)
                    if group == 'healthworker':
                        return Response({
                            'message': 'Login successful',
                            'Token': token,
                            'status': 'success',
                            'email': user_data.emailId,
                            'name' : user_data.name,         
                            'username': user_data.username,
                            'phoneNumber' : user_data.phoneNumber,
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
                            'email': user_data.emailId,
                            'name' : user_data.name,         
                            'username': user_data.username,
                            'phoneNumber' : user_data.phoneNumber,
                            # 'ward' : user_data.section.healthPost.ward.wardName ,
                            'healthPostName' : user_data.health_Post.healthPostName,
                            'healthPostID' : user_data.health_Post.id,
                            # 'areaId':user_data.section.healthPost.healthPost.id,
                            # 'areas':user_data.section.healthPost.area.areas,
                            # 'sectionId':user_data.section.id,
                            # 'sectionName':user_data.section.sectionName,

                            'Group': group}, status=200)
                    elif group == "mo":
                        return Response({
                            'message': 'Login successful',
                            'Token': token,
                            'status': 'success',
                            'email': user_data.emailId,
                            'name' : user_data.name,         
                            'username': user_data.username,
                            'phoneNumber' : user_data.phoneNumber,
                            # 'ward' : user_data.section.healthPost.ward.wardName ,
                            'healthPostName' : user_data.health_Post.healthPostName,
                            'healthPostID' : user_data.health_Post.id,
                            'dispensaryId':user_data.dispensary.id,
                            'dispensaryName':user_data.dispensary.dispensaryName,
                            # 'sectionId':user_data.section.id,
                            # 'sectionName':user_data.section.sectionName,
                            'Group': group}, status=200)
            
            else:
                
                key, value = list(serializer.errors.items())[0]
                error_message = value[0]
                return Response({'message': error_message, 
                                'status' : 'error'}, status=400)
        except:
            return Response({
                'message': 'Invalid Credentials',
                'status': 'failed'}, status=400)
            
            
         
            