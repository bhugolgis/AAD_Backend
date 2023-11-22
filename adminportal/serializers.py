
from rest_framework import serializers
from database.models import *
from django.contrib.auth.models import Group


def get_group_choice():
	"""
	The function "get_group_choice" returns all the available group names in the database as a tuple of
	tuples.
	:return: a tuple of tuples, where each inner tuple contains a group name as both the key and the
	value.
	"""
	group_names = list(Group.objects.values_list("name",flat=True))
	# print(group_names.remove('admin'))
	# group_names.remove("admin")
	group_names.remove("supervisor")

	return tuple((i,i) for i in group_names)

class AddUserSerializer(serializers.ModelSerializer):
	group = serializers.ChoiceField(choices = get_group_choice(),required = False)

	class Meta:
		model = CustomUser
		fields = ("name","username", "password", "phoneNumber", "emailId" , "health_Post",
					 "dispensary" , "HealthCareCenters" ,"section" , "group")
		extra_kwargs = {'password':{'write_only':True}}
		
	def create(self,validated_data):
		group = validated_data.pop("group")
		# healthPostName = validated_data.pop("healthPostName")
		customuser = CustomUser.objects.create_user(**validated_data)
		
		return customuser
	


class UpdateUserDetailsSerializer(serializers.ModelSerializer):
	username = serializers.CharField(max_length=200 , required = False)
	class Meta:
		model = CustomUser
		fields = ("name" , "username" ,"emailId" , "phoneNumber" , "supervisor" , 
			"section" , "ward" , "health_Post" , "area" , "dispensary")
		

class DeleteUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ("name" , "username" , "emailId" , "phoneNumber" , "supervisor" , 
			"section" , "ward" , "health_Post" , "area" , "dispensary")
		

class CustomUserSerializer(serializers.ModelSerializer):
	section = serializers.SerializerMethodField()
	ward = serializers.SerializerMethodField()
	health_Post = serializers.SerializerMethodField()
	# area = serializers.SerializerMethodField()
	dispensary = serializers.SerializerMethodField()
	class Meta:
		model = CustomUser
		fields = ( "id" ,"name" , "username" ,"emailId" , "phoneNumber" , 
			"section" , "ward" , "health_Post" , "area" , "dispensary")
		

	def get_ward(self , data):
		try:
			Ward_Name = data.section.healthPost.ward.wardName
		except:
			Ward_Name = ''
		return Ward_Name
	
	def get_section(self , data):
		try:
			sectionName = data.section.sectionName
		except:
			sectionName = ''
		return sectionName
	
	def get_health_Post(self , data):
		try:
			healthPostName = data.section.healthPost.healthPostName
		except:
			healthPostName = ''
		return healthPostName
	
	def get_dispensary(self , data):
		try:
			dispensaryName = data.dispensary.dispensaryName
		except:
			dispensaryName = ''
		return dispensaryName
	

