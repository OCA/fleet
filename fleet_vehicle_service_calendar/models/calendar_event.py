# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    vehicle_service_id = fields.Many2one(
        "fleet.vehicle.log.services", "Vehicle Service"
    )

    @api.model
    def default_get(self, fields):
        if self.env.context.get("default_vehicle_service_id"):
            self = self.with_context(
                default_res_model_id=self.env.ref(
                    "fleet.model_fleet_vehicle_log_services"
                ).id,
                default_res_id=self.env.context["default_vehicle_service_id"],
            )
        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to service id
        # (aka creating meeting from service chatter)
        ctx = self.env.context
        if "vehicle_service_id" not in defaults and \
                defaults.get("res_model") == 'fleet.vehicle.log.services':
            defaults["vehicle_service_id"] = defaults.get("res_id", False) or ctx.get(
                "default_res_id", False
            )

        return defaults

    def _compute_is_highlighted(self):
        super(CalendarEvent, self)._compute_is_highlighted()
        if self.env.context.get("active_model") == "fleet.vehicle.log.services":
            vehicle_service_id = self.env.context.get("active_id")
            for event in self:
                if event.vehicle_service_id.id == vehicle_service_id:
                    event.is_highlighted = True

    @api.model
    def create(self, vals):
        event = super(CalendarEvent, self).create(vals)

        if event.vehicle_service_id and not event.activity_ids:
            event.vehicle_service_id.log_meeting(
                event.name, event.start, event.duration
            )
        return event
