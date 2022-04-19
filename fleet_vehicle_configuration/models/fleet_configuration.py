# Copyright 2022 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class FleetVehicleConfiguration(models.Model):
    _name = "fleet.vehicle.configuration"
    _description = "Manage vehicle configuration"

    vehicle_id = fields.Many2one("fleet.vehicle", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    max_seats = fields.Integer(default=10)
    sequence = fields.Integer(default=10)
