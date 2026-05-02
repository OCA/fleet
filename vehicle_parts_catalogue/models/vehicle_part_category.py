from odoo import fields, models


class VehiclePartCategory(models.Model):
    _name = "vehicle.part.category"
    _description = "Vehicle Part Category"

    name = fields.Char(string="Category Name", required=True)
