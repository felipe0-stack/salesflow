"""Leitura compartilhada pelos comandos de inspeção e validação."""

import warnings
from pathlib import Path

import pandas as pd


def carregar_vendas(arquivo: Path, *, como_texto: bool = False) -> pd.DataFrame:
    """Lê o CSV, opcionalmente preservando a escrita original de todos os campos."""
    with warnings.catch_warnings():
        if como_texto:
            # Impede descartar campos excedentes ou inferir um índice com o ID.
            warnings.simplefilter("error", pd.errors.ParserWarning)
        try:
            return pd.read_csv(
                arquivo,
                dtype=(
                    "string"
                    if como_texto
                    else {"id_pedido": "string", "id_item": "string"}
                ),
                index_col=False if como_texto else None,
                keep_default_na=False,
                encoding="utf-8",
            )
        except pd.errors.ParserWarning as erro:
            raise pd.errors.ParserError(
                "Quantidade de campos incompatível com o cabeçalho do CSV"
            ) from erro
