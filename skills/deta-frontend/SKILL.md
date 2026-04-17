---
name: deta-frontend
description: Super skill de frontend para apps DETA. Combina Motion (spring animations, stagger), Tailwind v4 dark mode, shadcn/ui v4, liquid glass DETA y tokens de marca en código React/Next.js. Úsala cuando trabajas en DETA Ops, DETA Web o cualquier interfaz React que deba verse al nivel de Linear/Superhuman/Notion. Triggers: sidebar nav, animaciones de entrada, liquid glass, dark mode, componentes shadcn, reduced motion, stagger list.
---

# deta-frontend — Frontend de Nivel Linear para Apps DETA

El estándar visual de DETA es Linear / Superhuman / Notion / Apple HIG. "Funcional" o "decente" no son aceptables. Este skill te da las herramientas para llegar a ese nivel.

> **Stack backend:** para Server Actions, Drizzle, Auth.js → usar `deta-coding`.
> **Assets estáticos:** OG images, PDFs, blog heroes → usar `deta-brand`.

---

## Reglas inflexibles

1. **Fondos monocromáticos** — navy-950 en dark, blanco en light. Los tokens cyan/gold solo en focus rings, CTAs principales y detalles focales de dataviz. Nunca en fondos de sección o gradientes decorativos.
2. **`@theme inline` siempre** — los tokens DETA se declaran en `globals.css` con `@theme inline {}`, no en `:root` solo. Sin `@theme inline`, Tailwind no genera las clases de utilidad.
3. **Tokens DETA mapean a semántica shadcn** — `--color-primary` = navy, `--color-accent` = cyan, `--color-secondary` = gold. Nunca usar hex crudos en clases Tailwind (`bg-[#0c2b40]`).
4. **Motion, no Framer Motion** — importar siempre desde `motion/react`. La librería se renombró; `framer-motion` es la versión antigua.
5. **`reducedMotion="user"` obligatorio** — envolver la app en `<MotionConfig reducedMotion="user">`. Las transformaciones espaciales (x, y, scale) deben degradarse a fade de `opacity` cuando `useReducedMotion()` retorna `true`.
6. **Dark mode con clase `.dark`** — nunca `prefers-color-scheme` como única fuente. Usar `next-themes` que inyecta `.dark` en `<html>`. Sobrescribir la variante `dark` de Tailwind v4 para que dependa del selector `.dark`.
7. **Sin `forwardRef` en componentes nuevos** — React 19: pasar `ref` como prop normal, usar `React.ComponentProps<'element'>` para tipar. Al copiar componentes de shadcn v3 → actualizar a v4.
8. **Glass solo en elementos flotantes** — sidebars fijos, modals, popovers, drawers. Nunca en cards de listas ni botones — mata contraste y performance de compositing.

---

## Tokens DETA en código

### `globals.css` — configuración base

```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  /* DETA Core */
  --color-primary: oklch(0.22 0.05 235);       /* navy #0c2b40 */
  --color-primary-foreground: #ffffff;
  --color-secondary: oklch(0.76 0.08 65);       /* gold #d3ab6d */
  --color-secondary-foreground: #0c2b40;
  --color-accent: oklch(0.62 0.12 210);         /* cyan #12a9cc */
  --color-accent-foreground: #ffffff;

  /* Semantic */
  --color-background: #ffffff;
  --color-foreground: #1A1A2E;
  --color-muted: #F5F7FA;
  --color-muted-foreground: #6B7280;
  --color-border: rgba(12, 43, 64, 0.1);
  --color-ring: #12a9cc;

  /* Dark canvas */
  --color-canvas-dark: oklch(0.08 0.02 240);    /* navy-950 #040f1c */
  --color-surface-dark: oklch(0.14 0.025 240);  /* slate-800 */

  /* Liquid glass */
  --glass-panel: rgba(12, 43, 64, 0.72);
  --glass-card: rgba(255, 255, 255, 0.03);
  --glass-input: rgba(255, 255, 255, 0.04);

  /* Motion */
  --duration-fast: 120ms;
  --duration-base: 200ms;
  --duration-slow: 360ms;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}

/* Dark mode overrides */
.dark {
  --color-background: oklch(0.08 0.02 240);
  --color-foreground: oklch(0.93 0.01 240);
  --color-muted: oklch(0.14 0.025 240);
  --color-muted-foreground: oklch(0.6 0.02 240);
  --color-border: rgba(255, 255, 255, 0.07);
}
```

