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
    patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = PatientPathlab
        fields = [
            'patientFamilyMember_id',
            'LabTestSuggested',
            'suggested_by_doctor_id',
            'patientFamilyMember_FArea',
            'patientFamilyMember_pincode',
            'patientFamilyMember_address',
            'patientFamilyMember_plotNo',
        ]


class PatientPathlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPathlab
        fields = '__all__'

class MedicalOfficerConsultancySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalOfficerConsultancy
        fields = '__all__'

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




class ListPrimaryConsultancyPatientsSerializer(serializers.ModelSerializer):
    patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = PrimaryConsultancy
        fields = '__all__'









class FamilyMemberDetailsSerializer(serializers.ModelSerializer):
    pathlab_reports = PatientPathlabSerializer(many=True, read_only=True)
    medicalOfficerconsultancy = MedicalOfficerConsultancySerializer(many=True, read_only=True)
    primaryConsultancy = PrimaryConsultancySerializer(many=True, read_only=True)
    secondaryConsultancy = SecondaryConsultancySerializer(many=True, read_only=True)
    tertiaryConsultancy = TertiaryConsultancySerializer(many=True, read_only=True)

    class Meta:
        model = familyMembers
        fields = '__all__'

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
        fields = ('id','familyId','name','totalFamilyMembers','mobileNo','area','HealthPostName','created_datetime','partialSubmit')