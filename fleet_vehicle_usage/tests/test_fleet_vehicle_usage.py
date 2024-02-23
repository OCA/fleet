# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestFleetVehicleUsage(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        cls.model = cls.env["fleet.vehicle.model"].create(
            {
                "name": "Test model",
                "brand_id": cls.brand.id,
                "vehicle_type": "car",
            }
        )
        cls.vehicle = cls.env["fleet.vehicle"].create({"model_id": cls.model.id})
        cls.user = cls.env.ref("base.user_demo")

    def _create_fleet_vehicle_usage(self, vehicle):
        return self.env["fleet.vehicle.usage"].create(
            {"vehicle_id": vehicle.id, "user_id": self.user.id}
        )

    def test_fleet_vehicle_usage(self):
        usage = self._create_fleet_vehicle_usage(self.vehicle)
        self.assertFalse(self.vehicle.in_use)
        usage.action_pick()
        self.assertTrue(usage.date_picking)
        self.assertTrue(self.vehicle.in_use)
        usage.action_return()
        self.assertTrue(usage.date_return)
        self.assertFalse(self.vehicle.in_use)

    def test_fleet_vehicle_usage_constrain_1(self):
        usage = self._create_fleet_vehicle_usage(self.vehicle)
        usage.action_pick()
        with self.assertRaises(UserError):
            usage2 = self._create_fleet_vehicle_usage(self.vehicle)
            usage2.action_pick()

    def test_fleet_vehicle_usage_constrain_2(self):
        usage = self._create_fleet_vehicle_usage(self.vehicle)
        usage.action_pick()
        vehicle2 = self.vehicle.copy()
        with self.assertRaises(UserError):
            usage2 = self._create_fleet_vehicle_usage(vehicle2)
            usage2.action_pick()
