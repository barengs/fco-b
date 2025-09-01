from django.core.management.base import BaseCommand
from admin_module.serializers import AdminRegistrationSerializer
from admin_module.models import Role

class Command(BaseCommand):
    help = 'Test admin registration with role field'
    
    def handle(self, *args, **options):
        # Check if roles exist
        roles = Role.objects.all()
        self.stdout.write(f"Available roles: {[role.name for role in roles]}")
        
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
            self.stdout.write(f"Adding role: {roles.first().name}")
        
        # Test serializer
        serializer = AdminRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        self.stdout.write(f"Serializer is valid: {is_valid}")
        
        if not is_valid:
            self.stdout.write(f"Errors: {serializer.errors}")
        else:
            self.stdout.write("Serializer validation passed")
            # Try to save
            try:
                user = serializer.save()
                self.stdout.write(f"User created: {user.username}")
                self.stdout.write(f"User role: {user.role}")
            except Exception as e:
                self.stdout.write(f"Error saving user: {e}")