# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    fleet_vehicle_model_id = fields.Many2one(
        "fleet.vehicle.model",
        string="Vehicle Model",
    )
