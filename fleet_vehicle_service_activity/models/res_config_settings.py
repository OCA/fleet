# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    delay_alert_service = fields.Integer(
        string="Delay activity service outdated",
        default=30,
        config_parameter="hr_fleet.delay_alert_service",
    )
