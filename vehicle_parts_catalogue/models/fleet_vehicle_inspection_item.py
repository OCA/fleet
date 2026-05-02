from odoo import fields, models


class FleetVehicleInspectionItem(models.Model):
    _inherit = "fleet.vehicle.inspection.item"

    vehicle_part_ids = fields.One2many(
        "vehicle.part",
        "inspection_item_id",
        string="Vehicle Parts",
    )
