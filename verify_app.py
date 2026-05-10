import os
import django
from django.test import RequestFactory
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prince_portfolio.settings')
django.setup()

from portfolio.views import home

def verify():
    factory = RequestFactory()
    request = factory.get('/')
    response = home(request)
    
    if response.status_code == 200:
        print("Homepage loaded successfully (Status 200)")
        if b"Prince Raj Kiran" in response.content:
            print("Content verification passed: Name found")
        else:
            print("Content verification warning: Name not found")
    else:
        print(f"Homepage failed to load. Status: {response.status_code}")

if __name__ == "__main__":
    verify()
