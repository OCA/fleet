# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    create_fleet_vehicle = fields.Boolean(string="Creates a Fleet Vehicle")
    fleet_vehicle_model_id = fields.Many2one(
        "fleet.vehicle.model",
        compute="_compute_fleet_vehicle_model_id",
        inverse="_inverse_fleet_vehicle_model_id",
        store=True,
        string="Vehicle Model",
    )

    @api.depends("product_variant_ids", "product_variant_ids.fleet_vehicle_model_id")
    def _compute_fleet_vehicle_model_id(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fleet_vehicle_model_id = (
                template.product_variant_ids.fleet_vehicle_model_id
            )
        for template in self - unique_variants:
            template.fleet_vehicle_model_id = False

    def _inverse_fleet_vehicle_model_id(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fleet_vehicle_model_id = (
                self.fleet_vehicle_model_id
            )

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get("fleet_vehicle_model_id"):
                related_vals["fleet_vehicle_model_id"] = vals["fleet_vehicle_model_id"]
            if related_vals:
                template.write(related_vals)
        return templates

    _sql_constraints = [
        (
            "non_product_tracking_for_vehicle_model",
            "CHECK((tracking != 'serial' AND fleet_vehicle_model_id IS NULL) "
            "OR (tracking = 'serial'))",
            "It is mandatory to configure the traceability by serial number in order "
            "to be able to configure the vehicle model of the fleet in this product.",
        ),
    ]
