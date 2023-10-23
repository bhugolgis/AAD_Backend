from rest_framework import serializers


class GetGatewaySessionTokenSerializer(serializers.Serializer):
    clientId = serializers.CharField(max_length=100 , required=True)
    clientSecret = serializers.CharField(max_length=100 , required=True)


class generateAadharOtpSerializer(serializers.Serializer):
    aadhaar = serializers.CharField(max_length=1000, required=True)


class verifyAadharOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=1000, required=True)
    txnId = serializers.CharField(max_length=1000, required=True)



class checkAndGenerateMobileOTPSerializer(serializers.Serializer):
    mobile = serializers.IntegerField( required=True)
    txnId = serializers.CharField(max_length=1000, required=True)


class createHealthIdByAdhaarSerializer(serializers.Serializer):
    consent = serializers.BooleanField(required=True)
    consentVersion = serializers.CharField(max_length=100, default="v1.0")
    txnId = serializers.CharField(max_length=1000, required=True)
    

class verifyMobileOTPSerializer(serializers.Serializer):
    otp = serializers.IntegerField(required=True)
    txnId = serializers.CharField(max_length=1000, required=True)


class SearchAuthMethodsSerializer(serializers.Serializer):
    healhtIdNumber = serializers.CharField(max_length=17, required=True)



class AuthMethodSerializer(serializers.Serializer):
    choices = [('MOBILE_OTP' , 'MOBILE_OTP') , ('AADHAAR_OTP' , 'AADHAAR_OTP')]
    authMethod = serializers.ChoiceField(choices=choices ,required=True)
    healhtIdNumber = serializers.CharField(max_length=17, required=True)

class resendOtpSerializer(serializers.Serializer):
    transactionId = serializers.CharField(max_length=100, required=True)



class VerifyOTPSerializer(serializers.Serializer):
    transactionId = serializers.CharField(max_length=100, required=True)
    value = serializers.CharField(max_length=1000 , required=True)


class Abha_Adress_suggestionsSerializer(serializers.Serializer):
    transactionId = serializers.CharField(max_length=100, required=True)


class CreatePhrAddressSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, required=False) # You can leave this field blank like - password = ""
    transactionId = serializers.CharField(max_length=100, required=True)
    phrAddress = serializers.CharField(max_length=100, required=True)


class AuthByAadharSerializer(serializers.Serializer):
    healthid = serializers.CharField(max_length=17 , required=True)


class LinkHID_to_AddressSerializer(serializers.Serializer):
    choice = [('LINK' , 'LINK'), ('DELINK' , 'DELINK')]
    transactionId = serializers.CharField(max_length=100 , required=True)
    action = serializers.ChoiceField(choices=choice , required=True)