# -*- coding: utf-8 -*-
"""Prepara os relatorios para o indice do Radar Extrajudicial.

Faz quatro coisas, e nada mais:

1. injeta em cada relatorio, logo antes de </body>, um bloco de metadados
   e um "farol" que publica o progresso de leitura no localStorage, sob a
   chave radar:progresso:<slug>. A marcacao propria de cada relatorio fica
   intacta: o farol apenas conta as fichas no DOM;

2. injeta no <head> o favicon do Radar, embutido como data URI (a partir de
   icone/favicon-embutido.png), para o relatorio continuar autocontido. Se o
   relatorio ja traz um <link rel="icon"> proprio, nao mexe;

3. se o relatorio nao tem botao de voltar ao indice (elemento com a classe
   radar-voltar), injeta um discreto, de reserva, no canto da tela. Os
   relatorios ja existentes trazem o seu, no estilo da propria pagina;

4. espelha reports.json em dados/reports.js, porque o indice tambem precisa
   abrir por file:// (onde o fetch de JSON e bloqueado pelo navegador).

E idempotente: rodar de novo apenas substitui o bloco injetado antes.

Uso, a partir da pasta Radar:  python ferramentas/injetar-farol.py
"""
import base64
import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
INICIO = "<!-- radar:inicio -->"
FIM = "<!-- radar:fim -->"
ICONE_INICIO = "<!-- radar:icone -->"
ICONE_FIM = "<!-- radar:icone-fim -->"
VOLTAR_INICIO = "<!-- radar:voltar -->"
VOLTAR_FIM = "<!-- radar:voltar-fim -->"
ARQ_ICONE = RAIZ / "icone" / "favicon-embutido.png"

# botao de reserva: so entra no relatorio que nao trouxe o proprio
MOLDE_VOLTAR = VOLTAR_INICIO + """
<style>
a.radar-voltar{position:fixed;left:14px;bottom:14px;z-index:60;display:inline-flex;align-items:center;gap:6px;padding:7px 12px 7px 9px;font:600 12px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif;color:#1b2430;background:rgba(255,255,255,.94);border:1px solid rgba(27,36,48,.25);border-radius:999px;text-decoration:none;box-shadow:0 2px 10px rgba(0,0,0,.12)}
a.radar-voltar svg{width:14px;height:14px;flex:none}
a.radar-voltar:hover{background:#1b2430;color:#fff}
a.radar-voltar:focus-visible{outline:2px solid #3a6fd8;outline-offset:2px}
@media (prefers-color-scheme:dark){a.radar-voltar{color:#e8ecf2;background:rgba(24,30,40,.94);border-color:rgba(232,236,242,.28)}a.radar-voltar:hover{background:#e8ecf2;color:#141a24}}
@media print{a.radar-voltar{display:none}}
</style>
<a class="radar-voltar" href="../index.html" aria-label="Voltar ao índice do Radar Extrajudicial"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Voltar ao Radar</span></a>
""" + VOLTAR_FIM

CAMPOS_META = ("slug", "titulo", "orgao", "tipo", "inicio", "fim",
               "periodo", "fonte", "fichas", "produzido")

MOLDE = INICIO + """
<script type="application/json" id="radar-meta">{meta}</script>
<script>
/* Radar Extrajudicial - publica o progresso desta pagina para o indice.
   Nao interfere na marcacao propria do relatorio: apenas conta no DOM
   quantas fichas existem e quantas estao marcadas, e grava o resumo. */
(function(){{
  var SLUG = {slug};
  var FICHA = ".ficha";
  var FEITA = ".ficha.done,.ficha.feita,.ficha.feito,.ficha.is-done,.ficha.conferida,.ficha[data-done='true']";
  var t;
  function publicar(){{
    try{{
      var total = document.querySelectorAll(FICHA).length;
      if(!total) return;
      var feitas = document.querySelectorAll(FEITA).length;
      localStorage.setItem("radar:progresso:" + SLUG, JSON.stringify({{
        feitas: feitas, total: total, visto: Date.now()
      }}));
    }}catch(e){{}}
  }}
  function agendar(){{ clearTimeout(t); t = setTimeout(publicar, 200); }}
  function iniciar(){{
    agendar();
    try{{
      new MutationObserver(agendar).observe(document.body, {{
        subtree: true, childList: true,
        attributes: true, attributeFilter: ["class", "data-done"]
      }});
    }}catch(e){{}}
  }}
  if(document.readyState === "loading"){{
    document.addEventListener("DOMContentLoaded", iniciar);
  }} else {{ iniciar(); }}
}})();
</script>
""" + FIM

