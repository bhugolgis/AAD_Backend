from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
# from .models import *

# class CustomUserManager(BaseUserManager):
   
#     """
#     Custom user model manager where email is the unique identifiers
#     for authentication instead of usernames.
#     """
#     def create_user(self, email, password, **extra_fields):
#         """
#         Create and save a User with the given email and password.
#         """
#         if not email:
#             raise ValueError(_('The Email must be set'))
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user

#     def create_superuser(self, email, password, **extra_fields):
#         """
#         Create and save a SuperUser with the given email and password.
#         """
        
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(_('Superuser must have is_staff=True.'))
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError(_('Superuser must have is_superuser=True.'))
#         return self.create_user(email, password, **extra_fields)

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where phone is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given phone and password.
        """
        if not username:
            raise ValueError('The Username must be provided')
        # email = self.normalize_email(email)

        user = self.model(username=username, **extra_fields)
        user.is_staff = True
        
        user.set_password(password)
        # user.is_staff = True
        user.save()
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given phone and password.
        """
        user = self.create_user(
            username=username,
            
            password=password,
        )
        user.staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user