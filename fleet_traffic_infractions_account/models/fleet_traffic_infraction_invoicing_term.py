# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetTrafficInfractionInvoicingTerm(models.Model):
    _name = "fleet.traffic.infraction.invoicing.term"
    _description = "Fleet Infraction Invoicing Terms"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    driver_domain = fields.Char(
        string="Applies on Drivers",
        default="[]",
        help="Domain to select the drivers to whom this term applies. "
        "Leave empty to apply to all drivers.",
    )
    action = fields.Selection(
        [
            ("invoice_driver", "Invoice Driver"),
            ("company_pays", "Company Pays (No Driver Invoice)"),
        ],
        required=True,
        default="invoice_driver",
    )

    expense_line_ids = fields.One2many(
        "fleet.traffic.infraction.invoicing.term.line",
        "invoicing_term_id",
        string="Additional Expenses",
    )

    discount_type = fields.Selection(
        [
            ("none", "No Discount"),
            ("percentage", "Percentage"),
            ("fixed", "Fixed Amount"),
        ],
        default="none",
    )
    discount_value = fields.Float()
    discount_product_id = fields.Many2one(
        "product.product",
        string="Discount Product",
        domain="[('type', '=', 'service')]",
        help="A service product used to represent the discount on the invoice.",
    )

    @api.constrains("discount_type", "discount_value", "discount_product_id")
    def _check_discount(self):
        for term in self:
            if term.discount_type != "none":
                if not term.discount_product_id:
                    raise ValidationError(
                        _("You must select a Discount Product for a discount policy.")
                    )
                if term.discount_value <= 0:
                    raise ValidationError(
                        _("Discount value must be greater than zero.")
                    )