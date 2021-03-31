# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'

    description = fields.Text("Vehicle Description", translate=True)
    fuel_capacity = fields.Float(
        string='Fuel Capacity(l)',
        track_visibility='onchange'
    )
    calendar_year = fields.Char(
        'Calendar Year',
        track_visibility="onchange",
        help='Calendar year of the model'
    )
    fuel_type = fields.Selection(selection_add=[
        ('ethanol', 'Ethanol'),
        ('flex', 'Flex (Gasoline/Ethanol)'),
    ])
