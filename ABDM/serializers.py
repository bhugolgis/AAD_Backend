from rest_framework import serializers


class GetGatewaySessionTokenSerializer(serializers.Serializer):
    clientId = serializers.CharField(max_length=100 , required=True)
    clientSecret = serializers.CharField(max_length=100 , required=True)

    def validate(self, data):
        if 'clientId' not in data or data["clientId"] == '':
            raise serializers.ValidationError('clientId can not be empty !!')
        if 'clientSecret' not in data or data["clientSecret"] == '':
            raise serializers.ValidationError('clientSecret can not be empty !!')
        return data

class generateAadharOtpSerializer(serializers.Serializer):
    aadhaar = serializers.CharField(max_length=1000, required=True)
    
    def validate(self, data):
       
        if 'aadhaar' not in data or data["aadhaar"] == '':
                raise serializers.ValidationError('aadhaar can not be empty !!')
        return data 


class verifyAadharOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=1000, required=True)
    txnId = serializers.CharField(max_length=1000, required=True)

    def validate(self, data):
       
        if 'otp' not in data or data["otp"] == '':
                raise serializers.ValidationError('otp can not be empty !!')
        if 'txnId' not in data or data["txnId"] == '':
                raise serializers.ValidationError('txnId can not be empty !!')
        return data 
    

class checkAndGenerateMobileOTPSerializer(serializers.Serializer):
    mobile = serializers.IntegerField( required=True)
    txnId = serializers.CharField(max_length=1000, required=True)

    def validate(self, data):
       
        if 'mobile' not in data or data["mobile"] == '':
                raise serializers.ValidationError('mobile can not be empty !!')
        if 'txnId' not in data or data["txnId"] == '':
                raise serializers.ValidationError('txnId can not be empty !!')
        return data 


class createHealthIdByAdhaarSerializer(serializers.Serializer):
    consent = serializers.BooleanField(required=True)
    consentVersion = serializers.CharField(max_length=100, default="v1.0")
    txnId = serializers.CharField(max_length=1000, required=True)
    

    def validate(self, data):
        if 'consent' not in data or data["consent"] == '':
                raise serializers.ValidationError('consent can not be empty !!')
        if 'txnId' not in data or data["txnId"] == '':
                raise serializers.ValidationError('txnId can not be empty !!')
        return data


class verifyMobileOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length = 1000 ,  required=True)
    txnId = serializers.CharField(max_length=1000, required=True)

    def validate(self, data):
        if 'otp' not in data or data["otp"] == '':
                raise serializers.ValidationError('otp can not be empty !!')
        if 'txnId' not in data or data["txnId"] == '':
                raise serializers.ValidationError('txnId can not be empty !!')
        return data

class   SearchAuthMethodsSerializer(serializers.Serializer):
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


class searchByHealthIdSerializer(serializers.Serializer):
    healthId = serializers.CharField(max_length=17 , required=True)


    
class searchByMobileSerializer(serializers.Serializer):
    gender = serializers.CharField(max_length=10 , required=True)
    mobile = serializers.IntegerField( required=True)
    name = serializers.CharField(max_length= 100 , required=True)
    yearOfBirth = serializers.IntegerField(required = True )



class prfileLoginSerializer(serializers.Serializer):
    choices = [('MOBILE_OTP' , 'MOBILE_OTP') , ('AADHAAR_OTP' , 'AADHAAR_OTP')]
    authMethod = serializers.ChoiceField(choices=choices ,required=True)
    healthid = serializers.CharField(max_length=17, required=True)