# Copyright 2021 to TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleInspectionTemplateLine(models.Model):

    _name = "fleet.vehicle.inspection.template.line"
    _description = "Fleet Vehicle Inspection Template Line"

    inspection_template_id = fields.Many2one(
        "fleet.vehicle.inspection.template",
        string="Inspection Template Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )

    inspection_template_item_id = fields.Many2one(
        "fleet.vehicle.inspection.item",
        "Inspection Template Item",
        required=True,
        copy=True,
    )
