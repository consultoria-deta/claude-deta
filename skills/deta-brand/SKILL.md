---
name: deta-brand
description: Sistema de diseño, tokens de marca, estándares visuales y producción de assets para todo lo que produce DETA Consultores. Fusión de deta-design + graphic-design. Actívate con cualquier mención de: diseño, visual, colores, tipografía, marca, branding, tokens, componentes, UI, UX, estilo, layout, composición, sección, landing page, hero, card, botón, logo, paleta, fuente, espaciado, dark mode, responsive, móvil, desktop, pixel, svg, imagen, gráfico, ilustración, asset, banner, portada, thumbnail, OG image, redes sociales, infografía, diagrama, DALL-E, anti-slop. También actívate cuando se construya cualquier interfaz o documento visual para DETA.
---

# DETA Brand — Sistema de Marca y Producción Visual

Sistema unificado de diseño para DETA Consultores. Cubre UI interactiva (React/Tailwind) y assets estáticos (OG images, redes sociales, PDFs, infografías).

## Estándar visual (obligatorio)

Toda interfaz DETA — incluidas apps internas como DETA Ops — debe verse al nivel de Linear / Superhuman / Notion / Apple HIG. "Decente" o "funcional" **no son aceptables**. La app puede ser interna, pero se presenta ante clientes y debe transmitir la marca.

**Reglas:**
- Nunca usar placeholders visuales tipo "D en cuadro" — buscar el asset real de logo (`logo-deta-cyan.svg`, `logo-deta-white.svg`, `logo-deta-navy.svg` en `deta-web/public/`).
- Tipografía con contraste real de pesos y tamaños. Display serif (Playfair) con presencia; body sans con jerarquía clara. Nunca todo 13px/400.
- Liquid glass DETA: backdrop-blur con tinte navy, capas con profundidad, acentos gold en focus rings y puntos focales de dataviz.
- Motion con propósito: stagger entry (50ms cascade), hover lift cards, spring easing en drawers mobile.
- Mobile: probar viewport 375px real antes de declarar done. Scroll horizontal accidental = bug.
- Antes de cerrar una fase visual: screenshot antes/después + 3 referencias citadas (Linear/Superhuman/Apple/Notion).

**Referencias detalladas:**
- Paleta completa Tech Edition (escalas 50-950, semánticos, elevación, liquid glass, dark mode, motion) → `references/color-system.md`
- Export e impresión (WeasyPrint, reportlab, Playwright) → `references/print-export.md`

## Tokens Tech (extensión de la paleta — sin reemplazar core)

Los 3 tokens históricos son inmutables: `navy #0c2b40`, `gold #d3ab6d`, `cyan #12a9cc`. Todo lo demás son **derivados** para UI densa tipo Linear/Superhuman/Notion.

**Resumen rápido (detalle completo en `references/color-system.md`):**

- **Escalas 50–950** para navy, cyan, gold y **slate** (cool gray con undertone navy — reemplaza grays neutros que destiñen sobre navy).
- **Semánticos alineados**: `success #10b981`, `warning #d3ab6d` (gold reutilizado), `danger #e0556f` (coral, no rojo tomate), `info #12a9cc`.
- **Elevation**: stack de sombras con tinte navy (`rgba(12,43,64,*)`), `--shadow-glow-cyan` / `--shadow-glow-gold`, focus rings con offset navy-950.
- **Liquid glass DETA**: `--glass-panel` (navy 72% + blur 24px + saturate 1.2), `--glass-card` (white 3% + blur 16px), `--glass-input` (white 4% + blur 8px).
- **Dark mode**: canvas `navy-950 #040f1c`, surface `slate-800`, cyan se mantiene brillante, gold sube a `gold-300` para AA.
- **Motion**: `--duration-fast 120ms / base 200ms / slow 360ms`, `--ease-out cubic-bezier(0.22,1,0.36,1)`, `--ease-spring`.
- **Tipografía tech**: añade `'JetBrains Mono'` para código, IDs, data densa; `.tabular { font-variant-numeric: tabular-nums }` para KPIs y tablas.

