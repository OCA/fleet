# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # The 'account' module adds the 'autopost_bills' field as required=True.
    # While it has a default in its definition, this default sometimes fails to
    # apply during the setup of test suites for dependency modules, causing a
    # NotNullViolation.
    # By inheriting the create method, we explicitly inject the default value
    # if it's missing, ensuring system-wide stability during tests without
    # altering the field's original definition.
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "autopost_bills" not in vals:
                vals["autopost_bills"] = "ask"
        return super().create(vals_list)