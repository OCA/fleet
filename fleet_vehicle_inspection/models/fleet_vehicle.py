# Copyright 2020 - 2024, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    inspection_ids = fields.One2many(
        "fleet.vehicle.inspection", "vehicle_id", "Inspection Logs"
    )
    inspection_count = fields.Integer(
        compute="_compute_inspection_count", string="# Inspection Count"
    )

    @api.depends("inspection_ids")
    def _compute_inspection_count(self):
        res = self.env["fleet.vehicle.inspection"].read_group(
            domain=[("vehicle_id", "in", self.ids)],
            fields=["vehicle_id"],
            groupby=["vehicle_id"],
        )
        res_dict = {x["vehicle_id"][0]: x["vehicle_id_count"] for x in res}
        for rec in self:
            rec.inspection_count = res_dict.get(rec.id, 0)

    def action_view_inspection(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fleet_vehicle_inspection.fleet_vehicle_inspection_act_window"
        )
        if self.inspection_count > 1:
            action["domain"] = [("id", "in", self.inspection_ids.ids)]
        else:
            action["views"] = [
                (
                    self.env.ref(
                        "fleet_vehicle_inspection.fleet_vehicle_inspection_form_view"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = (
                fields.first(self.inspection_ids).id if self.inspection_ids else False
            )
        return action
