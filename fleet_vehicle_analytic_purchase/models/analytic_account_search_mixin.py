# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AnalyticAccountSearchMixin(models.AbstractModel):
    _name = "analytic.account.search.mixin"
    _description = "Analytic Account Search"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        store=False,
        search="_search_analytic_account_id",
    )

    def _search_analytic_account_id(self, operator, value):
        return [("distribution_analytic_account_ids", operator, value)]
