# -*- coding: utf-8 -*-
"""Gera plan-a.html, plan-b.html e plan7.html clonando downsell.html.

Roda: python build/gen_paginas.py

Reescreve os tres arquivos dentro de upsell-gluten/ a partir de duas fontes: a
copy aprovada em upsell2-maria-aguero.md (secoes 3 e 4) e a estrutura de
downsell.html. Depois de rodar, passar o QA: python qa/qa_paginas.py

Existe por tres motivos, nenhum deles cosmetico:

1. O miolo de plan-a e plan-b fica identico POR CONSTRUCAO. Editar os dois HTML
   a mao e como os dois divergem sem ninguem notar.
2. O mapa COMENTARIOS neutraliza os comentarios herdados de downsell.html, e o
   assert dentro de limpia() PARA a geracao se aparecer comentario que nao
   esteja no mapa nem em YA_LIMPIOS. E o que impede um export novo de design de
   republicar nota interna no fonte publico.
3. As rajadas e os intervalos ficam declarados num lugar so, em vez de
   espalhados por tres arquivos de 34 KB.

Se downsell.html mudar de estrutura, as ancoras usadas aqui sao '</style>',
'    <!-- HEADER WHATSAPP -->' e '    <!-- CHAT -->'.
"""
import io
import os
import re

# A copy aprovada (upsell2-maria-aguero.md) e documento interno e NAO esta
# neste repo, que e publico. Por isso a raiz e localizada subindo diretorios
# ate achar o arquivo, e o script funciona tanto dentro do repo quanto na
# pasta de trabalho que o contem.
HERE = os.path.dirname(os.path.abspath(__file__))


def _sube(marca):
    """Sobe diretorios a partir daqui ate achar quem contem `marca`."""
    d = HERE
    for _ in range(5):
        if os.path.exists(os.path.join(d, marca)):
            return d
        d = os.path.dirname(d)
    return None


PROJ = _sube("upsell2-maria-aguero.md")
if PROJ is None:
    raise SystemExit(
        "upsell2-maria-aguero.md nao encontrado subindo a partir de " + HERE
        + ". Ele e documento interno e nao vive no repo publico. Rode este "
        "script a partir da pasta de trabalho que contem os dois.")

REPO = _sube("downsell.html") or os.path.join(PROJ, "upsell-gluten")
BASE = io.open(os.path.join(REPO, "downsell.html"), encoding="utf-8").read()
MD = io.open(os.path.join(PROJ, "upsell2-maria-aguero.md"), encoding="utf-8").read()

CHECK_SVG = ('<svg viewBox="0 0 16 12"><path d="M15.01 3.316l-.478-.372a.365.365 0 0 '
             '0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 '
             '0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125'
             '.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365'
             '.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366'
             '.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143'
             '.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.063-.51z"/></svg>')


# ---------------------------------------------------------------- copy aprovada

def bloques(desde, hasta):
    trecho = MD[MD.index(desde):MD.index(hasta)]
    return re.findall(r"```\n(.*?)\n```", trecho, re.S)


U = bloques("## 3. COPY DO UPSELL 2", "## 4. COPY DO DOWNSELL")   # 21 blocos
D = bloques("## 4. COPY DO DOWNSELL", "## 5. NOTAS")              # 8 blocos
assert len(U) == 21 and len(D) == 8, (len(U), len(D))
assert U[19].startswith("[BOT") and D[6].startswith("[BOT")       # marcas do widget

# Aberturas da T2.1b. Substituem os blocos 1 e 2 da copy original.
# Mesmo numero de bolhas nos dois ramos, para a linha do tempo ser identica.
ABRE_A = [
    "✅ ¡Listo! Ya tienes tu lugar adentro 💚",
    "Antes de que te vayas, quiero contarte algo que casi nadie sabe.",
    "Ya tienes las recetas y el acompañamiento. Falta <b>una sola cosa</b>, "
    "y es la más simple de todas.",
]
ABRE_B = [
    "✅ ¡Listo! Tu libro ya va camino a tu correo.",
    "Tranquila, no te voy a ofrecer otra suscripción 💚",
    "Esto es distinto: es un plan cerrado de 21 días, se paga <b>una sola vez</b> "
    "y queda tuyo.",
]

