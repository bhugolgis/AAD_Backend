from database.models import *
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, Group
from rest_framework import serializers
from database.managers import *


#user Serializer
class AdminSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","emailId","phoneNumber")

class PathLabSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","emailId","phoneNumber")

class InsertSupervisorSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber")



class InsertAmoSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber","health_Post")

class InsertMoSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber","healthPost","dispensary")


class ViewAmoSerializer(serializers.ModelSerializer):
	healthpost = serializers.SerializerMethodField()
	# section = serializers.SerializerMethodField()
	# ward = serializers.SerializerMethodField()
	class Meta:
		model = CustomUser
		fields = ("id","name","username","emailId","phoneNumber" ,"healthpost" )
		depth = 3
	
	# def get_ward(self , data):
	# 	try:
	# 		sectionName = data.section.healthPost.ward.wardName
	# 	except:
	# 		sectionName = ''
	# 	return sectionName
	# def get_section(self , data):
	# 	try:
	# 		sectionName = data.section.sectionName
	# 	except:
	# 		sectionName = ''
	# 	return sectionName

	def get_healthpost(self , data):
		try:
			healthpost = data.section.healthPost.healthPostName
		except:
			healthpost = ''
		return healthpost


class ViewMoSerializer(serializers.ModelSerializer):
	healthPost = serializers.SerializerMethodField()
	dispensary = serializers.SerializerMethodField()
	# ward = serializers.SerializerMethodField()
	class Meta:
		model = CustomUser
		fields = ("id","name","username","emailId","phoneNumber" ,"healthPost","dispensary" )
		depth = 3
	
	# def get_ward(self , data):
	# 	try:
	# 		sectionName = data.section.healthPost.ward.wardName
	# 	except:
	# 		sectionName = ''
	# 	return sectionName
	def get_dispensary(self , data):
		try:
			sectionName = data.dispensary.dispensaryName
		except:
			sectionName = ''
		return sectionName

	def get_healthPost(self , data):
		try:
			health_Post = data.health_Post.healthPostName
		except:
			health_Post = ''
		return health_Post



class ViewSupervisorSerializer(serializers.ModelSerializer):
	healthpost = serializers.SerializerMethodField()
	section = serializers.SerializerMethodField()
	ward = serializers.SerializerMethodField()
	class Meta:
		model = CustomUser
		fields = ("id","name","username","emailId","phoneNumber" , "ward", "healthpost" , "section" )
		depth = 3
	
	def get_ward(self , data):
		try:
			sectionName = data.section.healthPost.ward.wardName
		except:
			sectionName = ''
		return sectionName
	def get_section(self , data):
		try:
			sectionName = data.section.sectionName
		except:
			sectionName = ''
		return sectionName

	def get_healthpost(self , data):
		try:
			healthpost = data.section.healthPost.healthPostName
		except:
			healthpost = ''
		return healthpost
		
class WardSerialzier(serializers.ModelSerializer):
	class Meta:
		model = ward
		fields = ("id","wardName",)

class healthPostSerializer(serializers.ModelSerializer):
	class Meta:
		model = healthPost
		fields = ("id","ward" , "healthPostName")

class AreaSerialzier(serializers.ModelSerializer):
	class Meta:
		model = area
		fields = ("areas",)

class sectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = section
		fields = ("id" , "sectionName" , )
	
class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)  # Assuming E.164 format

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

class SendEmailOrPhoneSerializer(serializers.Serializer):
	phoneNumber = serializers.CharField()
	class Meta:
		# model = CustomUser
		fields = ('phoneNumber')
  
class NewForgotPasswordSerializer(serializers.Serializer):
	phoneNumber = serializers.CharField()
	otp = serializers.CharField()
	class Meta:
		# model = CustomUser
		fields = ('phoneNumber','otp')
  
class ChangePasswordSerializer(serializers.Serializer):
	newpassword = serializers.CharField()
	class Meta:
		model = CustomUser
		fields = ('newpassword')


