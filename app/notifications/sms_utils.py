import os
from django.conf import settings

def send_sms(phone_number, message):
    """
    Sends an SMS via Africa's Talking API.
    Gracefully skips if africastalking is not installed.
    """
    try:
        import africastalking
    except ImportError:
        print("africastalking is not installed. Skipping SMS.")
        return None

    # Load credentials from settings (from environment variables)
    username = os.getenv('AT_USERNAME', 'sandbox')
    api_key = os.getenv('AT_API_KEY', 'fake_key')
    
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
    
    try:
        # Standardize phone number format for AT
        clean_phone = str(phone_number).strip()
        if not clean_phone:
            return None
            
        if clean_phone.startswith('0'):
            clean_phone = '+255' + clean_phone[1:]
            
        response = sms.send(message, [clean_phone])
        return response
    except Exception as e:
        print(f"SMS Error: {str(e)}")
        return None