AVISO_JS = ("/* Gerado por ferramentas/injetar-farol.py a partir de "
            "reports.json.\n   Nao edite aqui: edite reports.json e rode "
            "o script. */\n")


def bloco_icone():
    """<link> do favicon com o PNG embutido; None se o arquivo nao existir."""
    if not ARQ_ICONE.exists():
        return None
    dados = base64.b64encode(ARQ_ICONE.read_bytes()).decode("ascii")
    return (ICONE_INICIO + '<link rel="icon" type="image/png" '
            'href="data:image/png;base64,' + dados + '">' + ICONE_FIM)


def sem_bloco(texto, inicio, fim):
    # consome tambem as quebras em volta, senao cada execucao deixaria uma
    # linha em branco a mais no arquivo
    return re.sub(r"\n*" + re.escape(inicio) + r".*?" + re.escape(fim) + r"\n*",
                  "\n", texto, flags=re.S)


def injetar(relatorio):
    caminho = RAIZ / relatorio["arquivo"]
    original = caminho.read_text(encoding="utf-8")
    texto = original
    for inicio, fim in ((INICIO, FIM), (ICONE_INICIO, ICONE_FIM),
                        (VOLTAR_INICIO, VOLTAR_FIM)):
        texto = sem_bloco(texto, inicio, fim)
    slug = relatorio["slug"]
    notas = []

    # favicon, no <head>; relatorio sem </head> (so <title>) recebe antes do <title>
    icone = bloco_icone()
    if icone is None:
        notas.append("sem icone/favicon-embutido.png, favicon nao injetado")
    elif re.search(r"""<link[^>]+rel=["'](?:shortcut )?icon""", texto, re.I):
        notas.append("ja traz favicon proprio, mantido")
    elif "</head>" in texto:
        texto = texto.replace("</head>", icone + "\n</head>", 1)
        notas.append("favicon")
    elif "<title" in texto:
        texto = texto.replace("<title", icone + "\n<title", 1)
        notas.append("favicon")
    else:
        notas.append("sem </head> nem <title>, favicon nao injetado")

    if "</body>" not in texto:
        print("  ! sem </body>, ignorado:", slug)
        return False

    # botao de voltar: so de reserva
    if "radar-voltar" in texto:
        notas.append("voltar proprio, mantido")
    else:
        texto = texto.replace("</body>", MOLDE_VOLTAR + "\n</body>", 1)
        notas.append("voltar de reserva")

    # relatorio gerado conforme instrucoes-para-novos-relatorios.md ja traz
    # metadados e farol proprios: injetar de novo os duplicaria
    if 'id="radar-meta"' in texto:
        notas.append("metadados proprios, mantidos")
    else:
        bloco = MOLDE.format(
            meta=json.dumps({k: relatorio[k] for k in CAMPOS_META},
                            ensure_ascii=False),
            slug=json.dumps(slug))
        texto = texto.replace("</body>", bloco + "\n</body>", 1)
        notas.append("farol")

    if texto != original:
        caminho.write_text(texto, encoding="utf-8")
    print("  ok", slug, "(" + "; ".join(notas) + ")")
    return texto != original


def gerar_js(registro):
    destino = RAIZ / "dados" / "reports.js"
    destino.parent.mkdir(exist_ok=True)
    corpo = json.dumps(registro, ensure_ascii=False, indent=2)
    destino.write_text(AVISO_JS + "window.RADAR = " + corpo + ";\n",
                       encoding="utf-8")
    print("  ok dados/reports.js")


def main():
    registro = json.loads((RAIZ / "reports.json").read_text(encoding="utf-8"))
    for relatorio in registro["relatorios"]:
        injetar(relatorio)
    gerar_js(registro)


if __name__ == "__main__":
    main()
