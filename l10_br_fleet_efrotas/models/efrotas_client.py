# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging
import os
import tempfile
import time
import requests

_logger = logging.getLogger(__name__)


class EfrotasException(Exception):
    """Exceção base para erros na integração com o e-Frotas."""

    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class EfrotasAuthError(EfrotasException):
    """Exceção para erros de autenticação (HTTP 401/403)."""


class EfrotasNotFoundError(EfrotasException):
    """Exceção para recursos não encontrados (HTTP 404)."""


class EfrotasValidationError(EfrotasException):
    """Exceção para erros de validação ou parâmetros inválidos (HTTP 400/422)."""


class EfrotasClient:
    """Cliente HTTP para comunicação com a API do e-Frotas SENATRAN / SERPRO.

    Suporta:
    - Autenticação via Bearer Token JWT (Homologação e Produção)
    - Autenticação via Certificado Digital A1 (PKCS#12 / .pfx / .p12 / mTLS)
    - Serviços: CRLVe, Consultas, Gerenciamento (Autorizador), Notificações e Transacional.
    """

    DEFAULT_HOMOLOGATION_URL = (
        "https://hom-efrotas.np.estaleiro.serpro.gov.br/efrotas/api"
    )
    DEFAULT_PRODUCTION_URL = (
        "https://efrotas.estaleiro.serpro.gov.br/efrotas/api"
    )

    def __init__(
        self,
        base_url=None,
        token=None,
        certificate_data=None,
        certificate_password=None,
        timeout=30,
        log_callback=None,
    ):
        """Inicializa o cliente e-Frotas.

        :param base_url: URL base da API (ex: https://hom-efrotas.np.estaleiro.serpro.gov.br/efrotas/api)
        :param token: Bearer token JWT para autenticação.
        :param certificate_data: Conteúdo binário (bytes) do certificado A1 (.pfx/.p12).
        :param certificate_password: Senha do certificado digital.
        :param timeout: Tempo limite das requisições em segundos.
        :param log_callback: Função callable(endpoint, method, status_code, request_body, response_body, duration) para log.
        """
        self.base_url = (base_url or self.DEFAULT_HOMOLOGATION_URL).rstrip("/")
        self.token = token
        self.certificate_data = certificate_data
        self.certificate_password = certificate_password
        self.timeout = timeout
        self.log_callback = log_callback
        self._cert_temp_files = []

    def __del__(self):
        self._cleanup_temp_files()

    def _cleanup_temp_files(self):
        for path in self._cert_temp_files:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception:
                pass
        self._cert_temp_files.clear()

    def _get_cert_files(self):
        """Converte o certificado PKCS#12 em arquivos temporários PEM (cert e chave privada) para requests mTLS."""
        if not self.certificate_data:
            return None

        if self._cert_temp_files and len(self._cert_temp_files) == 2:
            return tuple(self._cert_temp_files)

        try:
            from cryptography.hazmat.primitives.serialization import (
                Encoding,
                NoEncryption,
                PrivateFormat,
                pkcs12,
            )

            import base64

            cert_data = self.certificate_data
            if isinstance(cert_data, str):
                try:
                    cert_data = base64.b64decode(cert_data)
                except Exception:
                    cert_data = cert_data.encode("latin1")

            pwd_bytes = None
            if self.certificate_password:
                if isinstance(self.certificate_password, str):
                    pwd_bytes = self.certificate_password.encode("utf-8")
                elif isinstance(self.certificate_password, bytes):
                    pwd_bytes = self.certificate_password

            from cryptography.hazmat.backends import default_backend

            private_key, certificate, additional_certificates = (
                pkcs12.load_key_and_certificates(
                    cert_data, pwd_bytes, default_backend()
                )
            )

            if not certificate:
                raise EfrotasAuthError(
                    "O arquivo PKCS#12 (.pfx/.p12) não contém um certificado público válido."
                )
            if not private_key:
                raise EfrotasAuthError(
                    "O arquivo PKCS#12 (.pfx/.p12) não contém uma chave privada válida."
                )

            cert_pem = certificate.public_bytes(Encoding.PEM)
            if additional_certificates:
                for add_cert in additional_certificates:
                    cert_pem += add_cert.public_bytes(Encoding.PEM)

            key_pem = private_key.private_bytes(
                Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
            )

            cert_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".pem", prefix="efrotas_cert_"
            )
            cert_file.write(cert_pem)
            cert_file.flush()
            cert_file.close()

            key_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".pem", prefix="efrotas_key_"
            )
            key_file.write(key_pem)
            key_file.flush()
            key_file.close()

            self._cert_temp_files = [cert_file.name, key_file.name]
            return tuple(self._cert_temp_files)
        except Exception as e:
            _logger.error(
                "Falha ao processar certificado digital PKCS#12: %s", e
            )
            raise EfrotasAuthError(
                f"Erro ao processar certificado digital: {e}"
            )

    def _build_url(self, service, path):
        """Monta a URL completa do endpoint.

        :param service: 'crlv', 'consultas', 'autorizador', 'notificacoes', 'transacional'
        :param path: Subcaminho da API (ex: '/v1/veiculos')
        """
        clean_path = "/" + path.lstrip("/")
        return f"{self.base_url}/{service}{clean_path}"

    def _request(
        self,
        service,
        path,
        method="GET",
        params=None,
        data=None,
        json_data=None,
        headers=None,
    ):
        """Executa a requisição HTTP com os cabeçalhos de autenticação e tratamento de erros."""
        url = self._build_url(service, path)
        req_headers = {
            "Accept": "application/json",
            "User-Agent": "Odoo-Fleet-eFrotas-Connector/1.0",
        }

        if self.token:
            clean_token = self.token.strip()
            if not clean_token.lower().startswith("bearer "):
                req_headers["Authorization"] = f"Bearer {clean_token}"
                req_headers["x-token-client"] = clean_token
            else:
                raw_token = clean_token.split(" ", 1)[1]
                req_headers["Authorization"] = clean_token
                req_headers["x-token-client"] = raw_token

        if headers:
            req_headers.update(headers)

        cert_files = self._get_cert_files()

        start_time = time.time()
        response = None
        duration = 0.0

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=req_headers,
                cert=cert_files,
                timeout=self.timeout,
            )
            duration = round(time.time() - start_time, 3)

            # Callback de auditoria/log se configurado
            if self.log_callback:
                try:
                    req_payload = (
                        json.dumps(json_data)
                        if json_data
                        else (str(data) if data else "")
                    )
                    self.log_callback(
                        url=url,
                        method=method.upper(),
                        status_code=response.status_code,
                        request_payload=req_payload,
                        response_payload=response.text,
                        duration=duration,
                    )
                except Exception as log_err:
                    _logger.warning(
                        "Falha ao executar log_callback e-Frotas: %s", log_err
                    )

            if response.status_code == 401 or response.status_code == 403:
                raise EfrotasAuthError(
                    f"Erro de autenticação e-Frotas ({response.status_code}): {response.text}",
                    status_code=response.status_code,
                    response_data=self._safe_json(response),
                )

            if response.status_code == 404:
                raise EfrotasNotFoundError(
                    f"Recurso não encontrado ({response.status_code}): {response.text}",
                    status_code=response.status_code,
                    response_data=self._safe_json(response),
                )

            if response.status_code in (400, 422):
                msg = self._extract_error_message(response)
                raise EfrotasValidationError(
                    f"Erro de validação e-Frotas ({response.status_code}): {msg}",
                    status_code=response.status_code,
                    response_data=self._safe_json(response),
                )

            response.raise_for_status()

            if (
                response.text
                and "application/json"
                in response.headers.get("Content-Type", "")
            ):
                return response.json()
            elif response.text:
                try:
                    return response.json()
                except Exception:
                    return response.text
            return {}

        except requests.RequestException as req_ex:
            duration = round(time.time() - start_time, 3)
            if self.log_callback:
                try:
                    self.log_callback(
                        url=url,
                        method=method.upper(),
                        status_code=getattr(response, "status_code", 0) or 0,
                        request_payload=json.dumps(json_data)
                        if json_data
                        else "",
                        response_payload=str(req_ex),
                        duration=duration,
                    )
                except Exception:
                    pass

            if isinstance(
                req_ex,
                (
                    EfrotasAuthError,
                    EfrotasNotFoundError,
                    EfrotasValidationError,
                ),
            ):
                raise
            raise EfrotasException(
                f"Erro de comunicação com e-Frotas: {req_ex}"
            ) from req_ex

    def _safe_json(self, response):
        try:
            return response.json()
        except Exception:
            return None

    def _extract_error_message(self, response):
        try:
            data = response.json()
            if isinstance(data, dict):
                return (
                    data.get("mensagem")
                    or data.get("mensagemTecnica")
                    or data.get("message")
                    or data.get("error")
                    or str(data)
                )
            return str(data)
        except Exception:
            return response.text

    # =========================================================================
    # 1. CRLVe API (Documento Digital CRLV-e)
    # =========================================================================

    def get_crlv(self, placa):
        """Consulta unitariamente o CRLV-e de um veículo por placa.

        :param placa: Placa do veículo (ex: 'SAV0741')
        :return: dict contendo pdfBase64, qrCode, anoLicenciamento, etc.
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request("crlv", f"/v1/documento/placa/{clean_placa}")

    # =========================================================================
    # 2. Consultas API
    # =========================================================================

    def get_veiculos(self, cnpj_filial=None, pagina=1, quantidade=20):
        """Consulta lista de veículos de um CNPJ (matriz ou filial).

        :param cnpj_filial: CNPJ da filial (opcional)
        :param pagina: Número da página (padrão 1)
        :param quantidade: Quantidade por página (padrão 20)
        """
        params = {"pagina": pagina, "quantidade": quantidade}
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial.replace(".", "").replace(
                "/", ""
            ).replace("-", "").strip()
        return self._request("consultas", "/v1/veiculos", params=params)

    def get_veiculo_por_placa(self, placa):
        """Consulta de dados cadastrais completos de um veículo por placa.

        :param placa: Placa do veículo
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request(
            "consultas", f"/v1/veiculos/placa/{clean_placa}"
        )

    def check_veiculo_associado(self, placa):
        """Verifica se um veículo está associado à frota do CNPJ.

        :param placa: Placa do veículo
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request(
            "consultas", f"/v1/veiculos/placa/{clean_placa}/associado"
        )

    def get_ocorrencias_roubo_furto(self, placa):
        """Consulta histórico de ocorrência de roubo e furto por placa.

        :param placa: Placa do veículo
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request(
            "consultas",
            f"/v1/veiculos/placa/{clean_placa}/ocorrencias-roubo-furto",
        )

    def get_recall(self, placa):
        """Consulta registros de recall pendente por placa.

        :param placa: Placa do veículo
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request(
            "consultas", f"/v1/veiculos/placa/{clean_placa}/recall"
        )

    def get_restricoes_renajud(
        self, placa, pagina=1, quantidade=50, tipo_restricao=None
    ):
        """Consulta restrições judiciais ativas (RENAJUD) por placa.

        :param placa: Placa do veículo
        :param pagina: Página
        :param quantidade: Itens por página
        :param tipo_restricao: Filtro por tipo de restrição (opcional)
        """
        clean_placa = placa.replace("-", "").strip().upper()
        params = {"pagina": pagina, "quantidade": quantidade}
        if tipo_restricao:
            params["tipoRestricao"] = tipo_restricao
        return self._request(
            "consultas",
            f"/v1/veiculos/placa/{clean_placa}/restricoes-renajud",
            params=params,
        )

    def get_infracoes_veiculo(self, placa, data_inicial, data_final):
        """Consulta infrações não pagas de um veículo em um período.

        :param placa: Placa do veículo
        :param data_inicial: Data início formato 'YYYY-MM-DD'
        :param data_final: Data fim formato 'YYYY-MM-DD' (limite de 1 ano)
        """
        clean_placa = placa.replace("-", "").strip().upper()
        params = {"dataInicial": data_inicial, "dataFinal": data_final}
        return self._request(
            "consultas",
            f"/v1/infracoes/placa/{clean_placa}",
            params=params,
        )

    def get_detalhes_infracao(
        self, codigo_orgao, numero_ait, codigo_infracao
    ):
        """Consulta detalhada de uma infração a partir da sua chave composta.

        :param codigo_orgao: Código do órgão autuador
        :param numero_ait: Número do Auto de Infração de Trânsito
        :param codigo_infracao: Código da infração
        """
        return self._request(
            "consultas",
            f"/v1/infracoes/codigoOrgao/{codigo_orgao}/numeroAit/{numero_ait}/codigoInfracao/{codigo_infracao}",
        )

    def get_pdf_notificacao_autuacao(
        self, placa, codigo_orgao, numero_ait, codigo_infracao
    ):
        """Consulta o PDF da Notificação de Autuação (NA) no SNE.

        :return: dict contendo base64 do PDF da Notificação de Autuação
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request(
            "consultas",
            f"/sne/pdf/placa/{clean_placa}/codigoOrgao/{codigo_orgao}/numeroAit/{numero_ait}/codigoInfracao/{codigo_infracao}/NA",
        )

    def get_pdf_notificacao_penalidade(
        self, placa, codigo_orgao, numero_ait, codigo_infracao
    ):
        """Consulta o PDF da Notificação de Penalidade (NP) no SNE.

        :return: dict contendo base64 do PDF da Notificação de Penalidade
        """
        clean_placa = placa.replace("-", "").strip().upper()
        return self._request(
            "consultas",
            f"/sne/pdf/placa/{clean_placa}/codigoOrgao/{codigo_orgao}/numeroAit/{numero_ait}/codigoInfracao/{codigo_infracao}/NP",
        )

    # =========================================================================
    # 3. Gerenciamento / Autorizador API (Webhooks / Endpoints de Eventos)
    # =========================================================================

    def get_endpoints(self):
        """Consulta a lista de endpoints (webhooks) cadastrados."""
        return self._request("autorizador", "/v1/endpoint")

    def create_endpoint(self, endpoint_payload):
        """Cadastra um novo endpoint (webhook) para recebimento de eventos.

        :param endpoint_payload: dict com dados do endpoint (URL, headers, eventos, etc.)
        """
        return self._request(
            "autorizador",
            "/v1/endpoint",
            method="PUT",
            json_data=endpoint_payload,
        )

    def delete_endpoint(self, endpoint_id):
        """Exclui um endpoint de webhook cadastrado pelo ID."""
        return self._request(
            "autorizador", f"/v1/endpoint/{endpoint_id}", method="DELETE"
        )

    def get_eventos(self, todos=False):
        """Consulta eventos configurados (todos ou apenas ativos).

        :param todos: bool indicando se deve retornar todos ou apenas ativos
        """
        return self._request(
            "autorizador",
            "/v1/eventos",
            params={"todos": "true" if todos else "false"},
        )

    def save_eventos(self, eventos_payload):
        """Salva a configuração de eventos autorizados."""
        return self._request(
            "autorizador",
            "/v1/eventos",
            method="PUT",
            json_data=eventos_payload,
        )

    # =========================================================================
    # 4. Notificações / Eventos API
    # =========================================================================

    def get_notificacoes(
        self,
        data_inicio,
        data_fim,
        lido=None,
        pagina=None,
        quantidade=None,
    ):
        """Consulta notificações de eventos recebidos pela frota por período.

        :param data_inicio: Data de início (formato ddMMyyyy ou YYYY-MM-DD)
        :param data_fim: Data de término
        :param lido: Filtro por lido (True/False/None)
        :param pagina: Página
        :param quantidade: Quantidade
        """
        params = {}
        if lido is not None:
            params["lido"] = "true" if lido else "false"
        if pagina is not None:
            params["pagina"] = pagina
        if quantidade is not None:
            params["quantidade"] = quantidade
        return self._request(
            "notificacoes",
            f"/v1/dataInicio/{data_inicio}/dataFim/{data_fim}",
            params=params,
        )

    def mark_notificacao_lida(self, payload):
        """Marca uma notificação como lida."""
        return self._request(
            "notificacoes",
            "/v1/lido",
            method="POST",
            json_data=payload,
        )

    def mark_notificacao_rastreamento_lida(self, payload):
        """Marca o rastreamento de uma notificação como lido."""
        return self._request(
            "notificacoes",
            "/v1/lido/rastreamento",
            method="POST",
            json_data=payload,
        )

    # =========================================================================
    # 5. Transacional API
    # =========================================================================

    def inserir_indicacao_real_infrator(self, payload):
        """Realiza a indicação do Real Infrator para uma infração de trânsito."""
        return self._request(
            "transacional",
            "/v1/realinfrator/indicacoes/inserir",
            method="POST",
            json_data=payload,
        )

    def cancelar_indicacao_real_infrator(self, chave_indicacao):
        """Cancela uma indicação pendente de Real Infrator."""
        return self._request(
            "transacional",
            f"/v1/realinfrator/indicacoes/{chave_indicacao}/cancelar",
            method="POST",
        )

    def get_status_indicacao_real_infrator(
        self, chave_indicacao, cnpj_filial=None
    ):
        """Consulta o status de uma indicação de real infrator pela chave."""
        params = {}
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial
        return self._request(
            "transacional",
            f"/v1/realinfrator/indicacoes/{chave_indicacao}/status",
            params=params,
        )

    def get_documento_assinado_real_infrator(
        self,
        chave_indicacao,
        codigo_orgao,
        numero_ait,
        codigo_infracao,
        cnpj_filial=None,
    ):
        """Consulta o documento assinado eletronicamente com o aceite do real infrator."""
        params = {}
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial
        return self._request(
            "transacional",
            f"/v1/realinfrator/indicacoes/{chave_indicacao}/{codigo_orgao}/{numero_ait}/{codigo_infracao}/documentoAssinado",
            params=params,
        )

    def get_historico_indicacao_real_infrator(
        self, codigo_orgao, numero_ait, codigo_infracao
    ):
        """Consulta o histórico de indicações de real infrator de uma infração."""
        return self._request(
            "transacional",
            f"/v1/realinfrator/indicacoes/historico/{codigo_orgao}/{numero_ait}/{codigo_infracao}",
        )

    def inserir_indicacao_principal_condutor(self, payload):
        """Realiza indicação de Principal Condutor para um veículo."""
        return self._request(
            "transacional",
            "/v1/principalcondutor/indicacoes/inserir",
            method="POST",
            json_data=payload,
        )

    def excluir_indicacao_principal_condutor(self, payload):
        """Exclui a indicação de Principal Condutor."""
        return self._request(
            "transacional",
            "/v1/principalcondutor/indicacoes/excluir",
            method="POST",
            json_data=payload,
        )

    def get_status_indicacao_principal_condutor(self, chave_indicacao):
        """Consulta o status de uma indicação de principal condutor."""
        params = {"chaveIndicacao": chave_indicacao}
        return self._request(
            "transacional",
            "/v1/principalcondutor/indicacoes/status",
            params=params,
        )

    def get_historico_indicacao_principal_condutor(
        self,
        placa,
        identificacao_possuidor,
        data_inicio,
        data_fim,
        cpf_principal_condutor=None,
        omitir_excluidas=True,
    ):
        """Consulta indicações de principal condutor efetivadas no Renavam no período."""
        params = {
            "placa": placa.replace("-", "").strip().upper(),
            "identificacaoPossuidor": identificacao_possuidor,
            "dataInicio": data_inicio,
            "dataFim": data_fim,
            "omitirExcluidas": "true" if omitir_excluidas else "false",
        }
        if cpf_principal_condutor:
            params["cpfPrincipalCondutor"] = cpf_principal_condutor
        return self._request(
            "transacional",
            "/v1/principalcondutor/indicacoes/historico",
            params=params,
        )

    def solicitar_boleto(
        self, placa, chave_infracao, desconto40=False, cnpj_filial=None
    ):
        """Solicita boleto bancário para pagamento de infração com ou sem desconto SNE (40%)."""
        params = {
            "placa": placa.replace("-", "").strip().upper(),
            "chaveInfracao": chave_infracao,
            "desconto40": "true" if desconto40 else "false",
        }
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial
        return self._request(
            "transacional",
            "/v1/boleto/solicitarBoleto",
            method="POST",
            params=params,
        )

    def reconhecer_infracao(self, placa, chave_infracao, cnpj_filial=None):
        """Reconhece o cometimento de uma infração de trânsito no SNE."""
        params = {
            "placa": placa.replace("-", "").strip().upper(),
            "chaveInfracao": chave_infracao,
        }
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial
        return self._request(
            "transacional",
            "/v1/boleto/reconhecerInfracao",
            method="POST",
            params=params,
        )

    def get_pdf_boleto(self, placa, chave_infracao, cnpj_filial=None):
        """Consulta o PDF do boleto gerado para pagamento da infração."""
        params = {
            "placa": placa.replace("-", "").strip().upper(),
            "chaveInfracao": chave_infracao,
        }
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial
        return self._request(
            "transacional",
            "/v1/boleto/consultarPdfBoleto",
            params=params,
        )

    def get_dados_pagamento(self, placa, chave_infracao, cnpj_filial=None):
        """Consulta dados para pagamento (linha digitável, código de barras, valor, etc.)."""
        params = {
            "placa": placa.replace("-", "").strip().upper(),
            "chaveInfracao": chave_infracao,
        }
        if cnpj_filial:
            params["cnpjFilial"] = cnpj_filial
        return self._request(
            "transacional",
            "/v1/boleto/consultarDadosPagamento",
            params=params,
        )
