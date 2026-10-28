# Copyright 2020 - 2024, Marcel Savegnago - Escodoo https://www.escodoo.com.br
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
        return self.inspection_ids._get_records_action(
            name=self.env._("Vehicle Inspection")
        )
