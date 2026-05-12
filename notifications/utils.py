from .models import Notification
from .sms_utils import send_sms
from .fcm_utils import send_fcm_push

def notify_user(user, title, message, n_type='SYSTEM', sms=False):
    """
    Saves a notification to the DB, pushes it via FCM (Push), and optionally sends an SMS.
    (WebSocket logic removed/deferred until channels is fully configured)
    """
    # 1. Save to DB
    notif = Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notification_type=n_type
    )
    
    # 2. Push via FCM (Phone Popup)
    if hasattr(user, 'fcm_token') and user.fcm_token:
        send_fcm_push(
            token=user.fcm_token,
            title=title,
            body=message,
            data={
                "notification_id": str(notif.id),
                "type": n_type
            }
        )
    
    # 3. Optional SMS
    if sms:
        # Send SMS for critical alerts
        phone = getattr(user, 'phone_number', None) or getattr(user, 'phone', None)
        if phone:
            send_sms(phone, f"BodaKitaa Alert: {title}. {message}")
        
    return notif
