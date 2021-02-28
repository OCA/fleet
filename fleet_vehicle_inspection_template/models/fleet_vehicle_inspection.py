# Copyright 2021 to TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicleInspection(models.Model):

    _inherit = "fleet.vehicle.inspection"

    inspection_template_id = fields.Many2one(
        "fleet.vehicle.inspection.template", string="Inspection Template"
    )

    def _compute_line_data_for_template_change(self, line):
        return {
            "inspection_item_id": line.inspection_template_item_id.id,
            "state": "draft",
        }

    @api.onchange("inspection_template_id")
    def _onchange_inspection_template_id(self):
        if self.inspection_template_id:
            self.name = self.inspection_template_id.name
            self.note = self.inspection_template_id.note

            inspection_lines = [(5, 0, 0)]
            for line in self.inspection_template_id.inspection_template_line_ids:
                data = self._compute_line_data_for_template_change(line)
                inspection_lines.append((0, 0, data))

            self.inspection_line_ids = inspection_lines
