# Copyright 2023 RPSJR
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    owner_id = fields.Many2one(
        "res.partner",
        "Owner",
        index=True,
        tracking=True,
        help="Owner of the vehicle",
        copy=False,
    )
