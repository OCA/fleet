# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    fleet_vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self):
        result = super()._prepare_account_move_line()
        result["vehicle_id"] = self.order_id.fleet_vehicle_id.id
        return result
