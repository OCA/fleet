# Copyright 2021 César Fernández Domínguez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FleetVehicleUsage(models.Model):
    _name = "fleet.vehicle.usage"
    _description = "Vehicle Usage"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name desc"

    name = fields.Char(
        string="Fleet Vehicle Usage",
        copy=False,
        readonly=True,
        default=lambda x: _("New"),
    )
    state = fields.Selection(
        selection=[
            ("draft", "New"),
            ("reserved", "Reserved"),
            ("in_use", "In Use"),
            ("returned", "Returned"),
            ("cancel", "Cancelled"),
        ],
        readonly=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company.id,
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Driver",
        required=True,
        tracking=True,
    )
    picking_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Picked up by",
        tracking=True,
    )
    return_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Returned by",
        tracking=True,
    )
    date_picking = fields.Datetime(
        string="Picking Date",
        copy=False,
        index=True,
        tracking=True,
    )
    date_return = fields.Datetime(
        string="Return Date",
        copy=False,
        index=True,
        tracking=True,
    )
    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicle",
        required=True,
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination",
        change_default=True,
        tracking=True,
    )
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fleet.vehicle.usage"
                ) or _("New")
        return super().create(vals_list)

    def action_pick(self):
        to_pick = self.filtered(lambda x: x.state in ("draft", "reserved"))
        to_pick_with_date = to_pick.filtered(lambda x: not x.date_picking)
        to_pick_with_date.date_picking = fields.Datetime.now()
        to_pick.state = "in_use"
        return True

    def action_return(self):
        to_return = self.filtered(lambda x: x.state == "in_use")
        to_return_with_date = to_return.filtered(lambda x: not x.date_return)
        to_return_with_date.date_return = fields.Datetime.now()
        to_return.state = "returned"
        return True

    def action_cancel(self):
        to_cancel = self.filtered(lambda x: x.state not in ("returned", "cancel"))
        to_cancel.state = "cancel"
        return True

    @api.onchange("user_id")
    def _onchange_user_id(self):
        for usage in self:
            usage.picking_user_id = usage.user_id
            usage.return_user_id = usage.user_id

    @api.constrains("state")
    def _constrains_state(self):
        """Allow only one usage in use per vehicle and driver"""
        for vehicle in self.mapped("vehicle_id"):
            items = vehicle.usage_ids.filtered(lambda x: x.state == "in_use")
            if len(items) > 1:
                raise UserError(
                    _("Every vehicle can only be picked once at the same time!")
                )
        for driver in self.mapped("user_id"):
            domain = [("user_id", "=", driver.id), ("state", "=", "in_use")]
            if self.search_count(domain) > 1:
                raise UserError(_("Every driver can only drive a vehicle at once!"))
