# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetTrafficInfractions(models.Model):
    _name = "fleet.traffic.infractions"
    _description = "Fleet Traffic Infractions"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "vehicle_infraction_auto_number_unique",
            "unique(vehicle_id, infraction_auto_number, infraction_type_id)",
            "This infraction number already exists for this vehicle and "
            "infraction type!",
        )
    ]

    name = fields.Char(
        "Reference", required=True, index=True, copy=False, default="New"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Canceled"),
        ],
        string="Status",
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )
    vehicle_id = fields.Many2one("fleet.vehicle")
    driver_id = fields.Many2one("res.partner", copy=False)
    infraction_type_id = fields.Many2one(
        "fleet.traffic.infraction.type",
        string="Infraction Type",
        ondelete="restrict",
    )
    issuing_agency_id = fields.Many2one(
        "res.partner",
        string="Issuing Agency",
        ondelete="restrict",
        domain="[('is_issuing_agency', '=', True)]",
        help="Select a partner that is marked as an Issuing Agency.",
    )
    infraction_key = fields.Char(
        compute="_compute_infraction_key",
        store=True,
        help="A human-readable key for this infraction.",
    )
    infraction_datetime = fields.Datetime()
    due_date = fields.Date()
    infraction_auto_number = fields.Char()
    fine_amount = fields.Float()
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    # Address Fields Mimicking res.partner
    street = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state", domain="[('country_id', '=', country_id)]"
    )
    country_id = fields.Many2one("res.country")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fleet.traffic.infractions"
                ) or _("New")
        return super().create(vals_list)

    def write(self, vals):
        original_drivers = (
            {rec.id: rec.driver_id for rec in self} if "driver_id" in vals else {}
        )
        res = super().write(vals)
        if original_drivers:
            for record in self:
                old_driver = original_drivers.get(record.id)
                if old_driver != record.driver_id:
                    record._log_driver_change(old_driver)
        return res

    def _log_driver_change(self, old_driver):
        self.ensure_one()
        new_driver = self.driver_id
        old_driver_name = old_driver.name if old_driver else _("None")
        new_driver_name = new_driver.name if new_driver else _("None")
        message_parts = [
            _(
                "Driver changed on infraction:\n"
                "- Old Driver: %(old_driver_name)s\n"
                "- New Driver: %(new_driver_name)s"
            )
            % {"old_driver_name": old_driver_name, "new_driver_name": new_driver_name}
        ]
        if self.infraction_datetime:
            user_tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
            lang = self.env["res.lang"]._lang_get(self.env.lang)
            lang_format = f"{lang.date_format} {lang.time_format}"
            user_tz_dt = fields.Datetime.context_timestamp(
                self, self.infraction_datetime
            )
            inf_datetime_str = f"{user_tz_dt.strftime(lang_format)} ({user_tz_name})"
            log_driver = self.vehicle_id.get_driver_for_datetime(
                self.infraction_datetime
            )
            if log_driver and new_driver == log_driver:
                message_parts.append(
                    _(
                        "The new driver matches the vehicle assignment log for "
                        "%(datetime)s."
                    )
                    % {"datetime": inf_datetime_str}
                )
            elif log_driver and new_driver != log_driver:
                message_parts.append(
                    _(
                        "Note: The assignment log suggests '%(log_driver)s' was the "
                        "driver at %(datetime)s, which differs from the new driver."
                    )
                    % {"log_driver": log_driver.name, "datetime": inf_datetime_str}
                )
            elif not log_driver:
                message_parts.append(
                    _("Note: No driver was found in assignment logs at %(datetime)s.")
                    % {"datetime": inf_datetime_str}
                )
        self.message_post(body="\n\n".join(message_parts), subtype_xmlid="mail.mt_note")

    @api.depends(
        "vehicle_id.license_plate", "infraction_auto_number", "infraction_type_id.code"
    )
    def _compute_infraction_key(self):
        for rec in self:
            if (
                rec.vehicle_id.license_plate
                and rec.infraction_auto_number
                and rec.infraction_type_id.code
            ):
                plate = rec.vehicle_id.license_plate
                auto_num = rec.infraction_auto_number
                inf_code = rec.infraction_type_id.code
                rec.infraction_key = f"{plate}-{auto_num}-{inf_code}"
            else:
                rec.infraction_key = False

    @api.onchange("vehicle_id", "infraction_datetime")
    def _onchange_vehicle_infraction_datetime(self):
        """Suggests the driver based on vehicle assignment logs."""
        if not self.vehicle_id or not self.infraction_datetime:
            self.driver_id = False
            return
        driver = self.vehicle_id.get_driver_for_datetime(self.infraction_datetime)
        if driver:
            self.driver_id = driver.id

    def button_confirm(self):
        self._check_required_fields_for_confirmation()
        self.write({"state": "confirmed"})

    def button_cancel(self):
        self.write({"state": "cancel"})

    def button_draft(self):
        self.write({"state": "draft"})

    def _check_required_fields_for_confirmation(self):
        for record in self:
            missing_fields = []
            if not record.vehicle_id:
                missing_fields.append(_("Vehicle"))
            if not record.driver_id:
                missing_fields.append(_("Driver"))
            if not record.infraction_type_id:
                missing_fields.append(_("Infraction Type"))
            if not record.issuing_agency_id:
                missing_fields.append(_("Issuing Agency"))
            if not record.infraction_datetime:
                missing_fields.append(_("Infraction Datetime"))
            if not record.street or not record.city or not record.country_id:
                missing_fields.append(_("Infraction Address"))
            if not record.infraction_auto_number:
                missing_fields.append(_("Infraction Auto Number"))
            if not record.fine_amount:
                missing_fields.append(_("Fine Amount"))

            if missing_fields:
                raise ValidationError(
                    _(
                        "Cannot confirm infraction '%(name)s'. The following fields "
                        "are mandatory:\n- %(fields)s"
                    )
                    % {"name": record.name, "fields": "\n- ".join(missing_fields)}
                )
