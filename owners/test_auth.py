"""
Test script for the custom authentication backend
"""
import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

print("Django setup completed")

from django.contrib.auth import get_user_model
from owners.authentication import ShipNumberOrUsernameBackend
from owners.models import Owner, Captain
from ships.models import Ship

print("Imports successful")

User = get_user_model()

def test_authentication():
    print("Testing custom authentication backend...")
    
    try:
        # Create test data
        # Type ignore comments to suppress type checker warnings
        owner = Owner.objects.create(  # type: ignore
            name="Test Owner",
            owner_type="individual"
        )
        print(f"Created owner: {owner}")
        
        user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        print(f"Created user: {user}")
        owner.user = user
        owner.save()
        
        # Create captain
        captain = Captain.objects.create(  # type: ignore
            name="Test Captain",
            license_number="LIC001",
            owner=owner
        )
        print(f"Created captain: {captain}")
        
        captain_user = User.objects.create_user(
            username="captainuser",
            password="captainpass123"
        )
        print(f"Created captain user: {captain_user}")
        captain.user = captain_user
        captain.save()
        
        ship = Ship.objects.create(  # type: ignore
            name="Test Ship",
            registration_number="SHIP001",
            owner=owner,
            captain=captain
        )
        print(f"Created ship: {ship}")
        
        # Test authentication backend
        backend = ShipNumberOrUsernameBackend()
        print("Created backend")
        
        # Test 1: Authenticate with username
        user1 = backend.authenticate(None, username="testuser", password="testpass123")
        print(f"Authenticated with username: {user1 is not None}")
        
        # Test 2: Authenticate with ship registration number (owner)
        user2 = backend.authenticate(None, username="SHIP001", password="testpass123")
        print(f"Authenticated with ship number (owner): {user2 is not None}")
        
        # Test 3: Authenticate with ship registration number (captain)
        captain.user = captain_user
        captain.save()
        
        user3 = backend.authenticate(None, username="SHIP001", password="captainpass123")
        print(f"Authenticated with ship number (captain): {user3 is not None}")
        
        # Clean up
        ship.delete()
        captain.delete()
        owner.delete()
        user.delete()
        captain_user.delete()
        
        print("Authentication tests completed.")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authentication()