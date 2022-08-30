# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_vehicle_values(self, move_line):
        return {
            "name": "{} ({})".format(move_line.product_id.name, move_line.lot_id.name),
            "model_id": move_line.product_id.fleet_vehicle_model_id.id,
            "product_id": move_line.product_id.id,
            "lot_id": move_line.lot_id.id,
            "current_stock_location_id": move_line.location_dest_id.id,
        }

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder)
        for rec in self:

            if (
                rec.product_id.product_tmpl_id.create_fleet_vehicle
                and not rec.product_id.fleet_vehicle_model_id
            ):
                raise UserError(
                    _(
                        "The product '%s' is configure to create a fleet "
                        "vehicle but vehicle model is not configured in the "
                        "product."
                    )
                    % rec.product_id.name
                )

            if (
                rec.state == "done"
                and rec.picking_type_id.create_fleet_vehicle
                and rec.product_tmpl_id.create_fleet_vehicle
                and rec.product_id.fleet_vehicle_model_id
            ):
                for line in rec.move_line_ids:
                    vals = self._prepare_vehicle_values(line)
                    line.lot_id.fleet_vehicle_id = rec.env["fleet.vehicle"].create(vals)
        return res
