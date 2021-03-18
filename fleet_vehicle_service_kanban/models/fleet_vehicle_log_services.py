# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicleLogServices(models.Model):
    _name = "fleet.vehicle.log.services"
    _inherit = ["fleet.vehicle.log.services", "mail.thread", "mail.activity.mixin"]
    _description = "Services for vehicles"

    def _default_stage(self):
        stage = self.env.ref(
            "fleet_vehicle_service_kanban.fleet_vehicle_log_services_stage_draft",
            raise_if_not_found=False,
        )
        return stage if stage and stage.id else False

    stage_id = fields.Many2one(
        "fleet.vehicle.log.services.stage",
        "Service Stage",
        default=lambda self: self._default_stage(),
        group_expand="_read_group_stage_ids",
        tracking=True,
        help="Current state of the vehicle",
        ondelete="set null",
    )

    vendor_id = fields.Many2one(tracking=True)
    purchaser_id = fields.Many2one(tracking=True)
    user_id = fields.Many2one(
        "res.users", "Responsible", tracking=True, default=lambda self: self.env.user
    )
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important")], default="0", index=True
    )
    tag_ids = fields.Many2many(
        "fleet.vehicle.log.services.tag",
        "fleet_vehicle_log_services_tag_rel",
        "service_id",
        "tag_id",
        string="Tags",
        help="Classify and analyze your services categories like: Repair, Maintenance",
    )
    active = fields.Boolean(default=True, tracking=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env["fleet.vehicle.log.services.stage"].search([], order=order)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "purchaser_id" in init_values:
            return self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_purchaser_updated"
            )
        if "vendor_id" in init_values:
            return self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_vendor_updated"
            )
        if "user_id" in init_values:
            return self.env.ref(
                "fleet_vehicle_service_kanban."
                "mail_message_subtype_fleet_service_user_updated"
            )
        return super(FleetVehicleLogServices, self)._track_subtype(init_values)
