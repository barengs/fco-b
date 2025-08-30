from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.apps import apps
from typing import Any, cast
from rest_framework.response import Response

class ShipImportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.import_url = reverse('ship-import-ships')
        
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create sample owner and captain first
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')
        
        self.owner = Owner.objects.create(
            name='Test Owner',
            owner_type='individual'
        )
        
        self.captain = Captain.objects.create(
            name='Test Captain',
            license_number='CAPT001',
            owner=self.owner
        )
        
        # Create sample CSV data for ships
        self.sample_csv_data = """name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
Test Ship 1,SHIP001,Test Owner,Test Captain,20.5,5.2,100.5,2020,Port A,true
Test Ship 2,SHIP002,Test Owner,,15.0,4.0,75.0,2018,Port B,true"""

    def test_import_ships_unauthorized(self):
        """Test that unauthenticated users cannot access the import endpoint"""
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_import_ships_authorized(self):
        """Test that authenticated users can import ships"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 2)  # type: ignore
        self.assertEqual(response.data['updated'], 0)  # type: ignore
        self.assertEqual(response.data['errors'], 0)  # type: ignore
        
        # Verify that the ships were actually created
        Ship = apps.get_model('ships', 'Ship')
        self.assertEqual(Ship._default_manager.count(), 2)  # type: ignore
        
        # Check that one of the ships exists with correct data
        ship = Ship._default_manager.get(registration_number='SHIP001')  # type: ignore
        self.assertEqual(ship.name, 'Test Ship 1')
        self.assertEqual(float(ship.length), 20.5)
        self.assertEqual(float(ship.width), 5.2)
        self.assertEqual(float(ship.gross_tonnage), 100.5)
        self.assertEqual(ship.year_built, 2020)
        self.assertEqual(ship.home_port, 'Port A')
        self.assertTrue(ship.active)

    def test_import_ships_missing_data(self):
        """Test handling of missing required data"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # CSV with missing required fields
        bad_csv_data = """name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
Test Ship 1,SHIP001,Test Owner,Test Captain,20.5,5.2,100.5,2020,Port A,true
,SHIP002,Test Owner,,15.0,4.0,75.0,2018,Port B,true
Test Ship 3,,Test Owner,,15.0,4.0,75.0,2018,Port B,true"""
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': bad_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 1)  # type: ignore # Only 1 valid entry
        self.assertEqual(response.data['errors'], 2)  # type: ignore # 2 errors for missing required fields