# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    vehicle_weight_uom_id = fields.Many2one(
        "uom.uom",
        string="Default Vehicle Weight and Capacity UOM",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id),
        ],
        default=lambda self: self._default_vehicle_weight_uom_id(),
        help="Default Unit of measure for vehicle weight and capacity.",
        default_model="res.config.settings",
        config_parameter="fleet.default_vehicle_weight_uom_id",
    )

    vehicle_volume_uom_id = fields.Many2one(
        "uom.uom",
        string="Default Vehicle Volume Capacity UOM",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id),
        ],
        default=lambda self: self._default_vehicle_volume_uom_id(),
        help="Default Unit of measure for vehicle volume capacity.",
        default_model="res.config.settings",
        config_parameter="fleet.default_vehicle_volume_uom_id",
    )

    vehicle_passenger_uom_id = fields.Many2one(
        "uom.uom",
        string="Default Vehicle Passenger Capacity UOM",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_unit").id),
        ],
        default=lambda self: self._default_vehicle_passenger_uom_id(),
        help="Default Unit of measure for vehicle passenger capacity.",
        default_model="res.config.settings",
        config_parameter="fleet.default_vehicle_passenger_uom_id",
    )

    @api.model
    def _default_vehicle_weight_uom_id(self):
        """Method to find and return the default UOM for vehicle weight and capacity."""
        uom = self.env["uom.uom"].search(
            [
                ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id),
                ("uom_type", "=", "bigger"),
            ],
            limit=1,
            order="id",
        )
        return uom.id if uom else False

    @api.model
    def _default_vehicle_volume_uom_id(self):
        """Method to find and return the default UOM for vehicle volume capacity."""
        uom = self.env["uom.uom"].search(
            [
                ("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id),
                ("uom_type", "=", "bigger"),
            ],
            limit=1,
            order="id",
        )
        return uom.id if uom else False

    @api.model
    def _default_vehicle_passenger_uom_id(self):
        """Method to find and return the default UOM for vehicle passenger capacity."""
        uom = self.env["uom.uom"].search(
            [
                ("category_id", "=", self.env.ref("uom.product_uom_categ_unit").id),
                ("uom_type", "=", "reference"),
            ],
            limit=1,
            order="id",
        )
        return uom.id if uom else False
