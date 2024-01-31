from django.urls import path , re_path
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
        path('DownloadAllWardUserList', DownloadAllWardUserList.as_view(), name='DownloadAllWardUserList'),
        path('UserCountsAPI', UserCountsAPI.as_view(), name='UserCountsAPI'),
        
        path('updateGroupResquest', PostUserGroupResquest.as_view(), name='updateGroupResquest'),
        path('updateUserGroupRequest/<int:id>', updateUserGroupRequest.as_view(), name='updateUserGroupRequest'),
        path('GetGroupRequestList', GetGroupRequestList.as_view(), name='GetGroupRequestList'),
        path('GetGroupList', GetGroupList.as_view(), name='GetGroupRequestList'),
        
        path('GetAllUserDetails', GetAllUserDetails, name='GetDataDashboard'),
        
        path('MOHDashboardExcelView', MOHDashboardExportView.as_view(), name='MOHDashboardExportView'),
        path('MOHDashboardView', MOHDashboardView.as_view(), name='MOHDashboardView'),


        path('Admin_dashboard_data', Admin_dashboard_data.as_view(), name='Admin_dashboard_data'),
        
        path('AdminDashboardView', AdminDashboardView.as_view(), name='AdminDashboardView'),
        path('AdminDashboardExportView', AdminDashboardExportView.as_view(), name='AdminDashboardExportView'),

        re_path(r'^GetuserListAPI/(?P<ward_name>.+)/(?P<group>.+)$', userListAPI.as_view(), name='user-list'),
        re_path(r'^GetDeactivatedUserList/(?P<ward_name>.+)/(?P<group>.+)$', GetDeactivatedUserList.as_view(), name='GetDeactivatedUserList'),
        re_path(r'^GetWardWiseSUerList/(?P<group>.+)$', GetWardWiseSUerList.as_view(), name='user-list'),

]