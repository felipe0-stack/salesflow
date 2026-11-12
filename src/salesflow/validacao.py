"""Regras de qualidade de vendas, independentes de arquivos e do terminal."""

import re
from dataclasses import dataclass
from datetime import date

import pandas as pd

COLUNAS_OBRIGATORIAS = (
    "id_pedido",
    "id_item",
    "data",
    "produto",
    "categoria",
    "quantidade",
    "preco_unitario",
)
COLUNAS_VALIDAS = (*COLUNAS_OBRIGATORIAS, "preco_unitario_centavos")
COLUNAS_REJEITADAS = (
    *COLUNAS_OBRIGATORIAS,
    "linha_origem",
    "classificacao",
    "motivo",
)


@dataclass
class ResultadoValidacao:
    """Tabelas de saída e contagens de categorias mutuamente exclusivas."""

    validos: pd.DataFrame
    rejeitados: pd.DataFrame
    resumo: dict[str, int]
    colunas_ausentes: tuple[str, ...] = ()


def converter_preco_centavos(preco: str) -> int:
    """Converte uma representação decimal positiva em inteiro, sem usar float."""
    if re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", preco) is None:
        raise ValueError("preco_unitario deve usar ponto e ter até duas casas decimais")
    inteira, _, fracao = preco.partition(".")
    centavos = int(inteira) * 100 + int(fracao.ljust(2, "0"))
    if centavos <= 0:
        raise ValueError("preco_unitario deve ser maior que zero")
    return centavos


def _texto(valor: object) -> str:
    """Representa campos ausentes como vazios, sem aparar o conteúdo original."""
    return "" if pd.isna(valor) else str(valor)


def _validar_registro(registro: dict[str, str]) -> tuple[dict, list[str]]:
    motivos = []
    for coluna in ("id_pedido", "id_item", "produto", "categoria"):
        if not registro[coluna].strip():
            motivos.append(f"{coluna} deve estar preenchido")

    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", registro["data"]) is None:
            raise ValueError
        date.fromisoformat(registro["data"])
    except ValueError:
        motivos.append("data deve ser uma data real no formato AAAA-MM-DD")

    quantidade = 0
    try:
        if re.fullmatch(r"[0-9]+", registro["quantidade"]) is None:
            raise ValueError
        quantidade = int(registro["quantidade"])
        if quantidade <= 0:
            raise ValueError
    except ValueError:
        motivos.append("quantidade deve ser um inteiro maior que zero")

    centavos = 0
    try:
        centavos = converter_preco_centavos(registro["preco_unitario"])
    except ValueError as erro:
        motivos.append(str(erro))

    if motivos:
        return {}, motivos
    return {
        **registro,
        "quantidade": quantidade,
        "preco_unitario": f"{centavos // 100}.{centavos % 100:02d}",
        "preco_unitario_centavos": centavos,
    }, []


def validar_vendas(dados: pd.DataFrame) -> ResultadoValidacao:
    """Valida campos primeiro e resolve duplicidades somente entre linhas válidas.

    Recebe preferencialmente o DataFrame de carregar_vendas(como_texto=True),
    para que nenhuma conversão numérica anterior esconda formatos inválidos.
    O DataFrame recebido não é alterado.
    """
    ausentes = tuple(c for c in COLUNAS_OBRIGATORIAS if c not in dados.columns)
    resumo = dict(
        lidas=len(dados), validas=0, invalidas=0, duplicadas_ignoradas=0, conflitantes=0
    )
    grupos: dict[tuple[str, str], list[tuple[int, dict, dict]]] = {}
    aceitos: list[tuple[int, dict]] = []
    rejeitados: dict[int, dict] = {}

    def rejeitar(linha: int, original: dict, classificacao: str, motivo: str) -> None:
        rejeitados[linha] = {
            **original,
            "linha_origem": linha,
            "classificacao": classificacao,
            "motivo": motivo,
        }

    for linha, entrada in enumerate(dados.to_dict(orient="records"), start=2):
        original = {c: _texto(entrada.get(c, "")) for c in COLUNAS_OBRIGATORIAS}
        if ausentes:
            normalizado, motivos = (
                {},
                [f"Colunas obrigatórias ausentes: {', '.join(ausentes)}"],
            )
        else:
            normalizado, motivos = _validar_registro(original)
        if motivos:
            rejeitar(linha, original, "invalida", "; ".join(motivos))
            resumo["invalidas"] += 1
        else:
            chave = (original["id_pedido"], original["id_item"])
            grupos.setdefault(chave, []).append((linha, original, normalizado))

    for ocorrencias in grupos.values():
        conteudos = {
            tuple(normalizado[c] for c in COLUNAS_OBRIGATORIAS)
            for _, _, normalizado in ocorrencias
        }
        if len(conteudos) > 1:
            for linha, original, _ in ocorrencias:
                rejeitar(
                    linha,
                    original,
                    "conflitante",
                    "Mesma chave (id_pedido, id_item) com conteúdos válidos "
                    "divergentes",
                )
            resumo["conflitantes"] += len(ocorrencias)
        else:
            linha_aceita, _, normalizado = ocorrencias[0]
            aceitos.append((linha_aceita, normalizado))
            resumo["validas"] += 1
            for linha, original, _ in ocorrencias[1:]:
                rejeitar(
                    linha,
                    original,
                    "duplicada_ignorada",
                    f"Repetição idêntica do registro {linha_aceita} para a mesma chave",
                )
                resumo["duplicadas_ignoradas"] += 1

    # dtype=object mantém inteiros Python exatos, inclusive acima de 64 bits.
    validos = pd.DataFrame(
        [registro for _, registro in sorted(aceitos)],
        columns=COLUNAS_VALIDAS,
        dtype=object,
    )
    descartados = pd.DataFrame(
        [rejeitados[linha] for linha in sorted(rejeitados)],
        columns=COLUNAS_REJEITADAS,
        dtype=object,
    )
    return ResultadoValidacao(validos, descartados, resumo, ausentes)