# Negrito no numero do estudo, no nome do produto e na comparacao de valor.
# El texto no cambia, solo su peso, entao a checagem 5 do QA segue valendo.
# Nao ha mais valor monetario em nenhuma bolha: o preco vive no widget.
NEGRITA = {
    9:  ("casi un 30%", "<b>casi un 30%</b>"),
    12: ("Plan 21 Días: El Orden Correcto", "<b>Plan 21 Días: El Orden Correcto</b>"),
    16: ("un almuerzo fuera de casa", "<b>un almuerzo fuera de casa</b>"),
    17: ("solo existe aquí", "<b>solo existe aquí</b>"),
}
NEGRITA_D = {4: ("bastante menos", "<b>bastante menos</b>")}


def realza(txt, i, tabla):
    if i in tabla:
        viejo, nuevo = tabla[i]
        assert viejo in txt, (i, viejo)
        return txt.replace(viejo, nuevo, 1)
    return txt


MIOLO = [realza(U[i], i, NEGRITA) for i in range(2, 19)]   # blocos 3 a 19
CIERRE_27 = U[20]                                          # depois do widget
PLAN7 = [realza(D[i], i, NEGRITA_D) for i in range(0, 6)]  # blocos 1 a 6
CIERRE_7 = D[7]

# ---------------------------------------------------------------- rajadas
# Cada rajada e uma lista de itens. Dentro dela as bolhas chegam a 200ms uma da
# outra, como no WhatsApp quando alguem manda varias mensagens curtas seguidas.
# Entre rajadas, 800ms a 2s, proporcional ao que esta por chegar.
#
# REGRA DE EDICAO: se for preciso encurtar a pagina, o primeiro corte e a copy
# de preparacao (blocos 3 a 6 da secao 3). Nunca cortar o estudo nem os tres
# numeros, e nunca descer abaixo de 800ms entre rajadas ou 150ms dentro dela.

TXT, FOTO, WIDGET = "txt", "foto", "widget"


def rajadas_27(abre):
    return [
        [(TXT, abre[0])],
        [(TXT, abre[1]), (TXT, abre[2])],
        [(TXT, MIOLO[0])],                                   # 500 recetas perfectas
        [(TXT, MIOLO[1]), (TXT, MIOLO[2])],                  # sabes por que + QUE comes
        # A foto entra colada no golpe: "Es en que ORDEN lo comes" e a imagem
        # mostra a ordem. O texto afirma, a foto prova, no mesmo folego.
        [(TXT, MIOLO[3]), (FOTO, None)],
        [(TXT, MIOLO[4])],                                   # Diabetes Care
        [(TXT, MIOLO[5]), (TXT, MIOLO[6])],                  # mismas comidas + solo cambio
        [(TXT, MIOLO[7])],                                   # el numero, sozinho
        [(TXT, MIOLO[8])],                                   # sin quitar nada
        [(TXT, MIOLO[9])],                                   # y ese pico es justo
        [(TXT, MIOLO[10])],                                  # por eso arme el Plan
        # As tres entregas sao uma lista, um mesmo folego, e chegam juntas.
        [(TXT, MIOLO[11]), (TXT, MIOLO[12]), (TXT, MIOLO[13])],
        # Rajada final: as tres ultimas bolhas antes do widget. Sem numero e
        # sem explicar pagamento. O preco quem mostra e o widget.
        [(TXT, MIOLO[14]), (TXT, MIOLO[15]), (TXT, MIOLO[16])],
        [(WIDGET, None)],
        [(TXT, CIERRE_27)],
    ]


RAJADAS_7 = [
    [(TXT, PLAN7[0])],
    [(TXT, PLAN7[1])],
    [(TXT, PLAN7[2])],
    # plan7 nao tem a bolha "Es en que ORDEN lo comes", entao a foto acompanha
    # "la diferencia", que e o resultado da ordem. Quem chega aqui vem de
    # plan-a e ja viu o mecanismo explicado.
    [(TXT, PLAN7[3]), (FOTO, None)],
    [(TXT, PLAN7[4])],
    [(TXT, PLAN7[5])],
    [(WIDGET, None)],
    [(TXT, CIERRE_7)],
]


