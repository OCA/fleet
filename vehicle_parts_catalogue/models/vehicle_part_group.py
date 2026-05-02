from odoo import fields, models


class VehiclePartGroup(models.Model):
    _name = "vehicle.part.group"
    _description = "Vehicle Part Group"

    name = fields.Char(string="Group Name", required=True)
