# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    def write(self, vals):
        """
        Overrides write to capture the precise time of a driver change.

        1. Sets the new assignment's start time to the exact moment of the change.
        2. Finds the previous assignment and sets its end time to match the new
           start time.
        """
        assignment_time = fields.Datetime.now()

        previous_logs = {}
        if "driver_id" in vals and vals.get("driver_id"):
            for vehicle in self:
                previous_log = self.env["fleet.vehicle.assignation.log"].search(
                    [
                        ("vehicle_id", "=", vehicle.id),
                        ("driver_id", "=", vehicle.driver_id.id),
                        ("date_end", "=", False),
                    ],
                    order="date_start desc, id desc",
                    limit=1,
                )
                previous_logs[vehicle.id] = previous_log

        res = super().write(vals)

        if "driver_id" in vals and vals.get("driver_id"):
            for vehicle in self:
                new_log = self.env["fleet.vehicle.assignation.log"].search(
                    [
                        ("vehicle_id", "=", vehicle.id),
                        ("driver_id", "=", vals["driver_id"]),
                        ("date_end", "=", False),
                    ],
                    order="date_start desc, id desc",
                    limit=1,
                )

                if new_log:
                    # Update the new log with the precise start time.
                    new_log.datetime_start = assignment_time

                    # Update the previous log with the precise end time.
                    previous_log = previous_logs.get(vehicle.id)
                    if previous_log:
                        previous_log.datetime_end = assignment_time

        return res
