# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFleetVehicleAnalyticPurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.account = cls.env["account.analytic.account"].create(
            {"name": "Cost Center A", "plan_id": cls.plan.id}
        )
        cls.other_account = cls.env["account.analytic.account"].create(
            {"name": "Cost Center B", "plan_id": cls.plan.id}
        )
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Audi"})
        cls.model = cls.env["fleet.vehicle.model"].create(
            {"brand_id": cls.brand.id, "name": "A3"}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.model.id,
                "driver_id": cls.env.user.partner_id.id,
                "plan_to_change_car": False,
                "analytic_distribution": {str(cls.account.id): 100},
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "service"}
        )

    @classmethod
    def _create_purchase_order(cls, distribution):
        return cls.env["purchase.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_qty": 1.0,
                            "price_unit": 100.0,
                            "analytic_distribution": distribution,
                        },
                    )
                ],
            }
        )

    def test_purchase_order_count_without_orders(self):
        self.assertEqual(self.vehicle.purchase_order_count, 0)

    def test_purchase_order_count_without_analytic_distribution(self):
        self._create_purchase_order({str(self.account.id): 100})
        self.vehicle.analytic_distribution = False
        self.vehicle.invalidate_recordset(["purchase_order_count"])
        self.assertEqual(self.vehicle.purchase_order_count, 0)

    def test_purchase_order_count_and_action(self):
        order = self._create_purchase_order({str(self.account.id): 100})
        self._create_purchase_order({str(self.other_account.id): 100})
        self.vehicle.invalidate_recordset(["purchase_order_count"])
        self.assertEqual(self.vehicle.purchase_order_count, 1)
        action = self.vehicle.action_view_purchase_orders()
        self.assertEqual(self.env[action["res_model"]].search(action["domain"]), order)

    def test_purchase_order_count_multiple_analytic_accounts(self):
        self.vehicle.analytic_distribution = {
            str(self.account.id): 50,
            str(self.other_account.id): 50,
        }
        order_a = self._create_purchase_order({str(self.account.id): 100})
        order_b = self._create_purchase_order({str(self.other_account.id): 100})
        self.vehicle.invalidate_recordset(["purchase_order_count"])
        self.assertEqual(self.vehicle.purchase_order_count, 2)
        action = self.vehicle.action_view_purchase_orders()
        self.assertEqual(
            self.env[action["res_model"]].search(action["domain"]),
            order_a | order_b,
        )

    def test_search_vehicle_by_analytic_account(self):
        other_vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.model.id,
                "plan_to_change_car": False,
                "analytic_distribution": {str(self.other_account.id): 100},
            }
        )
        vehicles = self.env["fleet.vehicle"].search(
            [("distribution_analytic_account_ids", "=", self.account.id)]
        )
        self.assertIn(self.vehicle, vehicles)
        self.assertNotIn(other_vehicle, vehicles)
