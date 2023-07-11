# Copyright 2021 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo.tests import SavepointCase


class TestFleetVehicleInspectionTemplate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFleetVehicleInspectionTemplate, cls).setUpClass()
        cls.inspection = cls.env["fleet.vehicle.inspection"]
        cls.inspection_item = cls.env["fleet.vehicle.inspection.item"]
        cls.inspection_template = cls.env["fleet.vehicle.inspection.template"]
        cls.vehicle = cls.env.ref("fleet.vehicle_5").id

        cls.item_01 = cls.inspection_item.create({"name": "Lights"})

        cls.item_02 = cls.inspection_item.create({"name": "Mirrors"})

        cls.inspection_template = cls.inspection_template.create(
            {
                "name": "TemplateTest",
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

        cls.inspection = cls.inspection.create(
            {
                "vehicle_id": cls.vehicle,
                "inspection_template_id": cls.inspection_template.id,
            }
        )

    def test_fleet_vehicle_inspection(self):

        self.inspection._onchange_inspection_template_id()
        self.assertEqual(self.inspection.name, self.inspection_template.name)
        self.assertTrue(self.inspection.inspection_line_ids)
