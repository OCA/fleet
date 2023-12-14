# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestVehicleServiceActivity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vehicle = cls.env.ref("fleet.vehicle_1")
        cls.user = new_test_user(cls.env, "test base user", groups="base.group_user")
        cls.user2 = new_test_user(cls.env, "test base user 2", groups="base.group_user")
        cls.vehicle.manager_id = cls.user.id
        cls.service_type = cls.env["fleet.service.type"].create(
            {"name": "Service Type Test", "category": "service"}
        )

    def test_scheduler_manage_service_date(self):
        # Create a service with a date that is outdated based on the delay_alert_service
        service_date = datetime.now() - relativedelta(days=35)
        service = self.env["fleet.vehicle.log.services"].create(
            {
                "description": "Test Service",
                "vehicle_id": self.vehicle.id,
                "date": service_date,
                "state": "running",
                "service_type_id": self.service_type.id,
            }
        )
        # Run the scheduler
        self.env["fleet.vehicle.log.services"]._cron_manage_service_date()

        self.assertEqual(service.activity_ids[0].user_id, self.user)
        self.assertEqual(
            service.activity_ids[0].activity_type_id.id,
            self.ref("fleet_vehicle_service_activity.mail_act_fleet_service_to_check"),
        )

        self.vehicle.manager_id = self.user2.id
        service2 = self.env["fleet.vehicle.log.services"].create(
            {
                "description": "Test Service 2",
                "vehicle_id": self.vehicle.id,
                "date": service_date,
                "state": "done",
                "service_type_id": self.service_type.id,
            }
        )
        # Run the scheduler
        self.env["fleet.vehicle.log.services"]._cron_manage_service_date()
        self.assertEqual(len(service2.activity_ids), 0)
