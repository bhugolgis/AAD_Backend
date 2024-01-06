from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import *

  
@receiver(post_save , sender=PatientsPathlabrecords)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    if created:
        family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
        family.isLabTestAdded = True 
        family.generalStatus = 'Appointment Booked' 
        family.save()



@receiver(post_save , sender=PatientPathLabReports)  
def update_general_status(sender, instance , created, **kwargs):
    if created:
        family = familyMembers.objects.get(pk=instance.patientPathLab.patientFamilyMember.id)
        family.generalStatus = 'Report generated' 
        family.save()
