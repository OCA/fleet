from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import FleetTelemetryCommon


class TestFleetTelemetryDevice(FleetTelemetryCommon):
    def test_default_values(self):
        self.assertEqual(self.device.company_id, self.env.company)
        self.assertTrue(self.device.active)
        self.assertEqual(self.device.display_name, "Tracker 1")

    def test_unique_reference_per_provider(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.Device.create(
                    {
                        "name": "Duplicated tracker",
                        "provider": "traccar",
                        "external_ref": "DEV-1",
                    }
                )

    def test_same_reference_other_provider(self):
        device = self.Device.create(
            {"name": "Other tracker", "provider": "other", "external_ref": "DEV-1"}
        )
        self.assertEqual(device.external_ref, self.device.external_ref)
