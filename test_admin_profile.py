import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from admin_module.models import AdminProfile

User = get_user_model()

# Create a test user with admin role
try:
    user = User.objects.create_user(
        username='testadmin',
        email='testadmin@example.com',
        password='testpass123',
        role='admin'
    )
    print(f"Created user: {user.username}")
    
    # Create admin profile
    admin_profile = AdminProfile.objects.create(
        user=user,
        full_name='Test Administrator',
        email='testadmin@example.com',
        phone='1234567890',
        department='IT',
        position='System Administrator'
    )
    print(f"Created admin profile: {admin_profile}")
    
except Exception as e:
    print(f"Error: {e}")