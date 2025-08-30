from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.apps import apps
from owners.models import CustomUser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from admin_module.models import Role, UserRole

class Command(BaseCommand):
    help = 'Initialize the system with default roles and an admin user'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get models using apps.get_model to avoid static analysis issues
        Role = apps.get_model('admin_module', 'Role')
        UserRole = apps.get_model('admin_module', 'UserRole')
        
        # Create default roles
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={'description': 'Administrator system'}
        )
        if created:
            self.stdout.write(f"Created admin role: {admin_role}")
        else:
            self.stdout.write(f"Admin role already exists: {admin_role}")
        
        owner_role, created = Role.objects.get_or_create(
            name='owner',
            defaults={'description': 'Pemilik kapal'}
        )
        if created:
            self.stdout.write(f"Created owner role: {owner_role}")
        else:
            self.stdout.write(f"Owner role already exists: {owner_role}")
        
        captain_role, created = Role.objects.get_or_create(
            name='captain',
            defaults={'description': 'Nahkoda kapal'}
        )
        if created:
            self.stdout.write(f"Created captain role: {captain_role}")
        else:
            self.stdout.write(f"Captain role already exists: {captain_role}")
        
        # Create default admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kkp.go.id',
                'role': 'admin'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write(f"Created admin user: {admin_user}")
        else:
            self.stdout.write(f"Admin user already exists: {admin_user}")
        
        # Assign admin role to admin user
        user_role, created = UserRole.objects.get_or_create(
            user=admin_user,
            role=admin_role
        )
        if created:
            self.stdout.write("Assigned admin role to admin user")
        else:
            self.stdout.write("Admin role already assigned to admin user")
        
        # Assign all permissions to admin role
        all_permissions = Permission.objects.all()
        admin_role.permissions.set(all_permissions)
        self.stdout.write("Assigned all permissions to admin role")
        
        # Use direct string for style to avoid static analysis issues
        success_message = 'Successfully initialized admin system with default roles and admin user'
        self.stdout.write(getattr(self.style, 'SUCCESS')(success_message))