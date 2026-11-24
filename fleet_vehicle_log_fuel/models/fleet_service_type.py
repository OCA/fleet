# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"

    category = fields.Selection(
        selection_add=[("fuel", "Fuel Log")], ondelete={"fuel": "cascade"}
    )
