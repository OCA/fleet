from odoo import fields, models


class VehiclePart(models.Model):
    _name = "vehicle.part"
    _description = "Vehicle Part"
    vehicle_model_id = fields.Many2one("fleet.vehicle.model", string="Vehicle Model", required=True)
    inspection_item_id = fields.Many2one("fleet.vehicle.inspection.item", string="Inspection Item", required=True)
    name = fields.Char(related="vehicle_model_id.name", store=True, readonly=True, string="Model Name")
    specification_id = fields.Many2one("vehicle.part.specification", string="Especificação", required=True)
    part_number = fields.Char(related="specification_id.name", string="Código da Peça", store=True, readonly=False)
    qty = fields.Integer(string="Quantidade Aplicada", default=1)
    group_id = fields.Many2one("vehicle.part.group", related="specification_id.group_id", string="Group", store=True, readonly=False)
    category_id = fields.Many2one("vehicle.part.category", related="specification_id.category_id", string="Category", store=True, readonly=False)
    product_ids = fields.Many2many(
        related="specification_id.product_ids",
        string="Products",
        readonly=False,
    )
