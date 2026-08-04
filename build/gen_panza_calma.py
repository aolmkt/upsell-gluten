# -*- coding: utf-8 -*-
"""Gera panza-calma.html clonando plan-a.html.

Roda: python build/gen_panza_calma.py

Le o roteiro aprovado em outputs/copy/panza-calma.md (secao 2, bloco a bloco) e
usa plan-a.html como fonte do <head>, do header WhatsApp, do indicador de
"escribiendo", do script de revelado e do loader do widget Hotmart: essas
partes saem de la BYTE A BYTE, sem reescrever nada, porque ja estao publicadas
e ja passaram por QA. So o corpo do chat (as bolhas) e novo.

Existe como script separado de gen_paginas.py, e nao como alteracao dele,
porque as duas familias de pagina tem fonte de copy em formato diferente
(blocos ```code``` la, lista numerada com marca [grupo N] aqui) e o roteiro
desta pagina nao compartilha miolo com plan-a/plan-b/plan7.

Se plan-a.html mudar de estrutura, as ancoras usadas aqui sao as mesmas de
gen_paginas.py: '</head>', '    <!-- HEADER WHATSAPP -->', '    <!-- CHAT -->',
mais o inicio da primeira burbuja real, do bloco de revelado e do loader do
widget.
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _sube(rel):
    """Sobe diretorios a partir daqui ate achar quem contem `rel`."""
    d = HERE
    for _ in range(6):
        if os.path.exists(os.path.join(d, rel)):
            return d
        d = os.path.dirname(d)
    return None


# O roteiro aprovado (outputs/copy/panza-calma.md) e documento interno e NAO
# esta neste repo, que e publico. A raiz e localizada subindo diretorios ate
# achar o arquivo, igual ao mecanismo de gen_paginas.py.
COPY_REL = os.path.join("outputs", "copy", "panza-calma.md")
PROJ = _sube(COPY_REL)
if PROJ is None:
    raise SystemExit(
        "outputs/copy/panza-calma.md nao encontrado subindo a partir de "
        + HERE + ". Ele e documento interno e nao vive no repo publico. Rode "
        "este script a partir da pasta de trabalho que contem os dois.")

REPO = _sube("plan-a.html") or os.path.join(PROJ, "site")
BASE = io.open(os.path.join(REPO, "plan-a.html"), encoding="utf-8").read()
MD = io.open(os.path.join(PROJ, COPY_REL), encoding="utf-8").read()

# Imagem nova referida na bolha 22 (La Lista Semaforo). Se nao estiver pronta
# no dia do build, a bolha sai inteira e nada mais muda, exatamente como a
# copy instrui.
IMG_LISTA_SEMAFORO = os.path.join(REPO, "lista-semaforo.webp")
TEM_FOTO = os.path.exists(IMG_LISTA_SEMAFORO)

# ---------------------------------------------------------------- roteiro

SECAO = MD[MD.index("## 2. Roteiro"):MD.index("## 3. Textos do widget")]

ITEM_RE = re.compile(
    r"\*\*(\d+)\.\s*([^*]+?)\*\*\s*`\[grupo (\d+)\]`\n((?:> .*\n?)+)"
)

TXT, FOTO, WIDGET = "txt", "foto", "widget"

items = []  # (num, grupo, tipo, texto_ou_None)
for m in ITEM_RE.finditer(SECAO):
    num = int(m.group(1))
    label = m.group(2).strip()
    grupo = int(m.group(3))
    bloque = m.group(4)
    primeira = bloque.splitlines()[0]
    assert primeira.startswith("> "), (num, primeira)
    texto = primeira[2:]
    if "(foto)" in label:
        items.append((num, grupo, FOTO, texto))
    elif label.startswith("Widget"):
        items.append((num, grupo, WIDGET, None))
    else:
        assert label == "Maria", (num, label)
        items.append((num, grupo, TXT, texto))

assert len(items) == 34, len(items)
assert [i[0] for i in items] == list(range(1, 35))
assert items[32][2] == WIDGET, "bolha 33 devia ser o widget"
assert items[21][2] == FOTO, "bolha 22 devia ser a foto"

PENDENCIAS = []
if not TEM_FOTO:
    PENDENCIAS.append(
        "lista-semaforo.webp ausente em " + REPO + ": bolha 22 (foto) omitida "
        "da pagina, como a copy instrui. Nada mais mudou.")

# Agrupa por grupo, na ordem em que aparecem no roteiro.
grupos = {}
ordem_grupos = []
for num, grupo, tipo, texto in items:
    if tipo == FOTO and not TEM_FOTO:
        continue
    if grupo not in grupos:
        grupos[grupo] = []
        ordem_grupos.append(grupo)
    grupos[grupo].append((tipo, texto))

RAJADAS = [grupos[g] for g in sorted(ordem_grupos)]

# ---------------------------------------------------------------- checagens
# Zero raya larga/corta no que a leitora le, nunca so no comentario.
for num, grupo, tipo, texto in items:
    if texto:
        for mal in ("—", "–"):
            assert mal not in texto, (num, texto[:60])

# Nenhum valor monetario: sem $, sem simbolo de moeda, sem "USD"/"MXN"/etc.
for num, grupo, tipo, texto in items:
    if texto:
        assert "$" not in texto, (num, texto)
        assert not re.search(r"\bUSD\b|\bMXN\b|\bARS\b", texto), (num, texto)

# ---------------------------------------------------------------- HTML

CHECK_SVG = ('<svg viewBox="0 0 16 12"><path d="M15.01 3.316l-.478-.372a.365.365 0 0 '
             '0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 '
             '0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125'
             '.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365'
             '.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366'
             '.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143'
             '.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.063-.51z"/></svg>')


def sin_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def demora(raj, primera):
    """800ms a 2s entre rajadas, proporcional ao texto que esta por chegar.
    Mesma formula usada nas paginas plan-a/plan-b/plan7."""
    if primera:
        return 1300
    n = sum(len(sin_tags(t)) for k, t in raj if k == TXT)
    if any(k == WIDGET for k, _ in raj):
        return 600
    return int(min(2000, max(800, round(450 + 3.2 * n))))


def burbuja(texto, idx, agrupada):
    cls = "bubble bubble-in" + (" bubble-grouped" if agrupada else "") + " pre-reveal"
    return (f'      <div class="{cls}" data-burst="{idx}">\n'
            f'        {texto}\n'
            f'        <span class="bubble-time">\n'
            f'          <span class="t">12:00</span>\n'
            f'          {CHECK_SVG}\n'
            f'        </span>\n'
            f'      </div>\n')


def foto(idx):
    return (f'      <div class="bubble bubble-in photo-bubble photo-semaforo pre-reveal" '
            f'data-burst="{idx}">\n'
            f'        <div class="photo-wrap photo-wrap-semaforo">\n'
            f'          <img src="./lista-semaforo.webp" '
            f'alt="Una hoja pegada en la puerta del refri, con tres columnas: verde, '
            f'amarillo y rojo, y los cambios anotados al lado." '
            f'width="1000" height="750" decoding="async" />\n'
            f'        </div>\n'
            f'        <div class="photo-meta">\n'
            f'          <span class="t">12:00</span>\n'
            f'          {CHECK_SVG}\n'
            f'        </div>\n'
            f'      </div>\n')


def widget(idx):
    return (f'      <div class="bubble bubble-in widget-bubble pre-reveal" '
            f'id="widgetBubble" data-burst="{idx}">\n'
            f'        <div id="hotmart-sales-funnel"></div>\n'
            f'      </div>\n')


def cuerpo_chat(rajs):
    out = []
    for i, raj in enumerate(rajs):
        d = demora(raj, i == 0)
        piezas = []
        for j, (tipo, dato) in enumerate(raj):
            if tipo == TXT:
                piezas.append(burbuja(dato, i, j > 0))
            elif tipo == FOTO:
                piezas.append(foto(i))
            else:
                piezas.append(widget(i))
        piezas[0] = piezas[0].replace(f'data-burst="{i}"',
                                      f'data-burst="{i}" data-delay="{d}"', 1)
        out.append("".join(piezas))
    return "\n".join(out)


CSS_EXTRA_FOTO = """
  /* Foto de la lista semaforo: 4:3, sin recorte */
  .photo-semaforo { max-width: 78%; }
  .photo-wrap-semaforo { aspect-ratio: 4 / 3; }
