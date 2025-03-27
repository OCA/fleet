# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestVehicleServiceActivity(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vehicle = cls.env.ref("fleet.vehicle_1")
        cls.user = new_test_user(cls.env, "test base user")
        cls.user2 = new_test_user(cls.env, "test base user 2")
        cls.vehicle.manager_id = cls.user
        cls.service_type = cls.env["fleet.service.type"].create(
            {"name": "Service Type Test", "category": "service"}
        )

    def _create_log_service(self, date, state):
        return self.env["fleet.vehicle.log.services"].create(
            {
                "description": f"Test Service ({state})",
                "vehicle_id": self.vehicle.id,
                "date": date,
                "state": state,
                "service_type_id": self.service_type.id,
            }
        )

    @freeze_time("2024-01-01")
    def test_scheduler_manage_service_date(self):
        service1 = self._create_log_service("2024-02-10", "running")
        self.assertFalse(service1.activity_ids)
        # Run the scheduler (1)
        self.env["fleet.vehicle.log.services"]._cron_manage_service_date()
        self.assertFalse(service1.activity_ids)
        # Change the date to an older date
        service1.date = "2024-01-15"
        # Run the scheduler again (2)
        self.env["fleet.vehicle.log.services"]._cron_manage_service_date()
        self.assertEqual(len(service1.activity_ids), 1)
        self.assertEqual(service1.activity_ids.user_id, self.user)
        self.assertEqual(
            service1.activity_ids.activity_type_id.id,
            self.ref("fleet_vehicle_service_activity.mail_act_fleet_service_to_check"),
        )
        # Run the scheduler again (3)
        self.env["fleet.vehicle.log.services"]._cron_manage_service_date()
        self.assertEqual(len(service1.activity_ids), 1)
        # Set manager + new done log service
        self.vehicle.manager_id = self.user2
        service2 = self._create_log_service("2024-01-20", "done")
        # Run the scheduler
        self.env["fleet.vehicle.log.services"]._cron_manage_service_date()
        self.assertEqual(len(service2.activity_ids), 0)
