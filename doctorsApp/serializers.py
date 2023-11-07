from rest_framework import serializers
from database.models import *

class PatientsPathlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPathlab
        fields = ['patientFamilyMember','LabTestSuggested']
        
        
        


# class ListPatientsPathlabSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PatientsPathlab
#         fields = ['patientFamilyMember_id','LabTestSuggested','suggested_by_doctor_id','patientFamilyMember__familyHead__area','patientFamilyMember__familyHead__pincode','patientFamilyMember__familyHead__address','patientFamilyMember__familyHead__plotNo']

        
        

class ListPatientsPathlabSerializer(serializers.ModelSerializer):
    # patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    # patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    # patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    # patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = PatientPathlab
        fields = [
            'patientFamilyMember_id',
            'LabTestSuggested',
            'suggested_by_doctor_id',
            # 'patientFamilyMember_FArea',
            # 'patientFamilyMember_pincode',
            # 'patientFamilyMember_address',
            # 'patientFamilyMember_plotNo',
        ]


class PatientPathlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPathlab
        fields = '__all__'

class MedicalOfficerConsultancySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalOfficerConsultancy
        fields = '__all__'

class MedicalOfficerAdviceSerializer(serializers.ModelSerializer):
    # patientsId = serializers.IntegerField()
    # ModoctorRemarks = serializers.CharField(max_length=250)
    # # referedTo = serializers.IntegerField()
    # isCompleted = serializers.BooleanField(default=False)
    class Meta:
        model = MedicalOfficerConsultancy
        fields =('ModoctorRemarks','isCompleted')


class MedicalOfficerReferalAdviceSerializer(serializers.Serializer):
    patientsPathLabReport = serializers.IntegerField(required=True)
    PriDoctor_name = serializers.CharField(max_length=250,default="Test Doctor Name")
    Prispecialization = serializers.CharField(max_length=250,default="Test Specialization")
    referedTo = serializers.IntegerField(required=True)
    # isCompleted = serializers.BooleanField(default=False)
    class Meta:
        # model = MedicalOfficerConsultancy
        fields =('referedTo','PriDoctor_name','patientsPathLabReport','Prispecialization')

class PrimaryConsultancySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimaryConsultancy
        fields = '__all__'

class SecondaryConsultancySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryConsultancy
        fields = '__all__'

class TertiaryConsultancySerializer(serializers.ModelSerializer):
    class Meta:
        model = TertiaryConsultancy
        fields = '__all__'



class LabTestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTests
        fields = '__all__'


class ListPrimaryConsultancyPatientsSerializer(serializers.ModelSerializer):
    # patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    # patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    # patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    # patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = PrimaryConsultancy
        fields = ('PriPatientsConsultancy_id','PriPatientsConsultancy__memberId','PriPatientsConsultancy__name','PriPatientsConsultancy__gender','PriPatientsConsultancy__age','PriPatientsConsultancy__aadharCard','PriPatientsConsultancy__abhaId','PriPatientsConsultancy__isLabTestAdded','PriPatientsConsultancy__isSampleCollected','PriPatientsConsultancy__isLabTestReportGenerated')



class ListSecondaryConsultancyPatientsSerializer(serializers.ModelSerializer):
    # patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    # patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    # patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    # patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = SecondaryConsultancy
        fields = ('SecPatientsConsultancy_id','SecPatientsConsultancy__memberId','SecPatientsConsultancy__name','SecPatientsConsultancy__gender','SecPatientsConsultancy__age','SecPatientsConsultancy__aadharCard','SecPatientsConsultancy__abhaId','SecPatientsConsultancy__isLabTestAdded','SecPatientsConsultancy__isSampleCollected','SecPatientsConsultancy__isLabTestReportGenerated')




class ListTertiaryConsultancyPatientsSerializer(serializers.ModelSerializer):
    # patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    # patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    # patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    # patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = TertiaryConsultancy
        fields = ('TerPatientsConsultancy_id','TerPatientsConsultancy__memberId','TerPatientsConsultancy__name','TerPatientsConsultancy__gender','TerPatientsConsultancy__age','TerPatientsConsultancy__aadharCard','TerPatientsConsultancy__abhaId','TerPatientsConsultancy__isLabTestAdded','TerPatientsConsultancy__isSampleCollected','TerPatientsConsultancy__isLabTestReportGenerated')








class FamilyMemberDetailsSerializer(serializers.ModelSerializer):
    # pathlab_reports = PatientPathlabSerializer(many=True)
    # medicalOfficerconsultancy = MedicalOfficerConsultancySerializer(many=True)
    # primaryConsultancy = PrimaryConsultancySerializer(many=True)
    # secondaryConsultancy = SecondaryConsultancySerializer(many=True)
    # tertiaryConsultancy = TertiaryConsultancySerializer(many=True, read_only=True)
    # area = serializers.SerializerMethodField()

    class Meta:
        model = familyMembers
        fields = ('id','memberId','name','gender','age','mobileNo','familyHead','familySurveyor','area','aadharCard','abhaId','pulse','bloodPressure','weight',
        'height','BMI','Questionnaire','bloodCollectionLocation','questionsConsent','aadharAndAbhaConsent','demandLetter','bloodConsent','cbacScore',
        'created_date','isLabTestAdded','isSampleCollected','isLabTestReportGenerated')
        depth = 1

    # def get_area(self , area):
    #     try:
    #         area_name = area.areas
    #         print(area_name)
    #     except:
    #         area_name = ''
    #         return area_name

       
    # def get_ward(self , data):
	# 	try:
	# 		sectionName = data.section.healthPost.ward.wardName
	# 	except:
	# 		sectionName = ''
	# 	return sectionName


# class ViewFamilyMemberDetailsSerializer(serializers.ModelSerializer):
#     pathlab_reports = PatientPathlabSerializer(many=True)
#     medicalOfficerconsultancy = MedicalOfficerConsultancySerializer(many=True)
#     primaryConsultancy = PrimaryConsultancySerializer(many=True)
#     secondaryConsultancy = SecondaryConsultancySerializer(many=True)
#     tertiaryConsultancy = TertiaryConsultancySerializer(many=True, read_only=True)

#     class Meta:
#         model = familyMembers
#         fields = ('id','memberId','name','gender','age','mobileNo','familyHead','familySurveyor','area','aadharCard','abhaId','pulse','bloodPressure','weight',
#         'height','BMI','Questionnaire','bloodCollectionLocation','questionsConsent','aadharAndAbhaConsent','demandLetter','bloodConsent','cbacScore',
#         'created_date','isLabTestAdded','isSampleCollected','isLabTestReportGenerated','pathlab_reports','medicalOfficerconsultancy','primaryConsultancy','secondaryConsultancy','tertiaryConsultancy')



class FamilyHeadDetailsSerializer(serializers.ModelSerializer):
    family_head_member = FamilyMemberDetailsSerializer(many=True, read_only=True)


    class Meta:
        model = familyHeadDetails
        fields = '__all__'
        


class ListFamilyHeadDetailsSerializer(serializers.ModelSerializer):
    # family_head_member = FamilyMemberDetailsSerializer(many=True, read_only=True)
    HealthPostName = serializers.CharField(source='familyhealthPost.healthPostName', read_only=True)


    class Meta:
        model = familyHeadDetails
        fields = ('id','familyId','name','totalFamilyMembers','area', 'address','mobileNo','HealthPostName','created_datetime', 'pendingMembers', 'partialSubmit')
        depth = 1