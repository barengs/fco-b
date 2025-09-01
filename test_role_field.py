import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from admin_module.serializers import AdminRegistrationSerializer
from admin_module.models import Role

def test_serializer_with_role():
    # Check if roles exist
    roles = Role.objects.all()
    print(f"Available roles: {[role.name for role in roles]}")
    
    # Test data
    data = {
        'username': 'testadminrole',
        'password': 'testpassword123',
        'email': 'testadminrole@example.com',
        'full_name': 'Test Admin with Role',
        'phone': '1234567890',
        'department': 'IT',
        'position': 'Developer',
    }
    
    # If we have roles, add one to the test data
    if roles.exists():
        data['role'] = roles.first().id
        print(f"Adding role: {roles.first().name}")
    
    # Test serializer
    serializer = AdminRegistrationSerializer(data=data)
    is_valid = serializer.is_valid()
    print(f"Serializer is valid: {is_valid}")
    
    if not is_valid:
        print(f"Errors: {serializer.errors}")
    else:
        print("Serializer validation passed")

if __name__ == "__main__":
    test_serializer_with_role()