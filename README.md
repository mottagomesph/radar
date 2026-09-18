# Radar Extrajudicial

Índice dos relatórios de jurisprudência e atos normativos em direito notarial
e registral, para revisão periódica com vista aos concursos de outorga de
delegações de serventias extrajudiciais.

Site estático, sem build e sem dependências: basta servir a pasta.

## Estrutura

```
index.html              índice: acervo, progresso, cobertura e inserção
reports.json            registro dos relatórios (fonte da verdade)
dados/reports.js        espelho do registro, gerado; só usado no file://
relatorios/*.html       os relatórios, um arquivo autocontido cada
ferramentas/
  injetar-farol.py      injeta metadados e o farol de progresso nos relatórios
```

Servido por HTTP, o índice lê `reports.json` direto. `dados/reports.js` é um
espelho para o caso de abrir o `index.html` pelo disco, onde o navegador
bloqueia a leitura de JSON.

A chave `github` de `reports.json` — usuário, repositório e ramo — serve à aba
*Inserir*, para listar os arquivos de `relatorios/` que ainda não estão
registrados. Sem ela, o resto continua funcionando; só a listagem automática
fica indisponível.

## Como acrescentar um relatório, pela própria página

A aba **Inserir**, no índice, é o caminho mais curto. Ela só funciona com o
site servido por HTTP — publicado, ou pelo servidor local descrito no fim
deste arquivo.

1. envie o arquivo para `relatorios/` (pelo GitHub, ou copiando para a pasta);
2. abra a aba **Inserir** e informe o nome do arquivo. Com `github`
   preenchido em `reports.json`, o botão *Procurar no GitHub* lista sozinho os
   arquivos que ainda não constam do registro;
3. a página abre o relatório num quadro oculto e lê dele o que consegue —
   título, órgão, número de fichas, faixa de informativos e período. Cada
   campo vem marcado como **lido** (veio do arquivo) ou **deduzido** (inferido
   do texto). Confira os deduzidos, sobretudo as datas;
4. *Copiar entrada* põe o JSON na área de transferência; cole-o na lista
   `relatorios` de `reports.json`, pelo editor do GitHub mesmo, e confirme.

O índice lê `reports.json` diretamente quando servido por HTTP, então essa
edição já basta: não é preciso rodar nada para o relatório aparecer.

*Ver como rascunho* guarda a entrada só neste aparelho, e o relatório passa a
aparecer no acervo com borda tracejada e o rótulo *rascunho local*. Serve para
conferir antes de publicar. O rascunho some sozinho quando a entrada de
verdade chega ao `reports.json`, e pode ser descartado a qualquer momento pelo
próprio cartão.

Falta só uma coisa depois disso: a **barra de progresso** do relatório novo
começa a contar quando o farol for injetado nele, com o script abaixo. Até lá
ele aparece normalmente, com o número de fichas do registro.

## Como acrescentar um relatório, pelo script

1. salve o arquivo em `relatorios/`, com nome em minúsculas, sem espaços nem
   acentos, no padrão `<orgao>-<periodo>.html` — por exemplo
   `stj-2026-t1.html`;
2. acrescente a entrada correspondente em `reports.json`;
3. rode, a partir desta pasta:

   ```
   python ferramentas/injetar-farol.py
   ```

O script injeta em cada relatório, antes de `</body>`, um bloco de metadados e
o farol de progresso, e regenera `dados/reports.js`. É idempotente: rodar de
novo apenas substitui o bloco anterior.

### Campos de `reports.json`

| campo       | o que é                                                        |
|-------------|----------------------------------------------------------------|
| `slug`      | identificador, igual ao nome do arquivo sem extensão           |
| `arquivo`   | caminho a partir da raiz, `relatorios/<slug>.html`             |
| `titulo`    | título exibido no cartão                                       |
| `orgao`     | `STF`, `STJ`, `CNJ`, `Kollemata`…                              |
| `tipo`      | `jurisprudencia` entra no mapa de cobertura; `normativo` não   |
| `inicio`    | primeiro mês coberto, `AAAA-MM`                                |
| `fim`       | último mês coberto, `AAAA-MM`                                  |
| `periodo`   | o mesmo intervalo em palavras, para leitura                    |
| `fonte`     | informativos ou ato de origem                                  |
| `fichas`    | número de fichas, usado antes da primeira abertura da página   |
| `produzido` | data de produção do relatório, `AAAA-MM-DD`                    |

`inicio` e `fim` são o que alimenta o mapa de cobertura e a lista de lacunas —
vale preenchê-los com cuidado.

### O que um relatório novo precisa ter

O índice não interpreta o conteúdo do relatório; ele só conta fichas. Para que
a barra de progresso funcione, o relatório precisa respeitar duas convenções:

- cada ficha é um elemento com a classe `ficha`;
- a ficha conferida ganha, nesse mesmo elemento, uma destas marcas:
  classe `done`, `feita`, `feito`, `is-done` ou `conferida`, ou o atributo
  `data-done="true"`.

Os relatórios existentes já seguem isso — usam, entre eles, quatro variantes
diferentes, e o farol cobre todas. Um relatório que marque a ficha de outra
maneira aparece no índice, mas com progresso sempre em zero; nesse caso, basta
acrescentar a marca nova à lista `FEITA` em `ferramentas/injetar-farol.py` e
rodar o script de novo.

Fora isso, o relatório é livre: cada um tem sua própria paleta, tipografia e
estrutura, e continua sendo um arquivo autocontido, que abre sozinho, offline.

## Como o progresso é registrado

Cada relatório já tinha sua própria marcação de fichas conferidas, em
`localStorage`, com chave e formato próprios. Nada disso foi alterado.

O farol injetado apenas observa o DOM, conta quantas fichas existem e quantas
estão marcadas, e grava o resumo numa chave uniforme:

```
radar:progresso:<slug>   →   {"feitas": 12, "total": 38, "visto": 178…}
```

O índice lê essas chaves e monta as barras de progresso. A situação de cada
relatório é derivada do progresso — não aberto, em revisão, revisado — e pode
ser sobreposta à mão pelo seletor do cartão, que grava em
`radar:situacao:<slug>`.

Duas consequências a ter em mente:

- `localStorage` é por origem e por navegador. O progresso não atravessa
  aparelhos, e o que foi marcado abrindo os arquivos por `file://` não migra
  para o site publicado;
- os botões **↓ progresso** e **↑ progresso**, no índice, exportam e importam
  todo esse estado num arquivo JSON. É o caminho para levar a leitura de um
  aparelho a outro, ou para guardar um ponto de retorno.

## Ver localmente

```
python -m http.server 8765
```

e abrir <http://localhost:8765>. Servir por HTTP, e não abrir o `index.html`
direto do disco, é o que reproduz o comportamento do site publicado: é a mesma
origem que faz o progresso dos relatórios chegar ao índice.
