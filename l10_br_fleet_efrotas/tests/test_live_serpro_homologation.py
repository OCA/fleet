#!/usr/bin/env python3
# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Script de teste de integração direto com o ambiente de homologação do SERPRO.

Pode ser executado diretamente com:
    python3 test_live_serpro_homologation.py
"""

import sys
from l10_br_fleet_efrotas.models.efrotas_client import (
    EfrotasClient,
    EfrotasException,
)

HOMOLOGATION_TOKEN = (
    "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDAxMDY4MDAsImlzcyI6Imh0dHBzOi8vZWZyb3Rh"
    "cy5zZXJwcm8uZ292LmJyL2lzc3VlciIsImNucGoiOiIzMzY4MzExMTAwMDEwNyJ9.GnYpQDIZ"
    "Qtprkqp3pv1BEUvf3mHAzpIATlgeCoJbuw4"
)
TEST_PLATE = "SAV0741"


def run_live_tests():
    print("=== TESTE DE CONEXÃO COM HOMOLOGAÇÃO e-FROTAS SERPRO ===")
    client = EfrotasClient(
        base_url="https://hom-efrotas.np.estaleiro.serpro.gov.br/efrotas/api",
        token=HOMOLOGATION_TOKEN,
        timeout=15,
    )

    success_count = 0
    total_count = 0

    # 1. Consulta Veículo
    total_count += 1
    try:
        print(f"\n1. Consultando veículo por placa ({TEST_PLATE})...")
        v_data = client.get_veiculo_por_placa(TEST_PLATE)
        print("   -> SUCESSO! Dados recebidos:")
        print(f"      Placa: {v_data.get('placa')}")
        print(f"      Renavam: {v_data.get('renavam')}")
        print(f"      Marca/Modelo: {v_data.get('descricaoMarcaModelo')}")
        print(f"      Chassi: {v_data.get('chassi')}")
        print(f"      Município: {v_data.get('descricaoMunicipioEmplacamento')}")
        success_count += 1
    except EfrotasException as ex:
        print(f"   -> FALHA: {ex}")

    # 2. Consulta Associação
    total_count += 1
    try:
        print(f"\n2. Verificando se veículo está associado ({TEST_PLATE})...")
        assoc_data = client.check_veiculo_associado(TEST_PLATE)
        print(f"   -> SUCESSO! Mensagem: {assoc_data.get('mensagem')}")
        success_count += 1
    except EfrotasException as ex:
        print(f"   -> FALHA: {ex}")

    # 3. Consulta CRLV-e Digital
    total_count += 1
    try:
        print(f"\n3. Baixando CRLV-e digital ({TEST_PLATE})...")
        crlv_data = client.get_crlv(TEST_PLATE)
        pdf_len = len(crlv_data.get("pdfBase64", ""))
        print(f"   -> SUCESSO! PDF Base64 recebido ({pdf_len} caracteres).")
        success_count += 1
    except EfrotasException as ex:
        print(f"   -> FALHA: {ex}")

    # 4. Lista de Veículos do CNPJ
    total_count += 1
    try:
        print("\n4. Consultando lista de veículos do CNPJ...")
        frota = client.get_veiculos(quantidade=5)
        print(
            f"   -> SUCESSO! {len(frota)} veículos retornados na primeira página."
        )
        for v in frota[:3]:
            print(
                f"      - Placa: {v.get('placa')} | Modelo: {v.get('descricaoMarcaModelo')}"
            )
        success_count += 1
    except EfrotasException as ex:
        print(f"   -> FALHA: {ex}")

    print("\n" + "=" * 55)
    print(
        f"RESULTADO: {success_count}/{total_count} testes passaram com sucesso!"
    )
    print("=" * 55)
    return success_count == total_count


if __name__ == "__main__":
    success = run_live_tests()
    sys.exit(0 if success else 1)
