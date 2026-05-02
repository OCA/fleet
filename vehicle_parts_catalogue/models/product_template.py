from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    vehicle_part_ids = fields.Many2many(
        "vehicle.part",
        "vehicle_part_product_rel",
        "product_id",
        "part_id",
        string="Vehicle Parts",
    )
