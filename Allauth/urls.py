from django.urls import path , re_path
from .views import *
from . import views
from knox.views import LogoutView


urlpatterns = [
        # path('CustomLoginAPI' , CustomLoginAPI.as_view() , name = 'CustomLoginAPI'),
        path('AddWardAPI', AddWardAPI.as_view(), name='AddWardAPI'),
        path('AddHealthPostAPI', AddHealthPostAPI.as_view(), name='AddHealthPostAPI'),
        path('GetCHV_ASHA_list/<int:section>', GetCHV_ASHA_list.as_view(), name='AddHealthPostAPI'),
        path('AddsectionAPI', AddsectionAPI.as_view(), name='AddsectionAPI'),
        path('AddDispensaryAPI', AddDispensaryAPI.as_view(), name='AddDispensaryAPI'),
        path('AddAreaAPI', AddAreaAPI.as_view(), name='AddAreaAPI'),
        # path('InsertUsers', InsertUsers.as_view(), name='knox_logout'),
        path('login', LoginView.as_view(), name='login'),
        path('GetHealthPostAreas/<str:id>' , GetHealthPostAreasAPI.as_view() , name = 'GetHealthPostAreas'),
        re_path(r'^GetWardListAPI', GetWardListAPI.as_view(), name='GetWardListAPI'),
        re_path(r'^GethealthPostNameList', GethealthPostNameListAPI.as_view(), name='GethealthPostNameList'),
        re_path(r'^GetSectionListAPI', GetSectionListAPI.as_view(), name='GetSectionListAPI'),
                
        path('healthcarecenters', HealthCareCentersList.as_view(), name='healthcare-centers-list'),
        path('healthcarecenters/<int:pk>/', HealthCareCentersDetail.as_view(), name='healthcare-centers-detail'),
        path('AddlabtestdeatilsAPI', AddlabtestdeatilsAPI.as_view(), name='healthcare-centers-detail'),
        path('usersList', UserGroupFilterView.as_view(), name='user-list'),
        path('SendOtp',views.SendOtp),
        path('CheckOtp',CheckOtp.as_view(),name="CheckOtp"),
        path('LoginWithOtp',LoginWithOtp.as_view(),name="LoginWithOtp"),
        path('changePassword', ChangePasswordView.as_view(), name='change-password'),
        path('logout', LogoutView.as_view(), name='knox_logout'),



        
        # path('InsertAmoAPI' , InsertAmoAPI.as_view() , name = 'InsertAmoAPI'),
        # path('InsertMoAPI' , InsertMoAPI.as_view() , name = 'InsertMoAPI'),

        # path('InsertHealthWorkerAPI' , InsertHealthWorkerAPI.as_view() , name = 'InsertHealthWorkerAPI'),
        # path('InsertCHV_ASHA_API' , InsertCHV_ASHA_API.as_view() , name = 'InsertHealthWorkerAPI'),
        # path('InsertPhlebotomistAPI' , InsertPhlebotomistAPI.as_view() , name = 'InsertPhlebotomistAPI'),
        # path('InsertphccAPI' , InsertphccAPI.as_view() , name = 'InsertphccAPI'),
        # path('InsertshccAPI' , InsertshccAPI.as_view() , name = 'InsertshccAPI'),
        # path('InsertthccAPI' , InsertthccAPI.as_view() , name = 'InsertthccAPI'),


        # path('InsertPrimaryHealthCareDoctorAPI' , InsertPrimaryHealthCareDoctorAPI.as_view() , name = 'InsertPrimaryHealthCareDoctorAPI'),
        # path('InsertSpecialityHealthCareDoctorAPI' , InsertSpecialityHealthCareDoctorAPI.as_view() , name = 'InsertSpecialityHealthCareDoctorAPI'),
        # path('InsertMedicalCollegeHealthCareDoctorAPI' , InsertMedicalCollegeHealthCareDoctorAPI.as_view() , name = 'InsertMedicalCollegeHealthCareDoctorAPI'),


        # path('phc/', PrimaryHealthCareCentersView.as_view(), name='phc-list'),
        # path('phc/<int:pk>/', PrimaryHealthCareCentersDetailView.as_view(), name='phc-detail'),
        # path('shc/', SpecialityHealthCareCentersView.as_view(), name='shc-list'),
        # path('shc/<int:pk>/', SpecialityHealthCareCentersDetailView.as_view(), name='shc-detail'),
        # path('mchc/', MedicalCollegeHealthCareCentersView.as_view(), name='mchc-list'),
        # path('mchc/<int:pk>/', MedicalCollegeHealthCareCentersDetailView.as_view(), name='mchc-detail'),



]