**Cuándo aplicar qué:**
- Sitio público detaconsultores.com → paleta clásica (navy/gold/cyan + white/surface).
- Apps internas (DETA Ops) → Tech Edition obligatoria: escalas slate, liquid glass, dark mode, motion tokens.
- PDFs / print → clásica, nunca cyan en tinta.

---

## Tokens Oficiales

### Colores

| Token | Hex | Uso |
|---|---|---|
| `primary` | `#0c2b40` | Navy — header, footer, texto principal, fondos oscuros |
| `secondary` | `#d3ab6d` | Gold — CTAs, underlines, acentos sobre fondo claro |
| `accent` | `#12a9cc` | Cyan — iconos, links, elementos interactivos |
| `background` | `#FFFFFF` | Canvas principal |
| `surface` | `#F5F7FA` | Secciones alternas |
| `text-primary` | `#1A1A2E` | Texto principal |
| `text-muted` | `#6B7280` | Texto secundario, labels |
| `border` | `rgba(12,43,64,0.1)` | Bordes sutiles |

**Proporciones de uso por pieza:**
```
Navy:    50% — fondo dominante, estructura
Blanco:  25% — canvas, respiración
Surface: 13% — bloques alternos
Gold:     7% — acentos, CTAs, detalles
Cyan:     5% — íconos, interactivos, highlights
```

**Reglas de color:**
1. Un color dominante por página — nunca navy y blanco compitiendo como fondo simultáneo
2. Gold y cyan permitidos sobre navy — nunca navy sobre navy ni cyan sobre cyan
3. Sobre fondos claros: navy para texto, gold para acentos, cyan para íconos
4. Navy solo en footer, hero oscuro, CTA de cierre
5. Cero colores fuera de la paleta — nunca hex inventados inline
6. Contraste mínimo 4.5:1 antes de cualquier decisión estética

### CSS Variables (copiar en `globals.css`)
```css
:root {
  --color-primary: #0c2b40;
  --color-secondary: #d3ab6d;
  --color-accent: #12a9cc;
  --color-background: #FFFFFF;
  --color-surface: #F5F7FA;
  --color-text-primary: #1A1A2E;
  --color-text-muted: #6B7280;
  --color-border: rgba(12,43,64,0.1);

  --font-display: 'Playfair Display', Georgia, serif;
  --font-sans: 'Source Sans Pro', system-ui, sans-serif;

  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-section: 80px;

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

### Tipografía

| Elemento | Fuente | Size desktop | Size mobile | Weight |
|---|---|---|---|---|
| H1 | Playfair Display | 48-56px | 32-36px | 700 |
| H2 | Playfair Display | 32-40px | 26-28px | 600 |
| H3 | Source Sans Pro | 22-26px | 20-22px | 600 |
| Body | Source Sans Pro | 16-18px | 16px | 400 |
| Label | Source Sans Pro | 12-14px | 12px | 600 uppercase |
| Eyebrow | Source Sans Pro | 12-14px | 12px | 700 uppercase |

### Espaciado — Sistema 8pt
- `4px` — dentro de elementos pequeños
- `8px` — entre elementos relacionados
- `16px` — entre elementos del mismo grupo
- `24px` — padding de cards
- `32px` — separación entre secciones cercanas
- `48px` — entre secciones mobile
- `80px` — entre secciones desktop ← default

**Regla crítica: 80px entre secciones desktop. Nunca secciones pegadas.**

### Iconografía
- Librería: Lucide React exclusivamente
- Stroke: `1.5` en todos
- Color: `accent` (#12a9cc) por defecto
- Tamaño: `24px` contenido, `20px` elementos pequeños

---

## Logo — Assets y Reglas de Uso

### Assets PNG disponibles

| Archivo | Color logo | Uso |
|---|---|---|
| `logo-deta-cyan.png` | Cyan `#12a9cc` | Fondos claros — blanco, surface, gris claro |
| `logo-deta-white.png` | Blanco `#FFFFFF` | Fondos oscuros — navy, headers oscuros |

