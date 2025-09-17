# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetTrafficInfractionType(models.Model):
    _name = "fleet.traffic.infraction.type"
    _description = "Fleet Traffic Infraction Type"
    _rec_name = "name"

    def _default_company_country(self):
        """Returns the country of the current company."""
        return self.env.company.country_id

    name = fields.Char(compute="_compute_name", store=True)
    code = fields.Char(string="Infraction Code", required=True, index=True)
    description = fields.Text()
    legal_reference = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()

    jurisdiction_level = fields.Selection(
        [
            ("country", "Country"),
            ("state", "State / Province"),
            ("municipal", "Municipal / City"),
        ],
        required=True,
        default="country",
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        default=_default_company_country,
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State / Province",
        domain="[('country_id', '=', country_id)]",
    )
    city = fields.Char()

    _sql_constraints = [
        ("code_unique", "unique(code)", "The infraction code must be unique!")
    ]

    @api.depends("code", "description")
    def _compute_name(self):
        for rec in self:
            rec.name = (
                f"[{rec.code}] {rec.description}"
                if rec.code and rec.description
                else rec.code
            )

    @api.constrains("jurisdiction_level", "state_id", "city")
    def _check_jurisdiction_fields(self):
        """Ensures that jurisdiction fields are consistent with the selected level."""
        for rec in self:
            if rec.jurisdiction_level == "country" and (rec.state_id or rec.city):
                raise ValidationError(
                    _(
                        "For a 'Country' level jurisdiction, State and City must be "
                        "empty."
                    )
                )
            if rec.jurisdiction_level == "state":
                if rec.city:
                    raise ValidationError(
                        _(
                            "For a 'State' level jurisdiction, the City field must be "
                            "empty."
                        )
                    )
                if not rec.state_id:
                    raise ValidationError(
                        _(
                            "For a 'State' level jurisdiction, the State field is "
                            "required."
                        )
                    )
            if rec.jurisdiction_level == "municipal" and (
                not rec.state_id or not rec.city
            ):
                raise ValidationError(
                    _(
                        "For a 'Municipal' level jurisdiction, both State and City are "
                        "required."
                    )
                )

    @api.onchange("jurisdiction_level")
    def _onchange_jurisdiction_level(self):
        """Clears irrelevant fields when the jurisdiction level changes for UX."""
        if self.jurisdiction_level == "country":
            self.state_id = False
            self.city = False
        elif self.jurisdiction_level == "state":
            self.city = False
