# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    fleet_vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Fleet Vehicle",
        readonly=True,
    )
