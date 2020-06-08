# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestVehicleLicensePlatAlt(TransactionCase):
    def setUp(self):
        super().setUp()
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "license_plate_alt": "1-ACK-556",
                "vin_sn": "883333",
                "color": "Black",
                "location": "Grand-Rosiere",
                "doors": 5,
                "driver_id": self.env.ref("base.user_demo_res_partner").id,
                "odometer_unit": "kilometers",
                "car_value": 20000,
                "model_id": self.env.ref("fleet.model_astra").id,
            }
        )

    def test_search_vehicle_by_license_plate_alt(self):
        """Check correct searching of vehicles by license_plate_alt."""
        vehicle_search = self.env["fleet.vehicle"].name_search("1-ACK-556")
        self.assertEqual(vehicle_search[0][1], self.vehicle.display_name)
