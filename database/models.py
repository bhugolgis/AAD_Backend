from email.policy import default
import re
from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin ,AbstractBaseUser
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import Group
# from .models import familyHeadDetails




class HealthCareCenters(models.Model):
    CenterTypeChoices = [
         ("PHCC" , "Primary Health Care Center"),
         ("SHCC" , "Secondary Health Care Center") ,
         ("THCC" , "Tertiary Health Care Center"),
    ]
    healthCareName = models.CharField(max_length=255, blank = True , null = True)
    HhealthcareAddress= models.CharField(max_length=500, blank = True , null = True)
    healthCareContactNumber= models.CharField(max_length=500, blank = True , null = True)
    healthCareType = ArrayField(models.CharField(max_length=255 , choices=CenterTypeChoices ,default=list ) , blank = True , null = True )


    def __str__(self) -> str:
         return self.healthCareName


class ward(models.Model):
    wardName = models.CharField(max_length=255 ,unique= True , blank = True , null = True)

    def __str__(self) -> str:
         return self.wardName

class dispensary(models.Model):
    ward = models.ForeignKey(ward, related_name="ward_dispensary", on_delete=models.SET_NULL, blank = True, null = True )
    dispensaryName = models.CharField(max_length=255 , blank = True , null = True )


class healthPost(models.Model):
    ward = models.ForeignKey(ward , related_name="ward_name" , on_delete=models.SET_NULL , blank = True , null = True )
    # dispensary = models.ForeignKey(dispensary, related_name="dispensarys_name", on_delete=models.SET_NULL, blank = True, null = True )
    healthPostName = models.CharField(max_length= 1000, unique= True ,  blank = True , null = True )

    def __str__(self) -> str:
         return self.healthPostName

class area(models.Model):
    dispensary = models.ForeignKey(dispensary, related_name = "area_dispensarys_name", on_delete=models.SET_NULL , blank = True , null = True )
    healthPost = models.ForeignKey(healthPost , related_name="area_healthpost_name" , on_delete=models.SET_NULL , blank= True , null = True )
    areas= models.TextField(max_length=1000 , blank = True , null = True  )


class section(models.Model):
    healthPost = models.ForeignKey(healthPost , related_name="healthPost_name" , on_delete=models.SET_NULL , blank = True , null = True )
    sectionName = models.CharField(max_length=255 , blank = True , null = True )

    def __str__(self) -> str:
        return self.sectionName




class CustomUser(AbstractUser, PermissionsMixin):
    name=models.CharField(max_length=300,blank=True,null=True)
    username=models.CharField(max_length=255,unique=True)
    emailId=models.EmailField(max_length=255,blank=True,null=True)
    phoneNumber=models.CharField(max_length=20,blank=True,null=True , unique = True )
    otpChecked = models.BooleanField(default=False)
    created_by = models.ForeignKey('CustomUser',related_name="supervisorId",on_delete=models.SET_NULL,null=True,blank=True)
    userSections = models.ManyToManyField(section , related_name = "multiple_Section" , blank = True )
    section = models.ForeignKey( section , related_name="section_name" , on_delete=models.SET_NULL , blank = True , null = True )
    ward = models.ForeignKey(ward , related_name="wardAmo_mo_name" , on_delete=models.SET_NULL , blank = True , null = True )
    health_Post = models.ForeignKey(healthPost , related_name="healthpostAmo_mo_name" , on_delete=models.SET_NULL , blank = True , null = True )
    area = models.ForeignKey(area , related_name="areaAmo_mo_name" , on_delete=models.SET_NULL , blank = True , null = True ) # By area we can find the health post , dispensary and Ward
    dispensary = models.ForeignKey(dispensary , related_name="dispensary_name" , on_delete=models.SET_NULL , blank = True , null = True )
    HealthCareCenters = models.ForeignKey(HealthCareCenters,related_name="HealthCareDoctor",on_delete=models.CASCADE,null=True,blank=True)
    ANM = models.ForeignKey('CustomUser',related_name="ANM_Id",on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default = False)
    created_date = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'phoneNumber'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
         return self.username

class UserApprovalRecords(models.Model):
    user = models.ForeignKey(CustomUser , related_name= "UserApprovalRecords" , on_delete=models.SET_NULL , blank = True , null = True )
    requester = models.ForeignKey(CustomUser , related_name= "UserRequester" , on_delete=models.SET_NULL , blank = True , null = True )
    old_group = models.ForeignKey( Group, related_name = "user_old_Group" , on_delete= models.CASCADE ,blank = True , null = True )
    new_group = models.ForeignKey( Group, related_name = "user_new_Group" , on_delete= models.CASCADE ,blank = True , null = True )
    status = models.BooleanField( default=False)
    request_date = models.DateTimeField(blank = True , null= True)
    approve_date = models.DateTimeField(blank = True , null= True)


