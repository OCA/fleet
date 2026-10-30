from odoo import _, api, fields, models


class FleetTelemetry(models.Model):
    _inherit = "fleet.telemetry"

    route_color = fields.Char(compute="_compute_route_color")
    map_marker_title = fields.Char(string="Map Title", compute="_compute_map_fields")
    map_marker_address = fields.Char(
        string="Map Address", compute="_compute_map_fields"
    )

    @api.depends("route_day")
    def _compute_route_color(self):
        colors = [
            "#017e84",
            "#875a7b",
            "#dc3545",
            "#ff9800",
            "#198754",
            "#0d6efd",
            "#6f42c1",
        ]
        for telemetry in self:
            telemetry.route_color = colors[
                (telemetry.route_day.toordinal() if telemetry.route_day else 0)
                % len(colors)
            ]

    @api.depends("device_id", "provider", "fix_time", "address", "speed")
    def _compute_map_fields(self):
        for telemetry in self:
            title = (
                telemetry.device_id.display_name or telemetry.provider or _("Telemetry")
            )
            fix_time = (
                fields.Datetime.to_string(telemetry.fix_time)
                if telemetry.fix_time
                else ""
            )
            telemetry.map_marker_title = f"{title} - {fix_time}"
            telemetry.map_marker_address = telemetry.address or _(
                "Speed: %s", telemetry.speed or 0
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._recompute_vehicle_map_position()
        return records

    def write(self, vals):
        result = super().write(vals)
        if {
            "vehicle_id",
            "latitude",
            "longitude",
            "fix_time",
            "address",
            "provider",
        } & set(vals):
            self._recompute_vehicle_map_position()
        return result

    def _recompute_vehicle_map_position(self):
        vehicles = self.mapped("vehicle_id")
        if not vehicles:
            return
        for field_name in [
            "map_latitude",
            "map_longitude",
            "map_marker_title",
            "map_marker_address",
            "map_last_update",
            "date_localization",
            "map_has_position",
        ]:
            if field_name in vehicles._fields:
                self.env.add_to_compute(vehicles._fields[field_name], vehicles)
        vehicles._recompute_recordset()
