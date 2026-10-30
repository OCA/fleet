import math
from datetime import datetime, timezone

from odoo import _, api, fields, models


def _traccar_datetime(value):
    if not value:
        return False
    if not isinstance(value, str):
        return value
    return (
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )


def _traccar_number(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(value)
    ):
        return False
    return float(value)


class TraccarDevice(models.Model):
    _name = "traccar.device"
    _description = "Traccar Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", index=True)
    telemetry_device_id = fields.Many2one(
        "fleet.telemetry.device",
        string="Telemetry Device",
        copy=False,
        index=True,
    )
    traccar_id = fields.Integer(string="Traccar ID", index=True, copy=False)
    name = fields.Char(required=True, tracking=True)
    unique_id = fields.Char(
        string="Unique ID", required=True, index=True, tracking=True
    )
    status = fields.Char()
    last_update = fields.Datetime()
    latitude = fields.Float(digits=(10, 7))
    longitude = fields.Float(digits=(10, 7))
    speed = fields.Float()
    course = fields.Float()
    address = fields.Char()
    active = fields.Boolean(default=True)
    traccar_sync_job_ids = fields.Many2many(
        "traccar.sync.job",
        "traccar_sync_job_device_rel",
        "device_id",
        "job_id",
        string="History Imports",
        readonly=True,
    )
    traccar_sync_job_count = fields.Integer(compute="_compute_traccar_sync_job_count")
    traccar_sync_job_progress = fields.Float(
        string="Import Progress", compute="_compute_traccar_sync_job_count"
    )

    _sql_constraints = [
        (
            "traccar_device_unique_company_unique_id",
            "unique(company_id, unique_id)",
            "The device Unique ID must be unique per company.",
        ),
        (
            "traccar_device_unique_company_traccar_id",
            "unique(company_id, traccar_id)",
            "The device Traccar ID must be unique per company.",
        ),
    ]

    @api.depends("traccar_sync_job_ids.state", "traccar_sync_job_ids.window_done")
    def _compute_traccar_sync_job_count(self):
        for device in self:
            jobs = device.traccar_sync_job_ids
            active_jobs = jobs.filtered(lambda job: job.state in ("queued", "running"))
            device.traccar_sync_job_count = len(jobs)
            device.traccar_sync_job_progress = (
                active_jobs[:1].progress if active_jobs else 0.0
            )

    def _prepare_traccar_payload(self):
        self.ensure_one()
        return {
            "name": self.name,
            "uniqueId": self.unique_id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        devices = super().create(vals_list)
        if self.env.context.get("skip_traccar_remote_create"):
            return devices
        for device in devices.filtered(lambda item: not item.traccar_id):
            company = device.company_id or self.env.company
            if not company.traccar_enabled:
                continue
            data = company._traccar_request(
                "POST", "/api/devices", json=device._prepare_traccar_payload()
            )
            device.write(
                {
                    "traccar_id": data.get("id"),
                    "name": data.get("name") or device.name,
                    "unique_id": data.get("uniqueId") or device.unique_id,
                    "status": data.get("status"),
                }
            )
        return devices

    def action_sync_devices(self):
        companies = self.mapped("company_id") or self.env.company
        for company in companies:
            self._sync_company_devices(company)
        return True

    def action_traccar_update_status(self):
        companies = self.mapped("company_id") or self.env.company
        for company in companies:
            self.with_company(company)._sync_company_devices(company)
            company.traccar_last_device_sync = fields.Datetime.now()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Traccar"),
                "message": _("Devices status updated."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_traccar_sync_telemetry_history(self):
        return self.env["traccar.history.import.wizard"]._get_wizard_action(self)

    def action_view_traccar_sync_jobs(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fleet_traccar_integration.action_traccar_sync_job"
        )
        action["domain"] = [("device_ids", "in", self.ids)]
        action["context"] = {}
        return action

    def _traccar_update_last_position(self, position):
        """Keep the newest known position on the device.

        History imports process old periods, so a position older than the
        current one must not replace it.
        """
        self.ensure_one()
        fix_time = _traccar_datetime(position.get("fixTime"))
        if fix_time and self.last_update and fix_time < self.last_update:
            return
        self.write(
            {
                "latitude": _traccar_number(position.get("latitude")) or 0,
                "longitude": _traccar_number(position.get("longitude")) or 0,
                "speed": _traccar_number(position.get("speed")) or 0,
                "course": _traccar_number(position.get("course")) or 0,
                "address": position.get("address"),
                "last_update": fix_time or self.last_update,
            }
        )

    @api.model
    def _sync_company_devices(self, company):
        devices = company._traccar_request("GET", "/api/devices")
        positions = company._traccar_request(
            "GET", "/api/positions", params={"all": "true"}
        )
        positions_by_device = {item.get("deviceId"): item for item in positions or []}
        for item in devices:
            traccar_id = item.get("id")
            unique_id = item.get("uniqueId")
            if not unique_id:
                continue
            device = self.search(
                [
                    ("company_id", "=", company.id),
                    "|",
                    ("traccar_id", "=", traccar_id),
                    ("unique_id", "=", unique_id),
                ],
                limit=1,
            )
            values = {
                "company_id": company.id,
                "traccar_id": traccar_id,
                "name": item.get("name") or unique_id,
                "unique_id": unique_id,
                "status": item.get("status")
                if item.get("status") in ("online", "offline", "unknown")
                else "unknown",
                "last_update": _traccar_datetime(item.get("lastUpdate")),
            }
            position = positions_by_device.get(traccar_id)
            if position:
                lat = _traccar_number(position.get("latitude"))
                lon = _traccar_number(position.get("longitude"))
                valid = (
                    lat is not False
                    and lon is not False
                    and -90 <= lat <= 90
                    and -180 <= lon <= 180
                )
                values.update(
                    {
                        "latitude": lat if valid else 0,
                        "longitude": lon if valid else 0,
                        "speed": _traccar_number(position.get("speed")) or 0,
                        "course": _traccar_number(position.get("course")) or 0,
                        "address": position.get("address"),
                        "last_update": _traccar_datetime(position.get("fixTime"))
                        or values["last_update"],
                    }
                )
            if device:
                device.write(values)
            else:
                device = self.with_context(skip_traccar_remote_create=True).create(
                    values
                )
            device._sync_telemetry_device()

    def _sync_telemetry_device(self):
        TelemetryDevice = self.env["fleet.telemetry.device"]
        for device in self:
            external_ref = str(device.traccar_id or device.unique_id)
            values = {
                "company_id": device.company_id.id,
                "name": device.name,
                "provider": "traccar",
                "external_ref": external_ref,
                "vehicle_id": device.vehicle_id.id,
            }
            telemetry_device = device.telemetry_device_id
            if not telemetry_device:
                telemetry_device = TelemetryDevice.search(
                    [
                        ("company_id", "=", device.company_id.id),
                        ("provider", "=", "traccar"),
                        ("external_ref", "=", external_ref),
                    ],
                    limit=1,
                )
            if telemetry_device:
                telemetry_device.write(values)
            else:
                telemetry_device = TelemetryDevice.create(values)
            device.telemetry_device_id = telemetry_device.id
