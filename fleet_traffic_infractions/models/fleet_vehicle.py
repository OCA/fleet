# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AG_PL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    infraction_ids = fields.One2many(
        "fleet.traffic.infractions", "vehicle_id", string="Traffic Infractions"
    )
    infraction_count = fields.Integer(compute="_compute_infraction_count")

    @api.depends("infraction_ids")
    def _compute_infraction_count(self):
        """Computes the number of infractions linked to this vehicle."""
        for vehicle in self:
            vehicle.infraction_count = len(vehicle.infraction_ids)

    def action_view_infractions(self):
        """
        Action to open the list of traffic infractions for the current vehicle.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fleet_traffic_infractions.action_fleet_traffic_infractions"
        )
        action["domain"] = [("id", "in", self.infraction_ids.ids)]
        action["context"] = {"default_vehicle_id": self.id}
        return action

    def get_driver_for_datetime(self, date):
        """
        Returns the driver assigned to the vehicle for a given datetime.

        This method searches for a vehicle assignment log where the provided
        date falls between the start and end datetimes. An open-ended
        assignment (no end datetime) is considered valid.
        """
        self.ensure_one()
        # Search domain to find a log covering the specific 'date'
        domain = [
            ("vehicle_id", "=", self.id),
            ("datetime_start", "<=", date),
            "|",
            ("datetime_end", "=", False),
            ("datetime_end", ">", date),
        ]
        # Order by start date descending to get the most recent assignment
        # in case of overlapping records.
        log = self.env["fleet.vehicle.assignation.log"].search(
            domain, order="datetime_start desc", limit=1
        )
        return log.driver_id if log else self.env["res.partner"]
