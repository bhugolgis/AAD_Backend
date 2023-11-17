from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import *


      
@receiver(post_save , sender=PatientPathlab)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    print("Created")
    if created:
        family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
        print(family)
        family.isLabTestAdded = True 
        family.save()




