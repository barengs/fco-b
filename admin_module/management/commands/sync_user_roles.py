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

        # Merge and clean up duplicate capitalized roles (e.g. 'Admin' -> 'admin', 'Regulator' -> 'regulator')
        canonical_map = {
            'Admin': admin_role,
            'Regulator': regulator_role,
            'SuperAdmin': superadmin_role,
            'Superadmin': superadmin_role,
            'Owner': owner_role,
            'Captain': captain_role,
        }
        for dup_name, target_role in canonical_map.items():
            dup_roles = Role.objects.filter(name=dup_name)
            for dup_role in dup_roles:
                for ur in dup_role.userrole_set.all():
                    if not UserRole.objects.filter(user=ur.user, role=target_role).exists():
                        UserRole.objects.create(user=ur.user, role=target_role)
                    ur.delete()
                self.stdout.write(f"Merged and removed duplicate role '{dup_name}' into '{target_role.name}'")
                dup_role.delete()
        
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