class sendOtp(models.Model):
    registerUser = models.ForeignKey(CustomUser,related_name="Registeruser",on_delete=models.CASCADE,null=True,blank=True)
    otp = models.CharField(max_length=6,blank=True,null=True)
    otpVerified = models.BooleanField(default=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    expireyDate = models.DateTimeField(blank=True,null=True)

class refereloptions(models.Model):
    choice = models.CharField(max_length=255 , blank = True, null=True)
    createdDate = models.DateField(auto_now_add= True)

class vulnerableOptions(models.Model):
    choice = models.CharField(max_length=255 , blank = True, null = True )
    createdDate = models.DateField(auto_now_add= True)

class familyHeadDetails(models.Model):

    familyId = models.CharField(max_length=150,blank=True,null=True , unique= True)
    name = models.CharField(max_length=255 , blank= True , null = True)
    mobileNo = models.BigIntegerField(unique= True , blank=True,null=True)
    plotNo = models.CharField(max_length=50 , blank= True , null= True)
    address = models.CharField(max_length=500,blank=True,null=True)
    # addressLine2 = models.CharField(max_length=500,blank=True,null=True)
    pincode = models.IntegerField(blank=True,null=True)
    area = models.ForeignKey(area, related_name="familyheaddeatils_area" , on_delete=models.CASCADE , blank= True , null= True )
    totalFamilyMembers = models.IntegerField(default=0)
    pendingMembers = models.IntegerField(default=0)
    location = models.PointField(blank= True , null= True )
    user = models.ForeignKey(CustomUser,related_name="surveyDoneBy", on_delete=models.CASCADE,null=True,blank=True)
    ASHA_CHV = models.ForeignKey(CustomUser , related_name="ASHA_CHV_family_head",on_delete=models.SET_NULL , blank = True , null = True)
    partialSubmit = models.BooleanField(default= False)
    created_date= models.DateTimeField(auto_now_add= True )
    isLabTestAdded = models.BooleanField(default=False)
    isSampleCollected = models.BooleanField(default=False)
    isLabTestReportGenerated = models.BooleanField(default=False)



class familyMembers(models.Model):
    bloodCollectionLocation_choices = [
         ("Home" , "Home"),
         ("Center" , "Center") ,
         ("Denied" , "Denied"),
         ("Not Required" , "Not Required"),
         ("Individual Itself" , "Individual Itself"),
         ("AMO" , "AMO"),
    ]
    relationship_choices = [
         ("Self" , "Self"),
         ("Mother" , "Mother"),
         ("Father" , "Father"),
         ("Spouse" , "Spouse"),
         ("Son" , "Son"),
         ("Daughter" , "Daughter"),
         ("Grandson" , "Grandson"),
         ("Granddaughter" , "Granddaughter"),
         ("Grandmother" , "Grandmother"),
         ("Grandfather" , "Grandfather"),
         ("Uncle" , "Uncle"),
         ("Aunty" , "Aunty"),
         ("Nephew" , "Nephew"),
         ("Niece" , "Niece"),
         ("Sibling" , "Sibling"),
         ("SonInLaw","SonInLaw"),
         ("DaughterInLaw","DaughterInLaw")


    ]
    caseCompletion_Choices = [
        ("Referral" , "Referral"),
        ("Diagnosis/Treatment" , "Diagnosis/Treatment"),
    ]

    memberId = models.CharField(max_length=255 , blank = True , null = True )
    name = models.CharField(max_length=900,blank=True,null=True)
    gender = models.CharField(max_length=15,blank=True,null=True)
    age  = models.IntegerField(blank = True , null = True)
    mobileNo  = models.BigIntegerField(blank = True , null = True , default=0)
    familyHead = models.ForeignKey(familyHeadDetails,related_name="family_head_member",on_delete=models.CASCADE,null=True,blank=True)
    familySurveyor = models.ForeignKey(CustomUser,related_name="familysurveyor",on_delete=models.CASCADE,null=True,blank=True)
    ASHA_CHV = models.ForeignKey(CustomUser , related_name="ASHA_CHV_family_Member",on_delete=models.SET_NULL , blank = True , null = True)
    area = models.ForeignKey(area , related_name="familymembers_area" , on_delete=models.CASCADE, blank = True , null = True  )
    aadharCard = models.BigIntegerField(blank = True , null = True , default=0)
    abhaId = models.CharField(max_length=100 , blank= True , null = True )
    isAbhaCreated = models.BooleanField(default=False)
    pulse = models.CharField(max_length=50 , blank = True , null = True)
    bloodPressure = models.CharField(max_length=50 , blank = True , null = True)
    weight = models.CharField(max_length=50 , blank = True , null = True)
    height = models.CharField(max_length=50 , blank = True , null = True)
    BMI = models.CharField(max_length=50 , blank = True , null = True)
    randomBloodSugar = models.CharField(max_length=50 , blank = True , null = True)

    Questionnaire = models.JSONField(blank= True , null = True)
    bloodCollectionLocation = models.CharField(max_length= 20 , choices= bloodCollectionLocation_choices , blank= True , null = True  )
    questionsConsent = models.BooleanField(default= False)
    aadharAndAbhaConsent = models.BooleanField(default= False)
    demandLetter = models.ImageField(upload_to= 'demand letter' , blank = True , null = True )
    bloodConsent = models.BooleanField(default= False)
    cbacScore = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now= True)
    isLabTestAdded = models.BooleanField(default=False)
    isSampleCollected = models.BooleanField(default=False)
    isLabTestReportGenerated = models.BooleanField(default=False)
    generalStatus = models.CharField(max_length=100 , default = 'Survey Completed' )
    cbacRequired = models.BooleanField( default= False)
    referels = models.ManyToManyField(refereloptions , related_name="refereloptions_related" , blank = True , )
    deniedBy = models.CharField(max_length=100 , blank = True , null = True)
    vulnerable  = models.BooleanField(default=False)
    vulnerable_choices  = models.ManyToManyField(vulnerableOptions , related_name= 'vulnerability_choices', blank = True )
    vulnerable_reason = models.TextField(max_length=500 , blank  = True , null = True )
    relationship = models.CharField(max_length = 100 , choices = relationship_choices ,  blank = True , null = True )
    caseCompletion = models.CharField(max_length = 100 , choices = caseCompletion_Choices , blank = True)

    def bool_transform(self, field:str) -> str:
        value = getattr(self,field,False)
        if value:
            return "YES"
        else:
            return "NO"

    def get_systolic_pressure(self):
        """This function will return the systolic value of bloodPressure."""
        systolic_pressure = self.bloodPressure.split("/")
        try:
            return int(systolic_pressure[0])
        except Exception:
            return 0


