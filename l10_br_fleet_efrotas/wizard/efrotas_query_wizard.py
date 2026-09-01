# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import _, fields, models
from odoo.exceptions import UserError
from ..models.efrotas_client import EfrotasException


class EfrotasQueryWizard(models.TransientModel):
    _name = "efrotas.query.wizard"
    _description = "Assistente de Consultas e-Frotas SENATRAN"

    config_id = fields.Many2one(
        "efrotas.config",
        string="Configuração e-Frotas",
        required=True,
        default=lambda self: self.env["efrotas.config"].search(
            [("active", "=", True)], limit=1
        ),
    )
    query_type = fields.Selection(
        [
            ("veiculo", "Dados Cadastrais do Veículo"),
            ("associado", "Verificar Associação à Frota"),
            ("crlv", "Documento Digital (CRLV-e)"),
            ("infracoes", "Infrações por Período"),
            ("infracao_detalhe", "Detalhe de Infração por Chave"),
            ("roubo_furto", "Histórico de Roubo / Furto"),
            ("recall", "Registros de Recall Pendente"),
            ("renajud", "Restrições Judiciais (RENAJUD)"),
            ("notificacoes", "Notificações / Eventos Recebidos"),
        ],
        string="Tipo de Consulta",
        default="veiculo",
        required=True,
    )
    license_plate = fields.Char(
        string="Placa",
        help="Placa do veículo a consultar (ex: SAV0741)",
    )
    date_start = fields.Date(
        string="Data Inicial",
        default=lambda self: date.today() - relativedelta(months=1),
    )
    date_end = fields.Date(
        string="Data Final",
        default=lambda self: date.today(),
    )
    codigo_orgao = fields.Char(string="Código do Órgão Autuador")
    numero_ait = fields.Char(string="Número do AIT")
    codigo_infracao = fields.Char(string="Código da Infração")
    tipo_restricao = fields.Char(
        string="Tipo de Restrição RENAJUD",
        help="Filtro opcional para restrições judiciais",
    )
    result_text = fields.Text(string="Resultado JSON", readonly=True)
    pdf_attachment_id = fields.Many2one(
        "ir.attachment", string="Arquivo PDF Gerado", readonly=True
    )

    def action_execute_query(self):
        """Executa a consulta selecionada utilizando o EfrotasClient."""
        self.ensure_one()
        if not self.config_id:
            raise UserError(_("Selecione uma configuração do e-Frotas."))

        client = self.config_id.get_client()
        placa = (
            self.license_plate.replace("-", "").strip().upper()
            if self.license_plate
            else ""
        )

        try:
            res_data = None

            if self.query_type == "veiculo":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                res_data = client.get_veiculo_por_placa(placa)

            elif self.query_type == "associado":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                res_data = client.check_veiculo_associado(placa)

            elif self.query_type == "crlv":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                res_data = client.get_crlv(placa)
                if isinstance(res_data, dict) and res_data.get("pdfBase64"):
                    att = self.env["ir.attachment"].create(
                        {
                            "name": f"CRLV-e_{placa}.pdf",
                            "type": "binary",
                            "datas": res_data.get("pdfBase64"),
                            "mimetype": "application/pdf",
                        }
                    )
                    self.pdf_attachment_id = att.id

            elif self.query_type == "infracoes":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                d_init = self.date_start.strftime("%Y-%m-%d")
                d_end = self.date_end.strftime("%Y-%m-%d")
                res_data = client.get_infracoes_veiculo(placa, d_init, d_end)

            elif self.query_type == "infracao_detalhe":
                if not (
                    self.codigo_orgao
                    and self.numero_ait
                    and self.codigo_infracao
                ):
                    raise UserError(
                        _(
                            "Preencha Código do Órgão, Número do AIT e Código da Infração."
                        )
                    )
                res_data = client.get_detalhes_infracao(
                    self.codigo_orgao.strip(),
                    self.numero_ait.strip(),
                    self.codigo_infracao.strip(),
                )

            elif self.query_type == "roubo_furto":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                res_data = client.get_ocorrencias_roubo_furto(placa)

            elif self.query_type == "recall":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                res_data = client.get_recall(placa)

            elif self.query_type == "renajud":
                if not placa:
                    raise UserError(_("Informe a placa do veículo."))
                res_data = client.get_restricoes_renajud(
                    placa, tipo_restricao=self.tipo_restricao or None
                )

            elif self.query_type == "notificacoes":
                d_init = self.date_start.strftime("%d%m%Y")
                d_end = self.date_end.strftime("%d%m%Y")
                res_data = client.get_notificacoes(d_init, d_end)

            formatted_result = (
                json.dumps(res_data, indent=2, ensure_ascii=False)
                if isinstance(res_data, (dict, list))
                else str(res_data)
            )
            self.result_text = formatted_result

            return {
                "type": "ir.actions.act_window",
                "res_model": "efrotas.query.wizard",
                "res_id": self.id,
                "view_mode": "form",
                "target": "new",
            }

        except EfrotasException as ex:
            raise UserError(_("Erro na consulta e-Frotas: %s") % str(ex))
