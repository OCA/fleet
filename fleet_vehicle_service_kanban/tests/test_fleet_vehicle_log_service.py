from odoo.tests.common import TransactionCase


class TestFleetVehicleLogServices(TransactionCase):
    def setUp(self):
        super(TestFleetVehicleLogServices, self).setUp()

        self.user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "testuser",
                "email": "testuser@example.com",
                "password": "password",
            }
        )

        self.brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Audi",
            }
        )
        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {"name": "Test Vehicle Model", "brand_id": self.brand.id}
        )
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "ABC-1234",
                "odometer": 1000,
            }
        )

        self.service_type = self.env["fleet.service.type"].create(
            {"name": "Fatura do Fornecedor", "category": "service"}
        )

    def test__read_group_stage_ids(self):
        stages = []
        domain = []
        order = "name asc"
        api = self.env["fleet.vehicle.log.services"]
        result = api._read_group_stage_ids(stages, domain, order)
        self.assertTrue(result)

    def test_create_service_entry(self):
        service_entry = self.env["fleet.vehicle.log.services"].create(
            {
                "vehicle_id": self.vehicle.id,
                "notes": "Test notes",
                "service_type_id": self.service_type.id,
            }
        )

        self.assertEqual(service_entry.vehicle_id, self.vehicle)
        self.assertEqual(service_entry.notes, "Test notes")

    def test_track_subtype(self):
        service_entry = self.env["fleet.vehicle.log.services"].create(
            {
                "vehicle_id": self.vehicle.id,
                "notes": "Test notes",
                "service_type_id": self.service_type.id,
            }
        )

        self.assertEqual(
            service_entry._track_subtype(init_values={"user_id": 1}),
            self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_user_updated"
            ),
        )
        self.assertEqual(
            service_entry._track_subtype(init_values={"purchaser_id": 1}),
            self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_purchaser_updated"
            ),
        )
        self.assertEqual(
            service_entry._track_subtype(init_values={"vendor_id": 1}),
            self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_vendor_updated"
            ),
        )
