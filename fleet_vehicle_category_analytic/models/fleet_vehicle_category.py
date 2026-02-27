# Copyright 2026 - Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleCategory(models.Model):
    _inherit = ["fleet.vehicle.category"]

    company_id = fields.Many2one(
        comodel_name="res.company",
        readonly=True,
        default=lambda self: self.env.company.root_id,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        check_company=True,
    )
