from datetime import datetime, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError

from odoo.addons.fleet_traccar_integration.models.traccar_device import (
    _traccar_datetime,
)

from .common import FleetTraccarCommon


def _position(position_id, fix_time, **values):
    position = {
        "id": position_id,
        "deviceId": 42,
        "latitude": -23.5,
        "longitude": -46.6,
        "speed": 10,
        "fixTime": fix_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "attributes": {},
    }
    position.update(values)
    return position


class TestTraccarSyncJob(FleetTraccarCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Job = cls.env["traccar.sync.job"]
        cls.Wizard = cls.env["traccar.history.import.wizard"]
        cls.device = cls._create_device(traccar_id=42)
        cls.vehicle.traccar_device_id = cls.device
        cls.Job.search([]).write({"state": "cancelled"})

    def _fake_route(self, method, endpoint, **kwargs):
        """Answer one position one hour after the start of each window."""
        if endpoint != "/api/reports/route":
            return []
        params = kwargs["params"]
        date_from = _traccar_datetime(params["from"])
        hours = int((date_from - datetime(2025, 1, 1)).total_seconds() // 3600)
        # Traccar position ids are unique across devices
        offset = 0 if str(params["deviceId"]) == "42" else 100000
        return [_position(hours + offset, date_from + timedelta(hours=1))]

    def _create_job(self, days=2, **values):
        date_to = datetime(2026, 1, 10)
        vals = {
            "company_id": self.company.id,
            "device_ids": [(6, 0, self.device.ids)],
            "date_from": date_to - timedelta(days=days),
            "date_to": date_to,
        }
        vals.update(values)
        return self.Job.create(vals)

    def test_store_positions_batch(self):
        fix_time = datetime(2026, 1, 10, 10, 0)
        positions = [
            _position(100, fix_time, attributes={"ignition": True}),
            _position(101, fix_time + timedelta(minutes=1)),
            # Same position repeated in the same answer
            _position(101, fix_time + timedelta(minutes=1)),
        ]
        created, updated = self.Telemetry._traccar_store_positions(
            self.company, self.device, positions
        )
        self.assertEqual((created, updated), (2, 0))
        positions[0]["attributes"] = {"battery": 90}
        created, updated = self.Telemetry._traccar_store_positions(
            self.company, self.device, positions[:2]
        )
        self.assertEqual((created, updated), (0, 2))
        telemetry = self.Telemetry.search([("traccar_position_id", "=", 100)])
        self.assertIn("ignition", telemetry.attributes)
        self.assertIn("battery", telemetry.attributes)
        self.assertEqual(self.device.last_update, fix_time + timedelta(minutes=1))

    def test_old_position_keeps_device_position(self):
        self.device.write(
            {"last_update": datetime(2026, 1, 10, 12, 0), "latitude": -10.0}
        )
        self.Telemetry._traccar_store_positions(
            self.company, self.device, [_position(200, datetime(2026, 1, 1, 8, 0))]
        )
        self.assertEqual(self.device.last_update, datetime(2026, 1, 10, 12, 0))
        self.assertEqual(self.device.latitude, -10.0)

    def test_job_windows_and_progress(self):
        job = self._create_job(days=2)
        self.assertEqual(job.window_count, 2)
        self.assertEqual(job.progress, 0.0)
        self.assertIn(self.device.name, job.name)

    def test_job_date_check(self):
        with self.assertRaises(UserError):
            self._create_job(days=0)

    def test_cron_process_jobs(self):
        job = self._create_job(days=2)
        with patch.object(
            type(self.company), "_traccar_request", side_effect=self._fake_route
        ) as mocked:
            self.Job._cron_process_jobs()
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(job.state, "done")
        self.assertEqual(job.window_done, 2)
        self.assertEqual(job.points_created, 2)
        self.assertEqual(job.progress, 100.0)
        self.assertTrue(job.date_finished)
        self.assertEqual(self.device.traccar_sync_job_count, 1)
        points = self.Telemetry.search([("traccar_device_id", "=", self.device.id)])
        self.assertEqual(len(points), 2)

    def test_cron_process_several_devices(self):
        device_2 = self._create_device(name="Tracker 2", unique_id="TRC-2")
        job = self._create_job(
            days=1, device_ids=[(6, 0, (self.device | device_2).ids)]
        )
        self.assertEqual(job.window_count, 2)
        with patch.object(
            type(self.company), "_traccar_request", side_effect=self._fake_route
        ):
            self.Job._cron_process_jobs()
        self.assertEqual(job.state, "done")
        self.assertEqual(job.points_created, 2)
        self.assertEqual(job.points_updated, 0)
        self.assertEqual(
            self.Telemetry.search_count([("traccar_device_id", "=", device_2.id)]), 1
        )

    def test_job_failure_and_resume(self):
        job = self._create_job(days=2)
        calls = []

        def failing_route(method, endpoint, **kwargs):
            calls.append(endpoint)
            if len(calls) > 1:
                raise ConnectionError("Traccar is down")
            return self._fake_route(method, endpoint, **kwargs)

        with patch.object(
            type(self.company), "_traccar_request", side_effect=failing_route
        ):
            self.Job._cron_process_jobs()
        self.assertEqual(job.state, "failed")
        self.assertEqual(job.error_message, "Traccar is down")
        self.assertEqual(job.window_done, 1)
        job.action_resume()
        self.assertEqual(job.state, "queued")
        self.assertFalse(job.error_message)
        with patch.object(
            type(self.company), "_traccar_request", side_effect=self._fake_route
        ) as mocked:
            self.Job._cron_process_jobs()
        # Resumes from the checkpoint: only the missing window is downloaded
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(job.state, "done")
        self.assertEqual(job.points_created, 2)

    def test_job_cancel(self):
        job = self._create_job(days=2)
        job.action_cancel()
        self.assertEqual(job.state, "cancelled")
        with patch.object(type(self.company), "_traccar_request") as mocked:
            self.Job._cron_process_jobs()
        mocked.assert_not_called()

    def test_sync_long_gap_creates_job(self):
        self.company.write(
            {"traccar_history_days": 30, "traccar_inline_sync_hours": 24}
        )
        with patch.object(type(self.company), "_traccar_request") as mocked:
            created, jobs = self.Telemetry._traccar_sync_devices(
                self.company, devices=self.device
            )
        mocked.assert_not_called()
        self.assertEqual(created, 0)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs.device_ids, self.device)
        self.assertEqual(jobs.state, "queued")

    def test_sync_skips_device_with_active_job(self):
        self._create_job(days=2)
        self.company.write({"traccar_history_days": 1, "traccar_inline_sync_hours": 48})
        with patch.object(type(self.company), "_traccar_request") as mocked:
            created, jobs = self.Telemetry._traccar_sync_devices(
                self.company, devices=self.device
            )
        mocked.assert_not_called()
        self.assertEqual(created, 0)
        self.assertFalse(jobs)

    def test_vehicle_sync_locations_opens_job(self):
        self.company.write(
            {"traccar_history_days": 30, "traccar_inline_sync_hours": 24}
        )
        with patch.object(type(self.company), "_traccar_request", return_value=[]):
            action = self.vehicle.action_traccar_sync_locations()
        self.assertEqual(action["res_model"], "traccar.sync.job")
        self.assertTrue(action["res_id"])

    def test_wizard_periods(self):
        wizard = self.Wizard.create(
            {"device_ids": [(6, 0, self.device.ids)], "period": "yesterday"}
        )
        self.assertEqual(wizard.date_to - wizard.date_from, timedelta(days=1))
        wizard.period = "last_7_days"
        self.assertEqual(
            (wizard.date_to - wizard.date_from).days,
            7,
        )
        self.Telemetry._traccar_store_positions(
            self.company, self.device, [_position(300, datetime(2026, 1, 5, 8, 0))]
        )
        wizard.period = "since_last_point"
        self.assertEqual(wizard.date_from, datetime(2026, 1, 5, 8, 0))

    def test_wizard_max_period(self):
        self.company.traccar_history_max_days = 31
        wizard = self.Wizard.create(
            {
                "device_ids": [(6, 0, self.device.ids)],
                "period": "custom",
                "date_from": fields.Datetime.now() - timedelta(days=40),
                "date_to": fields.Datetime.now(),
            }
        )
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_wizard_confirm(self):
        wizard = self.Wizard.create(
            {"device_ids": [(6, 0, self.device.ids)], "period": "last_7_days"}
        )
        action = wizard.action_confirm()
        job = self.Job.browse(action["res_id"])
        self.assertEqual(job.device_ids, self.device)
        self.assertEqual(job.state, "queued")
        # A second import of the same device opens the running one
        wizard_2 = self.Wizard.create(
            {"device_ids": [(6, 0, self.device.ids)], "period": "today"}
        )
        self.assertEqual(wizard_2.action_confirm()["res_id"], job.id)

    def test_device_action_opens_wizard(self):
        action = self.device.action_traccar_sync_telemetry_history()
        self.assertEqual(action["res_model"], "traccar.history.import.wizard")
        self.assertEqual(
            action["context"]["default_device_ids"], [(6, 0, self.device.ids)]
        )
        with self.assertRaises(UserError):
            self.Wizard._get_wizard_action(self.Device.browse())
