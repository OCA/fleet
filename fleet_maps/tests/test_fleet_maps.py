from datetime import datetime
from unittest.mock import patch

from .common import FleetMapsCommon


class TestFleetMaps(FleetMapsCommon):
    def test_get_map_position_values_default(self):
        values = self.vehicle._get_map_position_values()
        self.assertFalse(values["latitude"])
        self.assertFalse(values["longitude"])
        self.assertFalse(values["last_update"])
        self.assertEqual(values["title"], self.vehicle.name)
        self.assertEqual(values["address"], "MAP123")

    def test_compute_map_position_defaults(self):
        self.vehicle._compute_map_position()
        self.assertEqual(self.vehicle.map_latitude, 0)
        self.assertEqual(self.vehicle.map_longitude, 0)
        self.assertFalse(self.vehicle.map_has_position)
        self.assertEqual(self.vehicle.map_marker_title, self.vehicle.name)
        self.assertEqual(self.vehicle.map_marker_address, "MAP123")

    def test_map_preview_without_position(self):
        self.vehicle._compute_map_preview()
        self.assertFalse(self.vehicle.map_url)
        self.assertIn("No map position available", self.vehicle.map_preview_html)

    def test_map_preview_with_position(self):
        position = {
            "latitude": -23.5505199,
            "longitude": -46.6333094,
            "title": "Test vehicle",
            "address": "Sao Paulo",
            "last_update": datetime(2026, 1, 10, 10, 0),
        }
        with patch.object(
            type(self.vehicle),
            "_get_map_position_values",
            lambda *args: dict(position),
        ):
            self.vehicle.license_plate = "MAP999"
            self.vehicle._compute_map_position()
            self.assertEqual(self.vehicle.map_latitude, position["latitude"])
            self.assertEqual(self.vehicle.map_longitude, position["longitude"])
            self.assertTrue(self.vehicle.map_has_position)
            self.assertEqual(self.vehicle.map_last_update, position["last_update"])
            self.vehicle._compute_map_preview()
            self.assertIn("-23.5505199", self.vehicle.map_url)
            self.assertIn("-46.6333094", self.vehicle.map_url)
            self.assertIn(
                "openstreetmap.org/export/embed.html",
                self.vehicle.map_preview_html,
            )
            self.assertIn("Open in OpenStreetMap", self.vehicle.map_preview_html)

    def test_actions(self):
        action = self.vehicle.action_view_fleet_map()
        self.assertEqual(action["res_model"], "fleet.vehicle")
        self.assertIn("leaflet_map", action["view_mode"])
        vehicle_action = self.vehicle.action_view_vehicle_map()
        self.assertEqual(vehicle_action["res_id"], self.vehicle.id)
        self.assertEqual(vehicle_action["domain"][0], ("id", "=", self.vehicle.id))

    def test_data_records(self):
        self.assertTrue(self.env.ref("fleet_maps.action_fleet_vehicle_map"))
        self.assertTrue(self.env.ref("fleet_maps.menu_fleet_vehicle_map"))
        self.assertTrue(self.env.ref("fleet_maps.view_fleet_vehicle_leaflet_map"))
        self.assertTrue(self.env.ref("fleet_maps.fleet_vehicle_view_form_maps"))
