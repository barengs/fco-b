from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.apps import apps
from owners.models import CustomUser
from getpass import getpass
import sys

class Command(BaseCommand):
    help = 'Create a super admin user with full privileges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the super admin',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the super admin',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the super admin',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Create super admin interactively',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get models using apps.get_model
        Role = apps.get_model('admin_module', 'Role')
        UserRole = apps.get_model('admin_module', 'UserRole')
        AdminProfile = apps.get_model('admin_module', 'AdminProfile')
        
        # Interactive mode
        if options['interactive'] or not all([options['username'], options['email'], options['password']]):
            self.stdout.write("=== Membuat Super Admin ===")
            username = input("Username: ") if not options['username'] else options['username']
            email = input("Email: ") if not options['email'] else options['email']
            
            if not options['password']:
                password = getpass("Password: ")
                password_confirm = getpass("Konfirmasi Password: ")
                if password != password_confirm:
                    self.stdout.write(self.style.ERROR("Password tidak cocok!"))
                    return
            else:
                password = options['password']
        else:
            username = options['username']
            email = options['email']
            password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f"User dengan username '{username}' sudah ada!"))
            return

        # Create super admin user
        try:
            super_admin = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin'
            )
            super_admin.is_superuser = True
            super_admin.is_staff = True
            super_admin.is_active = True
            super_admin.save()
            
            self.stdout.write(self.style.SUCCESS(f"✓ Super admin user '{username}' berhasil dibuat"))

            # Create or get admin role
            admin_role, created = Role.objects.get_or_create(
                name='admin',
                defaults={'description': 'Super Administrator dengan akses penuh'}
            )
            
            if created:
                # Assign all permissions to admin role
                all_permissions = Permission.objects.all()
                admin_role.permissions.set(all_permissions)
                self.stdout.write(self.style.SUCCESS("✓ Admin role dibuat dengan semua permissions"))
            else:
                self.stdout.write("✓ Admin role sudah ada")

            # Assign admin role to user
            user_role, created = UserRole.objects.get_or_create(
                user=super_admin,
                role=admin_role
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS("✓ Admin role berhasil diberikan ke user"))
            else:
                self.stdout.write("✓ User sudah memiliki admin role")

            # Create admin profile
            admin_profile, created = AdminProfile.objects.get_or_create(
                user=super_admin,
                defaults={
                    'full_name': username.title(),
                    'email': email,
                    'department': 'IT',
                    'position': 'Super Administrator',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS("✓ Admin profile berhasil dibuat"))
            else:
                self.stdout.write("✓ Admin profile sudah ada")

            # Display summary
            self.stdout.write("\n" + "="*50)
            self.stdout.write(self.style.SUCCESS("SUPER ADMIN BERHASIL DIBUAT!"))
            self.stdout.write("="*50)
            self.stdout.write(f"Username: {super_admin.username}")
            self.stdout.write(f"Email: {super_admin.email}")
            self.stdout.write(f"Role: {super_admin.role}")
            self.stdout.write(f"Is Superuser: {super_admin.is_superuser}")
            self.stdout.write(f"Is Staff: {super_admin.is_staff}")
            self.stdout.write(f"Is Active: {super_admin.is_active}")
            self.stdout.write("="*50)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error membuat super admin: {str(e)}"))
            return

        self.stdout.write(self.style.SUCCESS("\nSuper admin siap digunakan untuk login ke sistem!"))