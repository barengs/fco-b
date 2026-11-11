"""
Unit tests for Ships application and domain services.
"""

from decimal import Decimal
from django.test import TestCase
from ships.models import Ship, Quota
from ships.domain.quota_policy import QuotaPolicy
from ships.application.quota_service import QuotaApplicationService


class QuotaPolicyTestCase(TestCase):
    def test_quota_policy_calculations(self):
        # 1000 total, 200 used -> 800 remaining (80%) -> Aman
        comp = QuotaPolicy.evaluate_compliance(1000, 200)
        self.assertEqual(comp["remaining_quota_kg"], 800.0)
        self.assertEqual(comp["remaining_percentage"], 80.0)
        self.assertEqual(comp["status"], "Aman")

        # 1000 total, 700 used -> 300 remaining (30%) -> Waspada (< 35%)
        status = QuotaPolicy.determine_status(1000, 700)
        self.assertEqual(status, "Waspada")

        # 1000 total, 900 used -> 100 remaining (10%) -> Kritis (< 15%)
        status = QuotaPolicy.determine_status(1000, 900)
        self.assertEqual(status, "Kritis")


class QuotaApplicationServiceTestCase(TestCase):
    def setUp(self):
        self.service = QuotaApplicationService()
        self.ship = Ship.objects.create(
            name="KM Laut Biru",
            registration_number="REG-TEST-001",
            gross_tonnage=Decimal("50.0"),
            active=True
        )

    def test_assign_manual_quota_creates_and_updates(self):
        res = self.service.assign_manual_quota(
            ship_registration_number="REG-TEST-001",
            year=2026,
            quota_amount=50000.0
        )
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["data"]["quota_amount"], 50000.0)

        quota = Quota.objects.get(ship=self.ship, year=2026)
        self.assertEqual(float(quota.quota), 50000.0)
        self.assertEqual(float(quota.remaining_quota), 50000.0)

        # Update existing
        res_update = self.service.assign_manual_quota(
            ship_registration_number="REG-TEST-001",
            year=2026,
            quota_amount=60000.0
        )
        self.assertEqual(res_update["status_code"], 200)
        quota.refresh_from_db()
        self.assertEqual(float(quota.quota), 60000.0)

    def test_predict_quota_not_found_ship(self):
        res = self.service.predict_quota_for_ship(
            ship_registration_number="NON-EXISTENT",
            prediction_months=12
        )
        self.assertEqual(res["status_code"], 404)
        self.assertIn("tidak ditemukan", res["error"])
