import os
import requests
from database.models import *

def AddTestReport():
    
    #Check for FamilyMember LabTest Added
    checkLabTestAdded = PatientPathlab.objects.filter(patientFamilyMember__isLabTestAdded = True,
                                                      patientFamilyMember__isSampleCollected =True,
                                                      patientFamilyMember__isLabTestReportGenerated = False)

    for labTest in checkLabTestAdded:
        # if checkLabTestAdded.exists():
        url1 ="http://ilis.krsnaadiagnostics.com/services/KDL_LIS_Report_APPService.asmx"
        url2 = "http://ilis.krsnaadiagnostics.com/api/KDL_LIS_APP_API/Patient_Results_Data"
        post_params = {
            'authKey': "auth_key",
            'PUID': labTest.puid,
            'BookingVisitId': labTest.bookingVisitID,
            'patientId': labTest.patientID,
        }

        # Send a POST request to the URL to get the PDF file
        response = requests.post(url1, data=post_params)
        responseJson = requests.post(url2, data=post_params)
            
        if response.status_code == 200 and responseJson.status_code == 200:
            # Specify the folder where you want to save the PDF file temporarily
            temp_folder = os.path.join('media', 'patientPathLabResults')
            os.makedirs(temp_folder, exist_ok=True)

            # Extract the file name from the URL
            file_name = str(labTest.patientFamilyMember.name)+str(labTest.patientFamilyMember.patientID)

            # Save the PDF file temporarily
            temp_file_path = os.path.join(temp_folder, file_name)
            with open(temp_file_path, 'wb') as temp_pdf_file:
                temp_pdf_file.write(response.content)

            # Create a PatientPathLabReports instance and save the file in the model's FileField
            pdf_file_instance = PatientPathLabReports(patientPathLab_id =labTest.id ,pdfResult=temp_file_path,jsonResult=responseJson)
            pdf_file_instance.save()

            # Clean up: remove the temporary file
            os.remove(temp_file_path)
         
        # pass
    else:
        pass
        # print("Test Not Added or Test Sample not Added")
    # print("Cron Running")