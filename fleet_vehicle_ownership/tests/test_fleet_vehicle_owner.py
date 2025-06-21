from odoo.tests import TransactionCase


class TestFleetVehicleOwner(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create necessary test data here, such as a partner and vehicles
        self.partner = self.env["res.partner"].create(
            {
                "name": "Lewis Hamilton",
            }
        )
        self.vehicle1 = self.env["fleet.vehicle"].create(
            {
                "license_plate": "1-ACK-554",
                "vin_sn": "8833334",
                "color": "Black",
                "location": "Grand-Rosiere",
                "doors": 5,
                "driver_id": self.partner.id,
                "owner_id": self.partner.id,
                "odometer_unit": "kilometers",
                "car_value": 20000,
                "model_id": self.env.ref("fleet.model_astra").id,
            }
        )
        self.vehicle2 = self.env["fleet.vehicle"].create(
            {
                "license_plate": "1-ACK-544",
                "vin_sn": "8833332",
                "color": "Black",
                "location": "Grand-Rosiere",
                "doors": 5,
                "driver_id": self.partner.id,
                "owner_id": self.partner.id,
                "odometer_unit": "kilometers",
                "car_value": 30000,
                "model_id": self.env.ref("fleet.model_astra").id,
            }
        )

    def test_compute_vehicle_count(self):
        # Check if the vehicle count is computed correctly,
        # test starts with test partner owing 2 vehucles
        self.assertEqual(self.partner.vehicle_count, 2, "Vehicle count is incorrect")

    def test_action_view_vehicles(self):
        # Check if action_view_vehicles method returns the correct action
        action = self.partner.action_view_vehicles()

        # Assert that the action is correctly configured
        self.assertEqual(
            action["res_model"], "fleet.vehicle", "Incorrect res_model in action"
        )
        self.assertEqual(action["name"], "Vehicles", "Incorrect name in action")

        # Test when there is more than one vehicle
        action = self.partner.action_view_vehicles()
        self.assertTrue(
            action["domain"],
            "Incorrect domain when multiple vehicles",
        )

        # Test when there is only one vehicle
        self.vehicle2.owner_id = None
        action = self.partner.action_view_vehicles()
        self.assertEqual(
            action["views"],
            [(self.env.ref("fleet.fleet_vehicle_view_form").id, "form")],
            "Incorrect views when only one vehicle",
        )
        self.assertEqual(
            action["res_id"],
            self.partner.vehicle_ids.ids[0],
            "Incorrect res_id when only one vehicle",
        )
