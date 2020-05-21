# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.fleet_vehicle_service_kanban.tests.common import (
    TestVehicleLogServicesCommon,
)


class TestVehicleServiceCalendar(TestVehicleLogServicesCommon):
    def test_service_calendar_meeting(self):
        """Check correct creation of meeting for service."""
        smartbutton_action = self.service_repair.action_schedule_meeting()
        service_meeting = (
            self.env["calendar.event"]
            .with_context(smartbutton_action["context"])
            .create(
                {
                    "start": datetime.now(),
                    "stop": datetime.now() + relativedelta(hours=1),
                }
            )
        )
        self.assertEqual(service_meeting.vehicle_service_id, self.service_repair)
        meeting_subject = "{} - {}".format(
            self.service_repair.vehicle_id.name,
            self.service_repair.cost_subtype_id.name,
        )
        self.assertEqual(service_meeting.name, meeting_subject)
