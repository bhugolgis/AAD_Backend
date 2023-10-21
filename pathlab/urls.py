from django.urls import path
from .views import *

urlpatterns = [
        path('GetPhleboFamilyMembersDetails' , GetPhleboFamilyMembersDetails.as_view() , name = 'GetPhleboFamilyMembersDetails'),
        # path('PostBloodTestReport' , PostBloodTestReport.as_view() , name = 'PostBloodTestReport'),
        path('GetCitizenBasicDetailsAPI' , GetCitizenBasicDetailsAPI.as_view() , name = 'GetCitizenBasicDetailsAPI'),
        # path('PostResponseLIMSAPI/<int:id>' , PostResponseLIMSAPI.as_view() , name = 'PostResponseLIMSAPI'),
        # path('GetPatientsDetailsAPI/<int:id>' , GetPatientsDetailsAPI.as_view() , name = 'GetPatientsDetailsAPI'),
]