"""

# ------------------------------------------------------- pedazos clonados
# Estos bloques salen de plan-a.html byte a byte: ya estan publicados y ya
# pasaron QA. Nada se reescribe aqui, solo se recorta.

HEAD_HTML = BASE[:BASE.index("</head>") + len("</head>\n")]
if not TEM_FOTO:
    # A pagina nao usa nenhuma foto: o CSS especifico de foto de plan-a.html
    # (photo-plato) nao se copia, para no dejar regla muerta que confunda.
    marca_css = "\n  /* Foto de los platos: 4:3, sin recorte */"
    HEAD_HTML = HEAD_HTML[:HEAD_HTML.index(marca_css)] + "</style>\n</head>\n"
else:
    marca_css = "\n  /* Foto de los platos: 4:3, sin recorte */"
    HEAD_HTML = (HEAD_HTML[:HEAD_HTML.index(marca_css)]
                 + CSS_EXTRA_FOTO + "</style>\n</head>\n")

_ini_header = BASE.index('    <!-- HEADER WHATSAPP -->')
_fin_header = BASE.index('    <!-- CHAT -->')
HEADER_HTML = BASE[_ini_header:_fin_header]

_ini_typing = BASE.index('      <div class="typing-bubble" id="typingFirst"')
_fin_typing = BASE.index('      <div class="bubble bubble-in pre-reveal" data-burst="0"')
TYPING_HTML = BASE[_ini_typing:_fin_typing]

_ini_reveal = BASE.index('  <!-- Revelado por rajadas')
_ini_widgetloader = BASE.index('  <!-- Hotmart widget -->')
_ini_tracker = BASE.index('  <!-- Tracker (Pixel + CAPI) -->')

SCRIPT_REVEAL_HTML = BASE[_ini_reveal:_ini_widgetloader]
WIDGET_LOADER_HTML = BASE[_ini_widgetloader:_ini_tracker]

# Up3CTAView: dispara cuando la burbuja del widget se revela, no en el load.
# Separa "no llego al boton" de "llego y no compro". Existe solo en esta
# pagina: es la unica insercion que no sale byte a byte de plan-a.html, por
# eso va aqui y no en SCRIPT_REVEAL_HTML directamente.
_MARCA_WIDGET_REVEAL = "if (el === widget) {\n              playTap();\n"
assert SCRIPT_REVEAL_HTML.count(_MARCA_WIDGET_REVEAL) == 1, (
    "ancora del reveal del widget cambio en plan-a.html, revisar gen_panza_calma.py")
SCRIPT_REVEAL_HTML = SCRIPT_REVEAL_HTML.replace(
    _MARCA_WIDGET_REVEAL,
    _MARCA_WIDGET_REVEAL
    + "              if (window.trackEvent) window.trackEvent"
      "('Up3CTAView', { content_name: 'Panza Calma 14 Dias' });\n",
    1)


def tracker(evento, nombre):
    return f"""  <!-- Tracker (Pixel + CAPI) -->
  <script src="./tracker.js"></script>
  <script>
    window.addEventListener('load', function() {{
      setTimeout(function() {{
        if (window.trackEvent) window.trackEvent('{evento}', {{ content_name: '{nombre}' }});
      }}, 600);
    }});
  </script>
