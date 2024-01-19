from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import *
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password


@receiver(post_save , sender=PatientsPathlabrecords)  
def update_Appoinment_schedule_check(sender, instance , created, **kwargs):
    if created:
        family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
        # family.appoinmentSchedule = True 
        family.isSampleCollected = True
        family.save()
      

@receiver(post_save , sender=PatientsPathlabrecords)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    if created:
        family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
        family.isLabTestAdded = True 
        family.save()




