# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VehicleCategory(models.Model):
    """
    A classification of vehicle based on functionality
    eg. tow truck, ambulance, trailer, boat
    """

    _name = "fleet.vehicle.category"
    _description = "Classification of vehicle, eg. tow truck, ambulance, trailer, boat"

    name = fields.Char(
        "Category",
        help="Eg. Tow truck, Ambulance, Trailer, Boat",
    )
    description = fields.Html(string="Description")
