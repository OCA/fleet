# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class FleetVehicleLogServices(models.Model):
    _inherit = "fleet.vehicle.log.services"

    @api.model
    def _cron_manage_service_date(self):
        params = self.env["ir.config_parameter"].sudo()
        delay_alert_service = int(
            params.get_param("hr_fleet.delay_alert_service", default=30)
        )
        date_today = fields.Date.today()
        outdated_days = date_today + relativedelta(days=+delay_alert_service)
        reminder_activity_type = (
            self.env.ref(
                "fleet_vehicle_service_activity.mail_act_fleet_service_to_check",
                raise_if_not_found=False,
            )
            or self.env["mail.activity.type"]
        )
        nearly_date_services = self.search(
            [
                ("state", "in", ("new", "running")),
                ("date", "<", outdated_days),
                ("vehicle_id.manager_id", "!=", False),
            ]
        ).filtered(
            lambda nec: reminder_activity_type not in nec.activity_ids.activity_type_id
        )
        for service in nearly_date_services:
            service.activity_schedule(
                "fleet_vehicle_service_activity.mail_act_fleet_service_to_check",
                service.date,
                user_id=service.vehicle_id.manager_id.id,
            )
