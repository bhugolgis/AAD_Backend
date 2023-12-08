from django.urls import path , re_path
from .views import *
from . import views
from knox.views import LogoutView
from .views import *


urlpatterns = [
        path('InsertUsersByadmin' , InsertUsersByadmin.as_view() , name = 'InsertUsersByadmin'),
        path('InsertUsersByMOH' , InsertUsersByMOH.as_view() , name = 'InsertUsersByMOH'),
        path('UpdateUserDetailsAPI/<int:pk>', UpdateUserDetails.as_view(), name='UpdateUserDetailsAPI'),
        path('deleteUserAPI/<int:id>', deleteUser.as_view(), name='deleteUserAPI'),
        path('AdminChangePasswordView/<int:id>', AdminChangePasswordView.as_view(), name='deleteUserAPI'),
        path('DownloadHealthpostwiseUserList/<int:id>', DownloadHealthpostwiseUserList.as_view(), name='DownloadHealthpostwiseUserList'),
        path('DownloadWardtwiseUserList/<int:id>', DownloadWardwiseUserList.as_view(), name='DownloadWardtwiseUserList'),
        path('DownloadDispensarywiseUserList/<int:id>', DownloadDispensarywiseUserList.as_view(), name='DownloadDispensarywiseUserList'),
        path('UserCountsAPI', UserCountsAPI.as_view(), name='UserCountsAPI'),
        # path('MOHDashboardView', MOHDashboardView.as_view(), name='MOHDashboardView'),
        path('GetDeactivatedUserList', GetDeactivatedUserList.as_view(), name='GetDeactivatedUserList'),

        path('MoHDashboard', MoHDashboard, name='MoHDashboard'),

        path('AdminDashboard', AdminDashboard, name='AdminDashboard'),


        re_path(r'^GetuserListAPI/(?P<group>.+)/(?P<ward_id>.+)$', userListAPI.as_view(), name='user-list'),
        # re_path(r'^GetWardWiseSUerList/(?P<group>.+)/(?P<ward>.+)$', GetWardWiseSUerList.as_view(), name='user-list'),
        re_path(r'^GetWardWiseSUerList/(?P<group>.+)$', GetWardWiseSUerList.as_view(), name='user-list'),

]