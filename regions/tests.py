from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.apps import apps
from typing import Any, cast
from rest_framework.response import Response

class FishingAreaImportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.import_url = reverse('fishingarea-import-areas')
        
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create sample CSV data for fishing areas
        self.sample_csv_data = """name,code,description,boundary_coordinates
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara,"[[10.0, 20.0], [10.5, 20.5]]"
Area Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan,"[[15.0, 25.0], [15.5, 25.5]]"""

    def test_import_areas_unauthorized(self):
        """Test that unauthenticated users cannot access the import endpoint"""
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_import_areas_authorized(self):
        """Test that authenticated users can import fishing areas"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 2)  # type: ignore
        self.assertEqual(response.data['updated'], 0)  # type: ignore
        self.assertEqual(response.data['errors'], 0)  # type: ignore
        
        # Verify that the fishing areas were actually created
        FishingArea = apps.get_model('regions', 'FishingArea')
        self.assertEqual(FishingArea._default_manager.count(), 2)  # type: ignore
        
        # Check that one of the fishing areas exists with correct data
        area = FishingArea._default_manager.get(code='APU-001')  # type: ignore
        self.assertEqual(area.name, 'Area Penangkapan Utara')
        self.assertEqual(area.description, 'Wilayah penangkapan di utara')
        self.assertEqual(area.boundary_coordinates, '[[10.0, 20.0], [10.5, 20.5]]')

    def test_import_areas_missing_data(self):
        """Test handling of missing required data"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # CSV with missing required fields
        bad_csv_data = """name,code,description,boundary_coordinates
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara,"[[10.0, 20.0], [10.5, 20.5]]"
,APS-002,Wilayah penangkapan di selatan,"[[15.0, 25.0], [15.5, 25.5]]"
Area Penangkapan Barat,,Wilayah penangkapan di barat,"[[12.0, 22.0], [12.5, 22.5]]"""
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': bad_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 1)  # type: ignore # Only 1 valid entry
        self.assertEqual(response.data['errors'], 2)  # type: ignore # 2 errors for missing required fields