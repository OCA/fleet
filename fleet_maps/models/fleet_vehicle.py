from markupsafe import Markup

from odoo import _, api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    map_latitude = fields.Float(
        digits=(10, 7),
        compute="_compute_map_position",
        store=True,
        readonly=False,
    )
    map_longitude = fields.Float(
        digits=(10, 7),
        compute="_compute_map_position",
        store=True,
        readonly=False,
    )
    map_marker_title = fields.Char(compute="_compute_map_position", store=True)
    map_marker_address = fields.Char(compute="_compute_map_position", store=True)
    map_last_update = fields.Datetime(compute="_compute_map_position", store=True)
    date_localization = fields.Datetime(
        string="Localization Date", compute="_compute_map_position", store=True
    )
    map_has_position = fields.Boolean(
        string="Has Map Position", compute="_compute_map_position", store=True
    )
    map_url = fields.Char(string="Map URL", compute="_compute_map_preview")
    map_preview_html = fields.Html(
        string="Map", compute="_compute_map_preview", sanitize=False
    )

    @api.depends("name", "license_plate")
    def _compute_map_position(self):
        for vehicle in self:
            values = vehicle._get_map_position_values()
            vehicle.map_latitude = values.get("latitude") or 0
            vehicle.map_longitude = values.get("longitude") or 0
            vehicle.map_marker_title = (
                values.get("title") or vehicle.name or vehicle.license_plate
            )
            vehicle.map_marker_address = (
                values.get("address") or vehicle.license_plate or False
            )
            vehicle.map_last_update = values.get("last_update") or False
            vehicle.date_localization = values.get("last_update") or False
            vehicle.map_has_position = bool(
                values.get("latitude") and values.get("longitude")
            )

    def _get_map_position_values(self):
        """Return the values used to place the vehicle on the map.

        Modules providing position data (e.g. telemetry integrations) must
        override this method.
        """
        self.ensure_one()
        return {
            "latitude": False,
            "longitude": False,
            "title": self.name or self.license_plate,
            "address": self.license_plate,
            "last_update": False,
        }

    @api.depends(
        "map_latitude", "map_longitude", "map_marker_title", "map_has_position"
    )
    def _compute_map_preview(self):
        for vehicle in self:
            if not vehicle.map_has_position:
                vehicle.map_url = False
                vehicle.map_preview_html = Markup(
                    "<div class='alert alert-info'>%s</div>"
                ) % _("No map position available for this vehicle.")
                continue
            lat = vehicle.map_latitude
            lon = vehicle.map_longitude
            vehicle.map_url = (
                f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"
                f"#map=16/{lat}/{lon}"
            )
            # Markup % escapes the interpolated values: keep %-formatting here
            vehicle.map_preview_html = Markup(
                "<iframe src='https://www.openstreetmap.org/export/embed.html"  # noqa: E501, UP031
                "?bbox=%(lon_min)s%%2C%(lat_min)s%%2C%(lon_max)s%%2C%(lat_max)s"
                "&amp;layer=mapnik&amp;marker=%(lat)s%%2C%(lon)s' "
                "style='border:0;width:100%%;height:520px;border-radius:8px;' "
                "loading='lazy'></iframe>"
                "<p class='mt-2'><a href='%(url)s' target='_blank'>"
                "%(label)s</a></p>"
                % {
                    "lat": lat,
                    "lon": lon,
                    "lat_min": lat - 0.01,
                    "lat_max": lat + 0.01,
                    "lon_min": lon - 0.01,
                    "lon_max": lon + 0.01,
                    "url": vehicle.map_url,
                    "label": _("Open in OpenStreetMap"),
                }
            )

    def action_view_fleet_map(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Fleet Map"),
            "res_model": "fleet.vehicle",
            "view_mode": "leaflet_map,list,form",
            "domain": [
                ("map_has_position", "=", True),
            ],
            "context": {"create": False, "search_default_has_position": 1},
        }

    def action_view_vehicle_map(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Vehicle Map"),
            "res_model": "fleet.vehicle",
            "view_mode": "leaflet_map,form",
            "domain": [("id", "=", self.id), ("map_has_position", "=", True)],
            "res_id": self.id,
            "context": {"create": False},
        }
