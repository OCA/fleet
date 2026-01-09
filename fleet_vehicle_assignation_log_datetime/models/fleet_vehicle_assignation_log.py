# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicleAssignationLog(models.Model):
    # Inherit from mail.thread and mail.activity.mixin to enable tracking
    _inherit = ["fleet.vehicle.assignation.log", "mail.thread", "mail.activity.mixin"]
    _name = "fleet.vehicle.assignation.log"  # Explicitly redeclare _name

    datetime_start = fields.Datetime(
        string="Start Datetime",
        help="Precise start date and time of the driver assignment.",
        required=True,
        default=fields.Datetime.now,
        tracking=True,  # Tracking is now valid
    )
    datetime_end = fields.Datetime(
        string="End Datetime",
        help="Precise end date and time of the driver assignment.",
        tracking=True,  # Tracking is now valid
    )

    @api.model
    def _synchronize_datetimes(self, vals):
        """
        Helper method to synchronize date and datetime fields.
        Ensures that if a date is provided without a datetime, the datetime
        is populated accordingly. This is used in create() and write().
        """
        # Synchronize start date
        if vals.get("date_start") and not vals.get("datetime_start"):
            vals["datetime_start"] = fields.Datetime.to_datetime(vals["date_start"])

        # Synchronize end date
        if vals.get("date_end") and not vals.get("datetime_end"):
            date_end = fields.Date.to_date(vals["date_end"])
            vals["datetime_end"] = fields.Datetime.to_datetime(date_end).replace(
                hour=23, minute=59, second=59
            )
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """
        On create, ensure datetimes are synchronized if only dates are provided.
        """
        for vals in vals_list:
            vals = self._synchronize_datetimes(vals)
        return super().create(vals_list)

    def write(self, vals):
        """
        On write, ensure datetimes are synchronized. This is crucial for
        compatibility with modules that set `date_end` programmatically.
        """
        vals = self._synchronize_datetimes(vals)
        return super().write(vals)

    # --- Onchange methods are still useful for UI responsiveness ---

    @api.onchange("datetime_start")
    def _onchange_datetime_start(self):
        """Synchronizes the date field from the datetime field."""
        if self.datetime_start:
            self.date_start = self.datetime_start.date()
        else:
            self.date_start = False

    @api.onchange("datetime_end")
    def _onchange_datetime_end(self):
        """Synchronizes the date field from the datetime field."""
        if self.datetime_end:
            self.date_end = self.datetime_end.date()
        else:
            self.date_end = False

    @api.onchange("date_start")
    def _onchange_date_start(self):
        """Synchronizes the datetime field from the date field in the UI."""
        if self.date_start and not self.datetime_start:
            self.datetime_start = fields.Datetime.to_datetime(self.date_start)

    @api.onchange("date_end")
    def _onchange_date_end(self):
        """Synchronizes the datetime field from the date field in the UI."""
        if self.date_end:
            if not self.datetime_end or self.datetime_end.date() != self.date_end:
                self.datetime_end = fields.Datetime.to_datetime(self.date_end).replace(
                    hour=23, minute=59, second=59
                )
        else:
            self.datetime_end = False
