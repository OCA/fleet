# Copyright 2020 - 2024, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FleetVehicleInspection(models.Model):
    _name = "fleet.vehicle.inspection"
    _description = "Fleet Vehicle Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    READONLY_STATES = {
        "confirmed": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    name = fields.Char(
        "Reference", required=True, index=True, copy=False, default="New"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancel", "Canceled")],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
        help=" * Draft: not confirmed yet.\n"
        " * Confirmed: inspection has been confirmed.\n"
        " * Canceled: has been canceled, can't be confirmed anymore.",
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        "Vehicle",
        help="Fleet Vehicle",
        required=True,
        states=READONLY_STATES,
    )
    odometer_id = fields.Many2one(
        "fleet.vehicle.odometer",
        "Odometer ID",
        help="Odometer measure of the vehicle at the moment of this log",
    )
    odometer = fields.Float(
        compute="_compute_odometer",
        inverse="_inverse_odometer",
        help="Odometer measure of the vehicle at the moment of this log",
        store=True,
        states=READONLY_STATES,
    )
    odometer_unit = fields.Selection(
        [("kilometers", "Kilometers"), ("miles", "Miles")],
        default="kilometers",
        required=True,
        states=READONLY_STATES,
    )
    date_inspected = fields.Datetime(
        "Inspection Date",
        required=True,
        default=fields.Datetime.now,
        help="Date when the vehicle has been inspected",
        copy=False,
        states=READONLY_STATES,
    )
    inspected_by = fields.Many2one(
        "res.partner",
        tracking=True,
        states=READONLY_STATES,
    )
    direction = fields.Selection(
        selection=[("in", "IN"), ("out", "OUT")],
        default="out",
        states=READONLY_STATES,
    )
    note = fields.Html("Notes", states=READONLY_STATES)
    inspection_line_ids = fields.One2many(
        "fleet.vehicle.inspection.line",
        "inspection_id",
        copy=True,
        auto_join=True,
        states=READONLY_STATES,
    )
    result = fields.Selection(
        [("todo", "Todo"), ("success", "Success"), ("failure", "Failure")],
        "Inspection Result",
        default="todo",
        compute="_compute_inspection_result",
        readonly=True,
        copy=False,
        store=True,
    )
    amount = fields.Monetary("Cost")
    service_type_id = fields.Many2one(
        comodel_name="fleet.service.type",
        string="Service Type",
        domain=[("category", "=", "service")],
    )
    vendor_id = fields.Many2one("res.partner", "Vendor")
    service_id = fields.Many2one(
        comodel_name="fleet.vehicle.log.services", readonly=True, copy=False
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    @api.depends("inspection_line_ids", "inspection_line_ids.result", "state")
    def _compute_inspection_result(self):
        for rec in self:
            if rec.inspection_line_ids:
                if any(line.result == "todo" for line in rec.inspection_line_ids):
                    rec.result = "todo"
                elif any(line.result == "failure" for line in rec.inspection_line_ids):
                    rec.result = "failure"
                else:
                    rec.result = "success"
            else:
                rec.result = "todo"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                prefix_code = "out" if vals.get("direction") == "out" else "in"
                code = "fleet.vehicle.inspection.%s" % (prefix_code)
                vals["name"] = self.env["ir.sequence"].next_by_code(code) or "/"
        return super().create(vals_list)

    def button_cancel(self):
        records = self.filtered(lambda rec: rec.state in ["draft", "confirmed"])
        records.mapped("service_id").sudo().unlink()
        records.state = "cancel"
        return True

    def _prepare_fleet_vehicle_log_services_vals(self):
        return {
            "service_type_id": self.service_type_id.id,
            "description": self.name,
            "vehicle_id": self.vehicle_id.id,
            "amount": self.amount,
            "odometer": self.odometer,
            "vendor_id": self.vendor_id.id if self.vendor_id else False,
            "state": "done",
        }

    def button_confirm(self):
        if any(not rec.inspection_line_ids for rec in self) or any(
            line.result == "todo" for line in self.mapped("inspection_line_ids")
        ):
            raise UserError(
                _("Inspection cannot be completed. " "There are uninspected items.")
            )
        if any(rec.state not in ["draft", "cancel"] for rec in self):
            raise ValidationError(
                _("Only inspections in 'draft' or 'cancel' states can be confirmed")
            )
        if self.amount:
            if not self.service_type_id:
                raise ValidationError(_("Must select service type"))
            self.service_id = self.env["fleet.vehicle.log.services"].create(
                self._prepare_fleet_vehicle_log_services_vals()
            )
        self.state = "confirmed"
        return True

    def button_draft(self):
        self.state = "draft"
        self.result = "todo"
        return True

    @api.depends("odometer_id", "odometer_id.value")
    def _compute_odometer(self):
        for rec in self.filtered("odometer_id"):
            rec.odometer = rec.odometer_id.value

    def _prepare_fleet_vehicle_odometer_vals(self):
        return {
            "value": self.odometer,
            "date": self.date_inspected or fields.Date.context_today(self),
            "vehicle_id": self.vehicle_id.id,
        }

    def _inverse_odometer(self):
        if any(not rec.odometer for rec in self):
            raise UserError(
                _("Emptying the odometer value of a " "vehicle is not allowed.")
            )
        for rec in self:
            rec.odometer_id = self.env["fleet.vehicle.odometer"].create(
                rec._prepare_fleet_vehicle_odometer_vals()
            )
