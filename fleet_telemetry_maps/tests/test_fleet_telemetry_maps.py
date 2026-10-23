from .common import FleetTelemetryMapsCommon


class TestFleetTelemetryMaps(FleetTelemetryMapsCommon):
    def test_compute_map_fields_with_device(self):
        telemetry = self._create_telemetry(address="Somewhere")
        telemetry._compute_map_fields()
        self.assertEqual(
            telemetry.map_marker_title,
            f"{self.device.display_name} - 2026-01-10 10:00:00",
        )
        self.assertEqual(telemetry.map_marker_address, "Somewhere")

    def test_compute_map_fields_without_address(self):
        telemetry = self._create_telemetry(address=False, speed=42.0)
        telemetry._compute_map_fields()
        self.assertEqual(telemetry.map_marker_address, "Speed: 42.0")

    def test_route_color_groups_by_day(self):
        first = self._create_telemetry()
        second = self._create_telemetry(external_position_ref="POS-2", speed=10)
        third = self._create_telemetry(
            external_position_ref="POS-3",
            fix_time="2026-01-11 10:00:00",
            latitude=-23.0,
            longitude=-46.0,
        )
        self.assertTrue(first.route_color.startswith("#"))
        self.assertEqual(first.route_color, second.route_color)
        self.assertNotEqual(first.route_color, third.route_color)

    def test_vehicle_map_position_from_telemetry(self):
        telemetry = self._create_telemetry(address="Somewhere")
        self.vehicle._compute_map_position()
        self.assertTrue(self.vehicle.map_has_position)
        self.assertAlmostEqual(self.vehicle.map_latitude, telemetry.latitude)
        self.assertAlmostEqual(self.vehicle.map_longitude, telemetry.longitude)
        values = self.vehicle._get_map_position_values()
        self.assertEqual(values["address"], "Somewhere")

    def test_vehicle_map_position_without_telemetry(self):
        values = self.vehicle._get_map_position_values()
        self.assertFalse(values["latitude"])
        self.assertFalse(values["longitude"])

    def test_write_recomputes_vehicle_position(self):
        telemetry = self._create_telemetry()
        telemetry.write({"latitude": -10.0, "longitude": -20.0})
        self.vehicle._compute_map_position()
        self.assertAlmostEqual(self.vehicle.map_latitude, -10.0)
        self.assertAlmostEqual(self.vehicle.map_longitude, -20.0)

    def test_data_records(self):
        self.assertTrue(self.env.ref("fleet_telemetry_maps.view_fleet_telemetry_map"))
        self.assertTrue(self.env.ref("fleet_telemetry_maps.menu_fleet_telemetry_map"))
        self.assertEqual(
            self.env["ir.config_parameter"].sudo().get_param("leaflet.tile_url"),
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        )
