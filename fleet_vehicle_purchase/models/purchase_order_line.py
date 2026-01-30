# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    fleet_vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        compute="_compute_fleet_vehicle_id",
        store=True,
        readonly=False,
    )
    fleet_vehicle_from_po = fields.Boolean(
        compute="_compute_fleet_vehicle_from_po", store=True
    )

    @api.depends("fleet_vehicle_from_po")
    def _compute_fleet_vehicle_id(self):
        for rec in self:
            if rec.fleet_vehicle_from_po:
                rec.fleet_vehicle_id = rec.order_id.fleet_vehicle_id

    @api.depends("order_id", "order_id.fleet_vehicle_id")
    def _compute_fleet_vehicle_from_po(self):
        for rec in self:
            rec.fleet_vehicle_from_po = bool(rec.order_id.fleet_vehicle_id)

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        result = super()._prepare_account_move_line(move)
        if self.fleet_vehicle_id:
            result["vehicle_id"] = self.fleet_vehicle_id.id
        return result
