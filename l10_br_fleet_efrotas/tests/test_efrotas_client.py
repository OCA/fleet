# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import unittest
from unittest.mock import MagicMock, patch

from l10_br_fleet_efrotas.models.efrotas_client import (
    EfrotasAuthError,
    EfrotasClient,
    EfrotasException,
    EfrotasNotFoundError,
    EfrotasValidationError,
)


class TestEfrotasClient(unittest.TestCase):
    def setUp(self):
        self.base_url = (
            "https://hom-efrotas.np.estaleiro.serpro.gov.br/efrotas/api"
        )
        self.token = "sample_jwt_token_12345"
        self.client = EfrotasClient(base_url=self.base_url, token=self.token)

    def test_headers_and_auth(self):
        """Verifica se os cabeçalhos Authorization e x-token-client são preenchidos corretamente."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"Content-Type": "application/json"}
            mock_resp.json.return_value = {"placa": "SAV0741"}
            mock_req.return_value = mock_resp

            res = self.client.get_veiculo_por_placa("SAV0741")
            self.assertEqual(res["placa"], "SAV0741")

            mock_req.assert_called_once()
            args, kwargs = mock_req.call_args
            headers = kwargs["headers"]
            self.assertEqual(headers["Authorization"], "Bearer sample_jwt_token_12345")
            self.assertEqual(headers["x-token-client"], "sample_jwt_token_12345")

    def test_get_crlv(self):
        """Testa a obtenção do CRLV-e digital."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"Content-Type": "application/json"}
            mock_resp.json.return_value = {
                "pdfBase64": "JVBERi0xLjUK...",
                "anoLicenciamento": 2024,
            }
            mock_req.return_value = mock_resp

            res = self.client.get_crlv("SAV-0741")
            self.assertIn("pdfBase64", res)
            self.assertEqual(res["anoLicenciamento"], 2024)

            expected_url = f"{self.base_url}/crlv/v1/documento/placa/SAV0741"
            self.assertEqual(mock_req.call_args[1]["url"], expected_url)

    def test_consultas_endpoints(self):
        """Testa chamadas aos endpoints de consultas (veículo, roubo, recall, renajud, infrações)."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"Content-Type": "application/json"}
            mock_resp.json.return_value = {"status": "ok"}
            mock_req.return_value = mock_resp

            # Veículos da frota
            self.client.get_veiculos(cnpj_filial="33.683.111/0001-07")
            self.assertEqual(
                mock_req.call_args[1]["url"], f"{self.base_url}/consultas/v1/veiculos"
            )
            self.assertEqual(
                mock_req.call_args[1]["params"]["cnpjFilial"], "33683111000107"
            )

            # Roubo e furto
            self.client.get_ocorrencias_roubo_furto("SAV0741")
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/consultas/v1/veiculos/placa/SAV0741/ocorrencias-roubo-furto",
            )

            # Recall
            self.client.get_recall("SAV0741")
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/consultas/v1/veiculos/placa/SAV0741/recall",
            )

            # RENAJUD
            self.client.get_restricoes_renajud(
                "SAV0741", tipo_restricao="TRANSFERENCIA"
            )
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/consultas/v1/veiculos/placa/SAV0741/restricoes-renajud",
            )
            self.assertEqual(
                mock_req.call_args[1]["params"]["tipoRestricao"], "TRANSFERENCIA"
            )

            # Infrações por período
            self.client.get_infracoes_veiculo(
                "SAV0741", "2024-01-01", "2024-06-01"
            )
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/consultas/v1/infracoes/placa/SAV0741",
            )

            # Detalhes de infração
            self.client.get_detalhes_infracao("200010", "AIT123", "50020")
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/consultas/v1/infracoes/codigoOrgao/200010/numeroAit/AIT123/codigoInfracao/50020",
            )

            # PDFs SNE
            self.client.get_pdf_notificacao_autuacao(
                "SAV0741", "200010", "AIT123", "50020"
            )
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/consultas/sne/pdf/placa/SAV0741/codigoOrgao/200010/numeroAit/AIT123/codigoInfracao/50020/NA",
            )

    def test_autorizador_and_notificacoes(self):
        """Testa endpoints de gerenciamento de webhook/eventos e notificações."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"Content-Type": "application/json"}
            mock_resp.json.return_value = [{"id": 1, "url": "https://meusite.com/hook"}]
            mock_req.return_value = mock_resp

            self.client.get_endpoints()
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/autorizador/v1/endpoint",
            )

            self.client.get_notificacoes("01012024", "01062024", lido=False)
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/notificacoes/v1/dataInicio/01012024/dataFim/01062024",
            )
            self.assertEqual(mock_req.call_args[1]["params"]["lido"], "false")

    def test_transacional(self):
        """Testa endpoints transacionais (boleto, condutor, real infrator)."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"Content-Type": "application/json"}
            mock_resp.json.return_value = {"chaveBoleto": "BOL123"}
            mock_req.return_value = mock_resp

            # Solicitar boleto com desconto
            self.client.solicitar_boleto("SAV0741", "INF_KEY_123", desconto40=True)
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/transacional/v1/boleto/solicitarBoleto",
            )
            self.assertEqual(
                mock_req.call_args[1]["params"]["desconto40"], "true"
            )

            # Reconhecer infração
            self.client.reconhecer_infracao("SAV0741", "INF_KEY_123")
            self.assertEqual(
                mock_req.call_args[1]["url"],
                f"{self.base_url}/transacional/v1/boleto/reconhecerInfracao",
            )

    def test_error_handling_401(self):
        """Valida que status 401 dispara EfrotasAuthError."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_resp.text = "Unauthorized token"
            mock_resp.json.side_effect = ValueError()
            mock_req.return_value = mock_resp

            with self.assertRaises(EfrotasAuthError):
                self.client.get_veiculo_por_placa("SAV0741")

    def test_error_handling_404(self):
        """Valida que status 404 dispara EfrotasNotFoundError."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_resp.text = "Not Found"
            mock_resp.json.side_effect = ValueError()
            mock_req.return_value = mock_resp

            with self.assertRaises(EfrotasNotFoundError):
                self.client.get_veiculo_por_placa("INEXISTENTE")

    def test_error_handling_400(self):
        """Valida que status 400 dispara EfrotasValidationError com mensagem descritiva."""
        with patch("requests.request") as mock_req:
            mock_resp = MagicMock()
            mock_resp.status_code = 400
            mock_resp.headers = {"Content-Type": "application/json"}
            mock_resp.json.return_value = {
                "mensagem": "Placa informada é inválida"
            }
            mock_resp.text = '{"mensagem": "Placa informada é inválida"}'
            mock_req.return_value = mock_resp

            with self.assertRaises(EfrotasValidationError) as ctx:
                self.client.get_veiculo_por_placa("1234")
            self.assertIn("Placa informada é inválida", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
