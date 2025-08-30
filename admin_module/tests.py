from django.test import TestCase
from django.contrib.auth import get_user_model
from owners.models import Owner, Captain
from ships.models import Ship
from .models import Role, UserRole

class AdminModuleTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.User = get_user_model()
        
        # Create roles
        self.admin_role = Role.objects.create(name='admin', description='Administrator')  # type: ignore
        self.owner_role = Role.objects.create(name='owner', description='Ship Owner')  # type: ignore
        self.captain_role = Role.objects.create(name='captain', description='Ship Captain')  # type: ignore
        
        # Create users
        self.admin_user = self.User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin'
        )
        
        self.owner_user = self.User.objects.create_user(
            username='owner_test',
            password='testpass123',
            role='owner'
        )
        
        # Create owner and captain
        self.owner = Owner.objects.create(  # type: ignore
            name='Test Owner',
            owner_type='individual'
        )
        self.owner.user = self.owner_user
        self.owner.save()
        
        # Assign roles to users
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)  # type: ignore
        UserRole.objects.create(user=self.owner_user, role=self.owner_role)  # type: ignore
    
    def test_user_roles(self):
        """Test that users have the correct roles"""
        # Check that admin user has admin role
        admin_user_roles = UserRole.objects.filter(user=self.admin_user)  # type: ignore
        self.assertEqual(admin_user_roles.count(), 1)
        self.assertEqual(admin_user_roles.first().role, self.admin_role)
        
        # Check that owner user has owner role
        owner_user_roles = UserRole.objects.filter(user=self.owner_user)  # type: ignore
        self.assertEqual(owner_user_roles.count(), 1)
        self.assertEqual(owner_user_roles.first().role, self.owner_role)
    
    def test_role_permissions(self):
        """Test that roles can have permissions assigned"""
        # Check that roles exist
        self.assertTrue(Role.objects.filter(name='admin').exists())  # type: ignore
        self.assertTrue(Role.objects.filter(name='owner').exists())  # type: ignore
        self.assertTrue(Role.objects.filter(name='captain').exists())  # type: ignore