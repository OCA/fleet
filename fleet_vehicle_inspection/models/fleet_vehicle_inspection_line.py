# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleInspectionLine(models.Model):

    _name = "fleet.vehicle.inspection.line"
    _description = "Fleet Vehicle Inspection Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    READONLY_STATES = {
        "confirmed": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    inspection_id = fields.Many2one(
        "fleet.vehicle.inspection",
        string="Inspection Reference",
        required=True,
        ondelete="cascade",
        index=True,
    )

    inspection_item_id = fields.Many2one(
        "fleet.vehicle.inspection.item",
        "Inspection Item",
        required=True,
        tracking=True,
        index=True,
        ondelete="cascade",
        states=READONLY_STATES,
        copy=True,
    )

    inspection_item_instruction = fields.Text(
        "Instruction", related="inspection_item_id.instruction"
    )

    result = fields.Selection(
        [("todo", "Todo"), ("success", "Success"), ("failure", "Failure")],
        "Result",
        default="todo",
        readonly=True,
        required=True,
        copy=False,
    )

    result_description = fields.Char()

    state = fields.Selection(
        related="inspection_id.state",
        readonly=True,
        store=True,
    )

    inspection_line_image_ids = fields.One2many(
        "fleet.vehicle.inspection.line.image", "inspection_line_id", string="Images"
    )

    def action_item_success(self):
        return self.write({"result": "success"})

    def action_item_failure(self):
        return self.write({"result": "failure"})
