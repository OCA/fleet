from odoo import fields, models


class FleetTelemetryDevice(models.Model):
    _name = "fleet.telemetry.device"
    _description = "Fleet Telemetry Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    name = fields.Char(required=True, tracking=True)
    provider = fields.Char(required=True, index=True, tracking=True)
    external_ref = fields.Char(
        string="External Reference", required=True, index=True, tracking=True
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", index=True, tracking=True
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "fleet_telemetry_device_provider_ref_unique",
            "unique(company_id, provider, external_ref)",
            "The telemetry device reference must be unique per company and provider.",
        ),
    ]
