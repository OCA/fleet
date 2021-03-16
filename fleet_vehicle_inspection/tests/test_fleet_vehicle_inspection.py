# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo.exceptions import UserError
from odoo.tests import SavepointCase


class TestFleetVehicleInspection(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFleetVehicleInspection, cls).setUpClass()
        cls.inspection = cls.env["fleet.vehicle.inspection"]
        cls.inspection_line = cls.env["fleet.vehicle.inspection.line"]
        cls.inspection_item = cls.env["fleet.vehicle.inspection.item"]
        cls.vehicle = cls.env.ref("fleet.vehicle_5").id

        cls.item_01 = cls.inspection_item.create({"name": "Lights"})

        cls.item_02 = cls.inspection_item.create({"name": "Mirrors"})

        cls.inspection = cls.inspection.create(
            {
                "vehicle_id": cls.vehicle,
                "inspection_line_ids": [
                    (
                        0,
                        0,
                        {"inspection_item_id": cls.item_01.id},
                    ),
                    (
                        0,
                        0,
                        {"inspection_item_id": cls.item_02.id},
                    ),
                ],
            }
        )

        cls.inspection2 = cls.inspection.create({"vehicle_id": cls.vehicle})

    def test_fleet_vehicle_inspection(self):

        self.assertTrue(self.inspection.name)

        self.inspection._compute_inspection_result()
        self.assertEqual(self.inspection.result, "todo")

        # inspection confirm not completed
        with self.assertRaises(UserError):
            self.inspection.button_confirm()

        self.inspection.vehicle_id._compute_inspection_count()
        self.assertEqual(self.inspection.vehicle_id.inspection_count, 2)

        self.inspection.inspection_line_ids[0].action_item_success()
        self.inspection._compute_inspection_result()
        self.assertEqual(self.inspection.result, "todo")

        self.inspection.inspection_line_ids[1].action_item_success()
        self.inspection._compute_inspection_result()
        self.assertEqual(self.inspection.result, "success")

        self.inspection.inspection_line_ids[1].action_item_failure()
        self.inspection._compute_inspection_result()
        self.assertEqual(self.inspection.result, "failure")

        self.inspection.button_confirm()
        self.assertEqual(self.inspection.state, "confirmed")

        self.inspection.button_cancel()
        self.assertEqual(self.inspection.state, "cancel")

        self.inspection.button_draft()
        self.assertEqual(self.inspection.state, "draft")

        self.inspection2._compute_inspection_result()
        self.assertEqual(self.inspection2.result, "todo")

        # inspection2 confirm without items
        with self.assertRaises(UserError):
            self.inspection2.button_confirm()
