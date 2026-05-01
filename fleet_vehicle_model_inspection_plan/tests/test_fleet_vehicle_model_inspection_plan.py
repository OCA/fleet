# Copyright 2024 - TODAY, Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestFleetVehicleModelInspectionPlan(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.VehicleModel = cls.env["fleet.vehicle.model"]
        cls.InspectionItem = cls.env["fleet.vehicle.inspection.item"]
        cls.InspectionPlan = cls.env["fleet.vehicle.model.inspection.plan"]
        cls.Brand = cls.env["fleet.vehicle.model.brand"]

        cls.brand = cls.Brand.create({"name": "Test Brand"})
        cls.model = cls.VehicleModel.create(
            {"name": "Test Model", "brand_id": cls.brand.id}
        )
        cls.item_oil = cls.InspectionItem.create({"name": "Oil Change"})
        cls.item_tires = cls.InspectionItem.create({"name": "Tire Rotation"})

    def test_inspection_plan_creation(self):
        plan = self.InspectionPlan.create(
            {
                "model_id": self.model.id,
                "item_id": self.item_oil.id,
                "interval_km": 5000,
                "interval_months": 6,
            }
        )
        self.assertTrue(plan)
        self.assertEqual(plan.model_id, self.model)
        self.assertEqual(plan.item_id, self.item_oil)
        self.assertEqual(plan.interval_km, 5000)
        self.assertEqual(plan.interval_months, 6)

    def test_model_one2many_relation(self):
        plan_oil = self.InspectionPlan.create(
            {
                "model_id": self.model.id,
                "item_id": self.item_oil.id,
            }
        )
        plan_tires = self.InspectionPlan.create(
            {
                "model_id": self.model.id,
                "item_id": self.item_tires.id,
            }
        )
        self.assertIn(plan_oil, self.model.inspection_plan_ids)
        self.assertIn(plan_tires, self.model.inspection_plan_ids)
        self.assertEqual(len(self.model.inspection_plan_ids), 2)

    def test_defaults(self):
        plan = self.InspectionPlan.create(
            {
                "model_id": self.model.id,
                "item_id": self.item_oil.id,
            }
        )
        # Check defaults defined in the model
        self.assertEqual(plan.interval_km, 10000)
        self.assertEqual(plan.interval_months, 12)
