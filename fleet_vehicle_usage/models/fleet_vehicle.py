# Copyright 2021 César Fernández Domínguez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    usage_ids = fields.One2many(
        comodel_name="fleet.vehicle.usage", inverse_name="vehicle_id", string="Usages"
    )
    in_use = fields.Boolean(
        compute="_compute_in_use",
        store=True,
    )

    @api.depends("usage_ids", "usage_ids.state")
    def _compute_in_use(self):
        for item in self:
            item.in_use = any(usage.state == "in_use" for usage in item.usage_ids)
