# Copyright (C) 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestFleetVehicle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env.ref("fleet.brand_opel")
        cls.stock_location = cls.env.ref("stock.stock_location_customers")

        cls.vehicle_model1 = cls.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model 1", "brand_id": cls.brand.id}
        )
        cls.vehicle_model2 = cls.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model 2", "brand_id": cls.brand.id}
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "is_storable": True,
                "type": "consu",
                "fleet_vehicle_model_id": cls.vehicle_model1.id,
                "tracking": "serial",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "is_storable": True,
                "type": "consu",
                "fleet_vehicle_model_id": cls.vehicle_model1.id,
                "tracking": "serial",
            }
        )

        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "serial1",
                "product_id": cls.product1.id,
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.lot2 = cls.env["stock.lot"].create(
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
        self.assertEqual(len(product2.product_variant_ids), 1)

        product2.fleet_vehicle_model_id = self.vehicle_model2
        self.assertEqual(
            product2.product_variant_ids.fleet_vehicle_model_id,
            product2.fleet_vehicle_model_id,
        )

    def test_create_product_template_with_model(self):
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Product Template With Model",
                "fleet_vehicle_model_id": self.vehicle_model1.id,
                "tracking": "serial",
            }
        )
        self.assertEqual(product_tmpl.fleet_vehicle_model_id, self.vehicle_model1)
        self.assertEqual(len(product_tmpl.product_variant_ids), 1)
        self.assertEqual(
            product_tmpl.product_variant_ids.fleet_vehicle_model_id, self.vehicle_model1
        )

    def test_stock_move_create_vehicle(self):
        picking_type = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type",
                "code": "incoming",
                "sequence_code": "TPT",
                "create_fleet_vehicle": True,
            }
        )
        self.product1.product_tmpl_id.create_fleet_vehicle = True

        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product1.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": picking_type.id,
            }
        )
        move._action_confirm()

        lot = self.env["stock.lot"].create(
            {
                "name": "new_serial",
                "product_id": self.product1.id,
                "company_id": self.env.user.company_id.id,
            }
        )

        move.move_line_ids.write({"quantity": 1.0, "lot_id": lot.id})

        move.picked = True
        move._action_done()

        self.assertTrue(lot.fleet_vehicle_id)
        self.assertEqual(lot.fleet_vehicle_id.model_id, self.vehicle_model1)
        self.assertEqual(lot.fleet_vehicle_id.product_id, self.product1)
        self.assertEqual(
            lot.fleet_vehicle_id.current_stock_location_id, self.stock_location
        )

    def test_stock_move_skip_vehicle_creation(self):
        picking_type_no_create = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type No Create",
                "code": "incoming",
                "sequence_code": "TPTNC",
                "create_fleet_vehicle": False,
            }
        )
        self.product1.product_tmpl_id.create_fleet_vehicle = True

        move1 = self.env["stock.move"].create(
            {
                "name": "Test Move Skip 1",
                "product_id": self.product1.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": picking_type_no_create.id,
            }
        )
        move1._action_confirm()
        lot1 = self.env["stock.lot"].create(
            {
                "name": "serial_skip_1",
                "product_id": self.product1.id,
                "company_id": self.env.user.company_id.id,
            }
        )
        move1.move_line_ids.write({"quantity": 1.0, "lot_id": lot1.id})
        move1.picked = True
        move1._action_done()
        self.assertFalse(
            lot1.fleet_vehicle_id,
            "Vehicle should not be created if picking type disabled",
        )

        picking_type_create = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type Create",
                "code": "incoming",
                "sequence_code": "TPTC",
                "create_fleet_vehicle": True,
            }
        )
        self.product1.product_tmpl_id.create_fleet_vehicle = False

        move2 = self.env["stock.move"].create(
            {
                "name": "Test Move Skip 2",
                "product_id": self.product1.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": picking_type_create.id,
            }
        )
        move2._action_confirm()
        lot2 = self.env["stock.lot"].create(
            {
                "name": "serial_skip_2",
                "product_id": self.product1.id,
                "company_id": self.env.user.company_id.id,
            }
        )
        move2.move_line_ids.write({"quantity": 1.0, "lot_id": lot2.id})
        move2.picked = True
        move2._action_done()
        self.assertFalse(
            lot2.fleet_vehicle_id,
            "Vehicle should not be created if product template disabled",
        )

    def test_create_fleet_vehicle_updates_lot(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "serial_vehicle_create",
                "product_id": self.product1.id,
                "company_id": self.env.user.company_id.id,
            }
        )

        vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model1.id,
                "product_id": self.product1.id,
                "lot_id": lot.id,
            }
        )

        self.assertEqual(
            lot.fleet_vehicle_id, vehicle, "Lot should be linked to the created vehicle"
        )

    def test_create_fleet_vehicle_no_lot(self):
        vehicle1 = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model1.id,
                "product_id": self.product1.id,
            }
        )
        self.assertFalse(vehicle1.lot_id, "Vehicle should have no lot")
        vehicle2 = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model1.id,
                "product_id": self.product1.id,
                "lot_id": False,
            }
        )
        self.assertFalse(vehicle2.lot_id, "Vehicle should have no lot")

    def test_stock_move_error(self):
        product_no_model = self.env["product.product"].create(
            {
                "name": "Product No Model",
                "is_storable": True,
                "create_fleet_vehicle": True,
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": "Test Move Error",
                "product_id": product_no_model.id,
                "product_uom_qty": 1.0,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock_location.id,
            }
        )

        with self.assertRaises(UserError):
            move._action_done()