class PatientsPathlabrecords(models.Model):
    patientFamilyMember = models.ForeignKey(familyMembers , related_name='patientFamilyMember' ,on_delete=models.SET_NULL , blank = True , null = True )
    suggested_by_doctor = models.ForeignKey(CustomUser , related_name='suggested_by_doctor' , on_delete=models.SET_NULL ,  blank = True , null = True  )
    suggested_date = models.DateTimeField(auto_now=True)
    LabTestSuggested = models.JSONField(default=dict)
    PatientSampleTaken = models.BooleanField(default=False)
    PathLab = models.ForeignKey(CustomUser,related_name="PathLab",on_delete=models.CASCADE,null=True,blank=True)
    ReportCheckByDoctor = models.ForeignKey(CustomUser,related_name="ReportCheckByDoctor",on_delete=models.CASCADE,null=True,blank=True)
    LabTestReport = models.JSONField(default = dict,null=True,blank=True)
    doctorRemarks = models.CharField(max_length=500,blank=True,null=True)
    PathLabRemarks = models.CharField(max_length=500,blank=True,null=True)
    response_date = models.DateTimeField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now=True)
    isCompleted = models.BooleanField(default=False)
    CentreID = models.CharField(max_length=255 , blank = True, null=True )
    centerName = models.CharField(max_length=255, blank = True, null = True )
    bookingVisitID = models.CharField(max_length=255 , blank = True, null=True )
    puid =models.CharField(max_length=255 , blank = True, null=True )
    patientID =models.CharField(max_length=255 , blank = True, null=True )
    citizenRejectedLabTest = models.BooleanField(default=False)
    transactionid = models.CharField(max_length=255, blank = True, null = True )

class PatientPathLabReports(models.Model):
    patientPathLab = models.ForeignKey(PatientsPathlabrecords , related_name="patientPathLabReports" , on_delete=models.CASCADE)
    pdfResult = models.FileField(upload_to='patientPathLabResults'  , max_length=500 , blank = True , null = True)
    pdfUrl = models.URLField(max_length= 500 , blank = True , null = True )
    jsonResult = models.JSONField(blank = True , null = True )
    created_at = models.DateTimeField(auto_now_add = True)

