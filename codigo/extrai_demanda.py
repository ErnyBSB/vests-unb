#!/usr/bin/env python3
"""Extrai a tabela de demanda e vagas do Vestibular da UnB para JSON.

Mesma disciplina do `extrai_anexo_i.py`: determinístico, sem rede, e conferido
contra os totais que a própria tabela imprime. Qualquer divergência aborta a
execução em vez de gravar dado errado com aparência de dado certo.

A tabela traz, por curso, doze trios (vagas, inscritos, demanda): os dez recortes
do sistema de cotas, o Sistema Universal e o total do curso.

Uso:
    python3 codigo/extrai_demanda.py <tabela.pdf> <saida.json> [--confere-com <app.html>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# Os onze sistemas de ingresso, na ordem em que a tabela imprime as colunas.
# Os nomes são os mesmos que o explorador exibe.
SISTEMAS = [
    "Cotas Negras",
    "Cotas Trans",
    "EP ≤1SM PPI · Defic.",
    "EP ≤1SM PPI · Geral",
    "EP ≤1SM não-PPI · Defic.",
    "EP ≤1SM não-PPI · Geral",
    "EP >1SM PPI · Defic.",
    "EP >1SM PPI · Geral",
    "EP >1SM não-PPI · Defic.",
    "EP >1SM não-PPI · Geral",
    "Universal",
]
N_TRIOS = len(SISTEMAS) + 1  # os onze sistemas mais o total do curso

TRIO = r"\d+\s+\d+\s+\d+[.,]\d{2}"
LINHA_CURSO = re.compile(
    rf"^(?P<grupo>I{{1,2}})\s+(?P<curso>\S.*?)\s+(?P<nums>{TRIO}(?:\s+{TRIO}){{{N_TRIOS - 1}}})$"
)
LINHA_TOTAL = re.compile(
    rf"^(?P<rotulo>Total\b.*?)\s+(?P<nums>{TRIO}(?:\s+{TRIO}){{{N_TRIOS - 1}}})$"
)
CAMPUS = re.compile(r"^Campus UnB\s*[—–-]\s*(?P<nome>.+?)\s*/\s*DF$")
TURNO = re.compile(r"^(?P<turno>Diurno|Noturno)$")


class ErroDeExtracao(Exception):
    """Uma premissa do formato da tabela não se confirmou."""


def linhas_do_pdf(pdf: Path) -> list[str]:
    """O PDF como linhas, com os espaços em branco colapsados.

    A tabela é uma planilha impressa num único quadro largo; o alinhamento das
    colunas não carrega informação depois que os campos já estão separados.
    """
    saida = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, check=True
    )
    texto = saida.stdout.decode("utf-8")
    return [re.sub(r"\s+", " ", linha).strip() for linha in texto.splitlines()]


def numeros(bruto: str) -> list[float]:
    """Os campos numéricos da linha; a tabela mistura ponto e vírgula decimal."""
    return [float(n.replace(",", ".")) for n in bruto.split()]


def trios(valores: list[float]) -> list[dict]:
    """Agrupa a sequência plana em trios (vagas, inscritos, demanda)."""
    if len(valores) != N_TRIOS * 3:
        raise ErroDeExtracao(f"esperava {N_TRIOS * 3} números, achei {len(valores)}")
    saida = []
    for i in range(0, len(valores), 3):
        vagas, inscritos, demanda = valores[i : i + 3]
        saida.append(
            {"vagas": int(vagas), "inscritos": int(inscritos), "demanda": demanda}
        )
    return saida


def nome_do_campus(bruto: str) -> str:
    """«Darcy Ribeiro (Plano Piloto)» é «Darcy Ribeiro» para quem lê o app."""
    return re.sub(r"\s*\(.*?\)\s*$", "", bruto).strip()


def extrai(pdf: Path) -> tuple[list[dict], list[dict], list[float]]:
    """Devolve os cursos, os totais impressos por seção e o Total Geral."""
    cursos: list[dict] = []
    secoes: list[dict] = []
    total_geral: list[float] | None = None
    campus = turno = None

    for linha in linhas_do_pdf(pdf):
        if not linha:
            continue

        if m := CAMPUS.match(linha):
            campus, turno = nome_do_campus(m["nome"]), None
            continue
        if m := TURNO.match(linha):
            turno = m["turno"]
            continue

        if m := LINHA_TOTAL.match(linha):
            valores = numeros(m["nums"])
            if m["rotulo"].strip().lower() == "total geral":
                total_geral = valores
            else:
                if campus is None or turno is None:
                    raise ErroDeExtracao(f"total fora de seção: {linha!r}")
                secoes.append(
                    {"campus": campus, "turno": turno,
                     "rotulo": m["rotulo"].strip(), "valores": valores}
                )
            continue

        if m := LINHA_CURSO.match(linha):
            if campus is None or turno is None:
                raise ErroDeExtracao(f"curso fora de campus/turno: {linha!r}")
            partes = trios(numeros(m["nums"]))
            *por_sistema, total = partes
            cursos.append(
                {
                    "grupo": m["grupo"],
                    "curso": m["curso"].strip(),
                    "campus": campus,
                    "turno": turno,
                    "vagas": total["vagas"],
                    "inscritos": total["inscritos"],
                    "demanda": total["demanda"],
                    "sistemas": [
                        {"sistema": nome, **valores}
                        for nome, valores in zip(SISTEMAS, por_sistema)
                    ],
                }
            )

    if not cursos:
        raise ErroDeExtracao("nenhum curso encontrado — o PDF é a tabela de demanda?")
    if total_geral is None:
        raise ErroDeExtracao("não encontrei a linha Total Geral")
    return cursos, secoes, total_geral


def confere(cursos: list[dict], secoes: list[dict], total_geral: list[float]) -> None:
    """Confronta o extraído com o que a própria tabela afirma.

    A demanda fica de fora de qualquer verificação aritmética: a Obs² da tabela
    diz que ela considera «todos os candidatos que concorrem às vagas do curso,
    independentemente de estarem ou não concorrendo prioritariamente a essas
    vagas» — ou seja, não é inscritos ÷ vagas, e recalculá-la seria inventar
    número que a fonte não traz.
    """
    erros: list[str] = []

    for curso in cursos:
        rotulo = f"{curso['campus']} · {curso['turno']} · {curso['curso']}"
        soma = sum(s["vagas"] for s in curso["sistemas"])
        if soma != curso["vagas"]:
            erros.append(
                f"{rotulo}: vagas dos sistemas somam {soma}, total do curso é "
                f"{curso['vagas']}"
            )
        universal = next(s for s in curso["sistemas"] if s["sistema"] == "Universal")
        if universal["inscritos"] != curso["inscritos"]:
            erros.append(
                f"{rotulo}: inscritos no Universal ({universal['inscritos']}) "
                f"diferem dos inscritos do curso ({curso['inscritos']})"
            )

    for secao in secoes:
        do_grupo = [
            c for c in cursos
            if c["campus"] == secao["campus"] and c["turno"] == secao["turno"]
        ]
        for i, sistema in enumerate(SISTEMAS):
            somado = sum(c["sistemas"][i]["vagas"] for c in do_grupo)
            impresso = int(secao["valores"][i * 3])
            if somado != impresso:
                erros.append(
                    f"{secao['rotulo']} ({secao['campus']} · {secao['turno']}), "
                    f"{sistema}: vagas somam {somado}, total impresso é {impresso}"
                )

    for i, sistema in enumerate(SISTEMAS):
        somado = sum(int(s["valores"][i * 3]) for s in secoes)
        impresso = int(total_geral[i * 3])
        if somado != impresso:
            erros.append(
                f"Total Geral, {sistema}: seções somam {somado}, impresso é {impresso}"
            )

    if erros:
        raise ErroDeExtracao(
            "a extração não bate com os totais impressos na tabela:\n  - "
            + "\n  - ".join(erros)
        )


def confere_com_app(cursos: list[dict], html: Path) -> None:
    """Confronta o extraído com o vetor CURSOS publicado no explorador.

    É o teste mais forte disponível: se bater, a extração reproduz exatamente o
    dataset que está no ar. O extrator não depende disto para funcionar — é uma
    conferência opcional, pedida pela linha de comando.
    """
    fonte = html.read_text(encoding="utf-8")
    achado = re.search(r"const CURSOS = (\[.*?\]);", fonte, re.S)
    if not achado:
        raise ErroDeExtracao(f"não encontrei o vetor CURSOS em {html}")
    publicado = json.loads(achado.group(1))

    if len(publicado) != len(cursos):
        raise ErroDeExtracao(
            f"{html.name} publica {len(publicado)} cursos, a extração produziu "
            f"{len(cursos)}"
        )

    # Duas categorias de divergência, com pesos diferentes. Valor divergente é
    # erro: uma das duas pontas está com o número errado. Nome divergente não é:
    # o explorador foi montado com nomes encurtados à mão, e a extração devolve o
    # que a tabela oficial escreve. Reportar, não abortar.
    sem_nome = lambda c: {k: v for k, v in c.items() if k != "curso"}
    valores = [
        f"{a['curso']} ({a['campus']} · {a['turno']}):\n"
        f"      publicado: {json.dumps(sem_nome(a), ensure_ascii=False, sort_keys=True)}\n"
        f"      extraído:  {json.dumps(sem_nome(b), ensure_ascii=False, sort_keys=True)}"
        for a, b in zip(publicado, cursos)
        if sem_nome(a) != sem_nome(b)
    ]
    if valores:
        raise ErroDeExtracao(
            f"{len(valores)} curso(s) com valores diferentes do publicado:\n  - "
            + "\n  - ".join(valores[:5])
            + ("\n  - ..." if len(valores) > 5 else "")
        )

    nomes = [(a["curso"], b["curso"]) for a, b in zip(publicado, cursos)
             if a["curso"] != b["curso"]]
    print(
        f"conferido com {html.name}: {len(cursos)} cursos, todos os valores idênticos"
    )
    if nomes:
        print(f"{len(nomes)} nome(s) diferem — o explorador publica versões encurtadas:")
        for publicado_nome, extraido in nomes:
            print(f"  · publicado: {publicado_nome}")
            print(f"    tabela:    {extraido}")


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def documento(pdf: Path, cursos: list[dict]) -> dict:
    return {
        "fonte": {
            "descricao": "Tabela de demanda e vagas do Vestibular 2026 — Cebraspe/UnB",
            "arquivo": pdf.as_posix(),
            "sha256": sha256(pdf),
            "observacao": (
                "A demanda considera todos os candidatos que concorrem às vagas do "
                "curso, independentemente de estarem ou não concorrendo "
                "prioritariamente a essas vagas (Obs² da tabela). Não é "
                "inscritos ÷ vagas."
            ),
            "gerado_por": "codigo/extrai_demanda.py",
        },
        "cursos": cursos,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdf", type=Path, help="a tabela de demanda em PDF")
    parser.add_argument("saida", type=Path, help="o JSON a gravar")
    parser.add_argument(
        "--confere-com", type=Path, metavar="HTML", dest="confere_com",
        help="confronta o resultado com o vetor CURSOS de um explorador publicado",
    )
    args = parser.parse_args(argv)

    if not args.pdf.is_file():
        print(f"erro: PDF não encontrado: {args.pdf}", file=sys.stderr)
        return 2

    try:
        cursos, secoes, geral = extrai(args.pdf)
        confere(cursos, secoes, geral)
        if args.confere_com:
            confere_com_app(cursos, args.confere_com)
    except ErroDeExtracao as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(documento(args.pdf, cursos), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    campi = len({c["campus"] for c in cursos})
    conferido = " · idêntico ao explorador publicado" if args.confere_com else ""
    print(
        f"{args.saida}: {len(cursos)} cursos em {campi} campi — "
        f"totais conferem{conferido}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
