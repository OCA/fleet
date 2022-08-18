# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleModel(models.Model):

    _inherit = "fleet.vehicle.model"

    product_id = fields.Many2one(
        "product.product",
        string="Default Product",
    )
