from datetime import datetime, timedelta
from unittest.mock import patch

from odoo import fields

from odoo.addons.fleet_traccar_integration.models.traccar_device import (
    _traccar_datetime,
    _traccar_number,
)

from .common import FleetTraccarCommon


class TestFleetTraccarIntegration(FleetTraccarCommon):
    def test_traccar_datetime(self):
        self.assertFalse(_traccar_datetime(False))
        expected = datetime(2026, 1, 10, 10, 0)
        self.assertEqual(_traccar_datetime("2026-01-10T10:00:00.000Z"), expected)
        self.assertEqual(
            _traccar_datetime("2026-01-10T10:00:00+00:00"),
            expected,
        )
        self.assertEqual(_traccar_datetime(expected), expected)

    def test_traccar_number(self):
        self.assertFalse(_traccar_number(True))
        self.assertFalse(_traccar_number("4.5"))
        self.assertFalse(_traccar_number(float("nan")))
        self.assertEqual(_traccar_number(4), 4.0)
        self.assertEqual(_traccar_number(4.5), 4.5)

    def test_traccar_due(self):
        self.assertTrue(self.company._traccar_due(False, 5))
        self.assertFalse(self.company._traccar_due(fields.Datetime.now(), 5))
        past = fields.Datetime.now() - timedelta(minutes=10)
        self.assertTrue(self.company._traccar_due(past, 5))

    def test_create_remote_device(self):
        response = {
            "id": 42,
            "name": "Tracker 1",
            "uniqueId": "TRC-1",
            "status": "online",
        }
        with patch.object(
            type(self.company), "_traccar_request", return_value=response
        ) as mocked:
            device = self.Device.create(
                {
                    "name": "Tracker 1",
                    "unique_id": "TRC-1",
                    "company_id": self.company.id,
                }
            )
        mocked.assert_called_once()
        args, kwargs = mocked.call_args
        self.assertEqual(args, ("POST", "/api/devices"))
        self.assertEqual(kwargs["json"], {"name": "Tracker 1", "uniqueId": "TRC-1"})
        self.assertEqual(device.traccar_id, 42)
        self.assertEqual(device.status, "online")

    def test_sync_company_devices(self):
        devices = [{"id": 42, "name": "Tracker 1", "uniqueId": "TRC-1"}]
        positions = [
            {
                "id": 100,
                "deviceId": 42,
                "latitude": -23.5,
                "longitude": -46.6,
                "speed": 10,
                "course": 90,
                "address": "Somewhere",
                "fixTime": "2026-01-10T10:00:00.000Z",
            }
        ]

        def fake_request(method, endpoint, **kwargs):
            if endpoint == "/api/devices":
                return devices
            if endpoint == "/api/positions":
                return positions
            raise AssertionError(f"Unexpected request: {endpoint}")

        with patch.object(
            type(self.company), "_traccar_request", side_effect=fake_request
        ):
            self.Device._sync_company_devices(self.company)
        device = self.Device.search([("unique_id", "=", "TRC-1")])
        self.assertTrue(device)
        self.assertEqual(device.traccar_id, 42)
        self.assertEqual(device.latitude, -23.5)
        self.assertEqual(device.longitude, -46.6)
        self.assertEqual(device.status, "unknown")
        self.assertTrue(device.telemetry_device_id)
        self.assertEqual(device.telemetry_device_id.external_ref, "42")
        self.assertFalse(device.telemetry_device_id.vehicle_id)

    def test_sync_company_telemetry(self):
        # A short gap is downloaded immediately
        self.company.write({"traccar_history_days": 1, "traccar_inline_sync_hours": 48})
        device = self._create_device(traccar_id=42)
        positions = [
            {
                "id": 100,
                "deviceId": 42,
                "latitude": -23.5,
                "longitude": -46.6,
                "speed": 10,
                "course": 90,
                "altitude": 760,
                "address": "Somewhere",
                "fixTime": "2026-01-10T10:00:00.000Z",
                "serverTime": "2026-01-10T10:00:05.000Z",
                "attributes": {"ignition": True},
            }
        ]
        with patch.object(
            type(self.company), "_traccar_request", return_value=positions
        ):
            created = self.Telemetry._sync_company_telemetry(
                self.company, devices=device
            )
        self.assertEqual(created, 1)
        telemetry = self.Telemetry.search([("traccar_position_id", "=", 100)])
        self.assertTrue(telemetry)
        self.assertEqual(telemetry.provider, "traccar")
        self.assertEqual(telemetry.traccar_device_id, device)
        self.assertEqual(telemetry.vehicle_id, self.vehicle)
        self.assertEqual(telemetry.fix_time, datetime(2026, 1, 10, 10, 0))
        self.assertEqual(telemetry.latitude, -23.5)
        self.assertEqual(telemetry.longitude, -46.6)
        self.assertEqual(telemetry.address, "Somewhere")

    def test_cron_traccar_sync(self):
        with patch.object(type(self.company), "_traccar_request", return_value=[]):
            self.company._cron_traccar_sync()
        self.assertTrue(self.company.traccar_last_device_sync)
        self.assertTrue(self.company.traccar_last_telemetry_sync)

    def test_cron_traccar_sync_disabled(self):
        self.company.traccar_enabled = False
        with patch.object(type(self.company), "_traccar_request") as mocked:
            self.company._cron_traccar_sync()
        mocked.assert_not_called()
        self.assertFalse(self.company.traccar_last_device_sync)

    def test_action_view_traccar_telemetry(self):
        device = self._create_device(traccar_id=42)
        self.vehicle.traccar_device_id = device
        action = self.vehicle.action_view_traccar_telemetry()
        self.assertEqual(action["res_model"], "fleet.telemetry")
        self.assertEqual(action["domain"][0], ("provider", "=", "traccar"))
        self.assertEqual(action["domain"][1], ("vehicle_id", "=", self.vehicle.id))

    def test_data_records(self):
        self.assertTrue(self.env.ref("fleet_traccar_integration.action_traccar_device"))
        self.assertTrue(
            self.env.ref("fleet_traccar_integration.menu_fleet_traccar_root")
        )
        self.assertTrue(self.env.ref("fleet_traccar_integration.ir_cron_traccar_sync"))
        self.assertTrue(
            self.env.ref("fleet_traccar_integration.group_traccar_administrator")
        )
