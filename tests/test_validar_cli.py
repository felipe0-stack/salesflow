"""Integração entre leitura original, regras, terminal e relatórios persistidos."""

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from salesflow.leitura import carregar_vendas

RAIZ = Path(__file__).resolve().parents[1]
CABECALHO = "id_pedido,id_item,data,produto,categoria,quantidade,preco_unitario\n"


def executar(*argumentos):
    return subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "salesflow",
            "validar",
            *map(str, argumentos),
        ],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def ler_resumo(saida):
    return json.loads((saida / "resumo.json").read_text(encoding="utf-8"))


def test_exemplo_controlado_gera_tres_relatorios_auditaveis(tmp_path):
    arquivo = RAIZ / "data" / "exemplo_com_erros.csv"
    saida = tmp_path / "nova" / "relatorios"

    processo = executar("--arquivo", arquivo, "--saida", saida)

    assert processo.returncode == 0, processo.stderr
    assert processo.stderr == ""
    assert "Validação concluída" in processo.stdout
    assert {p.name for p in saida.iterdir()} == {
        "validos.csv",
        "rejeitados.csv",
        "resumo.json",
    }
    resumo = ler_resumo(saida)
    assert {
        c: resumo[c]
        for c in (
            "lidas",
            "validas",
            "invalidas",
            "duplicadas_ignoradas",
            "conflitantes",
        )
    } == dict(lidas=11, validas=3, invalidas=5, duplicadas_ignoradas=1, conflitantes=2)
    assert resumo["arquivo_origem"] == str(arquivo)
    assert resumo["colunas_ausentes"] == []

    validos = carregar_vendas(saida / "validos.csv", como_texto=True)
    assert validos["id_item"].tolist() == ["01", "02", "01"]
    assert validos["preco_unitario_centavos"].tolist() == ["5000", "10000", "29"]
    rejeitados = pd.read_csv(
        saida / "rejeitados.csv", dtype="string", keep_default_na=False
    )
    assert len(rejeitados) == 8
    assert rejeitados["arquivo_origem"].eq(str(arquivo)).all()
    assert rejeitados["linha_origem"].tolist() == [str(n) for n in range(4, 12)]
    assert rejeitados["motivo"].str.len().gt(0).all()
    assert rejeitados["classificacao"].value_counts().to_dict() == {
        "invalida": 5,
        "conflitante": 2,
        "duplicada_ignorada": 1,
    }
    assert "10.999" in rejeitados["preco_unitario"].tolist()


def test_original_gera_quatro_validos_e_rejeitados_so_com_cabecalho(tmp_path):
    processo = executar(
        "--arquivo", RAIZ / "data" / "exemplo_vendas.csv", "--saida", tmp_path
    )

    assert processo.returncode == 0, processo.stderr
    resumo = ler_resumo(tmp_path)
    assert resumo["lidas"] == resumo["validas"] == 4
    assert (
        resumo["invalidas"]
        == resumo["duplicadas_ignoradas"]
        == resumo["conflitantes"]
        == 0
    )
    assert pd.read_csv(tmp_path / "rejeitados.csv").empty


def test_leitura_para_validar_preserva_formato_e_precisao_do_csv(tmp_path):
    arquivo = tmp_path / "entrada.csv"
    arquivo.write_text(
        CABECALHO
        + "0001,01,2026-10-01,Mouse,Perifericos,1,900719925474099300000.93\n"
        + "0002,01,2026-10-01,Mouse,Perifericos,1,1.000\n"
        + "0003,01,2026-10-01,Mouse,Perifericos,1,1e2\n",
        encoding="utf-8",
    )

    processo = executar("--arquivo", arquivo, "--saida", tmp_path / "saida")

    assert processo.returncode == 0, processo.stderr
    saida = tmp_path / "saida"
    assert ler_resumo(saida)["invalidas"] == 2
    dados = carregar_vendas(saida / "validos.csv", como_texto=True)
    assert dados.iloc[0]["id_pedido"] == "0001"
    assert dados.iloc[0]["preco_unitario_centavos"] == "90071992547409930000093"


