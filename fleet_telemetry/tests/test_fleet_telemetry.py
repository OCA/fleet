import json
from datetime import date, datetime

from psycopg2 import IntegrityError

from odoo.exceptions import AccessError
from odoo.tests import new_test_user
from odoo.tools import mute_logger

from odoo.addons.fleet_telemetry.models.fleet_telemetry import _max_datetime

from .common import FleetTelemetryCommon


class TestFleetTelemetry(FleetTelemetryCommon):
    def test_compute_dates(self):
        telemetry = self._create_telemetry(fix_time="2026-01-10 23:30:00")
        self.assertEqual(telemetry.date_localization, datetime(2026, 1, 10, 23, 30))
        self.assertEqual(telemetry.route_day, date(2026, 1, 10))
        telemetry.fix_time = "2026-01-11 08:00:00"
        self.assertEqual(telemetry.date_localization, datetime(2026, 1, 11, 8, 0))
        self.assertEqual(telemetry.route_day, date(2026, 1, 11))

    def test_compute_dates_without_fix_time(self):
        telemetry = self._create_telemetry(fix_time=False)
        self.assertFalse(telemetry.date_localization)
        self.assertFalse(telemetry.route_day)

    def test_default_attributes(self):
        telemetry = self._create_telemetry()
        self.assertEqual(json.loads(telemetry.attributes), {})

    def test_unique_position_per_provider(self):
        self._create_telemetry(external_position_ref="POS-1")
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self._create_telemetry(
                    external_position_ref="POS-1", fix_time="2026-01-10 11:00:00"
                )

    def test_max_datetime(self):
        first = datetime(2026, 1, 10, 10, 0)
        second = datetime(2026, 1, 10, 11, 0)
        self.assertEqual(_max_datetime(first, second), second)
        self.assertEqual(_max_datetime(second, first), second)
        self.assertEqual(_max_datetime("2026-01-10 10:00:00", False), first)
        self.assertEqual(_max_datetime(False, second), second)
        self.assertFalse(_max_datetime(False, False))

    def test_merge_attributes(self):
        merged = self.Telemetry._merge_attributes(
            json.dumps({"ignition": True, "fuel": 10}),
            json.dumps({"fuel": 20, "ignition": None, "motion": False}),
        )
        self.assertEqual(
            json.loads(merged), {"ignition": True, "fuel": 20, "motion": False}
        )
        self.assertEqual(self.Telemetry._merge_attributes(False, False), "{}")

    def test_merge_duplicate_telemetry(self):
        main = self._create_telemetry(
            server_time="2026-01-10 10:00:05",
            attributes=json.dumps({"ignition": True, "fuel": 10}),
        )
        duplicate = self._create_telemetry(
            external_position_ref="POS-2",
            server_time="2026-01-10 10:00:10",
            speed=42.0,
            course=90.0,
            altitude=760.0,
            address="Praça da Sé, São Paulo",
            attributes=json.dumps({"fuel": 20, "ignition": None}),
        )
        other_position = self._create_telemetry(
            fix_time="2026-01-10 10:05:00", latitude=-23.0, longitude=-46.0
        )
        self.Telemetry._merge_duplicate_telemetry()
        self.assertTrue(main.exists())
        self.assertFalse(duplicate.exists())
        self.assertTrue(other_position.exists())
        self.assertEqual(main.server_time, datetime(2026, 1, 10, 10, 0, 10))
        self.assertEqual(main.external_position_ref, "POS-2")
        self.assertEqual(main.speed, 42.0)
        self.assertEqual(main.course, 90.0)
        self.assertEqual(main.altitude, 760.0)
        self.assertEqual(main.address, "Praça da Sé, São Paulo")
        self.assertEqual(json.loads(main.attributes), {"ignition": True, "fuel": 20})

    def test_merge_duplicate_telemetry_keeps_main_values(self):
        main = self._create_telemetry(
            server_time="2026-01-10 10:00:10", speed=10.0, address="Main"
        )
        duplicate = self._create_telemetry(
            server_time="2026-01-10 10:00:05", speed=20.0, address="Duplicate"
        )
        self.Telemetry._merge_duplicate_telemetry()
        self.assertFalse(duplicate.exists())
        self.assertEqual(main.server_time, datetime(2026, 1, 10, 10, 0, 10))
        self.assertEqual(main.speed, 10.0)
        self.assertEqual(main.address, "Main")

    def test_merge_duplicate_telemetry_skips_incomplete_groups(self):
        records = (
            self._create_telemetry(device_id=False)
            | self._create_telemetry(device_id=False)
            | self._create_telemetry(fix_time=False)
            | self._create_telemetry(fix_time=False)
        )
        self.Telemetry._merge_duplicate_telemetry()
        self.assertEqual(records.exists(), records)

    def test_access_rights(self):
        telemetry = self._create_telemetry()
        fleet_user = new_test_user(
            self.env, login="fleet_tel_user", groups="fleet.fleet_group_user"
        )
        fleet_manager = new_test_user(
            self.env, login="fleet_tel_manager", groups="fleet.fleet_group_manager"
        )
        self.assertEqual(telemetry.with_user(fleet_user).provider, "traccar")
        with self.assertRaises(AccessError):
            self.Telemetry.with_user(fleet_user).create(
                {"company_id": self.company.id, "provider": "traccar"}
            )
        with self.assertRaises(AccessError):
            self.device.with_user(fleet_user).unlink()
        record = self.Telemetry.with_user(fleet_manager).create(
            {"company_id": self.company.id, "provider": "traccar"}
        )
        record.unlink()
        self.assertFalse(record.exists())
