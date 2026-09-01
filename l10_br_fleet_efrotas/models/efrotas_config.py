# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from .efrotas_client import EfrotasClient, EfrotasException

_logger = logging.getLogger(__name__)

DEFAULT_HOMOLOGATION_TOKEN = (
    "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDAxMDY4MDAsImlzcyI6Imh0dHBzOi8vZWZyb3Rh"
    "cy5zZXJwcm8uZ292LmJyL2lzc3VlciIsImNucGoiOiIzMzY4MzExMTAwMDEwNyJ9.GnYpQDIZ"
    "Qtprkqp3pv1BEUvf3mHAzpIATlgeCoJbuw4"
)


class EfrotasConfig(models.Model):
    _name = "efrotas.config"
    _description = "Configuração e Credenciais do e-Frotas SENATRAN"
    _order = "sequence, id"

    name = fields.Char(
        string="Nome da Configuração",
        required=True,
        default="Configuração e-Frotas",
    )
    sequence = fields.Integer(string="Sequência", default=10)
    active = fields.Boolean(string="Ativo", default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Empresa",
        default=lambda self: self.env.company,
        required=True,
    )
    environment = fields.Selection(
        [
            ("homologation", "Homologação (Estaleiro SERPRO)"),
            ("production", "Produção (SERPRO / SENATRAN)"),
            ("custom", "Personalizado"),
        ],
        string="Ambiente",
        default="homologation",
        required=True,
    )
    base_url = fields.Char(
        string="URL Base da API",
        required=True,
        default=EfrotasClient.DEFAULT_HOMOLOGATION_URL,
        help="URL base dos serviços e-Frotas (ex: https://hom-efrotas.np.estaleiro.serpro.gov.br/efrotas/api)",
    )
    auth_mode = fields.Selection(
        [
            ("token", "Token JWT (Bearer Token)"),
            ("certificate", "Certificado Digital A1 (mTLS / PKCS#12)"),
        ],
        string="Modo de Autenticação",
        default="token",
        required=True,
    )
    cnpj = fields.Char(
        string="CNPJ Matriz / Titular",
        default="33683111000107",
        help="CNPJ do titular do contrato e-Frotas (para homologação: 33.683.111/0001-07 - SERPRO)",
    )
    cnpj_filial = fields.Char(
        string="CNPJ Filial Padrão",
        help="CNPJ da filial a ser utilizado como padrão nas consultas, se aplicável.",
    )
    token = fields.Text(
        string="Token de Autenticação JWT",
        default=DEFAULT_HOMOLOGATION_TOKEN,
        help="Token JWT para envio no cabeçalho Authorization e x-token-client.",
    )
    certificate_file = fields.Binary(
        string="Arquivo do Certificado A1 (.pfx / .p12)",
        help="Upload do certificado digital ICP-Brasil modelo A1 (formato PKCS#12).",
    )
    certificate_filename = fields.Char(string="Nome do Arquivo do Certificado")
    certificate_password = fields.Char(
        string="Senha do Certificado Digital",
    )
    timeout = fields.Integer(
        string="Timeout de Requisição (segundos)",
        default=30,
        required=True,
    )
    enable_logging = fields.Boolean(
        string="Habilitar Logs Detalhados",
        default=True,
        help="Registra todas as requisições e respostas no histórico de logs para auditoria.",
    )
    last_test_date = fields.Datetime(
        string="Último Teste de Conexão", readonly=True
    )
    last_test_result = fields.Text(
        string="Resultado do Último Teste", readonly=True
    )
    last_test_status = fields.Selection(
        [("success", "Sucesso"), ("failed", "Falha")],
        string="Status do Último Teste",
        readonly=True,
    )

    @api.onchange("environment")
    def _onchange_environment(self):
        if self.environment == "homologation":
            self.base_url = EfrotasClient.DEFAULT_HOMOLOGATION_URL
            self.auth_mode = "token"
            self.cnpj = "33683111000107"
            if not self.token or self.token.strip() == "":
                self.token = DEFAULT_HOMOLOGATION_TOKEN
        elif self.environment == "production":
            self.base_url = EfrotasClient.DEFAULT_PRODUCTION_URL
            self.auth_mode = "certificate"

    def _log_communication(
        self,
        url,
        method,
        status_code,
        request_payload,
        response_payload,
        duration,
        vehicle_id=None,
    ):
        """Grava registro no modelo efrotas.log."""
        if not self.enable_logging:
            return
        try:
            self.env["efrotas.log"].sudo().create(
                {
                    "endpoint": url,
                    "method": method,
                    "status_code": status_code,
                    "duration": duration,
                    "request_payload": request_payload,
                    "response_payload": (response_payload or "")[
                        :100000
                    ],  # trunca respostas gigantes
                    "company_id": self.company_id.id,
                    "vehicle_id": vehicle_id,
                }
            )
        except Exception as e:
            _logger.warning("Erro ao registrar log e-Frotas: %s", e)

    def get_client(self, vehicle_id=None):
        """Retorna uma instância configurada de EfrotasClient."""
        self.ensure_one()
        cert_data = None
        if self.auth_mode == "certificate" and self.certificate_file:
            cert_data = base64.b64decode(self.certificate_file)

        def log_cb(
            url,
            method,
            status_code,
            request_payload,
            response_payload,
            duration,
        ):
            self._log_communication(
                url=url,
                method=method,
                status_code=status_code,
                request_payload=request_payload,
                response_payload=response_payload,
                duration=duration,
                vehicle_id=vehicle_id,
            )

        return EfrotasClient(
            base_url=self.base_url,
            token=self.token if self.auth_mode == "token" else None,
            certificate_data=cert_data,
            certificate_password=self.certificate_password,
            timeout=self.timeout or 30,
            log_callback=log_cb if self.enable_logging else None,
        )

    def action_test_connection(self):
        """Testa a conectividade com o serviço e-Frotas e valida as credenciais."""
        self.ensure_one()
        client = self.get_client()

        try:
            if self.environment == "homologation":
                test_plate = "SAV0741"
                res = client.get_veiculo_por_placa(test_plate)
                placa_retornada = (
                    res.get("placa") if isinstance(res, dict) else str(res)
                )
                msg = _(
                    "Conexão estabelecida com sucesso em Homologação! Veículo de teste: %s"
                ) % (placa_retornada or test_plate)
            else:
                # Em produção, consulta a frota vinculada ao CNPJ do certificado
                res = client.get_veiculos(
                    cnpj_filial=self.cnpj_filial, pagina=1, quantidade=20
                )
                total = 0
                sample_plates = []

                if isinstance(res, list):
                    total = len(res)
                    sample_plates = [
                        v.get("placa")
                        for v in res
                        if isinstance(v, dict) and v.get("placa")
                    ]
                elif isinstance(res, dict):
                    items = (
                        res.get("veiculos")
                        or res.get("content")
                        or res.get("itens")
                        or res.get("dados")
                        or res.get("frota")
                        or []
                    )
                    if isinstance(items, list):
                        sample_plates = [
                            v.get("placa")
                            for v in items
                            if isinstance(v, dict) and v.get("placa")
                        ]

                    total = (
                        res.get("totalRegistros")
                        or res.get("totalElementos")
                        or res.get("totalElements")
                        or res.get("total")
                        or res.get("count")
                        or res.get("total_registros")
                        or res.get("qtdRegistros")
                        or res.get("quantidade")
                        or (
                            isinstance(res.get("page"), dict)
                            and res["page"].get("totalElements")
                        )
                        or (
                            isinstance(res.get("paginacao"), dict)
                            and res["paginacao"].get("totalRegistros")
                        )
                        or len(items)
                    )

                details = f"Veículos encontrados: {total}"
                if sample_plates:
                    plates_str = ", ".join(sample_plates[:5])
                    if len(sample_plates) > 5:
                        plates_str += f" (+{len(sample_plates) - 5})"
                    details += f" | Placas de amostra: {plates_str}"

                msg = _(
                    "Conexão estabelecida com sucesso em Produção com o certificado digital! (%s)"
                ) % details
            self.write(
                {
                    "last_test_date": fields.Datetime.now(),
                    "last_test_result": msg,
                    "last_test_status": "success",
                }
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("e-Frotas SENATRAN"),
                    "message": msg,
                    "type": "success",
                    "sticky": False,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
        except EfrotasException as ex:
            msg = _("Falha na conexão com e-Frotas: %s") % str(ex)
            _logger.warning("Falha no teste de conexão e-Frotas: %s", msg)
            self.write(
                {
                    "last_test_date": fields.Datetime.now(),
                    "last_test_result": msg,
                    "last_test_status": "failed",
                }
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Falha no Teste de Conexão"),
                    "message": msg,
                    "type": "danger",
                    "sticky": True,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
        except Exception as ex:
            msg = _("Erro inesperado ao testar conexão: %s") % str(ex)
            _logger.exception("Erro inesperado no teste de conexão e-Frotas: %s", msg)
            self.write(
                {
                    "last_test_date": fields.Datetime.now(),
                    "last_test_result": msg,
                    "last_test_status": "failed",
                }
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Erro no Teste de Conexão"),
                    "message": msg,
                    "type": "danger",
                    "sticky": True,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
