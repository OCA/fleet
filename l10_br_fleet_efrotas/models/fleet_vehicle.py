# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
from odoo import _, fields, models
from odoo.exceptions import UserError
from .efrotas_client import EfrotasException

_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    # Campos e-Frotas SENATRAN
    efrotas_config_id = fields.Many2one(
        "efrotas.config",
        string="Configuração e-Frotas",
        help="Configuração e-Frotas utilizada para este veículo. Se não informada, usará a ativa da empresa.",
    )
    efrotas_synced = fields.Boolean(
        string="Sincronizado e-Frotas", readonly=True
    )
    efrotas_last_sync = fields.Datetime(
        string="Última Sincronização", readonly=True
    )
    efrotas_renavam = fields.Char(string="Renavam", readonly=True)
    efrotas_municipio = fields.Char(
        string="Município de Emplacamento", readonly=True
    )
    efrotas_chassi = fields.Char(string="Chassi (e-Frotas)", readonly=True)
    efrotas_cor = fields.Char(string="Cor", readonly=True)
    efrotas_ano_fabricacao = fields.Integer(
        string="Ano Fabricação", readonly=True
    )
    efrotas_ano_modelo = fields.Integer(string="Ano Modelo", readonly=True)
    efrotas_combustivel = fields.Char(string="Combustível", readonly=True)
    efrotas_tipo_veiculo = fields.Char(string="Tipo de Veículo", readonly=True)
    efrotas_especie = fields.Char(string="Espécie", readonly=True)
    efrotas_categoria = fields.Char(string="Categoria", readonly=True)
    efrotas_marca_modelo = fields.Char(string="Marca/Modelo", readonly=True)

    # Indicadores e alertas
    efrotas_is_associated = fields.Boolean(
        string="Associado à Frota",
        readonly=True,
        help="Indica se o veículo está oficialmente associado ao CNPJ no SENATRAN.",
    )
    efrotas_has_theft = fields.Boolean(
        string="Alerta Roubo/Furto",
        readonly=True,
        help="Indica se há registro ativo de furto ou roubo no SENATRAN.",
    )
    efrotas_has_recall = fields.Boolean(
        string="Recall Pendente",
        readonly=True,
        help="Indica se há chamado de recall pendente para o veículo.",
    )
    efrotas_has_renajud = fields.Boolean(
        string="Restrição Judicial (RENAJUD)",
        readonly=True,
        help="Indica se há restrição judicial cadastrada no RENAJUD.",
    )
    efrotas_has_infractions = fields.Boolean(
        string="Infrações Exigíveis",
        readonly=True,
        help="Indica se há infrações de trânsito em aberto.",
    )
    efrotas_has_sale_comm = fields.Boolean(
        string="Comunicação de Venda",
        readonly=True,
        help="Indica se há comunicação de venda registrada.",
    )
    efrotas_last_status_msg = fields.Char(
        string="Mensagem do Status", readonly=True
    )

    # Relacionamento com logs
    efrotas_log_ids = fields.One2many(
        "efrotas.log", "vehicle_id", string="Logs de Comunicação e-Frotas"
    )
    efrotas_log_count = fields.Integer(
        string="Total de Logs e-Frotas",
        compute="_compute_efrotas_log_count",
    )

    def _compute_efrotas_log_count(self):
        for vehicle in self:
            vehicle.efrotas_log_count = len(vehicle.efrotas_log_ids)

    def action_view_efrotas_logs(self):
        self.ensure_one()
        action = self.env.ref("l10_br_fleet_efrotas.action_efrotas_log").read()[0]
        action["domain"] = [("vehicle_id", "=", self.id)]
        action["context"] = {"default_vehicle_id": self.id}
        return action

    def _get_efrotas_config(self):
        """Obtém a configuração ativa para o veículo."""
        self.ensure_one()
        if self.efrotas_config_id:
            return self.efrotas_config_id
        config = self.env["efrotas.config"].search(
            [
                ("company_id", "=", self.company_id.id or self.env.company.id),
                ("active", "=", True),
            ],
            limit=1,
        )
        if not config:
            config = self.env["efrotas.config"].search(
                [("active", "=", True)], limit=1
            )
        if not config:
            raise UserError(
                _(
                    "Nenhuma configuração ativa do e-Frotas encontrada. "
                    "Por favor, configure o e-Frotas em Frota > Configuração > e-Frotas SENATRAN."
                )
            )
        return config

    def _get_efrotas_client(self):
        """Obtém o cliente de API configurado para este veículo."""
        config = self._get_efrotas_config()
        return config.get_client(vehicle_id=self.id)

    def action_efrotas_sync(self):
        """Consulta os dados cadastrais e indicadores do veículo no e-Frotas e atualiza o cadastro."""
        for vehicle in self:
            if not vehicle.license_plate:
                raise UserError(
                    _("Informe a placa do veículo antes de consultar o e-Frotas.")
                )

            client = vehicle._get_efrotas_client()
            placa = vehicle.license_plate.replace("-", "").strip().upper()

            try:
                # 1. Consulta dados cadastrais
                data = client.get_veiculo_por_placa(placa)

                # 2. Consulta associação
                assoc_data = {}
                try:
                    assoc_data = client.check_veiculo_associado(placa)
                except Exception as ex_assoc:
                    _logger.info(
                        "Falha ao checar associação para placa %s: %s",
                        placa,
                        ex_assoc,
                    )

                is_associated = True
                if isinstance(assoc_data, dict):
                    msg = assoc_data.get("mensagem", "")
                    if "não" in msg.lower() or "nao" in msg.lower():
                        is_associated = False

                vals = {
                    "efrotas_synced": True,
                    "efrotas_last_sync": fields.Datetime.now(),
                    "efrotas_is_associated": is_associated,
                    "efrotas_last_status_msg": _(
                        "Sincronizado com sucesso via e-Frotas."
                    ),
                }

                if isinstance(data, dict):
                    if data.get("renavam"):
                        vals["efrotas_renavam"] = data.get("renavam")
                    if data.get("chassi"):
                        vals["efrotas_chassi"] = data.get("chassi")
                        if not vehicle.vin_sn:
                            vals["vin_sn"] = data.get("chassi")
                    if data.get("descricaoMunicipioEmplacamento"):
                        vals["efrotas_municipio"] = data.get(
                            "descricaoMunicipioEmplacamento"
                        )
                    if data.get("descricaoCor"):
                        vals["efrotas_cor"] = data.get("descricaoCor")
                        if not vehicle.color:
                            vals["color"] = data.get("descricaoCor")
                    if data.get("anoFabricacao"):
                        vals["efrotas_ano_fabricacao"] = int(
                            data.get("anoFabricacao")
                        )
                    if data.get("anoModelo"):
                        vals["efrotas_ano_modelo"] = int(data.get("anoModelo"))
                        if not vehicle.model_year:
                            vals["model_year"] = str(data.get("anoModelo"))
                    if data.get("descricaoCombustivel"):
                        vals["efrotas_combustivel"] = data.get(
                            "descricaoCombustivel"
                        )
                    if data.get("descricaoTipoVeiculo"):
                        vals["efrotas_tipo_veiculo"] = data.get(
                            "descricaoTipoVeiculo"
                        )
                    if data.get("descricaoEspecie"):
                        vals["efrotas_especie"] = data.get("descricaoEspecie")
                    if data.get("descricaoCategoria"):
                        vals["efrotas_categoria"] = data.get(
                            "descricaoCategoria"
                        )
                    if data.get("descricaoMarcaModelo"):
                        vals["efrotas_marca_modelo"] = data.get(
                            "descricaoMarcaModelo"
                        )

                    # Indicadores
                    vals["efrotas_has_theft"] = bool(
                        data.get("indicadorRouboFurto")
                        or data.get("ocorrenciaRouboFurto")
                    )
                    vals["efrotas_has_recall"] = bool(
                        data.get("indicadorRecall")
                        or data.get("ocorrenciaRecall")
                    )
                    vals["efrotas_has_renajud"] = bool(
                        data.get("indicadorRestricaoJudicial")
                        or data.get("restricoesJudiciais")
                    )
                    vals["efrotas_has_infractions"] = bool(
                        data.get("indicadorInfracao")
                        or data.get("infracoesExigiveis")
                    )
                    vals["efrotas_has_sale_comm"] = bool(
                        data.get("indicadorComunicacaoVenda")
                    )

                vehicle.write(vals)

            except EfrotasException as ex:
                msg = _("Falha na sincronização com e-Frotas: %s") % str(ex)
                _logger.warning("Erro ao sincronizar veículo %s: %s", vehicle.license_plate, msg)
                vehicle.write({"efrotas_last_status_msg": msg})
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Falha na Sincronização"),
                        "message": _("Erro ao consultar e-Frotas para o veículo %s: %s")
                        % (vehicle.name or vehicle.license_plate, str(ex)),
                        "type": "danger",
                        "sticky": True,
                        "next": {
                            "type": "ir.actions.client",
                            "tag": "reload",
                        },
                    },
                }
            except Exception as ex:
                msg = _("Erro inesperado na sincronização: %s") % str(ex)
                _logger.exception("Erro inesperado ao sincronizar veículo %s: %s", vehicle.license_plate, msg)
                vehicle.write({"efrotas_last_status_msg": msg})
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Erro na Sincronização"),
                        "message": _("Erro inesperado para o veículo %s: %s")
                        % (vehicle.name or vehicle.license_plate, str(ex)),
                        "type": "danger",
                        "sticky": True,
                        "next": {
                            "type": "ir.actions.client",
                            "tag": "reload",
                        },
                    },
                }

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("e-Frotas SENATRAN"),
                "message": _(
                    "Veículo(s) sincronizado(s) com sucesso com o e-Frotas!"
                ),
                "type": "success",
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "reload",
                },
            },
        }

    def action_efrotas_download_crlv(self):
        """Obtém o documento digital CRLV-e da API e anexa como PDF ao veículo."""
        self.ensure_one()
        if not self.license_plate:
            raise UserError(_("Informe a placa do veículo antes de baixar o CRLV-e."))

        client = self._get_efrotas_client()
        placa = self.license_plate.replace("-", "").strip().upper()

        try:
            res = client.get_crlv(placa)
            pdf_base64 = res.get("pdfBase64") if isinstance(res, dict) else None

            if not pdf_base64:
                raise UserError(
                    _(
                        "A resposta do e-Frotas não continha o PDF em base64 do CRLV-e."
                    )
                )

            ano = res.get("anoLicenciamento") or res.get("anoExercicio") or ""
            filename = f"CRLV-e_{placa}{f'_{ano}' if ano else ''}.pdf"

            attachment = self.env["ir.attachment"].create(
                {
                    "name": filename,
                    "type": "binary",
                    "datas": pdf_base64,
                    "res_model": "fleet.vehicle",
                    "res_id": self.id,
                    "mimetype": "application/pdf",
                }
            )

            msg = _("CRLV-e baixado com sucesso e anexado ao veículo (%s).") % filename
            self.message_post(
                body=msg,
                attachment_ids=[attachment.id],
            )

            return {
                "type": "ir.actions.act_url",
                "url": f"/web/content/{attachment.id}?download=true",
                "target": "self",
            }
        except EfrotasException as ex:
            raise UserError(_("Erro ao obter CRLV-e no e-Frotas: %s") % str(ex))

    def action_efrotas_check_association(self):
        """Verifica se o veículo está associado ao CNPJ configurado."""
        self.ensure_one()
        if not self.license_plate:
            raise UserError(_("Informe a placa do veículo."))

        client = self._get_efrotas_client()
        placa = self.license_plate.replace("-", "").strip().upper()

        try:
            res = client.check_veiculo_associado(placa)
            msg = res.get("mensagem", _("Consulta concluída"))
            is_associated = not (
                "não" in msg.lower() or "nao" in msg.lower()
            )

            self.write(
                {
                    "efrotas_is_associated": is_associated,
                    "efrotas_last_status_msg": msg,
                }
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Associação e-Frotas"),
                    "message": msg,
                    "type": "info" if is_associated else "warning",
                    "sticky": False,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
        except EfrotasException as ex:
            msg = _("Erro ao verificar associação no e-Frotas: %s") % str(ex)
            _logger.warning("Erro ao checar associação placa %s: %s", placa, msg)
            self.write({"efrotas_last_status_msg": msg})
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Erro na Associação"),
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
            msg = _("Erro inesperado ao verificar associação: %s") % str(ex)
            _logger.exception("Erro inesperado ao checar associação placa %s: %s", placa, msg)
            self.write({"efrotas_last_status_msg": msg})
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Erro na Associação"),
                    "message": msg,
                    "type": "danger",
                    "sticky": True,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
