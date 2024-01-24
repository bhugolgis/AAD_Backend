from rest_framework import serializers
from database.models import *

class PatientsPathlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientsPathlabrecords
        fields = ['patientFamilyMember','LabTestSuggested']
        
        
        


class ListPatientsPathlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientsPathlabrecords
        fields = ['patientFamilyMember_id','LabTestSuggested','suggested_by_doctor_id','patientFamilyMember__familyHead__area','patientFamilyMember__familyHead__pincode','patientFamilyMember__familyHead__address','patientFamilyMember__familyHead__plotNo']

        
        

class ListPatientsPathlabSerializer(serializers.ModelSerializer):
    # patientFamilyMember_FArea = serializers.CharField(source='patientFamilyMember.family_head_member.FArea', read_only=True)
    # patientFamilyMember_pincode = serializers.IntegerField(source='patientFamilyMember.family_head_member.pincode', read_only=True)
    # patientFamilyMember_address = serializers.CharField(source='patientFamilyMember.family_head_member.address', read_only=True)
    # patientFamilyMember_plotNo = serializers.CharField(source='patientFamilyMember.family_head_member.plotNo', read_only=True)

    class Meta:
        model = PatientsPathlabrecords
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
        model = PatientsPathlabrecords
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





class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPathLabReports
        fields = ('pdfResult' ,)


class FamilyMemberDetailsSerializer(serializers.ModelSerializer):
    report = serializers.SerializerMethodField()
    Healthpost = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    ANM_coordinator = serializers.SerializerMethodField()
    ANM_number = serializers.SerializerMethodField()
    HOF_Number = serializers.SerializerMethodField()
    centerName = serializers.SerializerMethodField()
    vulnerable_reason = serializers.SerializerMethodField()


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
    
    def get_vulnerable_reason(self , data):
        if data.vulnerable == True:
            vulnerable_reason = []
            try:
                
                vulnerables = data.vulnerable_choices.all()
                for i in vulnerables:
                    vulnerable_reason.append(i.choice)
            
            except:
                vulnerable_reason = []
        else:
            vulnerable_reason = []

        return vulnerable_reason
    
    def get_centerName(self , data): 
        try:
            centerName = data.patientFamilyMember.get().centerName
           
        except:
            centerName = ''
        return centerName
    
    def get_ANM_number(self , data): 
        try:
            ANM_number = data.familySurveyor.phoneNumber
        except:
            ANM_number = ''
        return ANM_number
    
    def get_HOF_Number(self , data):
        try:
            HOF_Number = data.familyHead.mobileNo
        except:
            HOF_Number = ''
        return HOF_Number
    

    def get_ward(self , data ):
        try:
            userSections = data.familySurveyor.userSections.all()[0]
            Ward_id = userSections.healthPost.ward.wardName
        except:
            try:
                Ward_id = data.dispensary.ward.wardName
            except:
                Ward_id = ""
        return Ward_id
    
    def get_Healthpost(self , data):
        try:
            section = data.familySurveyor.userSections.all()[0]
            healthPostName = section.healthPost.healthPostName
        except:
            healthPostName = ''
        return healthPostName

    def get_ANM_coordinator(self , data):
        try:
            ANM_coordinator = data.familySurveyor.name
        except:
            ANM_coordinator = ''
        return ANM_coordinator
        


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
        fields = ('id','familyId','name','totalFamilyMembers','area', 'address','mobileNo','HealthPostName', 'pendingMembers', 'partialSubmit' , 'created_date')
        depth = 1


class BookPatientSerializer(serializers.Serializer):
    # authKey = serializers.CharField(max_length=100 , default = "05436EFE3826447DBE720525F78A9EEDBMC")
    centerName = serializers.CharField (max_length=500 , required = True )
    id = serializers.IntegerField()
    RegisteredDate= serializers.CharField(max_length=100)
    PRNNo= serializers.CharField(max_length=100)
    PatientCategory= serializers.CharField(max_length=100 )
    PatientType= serializers.CharField(max_length=100)
    RefDrCode= serializers.CharField(max_length=100)
    refDrName= serializers.CharField(max_length=100)
    RefLabCode= serializers.CharField(max_length=100)
    PatientName= serializers.CharField(max_length=100)
    Age= serializers.IntegerField()
    BirthDate= serializers.CharField(max_length=100 , required = False)
    PaymentAmount= serializers.IntegerField(default = 0 , required = False)
    CreatedBy= serializers.CharField(max_length=100)
    AgeUnit= serializers.CharField(max_length=100)
    Gender= serializers.CharField(max_length=100)
    PatientAddress= serializers.CharField(max_length=100 , required = False)
    IdentityNumber= serializers.CharField(max_length=100 , required = False)
    MobileNumber= serializers.CharField(max_length=100 , required = False) 
    HisUniquePatientCode= serializers.CharField(max_length=100)
    HisHospitalRefNo= serializers.CharField(max_length=100)
    Booking_TestDetails = serializers.JSONField(write_only=True , required = True)



class HomeBookPatientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    BookingDate= serializers.CharField(max_length=100)
    slots= serializers.CharField(max_length=250)
    CollectionAddress= serializers.CharField(max_length=500)
    labaddress= serializers.CharField(max_length=500)
    TransactionForId= serializers.CharField(max_length=500)
    latitude= serializers.CharField(max_length=100)
    UserId = serializers.CharField(max_length=100)
    longitude= serializers.CharField(max_length=100)
    note= serializers.CharField(max_length=500 , required = False)
    PatientAge= serializers.CharField(max_length=100)
    patientMobile= serializers.CharField(max_length=100 , required = False)
    patientname = serializers.CharField(max_length=100)
    PatientUid= serializers.CharField(max_length=100)
    pincode= serializers.CharField(max_length=100)
    Booking_TestDetails = serializers.JSONField(write_only=True , required = True)


class LIMSPatientRegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    adharcard = serializers.CharField(max_length=250)
    address = serializers.CharField(max_length=250)
    age = serializers.CharField(max_length=25)
    birthdate = serializers.CharField()
    bloodgroup = serializers.CharField(max_length=250)
    emailid = serializers.EmailField(max_length=100)
    gender = serializers.CharField()
    labID = serializers.CharField()
    mobileno = serializers.CharField()
    name = serializers.CharField()
    pincode = serializers.CharField()
    title = serializers.CharField()
 