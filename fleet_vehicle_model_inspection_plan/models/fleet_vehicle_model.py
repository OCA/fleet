from odoo import fields, models


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    inspection_plan_ids = fields.One2many(
        comodel_name="fleet.vehicle.model.inspection.plan",
        inverse_name="model_id",
        string="Inspection Plan",
    )
