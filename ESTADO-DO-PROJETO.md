# ESTADO DO PROJETO — Radar Extrajudicial

> **Documento de handoff e memória.** Ler inteiro antes de qualquer trabalho.
> **Regra permanente:** toda alteração, decisão ou pendência nova deve ser
> registrada aqui **no mesmo trabalho em que ocorrer**, antes do commit —
> atualize as seções afetadas e acrescente uma linha ao *Histórico*.
> Um documento desatualizado é pior que nenhum.

Última atualização: 2026-09-18

---

## 1. Contexto em uma tela

- **Usuário:** estuda para concursos de outorga de delegação de serventias
  extrajudiciais (cartório). Produz cadernos próprios de revisão e pede ao
  Claude relatórios HTML de jurisprudência ("Radar Extrajudicial") por órgão e
  período — STF, STJ, CNJ, Kollemata (informativo só de notarial e registral).
  Objetivo: máxima cobertura temporal, quantitativa e qualitativa, sempre
  atualizada.
- **O que existe:** um site estático que indexa esses relatórios, mostra o
  progresso de revisão de cada um e um mapa de lacunas de cobertura.
- **Publicado em:** https://mottagomesph.github.io/radar/ (GitHub Pages,
  ramo `main`, raiz). Repositório público: https://github.com/mottagomesph/radar
- **Pasta local (repositório git):**
  `C:\Users\motta\OneDrive - Tribunal de Justica de Sao Paulo\Cadernos pt. II\Informativos\Radar`
  — está dentro do OneDrive (risco conhecido: sincronização sobre `.git`).
- **Raiz `Informativos\`:** guarda os arquivos originais, com nomes antigos,
  como backup. Não são mais a fonte. Ignorar a pasta `Arquivo\`.
- **Vocabulário do usuário:** quando ele diz **"ficha"** no contexto do site,
  quer dizer **uma entrada do índice, isto é, um relatório** — confirmado por
  ele. "Ficha" *dentro* de um relatório é um julgado individual; o site não
  edita julgados.

## 2. Tarefa recorrente: acrescentar relatório ("nova ficha")

O usuário vai pedir, com frequência, que novas fichas/relatórios sejam
acrescentados. **Fazer de forma prática e completa, sem perguntar o óbvio.**
Dois casos:

**A. Ele já pôs o arquivo em `Radar/relatorios/`** (ou na raiz `Informativos\`):
1. localizar o arquivo; se estiver fora, copiar para `Radar/relatorios/<slug>.html`
   (slug minúsculo, sem espaços nem acentos: `stj-2025-t1`, `stf-2026-s2`,
   `cnj-2026-jan-ago`, `kollemata-2026-002`);
2. ler o bloco `<script type="application/json" id="radar-meta">`, se houver;
   senão, extrair título, órgão, período (`inicio`/`fim` = recorte do
   relatório, **não** datas de julgados citados), fonte e nº de fichas;
3. **conferir o nº de fichas na página montada** (servidor local + navegador:
   `document.querySelectorAll('.ficha').length`) — as fichas são desenhadas
   por script; o código-fonte não serve para contar;
4. testar o farol: marcar uma ficha e verificar `localStorage['radar:progresso:<slug>']`;
5. acrescentar a entrada em `reports.json` (campos da seção 4; `descricao` vem
   do `<meta name="description">`), agrupada por órgão;
6. rodar `python ferramentas/injetar-farol.py` (a partir de `Radar/`) —
   regenera `dados/reports.js` e injeta farol só nos relatórios que não têm
   bloco próprio;
7. conferir no índice (`http://localhost:8765`): cartão, link, matriz de
   cobertura, lacunas; console sem erros;
8. atualizar **este documento** (seções 5 e 8);
9. commit (mensagem em português, explicando o porquê) e `git push`;
10. aguardar ~1 min e confirmar que `https://mottagomesph.github.io/radar/relatorios/<slug>.html` responde 200.

**B. Ele pede para gerar o relatório:** produzir conforme o prompt dele e
conforme `instrucoes-para-novos-relatorios.md`, gravar direto em
`Radar/relatorios/<slug>.html` e seguir os passos 3 a 10.

