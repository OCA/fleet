# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class FleetVehicleTyre(models.Model):
    _name = "fleet.vehicle.tyre"
    _description = "Vehicle Tyre"
    _order = "name"

    name = fields.Char(required=True)
    manufacturer = fields.Char()
    tyre_type = fields.Selection(
        selection=[
            ("summer", "Summer"),
            ("winter", "Winter"),
            ("all_season", "All Season"),
        ]
    )
    size = fields.Char(
        help="Tyre size marking, for example 205/55 R16.",
    )
    width = fields.Integer(string="Width (mm)")
    aspect_ratio = fields.Integer()
    rim_diameter = fields.Float(string="Rim Diameter (in)")
    load_index = fields.Char()
    speed_rating = fields.Char()
    run_flat = fields.Boolean()
    active = fields.Boolean(default=True)
