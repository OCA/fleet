# Copyright 2026 Escodoo - Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    purchase_line_count = fields.Integer(
        string="Purchase Lines",
        compute="_compute_purchase_line_count",
    )

    def _compute_purchase_line_count(self):
        line_model = self.env["purchase.order.line"]
        data = line_model.read_group(
            [("fleet_vehicle_id", "in", self.ids)],
            ["fleet_vehicle_id"],
            ["fleet_vehicle_id"],
        )
        mapped_data = {
            item["fleet_vehicle_id"][0]: item["fleet_vehicle_id_count"] for item in data
        }
        for vehicle in self:
            vehicle.purchase_line_count = mapped_data.get(vehicle.id, 0)

    def action_view_purchase_lines(self):
        self.ensure_one()
        return {
            "name": _("Purchase Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.order.line",
            "view_mode": "tree,form",
            "domain": [("fleet_vehicle_id", "=", self.id)],
            "context": {"default_fleet_vehicle_id": self.id},
        }
