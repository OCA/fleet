# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestVehicleLogServicesCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Audi"})
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "license_plate": "1-ACK-555",
                "vin_sn": "883333",
                "color": "Black",
                "location": "Grand-Rosiere",
                "doors": 5,
                "driver_id": cls.env.ref("base.user_demo").id,
                "odometer_unit": "kilometers",
                "car_value": 20000,
                "model_id": cls.env.ref("fleet.model_focus").id,
            }
        )
        cls.service_type_repair = cls.env["fleet.service.type"].create(
            {"name": "Repair and maintenance", "category": "service"}
        )
        service_tag_oil = cls.env["fleet.vehicle.log.services.tag"].create(
            {"name": "Oil Change"}
        )
        cls.stage_draft = cls.env.ref(
            "fleet_vehicle_service_kanban.fleet_vehicle_log_services_stage_draft"
        )
        cls.stage_open = cls.env["fleet.vehicle.log.services.stage"].create(
            {"name": "In Process"}
        )
        cls.stage_done = cls.env["fleet.vehicle.log.services.stage"].create(
            {"name": "Done", "fold": True}
        )
        cls.service_repair = cls.env["fleet.vehicle.log.services"].create(
            {
                "vehicle_id": cls.vehicle.id,
                "service_type_id": cls.service_type_repair.id,
                "amount": 500,
                "priority": "1",
                "tag_ids": [(4, service_tag_oil.id)],
                "date": "2020-05-21",
                "inv_ref": "INV123",
            }
        )
        cls.user = new_test_user(cls.env, login="testuser")
