---
name: graphic-design
description: Diseño gráfico, assets visuales, imágenes para web y documentos, con la identidad de marca de DETA Consultores. Actívate con cualquier mención de: diseño gráfico, imagen, ilustración, asset, banner, portada, thumbnail, OG image, imagen de portada, imagen para redes sociales, logo, ícono, infografía, diagrama visual, imagen de perfil, cover, header image, visual para presentación, diseño de imagen, crear imagen, generar imagen, mockup, wireframe, diseño para LinkedIn, diseño para Instagram, tarjeta de presentación, diseño de documento. También actívate cuando el usuario quiera que algo "se vea bien" en términos de imagen estática.
---

# Graphic Design — Assets Visuales con Identidad DETA

Diseño de assets gráficos, imágenes para web, redes sociales y documentos. Toda producción visual mantiene la identidad de DETA Consultores.

---

## Sistema de Identidad Visual — Referencia Rápida

### Colores obligatorios
```
Navy:       #0c2b40  ← fondos oscuros, texto principal
Gold:       #d3ab6d  ← acentos, CTAs, detalles
Cyan:       #12a9CC  ← elementos interactivos, íconos
Blanco:     #FFFFFF  ← fondos limpios
Surface:    #F5F7FA  ← fondos alternos
```

### Tipografía
```
Display/Títulos:  Playfair Display — serif elegante
Body/UI:          Source Sans Pro — sans-serif legible
Fallback display: Georgia, serif
Fallback body:    system-ui, sans-serif
```

### Proporciones de espaciado
```
Compacto:   8px
Normal:     16px
Cómodo:     24px
Amplio:     48px
Sección:    80px
```

---

## OG Images — Imágenes para Compartir

### Dimensiones estándar
- **Open Graph (Facebook, LinkedIn, WhatsApp):** 1200×630px
- **Twitter Card:** 1200×628px
- **Instagram Post:** 1080×1080px
- **LinkedIn Banner:** 1584×396px

### Generación con Next.js (recomendado)
```typescript
// app/opengraph-image.tsx — OG global
// app/[page]/opengraph-image.tsx — OG por página
import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function OGImage() {
  return new ImageResponse(
    (
      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0c2b40',
        padding: '60px',
        position: 'relative',
      }}>
        {/* Acento decorativo gold */}
        <div style={{
          position: 'absolute',
          top: 0, left: 0,
          width: '100%', height: '6px',
          background: '#d3ab6d',
        }} />

        {/* Eyebrow */}
        <p style={{
          color: '#d3ab6d',
          fontSize: 18,
          letterSpacing: '0.25em',
          textTransform: 'uppercase',
          fontFamily: 'Georgia, serif',
          marginBottom: 24,
        }}>
          DETA Consultores
        </p>

        {/* Headline */}
        <h1 style={{
          color: '#FFFFFF',
          fontSize: 56,
          fontFamily: 'Georgia, serif',
          fontWeight: 700,
          textAlign: 'center',
          lineHeight: 1.2,
          margin: 0,
          maxWidth: '900px',
        }}>
          Tu Headline Aquí
        </h1>

        {/* Subtítulo */}
        <p style={{
          color: '#94a3b8',
          fontSize: 22,
          fontFamily: 'system-ui, sans-serif',
          textAlign: 'center',
          marginTop: 24,
          maxWidth: '700px',
        }}>
          Consultoría organizacional para empresas en crecimiento
        </p>

        {/* URL */}
        <p style={{
          position: 'absolute',
          bottom: 40,
          color: '#64748b',
          fontSize: 16,
          fontFamily: 'system-ui, sans-serif',
        }}>
          detaconsultores.com
        </p>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

### Variantes de OG Image

**Variante clara (para páginas de servicio):**
```typescript
// Fondo blanco con acento navy
background: '#FFFFFF',
// Title en navy
color: '#0c2b40',
// Borde superior gold
```

**Variante con foto de fondo:**
```typescript
// Requiere fetch de imagen + overlay
backgroundImage: `url(${imageUrl})`,
// Overlay navy semi-transparente
background: 'rgba(12,43,64,0.85)',
```

---

## SVG — Íconos y Gráficos

### Íconos personalizados DETA
```svg
<!-- Ícono de ejemplo — siempre usar viewBox, no width/height fijo -->
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path
    d="M12 2L2 7l10 5 10-5-10-5z"
    stroke="#12a9CC"
    stroke-width="1.5"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
