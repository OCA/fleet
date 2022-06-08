# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    log_fuels = fields.One2many("fleet.vehicle.log.fuel", "vehicle_id", "Fuel Logs")
    fuel_count = fields.Integer(compute="_compute_count_all", string="Fuel Log Count")

    def _compute_count_all(self):
        super()._compute_count_all()
        LogFuel = self.env["fleet.vehicle.log.fuel"]
        for record in self:
            record.fuel_count = LogFuel.search_count([("vehicle_id", "=", record.id)])

    def action_view_log_fuel(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fleet_vehicle_log_fuel.fleet_vehicle_log_fuel_action"
        )
        action.update(
            context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
            domain=[("vehicle_id", "=", self.id)],
        )
        return action


class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"

    category = fields.Selection(
        selection_add=[("fuel", "Fuel Log")], ondelete={"fuel": "cascade"}
    )
