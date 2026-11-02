from odoo import api, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    @api.depends("name", "license_plate")
    def _compute_map_position(self):
        return super()._compute_map_position()

    def _get_map_position_values(self):
        values = super()._get_map_position_values()
        telemetry = self.env["fleet.telemetry"].search(
            [
                ("vehicle_id", "=", self.id),
                ("latitude", "!=", 0),
                ("longitude", "!=", 0),
            ],
            order="fix_time desc, id desc",
            limit=1,
        )
        if not telemetry:
            return values
        values.update(
            {
                "latitude": telemetry.latitude,
                "longitude": telemetry.longitude,
                "last_update": telemetry.fix_time,
                "title": self.name or self.license_plate,
                "address": telemetry.address or telemetry.provider,
            }
        )
        return values
