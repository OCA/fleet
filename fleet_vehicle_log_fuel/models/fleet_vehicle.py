# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    log_fuels = fields.One2many("fleet.vehicle.log.fuel", "vehicle_id", "Fuel Logs")
    fuel_count = fields.Integer(compute="_compute_fuel_count", string="Fuel Log Count")

    @api.depends("log_fuels")
    def _compute_fuel_count(self):
        data = self.env["fleet.vehicle.log.fuel"]._read_group(
            domain=[("vehicle_id", "in", self.ids)],
            groupby=["vehicle_id"],
            aggregates=["__count"],
        )
        res_dict = {vehicle.id: count for vehicle, count in data}
        for record in self:
            record.fuel_count = res_dict.get(record.id, 0)

    def action_view_log_fuel(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fleet_vehicle_log_fuel.fleet_vehicle_log_fuel_action"
        )
        action.update(
            context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
            domain=[("vehicle_id", "=", self.id)],
        )
        return action
