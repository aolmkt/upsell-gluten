# Repo notes for Claude

## Files
- `index.html` — Upsell v6 (from Claude Design `Upsell v6.html`)
- `downsell.html` — Downsell 1 (from `Downsell.html`)
- `downsell2.html` — Downsell 2 / $1 trial (from `Downsell 2.html`)
- `tracker.js` — Facebook Pixel + CAPI tracker (production-only, NOT in design files)

Páginas do Plan 21 Días (upsell 2), criadas em 30/07/2026, sem arquivo de design de origem:
- `plan-a.html`: Plan 21 Días $27, ramo de quem aceitou alguma etapa da assinatura
- `plan-b.html`: Plan 21 Días $27, ramo de quem recusou tudo
- `plan7.html`: 7 Días $17, downsell que sai só de `plan-a.html`
- `platos-en-orden.webp`: foto dos três pratos em ordem, ilustra a bolha "es en qué orden lo comes", usada nas três acima

As três clonam a estrutura de `downsell.html`. O preço não aparece em nenhuma
bolha: quem exibe é o widget da Hotmart, e a âncora ("de $47 por $27") é
configuração da oferta no checkout.

Página de obrigado, criada em 03/08/2026:
- `gracias.html`: fim do funil, para onde caem todas as saídas das etapas

Ela **não** clona a estrutura de chat das outras seis, de propósito. A venda já
aconteceu: encenar uma conversa numa página de recibo seria mentira sem função.
Mantém a identidade (Inter, paleta, coluna de 440px, header com a Maria) e o
resto é conteúdo estático, sem animação, sem bolha e sem widget.

O texto foi portado da página antiga em `lavishcreative.com/gluten/gracias/`,
que era boa. Duas mudanças: saiu a promessa com prazo ("en pocos días notarás
la diferencia"), e o texto ficou genérico de propósito ("todo lo que elegiste",
"tu material"). Genérico é o que faz ela servir para qualquer combinação de
compras e para os upsells que ainda vão existir, sem precisar editar nada.

O e-mail de suporte é `ayuda@confiamosenti.com`, o mesmo da página antiga.

Página do upsell 3, criada em 03/08/2026:
- `panza-calma.html`: alcançável a partir das três saídas de compra do funil

Clona a estrutura de chat de `plan-a.html`. É gerada por
`build/gen_panza_calma.py`, script irmão de `gen_paginas.py`: a fonte de copy
fica fora do repo e o `<head>`, o header, o script de revelado e o loader do
widget são recortados de `plan-a.html`, não reescritos.

## ⚠️ Comentários no HTML: só rótulo estrutural

Comentário destes arquivos vai publicado e qualquer pessoa lê com View Source.
Em 30/07/2026 os comentários das seis páginas foram neutralizados. Saíram três
coisas:

1. Nome de pessoa ("Amanda: nada de vermelho gritando").
2. Racional de persuasão ("continuidade neural", `"No gracias"` como "link
   discreto, sem peso visual", "o cérebro precisa ver o verde IMEDIATAMENTE",
   "O cérebro tá cansado").
3. Admissão de que o chat é encenado ("tipo Maria mandou agora", "feels like
   she sent a photo grid", "Instagram Live style", "WhatsApp-style notification
   ding", "a foto sussurra").

Comentário de engenharia fica ("Disconnect intersection observer so it stops
triggering"). A regra é: sai nome de pessoa, racional de persuasão e admissão de
simulação. Fica o que descreve mecânica.

**Um export novo do Claude Design traz os comentários originais de volta.**
Depois de copiar o arquivo, neutralizar outra vez.

O QA (`qa/qa_paginas.py`, fora do repo) tem lista de permissão com os rótulos
aprovados das seis páginas e reprova o build em qualquer comentário novo. Ou
seja, o erro aparece sozinho, mas o motivo só está escrito aqui.

O mesmo QA congela o sha256 de `index.html`, `downsell.html` e `downsell2.html`
**sem comentário nenhum**, com base tirada da produção antes da limpeza. Serve
para provar, antes de um merge, que só comentário mudou nessas três e que
nenhuma linha de CSS, elemento ou JS foi tocada.

## ⚠️ When applying a new design update from Claude Design

The design HTML files do NOT contain the tracker. After copying a new
version of a design HTML over the corresponding page, you MUST re-inject
the tracker block before `</body>`:

```html
<!-- Tracker (Pixel + CAPI) -->
<script src="./tracker.js"></script>
<script>
  window.addEventListener('load', function() {
    setTimeout(function() {
      if (window.trackEvent) window.trackEvent('<EVENT_NAME>', { content_name: '<NAME>' });
    }, 600);
  });
</script>
```

Não mexa no iframe da Hotmart (não reescrever `src`). O tracker já
recupera o `sck` da URL/localStorage/cookie e envia como `external_id`
pro Pixel + CAPI. A Hotmart já tem o buyer atrelado via `fsid` do funil.

## ⚠️ Customizações permanentes do `tracker.js`

Quando o usuário trouxer uma versão nova do tracker, **manter sempre estas
mudanças** em relação ao código original do v2.81:

1. **Remover o auto-linker da Hotmart** (bloco `autoLink` no final) — sem efeito útil,
   já que o checkout é via iframe (não `<a href>`).
2. **Remover o disparo automático de `ViewContent`** dentro de `initSystem()`. O tracker
   deve disparar apenas `PageView` no carregamento. Os eventos personalizados
   (`UpsellView`, `DownsellView`, `Downsell2View`) ficam por conta das páginas via
   `window.trackEvent(...)`. Isso evita contaminar métricas com `ViewContent`
   genérico em todas as páginas.

Manter o Pixel ID `1771320517046203` e a `API_URL` `https://tracking.lavishcreative.com`
salvo instrução contrária.

Per-page event name:
- `index.html` → `UpsellView` / `Upsell v6`
- `downsell.html` → `DownsellView` / `Downsell`
- `downsell2.html` → `Downsell2View` / `Downsell 2 $1`
- `plan-a.html` → `PlanAView` / `Plan A 21 Dias`
- `plan-b.html` → `PlanBView` / `Plan B 21 Dias`
- `plan7.html` → `Plan7View` / `Plan 7 Dias`
- `gracias.html` → `GraciasView` / `Gracias`
- `panza-calma.html` → `Up3View` / `Panza Calma 14 Dias` (no load)
- `panza-calma.html` → `Up3CTAView` / `Panza Calma 14 Dias` (quando la burbuja
  del widget se revela, no en el load; separa "no llegó al botón" de "llegó y
  no compró")

`gracias.html` dispara **só o evento de view**, nunca `Purchase`. A compra da
Hotmart é confirmada server-side, e a URL da página de obrigado é pública: um
`Purchase` disparado pelo browser contaria venda para qualquer um que abrisse o
link, e contaria de novo a cada refresh. Se um dia precisar de `Purchase`, ele
vem do postback da Hotmart, não daqui.

Ao clonar uma página para criar outra, o erro clássico é o evento vir junto do
arquivo de origem. O QA confere um a um, pelo POST que sai na rede e não pela
string no fonte.

## Branch
Always develop on `claude/magical-mendel-K8BJz`.
