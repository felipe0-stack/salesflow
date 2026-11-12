"""Interface de linha de comando para inspecionar e validar vendas."""

import argparse
import sys
from pathlib import Path

import pandas as pd

from salesflow.leitura import carregar_vendas
from salesflow.relatorios import salvar_relatorios
from salesflow.validacao import validar_vendas


def main(argv: list[str] | None = None) -> int:
    """Interpreta argumentos e coordena a leitura, as regras e a saída."""
    parser = argparse.ArgumentParser(
        prog="salesflow", description="Inspecione e valide dados de vendas em CSV."
    )
    subcomandos = parser.add_subparsers(dest="comando", required=True)
    inspecionar = subcomandos.add_parser("inspecionar", help="Mostra um resumo do CSV.")
    inspecionar.add_argument(
        "--arquivo", type=Path, required=True, help="Caminho do arquivo CSV em UTF-8."
    )
    validar = subcomandos.add_parser("validar", help="Valida vendas e gera relatórios.")
    validar.add_argument(
        "--arquivo", type=Path, required=True, help="Caminho do arquivo CSV em UTF-8."
    )
    validar.add_argument(
        "--saida", type=Path, required=True, help="Pasta para os relatórios CSV e JSON."
    )
    argumentos = parser.parse_args(argv)

    try:
        dados = carregar_vendas(
            argumentos.arquivo, como_texto=argumentos.comando == "validar"
        )
    except FileNotFoundError:
        print(
            f"Erro: arquivo não encontrado: {argumentos.arquivo}",
            file=sys.stderr,
        )
        return 1
    except (
        OSError,
        UnicodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as erro:
        print(f"Erro ao ler o CSV: {erro}", file=sys.stderr)
        return 1

    if argumentos.comando == "validar":
        resultado = validar_vendas(dados)
        try:
            caminhos = salvar_relatorios(
                resultado, argumentos.arquivo, argumentos.saida
            )
        except (OSError, ValueError) as erro:
            print(f"Erro ao gerar os relatórios: {erro}", file=sys.stderr)
            return 1
        print("Validação concluída:")
        for categoria, quantidade in resultado.resumo.items():
            print(f"{categoria}: {quantidade}")
        if resultado.colunas_ausentes:
            print(f"Colunas ausentes: {', '.join(resultado.colunas_ausentes)}")
        for caminho in caminhos.values():
            print(f"Relatório: {caminho}")
        return 0

    print(f"Colunas: {', '.join(dados.columns)}")
    print(f"Quantidade de linhas: {len(dados)}")
    print("Prévia dos dados (até 5 linhas):")
    print(dados.head(5).to_string(index=False))
    return 0
