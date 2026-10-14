from odoo.addons.base.tests.common import BaseCommon


class FleetMapsCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create(
            {"name": "Test model", "brand_id": cls.brand.id}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {"model_id": cls.vehicle_model.id, "license_plate": "MAP123"}
        )
