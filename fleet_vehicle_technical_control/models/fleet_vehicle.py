# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    technical_control_every_months = fields.Integer(
        string="Technical Control Every (Months)",
        default=12,
    )
    date_last_technical_control = fields.Date(
        string="Last Technical Control Date",
        compute="_compute_date_last_technical_control",
        store=True,
    )
    date_next_technical_control = fields.Date(
        string="Next Technical Control Date",
        compute="_compute_date_next_technical_control",
    )
    technical_control_ids = fields.One2many(
        comodel_name="fleet.vehicle.technical.control",
        inverse_name="vehicle_id",
        string="Technical Controls",
    )

    @api.depends("technical_control_ids.date")
    def _compute_date_last_technical_control(self):
        for vehicle in self:
            vehicle.date_last_technical_control = max(
                vehicle.technical_control_ids.mapped("date") or [False]
            )

    @api.depends("date_last_technical_control", "technical_control_every_months")
    def _compute_date_next_technical_control(self):
        for vehicle in self:
            if (
                vehicle.date_last_technical_control
                and vehicle.technical_control_every_months
            ):
                vehicle.date_next_technical_control = (
                    vehicle.date_last_technical_control
                    + relativedelta(months=vehicle.technical_control_every_months)
                )
            else:
                vehicle.date_next_technical_control = False

    @api.constrains("technical_control_every_months")
    def _check_technical_control_every_months(self):
        for vehicle in self:
            if vehicle.technical_control_every_months < 0:
                raise ValidationError(
                    _("Technical control frequency must be greater than or equal to 0.")
                )

    def action_technical_control_done(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Technical Control Done"),
            "res_model": "fleet.vehicle.technical.control",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_vehicle_id": self.id,
            },
        }
