# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    vehicle_category_id = fields.Many2one(
        "fleet.vehicle.category",
        "Vehicle Category",
        help="Eg. Tow truck, Ambulance, Trailer, Boat",
    )
