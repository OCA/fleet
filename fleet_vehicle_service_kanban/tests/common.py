# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestVehicleLogServicesCommon(TransactionCase):
    def setUp(self):
        super().setUp()
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "license_plate": "1-ACK-555",
                "vin_sn": "883333",
                "color": "Black",
                "location": "Grand-Rosiere",
                "doors": 5,
                "driver_id": self.env.ref("base.user_demo").id,
                "odometer_unit": "kilometers",
                "car_value": 20000,
                "model_id": self.env.ref("fleet.model_astra").id,
            }
        )
        service_type_repair = self.env["fleet.service.type"].create(
            {"name": "Repair and maintenance", "category": "service"}
        )
        service_tag_oil = self.env["fleet.vehicle.log.services.tag"].create(
            {"name": "Oil Change"}
        )
        self.stage_draft = self.env.ref(
            "fleet_vehicle_service_kanban.fleet_vehicle_log_services_stage_draft"
        )
        self.stage_open = self.env["fleet.vehicle.log.services.stage"].create(
            {"name": "In Process"}
        )
        self.stage_done = self.env["fleet.vehicle.log.services.stage"].create(
            {"name": "Done", "fold": True}
        )
        self.service_repair = self.env["fleet.vehicle.log.services"].create(
            {
                "vehicle_id": self.vehicle.id,
                "service_type_id": service_type_repair.id,
                "amount": 500,
                "priority": "1",
                "tag_ids": [(4, service_tag_oil.id)],
                "date": "2020-05-21",
                "inv_ref": "INV123",
            }
        )
