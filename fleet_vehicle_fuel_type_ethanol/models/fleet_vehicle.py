# Copyright 2021 - TODAY, Marcel Savegnago
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'

    fuel_type = fields.Selection(selection_add=[
        ('ethanol', 'Ethanol'),
        ('flex', 'Flex (Gasoline/Ethanol)'),
    ])
