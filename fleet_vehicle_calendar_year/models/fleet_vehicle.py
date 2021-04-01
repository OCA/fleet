# Copyright 2021 - TODAY, Marcel Savegnago
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'

    calendar_year = fields.Char(
        'Calendar Year',
        track_visibility="onchange",
        help='Calendar year of the vehicle'
    )
