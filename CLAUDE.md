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
- `tabla-del-orden.webp`: imagem da folha La Tabla del Orden, usada nas três acima

As três clonam a estrutura de `downsell.html`. O preço não aparece em nenhuma
bolha: quem exibe é o widget da Hotmart, e a âncora ("de $47 por $27") é
configuração da oferta no checkout.

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

Ao clonar uma página para criar outra, o erro clássico é o evento vir junto do
arquivo de origem. O QA confere um a um, pelo POST que sai na rede e não pela
string no fonte.

## Branch
Always develop on `claude/magical-mendel-K8BJz`.
