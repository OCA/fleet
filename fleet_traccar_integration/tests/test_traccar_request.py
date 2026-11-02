import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import requests

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .common import FleetTraccarCommon

SESSION_PATH = (
    "odoo.addons.fleet_traccar_integration.models.res_company.requests.Session"
)


def _response(status_code=200, payload=None, content=None, reason="OK"):
    """Build a fake ``requests.Response`` answered by the mocked Traccar."""
    response = MagicMock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.reason = reason
    if content is None:
        content = json.dumps(payload).encode() if payload is not None else b""
    response.content = content
    response.text = content.decode()
    response.json.side_effect = lambda: json.loads(content)
    return response


class TestTraccarRequest(FleetTraccarCommon):
    """Calls to the Traccar API with a mocked HTTP session."""

    def _mock_session(self, response=None, login_response=None, error=None):
        patcher = patch(SESSION_PATH)
        session_class = patcher.start()
        self.addCleanup(patcher.stop)
        session = session_class.return_value
        if error:
            session.request.side_effect = error
        else:
            session.request.return_value = response or _response(payload=[])
        session.post.return_value = login_response or _response(payload={})
        return session

    def test_request_basic_auth(self):
        session = self._mock_session(_response(payload=[{"id": 1}]))
        self.company.traccar_base_url = "https://traccar.example.com/"
        result = self.company._traccar_request("GET", "api/devices", params={"a": 1})
        self.assertEqual(result, [{"id": 1}])
        args, kwargs = session.request.call_args
        self.assertEqual(args, ("GET", "https://traccar.example.com/api/devices"))
        self.assertEqual(kwargs["auth"], ("user", "secret"))
        self.assertEqual(kwargs["params"], {"a": 1})
        self.assertEqual(kwargs["headers"]["Accept"], "application/json")
        self.assertFalse(kwargs["allow_redirects"])
        session.post.assert_not_called()

    def test_request_token_auth(self):
        session = self._mock_session()
        self.company.write({"traccar_auth_mode": "token", "traccar_password": "abc"})
        self.company._traccar_request("GET", "/api/server")
        headers = session.request.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer abc")
        self.assertNotIn("auth", session.request.call_args.kwargs)
        self.company.traccar_password = "Bearer xyz"
        self.company._traccar_request("GET", "/api/server")
        headers = session.request.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer xyz")

    def test_request_session_auth(self):
        session = self._mock_session(_response(payload={"version": "6.0"}))
        self.company.traccar_auth_mode = "session"
        result = self.company._traccar_request("GET", "/api/server")
        self.assertEqual(result, {"version": "6.0"})
        session.post.assert_called_once()
        args, kwargs = session.post.call_args
        self.assertEqual(args, ("https://traccar.example.com/api/session",))
        self.assertEqual(kwargs["data"], {"email": "user", "password": "secret"})

    def test_request_session_auth_failed(self):
        session = self._mock_session(
            login_response=_response(401, content=b"", reason="Unauthorized")
        )
        self.company.traccar_auth_mode = "session"
        with self.assertRaisesRegex(UserError, "Unauthorized"):
            self.company._traccar_request("GET", "/api/server")
        session.request.assert_not_called()

    def test_request_missing_configuration(self):
        session = self._mock_session()
        self.company.traccar_password = False
        with self.assertRaises(UserError):
            self.company._traccar_request("GET", "/api/server")
        self.company.write({"traccar_password": "secret", "traccar_username": False})
        with self.assertRaises(UserError):
            self.company._traccar_request("GET", "/api/server")
        self.company.traccar_auth_mode = "session"
        with self.assertRaises(UserError):
            self.company._traccar_request("GET", "/api/server")
        session.request.assert_not_called()

    def test_request_http_errors(self):
        self._mock_session(_response(403))
        with self.assertRaisesRegex(UserError, "credentials"):
            self.company._traccar_request("GET", "/api/server")
        self._mock_session(_response(500))
        with self.assertRaisesRegex(UserError, "500"):
            self.company._traccar_request("GET", "/api/server")

    def test_request_connection_error(self):
        self._mock_session(error=requests.ConnectionError("down"))
        with self.assertRaisesRegex(UserError, "Could not reach Traccar"):
            self.company._traccar_request("GET", "/api/server")

    def test_request_invalid_and_empty_body(self):
        self._mock_session(_response(content=b"<html>"))
        with self.assertRaisesRegex(UserError, "invalid API response"):
            self.company._traccar_request("GET", "/api/server")
        self._mock_session(_response(content=b""))
        self.assertEqual(self.company._traccar_request("GET", "/api/server"), [])

    def test_settings_actions(self):
        self._mock_session(_response(payload=[{"id": 1}, {"id": 2}]))
        settings = self.env["res.config.settings"].create({})
        action = settings.action_traccar_test_connection()
        self.assertEqual(action["params"]["type"], "success")
        action = settings.action_traccar_test_api_access()
        self.assertIn("2", action["params"]["message"])
        action = settings.action_traccar_merge_duplicate_telemetry()
        self.assertEqual(action["tag"], "display_notification")

    def test_cron_sync_error_is_logged(self):
        with (
            patch.object(
                type(self.company),
                "_traccar_request",
                side_effect=UserError("Traccar is down"),
            ),
            mute_logger("odoo.addons.fleet_traccar_integration.models.res_company"),
        ):
            self.company._cron_traccar_sync()
        self.assertFalse(self.company.traccar_last_device_sync)


