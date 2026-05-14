import os
from django.conf import settings

# Path to your Firebase service account JSON file
CRED_PATH = os.path.join(settings.BASE_DIR, 'config', 'firebase_credentials.json')

_firebase_app = None

def initialize_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
        
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError:
        print("firebase_admin is not installed. Skipping Firebase init.")
        return None
    
    if os.path.exists(CRED_PATH):
        try:
            cred = credentials.Certificate(CRED_PATH)
            _firebase_app = firebase_admin.initialize_app(cred)
            return _firebase_app
        except Exception as e:
            print(f"Error initializing Firebase Admin: {e}")
            return None
    else:
        print(f"Firebase credentials not found at {CRED_PATH}. Push notifications will be skipped.")
        return None

def send_fcm_push(token, title, body, data=None):
    """
    Sends a push notification to a specific device token.
    Firebase requires all data values to be strings.
    """
    app = initialize_firebase()
    if not app or not token:
        return False
        
    try:
        from firebase_admin import messaging
    except ImportError:
        return False
    
    # FCM data values MUST all be strings
    safe_data = {k: str(v) for k, v in (data or {}).items()}
    safe_data['source'] = 'BodaKitaa'
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    channel_id='bodakitaa_channel',
                ),
            ),
            data=safe_data,
            token=token,
        )
        response = messaging.send(message)
        print(f"Successfully sent FCM message: {response}")
        return True
    except Exception as e:
        print(f"Error sending FCM message: {e}")
        return False
