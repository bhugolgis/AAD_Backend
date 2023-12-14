from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import familyHeadDetails , CustomUser , familyMembers , UserApprovalRecords
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

@receiver(post_save, sender= UserApprovalRecords)
def update_user_group(sender, instance,created , **kwargs):
    """
    The function creates a new user for a family head and assigns them to the "Family Head" group.
    
    :param sender: The `sender` parameter refers to the object that is sending the signal. In this case,
    it could be any model instance that triggers the signal
    :param instance: The `instance` parameter is an instance of the model that triggered the signal. In
    this case, it is likely an instance of a model representing a family head
    """

    if created: 
        group = Group.objects.get(id=instance.new_group.id)
        if instance.status == True:
            instance.user.groups.clear()
            instance.user.groups.add(group)
            