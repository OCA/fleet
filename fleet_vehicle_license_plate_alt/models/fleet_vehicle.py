# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    license_plate_alt = fields.Char(
        "Alternative Licence Plate",
        tracking=True,
        help="License plate alternative number of the vehicle.",
    )

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if operator == "ilike" and not (name or "").strip():
            domain = []
        else:
            domain = [
                "|",
                "|",
                ("name", operator, name),
                ("driver_id.name", operator, name),
                ("license_plate_alt", operator, name),
            ]
        rec = self._search(
            expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid
        )
        return models.lazy_name_get(self.browse(rec).with_user(name_get_uid))
