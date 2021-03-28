# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class FleetVehicleInspectionItem(models.Model):

    _inherit = 'fleet.vehicle.inspection.item'

    product_ids = fields.Many2many(
        "product.product",
        "fleet_vehicle_inspection_item_product_rel",
        "vehicle_inspection_item_id",
        "product_id",
        "Vehicle Products",
        domain=[("fleet_ok", "=", True)],
        help="Vehicle products that can be used to repair this inspection item",
    )
