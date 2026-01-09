# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetTrafficInfractionInvoicingTerm(models.Model):
    _name = "fleet.traffic.infraction.invoicing.term"
    _description = "Fleet Infraction Invoicing Term (Rule)"
    _order = "sequence, id"

    name = fields.Char(required=True, help="A descriptive name for this invoicing rule.")
    sequence = fields.Integer(
        default=10,
        help="The priority of the rule. Lower numbers are checked first. "
        "The first rule that matches the driver will be applied.",
    )
    active = fields.Boolean(default=True)
    driver_domain = fields.Char(
        string="Applies To Drivers",
        default="[]",
        help="Use the domain builder to define which drivers this rule applies to. "
        "Leave empty to create a 'catch-all' rule.",
    )
    action = fields.Selection(
        [
            ("invoice_driver", "Invoice Driver"),
            ("company_pays", "Company Pays (No Driver Invoice)"),
        ],
        required=True,
        default="invoice_driver",
        help="The action to take when this rule is matched.",
    )

    expense_line_ids = fields.One2many(
        "fleet.traffic.infraction.invoicing.term.line",
        "invoicing_term_id",
        string="Additional Expenses",
        help="Add lines for administrative fees or other charges to be added to the driver's invoice.",
    )

    discount_type = fields.Selection(
        [
            ("none", "No Discount"),
            ("percentage", "Percentage"),
            ("fixed", "Fixed Amount"),
        ],
        string="Discount Type",
        default="none",
    )
    discount_value = fields.Float("Discount Value")
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