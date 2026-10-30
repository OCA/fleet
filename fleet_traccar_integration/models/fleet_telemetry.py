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
        created_count, _jobs = self._traccar_sync_devices(company, devices=devices)
        return created_count

    @api.model
    def _traccar_sync_devices(self, company, devices=None):
        """Download the positions received since the last stored point.

        Devices with a gap longer than the inline limit, or without any
        point yet, get a background history import instead, so the caller
        never waits for a long download.
        """
        Device = self.env["traccar.device"]
        Job = self.env["traccar.sync.job"]
        devices = devices or Device.search([("company_id", "=", company.id)])
        busy_devices = Job._get_active_jobs(devices).device_ids
        now = fields.Datetime.now()
        default_from = now - timedelta(days=max(company.traccar_history_days or 1, 1))
        inline_limit = timedelta(hours=max(company.traccar_inline_sync_hours or 1, 1))
        created_count = 0
        jobs = Job.browse()
        for device in devices - busy_devices:
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
            if now - date_from > inline_limit:
                jobs |= Job.create(
                    {
                        "company_id": company.id,
                        "device_ids": [(6, 0, device.ids)],
                        "date_from": date_from,
                        "date_to": now,
                    }
                )
                continue
            created, _updated = self._traccar_import_positions(
                company, device, date_from, now
            )
            created_count += created
        if jobs:
            jobs._trigger_processing()
        return created_count, jobs

    @api.model
    def _traccar_fetch_positions(self, company, device, date_from, date_to):
        params = {
            "deviceId": device.traccar_id or device.unique_id,
            "from": fields.Datetime.to_string(date_from).replace(" ", "T") + "Z",
            "to": fields.Datetime.to_string(date_to).replace(" ", "T") + "Z",
        }
        positions = company._traccar_request("GET", "/api/reports/route", params=params)
        if not positions:
            positions = company._traccar_request("GET", "/api/positions", params=params)
        if isinstance(positions, dict):
            raise UserError(positions.get("message") or str(positions))
        return positions or []

    @api.model
    def _traccar_import_positions(self, company, device, date_from, date_to):
        positions = self._traccar_fetch_positions(company, device, date_from, date_to)
        return self._traccar_store_positions(company, device, positions)

    @api.model
    def _prepare_traccar_values(self, company, device, item):
        position_id = item.get("id")
        return {
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
            "attributes": json.dumps(item.get("attributes") or {}, ensure_ascii=True),
        }

    def _prepare_traccar_merge_values(self, values):
        self.ensure_one()
        return {
            "server_time": _max_datetime(self.server_time, values["server_time"]),
            "external_position_ref": self.external_position_ref
            or values["external_position_ref"],
            "traccar_position_id": self.traccar_position_id
            or values["traccar_position_id"],
            "speed": self.speed or values["speed"],
            "course": self.course or values["course"],
            "altitude": self.altitude or values["altitude"],
            "address": self.address or values["address"],
            "attributes": self._merge_attributes(self.attributes, values["attributes"]),
        }

    @api.model
    def _traccar_position_key(self, fix_time, latitude, longitude):
        return (fix_time, round(latitude or 0, 7), round(longitude or 0, 7))

    @api.model
    def _traccar_store_positions(self, company, device, positions):
        """Store a batch of Traccar positions of one device.

        Existing points are found with a single query and merged, new points
        are created at once. Returns the number of created and updated points.
        """
        if not positions:
            return 0, 0
        values_list = [
            self._prepare_traccar_values(company, device, item) for item in positions
        ]
        position_ids = [
            values["traccar_position_id"]
            for values in values_list
            if values["traccar_position_id"]
        ]
        fix_times = [values["fix_time"] for values in values_list if values["fix_time"]]
        existing = self.search(
            [
                ("company_id", "=", company.id),
                ("provider", "=", "traccar"),
                "|",
                "|",
                ("traccar_position_id", "in", position_ids),
                ("external_position_ref", "in", [str(pid) for pid in position_ids]),
                "&",
                ("traccar_device_id", "=", device.id),
                ("fix_time", "in", fix_times),
            ]
        )
        by_position = {}
        by_key = {}
        for record in existing:
            for position_ref in (
                record.traccar_position_id,
                record.external_position_ref,
            ):
                if position_ref:
                    by_position[str(position_ref)] = record
            if record.traccar_device_id == device:
                key = self._traccar_position_key(
                    record.fix_time, record.latitude, record.longitude
                )
                by_key[key] = record
        to_create = []
        updated = self.browse()
        for values in values_list:
            position_ref = values["external_position_ref"]
            key = self._traccar_position_key(
                values["fix_time"], values["latitude"], values["longitude"]
            )
            record = (position_ref and by_position.get(position_ref)) or by_key.get(key)
            if isinstance(record, dict):
                # Repeated position inside the same batch
                continue
            if record:
                record.write(record._prepare_traccar_merge_values(values))
                updated |= record
                continue
            to_create.append(values)
            if position_ref:
                by_position[position_ref] = values
            by_key[key] = values
        if to_create:
            self.create(to_create)
        last_position = max(
            positions,
            key=lambda item: _traccar_datetime(item.get("fixTime")) or datetime.min,
        )
        device._traccar_update_last_position(last_position)
        return len(to_create), len(updated)
