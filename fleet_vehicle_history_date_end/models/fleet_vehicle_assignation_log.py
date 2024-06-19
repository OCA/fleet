# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import date_utils


class FleetVehicleAssignationLog(models.Model):
    _inherit = "fleet.vehicle.assignation.log"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        history = self.search(
            [
                ("vehicle_id", "=", res.vehicle_id.id),
                ("date_end", "=", False),
                ("id", "!=", res.id),
            ]
        )
        if history:
            history.write({"date_end": date_utils.subtract(res.date_start, days=1)})
        return res
