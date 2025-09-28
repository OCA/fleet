# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class FleetTrafficInfractions(models.Model):
    _inherit = "fleet.traffic.infractions"

    state = fields.Selection(
        selection_add=[
            ("invoice", "To Invoice Driver"),
            ("bill", "To Create Agency Bill"),
            ("processed", "Processed"),
        ],
        ondelete={
            "invoice": "set default",
            "bill": "set default",
            "processed": "set default",
        },
    )

    driver_invoice_id = fields.Many2one(
        "account.move", "Driver Invoice", readonly=True, copy=False
    )
    agency_move_id = fields.Many2one(
        "account.move", "Agency Accounting Entry", readonly=True, copy=False
    )
    # This field is for display/informational purposes on the form
    applied_invoicing_term_id = fields.Many2one(
        "fleet.traffic.infraction.invoicing.term",
        string="Applied Invoicing Rule",
        compute="_compute_applied_invoicing_term_id",
        store=True,
    )

    @api.depends("driver_id")
    def _compute_applied_invoicing_term_id(self):
        """Find and set the first matching invoicing term for the driver."""
        for infraction in self:
            infraction.applied_invoicing_term_id = infraction._get_invoicing_term()

    def _get_invoicing_term(self):
        """
        Find the first invoicing term that matches the driver of the infraction.
        Terms are evaluated in ascending order of their sequence.
        """
        self.ensure_one()
        if not self.driver_id:
            return self.env["fleet.traffic.infraction.invoicing.term"]

        # Search for all active terms, ordered by sequence.
        # The lowest sequence number has the highest priority.
        terms = self.env["fleet.traffic.infraction.invoicing.term"].search(
            [("active", "=", True)], order="sequence asc"
        )

        for term in terms:
            try:
                domain = safe_eval(term.driver_domain or "[]")
                # Check if the current driver matches the domain of the term
                if self.driver_id.filtered_domain(domain):
                    return term  # Return the first matching term
            except Exception:
                # Ignore terms with invalid domains
                continue

        return self.env["fleet.traffic.infraction.invoicing.term"]

    def create_driver_invoice(self):
        for infraction in self:
            if not infraction.driver_id:
                raise UserError(_("A driver must be assigned to create an invoice."))
            
            term = infraction.applied_invoicing_term_id
            if not term:
                raise UserError(
                    _("No applicable Invoicing Rule found for driver %s.")
                    % infraction.driver_id.name
                )

            if term.action == "company_pays":
                infraction.message_post(
                    body=_(
                        "Driver invoice skipped as per Invoicing Rule '%s'. "
                        "The company will pay the fine."
                    )
                    % term.name
                )
                infraction.write({"state": "bill"})
                continue

            if term.action == "invoice_driver":
                invoice_line_vals = infraction._prepare_invoice_lines_from_term(term)
                invoice = self.env["account.move"].create(
                    {
                        "partner_id": infraction.driver_id.id,
                        "move_type": "out_invoice",
                        "invoice_date": fields.Date.today(),
                        "invoice_origin": infraction.name,
                        "invoice_line_ids": invoice_line_vals,
                    }
                )
                infraction.write({"driver_invoice_id": invoice.id, "state": "bill"})
        return True
    
    def create_agency_entry(self):
        for infraction in self:
            if not infraction.issuing_agency_id:
                raise UserError(_("An issuing agency must be set to create a bill."))
            if infraction.company_id.infraction_bill_method == "vendor_bill":
                infraction._create_agency_vendor_bill()
            else:
                infraction._create_agency_journal_entry()
        return True

    def _create_agency_vendor_bill(self):
        self.ensure_one()
        product = self._get_fine_product()
        bill = self.env["account.move"].create(
            {
                "partner_id": self.issuing_agency_id.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_date_due": self.due_date,
                "invoice_origin": self.name,
                "invoice_line_ids": [(0, 0, self._prepare_invoice_line(product))],
            }
        )
        self.write({"agency_move_id": bill.id, "state": "processed"})

    def _create_agency_journal_entry(self):
        self.ensure_one()
        product = self._get_fine_product()
        debit_account = product.product_tmpl_id.get_product_accounts()["expense"]
        if not debit_account:
            raise UserError(
                _("No expense account is configured for product '%s'.") % product.name
            )
        credit_account = self.issuing_agency_id.property_account_payable_id
        journal = self.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", self.company_id.id)],
            limit=1,
        )
        if not journal:
            raise UserError(_("No purchase journal found for this company."))
        move_lines = [
            (
                0,
                0,
                {
                    "name": self.name,
                    "account_id": debit_account.id,
                    "debit": self.fine_amount,
                    "credit": 0.0,
                },
            ),
            (
                0,
                0,
                {
                    "name": self.name,
                    "partner_id": self.issuing_agency_id.id,
                    "account_id": credit_account.id,
                    "debit": 0.0,
                    "credit": self.fine_amount,
                },
            ),
        ]
        entry = self.env["account.move"].create(
            {
                "journal_id": journal.id,
                "move_type": "entry",
                "date": fields.Date.today(),
                "ref": self.name,
                "line_ids": move_lines,
            }
        )
        self.write({"agency_move_id": entry.id, "state": "processed"})