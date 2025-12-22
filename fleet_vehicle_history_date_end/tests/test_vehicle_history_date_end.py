# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestFleetVehicleDateEnd(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Brand Test"})
        cls.model = cls.env["fleet.vehicle.model"].create(
            {"name": "Model Test", "brand_id": cls.brand.id}
        )
        cls.driver1 = cls.env["res.partner"].create({"name": "Driver 1"})
        cls.driver2 = cls.env["res.partner"].create({"name": "Driver 2"})
        cls.future_driver = cls.env["res.partner"].create({"name": "Future Driver"})
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.model.id,
                "driver_id": cls.driver1.id,
                "plan_to_change_car": False,
            }
        )

    def test_change_driver_history_date_end(self):
        """Check correct assignation of date_end in history of previous driver."""
        first_log = self.vehicle.log_drivers[0]
        self.assertFalse(first_log.date_end)
        self.vehicle.write({"driver_id": self.driver2.id})
        last_log = self.vehicle.log_drivers[0]
        self.assertEqual(first_log.date_end, last_log.date_start)

    def test_apply_future_driver(self):
        """Check correct assignation of date_end in previos history log
        when press button to apply future driver."""
        first_log = self.vehicle.log_drivers[0]
        self.vehicle.write({"future_driver_id": self.future_driver.id})
        self.assertFalse(first_log.date_end)
        self.vehicle.action_accept_driver_change()
        last_log = self.vehicle.log_drivers[0]
        self.assertEqual(first_log.date_end, last_log.date_start)
