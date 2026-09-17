# -*- coding: utf-8 -*-
"""Prepara os relatorios para o indice do Radar Extrajudicial.

Faz duas coisas, e nada mais:

1. injeta em cada relatorio, logo antes de </body>, um bloco de metadados
   e um "farol" que publica o progresso de leitura no localStorage, sob a
   chave radar:progresso:<slug>. A marcacao propria de cada relatorio fica
   intacta: o farol apenas conta as fichas no DOM;

2. espelha reports.json em dados/reports.js, porque o indice tambem precisa
   abrir por file:// (onde o fetch de JSON e bloqueado pelo navegador).

E idempotente: rodar de novo apenas substitui o bloco injetado antes.

Uso, a partir da pasta Radar:  python ferramentas/injetar-farol.py
"""
import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
INICIO = "<!-- radar:inicio -->"
FIM = "<!-- radar:fim -->"

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


def injetar(relatorio):
    caminho = RAIZ / relatorio["arquivo"]
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM), "",
                   texto, flags=re.S).rstrip()
    if "</body>" not in texto:
        print("  ! sem </body>, ignorado:", relatorio["slug"])
        return False
    bloco = MOLDE.format(
        meta=json.dumps({k: relatorio[k] for k in CAMPOS_META},
                        ensure_ascii=False),
        slug=json.dumps(relatorio["slug"]))
    caminho.write_text(texto.replace("</body>", bloco + "\n</body>", 1),
                       encoding="utf-8")
    print("  ok", relatorio["slug"])
    return True


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
