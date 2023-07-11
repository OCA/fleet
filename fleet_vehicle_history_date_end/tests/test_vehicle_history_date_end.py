# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFleetVehicleDateEnd(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestFleetVehicleDateEnd, cls).setUpClass()
        cls.vehicle = cls.env.ref("fleet.vehicle_1")

    def test_change_driver_history_date_end(self):
        """Check correct assignation of date_end in history of previous driver."""
        first_log = self.vehicle.log_drivers
        self.assertFalse(first_log.date_end)
        self.vehicle.write(
            {"driver_id": self.env.ref("base.res_partner_address_25").id}
        )
        last_log = self.vehicle.log_drivers[0]
        self.assertEqual(first_log.date_end, last_log.date_start)

    def test_apply_future_driver(self):
        """Check correct assignation of date_end in previos history log
        when press button to apply future driver."""
        first_log = self.vehicle.log_drivers
        self.vehicle.write(
            {"future_driver_id": self.env.ref("base.res_partner_address_17").id}
        )
        self.assertFalse(first_log.date_end)
        self.vehicle.action_accept_driver_change()
        last_log = self.vehicle.log_drivers[0]
        self.assertEqual(first_log.date_end, last_log.date_start)
