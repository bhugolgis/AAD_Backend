from rest_framework import serializers
from database.models import *
from drf_extra_fields.fields import Base64ImageField


# The below class is a serializer in Python that is used to validate and serialize data for a family
# member detail.
class postFamilyMemberDetailSerializer(serializers.ModelSerializer):
    demandLetter = Base64ImageField(required=False)

    class Meta:
        model = familyMembers
        fields = ('name' , 'gender' , 'age' , 'mobileNo' , 'familyHead' ,'area' ,'aadharAndAbhaConsent' ,'aadharCard' ,  'abhaId' , 'ASHA_CHV',
                   'pulse', 'bloodPressure','weight' , 'height' , 'BMI' ,  'questionsConsent','Questionnaire', 'isAbhaCreated', 
                  'bloodConsent' ,'demandLetter', 'bloodCollectionLocation' , 'cbacScore' ,'cbacRequired', 'created_date' ,
                    'referels' , 'deniedBy' , 'vulnerable' , 'vulnerable_choices' , 'vulnerable_reason' , "relationship" , "randomBloodSugar" )
    

    def validate(self, data):
        if 'area' not in data or data['area'] == '':
            raise serializers.ValidationError('area can not be empty !!')
        if 'ASHA_CHV' not in data or data['ASHA_CHV'] == '':
            raise serializers.ValidationError('ASHA-CHV can not be empty !!')
        if 'name' not in data or data["name"] == '':
            raise serializers.ValidationError('name can not be empty !!')
        if 'aadharCard' not in data or data["aadharCard"] == '':
            raise serializers.ValidationError('aadharCard can not be empty !!')
        if 'gender' not in data  or data['gender'] == '' :
            raise serializers.ValidationError('gender can not be empty !!')
        if 'age' not in data  or data['age'] == '' :
            raise serializers.ValidationError('age can not be empty !!')
        if 'mobileNo' not in data or data['mobileNo'] =='':
            raise serializers.ValidationError('mobileNo can not be empty !!')
        return data


class getReferelOptionListSerialzier(serializers.ModelSerializer):
    class Meta:
        model = refereloptions
        fields = ('id', 'choice',)


class getvulnerableOptionListSerialzier(serializers.ModelSerializer):
    class Meta:
        model = vulnerableOptions
        fields = ('id', 'choice',)

class GetFamilyMemberDetailSerializer(serializers.ModelSerializer):
    report = serializers.SerializerMethodField()
    class Meta:
        model = familyMembers
        fields = '__all__'

    def get_report(self , data):
        if data.isLabTestReportGenerated == True:
            try:
                pdf_url = str(data.patientFamilyMember.get().patientPathLabReports.get().pdfResult)
            
            except:
                pdf_url = ''
        else:
            pdf_url = ''

        return pdf_url
       
        

class UpdateFamilyMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = familyMembers
        fields = ('name' , 'gender' , 'age' , 'mobileNo' , 'familyHead' , 'aadharAndAbhaConsent' ,'aadharCard' ,  'abhaId' ,'isAbhaCreated' , 
                   'pulse', 'bloodPressure','weight' , 'height' , 'BMI' ,  'ASHA_CHV', 'cbacRequired', "randomBloodSugar" ,
                  'questionsConsent','Questionnaire' ,'bloodConsent' , 'bloodCollectionLocation' , 'cbacScore' , 'created_date' , 'deniedBy' , 'vulnerable'  , "relationship")
   


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
    longitude = serializers.CharField(max_length=50, required=False)

    class Meta:
        model = familyHeadDetails
        fields = ( 'area','name' , 'mobileNo' , 'plotNo',
                  'address' , 'pincode' ,'totalFamilyMembers' , 'ASHA_CHV',
                 'latitude' , 'longitude'  , 'familyMembers_details' , 'partialSubmit')
        
    def validate(self, data):
        # print(data.latitude)
        # print(data.longitude)
        """
        The function validates the data by checking if certain fields are present and not empty, and
        raises a validation error if any of the checks fail.
        
        :param data: The `data` parameter is a dictionary that contains the information to be validated.
        It should have the following keys:
        :return: the `data` dictionary.
        """

        if 'mobileNo' not in data or data['mobileNo'] == '' :
            raise serializers.ValidationError('mobileNo can not be empty !!')
        if 'area' not in data or data['area'] == '':
            raise serializers.ValidationError('area can not be empty !!')
        if 'ASHA_CHV' not in data or data['ASHA_CHV'] == '':
            raise serializers.ValidationError('ASHA-CHV can not be empty !!')
        
        return data
    
    def create(self,data):
        """
        The function creates a family head object and associated family member objects using the
        provided data.
        """
        familyMembers_details = data.pop('familyMembers_details')
        # print(data.latitude , data.longitude)
        data.pop('latitude' , None)
        data.pop('longitude', None)
               
        head = familyHeadDetails.objects.create(**data)
        member_id_counter = 1
        for family in familyMembers_details:
            try:
                reffer = family.pop('referels')
            except:
                reffer = []
            try:
            # print(reffer , "referels")
                vulnerable = family.pop('vulnerable_choices')
            except:
                vulnerable = []
            # print(vulnerable , "vulnerable_choices")
            member_id = str(head.familyId) + '-' + str(member_id_counter).zfill(2)
            member_id_counter += 1
            instance = familyMembers.objects.create(familyHead = head, familySurveyor = head.user, memberId = member_id , **family)
            instance.referels.add(*reffer)
            instance.vulnerable_choices.add(*vulnerable)

        return head
    


class GetFamilyHeadListSerialzier(serializers.ModelSerializer):
    member = GetFamilyMemberDetailSerializer(many=True, read_only=True)
    class Meta:
        model = familyHeadDetails
        fields = ('id','familyId','name' , 'mobileNo' , 'plotNo',
                  'address' ,  'pincode' ,'totalFamilyMembers' , 'pendingMembers' , 'ASHA_CHV',
                   'partialSubmit' , 'member')
      



class GetCitizenListSerializer(serializers.ModelSerializer):
    report = serializers.SerializerMethodField()
    class Meta:
        model = familyMembers
        fields = ('id','name' , 'gender' , 'age' , 'mobileNo' , 'familyHead','ASHA_CHV' ,'area' ,'aadharAndAbhaConsent' ,'aadharCard' ,  'abhaId' ,'memberId',
                   'pulse', 'bloodPressure','weight' , 'height' , 'BMI' , 'cbacRequired', "randomBloodSugar" , 'isAbhaCreated' , 
                  'questionsConsent','Questionnaire','bloodConsent' , 'bloodCollectionLocation' , 'created_date' , 'deniedBy' , 'vulnerable' , "relationship"  , "report")

    def get_report(self , data):
        if data.isLabTestReportGenerated == True:
            try:
                pdf_url = str(data.patientFamilyMember.get().patientPathLabReports.get().pdfResult)
            
            except:
                pdf_url = ''
        else:
            pdf_url = ''

        return pdf_url

class DumpExcelSerializer(serializers.Serializer):
    excel_file = serializers.FileField(required=True) 