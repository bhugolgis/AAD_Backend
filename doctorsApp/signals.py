from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from database.models import *
import hashlib
import requests 
import urllib.parse

  

@receiver(post_save , sender=PatientsPathlabrecords)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    if created:
        if instance.puid != None and instance.patientID == None and instance.bookingVisitID == None:
            family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)        
            family.generalStatus = 'Patient registerd at LIMS' 
            family.save()


@receiver(post_save , sender=PatientsPathlabrecords)  
def update_isLabTestAdded_check(sender, instance , created, **kwargs):
    if created:
        if instance.puid != None and instance.bookingVisitID != None and instance.patientID != None:
            family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
            family.isLabTestAdded = True 
            family.isSampleCollected = True 
            family.generalStatus = 'Tests Assigned' 
            family.save()
    else:
        if instance.puid != None and instance.transactionid != None:
            family = familyMembers.objects.get(pk=instance.patientFamilyMember.id)
            family.isLabTestAdded = True 
            family.isSampleCollected = True 
            family.generalStatus = 'Tests Assigned' 
            family.save()


def ConvertMsg(msg):
    message = msg
    finalmessage = ""
    for i in range(len(message)):
        ch = message[i]
        j = ord(ch)
        sss = f"&#{j};"
        finalmessage += sss
 
    return finalmessage
 
def hash_generator(user_name, sender_id, content, secure_key):
    final_string = f"{user_name.strip()}{sender_id.strip()}{content.strip()}{secure_key.strip()}"
    hash_gen = hashlib.sha512(final_string.encode('utf-8')).digest()
    hex_representation = ''.join(format(byte, '02x') for byte in hash_gen)
    return hex_representation


@receiver(post_save , sender=familyMembers) 
def send_msg(sender, instance , created, **kwargs):
    if instance.generalStatus == "Tests Assigned": 
        user_name = "MCGMSEVA-HEALTH"
        sender_id = "MCGMTA"
        message = '''मुख्यमंत्री आरोग्य आपल्या दारी" योजनेत सहभागासाठी धन्यवाद. पुढील तपासणी करीता जवळच्या  बृमुमपा / एचबीटी दवाखान्याला भेट द्या.'''
        content = ConvertMsg(message)
        secure_key = "881da998-3880-4c18-b921-0fdc9427f8d8"
        result = hash_generator(user_name, sender_id, content, secure_key)

        password = 'MCGMHEALTH@SMS123'
        mobile_number = str(instance.familyHead.mobileNo)
        
        url = "https://msdgweb.mgov.gov.in/esms/sendsmsrequestDLT"
        
        payload = 'key='+result+'&username=MCGMSEVA-HEALTH&password=MCGMHEALTH@SMS123'+'&smsservicetype=unicodemsg&content='+urllib.parse.quote(content)+'&mobileno='+mobile_number+'&senderid=MCGMTA&templateid=1007494286496479236'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.request("POST", url, headers=headers, data=payload)



@receiver(post_save , sender=familyMembers) 
def send_msgNew(sender, instance , created, **kwargs):
    if instance.generalStatus == "Survey Completed": 
        user_name = "MCGMSEVA-HEALTH"
        sender_id = "MCGMTA"
        message = '''मुख्यमंत्री आरोग्य आपल्या दारी" योजनेत सहभागासाठी धन्यवाद. पुढील तपासणी करीता जवळच्या  बृमुमपा / एचबीटी दवाखान्याला भेट द्या.'''
        content = ConvertMsg(message)
        secure_key = "881da998-3880-4c18-b921-0fdc9427f8d8"
        result = hash_generator(user_name, sender_id, content, secure_key)

        password = 'MCGMHEALTH@SMS123'
        mobile_number = str(instance.familyHead.mobileNo)
        
        url = "https://msdgweb.mgov.gov.in/esms/sendsmsrequestDLT"
        
        payload = 'key='+result+'&username=MCGMSEVA-HEALTH&password=MCGMHEALTH@SMS123'+'&smsservicetype=unicodemsg&content='+urllib.parse.quote(content)+'&mobileno='+mobile_number+'&senderid=MCGMTA&templateid=1007494286496479236'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.request("POST", url, headers=headers, data=payload)





@receiver(post_save , sender=PatientPathLabReports)  
def update_general_status(sender, instance , created, **kwargs):
    if created:
        family = familyMembers.objects.get(pk=instance.patientPathLab.patientFamilyMember.id)
        family.generalStatus = 'Report received' 
        family.save()
        
