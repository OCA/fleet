# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import TestVehicleLogServicesCommon


class TestFleetVehicleLogServices(TestVehicleLogServicesCommon):
    def test__read_group_stage_ids(self):
        result = self.env["fleet.vehicle.log.services"]._read_group_stage_ids(
            self.stage_draft, []
        )
        self.assertIn(self.stage_draft, result)
        self.assertIn(self.stage_open, result)
        self.assertIn(self.stage_done, result)

    def test_track_subtype(self):
        self.assertEqual(
            self.service_repair._track_subtype(init_values={"user_id": 1}),
            self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_user_updated"
            ),
        )
        self.assertEqual(
            self.service_repair._track_subtype(init_values={"purchaser_id": 1}),
            self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_purchaser_updated"
            ),
        )
        self.assertEqual(
            self.service_repair._track_subtype(init_values={"vendor_id": 1}),
            self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_vendor_updated"
            ),
        )

    def test_vehicle_service_stages(self):
        """Check workflow of services through stages."""
        self.assertEqual(self.service_repair.stage_id, self.stage_draft)
        self.service_repair.write({"stage_id": self.stage_open.id})
        self.assertEqual(self.service_repair.stage_id, self.stage_open)
        self.service_repair.write({"stage_id": self.stage_done.id})
        self.assertEqual(self.service_repair.stage_id, self.stage_done)
