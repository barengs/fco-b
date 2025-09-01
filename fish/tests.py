from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.apps import apps
from typing import Any, cast
from rest_framework.response import Response

class FishSpeciesImportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.import_url = reverse('fishspecies-import-species')
        
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create sample CSV data
        self.sample_csv_data = """name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning yang populer di perairan tropis
Ikan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat
Ikan Kerapu,Epinephelus spp.,Ikan batu yang bernilai ekonomi tinggi"""

    def test_import_species_unauthorized(self):
        """Test that unauthenticated users cannot access the import endpoint"""
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_import_species_authorized(self):
        """Test that authenticated users can import fish species"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 3)  # type: ignore
        self.assertEqual(response.data['updated'], 0)  # type: ignore
        self.assertEqual(response.data['errors'], 0)  # type: ignore
        
        # Verify that the species were actually created
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        self.assertEqual(FishSpecies._default_manager.count(), 3)  # type: ignore
        
        # Check that one of the species exists with correct data
        tuna = FishSpecies._default_manager.get(name='Tuna Sirip Kuning')  # type: ignore
        self.assertEqual(tuna.scientific_name, 'Thunnus albacares')
        self.assertEqual(tuna.description, 'Tuna dengan sirip kuning yang populer di perairan tropis')

    def test_import_species_with_updates(self):
        """Test that importing existing species updates them"""
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # First import
        response1 = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['created'], 3)  # type: ignore
        
        # Second import with updated data
        updated_csv_data = """name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning - UPDATED
Ikan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat - UPDATED
Ikan Baru,Novus species,Species baru yang ditambahkan"""
        
        response2 = cast(Response, self.client.post(self.import_url, {
            'csv_data': updated_csv_data
        }, format='json'))
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['created'], 1)  # type: ignore # 1 new species
        self.assertEqual(response2.data['updated'], 2)  # type: ignore # 2 updated species
        self.assertEqual(response2.data['errors'], 0)  # type: ignore
        
        # Verify the update
        tuna = FishSpecies._default_manager.get(name='Tuna Sirip Kuning')  # type: ignore
        self.assertEqual(tuna.description, 'Tuna dengan sirip kuning - UPDATED')

    def test_import_species_missing_data(self):
        """Test handling of missing required data"""
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # CSV with missing name
        bad_csv_data = """name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning
,Ikan tanpa nama,Ini tidak akan diproses
Ikan Kakap,Lutjanus campechanus,Ikan laut"""
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': bad_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 2)  # type: ignore # Only 2 valid entries
        self.assertEqual(response.data['errors'], 1)  # type: ignore # 1 error for missing name


class FishImportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.import_url = reverse('fish-import-fish')
        
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create sample fish species first
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        self.tuna_species = FishSpecies.objects.create(
            name='Tuna Sirip Kuning',
            scientific_name='Thunnus albacares',
            description='Tuna dengan sirip kuning yang populer di perairan tropis'
        )
        
        self.kakap_species = FishSpecies.objects.create(
            name='Ikan Kakap',
            scientific_name='Lutjanus campechanus',
            description='Ikan laut yang umum ditemukan di perairan hangat'
        )
        
        # Create sample CSV data for fish
        self.sample_csv_data = """species_name,name,length,weight,notes
Tuna Sirip Kuning,Budi,120.5,30.2,Ikan tangkapan pertama
Ikan Kakap,Andi,30.0,2.5,Ikan ukuran sedang"""

    def test_import_fish_unauthorized(self):
        """Test that unauthenticated users cannot access the import endpoint"""
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_import_fish_authorized(self):
        """Test that authenticated users can import fish"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': self.sample_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 2)  # type: ignore
        self.assertEqual(response.data['updated'], 0)  # type: ignore
        self.assertEqual(response.data['errors'], 0)  # type: ignore
        
        # Verify that the fish were actually created
        Fish = apps.get_model('fish', 'Fish')
        self.assertEqual(Fish._default_manager.count(), 2)  # type: ignore
        
        # Check that one of the fish exists with correct data
        fish = Fish._default_manager.get(name='Budi')  # type: ignore
        self.assertEqual(fish.species.name, 'Tuna Sirip Kuning')
        self.assertEqual(float(fish.length), 120.5)
        self.assertEqual(float(fish.weight), 30.2)
        self.assertEqual(fish.notes, 'Ikan tangkapan pertama')

    def test_import_fish_missing_species(self):
        """Test handling of missing species"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # CSV with non-existent species
        bad_csv_data = """species_name,name,length,weight,notes
Tuna Sirip Kuning,Budi,120.5,30.2,Ikan tangkapan pertama
Ikan Tidak Ada,Andi,30.0,2.5,Ikan tidak ditemukan"""
        
        response = cast(Response, self.client.post(self.import_url, {
            'csv_data': bad_csv_data
        }, format='json'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 1)  # type: ignore # Only 1 valid entry
        self.assertEqual(response.data['errors'], 1)  # type: ignore # 1 error for missing species


class FishSpeciesTemplateDownloadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_download_species_template(self):
        """Test that the fish species template download endpoint returns a CSV file"""
        url = reverse('fishspecies-download-template')
        response = cast(Response, self.client.get(url))
        
        # Check that the response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response content type is CSV
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Check that the response has the correct content disposition
        self.assertIn('attachment; filename="fish_species_import_template.csv"', response['Content-Disposition'])
        
        # Check that the response contains CSV data
        content = response.content.decode('utf-8')
        self.assertIn('name,scientific_name,description', content)


class FishTemplateDownloadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_download_fish_template(self):
        """Test that the fish template download endpoint returns a CSV file"""
        url = reverse('fish-download-template')
        response = cast(Response, self.client.get(url))
        
        # Check that the response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response content type is CSV
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Check that the response has the correct content disposition
        self.assertIn('attachment; filename="fish_import_template.csv"', response['Content-Disposition'])
        
        # Check that the response contains CSV data
        content = response.content.decode('utf-8')
        self.assertIn('species_name,name,length,weight,notes', content)
