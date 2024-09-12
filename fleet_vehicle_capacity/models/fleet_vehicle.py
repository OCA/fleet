# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    vehicle_weight = fields.Float(
        related="model_id.vehicle_weight",
        string="Vehicle Weight",
        help="The weight of the vehicle.",
    )

    weight_capacity = fields.Float(
        related="model_id.weight_capacity",
        string="Weight Capacity",
        help="The maximum weight capacity the vehicle can support.",
    )

    volume_capacity = fields.Float(
        related="model_id.volume_capacity",
        string="Volume Capacity",
        help="The maximum volume capacity the vehicle can support.",
    )

    passenger_capacity = fields.Float(
        related="model_id.passenger_capacity",
        string="Passenger Capacity",
        help="The maximum passenger capacity the vehicle can support.",
    )

    weight_uom_id = fields.Many2one(
        related="model_id.weight_uom_id",
        string="Weight and Capacity UOM",
    )

    volume_uom_id = fields.Many2one(
        related="model_id.volume_uom_id",
        string="Volume Capacity UOM",
    )

    passenger_uom_id = fields.Many2one(
        related="model_id.passenger_uom_id",
        string="Passenger Capacity UOM",
    )
