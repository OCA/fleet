# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestFleetTrafficInfractions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tz="UTC",
            )
        )
        # Models
        cls.Partner = cls.env["res.partner"]
        cls.Vehicle = cls.env["fleet.vehicle"]
        cls.VehicleModel = cls.env["fleet.vehicle.model"]
        cls.VehicleModelBrand = cls.env["fleet.vehicle.model.brand"]
        cls.Infraction = cls.env["fleet.traffic.infractions"]
        cls.InfractionType = cls.env["fleet.traffic.infraction.type"]
        cls.AssignationLog = cls.env["fleet.vehicle.assignation.log"]
        cls.Country = cls.env["res.country"]
        cls.State = cls.env["res.country.state"]

        # Create Partners
        cls.partner_agency = cls.Partner.create(
            {"name": "Traffic Agency", "is_issuing_agency": True, "is_company": True}
        )
        cls.driver_1 = cls.Partner.create({"name": "Driver One"})
        cls.driver_2 = cls.Partner.create({"name": "Driver Two"})

        # Create Vehicle
        cls.brand = cls.VehicleModelBrand.create({"name": "Test Brand"})
        cls.model = cls.VehicleModel.create(
            {"brand_id": cls.brand.id, "name": "Test Model"}
        )
        cls.vehicle_1 = cls.Vehicle.create(
            {"model_id": cls.model.id, "license_plate": "TEST-1"}
        )

        # Create Infraction Type
        cls.infraction_type_1 = cls.InfractionType.create(
            {"code": "SPEED", "description": "Speeding"}
        )

        # Create Geo Data for Jurisdiction tests
        cls.country_us = cls.env.ref("base.us")
        cls.state_ca = cls.env.ref("base.state_us_5")

        # Create Vehicle Assignment Logs
        cls.now = datetime.now()
        cls.log_1 = cls.AssignationLog.create(
            {
                "vehicle_id": cls.vehicle_1.id,
                "driver_id": cls.driver_1.id,
                "datetime_start": cls.now - timedelta(days=2),
                "datetime_end": cls.now - timedelta(days=1),
            }
        )
        cls.log_2 = cls.AssignationLog.create(
            {
                "vehicle_id": cls.vehicle_1.id,
                "driver_id": cls.driver_2.id,
                "datetime_start": cls.now - timedelta(hours=8),
                "datetime_end": cls.now + timedelta(hours=8),
            }
        )

    def test_01_infraction_creation_and_defaults(self):
        """Test the creation of an infraction and its default values."""
        infraction = self.Infraction.create({})
        self.assertEqual(infraction.state, "draft", "Default state should be 'draft'.")
        self.assertNotEqual(
            infraction.name, "New", "Reference should be assigned by sequence."
        )

    def test_02_get_driver_for_datetime_method(self):
        """Test the helper method to get the correct driver for a datetime."""
        time_for_driver_1 = self.now - timedelta(days=1, hours=12)
        found_driver_1 = self.vehicle_1.get_driver_for_datetime(time_for_driver_1)
        self.assertEqual(
            found_driver_1,
            self.driver_1,
            "Should find driver 1 for the specified time.",
        )
        time_for_driver_2 = self.now
        found_driver_2 = self.vehicle_1.get_driver_for_datetime(time_for_driver_2)
        self.assertEqual(
            found_driver_2,
            self.driver_2,
            "Should find driver 2 for the specified time.",
        )
        time_for_no_driver = self.now - timedelta(days=5)
        found_no_driver = self.vehicle_1.get_driver_for_datetime(time_for_no_driver)
        self.assertFalse(
            found_no_driver, "Should not find any driver for the specified time."
        )

    def test_03_onchange_driver_suggestion(self):
        """Test that the onchange correctly suggests the driver."""
        infraction = self.Infraction.new()
        infraction.vehicle_id = self.vehicle_1
        infraction.infraction_datetime = self.now
        infraction._onchange_vehicle_infraction_datetime()
        self.assertEqual(
            infraction.driver_id,
            self.driver_2,
            "Onchange should suggest driver 2 for the current time.",
        )
        infraction.infraction_datetime = self.now - timedelta(days=1, hours=12)
        infraction._onchange_vehicle_infraction_datetime()
        self.assertEqual(
            infraction.driver_id,
            self.driver_1,
            "Onchange should suggest driver 1 for the past time.",
        )
        infraction.vehicle_id = False
        infraction._onchange_vehicle_infraction_datetime()
        self.assertFalse(
            infraction.driver_id, "Clearing vehicle should clear the driver."
        )

    def test_04_confirmation_logic_and_validation(self):
        """Test that drafts can be saved and confirmation requires fields."""
        infraction = self.Infraction.create({})
        self.assertEqual(infraction.state, "draft")
        with self.assertRaises(ValidationError) as e:
            infraction.button_confirm()
        self.assertIn("Vehicle", str(e.exception))
        self.assertIn("Driver", str(e.exception))
        self.assertIn("Infraction Address", str(e.exception))
        infraction.write(
            {
                "vehicle_id": self.vehicle_1.id,
                "driver_id": self.driver_2.id,
                "infraction_type_id": self.infraction_type_1.id,
                "issuing_agency_id": self.partner_agency.id,
                "infraction_datetime": self.now,
                "street": "123 Test St",
                "city": "Testville",
                "country_id": self.country_us.id,
                "infraction_auto_number": "TICKET-123",
                "fine_amount": 150.0,
            }
        )
        infraction.button_confirm()
        self.assertEqual(
            infraction.state, "confirmed", "Infraction should be in confirmed state."
        )

    def test_05_driver_change_logging(self):
        """Test that changing a driver posts a detailed message."""
        infraction = self.Infraction.create(
            {
                "vehicle_id": self.vehicle_1.id,
                "driver_id": self.driver_2.id,
                "infraction_datetime": self.now,
                "infraction_auto_number": "LOG-TEST",
            }
        )
        infraction.write({"driver_id": self.driver_1.id})
        last_message = infraction.message_ids[0]
        self.assertIn("Driver changed on infraction", last_message.body)
        self.assertIn(self.driver_2.name, last_message.body)
        self.assertIn(self.driver_1.name, last_message.body)
        self.assertIn("The assignment log suggests", last_message.body)
        self.assertIn(self.driver_2.name, last_message.body)

    def test_06_computed_and_related_fields(self):
        """Test computed fields like infraction_key and smart button counts."""
        self.vehicle_1.infraction_ids.unlink()
        infraction = self.Infraction.create(
            {
                "vehicle_id": self.vehicle_1.id,
                "driver_id": self.driver_1.id,
                "infraction_type_id": self.infraction_type_1.id,
                "infraction_auto_number": "KEY-TEST",
                "fine_amount": 100.0,
                "state": "confirmed",
            }
        )
        expected_key = (
            f"{self.vehicle_1.license_plate}-KEY-TEST-{self.infraction_type_1.code}"
        )
        self.assertEqual(infraction.infraction_key, expected_key)
        self.assertEqual(self.vehicle_1.infraction_count, 1)
        self.driver_1.invalidate_recordset(["total_infraction_fines"])
        self.assertEqual(
            self.driver_1.total_infraction_fines,
            100.0,
            "Total fines for driver 1 should be updated.",
        )
        self.Infraction.create(
            {
                "vehicle_id": self.vehicle_1.id,
                "driver_id": self.driver_1.id,
                "infraction_type_id": self.infraction_type_1.id,
                "infraction_auto_number": "KEY-TEST-DRAFT",
                "fine_amount": 50.0,
                "state": "draft",
            }
        )
        self.driver_1.invalidate_recordset(["total_infraction_fines"])
        self.assertEqual(
            self.driver_1.total_infraction_fines,
            100.0,
            "Draft fines should not be included in the total.",
        )

    def test_07_res_partner_logic(self):
        """Test partner model computations, actions, and constraints."""
        self.Infraction.create(
            {
                "issuing_agency_id": self.partner_agency.id,
                "infraction_auto_number": "AGENCY-1",
            }
        )
        self.partner_agency.invalidate_recordset(["issuing_agency_rank"])
        self.assertEqual(self.partner_agency.issuing_agency_rank, 1)
        action_driver = self.driver_1.action_view_driver_infractions()
        self.assertIn(("driver_id", "=", self.driver_1.id), action_driver["domain"])
        self.assertEqual(
            action_driver["context"]["default_driver_id"], self.driver_1.id
        )
        action_agency = self.partner_agency.action_view_issued_infractions()
        self.assertIn(
            ("issuing_agency_id", "=", self.partner_agency.id), action_agency["domain"]
        )
        self.assertEqual(
            action_agency["context"]["default_issuing_agency_id"],
            self.partner_agency.id,
        )
        with self.assertRaises(ValidationError):
            self.driver_1.write({"is_issuing_agency": True})

    def test_08_infraction_type_constraints(self):
        """Test the jurisdiction constraints on infraction types."""
        with self.assertRaises(ValidationError, msg="Country level cannot have state"):
            self.InfractionType.create(
                {
                    "code": "C1",
                    "jurisdiction_level": "country",
                    "country_id": self.country_us.id,
                    "state_id": self.state_ca.id,
                }
            )
        with self.assertRaises(ValidationError, msg="State level cannot have city"):
            self.InfractionType.create(
                {
                    "code": "S1",
                    "jurisdiction_level": "state",
                    "country_id": self.country_us.id,
                    "state_id": self.state_ca.id,
                    "city": "Test City",
                }
            )
        with self.assertRaises(ValidationError, msg="State level must have state"):
            self.InfractionType.create(
                {
                    "code": "S2",
                    "jurisdiction_level": "state",
                    "country_id": self.country_us.id,
                }
            )
        with self.assertRaises(
            ValidationError, msg="Municipal level must have state and city"
        ):
            self.InfractionType.create(
                {
                    "code": "M1",
                    "jurisdiction_level": "municipal",
                    "country_id": self.country_us.id,
                    "state_id": self.state_ca.id,
                }
            )

    def test_09_infraction_type_onchange(self):
        """Test the onchange logic for jurisdiction level."""
        infraction_type = self.InfractionType.new(
            {
                "jurisdiction_level": "municipal",
                "state_id": self.state_ca.id,
                "city": "Test City",
            }
        )
        infraction_type.jurisdiction_level = "state"
        infraction_type._onchange_jurisdiction_level()
        self.assertFalse(infraction_type.city)
        self.assertTrue(infraction_type.state_id)
        infraction_type.jurisdiction_level = "country"
        infraction_type._onchange_jurisdiction_level()
        self.assertFalse(infraction_type.state_id)

    def test_10_vehicle_actions(self):
        """Test the action method on the fleet.vehicle model."""
        infraction = self.Infraction.create({"vehicle_id": self.vehicle_1.id})
        action = self.vehicle_1.action_view_infractions()
        self.assertIn(("id", "in", infraction.ids), action["domain"])
        self.assertEqual(action["context"]["default_vehicle_id"], self.vehicle_1.id)

    def test_11_infraction_edge_cases(self):
        """Test various edge cases for traffic infractions."""
        common_vals = {
            "vehicle_id": self.vehicle_1.id,
            "infraction_auto_number": "UNIQUE-TEST",
            "infraction_type_id": self.infraction_type_1.id,
        }
        self.Infraction.create(common_vals)
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.Infraction.create(common_vals)
        infraction = self.Infraction.create({"driver_id": self.driver_1.id})
        infraction.write({"driver_id": self.driver_2.id})
        last_message = infraction.message_ids[0]
        self.assertNotIn("assignment log", last_message.body)
        infraction_no_driver_time = self.now - timedelta(days=4)
        infraction_no_driver = self.Infraction.create(
            {
                "vehicle_id": self.vehicle_1.id,
                "driver_id": self.driver_1.id,
                "infraction_datetime": infraction_no_driver_time,
            }
        )
        infraction_no_driver.write({"driver_id": self.driver_2.id})
        last_message_no_driver = infraction_no_driver.message_ids[0]
        self.assertIn("No driver was found", last_message_no_driver.body)
        infraction.vehicle_id.license_plate = False
        self.assertFalse(infraction.infraction_key)
        infraction.state = "confirmed"
        infraction.button_cancel()
        self.assertEqual(infraction.state, "cancel")
        infraction.button_draft()
        self.assertEqual(infraction.state, "draft")

    def test_12_coverage_enhancements(self):
        """Specific tests to cover requested lines for higher coverage."""
        self.env["res.partner"]._compute_issuing_agency_rank()
        self.assertTrue(True, "Calling compute on empty recordset should not error.")
        infraction = self.Infraction.create({"driver_id": self.driver_1.id})
        self.assertFalse(infraction.infraction_datetime)
        infraction.write({"driver_id": self.driver_2.id})
        last_message = infraction.message_ids[0]
        self.assertNotIn("assignment log", last_message.body)
        self.assertNotIn("Note:", last_message.body)

    def test_13_advanced_coverage(self):
        """Test specific edge cases for increased test coverage."""
        infraction = self.Infraction.create({"driver_id": self.driver_1.id})
        initial_message_count = len(infraction.message_ids)
        infraction.write({"driver_id": self.driver_1.id})
        final_message_count = len(infraction.message_ids)
        self.assertEqual(
            initial_message_count,
            final_message_count,
            "Writing the same driver should not create a new message.",
        )
        infraction_onchange = self.Infraction.new()
        infraction_onchange.driver_id = self.driver_1
        infraction_onchange.vehicle_id = self.vehicle_1
        infraction_onchange.infraction_datetime = self.now - timedelta(days=5)
        infraction_onchange._onchange_vehicle_infraction_datetime()
        self.assertEqual(
            infraction_onchange.driver_id,
            self.driver_1,
            "Onchange should not clear a manual driver if no log is found.",
        )