class TestTraccarSync(FleetTraccarCommon):
    """Device and telemetry synchronization paths with a mocked API."""

    def _patch_request(self, **kwargs):
        return patch.object(type(self.company), "_traccar_request", **kwargs)

    def test_create_device_without_traccar(self):
        self.company.traccar_enabled = False
        with self._patch_request() as mocked:
            device = self.Device.create({"name": "Tracker 9", "unique_id": "TRC-9"})
        mocked.assert_not_called()
        self.assertFalse(device.traccar_id)

    def test_sync_existing_devices(self):
        device = self._create_device(traccar_id=42)
        devices = [
            {"id": 42, "name": "Renamed", "uniqueId": "TRC-1", "status": "online"},
            {"id": 43, "name": "No unique id"},
            {"id": 44, "name": "Without position", "uniqueId": "TRC-4"},
        ]
        positions = [{"deviceId": 42, "latitude": 100, "longitude": -46.6}]

        def fake_request(method, endpoint, **kwargs):
            return devices if endpoint == "/api/devices" else positions

        with self._patch_request(side_effect=fake_request):
            device.action_sync_devices()
            action = device.action_traccar_update_status()
        self.assertEqual(action["tag"], "display_notification")
        self.assertTrue(self.company.traccar_last_device_sync)
        self.assertEqual(device.name, "Renamed")
        self.assertEqual(device.status, "online")
        # Invalid coordinates are not stored
        self.assertEqual(device.latitude, 0)
        self.assertEqual(device.longitude, 0)
        self.assertEqual(self.Device.search_count([("traccar_id", "=", 43)]), 0)
        self.assertEqual(
            self.Device.search([("traccar_id", "=", 44)]).name, "Without position"
        )
        # The existing telemetry device is reused
        telemetry_device = device.telemetry_device_id
        device.telemetry_device_id = False
        device._sync_telemetry_device()
        self.assertEqual(device.telemetry_device_id, telemetry_device)

    def test_fetch_positions_fallback(self):
        device = self._create_device(traccar_id=42)
        date_to = datetime(2026, 1, 10)
        date_from = date_to - timedelta(hours=1)
        endpoints = []

        def fake_request(method, endpoint, **kwargs):
            endpoints.append(endpoint)
            if endpoint == "/api/reports/route":
                return []
            return [{"id": 7, "fixTime": "2026-01-09T23:30:00Z"}]

        with self._patch_request(side_effect=fake_request):
            positions = self.Telemetry._traccar_fetch_positions(
                self.company, device, date_from, date_to
            )
        self.assertEqual(endpoints, ["/api/reports/route", "/api/positions"])
        self.assertEqual(positions[0]["id"], 7)
        with self._patch_request(return_value={"message": "Bad request"}):
            with self.assertRaisesRegex(UserError, "Bad request"):
                self.Telemetry._traccar_fetch_positions(
                    self.company, device, date_from, date_to
                )
        with self._patch_request(return_value=[]):
            self.assertEqual(
                self.Telemetry._traccar_fetch_positions(
                    self.company, device, date_from, date_to
                ),
                [],
            )

    def test_vehicle_sync_locations(self):
        device = self._create_device(traccar_id=42)
        self.vehicle.traccar_device_id = device
        self.company.write({"traccar_history_days": 1, "traccar_inline_sync_hours": 48})
        position = {
            "id": 500,
            "deviceId": 42,
            "latitude": -23.5,
            "longitude": -46.6,
            "fixTime": fields.Datetime.to_string(fields.Datetime.now()).replace(
                " ", "T"
            )
            + "Z",
        }

        def fake_request(method, endpoint, **kwargs):
            if endpoint == "/api/devices":
                return [{"id": 42, "name": "Tracker 1", "uniqueId": "TRC-1"}]
            return [position]

        with self._patch_request(side_effect=fake_request):
            action = self.vehicle.action_traccar_sync_locations()
        self.assertEqual(action["tag"], "display_notification")
        self.assertTrue(self.company.traccar_last_telemetry_sync)
        self.assertEqual(self.vehicle.traccar_telemetry_count, 1)
        # Without vehicles the whole company is synchronized
        with self._patch_request(return_value=[]):
            action = self.env["fleet.vehicle"].action_traccar_sync_locations()
        self.assertEqual(action["tag"], "display_notification")

    def test_vehicle_and_device_actions(self):
        device = self._create_device(traccar_id=42)
        self.vehicle.traccar_device_id = device
        action = self.vehicle.action_traccar_import_history()
        self.assertEqual(action["res_model"], "traccar.history.import.wizard")
        action = device.action_view_traccar_sync_jobs()
        self.assertEqual(action["domain"], [("device_ids", "in", device.ids)])

    def test_cron_sync_not_due(self):
        now = fields.Datetime.now()
        self.company.write(
            {"traccar_last_device_sync": now, "traccar_last_telemetry_sync": now}
        )
        with self._patch_request() as mocked:
            self.company._cron_traccar_sync()
        mocked.assert_not_called()

    def test_store_positions_merges_existing_points(self):
        device = self._create_device(traccar_id=42)
        other_device = self._create_device(
            name="Tracker 2", unique_id="TRC-2", traccar_id=43
        )
        fix_time = datetime(2026, 1, 10, 10, 0)
        base_values = {
            "company_id": self.company.id,
            "provider": "traccar",
            "fix_time": fix_time,
            "latitude": -23.5,
            "longitude": -46.6,
        }
        # Point without position id, found by device, time and coordinates
        by_key = self.Telemetry.create(
            dict(base_values, traccar_device_id=device.id, speed=5)
        )
        # Point of another device, found by its position id
        by_id = self.Telemetry.create(
            dict(
                base_values,
                traccar_device_id=other_device.id,
                traccar_position_id=900,
                fix_time=fix_time + timedelta(hours=1),
            )
        )
        positions = [
            {
                "fixTime": "2026-01-10T10:00:00Z",
                "latitude": -23.5,
                "longitude": -46.6,
                "address": "Merged",
            },
            {
                "id": 900,
                "fixTime": "2026-01-10T11:00:00Z",
                "latitude": -23.5,
                "longitude": -46.6,
            },
            # New point without position id
            {"fixTime": "2026-01-10T12:00:00Z", "latitude": -23.6},
        ]
        created, updated = self.Telemetry._traccar_store_positions(
            self.company, device, positions
        )
        self.assertEqual((created, updated), (1, 2))
        self.assertEqual(by_key.address, "Merged")
        self.assertEqual(by_key.speed, 5)
        self.assertEqual(by_id.traccar_position_id, 900)

    def test_view_telemetry_with_map(self):
        map_view = self.env.ref(
            "fleet_traccar_integration.view_traccar_telemetry_search"
        )
        real_ref = type(self.env).ref

        def fake_ref(env, xml_id, raise_if_not_found=True):
            if xml_id == "fleet_telemetry_maps.view_fleet_telemetry_map":
                return map_view
            return real_ref(env, xml_id, raise_if_not_found=raise_if_not_found)

        with patch.object(type(self.env), "ref", fake_ref):
            action = self.vehicle.action_view_traccar_telemetry()
        self.assertEqual(action["view_mode"], "leaflet_map,list,form")
        self.assertEqual(action["views"][0], (map_view.id, "leaflet_map"))
