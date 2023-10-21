from django.urls import path
from doctorsApp.views import *

urlpatterns = [
    path('labtestsuggested/', LabTestSuggestedCreateView.as_view(), name='lab-test-suggested-create'),
    path('listpatientspathlab/', ListPatientsPathlabView.as_view(), name='list-patients-pathlab'),

    # Add other URLs as needed
]