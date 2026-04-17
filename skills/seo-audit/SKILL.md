---
name: seo-audit
description: Auditoría SEO técnica y on-page completa de sitios web. Actívate con cualquier mención de: auditoría SEO, audit SEO, revisar sitio, qué problemas tiene el sitio, errores SEO, SEO técnico, Screaming Frog, Core Web Vitals, velocidad del sitio, indexación, canonical, robots.txt, sitemap, redirecciones, links rotos, meta tags, schema markup, structured data, og tags, twitter cards, crawl, rastreo, indexar, Google Search Console, posicionamiento orgánico, por qué no rankea. También actívate cuando el usuario quiera mejorar el SEO de un sitio existente.
---

# SEO Audit — Auditoría Técnica y On-Page

Auditoría completa de SEO técnico y on-page. Detecta problemas que impiden posicionamiento y genera un plan de acción priorizado.

---

## Tipos de Auditoría

| Tipo | Cuándo | Tiempo estimado |
|---|---|---|
| **Rápida** — solo on-page | Antes de publicar una página nueva | 15 min |
| **Técnica** — Screaming Frog | Revisión periódica o después de cambios grandes | 30-45 min |
| **Completa** — técnica + contenido + GEO | Baseline inicial o diagnóstico para cliente | 60-90 min |

---

## Auditoría On-Page — Checklist por Página

### Title Tag
- [ ] Existe en `metadata` de Next.js o `<title>` tag
- [ ] Keyword principal al inicio del title
- [ ] 50-60 caracteres máximo
- [ ] Formato: `Keyword | DETA Consultores` o `Keyword — DETA Consultores`
- [ ] Único (no duplicado en otras páginas)

### Meta Description
- [ ] Existe en metadata
- [ ] 150-160 caracteres (no más, Google lo trunca)
- [ ] Keyword principal incluida naturalmente
- [ ] CTA incluido: "Agenda tu diagnóstico...", "Descubre cómo..."
- [ ] Única (no duplicada)

### Headings
- [ ] Un solo H1 por página
- [ ] H1 contiene la keyword principal
- [ ] H2s son subsecciones lógicas con keywords LSI
- [ ] No saltar niveles (H1 → H3 sin H2)
- [ ] No más de 5 H2s principales por página

### Open Graph + Twitter Card
```typescript
// Verificar en metadata de Next.js
openGraph: {
  title: '...',          // ✅ existe
  description: '...',    // ✅ 1-2 líneas
  type: 'website',       // ✅ correcto para páginas estáticas
  url: '...',            // ✅ URL canónica completa
  siteName: 'DETA Consultores', // ✅
  images: [{ url: '...', width: 1200, height: 630 }] // ✅ OG image
},
twitter: {
  card: 'summary_large_image', // ✅
  title: '...',
  description: '...',
}
```

### JSON-LD / Structured Data
```typescript
// En layout.tsx para toda la app
const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'ProfessionalService',
  name: 'DETA Consultores',
  url: 'https://detaconsultores.com',
  telephone: '+52-XXX-XXX-XXXX',
  address: { '@type': 'PostalAddress', addressCountry: 'MX' },
  sameAs: ['https://linkedin.com/company/detaconsultores'],
}
```

### URLs y Canonicals
- [ ] URL slug con keyword: `/consultoria-organizacional`
- [ ] Sin mayúsculas ni caracteres especiales en URL
- [ ] `<link rel="canonical">` apunta a la URL correcta
- [ ] Sin parámetros UTM en canonical

---

## Auditoría Técnica — Screaming Frog

### Ejecutar Crawl
```bash
# Audit completo headless
/Applications/Screaming\ Frog\ SEO\ Spider.app/Contents/MacOS/ScreamingFrogSEOSpider \
  --crawl https://detaconsultores.com \
  --headless \
  --output-folder /tmp/seo-audit-$(date +%Y%m%d) \
  --export-csv "All:All"

# Revisar archivos generados
ls /tmp/seo-audit-$(date +%Y%m%d)/
```

