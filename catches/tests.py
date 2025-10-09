from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.apps import apps
from decimal import Decimal
from datetime import date
import json

User = get_user_model()


class FishCatchModelTestCase(TestCase):
    """Test cases for FishCatch model"""

    def setUp(self):
        # Create test dependencies
        Ship = apps.get_model('ships', 'Ship')
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')

        # Create owner
        self.owner = Owner.objects.create(
            full_name='Test Owner',
            owner_type='individual'
        )

        # Create captain
        self.captain = Captain.objects.create(
            full_name='Test Captain',
            license_number='CAPT123456',
            owner=self.owner
        )

        # Create ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='SHIP123',
            owner=self.owner,
            captain=self.captain
        )

    def test_fish_catch_creation(self):
        """Test creating a FishCatch instance"""
        FishCatch = apps.get_model('catches', 'FishCatch')

        catch = FishCatch.objects.create(
            ship=self.ship,
            catch_date=date(2024, 1, 15),
            catch_type='pelagic',
            location_latitude=Decimal('-6.2088'),
            location_longitude=Decimal('106.8456'),
            description='Test catch'
        )

        self.assertEqual(catch.ship, self.ship)
        self.assertEqual(catch.catch_date, date(2024, 1, 15))
        self.assertEqual(catch.catch_type, 'pelagic')
        self.assertEqual(catch.location_latitude, Decimal('-6.2088'))
        self.assertEqual(catch.location_longitude, Decimal('106.8456'))
        self.assertEqual(catch.description, 'Test catch')
        self.assertEqual(str(catch), f"Laporan penangkapan untuk {self.ship.name} pada {catch.catch_date}")

    def test_fish_catch_str_method(self):
        """Test the string representation of FishCatch"""
        FishCatch = apps.get_model('catches', 'FishCatch')

        catch = FishCatch.objects.create(
            ship=self.ship,
            catch_date=date(2024, 1, 15),
            catch_type='pelagic',
            location_latitude=Decimal('-6.2088'),
            location_longitude=Decimal('106.8456')
        )

        expected_str = f"Laporan penangkapan untuk {self.ship.name} pada {catch.catch_date}"
        self.assertEqual(str(catch), expected_str)


class CatchDetailModelTestCase(TestCase):
    """Test cases for CatchDetail model"""

    def setUp(self):
        # Create test dependencies
        Ship = apps.get_model('ships', 'Ship')
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        FishingArea = apps.get_model('regions', 'FishingArea')
        FishCatch = apps.get_model('catches', 'FishCatch')

        # Create owner
        self.owner = Owner.objects.create(
            full_name='Test Owner',
            owner_type='individual'
        )

        # Create captain
        self.captain = Captain.objects.create(
            full_name='Test Captain',
            license_number='CAPT123456',
            owner=self.owner
        )

        # Create ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='SHIP123',
            owner=self.owner,
            captain=self.captain
        )

        # Create fish species
        self.fish_species = FishSpecies.objects.create(
            name='Test Fish',
            scientific_name='Test scientificus'
        )

        # Create fishing area
        self.fishing_area = FishingArea.objects.create(
            nama='WPP 711',
            code='711'
        )

        # Create fish catch
        self.fish_catch = FishCatch.objects.create(
            ship=self.ship,
            catch_date=date(2024, 1, 15),
            catch_type='pelagic',
            location_latitude=Decimal('-6.2088'),
            location_longitude=Decimal('106.8456')
        )

    def test_catch_detail_creation(self):
        """Test creating a CatchDetail instance"""
        CatchDetail = apps.get_model('catches', 'CatchDetail')

        detail = CatchDetail.objects.create(
            fish_catch=self.fish_catch,
            fish_species=self.fish_species,
            wpp=self.fishing_area,
            quantity=Decimal('100.50'),
            unit='kg',
            value=Decimal('500000.00'),
            notes='Test notes'
        )

        self.assertEqual(detail.fish_catch, self.fish_catch)
        self.assertEqual(detail.fish_species, self.fish_species)
        self.assertEqual(detail.wpp, self.fishing_area)
        self.assertEqual(detail.quantity, Decimal('100.50'))
        self.assertEqual(detail.unit, 'kg')
        self.assertEqual(detail.value, Decimal('500000.00'))
        self.assertEqual(detail.notes, 'Test notes')
        self.assertEqual(str(detail), f"{self.fish_species.name}: {detail.quantity} {detail.unit}")


