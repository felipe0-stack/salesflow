"""Gravação dos resultados da validação em CSV e JSON."""

import json
from pathlib import Path

from salesflow.validacao import ResultadoValidacao


def salvar_relatorios(
    resultado: ResultadoValidacao, arquivo_origem: Path, saida: Path
) -> dict[str, Path]:
    """Cria a pasta e salva as tabelas e contagens, sem sobrescrever a entrada."""
    caminhos = {
        "validos": saida / "validos.csv",
        "rejeitados": saida / "rejeitados.csv",
        "resumo": saida / "resumo.json",
    }
    if arquivo_origem.resolve() in {p.resolve() for p in caminhos.values()}:
        raise ValueError("A pasta de saída não pode sobrescrever o arquivo de entrada")
    saida.mkdir(parents=True, exist_ok=True)
    resultado.validos.to_csv(caminhos["validos"], index=False, encoding="utf-8")
    rejeitados = resultado.rejeitados.copy()
    rejeitados.insert(0, "arquivo_origem", str(arquivo_origem))
    rejeitados.to_csv(caminhos["rejeitados"], index=False, encoding="utf-8")
    resumo = {
        "arquivo_origem": str(arquivo_origem),
        **resultado.resumo,
        "colunas_ausentes": list(resultado.colunas_ausentes),
    }
    caminhos["resumo"].write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return caminhos
