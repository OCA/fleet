# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FleetVehicleLogServices(models.Model):
    _inherit = "fleet.vehicle.log.services"

    meeting_count = fields.Integer("# Meetings", compute="_compute_meeting_count")

    def _compute_meeting_count(self):
        meeting_data = (
            self.env["calendar.event"]
            .sudo()
            ._read_group(
                [("vehicle_service_id", "in", self.ids)],
                ["vehicle_service_id"],
                ["__count"],
            )
        )
        mapped_data = {service.id: count for service, count in meeting_data}
        for record in self:
            record.meeting_count = mapped_data.get(record.id, 0)

    def action_schedule_meeting(self):
        """Open meeting's calendar view to schedule meeting on current service.
        :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "calendar.action_calendar_event"
        )
        partner_ids = self.env.user.partner_id.ids
        if self.user_id:
            partner_ids += self.user_id.partner_id.ids
        action["context"] = {
            "default_vehicle_service_id": self.id,
            "default_partner_id": self.user_id.partner_id.id if self.user_id else False,
            "default_partner_ids": partner_ids,
            "default_name": f"{self.vehicle_id.name} - {self.service_type_id.name}",
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
        html_time = f"<time datetime='{meeting_date}+00:00'>{meeting_usertime}</time>"
        message = _(
            "Meeting scheduled at '%(html_time)s'<br> "
            + "Subject: %(meeting_subject)s <br> "
            + "Duration: %(duration)s hours"
        ) % {
            "html_time": html_time,
            "meeting_subject": meeting_subject,
            "duration": duration,
        }
        return self.message_post(body=message)
