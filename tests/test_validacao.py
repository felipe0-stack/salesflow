"""Regras de qualidade e classificação exclusiva dos registros de venda."""

from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from salesflow.validacao import COLUNAS_OBRIGATORIAS, validar_vendas


def venda(**alteracoes):
    registro = {
        "id_pedido": "001001",
        "id_item": "01",
        "data": "2026-10-01",
        "produto": "Mouse",
        "categoria": "Perifericos",
        "quantidade": "2",
        "preco_unitario": "50.00",
    }
    return registro | alteracoes


def verificar_contagens(resultado, **esperadas):
    assert resultado.resumo == esperadas
    assert esperadas["lidas"] == sum(
        esperadas[categoria]
        for categoria in (
            "validas",
            "invalidas",
            "duplicadas_ignoradas",
            "conflitantes",
        )
    )
    assert len(resultado.validos) == esperadas["validas"]
    assert len(resultado.rejeitados) == esperadas["lidas"] - esperadas["validas"]


def test_quatro_registros_originais_continuam_validos():
    arquivo = Path(__file__).resolve().parents[1] / "data" / "exemplo_vendas.csv"
    dados = pd.read_csv(arquivo, dtype="string", keep_default_na=False)

    resultado = validar_vendas(dados)

    verificar_contagens(
        resultado,
        lidas=4,
        validas=4,
        invalidas=0,
        duplicadas_ignoradas=0,
        conflitantes=0,
    )
    assert resultado.validos["id_pedido"].tolist() == ["1001", "1001", "1002", "1003"]
    assert resultado.validos["id_item"].tolist() == ["1", "2", "1", "1"]
    assert resultado.validos["preco_unitario_centavos"].tolist() == [
        5000,
        10000,
        30000,
        5000,
    ]


@pytest.mark.parametrize("campo", ["id_pedido", "id_item", "produto", "categoria"])
@pytest.mark.parametrize("valor", ["", " \t ", None, pd.NA])
def test_campos_obrigatorios_nao_podem_estar_vazios(campo, valor):
    resultado = validar_vendas(pd.DataFrame([venda(**{campo: valor})]))

    assert resultado.resumo["invalidas"] == 1
    assert resultado.validos.empty
    assert campo in resultado.rejeitados.iloc[0]["motivo"]


@pytest.mark.parametrize("ausentes", [("categoria",), tuple(COLUNAS_OBRIGATORIAS)])
def test_ausencia_de_colunas_invalida_cada_registro_uma_vez(ausentes):
    dados = pd.DataFrame([venda(), venda(id_item="02")]).drop(columns=list(ausentes))

    resultado = validar_vendas(dados)

    verificar_contagens(
        resultado,
        lidas=2,
        validas=0,
        invalidas=2,
        duplicadas_ignoradas=0,
        conflitantes=0,
    )
    assert resultado.rejeitados["linha_origem"].tolist() == [2, 3]
    for coluna in ausentes:
        assert resultado.rejeitados["motivo"].str.contains(coluna).all()


@pytest.mark.parametrize(
    "data",
    [
        "2026-02-29",
        "2026-04-31",
        "2026-13-01",
        "2026-00-01",
        "2026-01-00",
        "2026-1-01",
        "01/10/2026",
        "2026-10-01T00:00:00",
        " 2026-10-01",
        "２０２６-１０-０１",
        "0000-01-01",
    ],
)
def test_data_deve_ser_real_e_ter_formato_exato(data):
    resultado = validar_vendas(pd.DataFrame([venda(data=data)]))

    assert resultado.resumo["invalidas"] == 1
    assert "data" in resultado.rejeitados.iloc[0]["motivo"]


def test_data_bissexta_valida_e_aceita():
    resultado = validar_vendas(pd.DataFrame([venda(data="2024-02-29")]))

    assert resultado.resumo["validas"] == 1


@pytest.mark.parametrize(
    "quantidade", ["0", "-1", "1.5", "1.0", "1e2", "+1", " 1", "", "dois", "٢"]
)
def test_quantidade_deve_ser_inteira_e_positiva(quantidade):
    resultado = validar_vendas(pd.DataFrame([venda(quantidade=quantidade)]))

    assert resultado.resumo["invalidas"] == 1
    assert "quantidade" in resultado.rejeitados.iloc[0]["motivo"]


@pytest.mark.parametrize(
    "preco",
    [
        "0",
        "0.00",
        "-1.00",
        "+1.00",
        "1,50",
        "1.001",
        "1e2",
        "NaN",
        "inf",
        ".50",
        "10.",
        " 1.00",
        "",
        "１.００",
    ],
)
def test_preco_invalido_nao_e_arredondado_nem_reinterpretado(preco):
    resultado = validar_vendas(pd.DataFrame([venda(preco_unitario=preco)]))

    assert resultado.resumo["invalidas"] == 1
    assert "preco_unitario" in resultado.rejeitados.iloc[0]["motivo"]


