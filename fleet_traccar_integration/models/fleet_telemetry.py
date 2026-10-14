import json
import math
from datetime import datetime, timedelta, timezone

from odoo import api, fields, models
from odoo.exceptions import UserError


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


def _max_datetime(first, second):
    first = fields.Datetime.to_datetime(first) if first else False
    second = fields.Datetime.to_datetime(second) if second else False
    if first and second:
        return max(first, second)
    return first or second


class FleetTelemetry(models.Model):
    _inherit = "fleet.telemetry"

    traccar_device_id = fields.Many2one(
        "traccar.device", string="Traccar Device", index=True
    )
    traccar_position_id = fields.Integer(string="Traccar Position ID", index=True)

    @api.model
    def _sync_company_telemetry(self, company, devices=None):
        Device = self.env["traccar.device"]
        devices = devices or Device.search([("company_id", "=", company.id)])
        now = fields.Datetime.now()
        default_from = now - timedelta(days=max(company.traccar_history_days or 1, 1))
        created_count = 0
        for device in devices:
            device._sync_telemetry_device()
            last = self.search(
                [
                    ("company_id", "=", company.id),
                    ("provider", "=", "traccar"),
                    ("traccar_device_id", "=", device.id),
                ],
                order="fix_time desc",
                limit=1,
            )
            date_from = last.fix_time or default_from
            params = {
                "deviceId": device.traccar_id or device.unique_id,
                "from": fields.Datetime.to_string(date_from).replace(" ", "T") + "Z",
                "to": fields.Datetime.to_string(now).replace(" ", "T") + "Z",
            }
            positions = company._traccar_request(
                "GET", "/api/reports/route", params=params
            )
            if not positions:
                positions = company._traccar_request(
                    "GET", "/api/positions", params=params
                )
            if isinstance(positions, dict):
                raise UserError(positions.get("message") or str(positions))
            if not positions:
                continue
            for item in positions:
                position_id = item.get("id")
                values = {
                    "company_id": company.id,
                    "provider": "traccar",
                    "vehicle_id": device.vehicle_id.id,
                    "device_id": device.telemetry_device_id.id,
                    "traccar_device_id": device.id,
                    "external_device_ref": str(device.traccar_id or device.unique_id),
                    "external_position_ref": str(position_id) if position_id else False,
                    "traccar_position_id": position_id,
                    "fix_time": _traccar_datetime(item.get("fixTime")),
                    "server_time": _traccar_datetime(item.get("serverTime")),
                    "latitude": _traccar_number(item.get("latitude")) or 0,
                    "longitude": _traccar_number(item.get("longitude")) or 0,
                    "speed": _traccar_number(item.get("speed")) or 0,
                    "course": _traccar_number(item.get("course")) or 0,
                    "altitude": _traccar_number(item.get("altitude")) or 0,
                    "address": item.get("address"),
                    "attributes": json.dumps(
                        item.get("attributes") or {}, ensure_ascii=True
                    ),
                }
                existing = self.search(
                    [
                        ("company_id", "=", company.id),
                        ("provider", "=", "traccar"),
                        ("traccar_device_id", "=", device.id),
                        ("fix_time", "=", values["fix_time"]),
                        ("latitude", "=", values["latitude"]),
                        ("longitude", "=", values["longitude"]),
                    ],
                    limit=1,
                )
                if not existing and position_id:
                    existing = self.search(
                        [
                            ("company_id", "=", company.id),
                            ("provider", "=", "traccar"),
                            ("traccar_position_id", "=", position_id),
                        ],
                        limit=1,
                    )
                if existing:
                    existing.write(
                        {
                            "server_time": _max_datetime(
                                existing.server_time, values["server_time"]
                            ),
                            "external_position_ref": existing.external_position_ref
                            or values["external_position_ref"],
                            "traccar_position_id": existing.traccar_position_id
                            or position_id,
                            "speed": existing.speed or values["speed"],
                            "course": existing.course or values["course"],
                            "altitude": existing.altitude or values["altitude"],
                            "address": existing.address or values["address"],
                            "attributes": self._merge_attributes(
                                existing.attributes, values["attributes"]
                            ),
                        }
                    )
                else:
                    self.create(values)
                    created_count += 1
            last_position = positions[-1]
            device.write(
                {
                    "latitude": _traccar_number(last_position.get("latitude")) or 0,
                    "longitude": _traccar_number(last_position.get("longitude")) or 0,
                    "speed": _traccar_number(last_position.get("speed")) or 0,
                    "course": _traccar_number(last_position.get("course")) or 0,
                    "address": last_position.get("address"),
                    "last_update": _traccar_datetime(last_position.get("fixTime")),
                }
            )
        return created_count
