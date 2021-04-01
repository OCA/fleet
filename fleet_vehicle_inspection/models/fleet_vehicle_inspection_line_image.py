# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleInspectionLineImage(models.Model):

    _name = "fleet.vehicle.inspection.line.image"
    _description = "Fleet Vehicle Inspection Line Image"
    _order = "sequence, id"

    name = fields.Char('Name')
    sequence = fields.Integer(default=10, index=True)
    image_1920 = fields.Binary('Image', attachment=True, required=True)
    inspection_line_id = fields.Many2one(
        "fleet.vehicle.inspection.line", "Related Inspection Line", copy=True
    )
