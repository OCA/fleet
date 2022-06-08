# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FleetVehicleLogFuel(models.Model):
    _name = "fleet.vehicle.log.fuel"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "service_type_id"
    _description = "Fuel log for vehicles"

    active = fields.Boolean(default=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", "Vehicle", required=True, help="Vehicle concerned by this log"
    )
    amount = fields.Monetary("Cost")
    description = fields.Char("Description")
    odometer_id = fields.Many2one(
        "fleet.vehicle.odometer",
        "Odometer",
        help="Odometer measure of the vehicle at the moment of this log",
    )
    odometer = fields.Float(
        compute="_compute_odometer",
        inverse="_inverse_odometer",
        string="Odometer Value",
        help="Odometer measure of the vehicle at the moment of this log",
    )
    odometer_unit = fields.Selection(
        related="vehicle_id.odometer_unit", string="Unit", readonly=True
    )
    date = fields.Date(
        help="Date when the cost has been executed", default=fields.Date.context_today
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    purchaser_id = fields.Many2one(
        "res.partner",
        string="Driver",
        compute="_compute_purchaser_id",
        readonly=False,
        store=True,
    )
    inv_ref = fields.Char("Vendor Reference")
    vendor_id = fields.Many2one("res.partner", "Vendor")
    notes = fields.Text()
    service_type_id = fields.Many2one(
        "fleet.service.type",
        "Service Type",
        required=True,
        default=lambda self: self.env.ref(
            "fleet.type_service_refueling", raise_if_not_found=False
        ),
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
    liter = fields.Float()
    price_per_liter = fields.Float()

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

    def _compute_odometer(self):
        self.odometer = 0
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value

    def _inverse_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(
                    _("Emptying the odometer value of a vehicle is not allowed.")
                )
            odometer = self.env["fleet.vehicle.odometer"].create(
                {
                    "value": record.odometer,
                    "date": record.date or fields.Date.context_today(record),
                    "vehicle_id": record.vehicle_id.id,
                }
            )
            self.odometer_id = odometer

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            if "odometer" in data and not data["odometer"]:
                # if received value for odometer is 0, then remove it from the
                # data as it would result to the creation of an odometer log with 0,
                # which is to be avoided
                del data["odometer"]
        return super().create(vals_list)

    @api.depends("vehicle_id")
    def _compute_purchaser_id(self):
        for service in self:
            service.purchaser_id = service.vehicle_id.driver_id