# class RegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     class Meta:
#         model = CustomUser
#         fields = ('username', 'password', 'name', 'emailId', 'phoneNumber')

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = CustomUser.objects.create_user(password=password, **validated_data)
#         return user

class RegisterSerializer(serializers.ModelSerializer):
	# ward = serializers.CharField(max_length = 255 , required = True)
	# healthPostName = serializers.CharField(max_length = 255 , required = True)
	# section = serializers.CharField(max_length = 255 , required = True)
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" , "section")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		# ward = validated_data.pop("ward")
		# healthPostName = validated_data.pop("healthPostName")
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser

class MoRegisterSerializer(serializers.ModelSerializer):
	# ward = serializers.CharField(max_length = 255 , required = True)
	# healthPostName = serializers.CharField(max_length = 255 , required = True)
	# section = serializers.CharField(max_length = 255 , required = True)
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" , "dispensary","health_Post")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		# ward = validated_data.pop("ward")
		# healthPostName = validated_data.pop("healthPostName")
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser

class AMoRegisterSerializer(serializers.ModelSerializer):
	# ward = serializers.CharField(max_length = 255 , required = True)
	# healthPostName = serializers.CharField(max_length = 255 , required = True)
	# section = serializers.CharField(max_length = 255 , required = True)
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" ,"health_Post")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		# ward = validated_data.pop("ward")
		# healthPostName = validated_data.pop("healthPostName")
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser


	# def validate(self, data):
	# 	if data["name"]=="":
	# 		msg = "Must include username and bankAccountNo"
	# 		raise serializers.ValidationError(msg)
	# 	if data["username"]=="":
	# 		msg = "Must include username and username"
	# 		raise serializers.ValidationError(msg)
	# 	if CustomUser.objects.filter(phoneNumber=data["phoneNumber"]).exists():
	# 		msg = "Phone Number Already Exists"
	# 		raise serializers.ValidationError(msg)
	# 	if CustomUser.objects.filter(aadharNumber=data["aadharNumber"]).exists():
	# 		msg = "Aadhar Number Already Exists"
	# 		raise serializers.ValidationError(msg)
	# 	return data


class LoginSerializer(serializers.Serializer):
    phoneNumber = serializers.IntegerField()
    password = serializers.CharField()
    class Meta:
        # model = CustomUser
        fields = ('id','phoneNumber','password')
    def validate(self,data):
        phoneNumber = data.get('phoneNumber')
        password = data.get('password')
       
        customuser = auth.authenticate(phoneNumber=phoneNumber, password=password)
        
        if data["phoneNumber"] =="" or data["phoneNumber"] == None:
            msg = "Please enter username."
            raise serializers.ValidationError(msg)
        if data["password"] =="" or data["password"] == None:
            msg = "Please enter password."
            raise serializers.ValidationError(msg)
        if customuser and customuser.is_active:
            return customuser
        raise serializers.ValidationError("Incorrect Credentials")


class LoginWithOtpSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()
    class Meta:
        # model = CustomUser
        fields = ('id','username')
    def validate(self,data):
        username = data.get('username')
        print(username)
        customuser = auth.authenticate(username=username)
        
        if data["username"] =="":
            msg = "Please enter username."
            raise serializers.ValidationError(msg)
        # if data["password"] =="":
        #     msg = "Please enter password."
        #     raise serializers.ValidationError(msg)
        if customuser and customuser.is_active:
            return customuser
        raise serializers.ValidationError("Incorrect Credentials")


class AddwardSerializer(serializers.ModelSerializer):
	class Meta:
		model = ward
		fields = '__all__'


class AddHealthPostSerializer(serializers.ModelSerializer):
	class Meta:
		model = healthPost
		fields = '__all__'


class AddSectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = section
		fields = '__all__'


class AddAreaSerializer(serializers.ModelSerializer):
	class Meta:
		model = area
		fields = '__all__'

