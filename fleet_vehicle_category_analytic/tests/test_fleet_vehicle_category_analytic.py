# Copyright 2026 - Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestFleetVehicleCategoryAnalytic(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Analytic
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Default"})
        analytic_account_vehicle = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Vehicle",
                "plan_id": analytic_plan.id,
            }
        )
        analytic_account_other = analytic_account_vehicle.copy(
            {
                "name": "Analytic Other",
            }
        )
        cls.vehicle_key = str(analytic_account_vehicle.id)
        cls.other_key = str(analytic_account_other.id)

        # Fleet
        vehicle_brand = cls.env["fleet.vehicle.model.brand"].create(
            {"name": "TestBrand"}
        )
        vehicle_model = cls.env["fleet.vehicle.model"].create(
            {
                "name": "TestModel",
                "brand_id": vehicle_brand.id,
            }
        )
        cls.vehicle_category = cls.env["fleet.vehicle.category"].create(
            {
                "name": "Test Category",
                "analytic_account_id": analytic_account_vehicle.id,
            }
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "name": "Test Vehicle",
                "model_id": vehicle_model.id,
                "vehicle_category_id": cls.vehicle_category.id,
                "license_plate": "TEST-001",
            }
        )

    # Helpers
    def _create_vendor_bill(self, vehicle=None, analytic_distribution=None):
        """Return a draft vendor bill with one product line."""
        line_vals = {
            "name": "Test vehicle",
            "account_id": self.company_data["default_account_expense"].id,
            "quantity": 1,
            "price_unit": 100.0,
            "analytic_distribution": {self.other_key: 100},
        }
        if vehicle:
            line_vals["vehicle_id"] = vehicle.id
        if analytic_distribution:
            line_vals["analytic_distribution"] |= analytic_distribution
        move = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
                "invoice_line_ids": [Command.create(line_vals)],
            }
        )
        line = move.invoice_line_ids[0]
        if vehicle:
            # we need to force-compute: since we give 'analytic_distribution' at
            # line creation, _compute method is not called
            line._compute_analytic_distribution()
        return line

    # ====== Test cases =====#
    def test_analytic_cascading_from_vehicle_category(self):
        """Analytic should cascade from vehicle category to account move line
        without overwritten existing analytic distribution
        """
        line = self._create_vendor_bill(vehicle=self.vehicle)
        self.assertIn(self.vehicle_key, line.analytic_distribution)
        self.assertIn(self.other_key, line.analytic_distribution)

    def test_not_overwritten(self):
        """If the category account is already in the distribution (e.g. set
        manually), its percentage should not be overwritten"""
        line = self._create_vendor_bill(
            vehicle=self.vehicle,
            analytic_distribution={self.vehicle_key: 50},
        )
        self.assertEqual(line.analytic_distribution.get(self.vehicle_key), 50)

    def test_without_vehicle(self):
        """An account move line without a vehicle is not impacted"""
        line = self._create_vendor_bill()
        self.assertNotIn(self.vehicle_key, line.analytic_distribution)
        self.assertIn(self.other_key, line.analytic_distribution)

    def test_without_category_analytic(self):
        """A vehicle category without analytic should not modify anything"""
        self.vehicle_category.analytic_account_id = False
        line = self._create_vendor_bill(vehicle=self.vehicle)
        self.assertIn(self.other_key, line.analytic_distribution)
