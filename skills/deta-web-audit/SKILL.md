---
name: deta-web-audit
description: Auditoría completa del frontend de detaconsultores.com. Conoce la arquitectura del sitio, el funnel de conversión, el stack técnico y los tokens de marca. Orquesta los checks de diseño, copy, performance y accesibilidad. Actívate cuando el usuario mencione "auditoría", "revisar el sitio", "audit del front", "cómo está el sitio", "revisar la página", "checar el frontend", "qué hay que mejorar en el sitio" — tanto para producción como para localhost.
---

# DETA Web Audit — Orquestador

Auditoría del frontend de detaconsultores.com. Coordina brand, copy, performance y accesibilidad.
Funciona en producción y en localhost durante desarrollo.

---

## Inputs

| Parámetro | Default | Opciones |
|-----------|---------|----------|
| `url` | `https://detaconsultores.com` | `http://localhost:3000` o cualquier URL base |
| `scope` | `full` | `full`, `funnel`, `[ruta específica]` |
| `checks` | `all` | `brand`, `copy`, `performance`, `a11y`, `all` |

Si el usuario no especifica, usar defaults y preguntar solo si el scope no es claro.

---

## Arquitectura del sitio

### Rutas y propósito

| Ruta | Propósito | Prioridad |
|------|-----------|-----------|
| `/` | Homepage — primera impresión, secciones hero + servicios + credibilidad | Alta |
| `/servicios` | Overview de servicios — nodo de distribución hacia reclutamiento y capacitación | Alta |
| `/reclutamiento` | Página de servicio — 7 secciones, FAQ accordion, CTA principal | Alta |
| `/capacitacion` | Página de servicio — 15 cursos, inversión, CTA | Alta |
| `/metodologia` | Diferenciador — explica el método DETA | Media |
| `/diagnostico-express` | Formulario de 5 preguntas — conversión principal | Alta |
| `/contacto` | Formulario de contacto | Media |
| `/blog` | Listado de 7 posts — featured + grid | Media |
| `/blog/[slug]` | Posts individuales (7 publicados) | Media |
| `/casos-de-exito` | noindex — sin contenido real, pendiente | Baja |

### Funnel principal

```
/ → /servicios → /metodologia → /diagnostico-express → /contacto
```

### Stack

- Next.js 14.2 App Router, TypeScript strict, Tailwind v3
- Fuentes: Playfair Display + Source Sans 3 (next/font/google)
- Sin base de datos — formularios → Google Sheets via Apps Script webhook
- Deploy: push a main → Vercel auto-deploy

### Componentes críticos

| Componente | Archivo | Riesgo |
|------------|---------|--------|
| Header / Footer | `app/layout.tsx` (root) | Afecta todas las rutas |
| FloatingWhatsApp | Root layout | Mobile siempre, desktop delay 3s |
| FAQ accordion | `app/reclutamiento/faq.tsx` | Client component aislado |
| NewsletterForm | `app/blog/NewsletterForm.tsx` | Client component |
| OG images | `*/opengraph-image.tsx` por página | Edge runtime |

### Tokens de marca

| Token | Hex | Uso principal |
|-------|-----|---------------|
| Navy | `#0c2b40` | Headers, fondos oscuros, texto principal |
| Gold | `#d3ab6d` | Acentos, CTAs secundarios, separadores |
| Cyan | `#12a9cc` | CTAs principales, highlights, links activos |

---

## Flujo de auditoría

```
1. Determinar URL base y scope
2. Abrir cada página con Playwright — screenshot desktop + mobile (375px)
3. Correr checks según flags:
   a. Brand  → tokens de color, tipografía, logo, espaciado (skill: deta-brand)
   b. Copy   → tono, CTAs, jerarquía de mensajes (skill: deta-content)
   c. Perf   → Core Web Vitals, tiempos de carga (skill: performance-audit)
   d. A11y   → contraste, aria, teclado, alt texts (skill: a11y-audit)
4. Consolidar hallazgos por página y por categoría
5. Imprimir reporte en consola (formato abajo)
```

---

## Formato del reporte en consola

```
══════════════════════════════════════════════
  DETA WEB AUDIT — [URL BASE]
  Fecha: [YYYY-MM-DD HH:mm]
  Scope: [páginas auditadas]
══════════════════════════════════════════════

── / (Homepage) ──────────────────────────────
  BRAND   ✅ Colores correctos | ⚠ Logo: margen insuficiente en mobile
  COPY    ✅ H1 con keyword | ⚠ CTA secundario sin verbo de acción
  PERF    LCP 1.8s ✅ | CLS 0.02 ✅ | FCP 0.9s ✅
  A11Y    ✅ Sin errores críticos | ⚠ 2 imágenes sin alt text

── /reclutamiento ────────────────────────────
  BRAND   ✅
  COPY    ⚠ Precio visible pero sin contexto de valor previo
  PERF    LCP 2.4s ⚠ | CLS 0.0 ✅
  A11Y    ❌ FAQ accordion no accesible por teclado

...

══════════════════════════════════════════════
  RESUMEN
  ✅ Sin problemas: X páginas
  ⚠  Mejoras recomendadas: Y hallazgos
  ❌ Críticos: Z issues

  TOP 3 PRIORIDADES:
  1. [issue más crítico — ruta + descripción]
  2. [issue — ruta + descripción]
  3. [issue — ruta + descripción]
══════════════════════════════════════════════
```

---

## Reglas

- **Localhost**: si la URL es localhost, omitir checks de SEO (meta, sitemap, robots) — no aplican en dev
- **Scope funnel**: auditar solo `/`, `/servicios`, `/metodologia`, `/diagnostico-express`, `/contacto`
- **Prioridades**: reportar siempre un Top 3 accionable al final — no terminar sin él
- **Sin inventar**: si Playwright no puede cargar una página, reportarlo como error, no asumir que está bien
- **Mobile first**: siempre hacer screenshot a 375px además de desktop

---

## Skills que coordina

| Check | Skill |
|-------|-------|
| Brand | `deta-brand` |
| Copy | `deta-content` |
| Referencia visual | `design-library` |
| Patrones de componentes | `frontend-design` |
| Performance | `performance-audit` |
| Accesibilidad | `a11y-audit` |
