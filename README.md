<!-- Estrutura baseada no Best-README-Template (othneildrew), adaptada a um
     repositório público de dados, sem código de execução e com produto
     publicado no GitHub Pages. -->
<a id="readme-top"></a>

[![Unlicense][licenca-shield]](#licença-e-uso-do-material)
[![GitHub Pages][pages-shield]][pages-url]
[![HTML][html-shield]][html-url]
[![Cursos][cursos-shield]](#os-dados)



<!-- CABEÇALHO -->
<br />
<div align="center">

  <img src="images/repo-readme-image.png" alt="Vestibular UnB — vagas, demanda e cursos, dados em app HTML" width="100%">

  <h3 align="center">vests-unb</h3>

  <p align="center">
    Dados públicos do Vestibular da Universidade de Brasília,
    <br />
    transformados em aplicativos HTML que qualquer candidato abre no navegador.
    <br />
    <br />
    <a href="https://ernybsb.github.io/vests-unb/produtos/2026/explorador-concorrencia-unb-2026.html"><strong>Abrir o explorador de concorrência 2026 »</strong></a>
    <br />
    <br />
    <a href="#os-dados">Os dados</a>
    &middot;
    <a href="sources/2026/">Documentos-fonte</a>
    &middot;
    <a href="#roadmap">Roadmap</a>
  </p>
</div>



<!-- SUMÁRIO -->
<details>
  <summary>Sumário</summary>
  <ol>
    <li>
      <a href="#sobre-o-projeto">Sobre o projeto</a>
      <ul>
        <li><a href="#estado-atual">Estado atual</a></li>
        <li><a href="#construído-com">Construído com</a></li>
      </ul>
    </li>
    <li>
      <a href="#começando">Começando</a>
      <ul>
        <li><a href="#pré-requisitos">Pré-requisitos</a></li>
        <li><a href="#instalação">Instalação</a></li>
      </ul>
    </li>
    <li>
      <a href="#uso">Uso</a>
      <ul>
        <li><a href="#rodar-a-extração">Rodar a extração</a></li>
        <li><a href="#explorar-a-concorrência-de-2026">Explorar a concorrência de 2026</a></li>
      </ul>
    </li>
    <li><a href="#estrutura-do-repositório">Estrutura do repositório</a></li>
    <li><a href="#os-dados">Os dados</a></li>
    <li>
      <a href="#modelo-de-dados">Modelo de dados</a>
      <ul>
        <li><a href="#por-que-a-escala-logarítmica">Por que a escala logarítmica</a></li>
        <li><a href="#decisões-que-valem-conhecer">Decisões que valem conhecer</a></li>
      </ul>
    </li>
    <li><a href="#integridade-do-dado-fonte">Integridade do dado-fonte</a></li>
    <li><a href="#por-que-file-precisa-de-rede">Por que <code>file://</code> precisa de rede</a></li>
    <li><a href="#publicação">Publicação</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contribuindo">Contribuindo</a></li>
    <li><a href="#licença-e-uso-do-material">Licença e uso do material</a></li>
    <li><a href="#contato">Contato</a></li>
    <li><a href="#referências-e-créditos">Referências e créditos</a></li>
  </ol>
</details>



<!-- SOBRE O PROJETO -->
<a id="sobre-o-projeto"></a>
## Sobre o projeto

A UnB publica, antes de cada vestibular, a tabela de demanda por vaga. É informação
decisiva para quem ainda está escolhendo o curso — e chega em PDF, dezenas de páginas de
números miúdos, impossível de ordenar, filtrar ou comparar.

Este repositório pega esses documentos oficiais e devolve o mesmo conteúdo como
**aplicativo HTML de página única**: ordenável, filtrável, com o detalhe da concorrência
em cada sistema de ingresso a um clique. Sem instalação, sem servidor, sem cadastro.

O material é produzido em **Software Livre** (The Unlicense, domínio público) e está
disponível para ajudar pessoas interessadas no ingresso nessa universidade, que também
foi minha universidade por muitos anos.

A pergunta que o produto responde não é só «qual curso é mais concorrido». É
**«concorrido para quem»** — a demanda no sistema Universal e a demanda numa faixa de
cota podem diferir por uma ordem de grandeza no mesmo curso, e é essa diferença que muda
a decisão de quem se inscreve.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<a id="estado-atual"></a>
### Estado atual

**Todo dado publicado aqui é reproduzível a partir do repositório.** Os dois PDFs de
origem têm extração versionada em `codigo/`, e cada script confere o próprio resultado
contra os totais que o documento oficial imprime.

O que já existe:

* **Explorador de concorrência 2026** — 99 cursos/turnos, 11 sistemas de ingresso,
  publicado no GitHub Pages;
* os **documentos oficiais** que originaram os dados, preservados como recebidos;
* **extração da tabela de demanda de 2026** — os 99 cursos em JSON, com todos os valores
  conferidos contra o que o explorador publica hoje;
* **extração do Anexo I do edital de 2027** — 105 cursos, conferida contra os totais
  impressos no próprio edital;
* publicação automática: todo push em `main` redeploya o site.

O que ainda não existe:

| Referência | Situação |
|---|---|
| demanda de 2027 | só sai depois de encerradas as inscrições; o Anexo I traz vagas, não inscritos |
| nota de corte por sistema | não consta na tabela de demanda; exigiria outra fonte |
| edições anteriores a 2026 | a estrutura por ano comporta, nada foi modelado ainda |

> [!NOTE]
> O explorador **lê** `dados/2026/demanda-2026.json` desde a versão atual. O vetor
> embutido saiu do HTML, que encolheu de 118 KB para 16 KB. Como efeito colateral, seis
> cursos passaram a exibir o nome oficial completo em vez da abreviação que estava no
> código — «Música (Bacharelado)*» com o asterisco que marca exigência de habilidade
> específica, «Ciências Sociais» com as três habilitações, e as Engenharias do Gama com
> as cinco.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<a id="construído-com"></a>
### Construído com

O produto é um arquivo HTML único, sem build e sem dependências instaláveis. As
bibliotecas entram por CDN, em tempo de carregamento da página.

* [![HTML][html-shield]][html-url] — página única, sem build; os dados vêm de `dados/`
* **JavaScript sem framework** — a lista, os filtros, as escalas log/linear e o gráfico
  de barras do painel de detalhe, tudo à mão
* **SVG inline** — o gráfico, com `viewBox`, sem redesenhar no `resize`
* **Tipografia do sistema** — pilhas de fallback, nenhuma fonte baixada
* [![GitHub Pages][pages-shield]][pages-url] — publicação a partir de `main`, na raiz

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- COMEÇANDO -->
<a id="começando"></a>
## Começando

<a id="pré-requisitos"></a>
### Pré-requisitos

Para **usar** os produtos:

* Um **navegador** moderno.
* **Conexão com a internet apenas para os dados.** O explorador não busca nada de
  terceiros: sem bibliotecas de CDN, sem fontes externas. Só o
  `dados/2026/demanda-2026.json`.

  Onde ele busca esse arquivo depende de como a página foi aberta:

  | Aberta assim | O dado vem de | Precisa de rede? |
  |---|---|---|
  | servida por HTTP — Pages ou servidor local | `dados/` do próprio clone | não, se o servidor for local |
  | por `file://`, com duplo clique | a cópia publicada no GitHub Pages | **sim** |

  **Abrir por `file://` exige rede**, portanto, e é assim de propósito — ver
  [Por que `file://` precisa de rede](#por-que-file-precisa-de-rede). Para uso realmente
  offline, sirva a pasta por HTTP.

Para **rodar a extração** em `codigo/`:

* **Python 3.10+**, sem nenhuma dependência de terceiros — só a biblioteca padrão.
  ```sh
  python3 --version
  ```
* **`pdftotext`**, do poppler-utils — é ele que lê o PDF.
  ```sh
  sudo apt-get install poppler-utils   # Debian/Ubuntu
  pdftotext -v
  ```

Não há ambiente virtual, `make`, nem arquivo de dependências: se `python3` e `pdftotext`
respondem, está pronto.

<a id="instalação"></a>
### Instalação

Para só **usar**, não instale nada: abra
[o explorador publicado](https://ernybsb.github.io/vests-unb/produtos/2026/explorador-concorrencia-unb-2026.html).

Para trabalhar no repositório:

1. Clone
   ```sh
   git clone https://github.com/ErnyBSB/vests-unb.git
   cd vests-unb
   ```
2. Abra o produto direto do disco — o `file://` funciona, sem precisar de servidor
   ```sh
   xdg-open produtos/2026/explorador-concorrencia-unb-2026.html
   ```
   Nesse modo os dados vêm da **cópia publicada**, não do seu clone, e portanto **é
   preciso estar com rede** — o app avisa disso no rodapé, e a razão está em
   [Por que `file://` precisa de rede](#por-que-file-precisa-de-rede). Para ver o JSON
   **do clone**, ou para trabalhar offline, sirva a pasta por HTTP:
   ```sh
   python3 -m http.server 8000
   xdg-open http://localhost:8000/produtos/2026/explorador-concorrencia-unb-2026.html
   ```
3. Confira que os documentos-fonte vieram inteiros
   ```sh
   ls -l sources/2026/
   ```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- USO -->
<a id="uso"></a>
## Uso

<a id="rodar-a-extração"></a>
### Rodar a extração

São dois scripts, um por documento de origem. Nenhum dos dois aceita argumento
implícito: o PDF de entrada e o arquivo de saída são sempre explícitos, para que ninguém
regenere o arquivo errado por engano.

**Tabela de demanda de 2026** — 99 cursos, com o detalhe de cada sistema de ingresso:

```sh
python3 codigo/extrai_demanda.py \
    sources/2026/tabela-demanda-vagas-2026.pdf \
    dados/2026/demanda-2026.json
```

```
dados/2026/demanda-2026.json: 99 cursos em 4 campi — totais conferem
```

**Anexo I do edital de 2027** — o quadro de vagas:

```sh
python3 codigo/extrai_anexo_i.py \
    sources/2027/edital_Unb_2027.pdf \
    dados/2027/anexo-i-quadro-de-vagas.md
```

```
dados/2027/anexo-i-quadro-de-vagas.md: 105 cursos em 6 seções — totais conferem
```

As duas extrações são **determinísticas**: rodar duas vezes sobre o mesmo PDF produz um
arquivo byte a byte idêntico — não há data de geração na saída, nem acesso à rede.
Confira por conta própria:

```sh
python3 codigo/extrai_anexo_i.py sources/2027/edital_Unb_2027.pdf /tmp/a.md
python3 codigo/extrai_anexo_i.py sources/2027/edital_Unb_2027.pdf /tmp/b.md
cmp /tmp/a.md /tmp/b.md && echo idênticos
```

> [!IMPORTANT]
> Os scripts **não confiam em si mesmos**. Os dois documentos publicam os próprios
> totais, e a extração é confrontada com eles: a soma dos sistemas tem de dar o total de
> cada curso, a soma dos cursos tem de dar o total do campus, e a soma dos campi tem de
> dar o total geral. Qualquer divergência **aborta a execução** em vez de gravar o
> arquivo — uma coluna trocada produz dado errado com aparência de dado certo, e esse é o
> erro que não se percebe lendo o resultado.

> [!WARNING]
> **A demanda não é `inscritos ÷ vagas`** e não é recalculada em lugar nenhum. A Obs² da
> tabela de 2026 diz que no cálculo «foram considerados todos os candidatos que concorrem
> às vagas do curso, independentemente de estarem ou não concorrendo prioritariamente a
> essas vagas». Daí uma faixa com 2 vagas e 32 inscritos aparecer com demanda 17,00. O
> número é reproduzido como publicado; recalculá-lo inventaria dado que a fonte não traz.

<a id="explorar-a-concorrência-de-2026"></a>
### Explorar a concorrência de 2026

O explorador tem quatro controles, todos combináveis:

| Controle | O que faz |
|---|---|
| **Busca** | filtra por nome do curso, ignorando acento e maiúscula (`musica` acha «Música») |
| **Ordenação** | demanda ↓ ou ↑, inscritos ↓, vagas ↓, ou alfabética |
| **Chips** | ligam e desligam campi (Darcy Ribeiro, Ceilândia, Gama, Planaltina) e turnos |
| **Escala log** | alterna a escala das barras entre logarítmica e linear |

Os quatro indicadores do topo — cursos exibidos, inscritos, vagas e demanda média — são
recalculados sobre **o recorte visível**, não sobre o total. Filtrar por Planaltina e ler
a «demanda média» dá a demanda média de Planaltina.

Clicar numa linha abre o painel de detalhe: vagas, inscritos e demanda do curso, mais um
gráfico de barras com a concorrência em **cada sistema de ingresso**, colorido por
natureza do sistema — azul para o Universal, vinho para as cotas raciais e trans, verde
para as faixas de escola pública.

Extrair os dados para trabalhar em outra ferramenta, enquanto não há `.json` publicado:

```sh
python3 - <<'PY'
import re, json
html = open('produtos/2026/explorador-concorrencia-unb-2026.html', encoding='utf-8').read()
cursos = json.loads(re.search(r'const CURSOS = (\[.*?\]);', html, re.S).group(1))

print(len(cursos))                                    # 99
print(sum(c['vagas'] for c in cursos))                # 2102
print(sorted(cursos, key=lambda c: -c['demanda'])[0]) # Medicina
PY
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- ESTRUTURA -->
<a id="estrutura-do-repositório"></a>
## Estrutura do repositório

```
sources/<ano>/            Documentos oficiais em PDF — a fonte primária, preservada
                          exatamente como publicada pelo Cebraspe/UnB
  2026/
    tabela-demanda-vagas-2026.pdf           Demanda e vagas por curso e sistema
    2026_Boletim-informativo_VestUnB_v4.pdf Boletim informativo do vestibular
    Guia-do-Vestibular-2026_Tradicional.pdf Guia do Vestibular Tradicional
  2027/
    edital_Unb_2027.pdf                     Edital nº 1 – Vestibular 2027
codigo/                   Os scripts de extração
    extrai_demanda.py                       Tabela de demanda → JSON
    extrai_anexo_i.py                       Anexo I do edital → Markdown
dados/<ano>/              Dado derivado, gerado por script — nunca editado à mão
  2026/
    demanda-2026.json                       Demanda e vagas, 99 cursos
  2027/
    anexo-i-quadro-de-vagas.md              Quadro de vagas, 105 cursos
produtos/<ano>/           Os aplicativos HTML gerados, um por edição
  2026/
    explorador-concorrencia-unb-2026.html   Explorador de concorrência
images/                   Imagens do repositório
LICENSE                   The Unlicense — domínio público
```

A organização **por ano** é proposital: cada edição do vestibular entra como um diretório
novo, e o produto de uma edição passada continua abrindo exatamente como estava, com os
números daquele ano. Nada é sobrescrito de uma edição para a outra.

Os quatro diretórios de primeiro nível têm papéis que não se misturam:

| Diretório | Papel | Quem produz |
|---|---|---|
| `sources/` | documentos oficiais, intocados | a banca |
| `codigo/` | a extração | este repositório |
| `dados/` | dado derivado, regenerável | o script |
| `produtos/` | os aplicativos HTML | este repositório |

A fronteira que importa: **apagar `dados/` não deve perder nada** — basta rodar o script
de novo sobre o PDF em `sources/`. Se um dia isso deixar de ser verdade, é sinal de que
alguém editou dado derivado à mão.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- OS DADOS -->
<a id="os-dados"></a>
## Os dados

Vestibular Tradicional da UnB, edição **2026**, a partir da
[tabela de demanda e vagas][tabela-oficial] publicada pelo Cebraspe em dezembro de 2025 —
portanto **inscrições encerradas**, números definitivos, antes da aplicação da prova.
A mesma tabela está preservada aqui em
[`sources/2026/tabela-demanda-vagas-2026.pdf`](sources/2026/tabela-demanda-vagas-2026.pdf).

| | |
|---|---|
| Cursos/turnos | 99 |
| Vagas | 2.102 |
| Inscritos | 16.823 |
| Demanda média geral | 8,00 candidatos/vaga |
| Campi | 4 |
| Sistemas de ingresso | 11 |
| Grupos de prova | 2 (I: 56 cursos · II: 43) |
| Turnos | Diurno: 69 · Noturno: 30 |

Por campus:

| Campus | Cursos/turnos | Vagas | Inscritos | Demanda |
|---|---:|---:|---:|---:|
| Darcy Ribeiro | 88 | 1.729 | 15.397 | 8,91 |
| Ceilândia | 6 | 148 | 749 | 5,06 |
| Gama | 1 | 140 | 637 | 4,55 |
| Planaltina | 4 | 85 | 40 | 0,47 |

Os extremos, que é onde a informação costuma estar:

* **Medicina** — 208,95 candidatos por vaga, cinco vezes o segundo colocado;
* **Direito** diurno (41,40), **Psicologia** (40,56), **Ciência da Computação** (30,50);
* **18 cursos com demanda abaixo de 1** — mais vagas do que inscritos, sendo o menor
  Letras Tradução Espanhol, com 0,07.

Os 11 sistemas de ingresso: **Universal**, **Cotas para Pessoas Negras**, **Cotas Trans**
e as oito faixas de escola pública, cruzando renda (≤1 salário mínimo e >1), condição
PPI ou não-PPI, e vagas gerais ou de pessoa com deficiência.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- MODELO DE DADOS -->
<a id="modelo-de-dados"></a>
## Modelo de dados

`dados/2026/demanda-2026.json` traz um bloco `fonte`, com a procedência e o sha256 do
PDF, e um vetor `cursos` com um registro por **curso/turno** — a mesma graduação em dois
turnos são dois registros, porque concorrem separadamente:

```json
{
  "grupo": "I",
  "curso": "Administração (Bacharelado)",
  "campus": "Darcy Ribeiro",
  "turno": "Diurno",
  "vagas": 30,
  "inscritos": 172,
  "demanda": 5.73,
  "sistemas": [
    { "sistema": "Universal", "vagas": 12, "inscritos": 172, "demanda": 14.33 },
    { "sistema": "Cotas Negras", "vagas": 2, "inscritos": 13, "demanda": 6.5 }
  ]
}
```

> [!WARNING]
> **Não some os `inscritos` dos sistemas para chegar ao total do curso.** Todo candidato
> concorre no **Universal** *e* no sistema que reivindicou; o `inscritos` do Universal é,
> por isso, igual ao total do curso. Somar a coluna conta cada candidato duas vezes. O
> `inscritos` do nível do curso é o número correto.

<a id="por-que-a-escala-logarítmica"></a>
### Por que a escala logarítmica

A distribuição da demanda vai de 0,07 a 208,95 — quase quatro ordens de grandeza. Numa
escala linear, Medicina consome a largura inteira e os outros 98 cursos viram traços
indistinguíveis contra a margem. A escala log é o padrão do explorador por isso, com
domínio fixo em `[0.07, máximo]` e `clamp`, para que o eixo não se mexa quando os filtros
mudam e a comparação visual entre dois recortes continue válida.

<a id="decisões-que-valem-conhecer"></a>
### Decisões que valem conhecer

* **A unidade é o curso/turno, não o curso.** Direito diurno (41,40) e Direito noturno
  (25,67) são seleções distintas; fundi-los produziria um número que não corresponde a
  nenhuma decisão real de candidato.
* **A demanda por sistema é o que importa**, e é justamente o que o PDF esconde. A média
  do curso pode mascarar uma faixa vazia e outra saturada.
* **Sistemas sem vaga e sem inscrito são omitidos** do gráfico de detalhe: nem todo curso
  oferta todas as faixas, e barras zeradas só ocupariam espaço.
* **Nada é arredondado na origem.** A demanda vem da fonte com duas casas; a formatação
  em vírgula é só de exibição.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- INTEGRIDADE -->
<a id="integridade-do-dado-fonte"></a>
## Integridade do dado-fonte

Os PDFs em `sources/` **não são gerados aqui** — são baixados do Cebraspe/UnB e
preservados como vieram.

Cada documento tem, por isso, dois endereços com papéis distintos: a **origem oficial**,
que prova de onde o dado veio, e a **cópia preservada**, que prova o que foi efetivamente
usado e continua acessível se o CDN mudar de endereço entre edições — provável, já que o
nome do arquivo é um hash opaco.

| | |
|---|---|
| Origem oficial | [tabela de demanda e vagas do Vestibular 2026][tabela-oficial] (Cebraspe) |
| Cópia preservada | [`sources/2026/tabela-demanda-vagas-2026.pdf`](sources/2026/tabela-demanda-vagas-2026.pdf) |
| sha256 (idêntico nos dois) | `e4768cf4d360ad4a888f54d089785995994c56460f729fb6b137aa7b087c5654` |
| Conferido em | 26/08/2026 — `HTTP 200`, `application/pdf`, 516.051 bytes |

Conferir por conta própria:

```sh
curl -sL 'https://cdn.cebraspe.org.br/vestibulares/VESTUNB_26/arquivos/5E209CC58A5EAAE1E5E3CA2DFBB183EFFF3FF411D513947550BF7A77D8393426.pdf' | sha256sum
sha256sum sources/2026/tabela-demanda-vagas-2026.pdf
```

Os dois comandos devem devolver o mesmo hash. É isso que sustenta a afirmação de que a
cópia deste repositório **é** o documento oficial, e não uma versão parecida dele.

Duas regras seguem daí:

1. **Não edite, não reexporte, não otimize os PDFs.** Eles são o único registro do que a
   banca publicou, e são o que permite conferir qualquer número do explorador. Um PDF
   reprocessado deixa de servir a essa função sem que nada pareça errado.
2. **Em caso de divergência, o oficial vence.** Os editais e a página de acompanhamento
   do vestibular são a norma — não os números reproduzidos aqui, que passaram por uma
   extração e podem conter erro.

O explorador é uma **leitura** dos documentos oficiais, não uma fonte independente. Quem
for tomar decisão de inscrição deve conferir no edital.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- FILE:// -->
<a id="por-que-file-precisa-de-rede"></a>
## Por que `file://` precisa de rede

O explorador não carrega biblioteca nem fonte de terceiros — só o próprio JSON. Mesmo
assim, aberto com duplo clique ele busca esse JSON na **cópia publicada**, e portanto
precisa de rede. Isso é uma decisão, não uma pendência.

O navegador bloqueia `fetch` de caminho relativo na origem `file://`. Restam duas saídas,
e a escolhida foi a segunda:

| | O que faria | Por que não |
|---|---|---|
| **Embutir um instantâneo dos dados no HTML** | funcionaria offline em qualquer modo | o dado voltaria a viver duplicado no repositório, o HTML iria de 21 KB a ~117 KB, e `produtos/` deixaria de ser editável à mão. Trocar um número produziria diff de 96 KB |
| **Buscar da cópia publicada, avisando** | é o que o app faz | `file://` exige rede — e o rodapé diz, num aviso, que os dados não vieram do seu clone |

Uma terceira ideia aparece naturalmente e é pior que as duas: usar um instantâneo
embutido como último recurso, depois de tentar as outras origens. Funcionaria offline
**com dado possivelmente velho e ninguém sabendo**, porque o instantâneo envelheceria em
silêncio a cada nova extração. É o mesmo princípio que rege os extratores em `codigo/`:
**falhar visivelmente é melhor que acertar por acaso**.

Para uso offline de verdade, sirva a pasta por HTTP — um comando, descrito em
[Instalação](#instalação).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- PUBLICAÇÃO -->
<a id="publicação"></a>
## Publicação

O site é servido pelo **GitHub Pages** a partir de `main`, na raiz, com o build clássico
do Jekyll — é ele que transforma este README na página inicial. Todo push em `main`
redeploya automaticamente.

| | |
|---|---|
| Site | <https://ernybsb.github.io/vests-unb/> |
| Explorador 2026 | <https://ernybsb.github.io/vests-unb/produtos/2026/explorador-concorrencia-unb-2026.html> |

O HTML do explorador não usa a sintaxe de template do Liquid — chaves duplas ou
chaves-porcento —, então o Jekyll não interfere no JavaScript. Um produto futuro que use
essa sintaxe precisará ser protegido, ou o Jekyll desligado com um `.nojekyll`, ao custo
de o README deixar de virar página inicial.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- ROADMAP -->
<a id="roadmap"></a>
## Roadmap

- [x] Documentos oficiais de 2026 preservados em `sources/`
- [x] Explorador de concorrência 2026 — 99 cursos, 11 sistemas de ingresso
- [x] Publicação no GitHub Pages
- [x] **Extração versionada em `codigo/`** — primeiro caso: Anexo I do edital de 2027
    - [x] Conferência automática dos totais extraídos contra os impressos no PDF
    - [x] Estender à tabela de demanda de 2026 — `dados/2026/demanda-2026.json`
- [x] Fazer o explorador **ler** `dados/2026/demanda-2026.json` em vez do vetor embutido
- [ ] Página inicial listando as edições disponíveis
- [ ] Séries históricas — a mesma leitura para edições anteriores, e a variação entre elas
- [ ] Comparador de cursos lado a lado
- [x] **Zero dependências de terceiros** — o explorador não busca nada fora do projeto
    - [x] Remover o D3, reescrevendo escalas e lista em JavaScript puro (−273 KB)
    - [x] Remover o ECharts, desenhando o gráfico de detalhe em SVG (−1.001 KB)
    - [x] Trocar as fontes do Google por pilhas do sistema (−475 KB)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- CONTRIBUINDO -->
<a id="contribuindo"></a>
## Contribuindo

Correções de dado são especialmente bem-vindas: se um número do explorador não bate com o
PDF oficial, abra uma *issue* apontando o curso, o sistema de ingresso e a página do PDF.

1. Crie sua branch a partir de `main`, no padrão `tipo/assunto-em-kebab-case`
   (`docs/`, `feat/`, `fix/`, `chore/`)
   ```sh
   git checkout main && git pull --ff-only
   git checkout -b feat/extracao-tabela-demanda
   ```
2. Faça as alterações e confira o produto no navegador antes de commitar
3. **Ao alterar o explorador, suba a versão no mesmo commit.** A constante fica no topo
   do `<script>` de
   [`explorador-concorrencia-unb-2026.html`](produtos/2026/explorador-concorrencia-unb-2026.html):
   ```js
   const APP = {versao:'2.03', quando:'ago/2026'};
   ```
   Versão que se esquece de subir é pior que versão nenhuma, porque passa a mentir para
   quem abre a página por um link antigo. O mês é **declarado**, nunca capturado do
   relógio — ver o aviso em [Uso](#rodar-a-extração) sobre determinismo.

   A constante `DADOS`, logo abaixo, é outro fato: a edição do vestibular e o mês da
   tabela que originou os números. Só muda quando o dado muda.
4. Commite em **Conventional Commits**, com título em inglês no imperativo e escopo por
   edição quando fizer sentido
   ```sh
   git commit -m 'feat(2026): extract demand table into versioned json'
   ```
5. Empurre a branch
   ```sh
   git push -u origin feat/extracao-tabela-demanda
   ```
6. Abra um *pull request* — nunca use force-push

Conteúdo, código, comentários e documentação em **português**; só as mensagens de commit
em inglês.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- LICENÇA -->
<a id="licença-e-uso-do-material"></a>
## Licença e uso do material

Liberado em **domínio público** sob a [The Unlicense](LICENSE). Copie, modifique,
publique, use, compile, venda ou distribua, para qualquer fim, sem precisar pedir e sem
precisar dar crédito.

Os PDFs em `sources/` são **documentos públicos** do Cebraspe e da Universidade de
Brasília, preservados aqui sem modificação. A licença deste repositório cobre o trabalho
de análise e o aplicativo, não os documentos originais.

Projeto independente, **sem vínculo** com a Universidade de Brasília ou com o Cebraspe.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- CONTATO -->
<a id="contato"></a>
## Contato

Erny Bo-D — [@ErnyBSB](https://github.com/ErnyBSB)

Link do projeto: [https://github.com/ErnyBSB/vests-unb](https://github.com/ErnyBSB/vests-unb)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- CRÉDITOS -->
<a id="referências-e-créditos"></a>
## Referências e créditos

* [Cebraspe](https://www.cebraspe.org.br) — organizador do Vestibular da UnB; os documentos-fonte
* [Universidade de Brasília](https://www.unb.br) — a instituição, e a página oficial de acompanhamento do vestibular
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — estrutura deste README

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>



<!-- LINKS E IMAGENS -->
[licenca-shield]: https://img.shields.io/badge/licen%C3%A7a-Unlicense-brightgreen?style=for-the-badge
[pages-shield]: https://img.shields.io/badge/GitHub%20Pages-no%20ar-222222?style=for-the-badge&logo=github&logoColor=white
[pages-url]: https://ernybsb.github.io/vests-unb/
[html-shield]: https://img.shields.io/badge/HTML5-p%C3%A1gina%20%C3%BAnica-E34F26?style=for-the-badge&logo=html5&logoColor=white
[html-url]: https://developer.mozilla.org/pt-BR/docs/Web/HTML
[cursos-shield]: https://img.shields.io/badge/2026-99%20cursos%20%C2%B7%202.102%20vagas-1F5673?style=for-the-badge
[tabela-oficial]: https://cdn.cebraspe.org.br/vestibulares/VESTUNB_26/arquivos/5E209CC58A5EAAE1E5E3CA2DFBB183EFFF3FF411D513947550BF7A77D8393426.pdf
