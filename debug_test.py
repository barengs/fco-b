#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

print("Django setup completed")

from django.contrib.auth import get_user_model
from owners.models import Owner, Captain
from ships.models import Ship

print("Models imported successfully")

# Test if we can access the objects manager
print("Owner has objects:", hasattr(Owner, 'objects'))
print("Captain has objects:", hasattr(Captain, 'objects'))
print("Ship has objects:", hasattr(Ship, 'objects'))

print("Test completed")