### Clases de utilidad para liquid glass

```css
/* En globals.css — definir una vez, usar en todo flotante */
@layer utilities {
  .glass-panel {
    background: var(--glass-panel);
    backdrop-filter: blur(24px) saturate(1.2);
    -webkit-backdrop-filter: blur(24px) saturate(1.2);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .glass-card {
    background: var(--glass-card);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .glass-input {
    background: var(--glass-input);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
}
```

---

## Motion — Animaciones spring

### Setup global (una vez en el root layout)

```tsx
// app/providers.tsx
'use client'
import { MotionConfig } from 'motion/react'

export function MotionProvider({ children }: { children: React.ReactNode }) {
  return (
    <MotionConfig
      reducedMotion="user"
      transition={{ type: 'spring', visualDuration: 0.35, bounce: 0.2 }}
    >
      {children}
    </MotionConfig>
  )
}
```

### Spring presets

```ts
// lib/motion.ts
export const spring = {
  // Para elementos que aparecen/desaparecen — suave
  gentle: { type: 'spring' as const, visualDuration: 0.4, bounce: 0.15 },
  // Para hover lift, focus — rápido y táctil
  snappy: { type: 'spring' as const, visualDuration: 0.25, bounce: 0.3 },
  // Para modals, drawers — con presencia
  modal: { type: 'spring' as const, visualDuration: 0.45, bounce: 0.1 },
}
```

### Accesibilidad — degradar a fade cuando reduced motion

```tsx
'use client'
import { motion, useReducedMotion } from 'motion/react'

interface AnimatedCardProps {
  children: React.ReactNode
  className?: string
}

export function AnimatedCard({ children, className }: AnimatedCardProps) {
  const reduced = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: reduced ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={reduced
        ? { duration: 0.15 }
        : { type: 'spring', visualDuration: 0.4, bounce: 0.2 }
      }
      className={className}
    >
      {children}
    </motion.div>
  )
}
```

### Stagger — listas con entrada en cascada

```tsx
'use client'
import { motion } from 'motion/react'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.05,
    },
  },
}

const item = {
  hidden: { opacity: 0, y: 8 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', visualDuration: 0.35, bounce: 0.15 },
  },
}

export function StaggerList({ children }: { children: React.ReactNode }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show" className="space-y-1">
      {children}
    </motion.ul>
  )
}

export function StaggerItem({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.li variants={item} className={className}>
      {children}
    </motion.li>
  )
}
```

**Regla:** con listas >30 items, usar `staggerChildren: 0.03` (máximo 0.05) para evitar que el último elemento aparezca demasiado tarde.

### AnimatePresence — mount/unmount

```tsx
import { AnimatePresence, motion } from 'motion/react'

// Para sidebars, drawers, toasts
<AnimatePresence>
  {isOpen && (
    <motion.aside
      key="sidebar"
      initial={{ x: -280, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -280, opacity: 0 }}
      transition={{ type: 'spring', visualDuration: 0.4, bounce: 0.1 }}
      className="glass-panel fixed left-0 top-0 h-full w-64"
    />
  )}
</AnimatePresence>
```

### Hover lift — cards interactivas

```tsx
<motion.div
  whileHover={{ y: -2, scale: 1.01 }}
  whileTap={{ scale: 0.99 }}
  transition={{ type: 'spring', visualDuration: 0.2, bounce: 0.4 }}
  className="rounded-lg border border-border bg-card p-4 cursor-pointer"
>
  {content}
</motion.div>
```

---

## Dark Mode — configuración Next.js

### Instalar next-themes

```bash
npm install next-themes
```

### Setup

```tsx
// app/providers.tsx
'use client'
import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </ThemeProvider>
  )
}
```

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

**`suppressHydrationWarning`** es obligatorio — evita el warning de hidratación cuando next-themes aplica la clase `.dark` en el cliente.

### Fix del flash blanco (FOUC) en dark mode

Si el flash persiste con `suppressHydrationWarning`, agregar script inline en `<head>`:

```tsx
// En el layout, dentro de <head>
<script
  dangerouslySetInnerHTML={{
    __html: `
      try {
        const t = localStorage.getItem('theme');
        if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.classList.add('dark');
        }
      } catch(e) {}
    `,
  }}
/>
```

---

## shadcn/ui v4 — patrones actualizados

