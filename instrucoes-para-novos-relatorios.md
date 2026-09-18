# Instruções para novos relatórios

Este arquivo é para ser **colado no prompt** que gera um relatório novo, como
seção final do bloco *Formato do produto final*. Ele descreve o contrato entre
o relatório e o índice do Radar Extrajudicial.

Cumprido o contrato, o relatório novo se registra quase sozinho: a aba
**Registro** do índice lê dele todos os campos, sem deduzir nada, e a barra de
progresso funciona desde a primeira abertura, sem rodar script nenhum.

O contrato não interfere no desenho do relatório. Paleta, tipografia,
estrutura das fichas e requisitos funcionais continuam livres, e o arquivo
continua autocontido — abre sozinho, offline.

---

## Texto a colar no prompt

> ## Integração com o índice Radar Extrajudicial
>
> A página deve atender ao contrato abaixo, que permite ao índice do acervo
> ler seus dados e acompanhar o progresso de revisão.
>
> ### 1. Bloco de metadados
>
> Inclua, imediatamente antes de `</body>`, um bloco de metadados no formato
> exato abaixo, preenchido com os dados deste relatório:
>
> ```html
> <script type="application/json" id="radar-meta">
> {
>   "slug": "stj-2025-t4",
>   "titulo": "Jurisprudência do STJ — 4º trimestre de 2025",
>   "orgao": "STJ",
>   "tipo": "jurisprudencia",
>   "inicio": "2025-10",
>   "fim": "2025-12",
>   "periodo": "4º trimestre de 2025",
>   "fonte": "Informativos 865 a 874",
>   "fichas": 33,
>   "produzido": "2026-09-17"
> }
> </script>
> ```
>
> Significado de cada campo:
>
> - `slug` — identificador curto, em minúsculas, sem espaços nem acentos, no
>   padrão `<órgão>-<período>`: `stj-2025-t4`, `stf-2026-s1`,
>   `cnj-2026-jan-ago`, `kollemata-2026-001`. É também o nome do arquivo;
> - `titulo` — título do relatório, para exibição no acervo;
> - `orgao` — `STF`, `STJ`, `CNJ` ou `Kollemata`;
> - `tipo` — `jurisprudencia` para relatórios de julgados; `normativo` para
>   apresentações de atos normativos, que não entram no mapa de cobertura;
> - `inicio` e `fim` — primeiro e último mês **do período coberto**, no
>   formato `AAAA-MM`. Não são as datas dos julgamentos citados, e sim o
>   recorte temporal do relatório. São eles que alimentam o mapa de cobertura
>   e a lista de lacunas, e por isso pedem precisão;
> - `periodo` — o mesmo recorte por extenso: `4º trimestre de 2025`,
>   `1º semestre de 2026`, `agosto de 2026`;
> - `fonte` — os informativos ou o ato de origem: `Informativos 865 a 874`;
> - `fichas` — número de fichas do relatório;
> - `produzido` — data de produção, no formato `AAAA-MM-DD`.
>
> ### 2. Marcação das fichas
>
> O índice conta as fichas pelo DOM. Para isso:
>
> - cada ficha deve ser um elemento com a classe `ficha`;
> - a ficha marcada como conferida deve receber, **nesse mesmo elemento**, uma
>   destas marcas: a classe `done`, `feita`, `feito`, `is-done` ou
>   `conferida`, ou o atributo `data-done="true"`.
>
> O mecanismo de persistência da marcação continua a critério da página: chave
> e formato próprios em `localStorage`, como preferir.
>
> ### 3. Farol de progresso
>
> Inclua, logo após o bloco de metadados, o script abaixo, **sem alterações**,
> trocando apenas o valor de `SLUG` pelo slug deste relatório. Ele observa o
> DOM e publica o resumo do progresso para o índice, sem interferir na
> marcação da própria página.
>
> ```html
> <script>
> /* Radar Extrajudicial - publica o progresso desta pagina para o indice. */
> (function(){
>   var SLUG = "stj-2025-t4";
>   var FICHA = ".ficha";
>   var FEITA = ".ficha.done,.ficha.feita,.ficha.feito,.ficha.is-done,.ficha.conferida,.ficha[data-done='true']";
>   var t;
>   function publicar(){
>     try{
>       var total = document.querySelectorAll(FICHA).length;
>       if(!total) return;
>       var feitas = document.querySelectorAll(FEITA).length;
>       localStorage.setItem("radar:progresso:" + SLUG, JSON.stringify({
>         feitas: feitas, total: total, visto: Date.now()
>       }));
>     }catch(e){}
>   }
>   function agendar(){ clearTimeout(t); t = setTimeout(publicar, 200); }
>   function iniciar(){
>     agendar();
>     try{
>       new MutationObserver(agendar).observe(document.body, {
>         subtree: true, childList: true,
>         attributes: true, attributeFilter: ["class", "data-done"]
>       });
>     }catch(e){}
>   }
>   if(document.readyState === "loading"){
>     document.addEventListener("DOMContentLoaded", iniciar);
>   } else { iniciar(); }
> })();
> </script>
> ```
>
> ### 4. Nome do arquivo
>
> Grave a versão standalone com o nome `<slug>.html` — o mesmo slug do bloco
> de metadados, em minúsculas, sem espaços nem acentos.
>
> ### 5. Cabeçalho
>
> Mantenha, no `<head>`, um `<title>` curto e um
> `<meta name="description" content="…">` com uma frase descrevendo o
> relatório. São aproveitados pelo índice quando o bloco de metadados falta.

---

## Por que assim

O índice não interpreta o conteúdo jurídico do relatório; ele só precisa saber
o recorte e conseguir contar fichas. O bloco de metadados responde à primeira
necessidade, e a classe `ficha` à segunda.

A contagem é feita no DOM, e não no código-fonte, porque os relatórios
desenham as fichas por script: um relatório recém-gerado tem zero ocorrências
de `class="ficha"` no arquivo e várias dezenas na página montada.

O farol existe para o índice não precisar abrir todos os relatórios para saber
o progresso de cada um — seriam mais de um megabyte a cada visita. Cada
relatório publica seu próprio resumo quando é aberto, e o índice apenas lê.

## Se um relatório antigo não cumprir o contrato

Ele aparece no acervo do mesmo jeito, e a aba Registro deduz o que puder do
texto — com os campos deduzidos marcados como tal, para conferência. O que se
perde é a barra de progresso, que fica parada em zero.

Para corrigir um relatório nessa situação, basta acrescentar a entrada dele em
`reports.json` e rodar, a partir da pasta `Radar`:

```
python ferramentas/injetar-farol.py
```

O script injeta em cada relatório registrado o bloco de metadados e o farol,
exatamente como descritos acima. É idempotente: rodar de novo não duplica nada.
