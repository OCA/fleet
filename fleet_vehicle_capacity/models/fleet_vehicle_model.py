# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    vehicle_weight = fields.Float(
        string="Vehicle Weight", help="The weight of the vehicle."
    )

    weight_capacity = fields.Float(
        string="Weight Capacity",
        help="The maximum weight capacity the vehicle can support.",
    )

    volume_capacity = fields.Float(
        string="Volume Capacity",
        help="The maximum volume capacity the vehicle can support.",
    )

    passenger_capacity = fields.Float(
        string="Passenger Capacity",
        help="The maximum passenger capacity the vehicle can support.",
    )

    def _get_vehicle_weight_uom_id_from_ir_config_parameter(self):
        uom_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fleet.default_vehicle_weight_uom_id")
        )
        if uom_id:
            try:
                return int(uom_id)
            except ValueError:
                _logger.error("Invalid Vehicle Weight UOM ID format: %s", uom_id)
                return False
        else:
            return self.env["res.config.settings"]._default_vehicle_weight_uom_id()

    def _get_vehicle_volume_uom_id_from_ir_config_parameter(self):
        uom_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fleet.default_vehicle_volume_uom_id")
        )
        if uom_id:
            try:
                return int(uom_id)
            except ValueError:
                _logger.error("Invalid Vehicle Volume UOM ID format: %s", uom_id)
                return False
        else:
            return self.env["res.config.settings"]._default_vehicle_volume_uom_id()

    def _get_vehicle_passenger_uom_id_from_ir_config_parameter(self):
        uom_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fleet.default_vehicle_passenger_uom_id")
        )
        if uom_id:
            try:
                return int(uom_id)
            except ValueError:
                _logger.error("Invalid Vehicle Passenger UOM ID format: %s", uom_id)
                return False
        else:
            return self.env["res.config.settings"]._default_vehicle_passenger_uom_id()

    weight_uom_id = fields.Many2one(
        "uom.uom",
        string="Weight and Capacity UOM",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
        default=lambda x: x._get_vehicle_weight_uom_id_from_ir_config_parameter(),
    )

    volume_uom_id = fields.Many2one(
        "uom.uom",
        string="Volume Capacity UOM",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id)
        ],
        default=lambda x: x._get_vehicle_volume_uom_id_from_ir_config_parameter(),
    )

    passenger_uom_id = fields.Many2one(
        "uom.uom",
        string="Passenger Capacity UOM",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_unit").id)
        ],
        default=lambda x: x._get_vehicle_passenger_uom_id_from_ir_config_parameter(),
    )
