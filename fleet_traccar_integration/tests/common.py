from odoo.addons.base.tests.common import BaseCommon


class FleetTraccarCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "traccar_enabled": True,
                "traccar_base_url": "https://traccar.example.com",
                "traccar_username": "user",
                "traccar_password": "secret",
            }
        )
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create(
            {"name": "Test model", "brand_id": cls.brand.id}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {"model_id": cls.vehicle_model.id, "license_plate": "TRC123"}
        )
        cls.Device = cls.env["traccar.device"]
        cls.Telemetry = cls.env["fleet.telemetry"]

    @classmethod
    def _create_device(cls, **values):
        vals = {
            "name": "Tracker 1",
            "unique_id": "TRC-1",
            "company_id": cls.company.id,
            "vehicle_id": cls.vehicle.id,
        }
        vals.update(values)
        return cls.Device.with_context(skip_traccar_remote_create=True).create(vals)
