from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestCalendarEvent(TransactionCase):
    def setUp(self):
        super(TestCalendarEvent, self).setUp()
        self.calendar_event = self.env["calendar.event"].create({"name": "Test Event"})
        self.brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Audi",
            }
        )
        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model", "brand_id": self.brand.id}
        )
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "ABC-1234",
                "odometer": 1000,
            }
        )

        self.service_type = self.env["fleet.service.type"].create(
            {"name": "Fatura do Fornecedor", "category": "service"}
        )
        self.vehicle_service = self.env["fleet.vehicle.log.services"].create(
            {
                "vehicle_id": self.vehicle.id,
                "notes": "Test notes",
                "service_type_id": self.service_type.id,
            }
        )

    def test_default_get(self):
        fields = ["vehicle_service_id"]
        self.calendar_event.env.context = {
            "default_vehicle_service_id": self.vehicle_service.id
        }
        defaults = self.calendar_event.default_get(fields)
        self.assertEqual(defaults["vehicle_service_id"], self.vehicle_service.id)

    def test_compute_is_highlighted(self):
        self.calendar_event.vehicle_service_id = self.vehicle_service
        self.calendar_event.env.context = {
            "active_model": "fleet.vehicle.log.services",
            "active_id": self.vehicle_service.id,
        }
        self.calendar_event._compute_is_highlighted()
        self.assertTrue(self.calendar_event.is_highlighted)

    def test_create_vehicle_service(self):
        meeting_name = "Meeting"
        meeting_start = datetime(2023, 4, 5, 10, 0, 0)
        meeting_duration = 1.0
        meeting_end = meeting_start + timedelta(hours=meeting_duration)

        activity_type = self.env.ref("mail.mail_activity_data_meeting")
        activity_vals = {
            "activity_type_id": activity_type.id,
            "user_id": self.env.uid,
            "res_model_id": self.env.ref("fleet.model_fleet_vehicle_log_services").id,
            "res_id": self.vehicle_service.id,
            "note": meeting_name,
            "date_deadline": meeting_start,
        }
        activity = self.env["mail.activity"].create(activity_vals)
        event = self.env["calendar.event"].create(
            {
                "name": meeting_name,
                "start": meeting_start,
                "stop": meeting_end,
                "vehicle_service_id": self.vehicle_service.id,
                "activity_ids": [(4, activity.id)],
            }
        )
        self.assertTrue(event.activity_ids)
        self.assertTrue(
            event.activity_ids.filtered(
                lambda activity: activity.activity_type_id.name == "Meeting"
            )
        )
        self.assertTrue(
            event.activity_ids.filtered(
                lambda activity: activity.activity_type_id.name == "Meeting"
            ).note,
            meeting_name,
        )
        self.assertTrue(
            event.activity_ids.filtered(
                lambda activity: activity.activity_type_id.name == "Meeting"
            ).date_deadline,
            meeting_start,
        )
        self.assertTrue(
            event.activity_ids.filtered(
                lambda activity: activity.activity_type_id.name == "Meeting"
            ).user_id,
            self.env.uid,
        )
        self.assertTrue(
            event.activity_ids.filtered(
                lambda activity: activity.activity_type_id.name == "Meeting"
            ).res_model_id,
            self.env.ref("fleet.model_fleet_vehicle_log_services").id,
        )
        self.assertTrue(
            event.activity_ids.filtered(
                lambda activity: activity.activity_type_id.name == "Meeting"
            ).res_id,
            self.vehicle_service.id,
        )


class TestFleetVehicleLogServices2(TransactionCase):
    def setUp(self):
        super(TestFleetVehicleLogServices2, self).setUp()

        self.brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Audi",
            }
        )
        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model", "brand_id": self.brand.id}
        )
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "ABC-1234",
                "odometer": 1000,
            }
        )

        self.service_type = self.env["fleet.service.type"].create(
            {"name": "Fatura do Fornecedor", "category": "service"}
        )
        self.vehicle_service = self.env["fleet.vehicle.log.services"].create(
            {
                "vehicle_id": self.vehicle.id,
                "notes": "Test notes",
                "service_type_id": self.service_type.id,
            }
        )

    def test_compute_meeting_count(self):
        self.env["calendar.event"].create(
            {
                "name": "Meeting 1",
                "start": "2023-04-06 10:00:00",
                "stop": "2023-04-06 11:00:00",
                "vehicle_service_id": self.vehicle_service.id,
            }
        )

        self.vehicle_service._compute_meeting_count()

        self.assertEqual(self.vehicle_service.meeting_count, 1)