### Qué Revisar en los CSVs

**1. Response Codes — Errores HTTP**
```bash
# Links rotos (404)
grep ",404," /tmp/seo-audit-*/response_codes.csv

# Redirecciones (301/302)
grep ",30[12]," /tmp/seo-audit-*/response_codes.csv
```
Acción: Cada 404 → crear redirect 301. Cadenas de redirects > 1 salto → acortar.

**2. Page Titles — Problemas de Titles**
Filtrar: título vacío, duplicado, muy corto (<30 chars), muy largo (>60 chars)

**3. Meta Descriptions**
Filtrar: descripción vacía, duplicada, muy corta (<70 chars), muy larga (>160 chars)

**4. H1 — Headings**
Filtrar: sin H1, H1 duplicado en página, múltiples H1 en la misma página

**5. Images — Alt Text**
Filtrar: imágenes sin alt text

**6. Directives — Indexación**
Filtrar: páginas con `noindex` que no deberían tenerlo

---

## Core Web Vitals — Verificación

```bash
# Usar PageSpeed Insights (gratis, datos reales de Google)
web_fetch: https://pagespeed.web.dev/report?url=https://detaconsultores.com

# O via API (sin key para móvil/desktop)
web_fetch: https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://detaconsultores.com&strategy=mobile
```

**Umbrales objetivo (Google):**
| Métrica | Bueno | Necesita mejora | Malo |
|---|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5-4s | > 4s |
| INP (Interaction to Next Paint) | < 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 |

---

## GEO Audit — Visibilidad en IA

Verificar que los crawlers de IA puedan acceder al sitio:

```bash
# Revisar robots.txt
web_fetch: https://detaconsultores.com/robots.txt
```

**robots.txt ideal:**
```
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: https://detaconsultores.com/sitemap.xml
```

**Señales de citabilidad para IA:**
- [ ] Contenido con respuestas directas a preguntas del sector
- [ ] Bloques de 134-167 palabras que resuelven una pregunta específica
- [ ] Datos y estadísticas con fuente citada
- [ ] Schema FAQ en páginas con preguntas frecuentes
- [ ] llms.txt en la raíz del sitio (nuevo estándar emergente)

---

## Sitemap — Verificación

```bash
# Verificar sitemap
web_fetch: https://detaconsultores.com/sitemap.xml
```

**Verificar:**
- [ ] Todas las páginas públicas están incluidas
- [ ] Sin páginas 404 o redirigidas en el sitemap
- [ ] `lastmod` actualizado
- [ ] Sitemap registrado en Google Search Console

---

## Formato de Entrega — Audit Report

```markdown
# SEO Audit: detaconsultores.com
**Fecha:** [fecha] | **Tipo:** [Rápida/Técnica/Completa]

## Resumen Ejecutivo
**Score estimado:** [X/10]
**Problemas críticos:** [N]
**Problemas moderados:** [N]
**Oportunidades:** [N]

## Problemas Críticos (resolver esta semana)
1. **[Problema]** — [Página/sección] — [Impacto] — **Fix:** [acción concreta]

## Problemas Moderados (resolver este mes)
...

## Oportunidades de Mejora
...

## On-Page por Página
| Página | Title ✅/❌ | Meta ✅/❌ | H1 ✅/❌ | OG ✅/❌ | Schema ✅/❌ |
|---|---|---|---|---|---|

## Core Web Vitals
| Métrica | Mobile | Desktop | Estado |
|---|---|---|---|

## Plan de Acción Priorizado
**Semana 1:** [acciones críticas]
**Mes 1:** [acciones moderadas]
**Trimestre:** [mejoras y oportunidades]
```

---

## Frecuencia Sugerida

- **Antes de publicar cualquier página nueva** — checklist on-page básico
- **Mensual** — verificar Core Web Vitals y nuevos 404s
- **Trimestral** — audit técnico completo con Screaming Frog
- **Semestral** — audit completo técnico + contenido + GEO
- **Después de rediseño** — audit completo inmediato
