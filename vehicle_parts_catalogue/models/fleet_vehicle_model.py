from odoo import fields, models


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    part_ids = fields.One2many(
        "vehicle.part",
        "vehicle_model_id",
        string="Vehicle Parts",
    )
