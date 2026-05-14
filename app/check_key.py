import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bodaboda_be.settings')
django.setup()

print(f"SECRET_KEY starts with: {settings.SECRET_KEY[:20]}...")
print(f"SECRET_KEY length: {len(settings.SECRET_KEY)}")
