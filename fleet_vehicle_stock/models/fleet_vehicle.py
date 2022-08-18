# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    lot_id = fields.Many2one(
        "stock.production.lot",
        string="Serial #",
    )
    current_stock_location_id = fields.Many2one(
        "stock.location",
        string="Current Inventory Location",
        compute="_compute_current_stock_loc_id",
    )

    @api.depends("product_id", "lot_id")
    def _compute_current_stock_loc_id(self):
        for rec in self:
            if rec.lot_id:
                quants = self.env["stock.quant"].search(
                    [("lot_id", "=", rec.lot_id.id)], order="id desc", limit=1
                )
                if quants and quants.location_id:
                    rec.current_stock_location_id = quants.location_id.id
                else:
                    rec.current_stock_location_id = False
            else:
                rec.current_stock_location_id = False

    @api.onchange("model_id")
    def _onchange_model(self):
        for rec in self:
            rec.product_id = rec.model_id.product_id.id

    @api.onchange("product_id")
    def _onchange_product(self):
        for rec in self:
            rec.lot_id = False
            rec.current_stock_location_id = False

    @api.model
    def create(self, vals):
        res = super(FleetVehicle, self).create(vals)
        if res.lot_id:
            if "lot_id" in vals:
                res.lot_id.fleet_vehicle_id = res.id
        return res

    def write(self, vals):
        for rec in self:
            prev_lot = rec.lot_id
            res = super(FleetVehicle, rec).write(vals)
            if prev_lot and (prev_lot != rec.lot_id):
                prev_lot.fleet_vehicle_id = False
            if rec.lot_id and "lot_id" in vals:
                rec.lot_id.fleet_vehicle_id = rec.id
        return res
