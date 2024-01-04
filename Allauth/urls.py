from django.urls import path , re_path
from .views import *
from . import views
from knox.views import LogoutView


urlpatterns = [
        # path('CustomLoginAPI' , CustomLoginAPI.as_view() , name = 'CustomLoginAPI'),
        path('AddWardAPI', AddWardAPI.as_view(), name='AddWardAPI'),
        path('AddHealthPostAPI', AddHealthPostAPI.as_view(), name='AddHealthPostAPI'),
        path('GetCHV_ASHA_list/<int:id>', GetCHV_ASHA_list.as_view(), name='AddHealthPostAPI'),
        path('AddsectionAPI', AddsectionAPI.as_view(), name='AddsectionAPI'),
        path('AddDispensaryAPI', AddDispensaryAPI.as_view(), name='AddDispensaryAPI'),
        path('AddAreaAPI', AddAreaAPI.as_view(), name='AddAreaAPI'),
        # path('InsertUsers', InsertUsers.as_view(), name='knox_logout'),
        path('login', LoginView.as_view(), name='login'),
        path('GetHealthPostAreas/<str:id>' , GetHealthPostAreasAPI.as_view() , name = 'GetHealthPostAreas'),
        re_path(r'^GetWardAreasAPI/(?P<wardName>.+)$' , GetWardAreasAPI.as_view() , name = 'GetHealthPostAreas'),
        path('GetSectionListAPI/<str:id>' , GetSectionListAPI.as_view() , name = 'GetSectionListAPI'),
        path('updateSectionAPI/<int:id>' , updateSectionAPI.as_view() , name = 'updateSectionAPI'),
        path('updateAreaAPI/<int:id>' , updateAreaAPI.as_view() , name = 'updateAreaAPI'),
        re_path(r'^GetWardSectionListAPI/(?P<wardName>.+)$' , GetWardSectionListAPI.as_view() , name = 'GetSectionListAPI'),
        path('GethealthPostNameListAPI/<str:id>' , GethealthPostNameListAPI.as_view() , name = 'GethealthPostNameListAPI'),
        re_path(r'^GetWardListAPI', GetWardListAPI.as_view(), name='GetWardListAPI'),
        # re_path(r'^GethealthPostNameList', GethealthPostNameListAPI.as_view(), name='GethealthPostNameList'),
        # re_path(r'^GetSectionListAPI', GetSectionListAPI.as_view(), name='GetSectionListAPI'),
        re_path(r'^GetDispensaryListAPI/(?P<id>.+)$', GetDispensaryListAPI.as_view(), name='GetDispensaryListAPI'),
                
        path('healthcarecenters', HealthCareCentersList.as_view(), name='healthcare-centers-list'),
        path('GetCoordPassword', GetCoordPassword.as_view(), name='GetCoordPassword'),
        # path('healthcarecenters/<int:pk>/', HealthCareCentersDetail.as_view(), name='healthcare-centers-detail'),
        path('AddlabtestdeatilsAPI', AddlabtestdeatilsAPI.as_view(), name='healthcare-centers-detail'),
        path('usersList', UserGroupFilterView.as_view(), name='user-list'),
        path('SendOtp',views.SendOtp),
        path('CheckOtp',CheckOtp.as_view(),name="CheckOtp"),
        path('LoginWithOtp',LoginWithOtp.as_view(),name="LoginWithOtp"),
        path('changePassword', ChangePasswordView.as_view(), name='change-password'),
        path('logout', LogoutView.as_view(), name='knox_logout'),



]