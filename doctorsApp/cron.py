import os
import requests
from database.models import *
import re
import logging
from datetime import datetime
import json
from ArogyaAplyaDari.settings import MEDIA_ROOT
from pathlib import Path
from django.core.files import File
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

def GetBookingVisitID():
    transactionId = PatientsPathlabrecords.objects.filter(transactionid__isnull=False, bookingVisitID__isnull=True,
                                                          patientID__isnull=True)

    for id in transactionId:
        url = 'https://android.techjivaaindia.in/KRASNA/GetBookingVisitID'

        payload = json.dumps({
            "BookingId": id.transactionid
        })

        headers = {
            'accept': '*/*',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response_data = json.loads(response.content)

            # Check if keys exist in the response_data dictionary
            if "boobkingVisitID" in response_data and response_data["boobkingVisitID"]:
                booking_visit_id = response_data["boobkingVisitID"]

                # Validate if the values are "NAN" (as strings)
                patient_id = booking_visit_id.get("patientID")
                booking_visit_id_value = booking_visit_id.get("BookingVisitID")

                if patient_id and booking_visit_id_value and patient_id.lower() != "nan" and booking_visit_id_value.lower() != "nan":
                    id.patientID = patient_id
                    id.bookingVisitID = booking_visit_id_value
                    id.save()
                else:
                    # Handle the case where values are "NAN"
                    pass
            else:
                # Handle the case where "boobkingVisitID" is not present
                pass
        else:
            # Handle other HTTP status codes
            pass


 
def AddTestReport():
    # logger.warning("add test report running")

    # print("add test report running")
    #Check for FamilyMember LabTest Added
    checkLabTestAdded = PatientsPathlabrecords.objects.filter(patientFamilyMember__isLabTestAdded = True,
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
        jsonheaders = {
            'Content-Type': 'application/json',
        }
        # Send a POST request to the URL to get the PDF file
        response = requests.post(url1, headers=headers, data=payload)
        responseJson = requests.post(url2, headers=jsonheaders, data=post_params)
        # logger.warning(response.content , "1st logger")
        if response.status_code == 200 and responseJson.status_code == 200:
            # Specify the folder where you want to save the PDF file temporarily
            temp_folder = os.path.join(MEDIA_ROOT, 'patientPathLabResults')

            # Extract the file name from the URL
            file_name =str(labTest.patientFamilyMember.name.replace(" ",""))+str(labTest.patientID) + '.pdf'

            # Save the PDF file temporarily
            temp_file_path = os.path.join(temp_folder, file_name)
            
            #logger.warning(temp_file_path)
            pdfurl  = getPdfUrl(response.text)
            if pdfurl:
                pdfResponse = requests.get(pdfurl)
                with open(temp_file_path, 'wb') as temp_pdf_file:
                    temp_pdf_file.write(pdfResponse.content)
                    
                path = Path(temp_file_path)
                parts = path.parts[-2:]
                p2 = Path(*parts)
                pdf_file_instance = PatientPathLabReports(patientPathLab_id =labTest.id )
                pdf_file_instance.pdfResult.save(file_name, File(open(temp_file_path, 'rb')))
                pdf_file_instance.save()
                updateLabTest = familyMembers.objects.filter(id=labTest.patientFamilyMember_id).update(isLabTestReportGenerated=True , isSampleCollected = True)
            else:
                pass

        else:
            pass


def GetHomePaitentReport():
    Paitents = PatientsPathlabrecords.objects.filter(patientFamilyMember__isLabTestAdded = True,
                                                      patientFamilyMember__isSampleCollected =True,
                                                      patientFamilyMember__isLabTestReportGenerated = False,
                                                      bookingVisitID__isnull= False, puid__isnull = False ,  
                                                      patientID__isnull = False , transactionid__isnull = False
                                                      )
    

    for Paitent in Paitents:
        # if checkLabTestAdded.exists():
        url ="https://kdl.techjivaaindia.in/services/LISMobileAPPService.asmx/Get_LIS_PatientReportURL"

        authKey = 'E0DE107A7CA04A6CA7FBB6DAE89B4F3A'
        patientID = Paitent.patientID
        lisVisitID = Paitent.bookingVisitID
        puid = Paitent.puid

        post_params = {
            'authKey': authKey,
            'puid': puid,
            'lisVisitID': lisVisitID,
            'patientID': patientID,
        }
        headers =  {
            'Content-Type': 'application/json',
        }

        response = requests.post(url , headers=headers, data=post_params)
        logger.warning(response)
        if response.status_code == 200:
            response_data = json.loads(response.content)
            if response.status_code == 200 and response_data.get(("LISResult") == "True"):
                # Specify the folder where you want to save the PDF file temporarily
                temp_folder = os.path.join(MEDIA_ROOT, 'patientPathLabResults')

                # Extract the file name from the URL
                file_name =str(Paitent.patientFamilyMember.name.replace(" ",""))+str(Paitent.patientID) + '.pdf'

                # Save the PDF file temporarily
                temp_file_path = os.path.join(temp_folder, file_name)
                
                #logger.warning(temp_file_path)
                pdfurl  = getPdfUrl(response.text)
                if pdfurl:
                    pdfResponse = requests.get(pdfurl)
                    with open(temp_file_path, 'wb') as temp_pdf_file:
                        temp_pdf_file.write(pdfResponse.content)
                        
                    # logger.warning(temp_file_path , "file path")
                    path = Path(temp_file_path)
                    parts = path.parts[-2:]
                    p2 = Path(*parts)
                    pdf_file_instance = PatientPathLabReports(patientPathLab_id =Paitent.id )
                    pdf_file_instance.pdfResult.save(file_name, File(open(temp_file_path, 'rb')))
                    pdf_file_instance.save()
                    updateLabTest = familyMembers.objects.filter(id=Paitent.patientFamilyMember_id).update(isLabTestReportGenerated=True , isSampleCollected = True)
                else:
                    pass
            else:
                pass