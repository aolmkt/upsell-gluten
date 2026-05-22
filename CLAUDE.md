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

  // Inject sck=external_id into Hotmart iframe when it mounts
  (function() {
    var container = document.getElementById('hotmart-sales-funnel');
    if (!container) return;
    var done = false;
    function inject(iframe) {
      if (done || !iframe || !iframe.src) return;
      var sck = (window.trackingData && window.trackingData.external_id) || localStorage.getItem('sck_id');
      if (!sck) return;
      try {
        var u = new URL(iframe.src);
        if (!u.searchParams.get('sck')) {
          u.searchParams.set('sck', sck);
          iframe.src = u.toString();
        }
        done = true;
      } catch(e) {}
    }
    var existing = container.querySelector('iframe');
    if (existing) inject(existing);
    var mo = new MutationObserver(function() {
      var f = container.querySelector('iframe');
      if (f) { inject(f); if (done) mo.disconnect(); }
    });
    mo.observe(container, { childList: true, subtree: true });
  })();
</script>
```

Per-page event name:
- `index.html` → `UpsellView` / `Upsell v6`
- `downsell.html` → `DownsellView` / `Downsell`
- `downsell2.html` → `Downsell2View` / `Downsell 2 $1`

## Branch
Always develop on `claude/magical-mendel-K8BJz`.
