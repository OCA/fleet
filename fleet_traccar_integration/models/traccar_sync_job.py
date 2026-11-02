import logging
import math
import threading
import time
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Each window downloads and stores the positions of one device for this period
JOB_WINDOW = timedelta(days=1)
# Seconds a cron batch keeps processing windows before reporting its progress
JOB_TIME_BUDGET = 50


class TraccarSyncJob(models.Model):
    _name = "traccar.sync.job"
    _description = "Traccar History Import"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        readonly=True,
    )
    device_ids = fields.Many2many(
        "traccar.device",
        "traccar_sync_job_device_rel",
        "job_id",
        "device_id",
        string="Devices",
        required=True,
        readonly=True,
    )
    date_from = fields.Datetime(string="From", required=True, readonly=True)
    date_to = fields.Datetime(string="To", required=True, readonly=True)
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("running", "Running"),
            ("done", "Done"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="queued",
        required=True,
        readonly=True,
        index=True,
        tracking=True,
    )
    current_device_id = fields.Many2one(
        "traccar.device", string="Current Device", readonly=True
    )
    current_date = fields.Datetime(string="Processed Until", readonly=True)
    window_count = fields.Integer(
        string="Total Steps", compute="_compute_window_count", store=True
    )
    window_done = fields.Integer(string="Steps Done", readonly=True)
    progress = fields.Float(compute="_compute_progress")
    points_created = fields.Integer(string="New Points", readonly=True)
    points_updated = fields.Integer(string="Updated Points", readonly=True)
    date_started = fields.Datetime(string="Started On", readonly=True)
    date_finished = fields.Datetime(string="Finished On", readonly=True)
    error_message = fields.Text(readonly=True)

    @api.depends("device_ids", "date_from", "date_to")
    def _compute_name(self):
        for job in self:
            devices = job.device_ids
            label = (
                devices.name
                if len(devices) == 1
                else _("%(count)s devices", count=len(devices))
            )
            job.name = _(
                "%(devices)s: %(date_from)s - %(date_to)s",
                devices=label,
                date_from=fields.Datetime.to_string(job.date_from) or "",
                date_to=fields.Datetime.to_string(job.date_to) or "",
            )

    @api.depends("device_ids", "date_from", "date_to")
    def _compute_window_count(self):
        for job in self:
            job.window_count = len(job.device_ids) * job._get_windows_per_device()

    @api.depends("window_count", "window_done", "state")
    def _compute_progress(self):
        for job in self:
            if job.state == "done":
                job.progress = 100.0
            elif job.window_count:
                job.progress = min(100.0 * job.window_done / job.window_count, 100.0)
            else:
                job.progress = 0.0

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for job in self:
            if job.date_from and job.date_to and job.date_from >= job.date_to:
                raise ValidationError(
                    _("The import start date must be before its end date.")
                )

    def _get_windows_per_device(self):
        self.ensure_one()
        if not self.date_from or not self.date_to or self.date_to <= self.date_from:
            return 0
        return math.ceil((self.date_to - self.date_from) / JOB_WINDOW)

    @api.model
    def _get_active_jobs(self, devices):
        return self.search(
            [
                ("state", "in", ("queued", "running")),
                ("device_ids", "in", devices.ids),
            ]
        )

    def _trigger_processing(self):
        self.env.ref("fleet_traccar_integration.ir_cron_traccar_sync_job")._trigger()

    def _get_form_action(self):
        action = {
            "type": "ir.actions.act_window",
            "name": _("History Imports"),
            "res_model": "traccar.sync.job",
            "view_mode": "list,form",
            "domain": [("id", "in", self.ids)],
        }
        if len(self) == 1:
            action.update({"view_mode": "form", "res_id": self.id})
        return action

    def action_cancel(self):
        self.filtered(lambda job: job.state in ("queued", "running")).write(
            {"state": "cancelled", "date_finished": fields.Datetime.now()}
        )
        return True

    def action_resume(self):
        jobs = self.filtered(lambda job: job.state in ("failed", "cancelled"))
        jobs.write({"state": "queued", "error_message": False, "date_finished": False})
        if jobs:
            jobs._trigger_processing()
        return True

    @api.model
    def _cron_process_jobs(self):
        started = time.monotonic()
        done = 0
        while time.monotonic() - started < JOB_TIME_BUDGET:
            job = self._lock_next_job()
            if not job:
                break
            job._process_next_window()
            done += 1
            self._commit_progress()
        active_jobs = self.search([("state", "in", ("queued", "running"))])
        remaining = sum(
            max(job.window_count - job.window_done, 0) for job in active_jobs
        )
        self.env["ir.cron"]._notify_progress(done=done, remaining=remaining)

    @api.model
    def _lock_next_job(self):
        # SKIP LOCKED keeps a manually triggered run from waiting on the cron
        self.flush_model(["state"])
        self.env.cr.execute(
            """
            SELECT id FROM traccar_sync_job
            WHERE state IN ('queued', 'running')
            ORDER BY id
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """
        )
        row = self.env.cr.fetchone()
        return self.browse(row[0]) if row else self.browse()

    @api.model
    def _commit_progress(self):
        # Commit each window so a failure never loses the work already done
        if not getattr(threading.current_thread(), "testing", False):
            self.env.cr.commit()  # pylint: disable=invalid-commit

    def _process_next_window(self):
        self.ensure_one()
        devices = self.device_ids.sorted("id")
        if self.state == "queued" and not self.current_device_id:
            self.write(
                {
                    "state": "running",
                    "date_started": fields.Datetime.now(),
                    "current_device_id": devices[:1].id,
                    "current_date": self.date_from,
                }
            )
        elif self.state == "queued":
            self.state = "running"
        device = self.current_device_id
        if not device:
            self._finish()
            return
        window_from = self.current_date or self.date_from
        window_to = min(window_from + JOB_WINDOW, self.date_to)
        try:
            with self.env.cr.savepoint():
                created, updated = (
                    self.env["fleet.telemetry"]
                    .with_company(self.company_id)
                    ._traccar_import_positions(
                        self.company_id, device, window_from, window_to
                    )
                )
        except Exception as error:  # pylint: disable=broad-except
            _logger.exception("Traccar history import %s failed", self.display_name)
            # The savepoint rollback does not reset the ORM cache
            self.env.invalidate_all()
            self._fail(error)
            return
        values = {
            "window_done": self.window_done + 1,
            "points_created": self.points_created + created,
            "points_updated": self.points_updated + updated,
            "current_date": window_to,
        }
        if window_to >= self.date_to:
            next_device = devices.filtered(lambda item: item.id > device.id)[:1]
            values.update(
                {
                    "current_device_id": next_device.id,
                    "current_date": self.date_from if next_device else window_to,
                }
            )
        self.write(values)
        if not self.current_device_id:
            self._finish()

    def _finish(self):
        self.ensure_one()
        self.write(
            {
                "state": "done",
                "window_done": self.window_count,
                "date_finished": fields.Datetime.now(),
            }
        )
        message = _(
            "History imported for %(job)s. New points: %(created)s. "
            "Updated points: %(updated)s.",
            job=self.name,
            created=self.points_created,
            updated=self.points_updated,
        )
        self.message_post(body=message)
        self._notify_user(message, "success")

    def _fail(self, error):
        self.ensure_one()
        message = error.args[0] if isinstance(error, UserError) else str(error)
        self.write(
            {
                "state": "failed",
                "error_message": message,
                "date_finished": fields.Datetime.now(),
            }
        )
        self._notify_user(
            _(
                "History import %(job)s failed: %(error)s",
                job=self.name,
                error=message,
            ),
            "danger",
        )

    def _notify_user(self, message, notification_type):
        self.ensure_one()
        if not self.user_id:
            return
        self.user_id._bus_send(
            "simple_notification",
            {
                "title": _("Traccar"),
                "message": message,
                "type": notification_type,
                "sticky": notification_type == "danger",
            },
        )
