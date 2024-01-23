import requests

def send_sms(api_key, sender_id, mobile_number, message):
    # CDAC SMS Gateway API endpoint
    api_url = "https://msdgweb.mgov.gov.in/esms/sendsmsrequestDLT"

    # Prepare the request payload
    payload = {
        'apikey': api_key,
        'sms': message,
        'to': mobile_number,
        'senderid': sender_id,
        'route': 'P',
        'country': '91',  # Country code for India
    }

    # Make the HTTP POST request
    response = requests.post(api_url, data=payload)

    # Print the response from the API
    print(response.text)

# Replace these values with your CDAC SMS Gateway credentials
api_key = "881da998-3880-4c18-b921-0fdc9427f8d8"
sender_id = "MCGMTA"
mobile_number = "8850824601"
message = "Hello, this is a test message from CDAC SMS Gateway."

# Call the function to send SMS
send_sms(api_key, sender_id, mobile_number, message)
