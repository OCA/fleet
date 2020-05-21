# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleLogServicesStage(models.Model):
    _name = "fleet.vehicle.log.services.stage"
    _order = "sequence asc"
    _description = "Vehicle Services Stages"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(help="Used to order the stages")
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="If True this stage is folded in the kanban view.",
    )

    _sql_constraints = [
        (
            "fleet_service_stage_name_unique",
            "unique(name)",
            "Stage name already exists",
        )
    ]
