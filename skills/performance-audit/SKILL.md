---
name: performance-audit
description: Auditoría de performance web — Core Web Vitals, tiempos de carga y oportunidades de optimización. Usa Playwright para medir métricas reales y Lighthouse CLI si está disponible. Actívate cuando el usuario mencione "performance", "velocidad del sitio", "Core Web Vitals", "LCP", "CLS", "qué tan rápido carga", "Lighthouse", "optimizar carga" — tanto en producción como en localhost.
---

# Performance Audit

Mide Core Web Vitals y tiempos de carga usando Playwright. Usa Lighthouse CLI como capa adicional si está instalado.

---

## Inputs

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `url` | requerido | URL completa de la página a auditar |
| `device` | `both` | `desktop`, `mobile`, `both` |
| `runs` | `1` | Número de corridas para promediar (3 para mayor precisión) |

---

## Paso 1 — Verificar herramientas disponibles

```bash
# ¿Lighthouse CLI instalado?
npx lighthouse --version 2>/dev/null && echo "lighthouse: ok" || echo "lighthouse: no disponible"
```

Usar Lighthouse si está disponible. Si no, usar solo Playwright Navigation Timing API.

---

## Paso 2 — Medir con Playwright

```javascript
// Abrir página y capturar métricas de Navigation Timing
const metrics = await page.evaluate(() => {
  const nav = performance.getEntriesByType('navigation')[0];
  const paint = performance.getEntriesByType('paint');
  return {
    ttfb:        nav.responseStart - nav.requestStart,
    fcp:         paint.find(p => p.name === 'first-contentful-paint')?.startTime,
    domLoaded:   nav.domContentLoadedEventEnd - nav.startTime,
    loadComplete: nav.loadEventEnd - nav.startTime,
    transferSize: nav.transferSize,
    encodedSize:  nav.encodedBodySize,
  };
});

// LCP via PerformanceObserver (aproximado en Playwright)
const lcp = await page.evaluate(() => new Promise(resolve => {
  let lcpValue = 0;
  const observer = new PerformanceObserver(list => {
    const entries = list.getEntries();
    lcpValue = entries[entries.length - 1].startTime;
  });
  observer.observe({ type: 'largest-contentful-paint', buffered: true });
  setTimeout(() => resolve(lcpValue), 3000);
}));
```

---

## Paso 3 — Lighthouse (si disponible)

```bash
# Desktop
npx lighthouse [URL] \
  --output=json \
  --chrome-flags="--headless --no-sandbox" \
  --preset=desktop \
  --only-categories=performance \
  --quiet \
  2>/dev/null | jq '{score: .categories.performance.score, lcp: .audits["largest-contentful-paint"].numericValue, cls: .audits["cumulative-layout-shift"].numericValue, fcp: .audits["first-contentful-paint"].numericValue, tbt: .audits["total-blocking-time"].numericValue, si: .audits["speed-index"].numericValue}'

# Mobile (throttling 4G)
npx lighthouse [URL] \
  --output=json \
  --chrome-flags="--headless --no-sandbox" \
  --preset=perf \
  --only-categories=performance \
  --quiet \
  2>/dev/null | jq '{score: .categories.performance.score, lcp: .audits["largest-contentful-paint"].numericValue, cls: .audits["cumulative-layout-shift"].numericValue}'
```

---

## Umbrales de referencia

| Métrica | ✅ Bueno | ⚠ Mejorar | ❌ Crítico |
|---------|----------|-----------|-----------|
| LCP | < 2.5s | 2.5–4s | > 4s |
| CLS | < 0.1 | 0.1–0.25 | > 0.25 |
| FCP | < 1.8s | 1.8–3s | > 3s |
| TTFB | < 0.8s | 0.8–1.8s | > 1.8s |
| TBT | < 200ms | 200–600ms | > 600ms |
| Lighthouse score | > 90 | 50–90 | < 50 |

---

## Oportunidades comunes en Next.js / Vercel

Al analizar los resultados, revisar específicamente:

| Área | Qué buscar |
|------|-----------|
| Imágenes | `<img>` sin `next/image`, sin `priority` en LCP image, sin dimensiones explícitas |
| Fuentes | Flash de fuente si next/font no está configurado con `display: swap` |
| JS | Chunks grandes, third-party scripts bloqueantes |
| CSS | Tailwind purge configurado, no cargar estilos no usados |
| Server | TTFB alto en rutas dinámicas — revisar si necesitan ISR o SSG |

---

## Formato de output en consola

```
── PERFORMANCE: [URL] ([device]) ──────────────
  Lighthouse score : 87/100 ⚠
  LCP              : 2.1s ✅
  CLS              : 0.04 ✅
  FCP              : 0.9s ✅
  TTFB             : 0.3s ✅
  TBT              : 380ms ⚠

  Oportunidades:
  ⚠ /blog — imagen hero sin `priority` (impacta LCP ~0.6s)
  ⚠ /reclutamiento — chunk de FAQ 42KB, candidato a lazy load
  ❌ /diagnostico-express — CLS 0.31 por layout shift en formulario
```

---

## Notas

- **Localhost**: los tiempos serán menores que en producción — mencionar esto en el reporte
- **Múltiples corridas**: si `runs > 1`, promediar LCP y FCP, tomar el máximo de CLS
- **Sin Lighthouse en CI**: si el entorno no tiene Chrome, usar solo Playwright Timing API y notificar
