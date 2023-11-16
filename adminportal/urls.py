from django.urls import path , re_path
from .views import *
from . import views
from knox.views import LogoutView
from .views import *


urlpatterns = [
        path('InsertUsers' , InsertUsers.as_view() , name = 'InsertUsers'),
        path('UpdateUserDetailsAPI/<int:pk>', UpdateUserDetails.as_view(), name='UpdateUserDetailsAPI'),
        path('deleteUserAPI/<int:id>', deleteUser.as_view(), name='deleteUserAPI'),
        path('UserCountsAPI', UserCountsAPI.as_view(), name='deleteUserAPI'),


]