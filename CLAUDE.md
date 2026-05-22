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

Per-page event name:
- `index.html` → `UpsellView` / `Upsell v6`
- `downsell.html` → `DownsellView` / `Downsell`
- `downsell2.html` → `Downsell2View` / `Downsell 2 $1`

## Branch
Always develop on `claude/magical-mendel-K8BJz`.
