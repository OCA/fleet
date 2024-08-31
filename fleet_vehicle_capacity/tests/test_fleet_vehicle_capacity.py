# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestFleetVehicleCapacity(common.TransactionCase):
    def setUp(self):
        super(TestFleetVehicleCapacity, self).setUp()

        # References to standard UOMs
        self.uom_ton = self.env.ref("uom.product_uom_ton")
        self.uom_m3 = self.env.ref("uom.product_uom_cubic_meter")
        self.uom_unit = self.env.ref("uom.product_uom_unit")

        # Create default configuration settings
        self.res_config_settings = self.env["res.config.settings"].create(
            {
                "vehicle_weight_uom_id": self.uom_ton.id,
                "vehicle_volume_uom_id": self.uom_m3.id,
                "vehicle_passenger_uom_id": self.uom_unit.id,
            }
        )
        self.res_config_settings.execute()

        # Create a vehicle brand (fleet.model.brand)
        self.vehicle_brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Test Brand",  # Name of the brand
            }
        )

        # Create a vehicle model and associate it with the brand
        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {
                "name": "Test Model",
                "vehicle_weight": 5.0,
                "weight_capacity": 2.0,
                "volume_capacity": 10.0,
                "passenger_capacity": 4.0,
                "brand_id": self.vehicle_brand.id,  # Associate with the created brand
            }
        )

    def test_default_vehicle_weight_uom(self):
        """Test if the default vehicle weight UOM is correctly applied."""
        self.assertEqual(
            self.vehicle_model.weight_uom_id,
            self.uom_ton,
            "Default Vehicle Weight UOM is incorrect",
        )

    def test_default_vehicle_volume_uom(self):
        """Test if the default vehicle volume UOM is correctly applied."""
        self.assertEqual(
            self.vehicle_model.volume_uom_id,
            self.uom_m3,
            "Default Vehicle Volume UOM is incorrect",
        )

    def test_default_vehicle_passenger_uom(self):
        """Test if the default vehicle passenger UOM is correctly applied."""
        self.assertEqual(
            self.vehicle_model.passenger_uom_id,
            self.uom_unit,
            "Default Vehicle Passenger UOM is incorrect",
        )

    def test_vehicle_model_fields(self):
        """Test if the vehicle model fields are correctly set."""
        self.assertEqual(
            self.vehicle_model.vehicle_weight, 5.0, "Vehicle weight is incorrect"
        )
        self.assertEqual(
            self.vehicle_model.weight_capacity, 2.0, "Weight capacity is incorrect"
        )
        self.assertEqual(
            self.vehicle_model.volume_capacity, 10.0, "Volume capacity is incorrect"
        )
        self.assertEqual(
            self.vehicle_model.passenger_capacity,
            4.0,
            "Passenger capacity is incorrect",
        )

    def test_vehicle_model_brand(self):
        """Test if the vehicle model is correctly associated with the brand."""
        self.assertEqual(
            self.vehicle_model.brand_id,
            self.vehicle_brand,
            "Vehicle brand is incorrect",
        )
