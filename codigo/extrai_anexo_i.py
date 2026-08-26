#!/usr/bin/env python3
"""Extrai o Anexo I (Quadro de vagas) do edital do Vestibular da UnB.

A extração é determinística: rodar duas vezes sobre o mesmo PDF produz um arquivo
byte a byte idêntico. Nada de rede, nada de data de geração no arquivo de saída —
o que muda o resultado é o PDF de entrada, e só ele.

O edital imprime uma linha de Total por campus e um TOTAL (TODOS OS CURSOS) ao
final. A extração é conferida contra esses números: se qualquer soma não fechar,
o programa falha em vez de gravar dado errado com aparência de dado certo.

Duas saídas a partir do mesmo PDF: o Markdown, para ler, e o JSON, para o
aplicativo consumir. O PDF em `sources/` é a fonte única — nada é derivado do
Markdown.

Uso:
    python3 codigo/extrai_anexo_i.py <edital.pdf> <saida.md> [--json <saida.json>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# As 12 colunas numéricas do Anexo I, na ordem em que o edital as imprime.
# «EP» = Sistema de Cotas para Escolas Públicas.
# «PPI» = pessoas que se autodeclararam pretas, pardas, indígenas ou quilombolas.
# Os onze sistemas de ingresso, com os mesmos rótulos que `extrai_demanda.py`
# usa para 2026 — é o que permite comparar as duas edições sem tradução.
# O edital define os eixos nos itens 10.2.20.1 a 10.2.20.3: «grupo» é faixa de
# renda, «nível» é a autodeclaração PPI, «condição» é deficiência.
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

# Os quatro campi, com os mesmos nomes que 2026 usa. O Anexo I escreve
# «Campus UnB Ceilândia (FCTS)»; o turno vem em campo separado.
CAMPI = ["Darcy Ribeiro", "Ceilândia", "Gama", "Planaltina"]

# Rótulos curtos das colunas, para o cabeçalho da tabela em Markdown.
COLUNAS = [
    "Negros",
    "Trans",
    "EP ≤1SM PPI · Defic.",
    "EP ≤1SM PPI · Geral",
    "EP ≤1SM não-PPI · Defic.",
    "EP ≤1SM não-PPI · Geral",
    "EP >1SM PPI · Defic.",
    "EP >1SM PPI · Geral",
    "EP >1SM não-PPI · Defic.",
    "EP >1SM não-PPI · Geral",
    "Universal",
    "Total",
]
N_SISTEMAS = len(COLUNAS) - 1  # as 11 primeiras somam a 12ª

LINHA_NUMERICA = re.compile(r"^(?P<cabeca>.*?)\s+(?P<nums>\d+(?:\s+\d+){11})\s*$")
CABECALHO_SECAO = re.compile(r"^\s*(?P<n>\d+)\s+(?P<nome>CAMPUS\s+.+?)\s*$")
GRUPO = re.compile(r"^(?P<grupo>I{1,2})(?:\s+(?P<frag>.*))?$")
TOTAL_GERAL = re.compile(r"^\s*TOTAL\s*\(TODOS OS CURSOS\)\s*$", re.IGNORECASE)
TOTAL_SECAO = re.compile(r"^\s*Total\s*$", re.IGNORECASE)

# Além do Total de cada seção, o Anexo I traz subtotais que agrupam seções —
# «Total Darcy Ribeiro» (diurno + noturno) e «TOTAL (FUP)» (Planaltina).
# Qualquer linha numérica cuja cabeça não seja um grupo é tratada como agregado.


class ErroDeExtracao(Exception):
    """Uma premissa do formato do edital não se confirmou."""


def texto_do_pdf(pdf: Path) -> list[str]:
    """Devolve o PDF como linhas, preservando o alinhamento das colunas."""
    saida = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        check=True,
    )
    return saida.stdout.decode("utf-8").splitlines()


def recorta_anexo_i(linhas: list[str]) -> list[str]:
    """Isola o trecho entre o título do Anexo I e o início do Anexo II."""
    inicio = fim = None
    for i, linha in enumerate(linhas):
        nu = linha.strip()
        if inicio is None and nu == "ANEXO I":
            # o título vem seguido de QUADRO DE VAGAS; sem isso é outra ocorrência
            if any(linhas[j].strip() == "QUADRO DE VAGAS" for j in range(i + 1, i + 4)):
                inicio = i
        elif inicio is not None and nu == "ANEXO II":
            fim = i
            break
    if inicio is None:
        raise ErroDeExtracao("não encontrei o título do Anexo I no PDF")
    if fim is None:
        raise ErroDeExtracao("não encontrei o Anexo II, que delimita o fim do Anexo I")
    return linhas[inicio:fim]


def numeros(bruto: str) -> list[int]:
    return [int(n) for n in bruto.split()]


def junta(fragmentos: list[str]) -> str:
    """Recompõe o nome do curso quebrado em várias linhas pelo PDF."""
    nome = ""
    for frag in fragmentos:
        frag = frag.strip()
        if not frag:
            continue
        if not nome:
            nome = frag
        elif nome.endswith("/"):
            nome += frag  # "(Bacharelado/" + "Licenciatura)"
        else:
            nome += " " + frag
    return re.sub(r"\s+", " ", nome).strip()


def nome_fechado(fragmentos: list[str]) -> bool:
    """O nome do curso termina sempre na qualificação entre parênteses."""
    nome = junta(fragmentos)
    return "(" in nome and nome.count("(") == nome.count(")")


def descarta_cabecalho(linhas: list[str]) -> list[str]:
    """Remove o cabeçalho da tabela, que se repete no início de cada seção.

    A última linha do cabeçalho é sempre a que traz «deficiência» sob as colunas
    de cotas — palavra que não ocorre em nome de curso. Tudo até ela é descartado.
    """
    primeira_numerica = next(
        (i for i, l in enumerate(linhas) if LINHA_NUMERICA.match(l)), None
    )
    if primeira_numerica is None:
        return linhas
    ultima_cabecalho = None
    for i in range(primeira_numerica):
        if "deficiência" in linhas[i]:
            ultima_cabecalho = i
    return linhas if ultima_cabecalho is None else linhas[ultima_cabecalho + 1 :]


def secoes(linhas: list[str]) -> list[dict]:
    """Quebra o Anexo I em seções de campus, na ordem em que aparecem."""
    achadas: list[dict] = []
    for linha in linhas:
        m = CABECALHO_SECAO.match(linha)
        if m:
            achadas.append({"numero": int(m["n"]), "nome": m["nome"], "linhas": []})
        elif achadas:
            achadas[-1]["linhas"].append(linha)
    if not achadas:
        raise ErroDeExtracao("nenhuma seção de campus encontrada no Anexo I")
    return achadas


def analisa_secao(secao: dict) -> dict:
    """Extrai os cursos e a linha de Total de uma seção de campus."""
    cursos: list[dict] = []
    agregados: list[dict] = []
    pendentes: list[str] = []   # fragmentos ainda sem linha numérica
    aberto: dict | None = None  # curso cujo nome ainda não fechou os parênteses

    def fecha(motivo: str) -> None:
        nonlocal aberto
        if aberto is None:
            return
        if not nome_fechado(aberto["fragmentos"]):
            raise ErroDeExtracao(
                f"nome de curso não fechou os parênteses ({motivo}): "
                f"{junta(aberto['fragmentos'])!r}"
            )
        aberto["curso"] = junta(aberto["fragmentos"])
        cursos.append(aberto)
        aberto = None

    for linha in descarta_cabecalho(secao["linhas"]):
        m = LINHA_NUMERICA.match(linha)
        if m:
            cabeca = m["cabeca"].strip()
            vagas = numeros(m["nums"])
            g = GRUPO.match(cabeca)
            if not g:
                # não é curso: é Total da seção, subtotal ou o total geral
                fecha("linha agregada")
                agregados.append({"rotulo": " ".join(cabeca.split()), "vagas": vagas})
                pendentes = []
                continue
            fecha("nova linha numérica")
            aberto = {
                "grupo": g["grupo"],
                "vagas": vagas,
                "fragmentos": pendentes + ([g["frag"]] if g["frag"] else []),
            }
            pendentes = []
            # o nome pode caber inteiro na própria linha numérica —
            # «II   Física (Bacharelado)   0  1  ...» — e aí já fecha aqui.
            if nome_fechado(aberto["fragmentos"]):
                fecha("nome completo na linha numérica")
        elif linha.strip():
            if aberto is not None:
                aberto["fragmentos"].append(linha)
                if nome_fechado(aberto["fragmentos"]):
                    fecha("parênteses fechados")
            else:
                pendentes.append(linha)

    fecha("fim da seção")

    totais = [a for a in agregados if TOTAL_SECAO.match(a["rotulo"])]
    if len(totais) != 1:
        raise ErroDeExtracao(
            f"seção {secao['nome']!r}: esperava uma linha de Total, achei {len(totais)}"
        )
    subtotais = [
        a for a in agregados
        if a is not totais[0] and not TOTAL_GERAL.match(a["rotulo"])
    ]
    return {"numero": secao["numero"], "nome": secao["nome"], "cursos": cursos,
            "total_impresso": totais[0]["vagas"], "subtotais": subtotais}


def total_geral_impresso(linhas: list[str]) -> list[int]:
    """O TOTAL (TODOS OS CURSOS) que fecha o Anexo I."""
    for linha in linhas:
        m = LINHA_NUMERICA.match(linha)
        if m and TOTAL_GERAL.match(m["cabeca"].strip()):
            return numeros(m["nums"])
    raise ErroDeExtracao("não encontrei a linha TOTAL (TODOS OS CURSOS)")


def confere(secoes_lidas: list[dict], total_geral: list[int]) -> None:
    """Confronta o que foi extraído com os totais impressos no próprio edital."""
    erros: list[str] = []

    for secao in secoes_lidas:
        for curso in secao["cursos"]:
            soma = sum(curso["vagas"][:N_SISTEMAS])
            if soma != curso["vagas"][-1]:
                erros.append(
                    f"{secao['nome']} · {curso['curso']}: sistemas somam {soma}, "
                    f"Total impresso é {curso['vagas'][-1]}"
                )
        somado = [sum(c["vagas"][i] for c in secao["cursos"]) for i in range(len(COLUNAS))]
        if somado != secao["total_impresso"]:
            erros.append(
                f"{secao['nome']}: soma dos cursos {somado} difere do Total "
                f"impresso {secao['total_impresso']}"
            )

    # Os subtotais que agrupam seções — «Total Darcy Ribeiro», «TOTAL (FUP)» —
    # devem fechar com a soma das seções imediatamente anteriores. Qual conjunto
    # de seções cada um agrupa não é declarado no edital, então é procurado: se
    # nenhum conjunto contíguo fecha, o subtotal não foi entendido.
    for fim, secao in enumerate(secoes_lidas, start=1):
        for sub in secao["subtotais"]:
            soma = sum(sub["vagas"][:N_SISTEMAS])
            if soma != sub["vagas"][-1]:
                erros.append(
                    f"subtotal {sub['rotulo']!r}: sistemas somam {soma}, "
                    f"Total impresso é {sub['vagas'][-1]}"
                )
                continue
            casou = any(
                [
                    sum(s["total_impresso"][i] for s in secoes_lidas[inicio:fim])
                    for i in range(len(COLUNAS))
                ]
                == sub["vagas"]
                for inicio in range(fim)
            )
            if not casou:
                erros.append(
                    f"subtotal {sub['rotulo']!r} {sub['vagas']} não fecha com a soma "
                    "de nenhum conjunto contíguo de seções anteriores"
                )

    somado_geral = [
        sum(s["total_impresso"][i] for s in secoes_lidas) for i in range(len(COLUNAS))
    ]
    if somado_geral != total_geral:
        erros.append(
            f"soma das seções {somado_geral} difere do TOTAL (TODOS OS CURSOS) "
            f"{total_geral}"
        )

    if erros:
        raise ErroDeExtracao(
            "a extração não bate com os totais impressos no edital:\n  - "
            + "\n  - ".join(erros)
        )


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def markdown(pdf: Path, secoes_lidas: list[dict], total_geral: list[int]) -> str:
    n_cursos = sum(len(s["cursos"]) for s in secoes_lidas)
    linhas = [
        "# Anexo I — Quadro de vagas · Vestibular UnB 2027",
        "",
        "Extraído do Anexo I do edital, tabela por tabela, sem intervenção manual.",
        "**Em caso de divergência, vale o edital.**",
        "",
        "| | |",
        "|---|---|",
        "| Fonte | Edital nº 1 – Vestibular 2027, de 25 de agosto de 2026 (UnB/Cebraspe) |",
        f"| Arquivo | [`{pdf.as_posix()}`]({('../../' + pdf.as_posix())}) |",
        f"| sha256 do PDF | `{sha256(pdf)}` |",
        f"| Cursos | {n_cursos} em {len(secoes_lidas)} seções de campus |",
        "| Gerado por | [`codigo/extrai_anexo_i.py`](../../codigo/extrai_anexo_i.py) |",
        "",
        "> Arquivo **gerado**. Não edite à mão: rode o script de novo sobre o PDF.",
        "",
        "## Legenda das colunas",
        "",
        "| Coluna | Significado |",
        "|---|---|",
        "| Negros | Sistema de Cotas para Negros |",
        "| Trans | Sistema de Cotas para pessoas Trans |",
        "| EP | Sistema de Cotas para Escolas Públicas |",
        "| ≤1SM / >1SM | renda familiar bruta por pessoa até 1 salário mínimo, ou acima |",
        "| PPI / não-PPI | autodeclaração como preta, parda, indígena ou quilombola |",
        "| Defic. / Geral | vagas reservadas a pessoas com deficiência, ou gerais |",
        "| Universal | Sistema Universal |",
        "",
        "`*` no nome do curso: exige Certificação de Habilidade Específica.",
        "",
    ]

    cabecalho = "| Grupo | Curso | " + " | ".join(COLUNAS) + " |"
    separador = "|---|---|" + "---:|" * len(COLUNAS)

    for secao in secoes_lidas:
        titulo = secao["nome"].title().replace("Unb", "UnB")
        linhas += [
            f"## {secao['numero']}. {titulo}",
            "",
            f"{len(secao['cursos'])} cursos.",
            "",
            cabecalho,
            separador,
        ]
        for curso in secao["cursos"]:
            vagas = " | ".join(str(v) for v in curso["vagas"])
            linhas.append(f"| {curso['grupo']} | {curso['curso']} | {vagas} |")
        total = " | ".join(f"**{v}**" for v in secao["total_impresso"])
        linhas.append(f"| | **Total** | {total} |")
        for sub in secao["subtotais"]:
            vagas = " | ".join(f"**{v}**" for v in sub["vagas"])
            linhas.append(f"| | **{sub['rotulo']}** | {vagas} |")
        linhas.append("")

    linhas += [
        "## Total geral",
        "",
        cabecalho.replace("| Grupo | Curso |", "| | |"),
        separador,
        "| | **Todos os cursos** | "
        + " | ".join(f"**{v}**" for v in total_geral)
        + " |",
        "",
    ]
    return "\n".join(linhas)


def campus_e_turno(nome_secao: str) -> tuple[str, str]:
    """«Campus UnB Planaltina (FUP) – Noturno» vira («Planaltina», «Noturno»)."""
    turno = "Noturno" if "noturno" in nome_secao.lower() else "Diurno"
    limpo = re.sub(r"\s*\(.*?\)", "", nome_secao)
    for campus in CAMPI:
        if campus.lower() in limpo.lower():
            return campus, turno
    raise ErroDeExtracao(f"campus não reconhecido em {nome_secao!r}")


def documento_json(pdf: Path, secoes_lidas: list[dict]) -> dict:
    """O mesmo formato de dados/2026/demanda-2026.json, sem inscritos nem demanda.

    O Anexo I é publicado antes das inscrições: existe oferta, não existe procura.
    Inventar os dois campos com zero seria pior que omiti-los.
    """
    cursos = []
    for secao in secoes_lidas:
        campus, turno = campus_e_turno(secao["nome"])
        for curso in secao["cursos"]:
            cursos.append({
                "grupo": curso["grupo"],
                "curso": curso["curso"],
                "campus": campus,
                "turno": turno,
                "vagas": curso["vagas"][-1],
                "sistemas": [
                    {"sistema": nome, "vagas": vagas}
                    for nome, vagas in zip(SISTEMAS, curso["vagas"][:N_SISTEMAS])
                ],
            })
    return {
        "fonte": {
            "descricao": (
                "Anexo I (Quadro de vagas) do Edital nº 1 – Vestibular 2027, "
                "de 25 de agosto de 2026 — UnB/Cebraspe"
            ),
            "arquivo": pdf.as_posix(),
            "sha256": sha256(pdf),
            "observacao": (
                "Vagas ofertadas no segundo semestre letivo de 2027. Não há "
                "inscritos: o quadro é publicado antes da abertura das inscrições."
            ),
            "gerado_por": "codigo/extrai_anexo_i.py",
        },
        "cursos": cursos,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdf", type=Path, help="o edital em PDF")
    parser.add_argument("saida", type=Path, help="o Markdown a gravar")
    parser.add_argument("--json", type=Path, metavar="ARQUIVO", dest="saida_json",
                        help="grava também o JSON que o aplicativo consome")
    args = parser.parse_args(argv[1:])

    pdf, saida = args.pdf, args.saida
    if not pdf.is_file():
        print(f"erro: PDF não encontrado: {pdf}", file=sys.stderr)
        return 2

    try:
        anexo = recorta_anexo_i(texto_do_pdf(pdf))
        lidas = [analisa_secao(s) for s in secoes(anexo)]
        geral = total_geral_impresso(anexo)
        confere(lidas, geral)
    except ErroDeExtracao as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(markdown(pdf, lidas, geral) + "\n", encoding="utf-8")

    n_cursos = sum(len(s["cursos"]) for s in lidas)
    print(f"{saida}: {n_cursos} cursos em {len(lidas)} seções — totais conferem")

    if args.saida_json:
        try:
            doc = documento_json(pdf, lidas)
        except ErroDeExtracao as erro:
            print(f"erro: {erro}", file=sys.stderr)
            return 1
        args.saida_json.parent.mkdir(parents=True, exist_ok=True)
        args.saida_json.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        vagas = sum(c["vagas"] for c in doc["cursos"])
        campi = len({c["campus"] for c in doc["cursos"]})
        print(f"{args.saida_json}: {len(doc['cursos'])} cursos · {vagas} vagas · {campi} campi")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
