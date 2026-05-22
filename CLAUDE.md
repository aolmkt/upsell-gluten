# Repo notes for Claude

## Files
- `index.html` — Upsell v6 (from Claude Design `Upsell v6.html`)
- `downsell.html` — Downsell 1 (from `Downsell.html`)
- `downsell2.html` — Downsell 2 / $1 trial (from `Downsell 2.html`)
- `tracker.js` — Facebook Pixel + CAPI tracker (production-only, NOT in design files)

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

## Branch
Always develop on `claude/magical-mendel-K8BJz`.
