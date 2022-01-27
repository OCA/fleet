# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    create_fleet_vehicle = fields.Boolean(
        name="Create Fleet Vehicle",
        help='Products with the "Creates a Fleet Vehicle" flag'
        "will automatically be converted to an Fleet Vehicle.",
    )
