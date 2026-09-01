# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EfrotasLog(models.Model):
    _name = "efrotas.log"
    _description = "e-Frotas Communication Log"
    _order = "create_date desc"
    _rec_name = "endpoint"

    endpoint = fields.Char(string="Endpoint", required=True, readonly=True)
    method = fields.Selection(
        [
            ("GET", "GET"),
            ("POST", "POST"),
            ("PUT", "PUT"),
            ("DELETE", "DELETE"),
        ],
        string="Método",
        readonly=True,
    )
    status_code = fields.Integer(string="Status HTTP", readonly=True)
    duration = fields.Float(string="Duração (s)", readonly=True)
    request_payload = fields.Text(string="Payload Requisição", readonly=True)
    response_payload = fields.Text(string="Payload Resposta", readonly=True)
    company_id = fields.Many2one(
        "res.company",
        string="Empresa",
        default=lambda self: self.env.company,
        readonly=True,
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Veículo", readonly=True
    )
