from datetime import datetime

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestFleetVehicle(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.brand = self.env.ref("fleet.brand_opel")

        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model 1", "brand_id": self.brand.id}
        )
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "name": "Test Vehicle",
                "model_id": self.vehicle_model.id,
                "driver_id": self.partner.id,
                "license_plate": "TEST123",
            }
        )

        self.inspection1 = self.env["fleet.vehicle.inspection"].create(
            {
                "name": "Inspection 1",
                "vehicle_id": self.vehicle.id,
                "date_inspected": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        self.inspection2 = self.env["fleet.vehicle.inspection"].create(
            {
                "name": "Inspection 2",
                "vehicle_id": self.vehicle.id,
                "date_inspected": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def test_action_view_inspection(self):

        self.vehicle.write(
            {"inspection_ids": [(6, 0, [self.inspection1.id, self.inspection2.id])]}
        )
        action = self.vehicle.action_view_inspection()
        self.assertEqual(len(action.get("domain")), 1)
        self.assertEqual(
            action.get("domain")[0],
            ("id", "in", [self.inspection1.id, self.inspection2.id]),
        )

        self.vehicle.write({"inspection_ids": [(6, 0, [self.inspection1.id])]})
        action = self.vehicle.action_view_inspection()
        self.assertEqual(len(action.get("views")), 1)
        self.assertEqual(
            action.get("views")[0][0],
            self.env.ref(
                "fleet_vehicle_inspection.fleet_vehicle_inspection_form_view"
            ).id,
        )
        self.assertEqual(action.get("res_id"), self.inspection1.id)

    def test_inverse_odometer(self):
        with self.assertRaises(UserError):
            self.inspection1.odometer = 0

        odometer_value = 100
        self.inspection1.odometer = odometer_value
        self.assertTrue(self.inspection1.odometer_id)
        self.assertEqual(self.inspection1.odometer_id.value, odometer_value)
        self.assertEqual(self.inspection1.odometer_id.date, fields.Date.today())
        self.assertEqual(self.inspection1.odometer_id.vehicle_id.id, self.vehicle.id)


class TestFleetVehicleInspection(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.brand = self.env.ref("fleet.brand_opel")

        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model 1", "brand_id": self.brand.id}
        )
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "name": "Test Vehicle",
                "model_id": self.vehicle_model.id,
                "driver_id": self.partner.id,
                "license_plate": "TEST123",
            }
        )
        self.inspection = self.env["fleet.vehicle.inspection"].create(
            {
                "name": "Inspeção de teste",
                "vehicle_id": self.vehicle.id,
                "state": "draft",
                "date_inspected": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        self.inspection_item_id = self.env["fleet.vehicle.inspection.item"].create(
            {"name": "Test", "instruction": "Test"}
        )
        self.inspection_line = self.env["fleet.vehicle.inspection.line"].create(
            {
                "inspection_item_id": self.inspection_item_id.id,
                "inspection_id": self.inspection.id,
                "result": "success",
            }
        )

    def test_button_confirm(self):

        self.inspection.button_confirm()
        self.assertEqual(self.inspection.state, "confirmed")
        self.inspection_line.write({"result": "success"})

        with self.assertRaises(UserError):
            self.inspection.button_confirm()
        self.inspection.write({"state": "confirmed"})
        with self.assertRaises(ValidationError):
            self.inspection.button_confirm()
