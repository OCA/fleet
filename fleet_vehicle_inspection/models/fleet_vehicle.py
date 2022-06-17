# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    inspection_ids = fields.One2many(
        "fleet.vehicle.inspection", "vehicle_id", "Inspection Logs"
    )

    inspection_count = fields.Integer(
        compute="_compute_inspection_count", string="# Inspection Count"
    )

    @api.depends("inspection_ids")
    def _compute_inspection_count(self):
        for rec in self:
            rec.inspection_count = len(rec.inspection_ids)

    def action_view_inspection(self):
        action = (
            self.env.ref("fleet_vehicle_inspection.fleet_vehicle_inspection_act_window")
            .sudo()
            .read()[0]
        )
        if self.inspection_count > 1:
            action["domain"] = [("id", "in", self.inspection_ids.ids)]
        else:
            action["views"] = [
                (
                    self.env.ref(
                        "fleet_vehicle_inspection.fleet_vehicle_inspection_form_view"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = (
                self.inspection_ids and self.inspection_ids.ids[0] or False
            )
        return action
