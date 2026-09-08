# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _name = "fleet.vehicle"
    _inherit = ["fleet.vehicle", "analytic.mixin"]

    purchase_order_count = fields.Integer(
        string="Purchase Orders",
        compute="_compute_purchase_order_count",
    )

    @api.depends("distribution_analytic_account_ids")
    def _compute_purchase_order_count(self):
        self.purchase_order_count = 0
        vehicles = self.filtered("distribution_analytic_account_ids")
        if not vehicles:
            return
        lines = self.env["purchase.order.line"].search(
            [
                (
                    "distribution_analytic_account_ids",
                    "in",
                    vehicles.distribution_analytic_account_ids.ids,
                )
            ]
        )
        orders_per_account = defaultdict(set)
        for line in lines:
            for account in line.distribution_analytic_account_ids:
                orders_per_account[account.id].add(line.order_id.id)
        for vehicle in vehicles:
            order_ids = set()
            for account in vehicle.distribution_analytic_account_ids:
                order_ids |= orders_per_account[account.id]
            vehicle.purchase_order_count = len(order_ids)

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        action.update(
            {
                "domain": [
                    (
                        "order_line.distribution_analytic_account_ids",
                        "in",
                        self.distribution_analytic_account_ids.ids,
                    )
                ],
            }
        )
        return action
