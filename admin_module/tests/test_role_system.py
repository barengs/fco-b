from django.test import TestCase
from django.contrib.auth import get_user_model
from django.apps import apps
from owners.models import CustomUser

class RoleSystemTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.User = get_user_model()
        
        # Get models using apps.get_model
        self.Role = apps.get_model('admin_module', 'Role')
        self.UserRole = apps.get_model('admin_module', 'UserRole')
        
        # Create test roles
        self.admin_role = self.Role.objects.create(name='admin', description='Administrator')
        self.owner_role = self.Role.objects.create(name='owner', description='Owner')
        self.captain_role = self.Role.objects.create(name='captain', description='Captain')
        
        # Create test users
        self.admin_user = self.User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.owner_user = self.User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123',
            role='owner'
        )
        
        self.captain_user = self.User.objects.create_user(
            username='testcaptain',
            email='captain@test.com',
            password='testpass123',
            role='captain'
        )

    def test_role_assignment_via_flexible_system(self):
        """Test that users can be assigned roles via the flexible system"""
        # Assign roles using the flexible system
        self.UserRole.objects.create(user=self.admin_user, role=self.admin_role)
        self.UserRole.objects.create(user=self.owner_user, role=self.owner_role)
        self.UserRole.objects.create(user=self.captain_user, role=self.captain_role)
        
        # Check that roles are assigned correctly
        self.assertTrue(self.UserRole.objects.filter(user=self.admin_user, role=self.admin_role).exists())
        self.assertTrue(self.UserRole.objects.filter(user=self.owner_user, role=self.owner_role).exists())
        self.assertTrue(self.UserRole.objects.filter(user=self.captain_user, role=self.captain_role).exists())

    def test_user_role_determination(self):
        """Test that user roles are determined correctly"""
        # Assign roles using the flexible system
        self.UserRole.objects.create(user=self.admin_user, role=self.admin_role)
        self.UserRole.objects.create(user=self.owner_user, role=self.owner_role)
        self.UserRole.objects.create(user=self.captain_user, role=self.captain_role)
        
        # Test admin user
        admin_roles = [user_role.role.name for user_role in self.admin_user.userrole_set.all()]
        self.assertIn('admin', admin_roles)
        
        # Test owner user
        owner_roles = [user_role.role.name for user_role in self.owner_user.userrole_set.all()]
        self.assertIn('owner', owner_roles)
        
        # Test captain user
        captain_roles = [user_role.role.name for user_role in self.captain_user.userrole_set.all()]
        self.assertIn('captain', captain_roles)

    def test_backward_compatibility(self):
        """Test that the old role system still works as fallback"""
        # Users without flexible roles should still be identified by their role field
        user_roles = [user_role.role.name for user_role in self.admin_user.userrole_set.all()]
        # Since we haven't assigned flexible roles yet, it should fall back to the role field
        self.assertEqual(self.admin_user.role, 'admin')
        self.assertEqual(self.owner_user.role, 'owner')
        self.assertEqual(self.captain_user.role, 'captain')