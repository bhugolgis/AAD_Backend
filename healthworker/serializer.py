from rest_framework import serializers
from database.models import *
from drf_extra_fields.fields import Base64ImageField


class postFamilyMemberDetailSerializer(serializers.ModelSerializer):
    demandLetter = Base64ImageField(required=False)
    # familyHead = serializers.IntegerField(required = True ) 
    class Meta:
        model = familyMembers
        fields = ('name' , 'gender' , 'age' , 'mobileNo' , 'familyHead' ,'aadharAndAbhaConsent' ,'aadharCard' ,  'abhaId' ,
                   'pulse', 'bloodPressure','weight' , 'height' , 'BMI' , 'questionsConsent','Questionnaire',
                  'bloodConsent' ,'demandLetter', 'bloodCollectionLocation' , 'cbacScore' )

   
class GetFamilyMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = familyMembers
        fields = '__all__'
        

class UpdateFamilyMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = familyMembers
        fields = ('name' , 'gender' , 'age' , 'mobileNo' , 'familyHead' ,'aadharAndAbhaConsent' ,'aadharCard' ,  'abhaId' ,
                   'pulse', 'bloodPressure','weight' , 'height' , 'BMI' ,
                  'questionsConsent','Questionnaire' ,'bloodConsent' , 'bloodCollectionLocation' , 'cbacScore' )


    def validate(self, data):
        if 'name' not in data or data["name"] == '':
            raise serializers.ValidationError('name can not be empty !!')
        if 'gender' not in data  or data['gender'] == '' :
            raise serializers.ValidationError('gender can not be empty !!')
        if 'age' not in data  or data['age'] == '' :
            raise serializers.ValidationError('age can not be empty !!')
        if 'mobileNo' not in data or data['mobileNo'] =='':
            raise serializers.ValidationError('mobileNo can not be empty !!')
        
        return data




class PostSurveyFormSerializer(serializers.ModelSerializer):
    familyMembers_details = postFamilyMemberDetailSerializer(many = True)
    latitude = serializers.CharField(max_length=50,required=False)
    longitude = serializers.CharField(max_length=50,required=False)

    class Meta:
        model = familyHeadDetails
        fields = ( 'area','name' , 'mobileNo' , 'plotNo',
                  'address' , 'pincode' ,'totalFamilyMembers' ,
                 'latitude' , 'longitude'  , 'familyMembers_details' , 'partialSubmit')
        
    def validate(self, data):
        """
        The function validates the data by checking if certain fields are present and not empty, and
        raises a validation error if any of the checks fail.
        
        :param data: The `data` parameter is a dictionary that contains the information to be validated.
        It should have the following keys:
        :return: the `data` dictionary.
        """

        if 'mobileNo' not in data or data['mobileNo'] == '' :
            raise serializers.ValidationError('mobileNo can not be empty !!')
        # if 'plotNo' not in data or data['plotNo'] == '' :
        #     raise serializers.ValidationError('plotNo can not be empty !!')
        # if 'addressLine1' not in data or data['addressLine1'] == '' :
        #     raise serializers.ValidationError('addressLine1  can not be empty !!')
        # if 'pincode' not in data or data['pincode'] == '' :
        #     raise serializers.ValidationError('pincode can not be empty !!')
        return data
    
    def create(self,data):
        """
        The function creates a family head object and associated family member objects using the
        provided data.
        """
        familyMembers_details = data.pop('familyMembers_details')
        data.pop('latitude' , None)
        data.pop('longitude', None)
        head = familyHeadDetails.objects.create(**data)
        member_id_counter = 1
        for family in familyMembers_details:
            member_id = str(head.familyId) + '-' + str(member_id_counter).zfill(2)
            member_id_counter += 1
    
            familyMembers.objects.create(familyHead = head, familySurveyor = head.user, memberId = member_id , **family)
        return head
    


class GetFamilyHeadListSerialzier(serializers.ModelSerializer):
    member = GetFamilyMemberDetailSerializer(many=True, read_only=True)
    class Meta:
        model = familyHeadDetails
        fields = ('id','familyId','name' , 'mobileNo' , 'plotNo',
                  'address' ,  'pincode' ,'totalFamilyMembers' ,
                   'partialSubmit' , 'member')
        # depth = 1



class GetCitizenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = familyMembers
        fields = ('id','name' , 'gender' , 'age' , 'mobileNo' , 'familyHead' ,'aadharAndAbhaConsent' ,'aadharCard' ,  'abhaId' ,'memberId',
                   'pulse', 'bloodPressure','weight' , 'height' , 'BMI' ,
                  'questionsConsent','Questionnaire','bloodConsent' , 'bloodCollectionLocation' )


class DumpExcelSerializer(serializers.Serializer):
    excel_file = serializers.FileField(required=True)