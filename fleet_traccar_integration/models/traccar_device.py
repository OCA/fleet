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
        total = 0
        for company in self.mapped("company_id") or self.env.company:
            devices = self.filtered(
                lambda device, company=company: device.company_id == company
            )
            total += (
                self.env["fleet.telemetry"]
                .with_company(company)
                ._sync_company_telemetry(company, devices=devices)
            )
            company.traccar_last_telemetry_sync = fields.Datetime.now()
        existing = self.env["fleet.telemetry"].search_count(
            [("provider", "=", "traccar"), ("traccar_device_id", "in", self.ids)]
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Traccar"),
                "message": _(
                    "History updated. New points: %(new)s. Total in Odoo: %(total)s",  # noqa: E501
                    new=total,
                    total=existing,
                ),
                "type": "success",
                "sticky": False,
            },
        }

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
