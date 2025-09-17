# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_issuing_agency = fields.Boolean(
        string="Is a Traffic Issuing Agency",
        help="Check this box if this partner is an agency that can issue "
        "traffic infractions.",
    )

    issuing_agency_rank = fields.Integer(
        compute="_compute_issuing_agency_rank",
        store=True,
        help="The number of traffic infractions issued by this agency.",
    )

    issued_infraction_ids = fields.One2many(
        "fleet.traffic.infractions", "issuing_agency_id", string="Issued Infractions"
    )

    driver_infraction_ids = fields.One2many(
        "fleet.traffic.infractions", "driver_id", string="Driver Infractions"
    )

    total_infraction_fines = fields.Monetary(
        compute="_compute_total_infraction_fines",
        store=True,
        help="Total value of fines attributed to this partner as a driver.",
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", string="Currency"
    )

    @api.depends("issued_infraction_ids")
    def _compute_issuing_agency_rank(self):
        if not self.ids:
            return
        infraction_data = self.env["fleet.traffic.infractions"].read_group(
            [("issuing_agency_id", "in", self.ids)],
            ["issuing_agency_id"],
            ["issuing_agency_id"],
        )
        mapped_data = {
            data["issuing_agency_id"][0]: data["issuing_agency_id_count"]
            for data in infraction_data
        }
        for partner in self:
            partner.issuing_agency_rank = mapped_data.get(partner.id, 0)

    @api.depends("driver_infraction_ids.fine_amount", "driver_infraction_ids.state")
    def _compute_total_infraction_fines(self):
        for partner in self:
            fines = partner.driver_infraction_ids.filtered(
                lambda i: i.state not in ("draft", "cancel")
            ).mapped("fine_amount")
            partner.total_infraction_fines = sum(fines)

    def action_view_driver_infractions(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fleet_traffic_infractions.action_fleet_traffic_infractions"
        )
        action["domain"] = [("driver_id", "=", self.id)]
        action["context"] = {
            "default_driver_id": self.id,
            "search_default_driver_id": self.id,
        }
        return action

    # MODIFICATION: Add new method to open issued infractions
    def action_view_issued_infractions(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fleet_traffic_infractions.action_fleet_traffic_infractions"
        )
        action["domain"] = [("issuing_agency_id", "=", self.id)]
        action["context"] = {
            "default_issuing_agency_id": self.id,
            "search_default_issuing_agency_id": self.id,
        }
        return action

    @api.constrains("is_issuing_agency", "is_company")
    def _check_issuing_agency_is_company(self):
        """Ensures that only companies can be marked as Traffic Issuing Agencies."""
        for partner in self:
            if partner.is_issuing_agency and not partner.is_company:
                raise ValidationError(
                    _("Only companies can be marked as Traffic Issuing Agencies.")
                )