### Instalar con Tailwind v4

```bash
npx shadcn@latest init
```

### Componente actualizado (React 19 — sin forwardRef)

```tsx
// Patrón v4 con data-slot y React.ComponentProps
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ComponentProps<'button'> {
  variant?: 'default' | 'secondary' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  variant = 'default',
  size = 'md',
  className,
  ref,
  ...props
}: ButtonProps) {
  return (
    <button
      ref={ref}
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  )
}
```

### Añadir shadcn con tokens DETA

```bash
npx shadcn@latest add button card input dialog
```

Los componentes usan las variables CSS de `globals.css` automáticamente — no hardcodear colores.

---

## Liquid Glass DETA — patrones de uso

### Sidebar nav (glass-panel)

```tsx
<aside className="glass-panel fixed left-0 top-0 z-30 h-full w-60 flex flex-col">
  <div className="flex items-center gap-3 p-4 border-b border-white/10">
    <img src="/logo-deta-white.svg" alt="DETA" className="h-6 w-auto" />
  </div>
  <nav className="flex-1 overflow-y-auto p-3 space-y-1">
    {navItems}
  </nav>
</aside>
```

### Modal / Dialog (glass-card sobre overlay oscuro)

```tsx
<div className="fixed inset-0 z-50 flex items-center justify-center">
  {/* Overlay */}
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
  />
  {/* Panel */}
  <motion.div
    initial={{ opacity: 0, scale: 0.97, y: 8 }}
    animate={{ opacity: 1, scale: 1, y: 0 }}
    transition={{ type: 'spring', visualDuration: 0.4, bounce: 0.1 }}
    className="relative glass-card rounded-xl border border-white/10 p-6 w-full max-w-md shadow-2xl"
  >
    {content}
  </motion.div>
</div>
```

### Input con glass

```tsx
<input
  className="glass-input w-full rounded-lg border border-white/10 px-3 py-2
             text-sm text-foreground placeholder:text-muted-foreground
             focus:outline-none focus:ring-2 focus:ring-accent/50
             transition-shadow"
  placeholder="Buscar..."
/>
```

---

## Gradientes DETA

### Cyan → navy (OKLCH para evitar gris en el medio)

```css
/* Con interpolación OKLCH — evita grays */
background: linear-gradient(in oklch, #12a9cc, #0c2b40);

/* En Tailwind v4 */
.bg-deta-gradient {
  background: linear-gradient(135deg in oklch, var(--color-accent), var(--color-primary));
}
```

### Hero gradient sutil (dark mode)

```tsx
<section className="relative overflow-hidden bg-canvas-dark">
  {/* Glow de fondo — no visible como color, solo como profundidad */}
  <div
    className="absolute inset-0 opacity-20"
    style={{
      background: 'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(18,169,204,0.3), transparent)',
    }}
  />
  <div className="relative z-10">{content}</div>
</section>
```

---

## View Transitions — Next.js 16

Para transiciones entre rutas (nivel página), usar la API nativa de Next.js 16, **no** Motion.

```tsx
// app/layout.tsx
import { unstable_ViewTransition as ViewTransition } from 'next'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <ViewTransition>
      {children}
    </ViewTransition>
  )
}
```

```tsx
// Para transición de elemento compartido entre rutas
import { unstable_ViewTransition as ViewTransition } from 'next'

<ViewTransition name="hero-card">
  <img src={src} className="w-full rounded-lg" />
</ViewTransition>
```

**Regla:** View Transitions para rutas, Motion para micro-UI dentro de la misma página. No anidar ambos en el mismo elemento.

---

## Composición visual — principios Linear

### Jerarquía de un viewport

1. Un solo propósito visual por sección
2. Un H1 / título dominante, max 10 palabras
3. Soporte en 1-2 líneas
4. Un CTA — nunca dos del mismo peso

### Scrolling unidireccional

- Sin secciones en zig-zag (imagen izquierda / texto derecha alternado)
- Alineación consistente por viewport — todo left-aligned o todo centered, no mezclar
- Whitespace generoso entre secciones (`py-20` en desktop)

### Tipografía con contraste real

```tsx
{/* Nunca todo el mismo peso/tamaño */}
<div>
  <p className="text-xs font-semibold uppercase tracking-widest text-accent mb-2">
    DETA Ops
  </p>
  <h1 className="text-4xl font-bold tracking-tight text-foreground">
    Tu operación, sin depender de ti
  </h1>
  <p className="mt-3 text-lg text-muted-foreground leading-relaxed">
    CRM, tareas y cotizaciones en un solo lugar.
  </p>
</div>
```

