# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FleetVehicleLogFuel(models.Model):
    _name = "fleet.vehicle.log.fuel"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "service_type_id"
    _description = "Fuel log for vehicles"

    READONLY_STATES = {
        "running": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    active = fields.Boolean(default=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        "Vehicle",
        required=True,
        help="Vehicle concerned by this log",
        states=READONLY_STATES,
    )
    amount = fields.Monetary("Cost", states=READONLY_STATES)
    description = fields.Char(states=READONLY_STATES)
    odometer_id = fields.Many2one(
        "fleet.vehicle.odometer",
        "Odometer",
        help="Odometer measure of the vehicle at the moment of this log",
        states=READONLY_STATES,
    )
    odometer = fields.Float(
        compute="_compute_odometer",
        store=True,
        inverse="_inverse_odometer",
        string="Odometer Value",
        help="Odometer measure of the vehicle at the moment of this log",
        states=READONLY_STATES,
    )
    odometer_unit = fields.Selection(related="vehicle_id.odometer_unit", string="Unit")
    date = fields.Date(
        help="Date when the cost has been executed",
        default=fields.Date.context_today,
        states=READONLY_STATES,
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    purchaser_id = fields.Many2one(
        "res.partner",
        string="Driver",
        compute="_compute_purchaser_id",
        store=True,
        states=READONLY_STATES,
    )
    inv_ref = fields.Char("Vendor Reference", states=READONLY_STATES)
    vendor_id = fields.Many2one("res.partner", "Vendor", states=READONLY_STATES)
    notes = fields.Text()
    service_type_id = fields.Many2one(
        "fleet.service.type",
        "Service Type",
        required=True,
        default=lambda self: self.env.ref(
            "fleet.type_service_refueling", raise_if_not_found=False
        ),
        states=READONLY_STATES,
    )
    state = fields.Selection(
        [
            ("todo", "To Do"),
            ("running", "Running"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="todo",
        string="Stage",
    )
    liter = fields.Float(states=READONLY_STATES)
    price_per_liter = fields.Float(states=READONLY_STATES)
    service_id = fields.Many2one(
        comodel_name="fleet.vehicle.log.services", readonly=True, copy=False
    )

    @api.onchange("liter", "price_per_liter", "amount")
    def _onchange_liter_price_amount(self):
        liter = float(self.liter)
        price_per_liter = float(self.price_per_liter)
        amount = float(self.amount)
        if (
            liter > 0
            and price_per_liter > 0
            and round(liter * price_per_liter, 2) != amount
        ):
            self.amount = round(liter * price_per_liter, 2)
        elif amount > 0 and liter > 0 and round(amount / liter, 2) != price_per_liter:
            self.price_per_liter = round(amount / liter, 2)
        elif (
            amount > 0
            and price_per_liter > 0
            and round(amount / price_per_liter, 2) != liter
        ):
            self.liter = round(amount / price_per_liter, 2)

    @api.depends("odometer_id", "odometer_id.value")
    def _compute_odometer(self):
        for record in self.filtered("odometer_id"):
            record.odometer = record.odometer_id.value

    def _inverse_odometer(self):
        if any(not x.odometer for x in self):
            raise UserError(
                _("Emptying the odometer value of a vehicle is not allowed.")
            )
        for record in self:
            self.odometer_id = self.env["fleet.vehicle.odometer"].create(
                record._prepare_fleet_vehicle_odometer_vals()
            )

    @api.depends("vehicle_id")
    def _compute_purchaser_id(self):
        for service in self:
            service.purchaser_id = service.vehicle_id.driver_id

    def button_running(self):
        self.filtered(lambda x: x.state == "todo").state = "running"
        return True

    def _prepare_fleet_vehicle_odometer_vals(self):
        return {
            "value": self.odometer,
            "date": self.date or fields.Date.context_today(self),
            "vehicle_id": self.vehicle_id.id,
        }

    def _prepare_fleet_vehicle_log_services_vals(self):
        return {
            "service_type_id": self.service_type_id.id,
            "description": self.description,
            "vehicle_id": self.vehicle_id.id,
            "amount": self.amount,
            "odometer": self.odometer,
            "vendor_id": self.vendor_id.id if self.vendor_id else False,
            "state": "done",
        }

    def button_todo(self):
        records = self.filtered(lambda x: x.state == "cancelled")
        records.state = "todo"
        return True

    def button_done(self):
        for item in self.filtered(lambda x: x.state == "running"):
            item.service_id = self.env["fleet.vehicle.log.services"].create(
                self._prepare_fleet_vehicle_log_services_vals()
            )
            item.state = "done"
        return True

    def button_cancel(self):
        records = self.filtered(lambda x: x.state in ["todo", "running", "done"])
        records.mapped("service_id").sudo().unlink()
        records.state = "cancelled"
        return True