</body>
</html>
"""


def construir():
    body = (
        '<body>\n'
        '  <main class="page" data-screen-label="Panza Calma">\n\n'
        + HEADER_HTML
        + '    <!-- CHAT -->\n'
        + '    <div class="chat" id="chat">\n\n'
        + '      <div class="date-pill">Hoy</div>\n\n'
        + TYPING_HTML
        + cuerpo_chat(RAJADAS)
        + '\n      <div class="bottom-spacer"></div>\n'
        + '    </div>\n\n'
        + '  </main>\n'
        + SCRIPT_REVEAL_HTML
        + WIDGET_LOADER_HTML
        + tracker('Up3View', 'Panza Calma 14 Dias')
    )
    return HEAD_HTML + body


HTML = construir()

for mal in ("—", "–"):
    assert mal not in HTML, "raya en el HTML final"
assert "$" not in HTML, "simbolo de moneda en el HTML final"
assert not re.search(r"\bUSD\b|\bMXN\b|\bARS\b", HTML), "codigo de moneda en el HTML final"

OUT_PATH = os.path.join(REPO, "panza-calma.html")
io.open(OUT_PATH, "w", encoding="utf-8", newline="\n").write(HTML)

total = 0
for i, raj in enumerate(RAJADAS):
    total += demora(raj, i == 0) + (len(raj) - 1) * 200
    if any(k == WIDGET for k, _ in raj):
        widget_en = total
print(f"panza-calma.html  {len(RAJADAS):>2} rajadas  "
      f"{sum(len(r) for r in RAJADAS):>2} itens  "
      f"widget em {widget_en/1000:.1f}s  fim em {total/1000:.1f}s  "
      f"{len(HTML)/1024:.0f} KB")
if PENDENCIAS:
    print("Pendencias:")
    for p in PENDENCIAS:
        print(" -", p)
