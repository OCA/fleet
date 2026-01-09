# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import fields

# Corrected import for Odoo 18 - Form is no longer needed here
from odoo.tests import TransactionCase


class TestFleetVehicleAssignationLogDatetime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test Brand"})
        model = cls.env["fleet.vehicle.model"].create(
            {"brand_id": brand.id, "name": "Test Model"}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": model.id,
                "license_plate": "TEST-123",
            }
        )
        cls.driver1 = cls.env["res.partner"].create({"name": "Test Driver 1"})
        cls.driver2 = cls.env["res.partner"].create({"name": "Test Driver 2"})

    # ... (os testes 01, 02, 03 e 04 permanecem exatamente os mesmos) ...
    def test_01_driver_change_updates_datetimes(self):
        """
        Test that changing a vehicle's driver correctly sets the start and end
        datetimes on the assignation logs.
        """
        self.vehicle.write({"driver_id": self.driver1.id})
        log1 = self.env["fleet.vehicle.assignation.log"].search(
            [("vehicle_id", "=", self.vehicle.id), ("driver_id", "=", self.driver1.id)]
        )
        self.assertEqual(len(log1), 1)
        self.assertTrue(log1.datetime_start)
        self.assertFalse(log1.datetime_end)
        self.vehicle.write({"driver_id": self.driver2.id})
        log2 = self.env["fleet.vehicle.assignation.log"].search(
            [("vehicle_id", "=", self.vehicle.id), ("driver_id", "=", self.driver2.id)]
        )
        self.assertEqual(len(log2), 1)
        self.assertTrue(log2.datetime_start)
        self.assertFalse(log2.datetime_end)
        log1_updated = self.env["fleet.vehicle.assignation.log"].browse(log1.id)
        self.assertTrue(log1_updated.datetime_end)
        self.assertEqual(log1_updated.datetime_end, log2.datetime_start)

    def test_02_create_and_write_log_directly(self):
        """
        Test that creating/writing logs directly with date fields correctly
        populates the datetime fields.
        """
        log = self.env["fleet.vehicle.assignation.log"].create(
            {
                "vehicle_id": self.vehicle.id,
                "driver_id": self.driver1.id,
                "date_start": fields.Date.from_string("2025-01-15"),
            }
        )
        expected_datetime_start = fields.Datetime.from_string("2025-01-15 00:00:00")
        self.assertEqual(log.datetime_start, expected_datetime_start)
        log.write({"date_end": fields.Date.from_string("2025-01-20")})
        expected_datetime_end = fields.Datetime.from_string("2025-01-20 23:59:59")
        self.assertEqual(log.datetime_end, expected_datetime_end)

    def test_03_onchange_and_sync_logic(self):
        """
        Test all synchronization logic (onchange and create/write) in the
        assignation log model to ensure full test coverage.
        """
        log_model = self.env["fleet.vehicle.assignation.log"]
        log = log_model.new({})
        log.datetime_start = fields.Datetime.from_string("2025-02-01 10:00:00")
        log._onchange_datetime_start()
        self.assertEqual(log.date_start, fields.Date.from_string("2025-02-01"))
        log.datetime_start = False
        log._onchange_datetime_start()
        self.assertFalse(log.date_start)
        log.datetime_end = fields.Datetime.from_string("2025-02-10 18:00:00")
        log._onchange_datetime_end()
        self.assertEqual(log.date_end, fields.Date.from_string("2025-02-10"))
        log.datetime_end = False
        log._onchange_datetime_end()
        self.assertFalse(log.date_end)
        log.datetime_start = False
        log.date_start = fields.Date.from_string("2025-03-01")
        log._onchange_date_start()
        self.assertEqual(
            log.datetime_start, fields.Datetime.from_string("2025-03-01 00:00:00")
        )
        log.datetime_end = False
        log.date_end = fields.Date.from_string("2025-03-15")
        log._onchange_date_end()
        self.assertEqual(
            log.datetime_end, fields.Datetime.from_string("2025-03-15 23:59:59")
        )
        specific_time = fields.Datetime.from_string("2025-03-15 11:00:00")
        log.datetime_end = specific_time
        log._onchange_date_end()
        self.assertEqual(log.datetime_end, specific_time)
        log.date_end = False
        log._onchange_date_end()
        self.assertFalse(log.datetime_end)
        log_created = log_model.create(
            {
                "vehicle_id": self.vehicle.id,
                "driver_id": self.driver2.id,
                "date_start": fields.Date.from_string("2025-04-01"),
                "date_end": fields.Date.from_string("2025-04-10"),
            }
        )
        self.assertEqual(
            log_created.datetime_start,
            fields.Datetime.from_string("2025-04-01 00:00:00"),
        )
        self.assertEqual(
            log_created.datetime_end,
            fields.Datetime.from_string("2025-04-10 23:59:59"),
        )

    def test_04_coverage_edge_cases(self):
        """
        Test edge cases specifically to increase test coverage on conditional
        branches.
        """
        self.vehicle.write({"driver_id": self.driver1.id})
        log_count_before = self.env["fleet.vehicle.assignation.log"].search_count(
            [("vehicle_id", "=", self.vehicle.id)]
        )
        self.vehicle.write({"license_plate": "NEW-PLATE-456"})
        log_count_after = self.env["fleet.vehicle.assignation.log"].search_count(
            [("vehicle_id", "=", self.vehicle.id)]
        )
        self.assertEqual(log_count_before, log_count_after)
        log_model = self.env["fleet.vehicle.assignation.log"]
        log = log_model.new({})
        log.datetime_start = False
        log.date_start = fields.Date.from_string("2025-05-01")
        log._onchange_date_start()
        self.assertEqual(
            log.datetime_start,
            fields.Datetime.from_string("2025-05-01 00:00:00"),
        )

    def test_05_if_new_log_coverage(self):
        """
        Test the `if new_log:` branch in `fleet.vehicle.py` by mocking
        the log creation to simulate a failure.
        """
        log_model = self.env["fleet.vehicle.assignation.log"]
        # Use patch.object on the already loaded model class
        with patch.object(
            type(log_model), "create", return_value=log_model.browse([])
        ) as mock_create:
            # This write will trigger our overridden method, but the mock
            # will prevent the creation of the log.
            self.vehicle.write({"driver_id": self.driver2.id})
            # The subsequent search for `new_log` will be empty, covering the
            # 'else' path of the `if new_log:` condition.
            mock_create.assert_called()
