# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    compatible_vehicle_model_ids = fields.Many2many(
        "fleet.vehicle.model",
        "fleet_vehicle_model_compatible_product_rel",
        "product_id",
        "model_id",
        "Compatible Vehicle Models",
    )