**Reglas de uso:**
- Logo cyan → solo sobre fondo claro
- Logo blanco → solo sobre fondo navy u oscuro
- Nunca logo cyan sobre navy (el contraste desaparece)
- Ancho mínimo digital: 180px — Ancho mínimo impresión: 40mm
- Zona de exclusión: 1X (altura de la "D") en todos los lados
- Favicon: solo el ícono D, 32×32px mínimo

### En `deta_pdf_base.py` (PDFs)

```python
from deta_pdf_base import LOGO_PNG_PATH, LOGO_WHITE_PATH

# draw_header() selecciona automáticamente según bg_color
draw_header(c, bg_color=NAVY)     # → logo blanco automático
draw_header(c, bg_color=SURFACE)  # → logo cyan automático
draw_header_light(c)              # wrapper explícito para header claro
```

---

## Anti-Slop — Las 6 Categorías a Evitar

### 1. Gradientes Locros
❌ Gradientes de 3-4 colores, gradientes en mitad de contenido, gradientes en botones
✅ Máximo 1 gradiente por página, solo en hero o CTA de cierre

### 2. Decoración Vacía
❌ Líneas decorativas sin función, iconos que no comunican, badges sin información
✅ Cada elemento tiene propósito — si no comunica, no está

### 3. Paleta Arcoíris
❌ Más de 3 colores de fondo en una página
✅ Blanco dominante + un alterno gris claro + navy solo en cierre

### 4. Composición Lenta
❌ Secciones apiladas sin respiro, cards idénticas en tamaño
✅ Whitespace generoso, jerarquía de tamaño entre secciones

### 5. Tipografía Débil
❌ Headlines descriptivos ("Somos una empresa"), todo del mismo peso
✅ Headlines declarativos, peso visual diferenciado entre niveles

### 6. CTAs Ansiosos
❌ 3 botones de CTA en la misma viewport, urgencia artificial
✅ 1 CTA por sección, invitación — no demanda

---

## 8 Mandamientos Anti-Slop

1. **1 idea por viewport** — si hay más de un pensamiento, hay más de una sección
2. **Whitespace = confianza** — si se siente vacío, probablemente está correcto
3. **Si se puede comprar en ThemeForest, no es premium**
4. **El copy es diseño** — un mal copy arruina el mejor layout
5. **Reducir, no añadir** — cuando dudes, quita
6. **La jerarquía se siente antes de leerse** — si hay que leer para entender qué es más importante, la jerarquía falló
7. **CTAs claros, no ansiosos** — una acción, descrita con exactitud
8. **Make it obvious** — el hero comunica en 5 segundos qué hace DETA

---

## Identidad Verbal — Referencia Rápida

**Posicionamiento central:**
"Transformamos talento en arquitectura."

**Arquetipo:** El Socio Estratégico — está en las trincheras con el cliente, no en la tribuna.

**Resultado prometido:** "Mi empresa ya no depende de mí para funcionar."

**Vocabulario prohibido** (nunca usar en copy de ninguna pieza):
- Potenciar / Empoderar
- Holístico / Sinergia
- Best practices / Robusto / Innovador / World-class
- Soluciones integrales / Capital humano
- Apasionados por / Expertos en

**Tono:** Cálido y cercano — técnico pero humano. Directo, concreto, activo. Nunca voz pasiva donde pueda usarse activa.

---

## Jerarquía Visual — 5 Niveles

1. **Viewport goal** — qué quiero que el usuario haga o entienda
2. **Headline** — máximo 10 palabras, declarativo
3. **Soporte** — subheadline o contexto, 1-2 líneas
4. **Evidencia** — dato, ejemplo o prueba breve
5. **CTA** — una acción, no tres

---

## Layout — Composición Web

### Viewport
- Una idea por viewport — el scroll es narrativa, no lista
- Mínimo 50vh por sección en desktop

### Header
- Sticky, `backdrop-blur-sm`
- Logo: "DETA" en `secondary`, "Consultores" en `primary`, mismo peso
- Navegación: máximo 5 items
- CTA gold siempre visible

