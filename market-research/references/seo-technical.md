# SEO On-Page — Web Builder Reference

## Title Tags

- **Longitud ideal:** 50-60 caracteres
- **Estructura:** `Keyword Principal | Brand` o `Keyword + Beneficio | Brand`
- **Ejemplo:** `Consultoría Organizacional | DETA Consultores`

## Meta Descriptions

- **Longitud ideal:** 150-160 caracteres
- **Estructura:** Hook + keyword + CTA
- **Ejemplo:** "Consultoría para empresas que quieren crecer. Diagnóstico, estructura y ejecución. +15 años de experiencia. Agenda tu primera sesión gratis."

## Heading Hierarchy

```
H1 (1 por página) — Keyword principal
  H2 — Secciones principales
    H3 — Subsecciones
      H4 — Detalles (usar sparingly)
```

## Schema Markup

### Organization
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "DETA Consultores",
  "url": "https://detaconsultores.com",
  "logo": "https://detaconsultores.com/logo.png",
  "description": "Consultoría organizacional, comercial y financiera",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Chihuahua",
    "addressCountry": "MX"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+52-XXX-XXX-XXXX",
    "contactType": "customer service"
  }
}
```

### LocalBusiness (alternativa)
```json
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "DETA Consultores",
  "image": "https://detaconsultores.com/logo.png",
  "priceRange": "$$$$",
  "address": {
    "@type": "PostalAddress",
    "addressRegion": "CHIH",
    "addressCountry": "MX"
  },
  "telephone": "+52-XXX-XXX-XXXX",
  "email": "contacto@detaconsultores.com"
}
```

## Core Web Vitals

| Métrica | Qué mide | Target |
|---|---|---|
| LCP (Largest Contentful Paint) | Velocidad de carga del contenido principal | < 2.5s |
| FID (First Input Delay) | Tiempo hasta que la página responde | < 100ms |
| CLS (Cumulative Layout Shift) | Estabilidad visual durante carga | < 0.1 |

## Open Graph Tags

```html
<meta property="og:title" content="Título de la página">
<meta property="og:description" content="Descripción para social">
<meta property="og:image" content="https://ejemplo.com/og-image.jpg">
<meta property="og:url" content="https://ejemplo.com/pagina">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DETA Consultores">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Título">
<meta name="twitter:description" content="Descripción">
<meta name="twitter:image" content="https://ejemplo.com/og-image.jpg">
```

## Canonical URLs

```html
<link rel="canonical" href="https://ejemplo.com/pagina-canonica">
```

## Image Optimization

```html
<!-- Modern format con fallback -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Descripción" loading="lazy" width="800" height="600">
</picture>
```

## Robots.txt

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: https://detaconsultores.com/sitemap.xml
```

## Sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://detaconsultores.com/</loc>
    <lastmod>2026-04-07</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://detaconsultores.com/servicios/</loc>
    <lastmod>2026-04-07</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```
