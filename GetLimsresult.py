import requests
import json

url = "http://ilis.krsnaadiagnostics.com/api/KDL_LIS_APP_API/Patient_Results_Data"

payload = json.dumps({
  "authKey": "05436EFE3826447DBE720525F78A9EEDBMC",
  "BookingVisitID": "21772025",
  "PUID": "BMCM231100682727",
  "patientID": "e1af10a2-773d-4588-93ed-c36a5bc71059"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.content)