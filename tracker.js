/**
 * FACEBOOK TRACKING GATEWAY v2.81 (Site / Landing Page Edition)
 * - Re-hidratação de Dados (Match Quality Máximo via /hydrate)
 * - Persistência Extrema sem Poluição de URL (Cookie + LocalStorage)
 * - Preservação da Cadeia de SRC Original (original_src)
 */
(function() {
    // =================================================================
    const API_URL = 'https://tracking.lavishcreative.com';
    const FACEBOOK_PIXEL_ID = '1771320517046203';
    // =================================================================

    const COOKIE_NAME = 'external_id';
    let cachedIp = null;
    let hydratedData = {};

    const STANDARD_EVENTS = ['AddPaymentInfo', 'AddToCart', 'AddToWishlist', 'CompleteRegistration', 'Contact', 'CustomizeProduct', 'Donate', 'FindLocation', 'InitiateCheckout', 'Lead', 'Purchase', 'Schedule', 'Search', 'StartTrial', 'SubmitApplication', 'Subscribe', 'ViewContent', 'PageView'];

    // --- 0. PRESERVAÇÃO DE ATRIBUIÇÃO ORIGINAL (SRC CHAIN) ---
    function captureOriginalSrc() {
        const urlParams = new URLSearchParams(window.location.search);
        const src = urlParams.get('src');
        if (src && !document.cookie.includes('original_src=')) {
            const d = new Date(); d.setTime(d.getTime() + (30*24*60*60*1000));
            document.cookie = `original_src=${src};expires=${d.toUTCString()};path=/;SameSite=Lax;Secure`;
        }
    }
    captureOriginalSrc();

    // --- 1. PERSISTÊNCIA EXTREMA (Blindagem) ---
    function getExternalId() {
        const urlP = new URLSearchParams(window.location.search);
        let id = urlP.get('sck') || urlP.get('external_id');

        if (!id) id = localStorage.getItem('sck_id');

        if (!id) {
            const m = document.cookie.match(new RegExp('(^| )'+COOKIE_NAME+'=([^;]+)'));
            if (m) id = m[2];
        }

        if (!id) id = 'lead_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

        localStorage.setItem('sck_id', id);
        const d = new Date(); d.setTime(d.getTime() + (30*24*60*60*1000));
        document.cookie = `${COOKIE_NAME}=${id};expires=${d.toUTCString()};path=/;SameSite=Lax;Secure`;

        return id;
    }

    const extId = getExternalId();
    window.trackingData = { external_id: extId };

    function getCleanUrl() {
        try {
            const u = new URL(window.location.href);
            u.searchParams.delete('sck');
            u.searchParams.delete('external_id');
            return u.toString();
        } catch (e) { return window.location.href; }
    }

    function getFbc() {
        const f = new URLSearchParams(window.location.search).get('fbclid');
        if(f) return `fb.1.${Date.now()}.${f}`;
        const m = document.cookie.match(/(^| )_fbc=([^;]+)/);
        return m ? m[2] : null;
    }

    // --- 2. BOILERPLATE DO PIXEL ---
    if (!window.fbq) {
        !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
        n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
    }

    // --- 3. FUNÇÃO DE DISPARO ---
    function sendEvent(n, ip, data={}) {
        const eid = n.toLowerCase() + '_' + extId + '_' + Date.now();

        if (typeof fbq === 'function') {
            const method = STANDARD_EVENTS.includes(n) ? 'track' : 'trackCustom';
            fbq(method, n, data, { eventID: eid });
        }

        const pl = {
            event_name: n, event_id: eid, external_id: extId,
            url: getCleanUrl(),
            fbp: (document.cookie.match(/(^| )_fbp=([^;]+)/)||[])[2],
            fbc: getFbc(), target_pixel_id: FACEBOOK_PIXEL_ID
        };
        if(ip) pl.client_ip = ip; else if(cachedIp) pl.client_ip = cachedIp;

        fetch(`${API_URL}/track`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(pl), keepalive: true
        }).catch(()=>{});
    }

    window.trackEvent = function(n, data) { sendEvent(n, cachedIp, data); };

    // --- 4. INICIALIZAÇÃO + RE-HIDRATAÇÃO ---
    async function initSystem() {
        try {
            const res = await fetch(`${API_URL}/hydrate?sck=${extId}`);
            if (res.ok) hydratedData = await res.json();
        } catch(e) {}

        fbq('init', FACEBOOK_PIXEL_ID, { external_id: extId, ...hydratedData });

        fetch('https://api64.ipify.org?format=json')
            .then(r=>r.json()).then(d => {
                cachedIp = d.ip;
                sendEvent('PageView', d.ip);
            })
            .catch(() => {
                sendEvent('PageView', null);
            });
    }

    initSystem();
})();
