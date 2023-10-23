from django.urls import path
from .views import *

urlpatterns = [
        # ABHA ID Creation By Aadhar
        path('GetGatewaySessionTokenAPI' , GetGatewaySessionTokenAPI.as_view() , name = 'GetGatewaySessionTokenAPI'),
        path('generateAadharOtpAPI' , generateAadharOtpAPI.as_view() , name = 'generateAadharOtpAPI'),
        path('verifyAadharOTP' , verifyAadharOTP.as_view() , name = 'verifyAadharOTP'),
        path('checkAndGenerateMobileOTP' , checkAndGenerateMobileOTP.as_view() , name = 'checkAndGenerateMobileOTP'),
        path('verifyMobileOTP' , verifyMobileOTP.as_view() , name = 'verifyMobileOTP'),
        path('createHealthIdByAdhaarAPI' , createHealthIdByAdhaarAPI.as_view() , name = 'createHealthIdByAdhaarAPI'),
        
        
        # Abha Address Creation by Abha Number URL's
        path('v1/phr/registration/hid/search/auth-methods' , SearchAuthMethodsAPI.as_view() , name = 'SearchAuthMethodsAPI'),
        path('v1/phr/registration/hid/init/AuthMethodAPI' , AuthMethodAPI.as_view() , name = 'AuthMethodAPI'),
        path('v1/phr/registration/hid/init/resendOtp' , resendOtp.as_view() , name = 'resendOtp'),
        path('v1/phr/registration/hid/confirm/credential' , VerifyOTP.as_view() , name = 'VerifyOTP'),
        path('v1/phr/registration/phr/suggestion' , Abha_Adress_suggestions.as_view() , name = 'Abha_Adress_suggestions'),
        path('v1/phr/search/isExist' , abha_adress_search_isExist.as_view() , name = 'abha_adress_search_isExist'),
        path('v1/phr/registration/hid/create-phr-address' , CreatePhrAddress.as_view() , name = 'abha_adress_search_isExist'),

        # Linking of abha_adress to Abha ID 
        
        path('v1/phr/login/init/transaction' , GenerateOTP.as_view() , name = 'GenrateOTP'),
        path('v1/phr/login/mobileEmail/preVerification' , VerifymobileAadharOTP.as_view() , name = 'GenrateOTP'),
        path('v1/phr/profile/link/hid' , VerifymobileAadharOTP.as_view() , name = 'GenrateOTP'),


        # Authentication Using adhar and Mobile Number
        path('v1/auth/init/authByAadhar' , AuthByAadhar.as_view() , name = 'AuthByAadhar'),
        path('v1/auth/confirmWithAadhaarOtp' , confirmWithAadhaarOtp.as_view() , name = 'confirmWithAadhaarOtp'),
        path('v1/auth/resendAuthOTP' , resendAuthOTP.as_view() , name = 'resendAuthOTP'),


        #  Download ABHA Card And Qrcode 

        path('v1/account/getqrCode' , DownloadQrcodeAPI.as_view() , name = 'DownloadQrcodeAPI'),
        path('v1/account/getCard' , DownloadCardAPI.as_view() , name = 'DownloadCardAPI'),

        

]