</svg>
```

**Reglas para íconos:**
- Stroke: `1.5` siempre (como Lucide React)
- Color stroke: `#12a9CC` (cyan) para íconos de contenido
- Color stroke: `currentColor` para íconos en componentes (hereda el color del texto)
- Sin fill a menos que sea un ícono sólido
- ViewBox: `0 0 24 24` estándar

### Diagramas y Flowcharts (en SVG)
```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <!-- Nodo -->
  <rect x="50" y="150" width="180" height="60" rx="8"
    fill="#0c2b40" stroke="#d3ab6d" stroke-width="1.5"/>
  <text x="140" y="185" fill="white" text-anchor="middle"
    font-family="system-ui" font-size="14">Fase 1</text>

  <!-- Flecha -->
  <line x1="230" y1="180" x2="310" y2="180"
    stroke="#6B7280" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Definición de flecha -->
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
      markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#6B7280"/>
    </marker>
  </defs>
</svg>
```

---

## Infografías — Estructura

### Infografía de proceso (pasos numerados)
```html
<!-- Template HTML para renderizar como imagen con wkhtmltoimage -->
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Source Sans Pro', system-ui; background: #0c2b40;
    padding: 48px; margin: 0; width: 800px; }
  .eyebrow { color: #d3ab6d; font-size: 12px; letter-spacing: 0.2em;
    text-transform: uppercase; margin-bottom: 8px; }
  .title { color: white; font-size: 32px; font-family: Georgia, serif;
    margin-bottom: 40px; }
  .steps { display: flex; gap: 24px; }
  .step { background: rgba(255,255,255,0.05); border-radius: 12px;
    padding: 24px; flex: 1; border: 1px solid rgba(211,171,109,0.3); }
  .step-num { color: #d3ab6d; font-size: 36px; font-weight: 700;
    font-family: Georgia; margin-bottom: 12px; }
  .step-title { color: white; font-size: 16px; font-weight: 600;
    margin-bottom: 8px; }
  .step-desc { color: #94a3b8; font-size: 13px; line-height: 1.5; }
</style>
</head>
<body>
  <p class="eyebrow">DETA Consultores — Metodología</p>
  <h1 class="title">Nuestro Proceso</h1>
  <div class="steps">
    <div class="step">
      <div class="step-num">01</div>
      <div class="step-title">Diagnóstico</div>
      <div class="step-desc">Analizamos la situación actual de tu empresa</div>
    </div>
    <div class="step">
      <div class="step-num">02</div>
      <div class="step-title">Estrategia</div>
      <div class="step-desc">Diseñamos el plan de transformación</div>
    </div>
    <div class="step">
      <div class="step-num">03</div>
      <div class="step-title">Implementación</div>
      <div class="step-desc">Ejecutamos con tu equipo</div>
    </div>
  </div>
</body>
</html>
```

### Render como imagen
```bash
wkhtmltoimage \
  --width 896 \
  --format png \
  --quality 95 \
  --zoom 2 \
  /tmp/infografia.html \
  /tmp/infografia.png
```

---

## Redes Sociales — Templates

### LinkedIn Post Image (1200×628)
```
Layout: Fondo navy + headline grande + logo DETA
Copy: Dato/insight principal en 1-2 líneas
Estilo: Minimalista, tipografía grande, 1 idea
```

### Instagram Post (1080×1080)
```
Layout: Cuadrado — composición centrada
Opciones: fondo navy, fondo blanco, gradiente sutil
Copy: Headline + dato + @detaconsultores
```

### Twitter/X Header (1500×500)
```
Layout: Panorámico — logo izquierda, claim derecha
Fondo: Navy o foto de equipo con overlay
Claim: "Consultoría organizacional para empresas en crecimiento"
```

---

## Reglas de Producción Visual

1. **Identidad primero** — todo asset usa los tokens de DETA: navy, gold, cyan
2. **Un mensaje por pieza** — no apretar 5 ideas en una imagen
3. **Texto legible** — mínimo 14px en cualquier imagen, 24px para titulares
4. **Contraste** — texto sobre fondo oscuro: blanco o gold. Sobre blanco: navy
5. **Sin stock genérico** — no usar imágenes Unsplash de "handshake de negocios"
6. **Proporciones correctas** — verificar dimensiones antes de entregar
7. **Exportar en el formato correcto** — PNG para transparencia, JPG para fotos
8. **Sin watermarks** — los assets son producción final, no draft
