# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class FleetVehicleAssignationLog(models.Model):
    _inherit = "fleet.vehicle.assignation.log"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        for res_item in res:
            history = self.search(
                [
                    ("vehicle_id", "=", res_item.vehicle_id.id),
                    ("date_end", "=", False),
                    ("id", "!=", res_item.id),
                ]
            )
            if history:
                history.write({"date_end": res_item.date_start})

        return res
