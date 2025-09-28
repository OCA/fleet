# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetTrafficInfractionInvoicingTermLine(models.Model):
    _name = "fleet.traffic.infraction.invoicing.term.line"
    _description = "Fleet Infraction Invoicing Term Line (Expenses)"

    invoicing_term_id = fields.Many2one(
        "fleet.traffic.infraction.invoicing.term",
        string="Invoicing Term",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('type', '=', 'service')]",
    )
    calculation_method = fields.Selection(
        [
            ("fixed", "Fixed Amount"),
            ("percentage_fine", "Percentage of Fine Amount"),
        ],
        string="Calculation",
        required=True,
        default="fixed",
    )
    amount = fields.Float(
        string="Amount / Percentage",
        help="The fixed amount or the percentage (e.g., 10 for 10%).",
    )