### Footer
- Fondo navy `#0c2b40`
- 4 columnas: Logo+propuesta, Empresa, Servicios, Contacto
- Links blancos, hover gold
- Información de contacto real — nunca placeholder

### Fondos por página
- Máximo 2 fondos distintos
- `#FFFFFF` canvas base
- `#F5F7FA` para separar bloques alternos
- Navy `#0c2b40` solo footer y CTA de cierre

---

## Sistema de Cards

| Regla | Detalle |
|---|---|
| Borde O sombra — nunca ambos | Borde: `border border-black/5` / Sombra: `shadow-[0_2px_8px_rgba(0,0,0,0.06)]` |
| Hover | Agregar sutil lo que no tiene (si tiene borde → sombra en hover) |
| Padding interno | Mínimo 24px |
| Título | Playfair Display 20-24px |
| Sin badges decorativos | Solo badges con información real |

---

## OG Images — Estándar

### Dimensiones
- **Open Graph (Facebook, WhatsApp):** 1200×630px
- **Twitter Card:** 1200×628px
- **Instagram Post:** 1080×1080px
- **LinkedIn Banner:** 1584×396px — canal no activo

### Generación con Next.js (recomendado)
```typescript
// app/[page]/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function OGImage() {
  return new ImageResponse(
    <div style={{
      width: '100%', height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      background: '#0c2b40', padding: '60px', position: 'relative',
    }}>
      {/* Acento gold superior */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '6px', background: '#d3ab6d' }} />
      {/* Eyebrow */}
      <p style={{ color: '#d3ab6d', fontSize: 18, letterSpacing: '0.25em', textTransform: 'uppercase', fontFamily: 'Georgia, serif', marginBottom: 24 }}>
        DETA Consultores
      </p>
      {/* Headline */}
      <h1 style={{ color: '#FFFFFF', fontSize: 56, fontFamily: 'Georgia, serif', fontWeight: 700, textAlign: 'center', lineHeight: 1.2, margin: 0, maxWidth: '900px' }}>
        Tu Headline Aquí
      </h1>
      {/* Subtítulo */}
      <p style={{ color: '#94a3b8', fontSize: 22, fontFamily: 'system-ui, sans-serif', textAlign: 'center', marginTop: 24, maxWidth: '700px' }}>
        Consultoría organizacional para empresas en crecimiento
      </p>
      {/* URL */}
      <p style={{ position: 'absolute', bottom: 40, color: '#64748b', fontSize: 16, fontFamily: 'system-ui, sans-serif' }}>
        detaconsultores.com
      </p>
    </div>,
    { width: 1200, height: 630 }
  )
}
```

---

## Blog Hero Images — Generación Programática

Hero images de blog se generan con `~/research/hero_gen.py` — HTML/SVG renderizado a PNG via Playwright. No se usa DALL-E.

### Specs
- **Dimensiones:** 1200×675px (16:9)
- **Fondo:** Navy `#0c2b40` con grid sutil (rgba cyan a 0.04 opacity)
- **Colores:** Solo paleta DETA — navy, cyan `#12a9CC`, gold `#d3ab6d`
- **Estilo:** Abstracto, geométrico, sin texto, sin personas, sin fotos

### Metáforas por pilar

| Pilar | Metáfora | Descripción |
|-------|----------|-------------|
| `estrategia` | Convergencia | Líneas caóticas → nodo central → árbol ordenado |
| `organizacion` | Convergencia | Misma base, variante distinta por slug |
| `comercial` | Embudo | Partículas dispersas arriba → concentradas → salida |
| `finanzas` | Dashboard | Barras crecientes + línea de tendencia gold + KPIs |
| `talento` | Red | Nodos interconectados, líder central gold, roles cyan |

### Uso
```bash
# Generar hero para un artículo
python3 ~/research/hero_gen.py --pilar comercial --slug embudo-de-ventas-no-funciona

# Preview de todos los pilares
python3 ~/research/hero_gen.py --all
```

Cada slug genera una variante única (seed determinista del slug). Mismo slug = misma imagen siempre.

