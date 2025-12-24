# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleLogServicesTag(models.Model):
    _name = "fleet.vehicle.log.services.tag"
    _description = "Services Tags"

    name = fields.Char("Tag Name", required=True, translate=True)
    color = fields.Integer("Color Index")

    _name_unique = models.Constraint(
        "unique(name)",
        "Tag name already exists !",
    )
