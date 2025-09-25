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
        
        # Create sample CSV data for fishing areas (using Indonesian field names)
        self.sample_csv_data = """nama,code,deskripsi
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara
Area Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan"""

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
        self.assertEqual(area.nama, 'Area Penangkapan Utara')
        self.assertEqual(area.deskripsi, 'Wilayah penangkapan di utara')

    def test_import_areas_missing_data(self):
        """Test handling of missing required data"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # CSV with missing required fields
        bad_csv_data = """nama,code,deskripsi
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara
,APS-002,Wilayah penangkapan di selatan
Area Penangkapan Barat,,Wilayah penangkapan di barat"""
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': bad_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 1)  # type: ignore # Only 1 valid entry
        self.assertEqual(response.data['errors'], 2)  # type: ignore # 2 errors for missing required fields

    def test_download_template_csv(self):
        """Test downloading CSV template"""
        url = reverse('fishingarea-download-template')
        response = cast(Response, self.client.get(url))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="fishingarea_import_template.csv"', response['Content-Disposition'])
        
        # Check that response contains CSV data
        content = response.content.decode('utf-8')
        self.assertIn('nama,code,deskripsi', content)
        
    def test_download_template_excel(self):
        """Test downloading Excel template"""
        url = reverse('fishingarea-download-template')
        response = cast(Response, self.client.get(url, {'format': 'excel'}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment; filename="fishingarea_import_template.xlsx"', response['Content-Disposition'])