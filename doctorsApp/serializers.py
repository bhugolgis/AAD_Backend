from rest_framework import serializers
from database.models import PatientPathlab

class PatientsPathlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPathlab
        fields = ['patientFamilyMember','LabTestSuggested']
        
        
        


# class ListPatientsPathlabSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PatientsPathlab
#         fields = ['patientFamilyMember_id','LabTestSuggested','suggested_by_doctor_id','patientFamilyMember__familyHead__area','patientFamilyMember__familyHead__pincode','patientFamilyMember__familyHead__address','patientFamilyMember__familyHead__plotNo']


class ListPatientsPathlabSerializer(serializers.ModelSerializer):
    patientFamilyMember_area = serializers.CharField(source='patientFamilyMember.family_head_member.area', read_only=True)
    patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = PatientPathlab
        fields = [
            'patientFamilyMember_id',
            'LabTestSuggested',
            'suggested_by_doctor_id',
            'patientFamilyMember_area',
            'patientFamilyMember_pincode',
            'patientFamilyMember_address',
            'patientFamilyMember_plotNo',
        ]