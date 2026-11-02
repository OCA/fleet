from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TraccarHistoryImportWizard(models.TransientModel):
    _name = "traccar.history.import.wizard"
    _description = "Traccar History Import Wizard"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    device_ids = fields.Many2many("traccar.device", string="Devices", required=True)
    period = fields.Selection(
        [
            ("today", "Today"),
            ("yesterday", "Yesterday"),
            ("last_7_days", "Last 7 Days"),
            ("last_30_days", "Last 30 Days"),
            ("since_last_point", "Since Last Point"),
            ("custom", "Custom"),
        ],
        default="today",
        required=True,
    )
    date_from = fields.Datetime(
        string="From",
        compute="_compute_dates",
        store=True,
        precompute=True,
        readonly=False,
        required=True,
    )
    date_to = fields.Datetime(
        string="To",
        compute="_compute_dates",
        store=True,
        precompute=True,
        readonly=False,
        required=True,
    )
    max_days = fields.Integer(related="company_id.traccar_history_max_days")

    @api.model
    def _get_wizard_action(self, devices):
        if not devices:
            raise UserError(
                _("Select at least one vehicle linked to a Traccar device.")
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Import Traccar History"),
            "res_model": self._name,
            "view_mode": "form",
            "target": "new",
            "context": {"default_device_ids": [(6, 0, devices.ids)]},
        }

    def _local_midnight(self, days_ago=0):
        """Return the user's local midnight, ``days_ago`` days back, in UTC."""
        tz = pytz.timezone(self.env.user.tz or "UTC")
        day = datetime.now(tz).date() - timedelta(days=days_ago)
        local_midnight = tz.localize(datetime.combine(day, time.min))
        return local_midnight.astimezone(pytz.utc).replace(tzinfo=None)

    @api.depends("period", "device_ids")
    def _compute_dates(self):
        now = fields.Datetime.now()
        for wizard in self:
            if wizard.period == "custom":
                wizard.date_from = wizard.date_from or wizard._local_midnight()
                wizard.date_to = wizard.date_to or now
                continue
            wizard.date_to = now
            if wizard.period == "today":
                wizard.date_from = wizard._local_midnight()
            elif wizard.period == "yesterday":
                wizard.date_from = wizard._local_midnight(1)
                wizard.date_to = wizard._local_midnight()
            elif wizard.period == "last_7_days":
                wizard.date_from = now - timedelta(days=7)
            elif wizard.period == "last_30_days":
                wizard.date_from = now - timedelta(days=30)
            else:
                wizard.date_from = wizard._get_last_point_date() or now - timedelta(
                    days=max(wizard.company_id.traccar_history_days or 1, 1)
                )

    def _get_last_point_date(self):
        self.ensure_one()
        if not self.device_ids:
            return False
        groups = self.env["fleet.telemetry"]._read_group(
            [
                ("provider", "=", "traccar"),
                ("traccar_device_id", "in", self.device_ids.ids),
            ],
            ["traccar_device_id"],
            ["fix_time:max"],
        )
        last_dates = [last for _device, last in groups if last]
        # The oldest device sets the start, so every device catches up
        if len(last_dates) < len(self.device_ids):
            return False
        return min(last_dates)

    def action_confirm(self):
        self.ensure_one()
        if self.date_from >= self.date_to:
            raise UserError(_("The start date must be before the end date."))
        max_days = max(self.max_days or 1, 1)
        if self.date_to - self.date_from > timedelta(days=max_days):
            raise UserError(
                _(
                    "The period can not be longer than %(days)s days. "
                    "Choose a shorter period or split the import.",
                    days=max_days,
                )
            )
        Job = self.env["traccar.sync.job"]
        active_jobs = Job._get_active_jobs(self.device_ids)
        if active_jobs:
            # Never run two imports of the same device at the same time
            return active_jobs._get_form_action()
        job = Job.create(
            {
                "company_id": self.company_id.id,
                "device_ids": [(6, 0, self.device_ids.ids)],
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        job._trigger_processing()
        return job._get_form_action()
