"""Interface de linha de comando para a primeira entrega do SalesFlow."""

import argparse
import sys
from pathlib import Path

import pandas as pd


def carregar_vendas(arquivo: Path) -> pd.DataFrame:
    """Lê o CSV sem converter identificadores em números ou valores ausentes."""
    return pd.read_csv(
        arquivo,
        dtype={"id_pedido": "string", "id_item": "string"},
        keep_default_na=False,
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    """Interpreta os argumentos, inspeciona o arquivo e retorna o código de saída."""
    parser = argparse.ArgumentParser(
        prog="salesflow", description="Inspecione dados de vendas em CSV."
    )
    subcomandos = parser.add_subparsers(dest="comando", required=True)
    inspecionar = subcomandos.add_parser("inspecionar", help="Mostra um resumo do CSV.")
    inspecionar.add_argument(
        "--arquivo", type=Path, required=True, help="Caminho do arquivo CSV em UTF-8."
    )
    argumentos = parser.parse_args(argv)

    try:
        dados = carregar_vendas(argumentos.arquivo)
    except FileNotFoundError:
        print(
            f"Erro: arquivo não encontrado: {argumentos.arquivo}",
            file=sys.stderr,
        )
        return 1

    print(f"Colunas: {', '.join(dados.columns)}")
    print(f"Quantidade de linhas: {len(dados)}")
    print("Prévia dos dados (até 5 linhas):")
    print(dados.head(5).to_string(index=False))
    return 0