@pytest.mark.parametrize("tem_registro", [False, True])
def test_colunas_ausentes_constam_no_json_e_invalidam_linhas(tmp_path, tem_registro):
    arquivo = tmp_path / "sem_colunas.csv"
    arquivo.write_text(
        "id_pedido,id_item\n" + ("0001,01\n" if tem_registro else ""), encoding="utf-8"
    )

    processo = executar("--arquivo", arquivo, "--saida", tmp_path / "saida")

    assert processo.returncode == 0, processo.stderr
    resumo = ler_resumo(tmp_path / "saida")
    assert resumo["lidas"] == resumo["invalidas"] == int(tem_registro)
    assert resumo["validas"] == 0
    assert resumo["colunas_ausentes"] == [
        "data",
        "produto",
        "categoria",
        "quantidade",
        "preco_unitario",
    ]


def test_csv_so_com_cabecalho_gera_relatorios_vazios(tmp_path):
    arquivo = tmp_path / "cabecalho.csv"
    arquivo.write_text(CABECALHO, encoding="utf-8")

    processo = executar("--arquivo", arquivo, "--saida", tmp_path / "saida")

    assert processo.returncode == 0, processo.stderr
    assert ler_resumo(tmp_path / "saida")["lidas"] == 0
    assert pd.read_csv(tmp_path / "saida" / "validos.csv").empty
    assert pd.read_csv(tmp_path / "saida" / "rejeitados.csv").empty


@pytest.mark.parametrize(
    "conteudo",
    [
        "",
        CABECALHO + '"aspas sem fechar',
        CABECALHO + "EXTRA,001,01,2026-10-01,Mouse,Perifericos,1,10.00\n",
        CABECALHO
        + "001,01,2026-10-01,Mouse,Perifericos,1,10.00\n"
        + "EXTRA,002,01,2026-10-01,Mouse,Perifericos,1,10.00\n",
    ],
)
def test_erro_de_leitura_nao_gera_relatorios_nem_traceback(tmp_path, conteudo):
    arquivo = tmp_path / "entrada.csv"
    arquivo.write_text(conteudo, encoding="utf-8")
    saida = tmp_path / "saida"

    processo = executar("--arquivo", arquivo, "--saida", saida)

    assert processo.returncode == 1
    assert "Erro ao ler o CSV:" in processo.stderr
    assert "Traceback" not in processo.stderr
    assert not saida.exists()


def test_pasta_de_saida_nao_pode_ser_um_arquivo(tmp_path):
    saida = tmp_path / "saida"
    saida.write_text("preservar", encoding="utf-8")

    processo = executar(
        "--arquivo", RAIZ / "data" / "exemplo_vendas.csv", "--saida", saida
    )

    assert processo.returncode == 1
    assert "Erro ao gerar os relatórios:" in processo.stderr
    assert "Traceback" not in processo.stderr
    assert saida.read_text(encoding="utf-8") == "preservar"


def test_relatorios_nao_podem_sobrescrever_o_arquivo_de_entrada(tmp_path):
    arquivo = tmp_path / "validos.csv"
    original = CABECALHO + "0001,01,2026-10-01,Mouse,Perifericos,1,0.29\n"
    arquivo.write_text(original, encoding="utf-8")

    processo = executar("--arquivo", arquivo, "--saida", tmp_path)

    assert processo.returncode == 1
    assert "não pode sobrescrever" in processo.stderr
    assert arquivo.read_text(encoding="utf-8") == original


def test_arquivo_inexistente_e_opcoes_obrigatorias(tmp_path):
    processo = executar("--arquivo", tmp_path / "ausente.csv", "--saida", tmp_path)
    assert processo.returncode == 1
    assert "arquivo não encontrado" in processo.stderr
    processo = executar("--arquivo", RAIZ / "data" / "exemplo_vendas.csv")
    assert processo.returncode == 2
    assert "--saida" in processo.stderr
