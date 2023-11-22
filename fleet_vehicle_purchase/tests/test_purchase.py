# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, SavepointCase


class TestPurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Audi",
            }
        )
        cls.model = cls.env["fleet.vehicle.model"].create(
            {
                "brand_id": cls.brand.id,
                "name": "A3",
            }
        )
        cls.car_1 = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.model.id,
                "driver_id": cls.env.user.partner_id.id,
                "plan_to_change_car": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "product",
                "type": "service",
            }
        )

    def test_purchase(self):
        self.assertEqual(0, self.car_1.purchase_order_count)
        order_action = self.car_1.action_view_purchase_orders()
        self.assertFalse(
            self.env[order_action["res_model"]].search(order_action["domain"])
        )
        with Form(self.env["purchase.order"]) as form:
            form.partner_id = self.env.user.partner_id
            form.fleet_vehicle_id = self.car_1
            with form.order_line.new() as form_line:
                form_line.product_id = self.product
                form_line.price_unit = 100
        self.assertEqual(1, self.car_1.purchase_order_count)
        purchase = form.save()
        self.assertEqual(
            purchase, self.env[order_action["res_model"]].search(order_action["domain"])
        )
        purchase.button_confirm()
        purchase.order_line.qty_received = 1
        invoice_action = purchase.action_create_invoice()
        invoice = self.env[invoice_action["res_model"]].browse(invoice_action["res_id"])
        invoice.invoice_date = fields.Date.today()
        self.assertTrue(invoice.invoice_line_ids.vehicle_id)
        self.assertFalse(self.car_1.log_services)
        invoice.action_post()
        self.assertTrue(self.car_1.log_services)
