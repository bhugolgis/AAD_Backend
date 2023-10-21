from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import familyHeadDetails , CustomUser , familyMembers
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

@receiver(post_save, sender=familyHeadDetails)
def create_new_user_for_familyHead(sender, instance,created , **kwargs):
    """
    The function creates a new user for a family head and assigns them to the "Family Head" group.
    
    :param sender: The `sender` parameter refers to the object that is sending the signal. In this case,
    it could be any model instance that triggers the signal
    :param instance: The `instance` parameter is an instance of the model that triggered the signal. In
    this case, it is likely an instance of a model representing a family head
    """

    if created: 
        password = str(instance.mobileNo) + '@pass' 
 
        new_instance = CustomUser.objects.create_user(phoneNumber=instance.mobileNo , username= instance.mobileNo , password=password )
        if new_instance:
            group = Group.objects.get(name = 'Family Head')
            new_instance.groups.add(group )
         


@receiver(post_save, sender=familyMembers)
def Update_Partial_Submit_Field(sender, instance, created , **kwargs):
    """
    The function creates a new user for a family head and assigns them to the "Family Head" group.
    
    :param sender: The `sender` parameter refers to the object that is sending the signal. In this case,
    it could be any model instance that triggers the signal
    :param instance: The `instance` parameter is an instance of the model that triggered the signal. In
    this case, it is likely an instance of a model representing a family head
    """

    if created: 
        citizen_count = familyMembers.objects.filter(familyHead_id = instance.familyHead).count()
        print(citizen_count)
        if citizen_count == instance.familyHead.totalFamilyMembers:
            instance.familyHead.partialSubmit = False
            instance.familyHead.save()

         
        
      





