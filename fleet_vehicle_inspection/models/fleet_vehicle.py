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
        # Odoo 19: Use _read_group
        data = self.env["fleet.vehicle.inspection"]._read_group(
            domain=[("vehicle_id", "in", self.ids)],
            groupby=["vehicle_id"],
            aggregates=["__count"],
        )
        res_dict = {vehicle.id: count for vehicle, count in data}
        for rec in self:
            rec.inspection_count = res_dict.get(rec.id, 0)

    def action_view_inspection(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fleet_vehicle_inspection.fleet_vehicle_inspection_act_window"
        )
        if self.inspection_count > 1:
            action["domain"] = [("id", "in", self.inspection_ids.ids)]
        else:
            form_view = self.env.ref(
                "fleet_vehicle_inspection.fleet_vehicle_inspection_form_view"
            )
            action["views"] = [(form_view.id, "form")]
            action["res_id"] = (
                self.inspection_ids[0].id if self.inspection_ids else False
            )
        return action
