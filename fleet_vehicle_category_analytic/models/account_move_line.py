# Copyright 2026 - Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line"]

    @api.depends("vehicle_id")
    def _compute_analytic_distribution(self):
        """Inject the analytic account of the vehicle's category.
        When the account is already present in the distribution its
        percentage is kept as-is to avoid overriding manual adjustments made
        through other sources; otherwise it is added at 100%.
        """
        res = super()._compute_analytic_distribution()
        for line in self:
            if not line.vehicle_id:
                continue
            account = line.vehicle_id.vehicle_category_id.analytic_account_id
            if not account:
                continue

            distribution = line.analytic_distribution or {}
            account_key = str(account.id)
            if account_key not in distribution:
                distribution[account_key] = 100
            line.analytic_distribution = distribution
        return res
