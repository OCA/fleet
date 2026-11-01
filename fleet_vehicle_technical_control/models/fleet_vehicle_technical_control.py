# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicleTechnicalControl(models.Model):
    _name = "fleet.vehicle.technical.control"
    _description = "Fleet Vehicle Technical Control"
    _order = "date desc, id desc"

    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        required=True,
        ondelete="cascade",
    )
    date = fields.Date(required=True)
    result = fields.Selection(
        selection=[("valid", "Valid"), ("not_valid", "Not Valid")],
        required=True,
    )
    comment = fields.Text()
    attachment_id = fields.Binary(attachment=True)
    attachment_filename = fields.Char()

    @api.constrains("result", "comment")
    def _check_comment_required_if_not_valid(self):
        for control in self:
            if control.result == "not_valid" and not control.comment:
                raise ValidationError(
                    _("A comment is required when the technical control is not valid.")
                )
