from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    traccar_enabled = fields.Boolean(
        related="company_id.traccar_enabled", readonly=False
    )
    traccar_base_url = fields.Char(
        related="company_id.traccar_base_url", readonly=False
    )
    traccar_auth_mode = fields.Selection(
        related="company_id.traccar_auth_mode", readonly=False
    )
    traccar_username = fields.Char(
        related="company_id.traccar_username", readonly=False
    )
    traccar_password = fields.Char(
        related="company_id.traccar_password", readonly=False
    )
    traccar_device_sync_interval = fields.Integer(
        related="company_id.traccar_device_sync_interval", readonly=False
    )
    traccar_telemetry_sync_interval = fields.Integer(
        related="company_id.traccar_telemetry_sync_interval", readonly=False
    )
    traccar_history_days = fields.Integer(
        related="company_id.traccar_history_days", readonly=False
    )
    traccar_history_max_days = fields.Integer(
        related="company_id.traccar_history_max_days", readonly=False
    )
    traccar_inline_sync_hours = fields.Integer(
        related="company_id.traccar_inline_sync_hours", readonly=False
    )

    def action_traccar_test_connection(self):
        self.ensure_one()
        return self.company_id.action_traccar_test_connection()

    def action_traccar_test_api_access(self):
        self.ensure_one()
        return self.company_id.action_traccar_test_api_access()

    def action_traccar_merge_duplicate_telemetry(self):
        self.ensure_one()
        return self.company_id.action_traccar_merge_duplicate_telemetry()
