# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetTrafficInfractionType(models.Model):
    _inherit = "fleet.traffic.infraction.type"

    product_id = fields.Many2one(
        "product.product",
        string="Fine Product",
        domain="[('type', '=', 'service')]",
        help="Product used for invoicing this type of infraction. "
        "Its expense account will be used for journal entries.",
    )