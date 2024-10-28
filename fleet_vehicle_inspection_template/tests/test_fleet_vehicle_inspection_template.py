# Copyright 2021 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo.tests import TransactionCase


class TestFleetVehicleInspectionTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestFleetVehicleInspectionTemplate, cls).setUpClass()
        cls.inspection = cls.env["fleet.vehicle.inspection"]
        cls.inspection_item = cls.env["fleet.vehicle.inspection.item"]
        cls.inspection_template = cls.env["fleet.vehicle.inspection.template"]
        cls.vehicle = cls.env.ref("fleet.vehicle_5").id

        cls.item_01 = cls.inspection_item.create({"name": "Lights"})

        cls.item_02 = cls.inspection_item.create({"name": "Mirrors"})

        cls.inspection_template_01 = cls.inspection_template.create(
            {
                "name": "TemplateTest_01",
                "inspection_template_line_ids": [
                    (
                        0,
                        0,
                        {"inspection_template_item_id": cls.item_01.id},
                    ),
                    (
                        0,
                        0,
                        {"inspection_template_item_id": cls.item_02.id},
                    ),
                ],
            }
        )

        cls.inspection_template_02 = cls.inspection_template.create(
            {
                "name": "TemplateTest_02",
                "inspection_template_line_ids": [
                    (
                        0,
                        0,
                        {
                            "inspection_template_item_id": cls.item_01.id,
                            "sequence": 11,  # Different sequence in the template line
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "inspection_template_item_id": cls.item_02.id,
                            "sequence": 10,  # Different sequence in the template line
                        },
                    ),
                ],
            }
        )

        cls.inspection = cls.inspection.create(
            {
                "vehicle_id": cls.vehicle,
                "inspection_template_id": cls.inspection_template_01.id,
            }
        )

    def test_fleet_vehicle_inspection(self):
        # --- Test with an inspection template ---
        self.inspection._onchange_inspection_template_id()

        self.assertEqual(self.inspection.name, self.inspection_template_01.name)
        self.assertTrue(self.inspection.inspection_line_ids)

        # --- Change the template ID ---
        self.inspection.inspection_template_id = self.inspection_template_02

        # Trigger the onchange method again
        self.inspection._onchange_inspection_template_id()

        self.assertEqual(len(self.inspection.inspection_line_ids), 2)

        # Check if the sequence is correctly copied from the template line
        line_1 = self.inspection.inspection_line_ids.filtered(
            lambda linei: linei.inspection_item_id == self.item_01
        )
        self.assertEqual(line_1.sequence, 11)

        # --- Test without an inspection template ---
        self.inspection.inspection_template_id = False  # Remove the template

        # Trigger the onchange method again
        self.inspection._onchange_inspection_template_id()

        # Assert that the name and note are not changed
        self.assertEqual(self.inspection.name, self.inspection_template_02.name)
        # (remains the same as the previous template)
        self.assertNotEqual(self.inspection.name, self.inspection_template_01.name)

        # Assert that the inspection lines are NOT removed
        self.assertTrue(self.inspection.inspection_line_ids)
        self.assertEqual(len(self.inspection.inspection_line_ids), 2)
