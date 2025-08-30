from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from admin_module.models import AdminProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Test admin profile creation'
    
    def handle(self, *args, **options):
        # Create a test user with admin role
        try:
            user, created = User.objects.get_or_create(
                username='testadmin',
                defaults={
                    'email': 'testadmin@example.com',
                    'role': 'admin'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User already exists: {user.username}'))
            
            # Create or get admin profile
            admin_profile, created = AdminProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': 'Test Administrator',
                    'email': 'testadmin@example.com',
                    'phone': '1234567890',
                    'department': 'IT',
                    'position': 'System Administrator'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created admin profile: {admin_profile}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Admin profile already exists: {admin_profile}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))