class MedicalOfficerConsultancy(models.Model):
    #patientLabTest to patientTest
    MoPatientsPathReport = models.ForeignKey(PatientsPathlabrecords,related_name="moPatientsPathReport",on_delete=models.CASCADE,null=True,blank=True)
    MoPatientsConsultancy = models.ForeignKey(familyMembers,related_name="moPatientsConsultancy",on_delete=models.CASCADE,null=True,blank=True)
    MooassignedDoctor = models.ForeignKey(CustomUser,related_name="moassignedDoctor",on_delete=models.CASCADE,null=True,blank=True)
    Moodoctor_name = models.CharField(max_length=500,blank=True,null=True)
    Mospecialization = models.CharField(max_length=500,blank=True,null=True)
    ModoctorRemarks = models.CharField(max_length=500,blank=True,null=True)
    MofileUpload = models.FileField(upload_to='doctorFolder',blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    referedToPrimaryConsultancy = models.BooleanField(default=False)
    isCompleted = models.BooleanField(default=False)

class PrimaryConsultancy(models.Model):
    #patientLabTest to patientTest
    ReferByMedicalOfficer = models.ForeignKey(CustomUser,related_name="referByDoctor",on_delete=models.CASCADE,null=True,blank=True)
    PriPatientsPathReport = models.ForeignKey(PatientsPathlabrecords,related_name="PriPatientsPathReport",on_delete=models.CASCADE,null=True,blank=True)
    PriPatientsConsultancy = models.ForeignKey(familyMembers,related_name="PriPatientsConsultancy",on_delete=models.CASCADE,null=True,blank=True)
    PriassignedDoctor = models.ForeignKey(CustomUser,related_name="PriassignedDoctor",on_delete=models.CASCADE,null=True,blank=True)
    PriDoctor_name = models.CharField(max_length=500,blank=True,null=True)
    Prispecialization = models.CharField(max_length=500,blank=True,null=True)
    PridoctorRemarks = models.CharField(max_length=500,blank=True,null=True)
    fileUpload = models.FileField(upload_to='doctorFolder',blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    referedToSecondaryConsultancy = models.BooleanField(default=False)
    isCompleted = models.BooleanField(default=False)

class SecondaryConsultancy(models.Model):
    #patientLabTest to patientTest
    ReferByPrimaryDoctor = models.ForeignKey(CustomUser,related_name="ReferByPrimaryDoctor",on_delete=models.CASCADE,null=True,blank=True)
    SecPatientsPathReport = models.ForeignKey(PatientsPathlabrecords,related_name="SecPatientsPathReport",on_delete=models.CASCADE,null=True,blank=True)
    SecPatientsConsultancy = models.ForeignKey(familyMembers,related_name="SecPatientsConsultancy",on_delete=models.CASCADE,null=True,blank=True)
    SecSecassignedDoctor = models.ForeignKey(CustomUser,related_name="SecassignedDoctor",on_delete=models.CASCADE,null=True,blank=True)
    Secdoctor_name = models.CharField(max_length=500,blank=True,null=True)
    Secspecialization = models.CharField(max_length=500,blank=True,null=True)
    SecdoctorRemarks = models.CharField(max_length=500,blank=True,null=True)
    SecfileUpload = models.FileField(upload_to='doctorFolder',blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    isCompleted = models.BooleanField(default=False)

class TertiaryConsultancy(models.Model):
    #patientLabTest to patientTest
    ReferBySecondaryDoctor = models.ForeignKey(CustomUser,related_name="ReferBySecondaryDoctor",on_delete=models.CASCADE,null=True,blank=True)
    TerPatientsPathReport = models.ForeignKey(PatientsPathlabrecords,related_name="TerPatientsPathReport",on_delete=models.CASCADE,null=True,blank=True)
    TerPatientsConsultancy = models.ForeignKey(familyMembers,related_name="TerPatientsConsultancy",on_delete=models.CASCADE,null=True,blank=True)
    TerassignedDoctor = models.ForeignKey(CustomUser,related_name="TerassignedDoctor",on_delete=models.CASCADE,null=True,blank=True)
    Terdoctor_name = models.CharField(max_length=500,blank=True,null=True)
    Terspecialization = models.CharField(max_length=500,blank=True,null=True)
    TerdoctorRemarks = models.CharField(max_length=500,blank=True,null=True)
    fileUpload = models.FileField(upload_to='doctorFolder',blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    referedToTertiaryConsultancy = models.BooleanField(default=False)

    isCompleted = models.BooleanField(default=False)


class LabTests(models.Model):
    testName = models.CharField(max_length=500,blank=True,null=True)
    testId = models.CharField(max_length=200 , unique= True ,  blank = True , null = True )
    description = models.CharField(max_length=500,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=True)

    def __str__(self) -> str:
         return self.testName