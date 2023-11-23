# Copyright 2023 RPSJR
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("vehicle_ids")
    def _compute_vehicle_count(self):
        for rec in self:
            rec.vehicle_count = len(rec.vehicle_ids)

    vehicle_ids = fields.One2many(
        "fleet.vehicle",
        "owner_id",
        required=True,
        help="Vehicles owned by this partner",
    )
    vehicle_count = fields.Integer(
        compute=_compute_vehicle_count, string="Number of Vehicles", store=True
    )

    def action_view_vehicles(self):
        self.ensure_one()
        xmlid = "fleet.fleet_vehicle_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["context"] = self.env.context.copy()
        action["context"].update({"default_owner_id": self.id})
        if self.vehicle_count > 1:
            action["domain"] = [("id", "in", self.vehicle_ids.ids)]
        else:
            action["views"] = [
                (self.env.ref("fleet.fleet_vehicle_view_form").id, "form")
            ]
            action["res_id"] = self.vehicle_ids and self.vehicle_ids.ids[0] or False
        return action
