# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MaintenanceEquipment(models.Model):

    _inherit = 'maintenance.equipment'

    is_fleet_vehicle = fields.Boolean(string='Is a Fleet Vehicle')
