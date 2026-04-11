---
name: deta-design
description: Sistema de diseño, tokens de marca y estándares visuales para todo lo que produce DETA Consultores. Actívate con cualquier mención de: diseño, visual, colores, tipografía, marca, branding, tokens, componentes, UI, UX, estilo, layout, composición, sección, landing page, hero, card, botón, logo, paleta, fuente, espaciado, dark mode, responsive, móvil, desktop, pixel, svg, imagen, gráfico, ilustración, anti-slop. También actívate cuando se construya cualquier interfaz o documento visual para DETA.
---

# DETA Design — Sistema de Marca y Estándares Visuales

Sistema de diseño para DETA Consultores. Todo lo visual parte de aquí: colores, tipografía, espaciado, composición y reglas anti-slop.

**Referencias detalladas:**
- Paleta completa y usos → `references/color-system.md`
- Export e impresión → `references/print-export.md`

---

## Tokens Oficiales

### Colores

| Token | Hex | Uso |
|---|---|---|
| `primary` | `#0c2b40` | Navy — header, footer, texto principal, fondos oscuros |
| `secondary` | `#d3ab6d` | Gold — CTAs, underlines, acentos sobre fondo claro |
| `accent` | `#12a9CC` | Cyan — iconos, links, elementos interactivos |
| `background` | `#FFFFFF` | Canvas principal |
| `surface` | `#F5F7FA` | Secciones alternas |
| `text-primary` | `#1A1A2E` | Texto principal |
| `text-muted` | `#6B7280` | Texto secundario, labels |
| `border` | `rgba(12,43,64,0.1)` | Bordes sutiles |

**Reglas de color:**
1. Un color dominante por página — nunca navy y blanco compitiendo como fondo simultáneo
2. Gold y cyan sobre fondo claro — nunca sobre oscuro
3. Navy solo en footer, hero oscuro, CTA de cierre
4. Cero colores fuera de la paleta — nunca hex inventados inline
5. Contraste mínimo 4.5:1 antes de cualquier decisión estética

### CSS Variables (copiar en `globals.css`)
```css
:root {
  --color-primary: #0c2b40;
  --color-secondary: #d3ab6d;
  --color-accent: #12a9CC;
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
- Color: `accent` (#12a9CC) por defecto
- Tamaño: `24px` contenido, `20px` elementos pequeños

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

## Jerarquía Visual — 5 Niveles

1. **Viewport goal** — qué quiero que el usuario haga o entienda
2. **Headline** — máximo 10 palabras, declarativo
3. **Soporte** — subheadline o contexto, 1-2 líneas
4. **Evidencia** — dato, ejemplo o prueba breve
5. **CTA** — una acción, no tres

---

## Layout — Composición

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

## QA Visual — Checklist Anti-Slop

Antes de considerar una sección o página terminada:

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
- [ ] Teléfono y email reales
- [ ] Sin errores ortográficos
- [ ] Footer completo con información real

---

## OG Images — Estándar

Para compartir en redes, cada página debe tener OG image:
- Dimensiones: 1200×630px
- Fondo navy `#0c2b40` o blanco `#FFFFFF`
- Logo DETA visible
- Headline de la página en Playfair Display
- Sin texto menor a 24px (ilegible en preview)

```typescript
// app/opengraph-image.tsx — OG image dinámica
import { ImageResponse } from 'next/og'

export default function OGImage() {
  return new ImageResponse(
    <div style={{
      background: '#0c2b40',
      width: '100%', height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '60px',
    }}>
      <p style={{ color: '#d3ab6d', fontSize: 20, letterSpacing: '0.2em', textTransform: 'uppercase' }}>
        DETA Consultores
      </p>
      <h1 style={{ color: '#FFFFFF', fontSize: 56, textAlign: 'center', marginTop: 24 }}>
        Tu Headline Aquí
      </h1>
    </div>,
    { width: 1200, height: 630 }
  )
}
```
