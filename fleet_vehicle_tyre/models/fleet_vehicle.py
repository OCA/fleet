# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    vehicle_tyre_id = fields.Many2one(comodel_name="fleet.vehicle.tyre")
    last_tyre_change_date = fields.Date()
