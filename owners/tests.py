from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Owner, Captain

CustomUser = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        # Create an owner for testing
        self.owner = Owner.objects.create(  # type: ignore
            name="Test Owner",
            owner_type="individual",
            email="test@example.com"
        )
    
    def test_create_user_with_owner(self):
        """Test creating a user with an associated owner"""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            owner=self.owner
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.owner, self.owner)
        self.assertTrue(user.check_password("testpass123"))
        
        # Test the reverse relationship
        self.assertEqual(self.owner.user, user)  # type: ignore
    
    def test_create_user_without_owner(self):
        """Test creating a user without an associated owner"""
        user = CustomUser.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )
        
        self.assertEqual(user.username, "testuser2")
        self.assertIsNone(user.owner)
    
    def test_owner_str_representation(self):
        """Test the string representation of Owner model"""
        self.assertEqual(str(self.owner), "Test Owner")

class CaptainModelTest(TestCase):
    def setUp(self):
        # Create an owner for testing
        self.owner = Owner.objects.create(  # type: ignore
            name="Test Owner",
            owner_type="individual",
            email="owner@example.com"
        )
        
        # Create a user for testing
        self.user = CustomUser.objects.create_user(
            username="testcaptain",
            email="captain@example.com",
            password="testpass123"
        )
    
    def test_create_captain(self):
        """Test creating a captain"""
        captain = Captain.objects.create(  # type: ignore
            name="Captain Test",
            license_number="CAPT123456",
            owner=self.owner,
            user=self.user,
            email="captain@example.com",
            phone="0987654321",
            years_of_experience=10
        )
        
        self.assertEqual(captain.name, "Captain Test")
        self.assertEqual(captain.license_number, "CAPT123456")
        self.assertEqual(captain.owner, self.owner)
        self.assertEqual(captain.user, self.user)
        self.assertEqual(captain.email, "captain@example.com")
        self.assertEqual(captain.phone, "0987654321")
        self.assertEqual(captain.years_of_experience, 10)
        
        # Test the reverse relationships
        self.assertIn(captain, self.owner.captains.all())  # type: ignore
        self.assertEqual(self.user.captain, captain)
    
    def test_captain_str_representation(self):
        """Test the string representation of Captain model"""
        captain = Captain.objects.create(  # type: ignore
            name="Captain Test",
            license_number="CAPT123456",
            owner=self.owner
        )
        
        self.assertEqual(str(captain), "Captain Test")