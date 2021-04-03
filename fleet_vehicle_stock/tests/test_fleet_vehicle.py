# Copyright (C) 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFleetVehicle(TransactionCase):

    def setUp(self):
        super(TestFleetVehicle, self).setUp()
        self.vehicle = self.env['fleet.vehicle']
        self.vehicle_model = self.env['fleet.vehicle.model']
        self.brand = self.env.ref('fleet.brand_opel')
        self.stock_location = self.env.ref('stock.stock_location_customers')
        self.product = self.env['product.template']

        self.vehicle_model = self.vehicle_model.create({
            'name': 'Test Vehicle Model',
            'brand_id': self.brand.id,
        })

        product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'fleet_vehicle_model_id': self.vehicle_model.id,
            'tracking': 'serial',
        })

        lot1 = self.env['stock.production.lot'].create({
            'name': 'serial1',
            'product_id': product1.id,
        })

        lot2 = self.env['stock.production.lot'].create({
            'name': 'serial2',
            'product_id': product1.id,
        })

        self.env['stock.quant'].create({
            'product_id': product1.id,
            'location_id': self.stock_location.id,
            'quantity': 1.0,
            'lot_id': lot1.id,
        })

        self.vehicle = self.vehicle.create({
            'model_id': self.vehicle_model.id,
            'product_id': product1.id,
            'lot_id': lot1.id,
            'current_stock_location_id': self.stock_location.id,
        })

        self.vehicle_without_quant = self.vehicle.create({
            'model_id': self.vehicle_model.id,
            'product_id': product1.id,
            'lot_id': lot2.id,
        })

        self.vehicle_without_lot_id = self.vehicle.create({
            'model_id': self.vehicle_model.id,
            'product_id': product1.id,
        })

        self.product2 = self.product.create({
            'name': 'Product B',
            'type': 'product',
            'fleet_vehicle_model_id': self.vehicle_model.id,
            'tracking': 'serial',
        })

    def test_onchange_product(self):
        vehicle = self.vehicle
        vehicle._onchange_product()
        self.assertFalse(vehicle.current_stock_location_id)

    def test_onchange_model(self):
        vehicle = self.vehicle
        vehicle._onchange_model()
        self.assertTrue(vehicle.product_id == vehicle.model_id.product_id)

    def test_compute_current_stock_loc_id(self):
        vehicle = self.vehicle
        vehicle._compute_current_stock_loc_id()
        self.assertTrue(vehicle.current_stock_location_id == self.stock_location)

        vehicle_without_quant = self.vehicle_without_quant
        vehicle_without_quant._compute_current_stock_loc_id()
        self.assertTrue(vehicle_without_quant.current_stock_location_id.id is False)

        vehicle_without_lot_id = self.vehicle_without_lot_id
        vehicle_without_lot_id._compute_current_stock_loc_id()
        self.assertTrue(vehicle_without_lot_id.current_stock_location_id.id is False)

    def test_set_fleet_vehicle_model_id(self):
        product2 = self.product2
        product2._set_fleet_vehicle_model_id()
        self.assertTrue(product2.product_variant_ids.fleet_vehicle_model_id ==
                        product2.fleet_vehicle_model_id)