@pytest.mark.parametrize(
    ("preco", "centavos"),
    [
        ("0.01", 1),
        ("0.29", 29),
        ("1.1", 110),
        ("10", 1000),
        ("0001.05", 105),
        ("90071992547409.93", 9007199254740993),
    ],
)
def test_preco_e_convertido_exatamente_para_centavos(preco, centavos):
    resultado = validar_vendas(pd.DataFrame([venda(preco_unitario=preco)]))

    assert resultado.resumo["validas"] == 1
    assert resultado.validos.iloc[0]["preco_unitario_centavos"] == centavos
    assert isinstance(resultado.validos["preco_unitario_centavos"].tolist()[0], int)


def test_identificadores_preservam_zeros_e_textos_literais():
    dados = pd.DataFrame([venda(), venda(id_pedido="NA", id_item="NULL")])

    resultado = validar_vendas(dados)

    assert resultado.resumo["validas"] == 2
    assert resultado.validos["id_pedido"].tolist() == ["001001", "NA"]
    assert resultado.validos["id_item"].tolist() == ["01", "NULL"]


def test_repeticoes_identicas_aceitam_primeira_ocorrencia_e_ignoram_demais():
    dados = pd.DataFrame([venda(), venda(), venda()], index=[90, 90, 5])

    resultado = validar_vendas(dados)

    verificar_contagens(
        resultado,
        lidas=3,
        validas=1,
        invalidas=0,
        duplicadas_ignoradas=2,
        conflitantes=0,
    )
    assert resultado.rejeitados["linha_origem"].tolist() == [3, 4]
    assert resultado.rejeitados["classificacao"].tolist() == [
        "duplicada_ignorada",
        "duplicada_ignorada",
    ]
    assert resultado.rejeitados["motivo"].str.len().gt(0).all()


def test_representacoes_numericas_equivalentes_sao_duplicadas():
    dados = pd.DataFrame(
        [
            venda(quantidade="1", preco_unitario="10"),
            venda(quantidade="01", preco_unitario="10.0"),
            venda(quantidade="1", preco_unitario="10.00"),
        ]
    )

    resultado = validar_vendas(dados)

    assert resultado.resumo["validas"] == 1
    assert resultado.resumo["duplicadas_ignoradas"] == 2
    assert resultado.resumo["conflitantes"] == 0


def test_conflito_rejeita_todos_os_validos_da_chave_mas_nao_reclassifica_invalidos():
    dados = pd.DataFrame(
        [
            venda(),
            venda(),
            venda(produto="Teclado"),
            venda(preco_unitario="50.001"),
            venda(id_item="02"),
            venda(id_pedido="001002"),
        ]
    )

    resultado = validar_vendas(dados)

    verificar_contagens(
        resultado,
        lidas=6,
        validas=2,
        invalidas=1,
        duplicadas_ignoradas=0,
        conflitantes=3,
    )
    assert resultado.rejeitados["linha_origem"].tolist() == [2, 3, 4, 5]
    assert resultado.rejeitados["classificacao"].tolist() == [
        "conflitante",
        "conflitante",
        "conflitante",
        "invalida",
    ]


def test_invalido_nao_causa_conflito_com_registro_valido_da_mesma_chave():
    dados = pd.DataFrame([venda(quantidade="0"), venda()])

    resultado = validar_vendas(dados)

    verificar_contagens(
        resultado,
        lidas=2,
        validas=1,
        invalidas=1,
        duplicadas_ignoradas=0,
        conflitantes=0,
    )


def test_registro_com_varios_problemas_conta_uma_vez_e_preserva_os_motivos():
    registro = venda(produto="", data="2026-02-30", quantidade="0", preco_unitario="-1")

    resultado = validar_vendas(pd.DataFrame([registro]))

    verificar_contagens(
        resultado,
        lidas=1,
        validas=0,
        invalidas=1,
        duplicadas_ignoradas=0,
        conflitantes=0,
    )
    rejeitado = resultado.rejeitados.iloc[0]
    for campo in ("produto", "data", "quantidade", "preco_unitario"):
        assert campo in rejeitado["motivo"]
        assert rejeitado[campo] == registro[campo]


def test_somente_cabecalho_produz_contagens_zeradas_e_relatorios_com_colunas():
    resultado = validar_vendas(pd.DataFrame(columns=COLUNAS_OBRIGATORIAS))

    verificar_contagens(
        resultado,
        lidas=0,
        validas=0,
        invalidas=0,
        duplicadas_ignoradas=0,
        conflitantes=0,
    )
    assert set(COLUNAS_OBRIGATORIAS).issubset(resultado.validos.columns)
    assert {"linha_origem", "classificacao", "motivo"}.issubset(
        resultado.rejeitados.columns
    )


def test_validacao_nao_modifica_o_dataframe_recebido():
    dados = pd.DataFrame([venda(), venda(quantidade="0")])
    original = dados.copy(deep=True)

    validar_vendas(dados)

    assert_frame_equal(dados, original)
