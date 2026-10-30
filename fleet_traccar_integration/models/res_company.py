import json
import logging
from datetime import timedelta

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    traccar_enabled = fields.Boolean(string="Enable Traccar Integration")
    traccar_base_url = fields.Char(string="Traccar Base URL")
    traccar_auth_mode = fields.Selection(
        [("basic", "Basic"), ("session", "Session"), ("token", "Token")],
        string="Traccar Authentication Mode",
        default="basic",
        required=True,
    )
    traccar_username = fields.Char()
    traccar_password = fields.Char(string="Traccar Password/Token")
    traccar_device_sync_interval = fields.Integer(
        string="Device Sync Interval (min)", default=60
    )
    traccar_telemetry_sync_interval = fields.Integer(
        string="Telemetry Sync Interval (min)", default=5
    )
    traccar_history_days = fields.Integer(
        string="Initial History (days)",
        default=30,
        help="Period downloaded for a device that has no telemetry yet.",
    )
    traccar_history_max_days = fields.Integer(
        string="Maximum Import Period (days)",
        default=31,
        help="Longest period a user can request in a manual history import.",
    )
    traccar_inline_sync_hours = fields.Integer(
        string="Immediate Sync Limit (hours)",
        default=24,
        help="Gaps longer than this are downloaded by a background history "
        "import instead of during the synchronization itself.",
    )
    traccar_last_device_sync = fields.Datetime(string="Last Device Sync")
    traccar_last_telemetry_sync = fields.Datetime(string="Last Telemetry Sync")

    def _traccar_request(self, method, endpoint, **kwargs):
        self.ensure_one()
        if not self.traccar_base_url or not self.traccar_password:
            raise UserError(_("Configure the Traccar URL and password/token."))

        base_url = self.traccar_base_url.rstrip("/")
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{base_url}{endpoint}"
        request_kwargs = dict(kwargs)
        request_kwargs.setdefault("headers", {})["Accept"] = "application/json"
        session = requests.Session()
        auth_mode = self.traccar_auth_mode or "basic"
        if auth_mode == "token":
            token = self.traccar_password.strip()
            request_kwargs["headers"]["Authorization"] = (
                token if token.lower().startswith("bearer ") else f"Bearer {token}"
            )
        elif auth_mode == "basic":
            if not self.traccar_username:
                raise UserError(_("Configure the Traccar username."))
            request_kwargs["auth"] = (self.traccar_username, self.traccar_password)
        try:
            if auth_mode == "session":
                if not self.traccar_username:
                    raise UserError(_("Configure the Traccar username."))
                login_response = session.post(
                    f"{base_url}/api/session",
                    data={
                        "email": self.traccar_username,
                        "password": self.traccar_password,
                    },
                    timeout=30,
                )
                if not login_response.ok:
                    message = login_response.text.strip() or login_response.reason
                    raise UserError(
                        _(
                            "Traccar authentication failed: %(status)s %(message)s",
                            status=login_response.status_code,
                            message=message,
                        )
                    )
            response = session.request(
                method,
                url,
                timeout=(5, 20),
                allow_redirects=False,
                **request_kwargs,
            )
            if response.status_code in (401, 403):
                raise UserError(
                    _("Traccar rejected the credentials or access permissions.")
                )
            if not response.ok:
                raise UserError(
                    _(
                        "Traccar returned HTTP %s. Check the URL and permissions.",
                        response.status_code,
                    )
                )
        except requests.RequestException as error:
            raise UserError(
                _(
                    "Could not reach Traccar. Check the URL, network and TLS certificate."  # noqa: E501
                )
            ) from error

        if response.content:
            try:
                return response.json()
            except json.JSONDecodeError as error:
                raise UserError(
                    _("Traccar returned an invalid API response.")
                ) from error
        return []

    def action_traccar_test_connection(self):
        for company in self:
            company._traccar_request("GET", "/api/server")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Traccar Connection"),
                "message": _("Connection successful."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_traccar_test_api_access(self):
        for company in self:
            devices = company._traccar_request("GET", "/api/devices")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Traccar API"),
                "message": _(
                    "Devices API access confirmed. Devices returned: %s",
                    len(devices),
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def action_traccar_merge_duplicate_telemetry(self):
        self.env["fleet.telemetry"].search(
            [("provider", "=", "traccar")]
        )._merge_duplicate_telemetry()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Traccar Telemetry"),
                "message": _("Duplicate telemetry merged."),
                "type": "success",
                "sticky": False,
            },
        }

    def _traccar_due(self, last_sync, interval):
        if not last_sync:
            return True
        interval = max(interval or 0, 1)
        return fields.Datetime.now() >= last_sync + timedelta(minutes=interval)

    def _cron_traccar_sync(self):
        companies = self.search([("traccar_enabled", "=", True)])
        for company in companies:
            try:
                if company._traccar_due(
                    company.traccar_last_device_sync,
                    company.traccar_device_sync_interval,
                ):
                    self.env["traccar.device"].with_company(
                        company
                    )._sync_company_devices(company)
                    company.traccar_last_device_sync = fields.Datetime.now()

                if company._traccar_due(
                    company.traccar_last_telemetry_sync,
                    company.traccar_telemetry_sync_interval,
                ):
                    self.env["fleet.telemetry"].with_company(
                        company
                    )._sync_company_telemetry(company)
                    company.traccar_last_telemetry_sync = fields.Datetime.now()
            except Exception:
                _logger.exception(
                    "Traccar sync failed for company %s", company.display_name
                )
