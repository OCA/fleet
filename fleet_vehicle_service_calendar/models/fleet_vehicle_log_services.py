# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FleetVehicleLogServices(models.Model):
    _inherit = "fleet.vehicle.log.services"

    meeting_count = fields.Integer("# Meetings", compute="_compute_meeting_count")

    def _compute_meeting_count(self):
        meeting_data = self.env["calendar.event"].read_group(
            [("vehicle_service_id", "in", self.ids)],
            ["vehicle_service_id"],
            ["vehicle_service_id"],
        )
        mapped_data = {
            m["vehicle_service_id"][0]: m["vehicle_service_id_count"]
            for m in meeting_data
        }
        for record in self:
            record.meeting_count = mapped_data.get(record.id, 0)

    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current service.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        action = self.env.ref("calendar.action_calendar_event").read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.user_id:
            partner_ids += self.user_id.partner_id.ids
        action["context"] = {
            "default_vehicle_service_id": self.id,
            "default_partner_id": self.user_id.partner_id.id if self.user_id else False,
            "default_partner_ids": partner_ids,
            "default_name": "%s - %s"
            % (self.vehicle_id.name, self.cost_subtype_id.name),
            "search_default_vehicle_service_id": self.id,
        }
        return action

    def log_meeting(self, meeting_subject, meeting_date, duration):
        if not duration:
            duration = _("unknown")
        else:
            duration = str(duration)
        meet_date = fields.Datetime.from_string(meeting_date)
        meeting_usertime = fields.Datetime.to_string(
            fields.Datetime.context_timestamp(self, meet_date)
        )
        html_time = "<time datetime='{}+00:00'>{}</time>".format(
            meeting_date, meeting_usertime,
        )
        message = _(
            "Meeting scheduled at '%s'<br> Subject: %s <br> Duration: %s hours"
        ) % (html_time, meeting_subject, duration)
        return self.message_post(body=message)
