# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestVehicleLogServicesCommon


class TestVehicleLogServices(TestVehicleLogServicesCommon):
    def test_vehicle_service_stages(self):
        """Check workflow of services through stages."""
        self.assertEqual(self.service_repair.stage_id, self.stage_draft)
        self.service_repair.write({"stage_id": self.stage_open.id})
        self.assertEqual(self.service_repair.stage_id, self.stage_open)
        self.service_repair.write({"stage_id": self.stage_done.id})
        self.assertEqual(self.service_repair.stage_id, self.stage_done)
