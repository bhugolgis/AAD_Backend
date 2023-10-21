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