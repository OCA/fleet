# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from odoo.exceptions import UserError
from odoo.tests import Form

from .common import TestFleetVehicleLogFuelBase


class TestFleetVehicleLogFuelMisc(TestFleetVehicleLogFuelBase):
    def test_fleet_vehicle_log_fuel_process(self):
        fuel_form = Form(
            self.env["fleet.vehicle.log.fuel"].with_context(
                default_vehicle_id=self.vehicle.id
            )
        )
        with self.assertRaises(UserError):
            fuel_form.odometer = 0
            fuel_form.save()
        fuel_form.odometer = 5000
        fuel = fuel_form.save()
        self.assertTrue(fuel.odometer_id)
        self.assertEqual(self.vehicle.odometer, 5000)
        self.assertEqual(self.vehicle.fuel_count, 1)
        res = self.vehicle.action_view_log_fuel()
        items = self.env[res["res_model"]].search(res["domain"])
        self.assertIn(fuel, items)
        fuel.button_running()
        self.assertEqual(fuel.state, "running")
        fuel.button_done()
        self.assertEqual(fuel.state, "done")
        self.assertTrue(fuel.service_id)
        self.assertEqual(fuel.service_id.service_type_id, fuel.service_type_id)
        self.assertEqual(fuel.service_id.state, "done")
        fuel.button_cancel()
        self.assertEqual(fuel.state, "cancelled")
        self.assertFalse(fuel.service_id)
        fuel.button_todo()
        self.assertEqual(fuel.state, "todo")

    def test_fleet_vehicle_log_fuel_onchange(self):
        # Check amount
        fuel_form_1 = Form(
            self.env["fleet.vehicle.log.fuel"].with_context(
                default_vehicle_id=self.vehicle.id
            )
        )
        fuel_form_1.liter = 50
        fuel_form_1.price_per_liter = 1.5
        self.assertEqual(fuel_form_1.amount, 75)
        # Check price_per_liter
        fuel_form_2 = Form(
            self.env["fleet.vehicle.log.fuel"].with_context(
                default_vehicle_id=self.vehicle.id
            )
        )
        fuel_form_2.amount = 75
        fuel_form_2.liter = 50
        self.assertEqual(fuel_form_2.price_per_liter, 1.5)
        # Check liter
        fuel_form_2 = Form(
            self.env["fleet.vehicle.log.fuel"].with_context(
                default_vehicle_id=self.vehicle.id
            )
        )
        fuel_form_2.amount = 75
        fuel_form_2.price_per_liter = 1.5
        self.assertEqual(fuel_form_2.liter, 50)


class TestFleetVehicleLogFuelReport(TestFleetVehicleLogFuelBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create log fuel + log service to check report after
        fuel = cls.env["fleet.vehicle.log.fuel"].create(
            {
                "vehicle_id": cls.vehicle.id,
                "date": "2024-01-01",
                "amount": 75,
                "price_per_liter": 1.5,
                "liter": 50,
            }
        )
        fuel.button_running()
        fuel.button_done()

    def test_fleet_vehicle_cost_report(self):
        items = self.env["fleet.vehicle.cost.report"].search(
            [("vehicle_id", "=", self.vehicle.id), ("date_start", "=", "2024-01-01")]
        )
        self.assertIn("fuel", items.mapped("cost_type"))
        self.assertEqual(
            sum(items.filtered(lambda x: x.cost_type == "fuel").mapped("cost")), 75
        )
