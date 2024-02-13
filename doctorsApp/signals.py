from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import *

  

@receiver(post_save , sender=PatientsPathlabrecords)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    if created:
        if instance.puid != None and instance.patientID == None and instance.bookingVisitID == None:
        # print(instance.transactionid , "instace created")
            family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)        
            family.generalStatus = 'Patient registerd at LIMS' 
            family.save()


@receiver(post_save , sender=PatientsPathlabrecords)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    if created:
        if instance.puid != None and instance.bookingVisitID != None and instance.patientID != None:
            family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
            family.isLabTestAdded = True 
            family.isSampleCollected = True 
            family.generalStatus = 'Tests Assigned' 
            family.save()
    else:
        if instance.puid != None and instance.transactionid != None:
            family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
            family.isLabTestAdded = True 
            family.isSampleCollected = True 
            family.generalStatus = 'Tests Assigned' 
            family.save()




@receiver(post_save , sender=PatientPathLabReports)  
def update_general_status(sender, instance , created, **kwargs):
    if created:
        family = familyMembers.objects.get(pk=instance.patientPathLab.patientFamilyMember.id)
        family.generalStatus = 'Report received' 
        family.save()
        
