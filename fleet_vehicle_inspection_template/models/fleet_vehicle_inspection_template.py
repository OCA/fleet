# Copyright 2021 to TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleInspectionTemplate(models.Model):

    _name = "fleet.vehicle.inspection.template"
    _description = "Fleet Vehicle Inspection Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    note = fields.Html("Notes")
    inspection_template_line_ids = fields.One2many(
        "fleet.vehicle.inspection.template.line",
        "inspection_template_id",
        string="Inspection Template Lines",
        copy=True,
        auto_join=True,
    )
