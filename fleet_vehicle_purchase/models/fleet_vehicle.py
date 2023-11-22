# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    purchase_order_ids = fields.One2many(
        "purchase.order", inverse_name="fleet_vehicle_id"
    )
    purchase_order_count = fields.Integer(compute="_compute_purchase_order_count")

    @api.depends("purchase_order_ids")
    def _compute_purchase_order_count(self):
        for record in self:
            record.purchase_order_count = len(record.purchase_order_ids)

    def action_view_purchase_orders(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        result.update(
            {
                "domain": [("fleet_vehicle_id", "=", self.id)],
            }
        )
        return result
