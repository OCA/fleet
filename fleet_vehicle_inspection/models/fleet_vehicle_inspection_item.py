# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleInspectionItem(models.Model):

    _name = "fleet.vehicle.inspection.item"
    _description = "Fleet Vehicle Inspection Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    instruction = fields.Text(string="Instruction")
