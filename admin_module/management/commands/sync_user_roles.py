from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from owners.models import CustomUser

class Command(BaseCommand):
    help = 'Synchronize existing users with the flexible role system'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get models using apps.get_model to avoid static analysis issues
        Role = apps.get_model('admin_module', 'Role')
        UserRole = apps.get_model('admin_module', 'UserRole')
        
        # Get all users
        users = User.objects.all()
        self.stdout.write(f"Found {users.count()} users to synchronize")
        
        # Ensure all default roles exist
        superadmin_role, _ = Role.objects.get_or_create(
            name='superadmin',
            defaults={'description': 'Super Administrator dengan hak akses penuh tata kelola sistem'}
        )

        admin_role, _ = Role.objects.get_or_create(
            name='admin',
            defaults={'description': 'Administrator sistem pelayanan operasional'}
        )

        regulator_role, _ = Role.objects.get_or_create(
            name='regulator',
            defaults={'description': 'Pengawas / Inspektur Kuota Perikanan'}
        )
        
        owner_role, _ = Role.objects.get_or_create(
            name='owner',
            defaults={'description': 'Pemilik kapal'}
        )
        
        captain_role, _ = Role.objects.get_or_create(
            name='captain',
            defaults={'description': 'Nahkoda kapal'}
        )
        
        # Synchronize each user
        for user in users:
            # Skip if user already has roles assigned in the flexible system
            if UserRole.objects.filter(user=user).exists():
                self.stdout.write(f"User {user.username} already has roles assigned, skipping...")
                continue
                
            # Assign role based on user's flags and role field
            if user.is_superuser or user.role == 'superadmin':
                user_role, created = UserRole.objects.get_or_create(user=user, role=superadmin_role)
                if created:
                    self.stdout.write(f"Assigned superadmin role to user {user.username}")

            elif user.role == 'admin':
                user_role, created = UserRole.objects.get_or_create(user=user, role=admin_role)
                if created:
                    self.stdout.write(f"Assigned admin role to user {user.username}")

            elif user.role == 'regulator':
                user_role, created = UserRole.objects.get_or_create(user=user, role=regulator_role)
                if created:
                    self.stdout.write(f"Assigned regulator role to user {user.username}")
                    
            elif user.role == 'owner':
                user_role, created = UserRole.objects.get_or_create(user=user, role=owner_role)
                if created:
                    self.stdout.write(f"Assigned owner role to user {user.username}")
                    
            elif user.role == 'captain':
                user_role, created = UserRole.objects.get_or_create(user=user, role=captain_role)
                if created:
                    self.stdout.write(f"Assigned captain role to user {user.username}")
            
            else:
                user_role, created = UserRole.objects.get_or_create(user=user, role=owner_role)
                if created:
                    self.stdout.write(f"Assigned default owner role to user {user.username}")
        
        self.stdout.write(
            'Successfully synchronized all users with flexible role system'
        )