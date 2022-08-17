# Copyright (C) 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestFleetVehicle(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFleetVehicle, cls).setUpClass()
        cls.brand = cls.env.ref("fleet.brand_opel")
        cls.stock_location = cls.env.ref("stock.stock_location_customers")

        cls.vehicle_model1 = cls.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model 1", "brand_id": cls.brand.id}
        )
        cls.vehicle_model2 = cls.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model 2", "brand_id": cls.brand.id}
        )

        cls.product1 = cls.env["product.template"].create(
            {
                "name": "Product 1",
                "type": "product",
                "fleet_vehicle_model_id": cls.vehicle_model1.id,
                "tracking": "serial",
            }
        )
        cls.product2 = cls.env["product.template"].create(
            {
                "name": "Product 2",
                "type": "product",
                "fleet_vehicle_model_id": cls.vehicle_model1.id,
                "tracking": "serial",
            }
        )

        cls.lot1 = cls.env["stock.production.lot"].create(
            {
                "name": "serial1",
                "product_id": cls.product1.id,
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.lot2 = cls.env["stock.production.lot"].create(
            {
                "name": "serial2",
                "product_id": cls.product1.id,
                "company_id": cls.env.user.company_id.id,
            }
        )

        cls.quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product1.id,
                "location_id": cls.stock_location.id,
                "quantity": 1.0,
                "lot_id": cls.lot1.id,
            }
        )

        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.vehicle_model1.id,
                "product_id": cls.product1.id,
                "lot_id": cls.lot1.id,
            }
        )

    def test_onchange_product(self):
        vehicle = self.vehicle
        vehicle._onchange_product()
        self.assertFalse(vehicle.current_stock_location_id)

    def test_onchange_model(self):
        vehicle = self.vehicle
        vehicle._onchange_model()
        self.assertEqual(vehicle.product_id, vehicle.model_id.product_id)

    def test_compute_current_stock_loc_id(self):
        vehicle = self.vehicle
        self.assertEqual(vehicle.current_stock_location_id, self.stock_location)

        vehicle.lot_id = self.lot2
        self.assertTrue(vehicle.current_stock_location_id.id is False)

        vehicle.lot_id = False
        self.assertTrue(vehicle.current_stock_location_id.id is False)

    def test_inverse_fleet_vehicle_model_id(self):
        product2 = self.product2
        product2.fleet_vehicle_model_id = self.vehicle_model2
        self.assertEqual(
            product2.product_variant_ids.fleet_vehicle_model_id,
            product2.fleet_vehicle_model_id,
        )
