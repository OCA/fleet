# models/fleet_vehicle_model_inspection_plan.py
from odoo import fields, models


class FleetVehicleModelInspectionPlan(models.Model):
    _name = "fleet.vehicle.model.inspection.plan"
    _description = "Vehicle Model Inspection Plan Line"

    model_id = fields.Many2one(
        comodel_name="fleet.vehicle.model",
        string="Vehicle Model",
        required=True,
        ondelete="cascade",
    )

    # Este campo vem do módulo da OCA fleet_vehicle_inspection
    item_id = fields.Many2one(
        comodel_name="fleet.vehicle.inspection.item",
        string="Inspection Item",
        required=True,
    )

    interval_km = fields.Integer(
        string="Interval (KM)",
        help="Interval in kilometers between inspections for this item.",
        default=10000,
    )

    criticality = fields.Selection(
        [("baixa", "Baixa"), ("media", "Média"), ("alta", "Alta")],
        string="Criticidade",
        default="alta",
        required=True,
    )

    interval_months = fields.Integer(
        string="Interval (Months)",
        help="Interval in months between inspections for this item.",
        default=12,
    )
