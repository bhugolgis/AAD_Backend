from django.urls import path
from .views import *

urlpatterns = [
        path('PostSurveyForm' , PostSurveyForm.as_view() , name = 'PostSurveyForm'),
        path('GetFamilyHeadList' , GetFamilyHeadList.as_view() , name = 'GetFamilyHeadList'),
        path('GetPartiallyInsertedRecord' , GetPartiallyInsertedRecord.as_view() , name = 'GetpartiallyUpdateRecord'),
        path('PostFamilyDetails' , PostFamilyDetails.as_view() , name = 'PostSurveyForm'),
        path('GetFamilyMembersDetails' , GetFamilyMembersDetails.as_view() , name = 'GetFamilyMembersDetails'),
        path('UpdateFamilyDetails/<int:id>' , UpdateFamilyDetails.as_view() , name = 'UpdateFamilyDetails'),
        path('GetSurveyorDashboard' , GetSurveyorCountDashboard.as_view() , name = 'GetSurveyorCountDashboard'),
        path('GetCitizenList/<str:choice>' , GetCitizenList.as_view() , name = 'GetTotalCitizenList'),
        path('GetFamilyList/<str:choice>' , GetFamilyList.as_view() , name = 'GetFamilyList'),
        path('GetBloodCollectionDetail' , GetBloodCollectionDetail.as_view() , name = 'GetBloodCollectionDetail'),


        path('verifyMobileNumber/<int:mobileNo>' , verifyMobileNumber.as_view() , name = 'verifyMobileNumber'),
        path('veirfyaadharCard/<int:aadharCard>' , veirfyaadharCard.as_view() , name = 'aadharCard'),
        path('verifyabhaId/<str:abhaId>' , verifyabhaId.as_view() , name = 'aadharCard'),
        path('DumpExcelInsertxlsx' , DumpExcelInsertxlsx.as_view() , name = 'DumpExcelInsertxlsx'),



 
 


]