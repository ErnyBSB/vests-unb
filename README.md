![Vestibular UnB — vagas, demanda e cursos, dados em app HTML](images/repo-readme-image.png)

# vests-unb

Neste repositório há arquivos, executáveis ou não, com dados sobre os
vestibulares da Universidade de Brasília (UnB). O material é produzido em
Software Livre (The Unlicense, domínio público) e está disponível para ajudar
pessoas interessadas no ingresso nessa universidade, que também foi minha
universidade por muitos anos.

Na prática: os documentos oficiais publicados pelo Cebraspe/UnB (em PDF) viram
um aplicativo HTML de página única, navegável, que permite comparar a
concorrência (candidato/vaga) curso a curso e por sistema de ingresso.

## O produto

**[`produtos/2026/explorador-concorrencia-unb-2026.html`](produtos/2026/explorador-concorrencia-unb-2026.html)**
— Explorador de concorrência do Vestibular 2026.

Abra o arquivo direto no navegador (duplo clique). Não há build, servidor nem
instalação. É necessária conexão com a internet: as bibliotecas de gráficos e as
fontes são carregadas por CDN.

O que dá para fazer:

- Percorrer as **99 combinações de curso/turno** ordenadas por demanda,
  inscritos, vagas ou nome.
- Filtrar por **campus** (Darcy Ribeiro, Ceilândia, Gama, Planaltina) e por
  **turno** (diurno/noturno).
- Buscar curso pelo nome, sem sensibilidade a acento ou maiúscula.
- Alternar entre **escala logarítmica e linear** nas barras — necessário porque a
  distribuição é muito assimétrica (Medicina, com ~209 candidatos por vaga,
  achata visualmente todo o resto numa escala linear).
- Clicar num curso para abrir o detalhe da concorrência em cada um dos
  **11 sistemas de ingresso** (Universal, Cotas para Pessoas Negras, Cotas Trans
  e as faixas de escola pública por renda, PPI/não-PPI e deficiência).

Os indicadores do topo (cursos exibidos, inscritos, vagas, demanda média) são
recalculados conforme os filtros aplicados.

### O recorte de 2026

| | |
|---|---|
| Cursos/turnos | 99 |
| Vagas | 2.102 |
| Inscritos | 16.823 |
| Campi | 4 |
| Sistemas de ingresso | 11 |

Cursos mais concorridos: Medicina (208,95 cand/vaga), Direito diurno (41,40),
Psicologia (40,56), Ciência da Computação (30,50) e Direito noturno (25,67).

## Estrutura do repositório

```
sources/<ano>/      Documentos oficiais em PDF — a fonte primária, preservada
                   como recebida do Cebraspe/UnB
codigo/            Scripts de extração e tratamento dos dados
produtos/<ano>/    Os aplicativos HTML gerados, um por edição do vestibular
images/            Imagens do repositório
```

A organização por ano é proposital: cada edição do vestibular entra como um novo
diretório, e os produtos das edições anteriores continuam abríveis como estavam.

## Fontes

Todos os PDFs em `sources/2026/` são documentos públicos publicados pelo Cebraspe
e pela Universidade de Brasília:

- `tabela-demanda-vagas-2026.pdf` — tabela de demanda e vagas por curso e
  sistema de ingresso. **É a origem dos números do explorador.**
- `2026_Boletim-informativo_VestUnB_v4.pdf` — boletim informativo do vestibular.
- `Guia-do-Vestibular-2026_Tradicional.pdf` — guia do Vestibular Tradicional.

Em caso de divergência, valem os editais e a página oficial de acompanhamento do
vestibular, não os números reproduzidos aqui.

## Estado atual

Os dados do explorador de 2026 estão embutidos no próprio HTML, no vetor
`CURSOS`. A extração a partir do PDF ainda não está versionada — `codigo/` está
vazio. Enquanto isso não for resolvido, o dataset não é reproduzível a partir do
que está no repositório, o que é o principal ponto em aberto para a edição de
2027.

## Licença

Liberado em domínio público sob a [The Unlicense](LICENSE). Use, copie,
modifique e redistribua à vontade, sem precisar pedir.

## Aviso

Projeto independente, sem vínculo com a Universidade de Brasília ou com o
Cebraspe. Os dados são reproduzidos a partir de documentos públicos e podem
conter erros de extração.
