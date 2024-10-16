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
        orders = self.env["purchase.order"].read_group(
            [("fleet_vehicle_id", "in", self.ids)],
            ["fleet_vehicle_id"],
            ["fleet_vehicle_id"],
        )
        mapped_data = {
            po["fleet_vehicle_id"][0]: po["fleet_vehicle_id_count"] for po in orders
        }
        for rec in self:
            rec.purchase_order_count = mapped_data.get(rec.id, 0)

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
