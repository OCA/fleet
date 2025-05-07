# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from odoo.addons.base.tests.common import BaseCommon


class TestFleetVehicleLogFuelBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