class FishCatchAPITestCase(TestCase):
    """Test cases for FishCatch API endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create test dependencies
        Ship = apps.get_model('ships', 'Ship')
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')

        # Create owner
        self.owner = Owner.objects.create(
            full_name='Test Owner',
            owner_type='individual'
        )

        # Create captain
        self.captain = Captain.objects.create(
            full_name='Test Captain',
            license_number='CAPT123456',
            owner=self.owner
        )

        # Create ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='SHIP123',
            owner=self.owner,
            captain=self.captain
        )

    def test_list_fish_catches_unauthenticated(self):
        """Test that unauthenticated users can list fish catches"""
        response = self.client.get(reverse('fishcatch-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_fish_catch_authenticated(self):
        """Test that authenticated users can create fish catches"""
        self.client.force_authenticate(user=self.user)

        data = {
            'ship': self.ship.registration_number,
            'catch_date': '2024-01-15',
            'catch_type': 'pelagic',
            'location_latitude': '-6.2088',
            'location_longitude': '106.8456',
            'description': 'Test catch via API'
        }

        response = self.client.post(reverse('fishcatch-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the catch was created
        FishCatch = apps.get_model('catches', 'FishCatch')
        catch = FishCatch.objects.get(description='Test catch via API')
        self.assertEqual(catch.ship, self.ship)
        self.assertEqual(catch.catch_date, date(2024, 1, 15))

    def test_create_fish_catch_unauthenticated(self):
        """Test that unauthenticated users cannot create fish catches"""
        data = {
            'ship': self.ship.registration_number,
            'catch_date': '2024-01-15',
            'catch_type': 'pelagic',
            'location_latitude': '-6.2088',
            'location_longitude': '106.8456',
            'description': 'Test catch via API'
        }

        response = self.client.post(reverse('fishcatch-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FishCatchWithDetailsAPITestCase(TestCase):
    """Test cases for FishCatchWithDetails API endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create test dependencies
        Ship = apps.get_model('ships', 'Ship')
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')
        FishSpecies = apps.get_model('fish', 'FishSpecies')

        # Create owner
        self.owner = Owner.objects.create(
            full_name='Test Owner',
            owner_type='individual'
        )

        # Create captain
        self.captain = Captain.objects.create(
            full_name='Test Captain',
            license_number='CAPT123456',
            owner=self.owner
        )

        # Create ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='SHIP123',
            owner=self.owner,
            captain=self.captain
        )

        # Create fish species
        self.fish_species1 = FishSpecies.objects.create(
            name='Tuna Sirip Kuning',
            scientific_name='Thunnus albacares'
        )

        self.fish_species2 = FishSpecies.objects.create(
            name='Ikan Kakap',
            scientific_name='Lutjanus campechanus'
        )

    def test_create_fish_catch_with_details_authenticated(self):
        """Test creating fish catch with details via API"""
        self.client.force_authenticate(user=self.user)

        data = {
            'ship': self.ship.registration_number,
            'catch_date': '2024-01-15',
            'catch_type': 'pelagic',
            'location_latitude': '-6.2088',
            'location_longitude': '106.8456',
            'description': 'Test catch with details',
            'catch_details': [
                {
                    'fish_species': self.fish_species1.id,
                    'quantity': '150.50',
                    'unit': 'kg',
                    'value': '750000.00',
                    'notes': 'Good catch'
                },
                {
                    'fish_species': self.fish_species2.id,
                    'quantity': '75.25',
                    'unit': 'kg',
                    'value': '375000.00',
                    'notes': 'Medium catch'
                }
            ]
        }

        response = self.client.post(reverse('fishcatch-with-details-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the catch and details were created
        FishCatch = apps.get_model('catches', 'FishCatch')
        CatchDetail = apps.get_model('catches', 'CatchDetail')

        catch = FishCatch.objects.get(description='Test catch with details')
        self.assertEqual(catch.ship, self.ship)

        details = CatchDetail.objects.filter(fish_catch=catch)
        self.assertEqual(details.count(), 2)

        # Check first detail
        detail1 = details.filter(fish_species=self.fish_species1).first()
        self.assertEqual(detail1.quantity, Decimal('150.50'))
        self.assertEqual(detail1.unit, 'kg')
        self.assertEqual(detail1.value, Decimal('750000.00'))
        self.assertEqual(detail1.notes, 'Good catch')

    def test_download_template(self):
        """Test downloading CSV template"""
        response = self.client.get(reverse('fishcatch-with-details-download-template'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="catch_data_import_template.csv"', response['Content-Disposition'])

        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('ship_registration', content)
        self.assertIn('fish_species_name', content)
        self.assertIn('Tuna Sirip Kuning', content)
