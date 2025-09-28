# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    infraction_bill_method = fields.Selection(
        [
            ("vendor_bill", "Create Vendor Bill"),
            ("journal_entry", "Create Miscellaneous Journal Entry"),
        ],
        string="Infraction Agency Billing Method",
        default="vendor_bill",
        help="Choose the default method to record fines from issuing agencies.\n"
        "- Vendor Bill: Treats the fine as a standard purchase, affecting "
        "procurement reports.\n"
        "- Journal Entry: Treats the fine as a direct expense, bypassing "
        "the procurement process.",
    )