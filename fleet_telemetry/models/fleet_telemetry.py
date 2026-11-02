import json

from odoo import api, fields, models


def _max_datetime(first, second):
    first = fields.Datetime.to_datetime(first) if first else False
    second = fields.Datetime.to_datetime(second) if second else False
    if first and second:
        return max(first, second)
    return first or second


class FleetTelemetry(models.Model):
    _name = "fleet.telemetry"
    _description = "Fleet Telemetry"
    _order = "fix_time desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", index=True)
    device_id = fields.Many2one(
        "fleet.telemetry.device", string="Telemetry Device", index=True
    )
    provider = fields.Char(required=True, index=True)
    external_device_ref = fields.Char(string="External Device Reference", index=True)
    external_position_ref = fields.Char(
        string="External Position Reference", index=True
    )
    fix_time = fields.Datetime(string="GPS Date", index=True)
    date_localization = fields.Datetime(
        string="Localization Date",
        compute="_compute_date_localization",
        store=True,
        index=True,
    )
    server_time = fields.Datetime(string="Server Date")
    latitude = fields.Float(digits=(10, 7))
    longitude = fields.Float(digits=(10, 7))
    speed = fields.Float()
    course = fields.Float()
    altitude = fields.Float()
    address = fields.Char()
    attributes = fields.Text(default="{}")
    route_day = fields.Date(compute="_compute_route_day", store=True, index=True)

    _sql_constraints = [
        (
            "fleet_telemetry_provider_position_unique",
            "unique(company_id, provider, external_position_ref)",
            "The external telemetry position must be unique per company and provider.",
        ),
    ]

    @api.depends("fix_time")
    def _compute_date_localization(self):
        for telemetry in self:
            telemetry.date_localization = telemetry.fix_time

    @api.depends("fix_time")
    def _compute_route_day(self):
        for telemetry in self:
            telemetry.route_day = (
                fields.Date.to_date(telemetry.fix_time) if telemetry.fix_time else False
            )

    def _merge_attributes(self, old_attributes, new_attributes):
        old_values = json.loads(old_attributes or "{}")
        new_values = json.loads(new_attributes or "{}")
        old_values.update(
            {key: value for key, value in new_values.items() if value is not None}
        )
        return json.dumps(old_values, ensure_ascii=True)

    @api.model
    def _merge_duplicate_telemetry(self):
        duplicates = self.read_group(
            [],
            ["provider", "device_id", "fix_time", "latitude", "longitude"],
            ["provider", "device_id", "fix_time", "latitude", "longitude"],
            lazy=False,
        )
        for group in duplicates:
            if (
                group["__count"] <= 1
                or not group.get("device_id")
                or not group.get("fix_time")
            ):
                continue
            records = self.search(group["__domain"], order="id")
            main = records[:1]
            for duplicate in records[1:]:
                vals = {
                    "server_time": _max_datetime(
                        main.server_time, duplicate.server_time
                    ),
                    "external_position_ref": main.external_position_ref
                    or duplicate.external_position_ref,
                    "speed": main.speed or duplicate.speed,
                    "course": main.course or duplicate.course,
                    "altitude": main.altitude or duplicate.altitude,
                    "address": main.address or duplicate.address,
                    "attributes": self._merge_attributes(
                        main.attributes, duplicate.attributes
                    ),
                }
                # Remove the duplicate first, as moving its external position
                # reference to main would violate the unique constraint
                duplicate.unlink()
                main.write(vals)
