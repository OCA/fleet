# Copyright 2026 Escodoo - Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    purchase_line_count = fields.Integer(
        string="Purchase Lines",
        compute="_compute_purchase_line_count",
    )

    def _compute_purchase_line_count(self):
        data = self.env["purchase.order.line"]._read_group(
            [("fleet_vehicle_id", "in", self.ids)],
            ["fleet_vehicle_id"],
            ["__count"],
        )
        mapped_data = {vehicle.id: count for vehicle, count in data}
        for vehicle in self:
            vehicle.purchase_line_count = mapped_data.get(vehicle.id, 0)

    def action_view_purchase_lines(self):
        self.ensure_one()
        return {
            "name": self.env._("Purchase Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.order.line",
            "view_mode": "list,form",
            "domain": [("fleet_vehicle_id", "=", self.id)],
            "context": {"default_fleet_vehicle_id": self.id},
        }
