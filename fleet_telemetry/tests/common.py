from odoo.addons.base.tests.common import BaseCommon


class FleetTelemetryCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create(
            {"name": "Test model", "brand_id": cls.brand.id}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {"model_id": cls.vehicle_model.id, "license_plate": "TEL123"}
        )
        cls.Device = cls.env["fleet.telemetry.device"]
        cls.Telemetry = cls.env["fleet.telemetry"]
        cls.device = cls.Device.create(
            {
                "name": "Tracker 1",
                "provider": "traccar",
                "external_ref": "DEV-1",
                "vehicle_id": cls.vehicle.id,
            }
        )

    @classmethod
    def _create_telemetry(cls, **values):
        vals = {
            "company_id": cls.company.id,
            "provider": "traccar",
            "device_id": cls.device.id,
            "vehicle_id": cls.vehicle.id,
            "fix_time": "2026-01-10 10:00:00",
            "latitude": -23.5505199,
            "longitude": -46.6333094,
        }
        vals.update(values)
        return cls.Telemetry.create(vals)
