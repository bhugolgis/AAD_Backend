from database.models import *
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, Group
from rest_framework import serializers
from database.managers import *
from ArogyaAplyaDari import settings


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


class HealthCareCentersSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCareCenters
        fields = '__all__'

def get_group_choice():
	"""
	The function "get_group_choice" returns all the available group names in the database as a tuple of
	tuples.
	:return: a tuple of tuples, where each inner tuple contains a group name as both the key and the
	value.
	"""
	group_names = list(Group.objects.values_list("name",flat=True))
	# print(group_names.remove('admin'))
	group_names.remove("admin")
	group_names.remove("supervisor")

	return tuple((i,i) for i in group_names)


# class AddUserSerializer(serializers.ModelSerializer):
# 	password=serializers.CharField(max_length=20)
# 	groups = serializers.ChoiceField(choices = get_group_choice(),required = False)
# 	class Meta:
# 		model=CustomUser
# 		fields=["name","username","password","email","phoneNumber","groups"]
# 		extra_kwargs={"password": {"write_only": True}}


class InsertAmoSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber","health_Post")

class InsertMoSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber","dispensary")





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
		fields = ("id","name","username","emailId","phoneNumber" ,"dispensary" )
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

	# def get_healthPost(self , data):
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
	healthPost_id = serializers.SerializerMethodField()
	healthPost_name = serializers.SerializerMethodField()
	ward = serializers.SerializerMethodField()
	ward_id = serializers.SerializerMethodField()
	class Meta:

		model = area
		fields = ("id","areas", "healthPost_id" , "healthPost_name" , "ward" , "ward_id")

	def get_healthPost_id(self , data):
		try:
			healthPost_id = data.healthPost.id
		except:
			healthPost_id = ''
		return healthPost_id
	
	def get_healthPost_name(self , data):
		try:
			healthPost_name = data.healthPost.healthPostName
		except:
			healthPost_name = ''
		return healthPost_name
	
	def get_ward(self , data):
		try:
			ward = data.healthPost.ward.wardName
		except:
			ward = ''
		return ward
	
	def get_ward_id(self , data):
		try:
			ward_id = data.healthPost.ward.id
		except:
			ward_id = ''
		return ward_id
	

class UpdateSectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = section
		fields = ("sectionName" , "healthPost")
		# read_only = fields

class UpdateAreaSerializer(serializers.ModelSerializer):
	class Meta:
		model = area
		fields = ("dispensary" , "healthPost" , "areas")

class sectionSerializer(serializers.ModelSerializer):
	healthPost_id = serializers.SerializerMethodField()
	healthPost_name = serializers.SerializerMethodField()
	ward = serializers.SerializerMethodField()
	ward_id = serializers.SerializerMethodField()
	class Meta:
		model = section
		fields = ("id" , "sectionName" ,"healthPost_id" , "healthPost_name" , "ward" , "ward_id" )

	def get_healthPost_id(self , data):
		try:
			healthPost_id = data.healthPost.id
		except:
			healthPost_id = ''
		return healthPost_id
	
	def get_healthPost_name(self , data):
		try:
			healthPost_name = data.healthPost.healthPostName
		except:
			healthPost_name = ''
		return healthPost_name
	
	def get_ward(self , data):
		try:
			ward = data.healthPost.ward.wardName
		except:
			ward = ''
		return ward
	
	def get_ward_id(self , data):
		try:
			ward_id = data.healthPost.ward.id
		except:
			ward_id = ''
		return ward_id
	
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




class RegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" , "section")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser



class MoRegisterSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" , "dispensary")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser


class HccRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" , "HealthCareCenters")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
	
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser

class ViewPrimaryHealthCareSerializer(serializers.ModelSerializer):
    # HealthCareDoctor = HealthCareCentersSerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = ("id","name","username","password","emailId","phoneNumber","HealthCareCenters_id")





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


class PrimaryHealthCareRegisterSerializer(serializers.ModelSerializer):
	# ward = serializers.CharField(max_length = 255 , required = True)
	# healthPostName = serializers.CharField(max_length = 255 , required = True)
	# section = serializers.CharField(max_length = 255 , required = True)
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" ,"PrimaryHealthCare")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		# ward = validated_data.pop("ward")
		# healthPostName = validated_data.pop("healthPostName")
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser



class MedicalCollegeHealthCareRegisterSerializer(serializers.ModelSerializer):
	# ward = serializers.CharField(max_length = 255 , required = True)
	# healthPostName = serializers.CharField(max_length = 255 , required = True)
	# section = serializers.CharField(max_length = 255 , required = True)
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" ,"MedicalCollegeHealthCare")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		# ward = validated_data.pop("ward")
		# healthPostName = validated_data.pop("healthPostName")
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser

class ViewMedicalCollegeSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber","MedicalCollegeHealthCare")

class SpecialityHealthCareRegisterSerializer(serializers.ModelSerializer):
	# ward = serializers.CharField(max_length = 255 , required = True)
	# healthPostName = serializers.CharField(max_length = 255 , required = True)
	# section = serializers.CharField(max_length = 255 , required = True)
	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" ,"SpecialityHealthCare")
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

class ViewSpecialHealthCareSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id","name","username","password","emailId","phoneNumber","SpecialityHealthCare")

class CoordPasswordSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("id" , "phoneNumber")

class LoginSerializer(serializers.Serializer):
	phoneNumber = serializers.CharField()
	password = serializers.CharField()
	class Meta:
		# model = CustomUser
		fields = ('id','phoneNumber','password')
	def validate(self,data):
		phoneNumber = data.get('phoneNumber')
		password = data.get('password')

		customuser = auth.authenticate(phoneNumber=phoneNumber, password=password)
		try:
			if not customuser:
				user = CustomUser.objects.get_by_natural_key(phoneNumber)
				if not user.is_active:
					raise serializers.ValidationError("Account is not active")
		except:
			raise serializers.ValidationError("Incorrect Credentials")
		

				

		if data["phoneNumber"] =="" or data["phoneNumber"] == None:
			msg = "Please enter username."
			raise serializers.ValidationError(msg)
		if data["password"] =="" or data["password"] == None:
			msg = "Please enter password."
			raise serializers.ValidationError(msg)
		elif customuser and customuser.is_active:
			return customuser
		raise serializers.ValidationError("Incorrect Credentials")
		# return customuser


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

class CHV_ASHA_Serializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['id','name' , 'username' , 'phoneNumber' , 'section']
		depth = 1


class HealthCareCentersSerializer(serializers.ModelSerializer):
	class Meta:
		model = HealthCareCenters
		fields = '__all__'

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

	def validate(self , data) :
		if data["healthPost"] =="" or data["healthPost"] == None:
				raise serializers.ValidationError("Health post Can not be empty")
		
		if data["sectionName"] == "" or data["sectionName"] == None:
			raise serializers.ValidationError("Section Name can not be empty !!")
		return data

	


class AddAreaSerializer(serializers.ModelSerializer):
	class Meta:
		model = area
		fields = '__all__'


class Addlabtestserializer(serializers.ModelSerializer):
	class Meta:
		model = LabTests
		fields = ('testName' , 'description' , 'testId' )


class UpdateUserDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("name" , "username" , "emailId" , "phoneNumber" , "created_by" , 
			"section" , "ward" , "health_Post" , "area" , "dispensary" , "is_active" )
		

class AddDispensarySerializer(serializers.ModelSerializer):
	class Meta:
		model = dispensary
		fields = ("ward", 	"dispensaryName" )



class getDispensarySerializer(serializers.ModelSerializer):
	class Meta:
		model = dispensary
		fields = ("id","ward", 	"dispensaryName")