def sin_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def demora(raj, primera):
    """800ms a 2s entre rajadas, proporcional ao texto que esta por chegar."""
    if primera:
        return 1300
    n = sum(len(sin_tags(t)) for k, t in raj if k == TXT)
    if any(k == WIDGET for k, _ in raj):
        return 600
    return int(min(2000, max(800, round(450 + 3.2 * n))))


# ---------------------------------------------------------------- HTML

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
    # O degradado de reserva de .photo-wrap fica ativo aqui, ao contrario da
    # foto da folha: ele foi desenhado justamente para foto de comida.
    return (f'      <div class="bubble bubble-in photo-bubble photo-plato pre-reveal" '
            f'data-burst="{idx}">\n'
            f'        <div class="photo-wrap photo-wrap-plato">\n'
            f'          <img src="./platos-en-orden.webp" '
            f'alt="Tres platos en fila sobre una mesa de madera: primero la ensalada, '
            f'después el pollo a la plancha, al final el arroz." '
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
        # a demora vive no primeiro elemento da rajada, para auditar no fonte
        piezas[0] = piezas[0].replace(f'data-burst="{i}"',
                                      f'data-burst="{i}" data-delay="{d}"', 1)
        out.append("".join(piezas))
    return "\n".join(out)


# Os comentarios herdados de downsell.html descreviam intencao de design e
# citavam nome de pessoa. O HTML de uma pagina publicada e legivel por qualquer
# um, entao aqui eles viram rotulo estrutural e nada mais: o comentario diz o
# que o bloco E, nunca por que ele existe.
#
# Mapa explicito de proposito. Se um import de design novo trouxer comentario
# fora deste mapa, o assert para a geracao em vez de publicar.
COMENTARIOS = {
    "TOP SOFT NOTICE": "/* Aviso superior (no usado en esta pagina) */",
    "WHATSAPP HEADER": "/* Header WhatsApp */",
    "CHAT AREA": "/* Area de chat */",
    "Bubble base": "/* Burbuja, base */",
    "Bullets": "/* Lista dentro de burbuja (no usada en esta pagina) */",
    "Photo bubble": "/* Burbuja de foto */",
    "Fallback gradient": "/* Fondo de reserva si la imagen no carga */",
    "Typing indicator": "/* Indicador de escritura */",
    "Hotmart widget bubble": "/* Burbuja del widget */",
    "Sem margin negativa": "/* Sin margen negativo */",
    '"No gracias"': "/* Enlace de salida (no usado en esta pagina) */",
    "Entrance + reveal": "/* Entrada y revelado */",
    "Chat bubble silhouette": "<!-- silueta -->",
    "Typing dots bubble": "<!-- puntos -->",
    "WA HEADER": "<!-- Header WhatsApp -->",
}


# A fonte, downsell.html, foi neutralizada em producao. Entao os comentarios
# dela ja sao rotulos aprovados e passam direto. O assert continua valendo para
# qualquer comentario que nao esteja nem no mapa nem nesta lista, que e o caso
# de um import novo de design.
YA_LIMPIOS = {
    "<!-- Chat bubble silhouette -->", "<!-- Typing dots bubble -->",
    "<!-- Sin barra superior -->", "<!-- HEADER WHATSAPP -->", "<!-- CHAT -->",
    "<!-- 1) Indicador de escritura inicial -->", "<!-- 2) Primera burbuja -->",
    "<!-- 3) Foto -->", "<!-- 4) Burbuja -->", "<!-- 5) Burbuja final -->",
    "<!-- 6) Widget Hotmart -->", "<!-- Sin enlace de salida propio -->",
    "<!-- Secuencia de revelado -->", "<!-- Hotmart widget -->",
    "<!-- Tracker (Pixel + CAPI) -->",
    "/* ---------- BARRA SUPERIOR ---------- */",
    "/* ---------- HEADER WHATSAPP ---------- */",
    "/* ---------- CHAT AREA ---------- */", "/* Bubble base */",
    "/* Lista dentro de burbuja */", "/* Burbuja de foto */",
    "/* Fondo de reserva si la imagen no carga */", "/* Typing indicator */",
    "/* Burbuja del widget */", "/* Sin margen negativo */",
    "/* Enlace de salida */", "/* Entrance + reveal */",
}

def limpia(fragmento):
    """Troca cada comentario herdado pelo seu rotulo estrutural."""
    def sub(m):
        bruto = m.group(0)
        if re.sub(r"\s+", " ", bruto).strip() in YA_LIMPIOS:
            return bruto
        for clave, limpio in COMENTARIOS.items():
            if clave in bruto:
                return limpio
        raise AssertionError("comentario herdado sem rotulo definido: "
                             + re.sub(r"\s+", " ", bruto)[:90])
    fragmento = re.sub(r"/\*.*?\*/", sub, fragmento, flags=re.S)
    return re.sub(r"<!--.*?-->", sub, fragmento, flags=re.S)


CSS_EXTRA = """
  /* Foto de los platos: 4:3, sin recorte */
  .photo-plato { max-width: 78%; }
  .photo-wrap-plato { aspect-ratio: 4 / 3; }
"""

SCRIPT_REVEAL = """
  <!-- Revelado por rajadas. El intervalo de cada rajada vive en data-delay. -->
  <script>
    (function() {
      var PASO_DENTRO = 200;   // 150 a 250ms: mensagens do mesmo folego
      var typingFirst = document.getElementById('typingFirst');
      var waStatus = document.getElementById('wa-status');
      var widget = document.getElementById('widgetBubble');

      var grupos = [];
      Array.prototype.forEach.call(document.querySelectorAll('[data-burst]'), function(el) {
        var k = parseInt(el.getAttribute('data-burst'), 10);
        if (!grupos[k]) grupos[k] = [];
        grupos[k].push(el);
      });
      grupos = grupos.filter(function(g) { return !!g; });

      function show(el) {
        if (!el) return;
        el.classList.remove('pre-reveal');
        el.classList.add('reveal-in');
      }
      function hide(el) {
        if (!el) return;
        el.classList.remove('reveal-in');
        el.classList.add('pre-reveal');
      }

      // Sonido: primera burbuja y llegada del widget
      function playTap() {
        try {
          var Ctx = window.AudioContext || window.webkitAudioContext;
          if (!Ctx) return;
          var ctx = new Ctx();
          var now = ctx.currentTime;
          var osc = ctx.createOscillator();
          var g = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = 880;
          g.gain.setValueAtTime(0, now);
          g.gain.linearRampToValueAtTime(0.08, now + 0.01);
          g.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
          osc.connect(g); g.connect(ctx.destination);
          osc.start(now);
          osc.stop(now + 0.22);
        } catch(e) {}
      }

      // Mantiene visible el ultimo mensaje. Se detiene si hay scroll manual arriba.
      var subioSola = false;
      window.addEventListener('scroll', function() {
        var falta = document.documentElement.scrollHeight
                  - window.pageYOffset - window.innerHeight;
        subioSola = falta > 140;
      }, { passive: true });

      function seguir(el) {
        if (!el || subioSola) return;
        try {
          var r = el.getBoundingClientRect();
          if (r.bottom > window.innerHeight - 8) {
            window.scrollTo({
              top: window.pageYOffset + (r.bottom - window.innerHeight) + 24,
              behavior: 'smooth'
            });
          }
        } catch(e) {}
      }

      var t = 0;
      grupos.forEach(function(grupo, i) {
        var d = parseInt(grupo[0].getAttribute('data-delay'), 10) || 900;
        t += d;
        var enT = t;
        // Estado del header entre rajadas
        if (i > 0) {
          setTimeout(function() {
            if (waStatus) waStatus.textContent = 'escribiendo…';
          }, enT - Math.min(700, d - 100));
        }
        grupo.forEach(function(el, j) {
          setTimeout(function() {
            if (i === 0) hide(typingFirst);
            show(el);
            if (j === grupo.length - 1) {
              if (waStatus) waStatus.textContent = 'en línea';
              seguir(el);
            }
            if (i === 0 && j === 0) playTap();
            if (el === widget) {
              playTap();
              setTimeout(function() {
                try {
                  var rect = widget.getBoundingClientRect();
                  window.scrollTo({
                    top: window.pageYOffset + rect.top - 12,
                    behavior: 'smooth'
                  });
                } catch(e) {}
              }, 380);
            }
          }, enT + j * PASO_DENTRO);
        });
        t += (grupo.length - 1) * PASO_DENTRO;
      });

      // Hora local del dispositivo
      function nowHHMM() {
        var d = new Date();
        return String(d.getHours()).padStart(2, '0') + ':'
             + String(d.getMinutes()).padStart(2, '0');
      }
      var stamp = nowHHMM();
      document.querySelectorAll('.bubble-time .t, .photo-meta .t').forEach(function(el) {
        el.textContent = stamp;
      });
    })();
  </script>
"""

WIDGET_LOADER = """
  <!-- Hotmart widget -->
  <script src="https://checkout.hotmart.com/lib/hotmart-checkout-elements.js"></script>
  <script>
    if (window.checkoutElements) {
      try { checkoutElements.init('salesFunnel').mount('#hotmart-sales-funnel'); } catch(e) {}
    }
  </script>
"""


def tracker(evento, nombre):
    return f"""
  <!-- Tracker (Pixel + CAPI) -->
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


def construir(rajs, etiqueta, evento, nombre):
    # As regras de CSS saem de downsell.html sem alteracao. Os comentarios, nao:
    # passam por limpia() antes de virar arquivo publicado.
    cab = limpia(BASE[:BASE.index("</style>")]) + CSS_EXTRA + "</style>\n</head>\n"
    ini = BASE.index('    <!-- HEADER WHATSAPP -->')
    fin = BASE.index('    <!-- CHAT -->')
    header = limpia(BASE[ini:fin])
    return (cab
            + '<body>\n'
            + f'  <main class="page" data-screen-label="{etiqueta}">\n\n'
            + header
            + '    <!-- CHAT -->\n'
            + '    <div class="chat" id="chat">\n\n'
            + '      <div class="date-pill">Hoy</div>\n\n'
            + '      <div class="typing-bubble" id="typingFirst" '
              'style="animation-delay: 0.3s">\n'
            + '        <span class="typing-dot"></span>\n'
            + '        <span class="typing-dot"></span>\n'
            + '        <span class="typing-dot"></span>\n'
            + '      </div>\n\n'
            + cuerpo_chat(rajs)
            + '\n      <div class="bottom-spacer"></div>\n'
            + '    </div>\n\n'
            + '  </main>\n'
            + SCRIPT_REVEAL
            + WIDGET_LOADER
            + tracker(evento, nombre))


PAGINAS = [
    ("plan-a.html", rajadas_27(ABRE_A), "Plan A", "PlanAView", "Plan A 21 Dias"),
    ("plan-b.html", rajadas_27(ABRE_B), "Plan B", "PlanBView", "Plan B 21 Dias"),
    ("plan7.html", RAJADAS_7, "Plan 7", "Plan7View", "Plan 7 Dias"),
]

# Cero raya larga no que eu escrevo e no que a compradora le. O CSS e o header
# herdados de downsell.html ficam verbatim, inclusive os comentarios com raya
# que ja estao nos tres arquivos de producao, para que um update de design futuro
# continue dando diff limpo. A raya nunca aparece em copy visivel, e o QA garante
# isso sobre o DOM.
MIO = [CSS_EXTRA, SCRIPT_REVEAL, WIDGET_LOADER] + [t for t in MIOLO] \
      + ABRE_A + ABRE_B + PLAN7 + [CIERRE_27, CIERRE_7]
for texto in MIO:
    for mal in ("\u2014", "\u2013"):
        assert mal not in texto, texto[:60]

for nombre_arch, rajs, etiqueta, evento, nombre in PAGINAS:
    html = construir(rajs, etiqueta, evento, nombre)
    cuerpo = html[html.index('<div class="chat"'):html.index("</main>")]
    for mal in ("\u2014", "\u2013"):
        assert mal not in cuerpo, (nombre_arch, "raya no corpo do chat")
    io.open(os.path.join(REPO, nombre_arch), "w", encoding="utf-8", newline="\n").write(html)
    total = 0
    for i, raj in enumerate(rajs):
        total += demora(raj, i == 0) + (len(raj) - 1) * 200
        if any(k == WIDGET for k, _ in raj):
            widget_en = total
    print(f"{nombre_arch:<14} {len(rajs):>2} rajadas  "
          f"{sum(len(r) for r in rajs):>2} itens  "
          f"widget em {widget_en/1000:.1f}s  fim em {total/1000:.1f}s  "
          f"{len(html)/1024:.0f} KB")
