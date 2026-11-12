"""Testes da leitura e do comando executado pelo usuário."""

import subprocess
import sys
from pathlib import Path

import pytest

from salesflow.cli import carregar_vendas

RAIZ = Path(__file__).resolve().parents[1]
EXEMPLO = RAIZ / "data" / "exemplo_vendas.csv"


def executar(*argumentos: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "salesflow", *argumentos],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_csv_de_exemplo_tem_as_colunas_e_linhas_esperadas():
    dados = carregar_vendas(EXEMPLO)

    assert dados.columns.tolist() == [
        "id_pedido",
        "id_item",
        "data",
        "produto",
        "categoria",
        "quantidade",
        "preco_unitario",
    ]
    assert len(dados) == 4
    assert dados["id_pedido"].tolist() == ["1001", "1001", "1002", "1003"]
    assert dados["id_item"].tolist() == ["1", "2", "1", "1"]


def test_leitura_preserva_identificadores_como_texto(tmp_path):
    arquivo = tmp_path / "identificadores.csv"
    arquivo.write_text(
        "id_pedido,id_item,quantidade\n001001,01,2\nNA,NULL,1\n",
        encoding="utf-8",
    )

    dados = carregar_vendas(arquivo)

    assert dados["id_pedido"].tolist() == ["001001", "NA"]
    assert dados["id_item"].tolist() == ["01", "NULL"]
    assert dados["quantidade"].tolist() == [2, 1]


def test_comando_inspeciona_o_csv_de_exemplo():
    resultado = executar("inspecionar", "--arquivo", "data/exemplo_vendas.csv")

    assert resultado.returncode == 0
    assert resultado.stderr == ""
    assert (
        "Colunas: id_pedido, id_item, data, produto, categoria, "
        "quantidade, preco_unitario"
    ) in resultado.stdout
    assert "Quantidade de linhas: 4" in resultado.stdout
    assert "Prévia dos dados (até 5 linhas):" in resultado.stdout
    for produto in ("Mouse", "Teclado", "Monitor"):
        assert produto in resultado.stdout
    assert "1003" in resultado.stdout


def test_comando_limita_a_previa_e_conta_todas_as_linhas(tmp_path):
    arquivo = tmp_path / "sete_vendas.csv"
    linhas = [f"{i:04},01,Produto_{i}" for i in range(1, 8)]
    arquivo.write_text(
        "id_pedido,id_item,produto\n" + "\n".join(linhas) + "\n", encoding="utf-8"
    )

    resultado = executar("inspecionar", "--arquivo", str(arquivo))

    assert resultado.returncode == 0
    assert "Quantidade de linhas: 7" in resultado.stdout
    assert "0001" in resultado.stdout
    assert "Produto_5" in resultado.stdout
    assert "Produto_6" not in resultado.stdout
    assert "Produto_7" not in resultado.stdout


def test_comando_informa_arquivo_inexistente_sem_traceback(tmp_path):
    arquivo = tmp_path / "inexistente.csv"

    resultado = executar("inspecionar", "--arquivo", str(arquivo))

    assert resultado.returncode == 1
    assert resultado.stdout == ""
    assert "Erro: arquivo não encontrado:" in resultado.stderr
    assert str(arquivo) in resultado.stderr
    assert "Traceback" not in resultado.stderr


@pytest.mark.parametrize("argumentos", [(), ("inspecionar",)])
def test_comando_exige_subcomando_e_arquivo(argumentos):
    resultado = executar(*argumentos)

    assert resultado.returncode == 2
    assert "required" in resultado.stderr