Servidor local: `.claude/launch.json` na raiz `Informativos\` define o
servidor `radar` (`python -m http.server 8765 --directory Radar`); usar
`preview_start` com nome `radar`.

## 3. Arquitetura

```
Radar/
  index.html                       índice (abas Acervo, Cobertura, Registro)
  reports.json                     registro — FONTE DA VERDADE
  dados/reports.js                 espelho gerado (só para file://); não editar
  relatorios/*.html                relatórios autocontidos
  ferramentas/injetar-farol.py     injeta metadados+farol; gera o espelho
  instrucoes-para-novos-relatorios.md   contrato para colar no prompt de geração
  README.md                        documentação de uso
  ESTADO-DO-PROJETO.md             este arquivo
```

- **Sem build, sem dependências.** Só Google Fonts como externo.
- **Leitura do registro:** servido por HTTP, o índice faz `fetch('reports.json')`;
  em `file://` cai no espelho `dados/reports.js` (`window.RADAR`).
- **Progresso (o "farol"):** cada relatório tem sua própria marcação de fichas
  conferidas, com chaves e formatos distintos — **não mexer nelas**. O farol é
  um script de ~20 linhas no fim de cada relatório que conta no DOM
  `.ficha` (total) e `.ficha.done, .feita, .feito, .is-done, .conferida,
  [data-done='true']` (feitas) e grava
  `localStorage['radar:progresso:<slug>'] = {feitas,total,visto}`. O índice só lê.
  Funciona porque índice e relatórios têm a **mesma origem**.
- **Situação do relatório:** derivada do progresso (não revisado / em revisão /
  revisado); sobreposição manual em `radar:situacao:<slug>`
  (`auto|revisado|rever|nao-iniciado`).
- **Aba Registro:** acrescenta (analisa o arquivo num iframe oculto, marca
  campos como *lido* ou *deduzido*), edita e remove entradas. Mudanças vão para
  uma cópia de trabalho em `localStorage['radar:registro-pendente']` e o passo 3
  entrega o **`reports.json` inteiro** para colar por cima no GitHub (site
  estático não escreve no repositório). Avisa se o slug não corresponder a
  arquivo existente. Botão *Procurar no GitHub* usa a API pública
  (`reports.json` → `github: {usuario: mottagomesph, repo: radar, ramo: main}`).
- **Aba Cobertura:** matriz órgão × semestre, de `min(2024, ano do relatório
  mais antigo)` até o semestre corrente — cresce sozinha com o calendário.
  Células: meses cobertos/6. Lista "o que ainda falta pedir" gerada disso.
  Relatórios `tipo: normativo` ficam fora da matriz.
- **Outros:** exportar/importar progresso em JSON (↓/↑ progresso), tema
  claro/escuro, busca, filtros por órgão e situação; no celular a barra de
  controles deixa de ser fixa.

## 4. Contratos e convenções

- **Entrada de `reports.json`:** `slug, arquivo (relatorios/<slug>.html),
  titulo, orgao (STF|STJ|CNJ|Kollemata), tipo (jurisprudencia|normativo),
  inicio (AAAA-MM), fim (AAAA-MM), periodo (por extenso), fonte, fichas,
  produzido (AAAA-MM-DD), descricao`. Topo do arquivo: `atualizado, github,
  orgaos, relatorios`.
- **Relatório novo** deve seguir `instrucoes-para-novos-relatorios.md`: bloco
  `radar-meta` + farol embutido + classe `ficha` + marca de conferida + nome
  `<slug>.html`. Assim nasce autorregistrável e com progresso funcionando.
- **Injetor** (`injetar-farol.py`): idempotente; envolve o que injeta em
  `<!-- radar:inicio -->…<!-- radar:fim -->`; **pula** arquivos que já têm
  `id="radar-meta"` próprio.
- **Commits:** mensagens em português, corpo explicando o porquê, rodapé
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`. **Usar a identidade
  git global do usuário** (`mottagomesph` /
  `85656706+mottagomesph@users.noreply.github.com`) — **nunca** sobrescrever
  com `-c user.name/-c user.email`. Ver pendência P1.
- **Redação dos relatórios** (prompt do usuário): identificação
  `(REsp n. 1796394, rel. min. nome em minúsculas, T3, j. DD/MM/AAAA, Informativo n. X)`;
  "Lei n. NNNN/AAAA"; artigos acima de mil sem ponto; LRP; CNN/CN/CNJ;
  "serventias" em vez de "cartórios"; especialidades por extenso.

## 5. Acervo atual (10 relatórios, 264 fichas)

| slug | órgão | recorte | fonte | fichas |
|---|---|---|---|---|
| stf-2025-s1 | STF | 2025-01 → 2025-06 | Inf. 1163–1182 | 39 |
| stf-2025-s2 | STF | 2025-07 → 2025-12 | Inf. 1183–1202 | 45 |
| stf-2026-s1 | STF | 2026-01 → 2026-06 | Inf. 1203–1222 | 42 |
| stj-2025-t4 | STJ | 2025-10 → 2025-12 | Inf. 865–874 | 33 |
| stj-2026-inf-898-899 | STJ | 2026-08 → 2026-09 | Inf. 898–899 | 21 |
| cnj-2025-s1 | CNJ | 2025-01 → 2025-06 | Inf. 1/2025–9/2025 | 9 |
| cnj-2025-s2 | CNJ | 2025-07 → 2025-12 | Inf. 10–17/2025 | 25 |
| cnj-2026-jan-ago | CNJ | 2026-01 → 2026-08 | Inf. 01–11/2026 | 22 |
| kollemata-2026-001 | Kollemata | 2026-08 | n. 001 | 28 |
| cnj-res-696-2026 | CNJ (normativo) | — | Res. 696/2026 | 0 |

Só `cnj-2025-s1` nasceu conforme a especificação; os demais têm farol injetado.

**Lacunas (o que pedir em seguida):**
- **STJ — a mais grave:** 2024 inteiro, 2025·S1, 3º trimestre de 2025
  (jul–set), 2026·S1, julho de 2026.
- **STF:** 2024 inteiro, 2026·S2.
- **CNJ:** 2024 inteiro, set–dez de 2026.
- **Kollemata:** só o n. 001 (ago/2026); números seguintes.

## 6. Decisões tomadas (não reabrir sem motivo)

- GitHub Pages, repositório **público** (usuário aceitou).
- Progresso anterior (aberto por `file://`) foi **zerado** na migração (aceito).
- Arquivos **renomeados** para slugs (autorizado); originais ficam na raiz.
- **Não reescrever** a lógica de marcação dos relatórios; o farol só observa.
- Relatórios continuam **autocontidos** (sem JS compartilhado externo).
- Sem token do GitHub na página e sem backend: gravação por colagem do
  `reports.json` inteiro, ou por commit feito pelo Claude.
- Rascunhos avulsos foram substituídos por uma **cópia de trabalho** única do
  registro.
- Dedução de período por **concentração de datas** (anos dominantes + meses
  frequentes), não por mínimo/máximo — precedentes antigos distorciam.
- Edição de julgados dentro dos relatórios: **fora do escopo** (usuário
  confirmou que "ficha" = entrada do índice).

## 7. Armadilhas conhecidas

- `file://` quebra `localStorage` compartilhado, `fetch` e a análise da aba
  Registro — testar sempre por HTTP.
- Após push, o Pages leva ~50 s para refletir; antes disso, arquivo novo dá 404
  (e a aba Registro diz "não encontrei").
- Console do Windows mostra acentos como `�`; os arquivos estão em UTF-8.
- Heredoc em Bash falhou com HTML grande: usar a ferramenta Write.
- `input type="month"` exibe o mês no idioma do navegador (cosmético).

## 8. Pendências

- **P1 — privacidade no histórico git (decisão do usuário).** Os commits
  `92010bc` a `f8b6dfd` foram feitos com a autoria `Pedro Motta
  <[e-mail pessoal]>`, sobrescrevendo a identidade global. O nome foi
  inventado pelo Claude e o Gmail pessoal ficou exposto no repositório
  público. Correção possível: reescrever a autoria dos commits e fazer
  force-push. É destrutivo, então só com autorização explícita do usuário.
  Commits futuros já usam a identidade global.
- **P2 — GitHub Action** (oferecida, aguardando o usuário): ao entrar arquivo
  novo em `relatorios/`, ler o `radar-meta`, atualizar `reports.json` e
  commitar sozinha.
- **P3 — preencher lacunas** da seção 5, conforme pedidos do usuário.
- Ideia futura (não pedida): por volta de 2032, agrupar semestres antigos por
  ano na matriz.

## 9. Histórico

- **2026-09-17** — Criado o site: índice (acervo, progresso, cobertura),
  farol, `reports.json`, injetor, README. Repositório git em `Radar/`.
- **2026-09-17** — Aba Inserir (análise do arquivo num iframe, campos lidos
  ou deduzidos); índice passa a ler `reports.json` direto por HTTP; injetor
  idempotente de verdade.
- **2026-09-17** — Aba Registro com acrescentar/editar/remover, cópia de
  trabalho e saída do `reports.json` inteiro;
  `instrucoes-para-novos-relatorios.md` criado.
- **2026-09-17** — Publicado em `mottagomesph/radar`; chave `github`
  preenchida; Pages ativo.
- **2026-09-17** — Cobertura recua para anos anteriores a 2024 quando houver
  relatório; aviso de slug sem arquivo correspondente.
- **2026-09-18** — Acrescentado `cnj-2025-s1` (primeiro conforme a
  especificação); injetor passa a pular relatórios com metadados próprios.
- **2026-09-18** — Criado este documento. Identificado o problema de autoria
  dos commits (P1).
