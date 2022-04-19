# Copyright 2022 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    configuration_ids = fields.One2many(
        "fleet.vehicle.configuration",
        "vehicle_id",
        string="Configurations",
        help="Define several configurations for a vehicle",
    )