### Restricciones
- Sin texto overlay — el título va en el HTML del blog, no en la imagen
- Sin logos — la imagen es abstracta pura
- Opacidades bajas (0.1-0.6) para mantener el estilo sutil
- Los nodos gold se reservan para puntos focales (máx 3-5 por imagen)

---

## SVG — Íconos y Gráficos

### Reglas para íconos SVG
- Stroke: `1.5` siempre (consistente con Lucide React)
- Color stroke: `#12a9cc` (cyan) para íconos de contenido
- Color stroke: `currentColor` para íconos en componentes
- Sin fill a menos que sea un ícono sólido
- ViewBox: `0 0 24 24` estándar

### Diagramas y Flowcharts
```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="150" width="180" height="60" rx="8"
    fill="#0c2b40" stroke="#d3ab6d" stroke-width="1.5"/>
  <text x="140" y="185" fill="white" text-anchor="middle"
    font-family="system-ui" font-size="14">Fase 1</text>
  <line x1="230" y1="180" x2="310" y2="180"
    stroke="#6B7280" stroke-width="1.5" marker-end="url(#arrow)"/>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
      markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#6B7280"/>
    </marker>
  </defs>
</svg>
```

---

## Infografías — Template HTML

```html
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
  .step-title { color: white; font-size: 16px; font-weight: 600; margin-bottom: 8px; }
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
  </div>
</body>
</html>
```

```bash
# Render como imagen
wkhtmltoimage --width 896 --format png --quality 95 --zoom 2 /tmp/infografia.html /tmp/infografia.png
```

---

## DALL-E — Generación de Imágenes

### Prompt base DETA
```
Editorial illustration, dark navy #0c2b40 background,
gold #d3ab6d accent details, cyan #12a9cc highlights,
clean minimal composition, no people, abstract geometric
elements suggesting organizational structure and growth,
high contrast, professional consulting aesthetic.
Style: {FORMAT_STYLE}. Dimensions: {SIZE}.
Topic context: {POST_TITLE}
```

### Variables por formato
| Formato | FORMAT_STYLE | SIZE |
|---|---|---|
| Blog header | flat design, wide panoramic | 1792x1024 |
| Carrusel cover | bold centered composition | 1024x1024 |
| Instagram post | editorial magazine | 1792x1024 |

### Reglas
- Nunca personas ni caras — ilustración abstracta siempre
- Navy como fondo dominante en el 80% de las imágenes
- Gold como único acento cálido — no agregar otros colores
- Pedir `quality="hd"` siempre en la API

---

## QA Visual — Checklist Anti-Slop

**Jerarquía:**
- [ ] El headline se lee en 3 segundos sin esfuerzo
- [ ] No más de 3 niveles de peso visual compitiendo
- [ ] El CTA es el elemento más visible de su viewport

**Composición:**
- [ ] Mínimo 80px entre secciones desktop
- [ ] Cards con 24px padding mínimo
- [ ] No hay 2 elementos del mismo tamaño sin jerarquía

**Color:**
- [ ] Solo colores de la paleta oficial
- [ ] No más de 2 fondos por página
- [ ] Gold y cyan no compiten entre sí

**CTAs:**
- [ ] Solo 1 CTA visible por sección
- [ ] El CTA es claro y accionable
- [ ] Sin urgencia artificial

**Anti-slop:**
- [ ] No parece ThemeForest
- [ ] Sin gradientes múltiples
- [ ] Sin quotes decorativos grandes con opacity
- [ ] Sin iconos decorativos sin función
- [ ] Sin badges genéricos sin información
- [ ] Sin imágenes Unsplash genéricas en hero

**Producción:**
- [ ] Sin placeholder, TODO, XXX
- [ ] Sin links a páginas inexistentes
- [ ] Email: consultoria@detaconsultores.com — Web: detaconsultores.com
- [ ] Sin errores ortográficos
- [ ] Footer completo con información real

**Assets estáticos:**
- [ ] Proporciones correctas verificadas antes de entregar
- [ ] PNG para transparencia, JPG para fotos
- [ ] Sin watermarks — los assets son producción final
- [ ] Texto mínimo 14px en cualquier imagen, 24px para titulares
