#!/usr/bin/env python
"""
Script to create a superuser for the eSchool application.
This script is idempotent - it won't fail if the user already exists.
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

# Superuser credentials
SUPERUSER_EMAIL = "MichelAdmin@eschool.com"
SUPERUSER_PASSWORD = "Welcome@2025"
SUPERUSER_FIRST_NAME = "Michel"
SUPERUSER_LAST_NAME = "Admin"

def create_superuser():
    """Create superuser if it doesn't exist."""
    try:
        if User.objects.filter(email=SUPERUSER_EMAIL).exists():
            print(f"✓ Superuser '{SUPERUSER_EMAIL}' already exists.")
            return
        
        user = User.objects.create_superuser(
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
            first_name=SUPERUSER_FIRST_NAME,
            last_name=SUPERUSER_LAST_NAME,
            role='SUPER_ADMIN'
        )
        print(f"✓ Superuser '{SUPERUSER_EMAIL}' created successfully!")
        print(f"  Email: {SUPERUSER_EMAIL}")
        print(f"  Password: {SUPERUSER_PASSWORD}")
        print(f"  Role: SUPER_ADMIN")
        
    except IntegrityError as e:
        print(f"✗ Error creating superuser: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == '__main__':
    print("Creating superuser for eSchool...")
    create_superuser()
    print("Done!")
