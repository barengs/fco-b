from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import SmartScale
from .application.iot_device_service import SmartScaleApplicationService


class SmartScaleSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.service = SmartScaleApplicationService()
        self.scale = SmartScale.objects.create(
            device_id="SCALE-TEST-01",
            name="Timbangan Uji",
            port_name="Pelabuhan Benoa",
            is_active=True
        )

    def test_unregistered_device_rejected(self):
        """Pastikan perangkat tidak terdaftar ditolak (mencegah rogue device creation)."""
        success, res_data, code = self.service.record_weight(
            device_id="ROGUE-DEVICE-99",
            weight=Decimal("25.50"),
            api_key="any_key"
        )
        self.assertFalse(success)
        self.assertEqual(code, 404)
        self.assertIn("belum terdaftar", res_data.get('error', ''))

    def test_registered_device_invalid_api_key_rejected(self):
        """Pastikan perangkat terdaftar dengan API key salah ditolak."""
        success, res_data, code = self.service.record_weight(
            device_id="SCALE-TEST-01",
            weight=Decimal("25.50"),
            api_key="wrong_secret_key"
        )
        self.assertFalse(success)
        self.assertEqual(code, 403)
        self.assertIn("tidak sesuai", res_data.get('error', ''))

    def test_registered_device_valid_api_key_accepted(self):
        """Pastikan perangkat terdaftar dengan API key benar diterima."""
        success, res_data, code = self.service.record_weight(
            device_id="SCALE-TEST-01",
            weight=Decimal("25.50"),
            api_key=self.scale.api_key
        )
        self.assertTrue(success)
        self.assertEqual(code, 201)
        self.assertEqual(res_data['status'], 'success')

    def test_deactivated_device_rejected(self):
        """Pastikan perangkat nonaktif ditolak."""
        self.scale.is_active = False
        self.scale.save()

        success, res_data, code = self.service.record_weight(
            device_id="SCALE-TEST-01",
            weight=Decimal("25.50"),
            api_key=self.scale.api_key
        )
        self.assertFalse(success)
        self.assertEqual(code, 403)
        self.assertIn("dinonaktifkan", res_data.get('error', ''))

    def test_endpoint_unregistered_device_404(self):
        """Pengujian melalui REST endpoint /api/iot/receive-weight/"""
        url = "/api/iot/receive-weight/"
        res = self.client.post(url, {
            "device_id": "ROGUE-DEVICE-99",
            "weight": 50.0
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_endpoint_valid_device_with_header_201(self):
        """Pengujian melalui REST endpoint dengan X-Device-Token header"""
        url = "/api/iot/receive-weight/"
        res = self.client.post(
            url,
            {"device_id": "SCALE-TEST-01", "weight": 42.5},
            format='json',
            HTTP_X_DEVICE_TOKEN=self.scale.api_key
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
