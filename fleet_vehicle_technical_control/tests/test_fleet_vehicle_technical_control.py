# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFleetVehicleTechnicalControl(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Vehicle = cls.env["fleet.vehicle"]
        cls.TechnicalControl = cls.env["fleet.vehicle.technical.control"]
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test Brand"})
        cls.model = cls.env["fleet.vehicle.model"].create(
            {"name": "Test Model", "brand_id": cls.brand.id}
        )

    def _create_vehicle(self, **values):
        vals = {"model_id": self.model.id, "license_plate": "TC-001"}
        vals.update(values)
        return self.Vehicle.create(vals)

    def test_vehicle_default_frequency_and_next_control_date(self):
        vehicle = self._create_vehicle()
        self.TechnicalControl.create(
            {"vehicle_id": vehicle.id, "date": "2026-01-15", "result": "valid"}
        )

        self.assertEqual(vehicle.technical_control_every_months, 12)
        self.assertTrue(
            self.Vehicle._fields["date_last_technical_control"].store,
            "Last technical control date must be stored.",
        )
        self.assertFalse(
            self.Vehicle._fields["date_next_technical_control"].store,
            "Next technical control date must not be stored.",
        )
        self.assertEqual(vehicle.date_last_technical_control, date(2026, 1, 15))
        self.assertEqual(vehicle.date_next_technical_control, date(2027, 1, 15))

        vehicle.technical_control_every_months = 6
        self.assertEqual(vehicle.date_next_technical_control, date(2026, 7, 15))

    def test_negative_frequency_is_rejected(self):
        with self.assertRaisesRegex(
            ValidationError,
            "Technical control frequency must be greater than or equal to 0",
        ):
            self._create_vehicle(technical_control_every_months=-1)

    def test_not_valid_control_requires_comment(self):
        vehicle = self._create_vehicle()

        with self.assertRaisesRegex(
            ValidationError,
            "A comment is required when the technical control is not valid",
        ):
            self.TechnicalControl.create(
                {"vehicle_id": vehicle.id, "date": "2026-02-01", "result": "not_valid"}
            )

    def test_last_control_date_is_max_history_date(self):
        vehicle = self._create_vehicle()

        recent_control = self.TechnicalControl.create(
            {"vehicle_id": vehicle.id, "date": "2026-03-10", "result": "valid"}
        )
        old_control = self.TechnicalControl.create(
            {"vehicle_id": vehicle.id, "date": "2026-01-05", "result": "valid"}
        )

        self.assertEqual(vehicle.date_last_technical_control, date(2026, 3, 10))
        self.assertIn(recent_control, vehicle.technical_control_ids)
        self.assertIn(old_control, vehicle.technical_control_ids)

    def test_action_technical_control_done(self):
        vehicle = self._create_vehicle()

        action = vehicle.action_technical_control_done()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "fleet.vehicle.technical.control")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_vehicle_id"], vehicle.id)
