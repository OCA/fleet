# Copyright 2020 - 2024, Marcel Savegnago - Escodoo
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestFleetVehicleInspection(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.driver = cls.env["res.partner"].create({"name": "Test Driver"})
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        cls.model = cls.env["fleet.vehicle.model"].create(
            {
                "name": "Test model",
                "brand_id": cls.brand.id,
            }
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.model.id,
                "driver_id": cls.driver.id,
                "license_plate": "TEST123",
            }
        )
        cls.item_lights = cls.env.ref(
            "fleet_vehicle_inspection.fleet_vehicle_inspection_item_demo_1"
        )
        cls.item_mirrors = cls.env.ref(
            "fleet_vehicle_inspection.fleet_vehicle_inspection_item_demo_2"
        )
        cls.inspection = cls.env["fleet.vehicle.inspection"]
        cls.inspection = cls.inspection.create(
            {
                "vehicle_id": cls.vehicle.id,
                "inspection_line_ids": [
                    (
                        0,
                        0,
                        {"inspection_item_id": cls.item_lights.id},
                    ),
                    (
                        0,
                        0,
                        {"inspection_item_id": cls.item_mirrors.id},
                    ),
                ],
            }
        )
        cls.inspection2 = cls.inspection.create({"vehicle_id": cls.vehicle.id})
        cls.service_type = cls.env["fleet.service.type"].create(
            {
                "name": "Test service",
                "category": "service",
            }
        )

    def test_inverse_odometer(self):
        inspection = self.inspection.create(
            {
                "name": "Extra inspection",
                "vehicle_id": self.vehicle.id,
                "date_inspected": "2023-01-01",
            }
        )
        with self.assertRaises(UserError):
            inspection.odometer = 0
        inspection.odometer = 100
        self.assertTrue(inspection.odometer_id)
        self.assertEqual(inspection.odometer_id.value, 100)
        self.assertEqual(
            inspection.odometer_id.date, fields.Date.from_string("2023-01-01")
        )
        self.assertEqual(inspection.odometer_id.vehicle_id.id, self.vehicle.id)

    def test_fleet_vehicle_action_view_inspection(self):
        action = self.vehicle.action_view_inspection()
        self.assertEqual(len(action.get("domain")), 1)
        self.assertEqual(
            action.get("domain")[0],
            ("id", "in", [self.inspection.id, self.inspection2.id]),
        )
        self.inspection2.unlink()
        action = self.vehicle.action_view_inspection()
        self.assertEqual(len(action.get("views")), 1)
        self.assertEqual(
            action.get("views")[0][0],
            self.env.ref(
                "fleet_vehicle_inspection.fleet_vehicle_inspection_form_view"
            ).id,
        )
        self.assertEqual(action.get("res_id"), self.inspection.id)

    def test_fleet_vehicle_inspection_button_confirm(self):
        inspection = self.inspection.create(
            {
                "name": "Extra inspection",
                "vehicle_id": self.vehicle.id,
                "state": "draft",
                "date_inspected": "2023-01-01",
                "inspection_line_ids": [
                    (
                        0,
                        0,
                        {
                            "inspection_item_id": self.item_lights.id,
                            "result": "success",
                        },
                    ),
                ],
            }
        )
        inspection.button_confirm()
        self.assertEqual(inspection.state, "confirmed")
        inspection.inspection_line_ids.result = "success"
        with self.assertRaises(UserError):
            inspection.button_confirm()
        inspection.state = "confirmed"
        with self.assertRaises(ValidationError):
            inspection.button_confirm()

    def test_fleet_vehicle_inspection_full_process(self):
        self.assertTrue(self.inspection.name)
        self.assertEqual(self.inspection.result, "todo")
        # inspection confirm not completed
        with self.assertRaises(UserError):
            self.inspection.button_confirm()
        self.assertEqual(self.inspection.vehicle_id.inspection_count, 2)
        inspection_line_lights = self.inspection.inspection_line_ids.filtered(
            lambda x: x.inspection_item_id == self.item_lights
        )
        inspection_line_mirrors = self.inspection.inspection_line_ids.filtered(
            lambda x: x.inspection_item_id == self.item_mirrors
        )
        inspection_line_lights.action_item_success()
        self.assertEqual(self.inspection.result, "todo")
        inspection_line_mirrors.action_item_success()
        self.assertEqual(self.inspection.result, "success")
        inspection_line_mirrors.action_item_failure()
        self.assertEqual(self.inspection.result, "failure")
        self.inspection.button_confirm()
        self.assertEqual(self.inspection.state, "confirmed")
        self.inspection.button_cancel()
        self.assertEqual(self.inspection.state, "cancel")
        self.inspection.button_draft()
        self.assertEqual(self.inspection.state, "draft")
        self.assertEqual(self.inspection2.result, "todo")
        # inspection2 confirm without items
        with self.assertRaises(UserError):
            self.inspection2.button_confirm()

    def test_fleet_vehicle_inspection_with_amount(self):
        self.inspection.inspection_line_ids.action_item_success()
        self.inspection.amount = 100
        self.inspection.vendor_id = self.vendor
        with self.assertRaisesRegex(ValidationError, "Must select service type"):
            self.inspection.button_confirm()
        self.inspection.service_type_id = self.service_type
        self.inspection.button_confirm()
        self.assertEqual(self.inspection.service_id.description, self.inspection.name)
        self.assertEqual(self.inspection.service_id.vendor_id, self.vendor)
        self.assertEqual(self.inspection.service_id.vehicle_id, self.vehicle)
        self.assertEqual(self.inspection.service_id.odometer, self.inspection.odometer)
        self.assertEqual(self.inspection.service_id.service_type_id, self.service_type)
        self.assertEqual(self.inspection.service_id.amount, self.inspection.amount)
        self.assertEqual(self.inspection.service_id.state, "done")
        self.inspection.button_cancel()
        self.assertFalse(self.inspection.service_id)
