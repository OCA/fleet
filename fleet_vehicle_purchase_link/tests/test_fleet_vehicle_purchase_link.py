# Copyright 2026 Escodoo - Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestFleetVehiclePurchaseLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        cls.model = cls.env["fleet.vehicle.model"].create(
            {"name": "Test model", "brand_id": cls.brand.id}
        )
        cls.car = cls.env["fleet.vehicle"].create({"model_id": cls.model.id})
        cls.other_car = cls.env["fleet.vehicle"].create({"model_id": cls.model.id})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "service"}
        )
        order_form = Form(cls.env["purchase.order"])
        order_form.partner_id = cls.env.user.partner_id
        order_form.fleet_vehicle_id = cls.car
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.price_unit = 100
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.price_unit = 200
        cls.order = order_form.save()

    def test_purchase_line_count(self):
        self.assertEqual(2, self.car.purchase_line_count)
        self.assertEqual(0, self.other_car.purchase_line_count)

    def test_view_purchase_lines(self):
        action = self.car.action_view_purchase_lines()
        self.assertEqual(
            self.order.order_line,
            self.env[action["res_model"]].search(action["domain"]),
        )
        self.assertEqual(self.car.id, action["context"]["default_fleet_vehicle_id"])

    def test_view_purchase_lines_without_purchases(self):
        action = self.other_car.action_view_purchase_lines()
        self.assertFalse(self.env[action["res_model"]].search(action["domain"]))
