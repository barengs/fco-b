from django.core.management.base import BaseCommand
# Import the models using string references to avoid circular import issues
from django.apps import apps

class Command(BaseCommand):
    help = 'Test the ship registration checking functionality'

    def handle(self, *args, **options):
        self.stdout.write("Testing ship registration checking functionality...")
        
        # Get models using apps.get_model to avoid circular import issues
        Owner = apps.get_model('owners', 'Owner')
        Ship = apps.get_model('ships', 'Ship')
        
        # Create a test owner
        owner, created = Owner.objects.get_or_create(
            name="Test Owner",
            owner_type="individual"
        )
        if created:
            self.stdout.write(f"Created owner: {owner}")
        else:
            self.stdout.write(f"Using existing owner: {owner}")
        
        # Create a test ship
        ship, created = Ship.objects.get_or_create(
            name="Test Ship",
            registration_number="TEST001",
            owner=owner,
            defaults={
                'length': 20.5,
                'width': 5.2,
                'gross_tonnage': 100.0,
                'year_built': 2020,
                'home_port': "Test Port"
            }
        )
        if created:
            self.stdout.write(f"Created ship: {ship}")
        else:
            self.stdout.write(f"Using existing ship: {ship}")
        
        # Test the ship checking functionality
        self.stdout.write("\nTo test the ship checking endpoint, use the following curl command:")
        self.stdout.write('curl -X GET "http://localhost:8000/api/ships/check-ship/?registration_number=TEST001"')
        
        self.stdout.write("\nTo test with a non-existent registration number:")
        self.stdout.write('curl -X GET "http://localhost:8000/api/ships/check-ship/?registration_number=NONEXISTENT"')
        
        self.stdout.write("\nShip registration checking test setup completed.")