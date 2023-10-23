from django.shortcuts import render
from rest_framework import generics
from .serializers import *
import json
import requests
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView



# Create your views here.
class GetGatewaySessionTokenAPI(generics.GenericAPIView):
    serializer_class = GetGatewaySessionTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url = "https://dev.abdm.gov.in/gateway/v0.5/sessions"

            payload = json.dumps({
            "clientId": serializer.validated_data.get('clientId'),
            "clientSecret": serializer.validated_data.get('clientSecret'),
            "grantType": "client_credentials"
            })
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',}
            response = requests.request("POST", url, headers=headers, data=payload)
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class generateAadharOtpAPI(generics.GenericAPIView):
    serializer_class = generateAadharOtpSerializer 

    def post(self, request, *args, **kwargs):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v2/registration/aadhaar/generateOtp"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "aadhaar": serializer.validated_data.get('aadhaar'),})
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        
class verifyAadharOTP(generics.GenericAPIView):
    serializer_class = verifyAadharOTPSerializer 

    def post(self, request, *args, **kwargs):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v2/registration/aadhaar/verifyOTP"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "otp": serializer.validated_data.get('otp'),
            "txnId": serializer.validated_data.get('txnId'),})
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class checkAndGenerateMobileOTP(generics.GenericAPIView):
    serializer_class = checkAndGenerateMobileOTPSerializer 

    def post(self, request, *args, **kwargs):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v2/registration/aadhaar/checkAndGenerateMobileOTP"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "mobile": serializer.validated_data.get('mobile'),
            "txnId": serializer.validated_data.get('txnId'),})
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)


class createHealthIdByAdhaarAPI(generics.GenericAPIView):
    serializer_class = createHealthIdByAdhaarSerializer    

    def post(self, request, *args, **kwargs):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v2/registration/aadhaar/createHealthIdByAdhaar"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "consent": serializer.validated_data.get('consent'),
            "consentVersion" : serializer.validated_data.get('consentVersion'),
            "txnId": serializer.validated_data.get('txnId'),})
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)


class verifyMobileOTP(generics.GenericAPIView):
    serializer_class = verifyMobileOTPSerializer

    def post(self, request, *args, **kwargs):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v2/registration/aadhaar/verifyMobileOTP"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "otp": serializer.validated_data.get('otp'),
            "txnId": serializer.validated_data.get('txnId'),})
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        


# Abha Address Creation by Abha Number ----------------------------------------------------------------


class SearchAuthMethodsAPI(generics.GenericAPIView):
    serializer_class = SearchAuthMethodsSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/registration/hid/search/auth-methods"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "healhtIdNumber": serializer.validated_data.get('healhtIdNumber'),})
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class AuthMethodAPI(generics.GenericAPIView):
    serializer_class = AuthMethodSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/registration/hid/init/transaction"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "healhtIdNumber": serializer.validated_data.get('healhtIdNumber'),
            "authMethod": serializer.validated_data.get('authMethod'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class resendOtp(generics.GenericAPIView):
    serializer_class = resendOtpSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/registration/hid/init/resendOtp"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "transactionId": serializer.validated_data.get('transactionId'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class VerifyOTP(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer


    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/registration/hid/confirm/credential"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "transactionId": serializer.validated_data.get('transactionId'),
            "value": serializer.validated_data.get('value'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class Abha_Adress_suggestions(generics.GenericAPIView):
    serializer_class = Abha_Adress_suggestionsSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/registration/phr/suggestion"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "transactionId": serializer.validated_data.get('transactionId'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class abha_adress_search_isExist(APIView):
    def get(self, request):
        url = "https://phrsbx.abdm.gov.in/api/v1/phr/search/isExist"
        headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}"
        }

        params = {
            'phrAddress': request.GET.get('phrAddress')
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return Response(json.loads(response.content), status=200)
        else:
            return Response("Failed to fetch data", status=response.status_code)
        
class CreatePhrAddress(generics.GenericAPIView):
    serializer_class = CreatePhrAddressSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/registration/hid/create-phr-address"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "transactionId": serializer.validated_data.get('transactionId'),
            "phrAddress": serializer.validated_data.get('phrAddress'),
            "password": serializer.validated_data.get('password'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        
# LINK TO HEALTH ADDRESS TO HEALTH ID 

class GenerateOTP(generics.GenericAPIView):
    serializer_class = AuthMethodSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/login/init/transaction"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "healhtIdNumber": serializer.validated_data.get('healhtIdNumber'),
            "authMethod": serializer.validated_data.get('authMethod'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class VerifymobileAadharOTP(generics.GenericAPIView):
    serializer_class = verifyAadharOTPSerializer

    def post(self, request , *args , **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/login/mobileEmail/preVerification"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "transactionId": serializer.validated_data.get('txnId'),
            "otp": serializer.validated_data.get('otp'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)


class LinkHID_to_Address(generics.GenericAPIView):
    serializer_class = LinkHID_to_AddressSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://phrsbx.abdm.gov.in/api/v1/phr/profile/link/hid"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "transactionId": serializer.validated_data.get('transactionId'),
            "action": serializer.validated_data.get('action'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)






# Authentication Usin aadhar OTP  ----------------------------------------------------------------

class AuthByAadhar(generics.GenericAPIView):
    serializer_class = AuthByAadharSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v1/auth/init"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "healthid": serializer.validated_data.get('healthid'),
            "authMethod": "AADHAAR_OTP",
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class confirmWithAadhaarOtp(generics.GenericAPIView):
    serializer_class = verifyAadharOTPSerializer


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v1/auth/confirmWithAadhaarOtp"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "txnId": serializer.validated_data.get('txnId'),
            "otp": serializer.validated_data.get('otp'),
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)
        

class resendAuthOTP(generics.GenericAPIView):
    serializer_class = resendOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            url= "https://healthidsbx.abdm.gov.in/api/v1/auth/resendAuthOTP"
            headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}" }

            payload = json.dumps({
            "txnId": serializer.validated_data.get('transactionId'),
            "authMethod": "AADHAAR_OTP",
            })
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            return Response(json.loads(response.content) , status=response.status_code)
        else:
            return Response({'message': serializer.errors , 
                             "status": "error" } , status=400)


# Download ABHA Card And Qrcode 

class DownloadQrcodeAPI(APIView):
    def get(self, request):
        url = "https://healthidsbx.abdm.gov.in/api/v1/account/qrCode"
        headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}",
            'X-Token' : f"{request.headers.get('X-Token')}"
        }

        # params = {
        #     'phrAddress': request.GET.get('phrAddress')
        # }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(json.loads(response.content), status=200)
        else:
            return Response("Failed to fetch data", status=response.status_code)
        

class DownloadCardAPI(APIView):
    def get(self, request):
        url = "https://healthidsbx.abdm.gov.in/api/v1/account/getCard"
        headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Authorization': f"{request.headers.get('Authorization')}",
            'X-Token' : f"{request.headers.get('X-Token')}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(json.loads(response.content), status=200)
        else:
            return Response("Failed to fetch data", status=response.status_code)