### Focus rings con cyan DETA

```css
/* En globals.css — override de shadcn */
*:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

---

## QA antes de cerrar una fase visual

- [ ] Logo real — nunca placeholder "D en cuadro". Usar `logo-deta-white.svg` sobre fondos oscuros, `logo-deta-cyan.svg` sobre fondos claros
- [ ] Mobile 375px: sin overflow horizontal, sin scroll accidental
- [ ] Dark mode: sin flash blanco al cargar, colores con contraste mínimo 4.5:1
- [ ] `useReducedMotion()` verificado: las animaciones se degradan a fade
- [ ] Fondos: máximo 2 valores distintos por página, sin arcoíris
- [ ] CTAs: 1 primario visible por viewport
- [ ] Sin `forwardRef` en componentes nuevos
- [ ] Gradientes con tokens OKLCH si incluyen cyan/navy juntos
- [ ] Glass solo en elementos flotantes, no en cards de listas

---

## Mobile UX — Calendario y Kanban

Las vistas de calendario y kanban en desktop no escalan a mobile. Requieren patrones distintos deliberados — no solo texto más pequeño.

### Reglas base mobile

1. **Agenda view como primaria** — en ≤480px, la cuadrícula mensual no cabe. La vista default debe ser lista vertical (agenda), con el mes compacto como selector arriba.
2. **Máximo 3-4 columnas kanban visibles** — más causa sobrecarga. Usar `minmax(85vw,1fr)` con scroll horizontal + CSS snap para que cada columna ocupe casi toda la pantalla.
3. **Touch sensors en @dnd-kit** — activar `TouchSensor` junto con `PointerSensor`. Sin él, el drag-and-drop no funciona en táctil.
4. **Bottom sheet para pickers y event detail** — nunca modal centrado en mobile; el panel inferior preserva contexto y es accesible con una mano.
5. **No hover tooltips** — hover no existe en táctil. Tap simple para expandir detalle.

### CSS scroll snap para kanban columnas

```css
/* Contenedor del kanban board */
.kanban-scroll {
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}

/* Cada columna */
.kanban-col-wrapper {
  scroll-snap-align: start;
  scroll-snap-stop: always;
}
```

```tsx
{/* En Tailwind v4 */}
<div className="flex overflow-x-auto [scroll-snap-type:x_mandatory] [-webkit-overflow-scrolling:touch]">
  {columns.map((col) => (
    <div key={col} className="[scroll-snap-align:start] [scroll-snap-stop:always] min-w-[85vw] sm:min-w-[240px]">
      <Column ... />
    </div>
  ))}
</div>
```

### @dnd-kit con touch support

```tsx
import { PointerSensor, TouchSensor, useSensor, useSensors } from '@dnd-kit/core'

