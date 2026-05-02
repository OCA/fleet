from odoo import fields, models


class VehiclePartSpecification(models.Model):
    _name = "vehicle.part.specification"
    _description = "Vehicle Part Specification"

    name = fields.Char(string="Código da Peça", required=True)
    group_id = fields.Many2one("vehicle.part.group", string="Group")
    category_id = fields.Many2one("vehicle.part.category", string="Category")
    product_ids = fields.Many2many(
        "product.template",
        "vehicle_part_spec_product_rel",
        "spec_id",
        "product_id",
        string="Products",
    )
