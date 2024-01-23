from django.urls import path
from doctorsApp.views import *
from . import views
urlpatterns = [
    path('labtestsuggested/', LabTestSuggestedCreateView.as_view(), name='lab-test-suggested-create'),
    path('listpatientspathlab/', ListPatientsPathlabView.as_view(), name='list-patients-pathlab'),
    path('BookPatientAPI', LIMSBookPatientAPI.as_view(), name='BookPatientAPI'),

    path('HomeBookPatientAPI', LIMSHomeBookPatientAPI.as_view(), name='LIMSHomeBookPatientAPI'),
    path('LIMSPatientRegisterAPI', LIMSPatientRegisterAPI.as_view(), name='LIMSPatientRegisterAPI'),
    # path('LIMSPatientRegisterAPI', LIMSPatientRegisterAPI.as_view(), name='LIMSPatientRegisterAPI'),

    path('ViewFamilysDetails/<int:id>/', ViewFamilysDetails.as_view(), name='ViewFamilysDetails'),
    path('GetAllFamilysDetails/', GetAllFamilysDetails.as_view(), name='ViewFamilysDetails'),
    # path('FamilyHeadList/', FamilyHeadList.as_view(), name='FamilyHeadList'),
    # path('ViewFamilyDetails/<str:pk>/', ViewFamilyDetails.as_view(), name='ViewFamilyDetails'),
    # path('FamilyHeadList',views.FamilyHeadList),

    # path('ViewFamilyDetails/<str:pk>/',views.ViewFamilyDetails),
    # path('ViewPatientsLabTestViewDetails/<str:pk>/',views.ViewPatientsLabTestViewDetails),
    path('medicalOfficerAdviceView/<int:patients_id>/', views.medicalOfficerAdviceView, name='medicalOfficerAdviceView'),
    path('medicalOfficerReferalAdviceView/<int:patients_id>/', views.medicalOfficerReferalAdviceView, name='medicalOfficerReferalAdviceView'),
    path('ViewFamilyMemberView/<str:pk>/',views.ViewFamilyMemberView),
    path('ViewMedicalOfficerConsaltancyView/<int:patients_id>/', views.ViewMedicalOfficerConsaltancyView, name='ViewMedicalOfficerConsaltancyView'),
    path('ViewPrimaryConsultancyView/<int:patients_id>/', views.ViewPrimaryConsultancyView, name='ViewPrimaryConsultancyView'),
    path('ViewSecondaryConsultancyView/<int:patients_id>/', views.ViewSecondaryConsultancyView, name='ViewSecondaryConsultancyView'),
    path('ViewTertiaryConsultancyView/<int:patients_id>/', views.ViewTertiaryConsultancyView, name='ViewTertiaryConsultancyView'),

    path('PatientsForPrimaryDoctorList', views.PatientsForPrimaryDoctorList, name='PatientsForPrimaryDoctorList'),
    path('PatientsForSecondaryDoctorList', views.PatientsForSecondaryDoctorList, name='PatientsForSecondaryDoctorList'),
    path('PatientsForTertairyDoctorList', views.PatientsForTertairyDoctorList, name='PatientsForTertairyDoctorList'),

    path('labTestsList/', labTestsList, name='labTestsList'),
    
    
    path('MoDashboard', MoDashboard, name='MoDashboard'),


    


    # Add other URLs as needed
]