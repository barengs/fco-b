from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from owners.authentication import ShipNumberOrUsernameBackend

class Command(BaseCommand):
    help = 'Test the custom authentication system'

    def handle(self, *args, **options):
        self.stdout.write("Testing authentication system...")
        
        # Get the User model
        User = get_user_model()
        
        # Import models inside the method to avoid potential circular import issues
        from owners.models import Owner, Captain
        from ships.models import Ship
        
        # Create test data
        self.stdout.write("Creating test data...")
        
        # Create an owner with a unique name to avoid MultipleObjectsReturned
        owner_name = "Test Owner Unique"
        # Use _default_manager to make Pyright happy
        owner, created = Owner._default_manager.get_or_create(
            name=owner_name,
            owner_type="individual"
        )
        if created:
            self.stdout.write(f"Created owner: {owner}")
        else:
            self.stdout.write(f"Using existing owner: {owner}")
        
        # Create or get a user for the owner
        owner_user, created = User.objects.get_or_create(
            username="testowner_unique"
        )
        if created:
            owner_user.set_password("testpass123")
            owner_user.save()
            self.stdout.write(f"Created user for owner: {owner_user}")
        else:
            self.stdout.write(f"Using existing user for owner: {owner_user}")
        
        owner.user = owner_user
        owner.save()
        
        # Create or get a captain with a unique license number
        # Use _default_manager to make Pyright happy
        captain, created = Captain._default_manager.get_or_create(
            name="Test Captain Unique",
            license_number="LIC001_UNIQUE",
            owner=owner
        )
        if created:
            self.stdout.write(f"Created captain: {captain}")
        else:
            self.stdout.write(f"Using existing captain: {captain}")
        
        # Create or get a user for the captain
        captain_user, created = User.objects.get_or_create(
            username="testcaptain_unique"
        )
        if created:
            captain_user.set_password("captainpass123")
            captain_user.save()
            self.stdout.write(f"Created user for captain: {captain_user}")
        else:
            self.stdout.write(f"Using existing user for captain: {captain_user}")
        
        captain.user = captain_user
        captain.save()
        
        # Create or get a ship with a unique registration number
        # Use _default_manager to make Pyright happy
        ship, created = Ship._default_manager.get_or_create(
            name="Test Ship Unique",
            registration_number="SHIP001_UNIQUE",
            owner=owner,
            defaults={'captain': captain}
        )
        if created:
            self.stdout.write(f"Created ship: {ship}")
        else:
            self.stdout.write(f"Using existing ship: {ship}")
        
        # Test the authentication backend
        self.stdout.write("\nTesting authentication backend...")
        backend = ShipNumberOrUsernameBackend()
        
        # Test 1: Authenticate with username (owner)
        self.stdout.write("Test 1: Authenticating with username (owner)")
        user1 = backend.authenticate(None, username="testowner_unique", password="testpass123")
        self.stdout.write(f"Result: {user1 is not None}")
        if user1:
            self.stdout.write(f"Authenticated user: {user1.username}")
        
        # Test 2: Authenticate with username (captain)
        self.stdout.write("Test 2: Authenticating with username (captain)")
        user2 = backend.authenticate(None, username="testcaptain_unique", password="captainpass123")
        self.stdout.write(f"Result: {user2 is not None}")
        if user2:
            self.stdout.write(f"Authenticated user: {user2.username}")
        
        # Test 3: Authenticate with ship registration number (owner)
        self.stdout.write("Test 3: Authenticating with ship registration number (owner)")
        user3 = backend.authenticate(None, username="SHIP001_UNIQUE", password="testpass123")
        self.stdout.write(f"Result: {user3 is not None}")
        if user3:
            self.stdout.write(f"Authenticated user: {user3.username}")
        
        # Test 4: Authenticate with ship registration number (captain)
        self.stdout.write("Test 4: Authenticating with ship registration number (captain)")
        user4 = backend.authenticate(None, username="SHIP001_UNIQUE", password="captainpass123")
        self.stdout.write(f"Result: {user4 is not None}")
        if user4:
            self.stdout.write(f"Authenticated user: {user4.username}")
        
        self.stdout.write("\nAuthentication system test completed.")