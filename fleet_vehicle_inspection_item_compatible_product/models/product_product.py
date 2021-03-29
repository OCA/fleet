# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    vehicle_inspection_item_ids = fields.Many2many(
        "fleet.vehicle.inspection.item",
        "fleet_vehicle_inspection_item_compatible_product_rel",
        "product_id",
        "vehicle_inspection_item_id",
        "Vehicle Inspection Itens",
        help="Compatible Vehicle Inspection Items",
    )
