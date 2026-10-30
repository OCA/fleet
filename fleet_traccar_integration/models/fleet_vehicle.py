from odoo import _, api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    traccar_device_id = fields.Many2one("traccar.device", string="Traccar Device")
    traccar_device_status = fields.Char(
        related="traccar_device_id.status", string="Traccar Status", readonly=True
    )
    traccar_last_update = fields.Datetime(
        related="traccar_device_id.last_update",
        string="Traccar Last Update",
        readonly=True,
    )
    traccar_latitude = fields.Float(related="traccar_device_id.latitude", readonly=True)
    traccar_longitude = fields.Float(
        related="traccar_device_id.longitude", readonly=True
    )
    traccar_speed = fields.Float(related="traccar_device_id.speed", readonly=True)
    traccar_telemetry_count = fields.Integer(compute="_compute_traccar_telemetry_count")

    @api.depends("traccar_device_id")
    def _compute_traccar_telemetry_count(self):
        grouped = self.env["fleet.telemetry"].read_group(
            [("provider", "=", "traccar"), ("vehicle_id", "in", self.ids)],
            ["vehicle_id"],
            ["vehicle_id"],
        )
        counts = {item["vehicle_id"][0]: item["vehicle_id_count"] for item in grouped}
        for vehicle in self:
            vehicle.traccar_telemetry_count = counts.get(vehicle.id, 0)

    def action_traccar_sync_locations(self):
        total = 0
        jobs = self.env["traccar.sync.job"]
        companies = self.mapped("company_id") or self.env.company
        for company in companies:
            self.env["traccar.device"].with_company(company)._sync_company_devices(
                company
            )
            company.traccar_last_device_sync = fields.Datetime.now()
            devices = self.mapped("traccar_device_id").filtered(
                lambda device, company=company: device.company_id == company
                and device.traccar_id
            )
            created, company_jobs = (
                self.env["fleet.telemetry"]
                .with_company(company)
                ._traccar_sync_devices(company, devices=devices or None)
            )
            total += created
            jobs |= company_jobs
            company.traccar_last_telemetry_sync = fields.Datetime.now()
        if jobs:
            # Long gaps are imported in background: show the progress instead
            return jobs._get_form_action()
        domain = [("provider", "=", "traccar")]
        if self:
            domain.append(("vehicle_id", "in", self.ids))
        existing = self.env["fleet.telemetry"].search_count(domain)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Traccar"),
                "message": _(
                    "Locations updated. New points: %(new)s. Total in Odoo: %(total)s",  # noqa: E501
                    new=total,
                    total=existing,
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def action_traccar_import_history(self):
        return self.env["traccar.history.import.wizard"]._get_wizard_action(
            self.mapped("traccar_device_id")
        )

    def action_view_traccar_telemetry(self):
        self.ensure_one()
        map_view = self.env.ref(
            "fleet_telemetry_maps.view_fleet_telemetry_map", raise_if_not_found=False
        )
        views = [(False, "list"), (False, "form")]
        view_mode = "list,form"
        if map_view:
            views = [(map_view.id, "leaflet_map")] + views
            view_mode = "leaflet_map,list,form"
        action = {
            "type": "ir.actions.act_window",
            "name": _("Traccar Telemetry"),
            "res_model": "fleet.telemetry",
            "view_mode": view_mode,
            "views": views,
            "domain": [("provider", "=", "traccar"), ("vehicle_id", "=", self.id)],
            "context": {"default_vehicle_id": self.id, "default_provider": "traccar"},
        }
        search_view = self.env.ref(
            "fleet_traccar_integration.view_traccar_telemetry_search",
            raise_if_not_found=False,
        )
        if search_view:
            action["search_view_id"] = search_view.id
        return action
