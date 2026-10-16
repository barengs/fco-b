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

        regulator_role, created = Role.objects.get_or_create(
            name='regulator',
            defaults={'description': 'Pengawas / Inspektur Kuota Perikanan'}
        )
        if created:
            self.stdout.write(f"Created regulator role: {regulator_role}")
        else:
            self.stdout.write(f"Regulator role already exists: {regulator_role}")
        
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

        # Create default system menus and map to admin
        Menu = apps.get_model('admin_module', 'Menu')
        RoleMenu = apps.get_model('admin_module', 'RoleMenu')

        default_menus = [
            {'name': 'Ringkasan', 'url': '/admin', 'icon': 'LayoutDashboard', 'order': 1},
            {'name': 'Kapal', 'url': '/admin/ships', 'icon': 'Ship', 'order': 2},
            {'name': 'Pemilik Kapal', 'url': '/admin/owners', 'icon': 'Building2', 'order': 3},
            {'name': 'Nahkoda', 'url': '/admin/captains', 'icon': 'Anchor', 'order': 4},
            {'name': 'Laporan Tangkapan', 'url': '/admin/catches', 'icon': 'ClipboardList', 'order': 5},
            {'name': 'Spesies Ikan', 'url': '/admin/species', 'icon': 'Fish', 'order': 6},
            {'name': 'Wilayah (WPP)', 'url': '/admin/areas', 'icon': 'MapPin', 'order': 7},
            {'name': 'Kuota dan PNBP', 'url': '/admin/quota', 'icon': 'BarChart3', 'order': 8},
            {'name': 'Blockchain', 'url': '/admin/blockchain', 'icon': 'Link2', 'order': 9},
            {'name': 'Peran dan Menu', 'url': '/admin/roles', 'icon': 'KeyRound', 'order': 10},
        ]

        for m_data in default_menus:
            menu_obj, m_created = Menu.objects.get_or_create(
                url=m_data['url'],
                defaults={
                    'name': m_data['name'],
                    'icon': m_data['icon'],
                    'order': m_data['order'],
                    'is_active': True
                }
            )
            RoleMenu.objects.get_or_create(
                role=admin_role,
                menu=menu_obj,
                defaults={
                    'can_view': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                }
            )
        self.stdout.write("Initialized default system menus and role assignments")
        
        # Use direct string for style to avoid static analysis issues
        success_message = 'Successfully initialized admin system with default roles and admin user'
        self.stdout.write(getattr(self.style, 'SUCCESS')(success_message))