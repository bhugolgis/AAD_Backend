from django.urls import path , re_path
from .views import *
from . import views
from knox.views import LogoutView
from .views import *


urlpatterns = [
        path('InsertUsers' , InsertUsers.as_view() , name = 'InsertUsers'),
        path('UpdateUserDetailsAPI/<int:pk>', UpdateUserDetails.as_view(), name='UpdateUserDetailsAPI'),
        path('deleteUserAPI/<int:id>', deleteUser.as_view(), name='deleteUserAPI'),
        path('AdminChangePasswordView/<int:id>', AdminChangePasswordView.as_view(), name='deleteUserAPI'),
        path('UserCountsAPI', UserCountsAPI.as_view(), name='UserCountsAPI'),
        # path('GetASHA_CHV', GetASHA_CHV.as_view(), name='GetASHA_CHV'),
        re_path(r'^GetuserListAPI/(?P<group>.+)$', userListAPI.as_view(), name='user-list'),
        # re_path(r'^LabtestUpdate/(?P<caseNumber>.+)$'

]