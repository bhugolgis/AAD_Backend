from django.shortcuts import render
from rest_framework import generics
from .serializers import *
import json
import requests
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser



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