// Activar ambos sensores — PointerSensor para mouse, TouchSensor para táctil
const sensors = useSensors(
  useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
  useSensor(TouchSensor, { activationConstraint: { delay: 250, tolerance: 5 } }),
)
```

**Por qué `delay: 250`:** evita que el drag-start compita con el scroll vertical de la página. El usuario tiene 250ms de "intención de scroll" antes de que inicie el drag.

### Agenda View — patrón para calendarios mobile

El patrón Google Calendar / Apple Calendar en mobile:
- **Header fijo**: mes compacto colapsable (7 columnas con solo la inicial del día + número)
- **Body**: lista vertical de eventos ordenada por día, scroll infinito hacia arriba/abajo
- **Al tocar un día en el header**: la lista hace scroll al día seleccionado

```tsx
function AgendaView({ events }: { events: CalendarEvent[] }) {
  const grouped = groupByDay(events) // Map<string, CalendarEvent[]>
  
  return (
    <div className="flex flex-col h-full">
      {/* Mes compacto — colapsa en mobile, expande en desktop */}
      <div className="sm:hidden border-b border-border">
        <CompactMonthStrip onDaySelect={(d) => scrollToDay(d)} />
      </div>
      
      {/* Lista de eventos */}
      <div className="flex-1 overflow-y-auto">
        {[...grouped.entries()].map(([day, dayEvents]) => (
          <div key={day} id={`day-${day}`} className="py-2">
            <p className="px-4 py-1 text-[11px] font-semibold uppercase tracking-wide text-ink-muted sticky top-0 bg-surface/80 backdrop-blur-sm">
              {formatDay(day)}
            </p>
            {dayEvents.map((e) => <EventRow key={e.id} event={e} />)}
            {dayEvents.length === 0 && (
              <p className="px-4 py-2 text-[13px] text-ink-faint">Sin eventos</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Bottom Sheet para event detail

```tsx
'use client'
import { AnimatePresence, motion } from 'motion/react'

export function EventBottomSheet({ event, onClose }: { event: CalendarEvent | null; onClose: () => void }) {
  return (
    <AnimatePresence>
      {event && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-black/40 sm:hidden"
          />
          {/* Sheet — solo en mobile; en desktop usa popover */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', visualDuration: 0.35, bounce: 0.1 }}
            className="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl bg-surface border-t border-border p-5 sm:hidden"
          >
            {/* Drag handle */}
            <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-border" />
            <EventDetail event={event} />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### View toggle mobile — patrón switcher

Para cualquier vista que tenga alternativa mobile/desktop:

```tsx
'use client'
import { useState } from 'react'
import { Calendar, LayoutList } from 'lucide-react'
import { cn } from '@/lib/ui/cn'

type ViewMode = 'board' | 'list'

export function ViewToggle({ value, onChange }: { value: ViewMode; onChange: (v: ViewMode) => void }) {
  return (
    <div className="flex items-center rounded-md border border-border bg-surface p-0.5">
      {(['board', 'list'] as const).map((v) => (
        <button
          key={v}
          type="button"
          onClick={() => onChange(v)}
          className={cn(
            'flex items-center gap-1.5 rounded px-2.5 py-1.5 text-[12px] font-medium transition-colors',
            value === v
              ? 'bg-navy-900 text-white'
              : 'text-ink-muted hover:text-navy-900',
          )}
        >
          {v === 'board' ? <LayoutList className="size-3.5" /> : <Calendar className="size-3.5" />}
          <span className="hidden sm:inline">{v === 'board' ? 'Tablero' : 'Agenda'}</span>
        </button>
      ))}
    </div>
  )
}
```

### Anti-patrones mobile rápidos

| ❌ | ✅ |
|---|---|
| Grilla mensual como vista default en mobile | Agenda list como primaria, mes compacto como nav |
| `useSensor(PointerSensor)` solo | `PointerSensor` + `TouchSensor` con `delay: 250` |
| Modal centrado para event detail | Bottom sheet en mobile (`sm:hidden`) |
| Todas las columnas kanban visibles en 375px | `minmax(85vw,1fr)` + CSS snap |
| Hover para revelar acciones de tarjeta | Tap simple expande detalle |
| `grid-cols-[repeat(N,minmax(Xpx,1fr))]` fijo | Breakpoint mobile vs desktop separados |

### QA mobile antes de cerrar fase

- [ ] Calendario en 375px: ¿se ve la lista de eventos? ¿no hay grid comprimido?
- [ ] Al tocar un día: ¿abre bottom sheet (no modal)? ¿el sheet cubre toda la parte inferior?
- [ ] Kanban en 375px: ¿columnas se deslizan horizontalmente? ¿drag funciona con el dedo?
- [ ] View toggle visible: ¿hay botón para cambiar entre tablero y lista?
- [ ] Targets táctiles: ≥44px de altura en todos los elementos interactivos mobile

---

## Anti-patrones rápidos

| ❌ | ✅ |
|---|---|
| `from 'framer-motion'` | `from 'motion/react'` |
| `mass: 1, stiffness: 300` | `visualDuration: 0.35, bounce: 0.2` |
| Glass en cards de lista | Glass en sidebar, modal, popover |
| `prefers-color-scheme` solo | `next-themes` + clase `.dark` |
| `bg-[#0c2b40]` en JSX | `bg-primary` con token semántico |
| `forwardRef` en nuevo componente | `ref` como prop normal (React 19) |
| Stagger de 0.15s con 40 items | Stagger de 0.03-0.05s con `from: "first"` |
| `dark:via-transparent` en gradiente | `dark:via-none` (Tailwind v4) |
| Overlay de color en dark mode | `suppressHydrationWarning` + next-themes |
| View Transitions + Motion en mismo div | View Transitions para rutas, Motion para micro-UI |
