import os
import requests
from database.models import *
import re
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

def getPdfUrl(response_string):
    
    report_url =""

    # Use regular expression to extract the ReportURL
    match = re.search(r'ReportURL":"([^"]+)"', response_string)

    if match:
        report_url = match.group(1)
        return report_url
    else:
        print("ReportURL not found in the response.")
        
        
        
        
def AddTestReport():
    logger.warning("add test report running")

    print("add test report running")
    #Check for FamilyMember LabTest Added
    checkLabTestAdded = PatientPathlab.objects.filter(patientFamilyMember__isLabTestAdded = True,
                                                      patientFamilyMember__isSampleCollected =True,
                                                      patientFamilyMember__isLabTestReportGenerated = False)

    for labTest in checkLabTestAdded:
        # if checkLabTestAdded.exists():
        url1 ="http://ilis.krsnaadiagnostics.com/services/KDL_LIS_Report_APPService.asmx"
        url2 = "http://ilis.krsnaadiagnostics.com/api/KDL_LIS_APP_API/Patient_Results_Data"
        
        auth_key = "05436EFE3826447DBE720525F78A9EEDBMC"
        puid = labTest.puid
        booking_visit_id = labTest.bookingVisitID
        patient_id = labTest.patientID

        payload = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <Get_LIS_PatientReportURL xmlns="http://tempuri.org/">
            <authKey>{auth_key}</authKey>
            <PUID>{puid}</PUID>
            <BookingVisitID>{booking_visit_id}</BookingVisitID>
            <patientID>{patient_id}</patientID>
            </Get_LIS_PatientReportURL>
        </soap:Body>
        </soap:Envelope>
        """

        headers = {
            'Content-Type': 'text/xml',
            'SOAPAction': 'http://tempuri.org/Get_LIS_PatientReportURL'
        }
        post_params = {
            'authKey': auth_key,
            'PUID': puid,
            'BookingVisitId': booking_visit_id,
            'patientId': patient_id,
        }

        # Send a POST request to the URL to get the PDF file
        response = requests.post(url1, headers=headers, data=payload)
        responseJson = requests.post(url2, data=post_params)
            
        if response.status_code == 200 and responseJson.status_code == 200:
            # Specify the folder where you want to save the PDF file temporarily
            temp_folder = os.path.join('media', 'patientPathLabResults')
            os.makedirs(temp_folder, exist_ok=True)

            # Extract the file name from the URL
            file_name = str(labTest.patientFamilyMember.name)+str(labTest.patientFamilyMember.patientID)

            # Save the PDF file temporarily
            temp_file_path = os.path.join(temp_folder, file_name)
            pdfurl  = getPdfUrl(response.text)
            pdfResponse = requests.get(pdfurl)
            with open(temp_file_path, 'wb') as temp_pdf_file:
                temp_pdf_file.write(pdfResponse.content)

            # Create a PatientPathLabReports instance and save the file in the model's FileField
            pdf_file_instance = PatientPathLabReports(patientPathLab_id =labTest.id ,pdfResult=temp_file_path,jsonResult=responseJson)
            pdf_file_instance.save()

            # Clean up: remove the temporary file
            # os.remove(temp_file_path)
         
        # pass
    else:
        pass
        # print("Test Not Added or Test Sample not Added")
    # print("Cron Running")