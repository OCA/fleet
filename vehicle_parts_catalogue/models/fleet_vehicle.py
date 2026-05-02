from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    part_count = fields.Integer(compute="_compute_part_count", string="Part Count")

    @api.depends("model_id.part_ids")
    def _compute_part_count(self):
        for vehicle in self:
            vehicle.part_count = len(vehicle.model_id.part_ids)

    def action_view_parts(self):
        self.ensure_one()
        action = self.env.ref("vehicle_parts_catalogue.action_vehicle_part").read()[0]
        action["domain"] = [("vehicle_model_id", "=", self.model_id.id)]
        return action
