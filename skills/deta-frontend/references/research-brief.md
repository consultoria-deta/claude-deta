# Research Brief — deta-frontend superskill

> Generado 2026-04-16. NLM notebook: `b2a63cf9-17e7-408b-8d00-36b0fcfe0631` (efímero).
> 10 fuentes indexadas: Motion docs (spring, stagger, a11y), Tailwind v4 dark mode, shadcn/ui v4 theming, Linear design analysis, View Transitions Next.js.

---

## 1. Conocimiento nuclear

1. **`@theme inline` — obligatorio para tokens DETA en Tailwind v4:** Las variables de tema deben declararse con `@theme inline {}` en `globals.css` para que Tailwind genere las clases de utilidad correspondientes. Usar solo `:root` NO genera utilidades.
2. **shadcn/ui v4 — pares semánticos:** El theming se basa en pares `background/foreground`, `primary/primary-foreground`. El modo oscuro se activa sobrescribiendo estos tokens bajo `.dark`, no duplicando clases en el HTML. Esto exige mapear los tokens DETA a las variables semánticas de shadcn.
3. **Motion spring — `visualDuration` + `bounce`:** Para el "feeling" de Linear/Notion usar `type: "spring"` con `visualDuration` (segundos) y `bounce` (0-1). No tunear `mass/stiffness/damping` — es más difícil de coordinar y mantener.
4. **Accesibilidad obligatoria — `<MotionConfig reducedMotion="user">`:** Envolver la app en `MotionConfig` con `reducedMotion="user"`. Las transformaciones espaciales (scale, x, y) deben degradarse a `opacity` fade cuando `useReducedMotion()` retorna `true`.
5. **Estética Linear — linealidad estructural:** Scrolling unidimensional, sin contenido en zig-zag, alineación consistente, fondos monocromáticos oscuros, mínimos CTAs visibles por viewport. El color acento (cyan/gold) solo en focus rings y CTAs principales — no en todo.
6. **React 19 — sin `forwardRef` en shadcn v4:** Los componentes usan `React.ComponentProps`, ref como prop normal, atributos `data-slot` para styling selectivo con Tailwind. Actualizar qualquier componente copiado de shadcn v3.
7. **Stagger con Variants — coordinar padre/hijo:** Para listas tipo Notion, el contenedor padre necesita `delayChildren: stagger(0.05-0.1)` y `when: "beforeChildren"`. Sin esto, todos los hijos aparecen simultáneamente.
8. **Dark mode — clase `.dark`, no `prefers-color-scheme`:** Sobrescribir la variante `dark` de Tailwind v4 para que dependa de `.dark` en el HTML, gestionado vía JavaScript (next-themes). Esto permite forzar modo desde la app sin depender del OS.
9. **Glassmorphism — solo en elementos flotantes:** Liquid glass (`backdrop-blur` + `bg-background/50` + borde translúcido) solo en panels flotantes: sidebars, modals, popovers. En cards de listas destruye contraste y performance.
10. **OKLCH en Tailwind v4:** Tailwind v4 usa OKLCH internamente. Al definir tokens DETA se puede usar hex (#0c2b40) — Tailwind convierte. Pero para interpolaciones de gradiente en oklch usar `interpolate: oklch` para evitar grays en el punto medio.

---

## 2. Anti-patrones

| Anti-patrón | Por qué falla | Fix |
|---|---|---|
| Animar scale/translate para todos los usuarios | Mareo en usuarios con `prefers-reduced-motion` | `useReducedMotion()` → reemplazar por fade `opacity` |
| Tokens DETA crudos en clases Tailwind (`bg-[#0c2b40]`) | No usa el sistema semántico de shadcn, rompe dark mode | Mapear tokens a variables semánticas vía `@theme inline` |
| `var(--token)` en valores arbitrarios sin `@theme inline` | CSS resuelve variables según DOM — valores inesperados | Declarar en `@theme inline`, usar la clase de utilidad generada |
| Glass en todos los elementos (cards, botones) | Contraste bajo, baja performance de compositing | Limitar a panels flotantes únicamente |
| Fondos de colores distintos por sección (arcoíris) | Destruye linealidad Linear, aumenta carga cognitiva | Fondo monocromático dark, acentos solo en detalles focales |
| Crear componentes desde cero en lugar de adaptar shadcn | Inconsistencias, trabajo duplicado | Extender primitivos shadcn v4 con tokens DETA |
| `forwardRef` en componentes React 19 | Obsoleto — deprecado en React 19 | `ref` como prop, `React.ComponentProps<'element'>` |
| Tunear `mass/stiffness/damping` manualmente | Difícil coordinar con otras animaciones | `visualDuration` + `bounce` en `type: spring` |
| Animar `height` desde un elemento con `display: none` | El navegador no puede medir → snap sin transición | Animar `visibility` + `height: 0 → auto` en secuencia |

---

## 3. Edge cases

1. **`height: auto` en animaciones de expand/collapse:** Animar `height` hacia `"auto"` mientras el elemento tiene `display: none` genera un snap instantáneo. Fix: usar `visibility: "hidden"` → `"visible"` coordinado con height `0` → `"auto"`.

2. **Sincronizar variants padre-hijo (stagger listas grandes):** Con listas de 50+ items, un `stagger(0.05)` puede resultar en el último elemento apareciendo 2.5s después del primero — lento y frustrante. Fix: limitar stagger efectivo usando `staggerChildren` con `from: "first"` y `delayChildren` pequeño (0.03-0.05), o animar solo los primeros N visibles.

3. **Dark mode flash on load (FOUC):** Con `next-themes`, el DOM monta en light y después aplica `.dark` — un flash de color blanco en dark mode. Fix: bloquear render inicial con un script inline en `<head>` que aplique la clase antes del paint, o usar `suppressHydrationWarning` en `<html>`.

4. **View Transitions + Motion simultáneos:** Next.js 16 `<ViewTransition>` y Motion `<AnimatePresence>` pueden generar conflictos en el mismo elemento. Fix: usar View Transitions para transiciones de ruta (nivel página), Motion para micro-UI dentro de la página — no anidar los dos en el mismo componente.

5. **Gradientes en dark mode Tailwind v4:** `dark:via-transparent` no resetea gradiente en v4. Fix: `dark:via-none` para volver a gradiente de dos colores. Para gradientes con cyan/gold, especificar siempre el espacio OKLCH explícitamente para evitar gris en el punto medio.

---

## 4. Estructura propuesta

```
deta-frontend/
├── SKILL.md                    ← reglas inflexibles + motion + glass + tokens
└── references/
    ├── research-brief.md       ← este archivo
    ├── motion-patterns.md      ← spring config, stagger, variants, a11y
    ├── shadcn-tailwind-v4.md   ← theming, data-slot, dark mode, OKLCH tokens
    └── liquid-glass-css.md     ← glassmorphism DETA, backdrop-blur patterns
```

---

## 5. Scripts reutilizables

### `globals.css` base — Tailwind v4 + shadcn + tokens DETA

```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: #ffffff;
  --color-foreground: #1A1A2E;
  --color-primary: #0c2b40;
  --color-primary-foreground: #ffffff;
  --color-secondary: #d3ab6d;
  --color-secondary-foreground: #0c2b40;
  --color-accent: #12a9cc;
  --color-accent-foreground: #ffffff;
  --color-muted: #F5F7FA;
  --color-muted-foreground: #6B7280;
  --color-border: rgba(12, 43, 64, 0.1);
  --color-ring: #12a9cc;

  /* Dark mode overrides */
  --color-background: oklch(0.08 0.02 240);    /* navy-950 */
  --color-surface: oklch(0.14 0.025 240);       /* slate-800 */

  /* Liquid glass */
  --glass-panel: rgba(12, 43, 64, 0.72);
  --glass-card: rgba(255, 255, 255, 0.03);
  --glass-input: rgba(255, 255, 255, 0.04);
  --glass-blur: 24px;
  --glass-blur-card: 16px;
  --glass-blur-input: 8px;
}
```

### `MotionProvider.tsx` — config global

```tsx
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

### `StaggerList.tsx` — lista con entrada en cascada

```tsx
'use client'
import { motion } from 'motion/react'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0 },
  },
}

const item = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 },
}

export function StaggerList({ children }: { children: React.ReactNode }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {children}
    </motion.ul>
  )
}

export function StaggerItem({ children }: { children: React.ReactNode }) {
  return <motion.li variants={item}>{children}</motion.li>
}
```

---

## 6. Triggers naturales

1. "Crea un sidebar de navegación al estilo Linear, fondo navy oscuro, con los tokens DETA"
2. "Aplica liquid glass a este modal flotante / popover"
3. "Anima la entrada de estos cards con stagger, como en Notion"
4. "Refactoriza esta página para seguir diseño Linear: quita el zig-zag, reduce CTAs"
5. "Asegúrate de que las animaciones respeten reduced motion / accesibilidad"
6. "Actualiza estos componentes shadcn para React 19 y Tailwind v4 (quitar forwardRef)"
7. "Configura dark mode con next-themes para que use la clase .dark"
8. "El dark mode flashea blanco al cargar — arréglalo"
9. "Esta lista de leads necesita animación de entrada suave al cargar"
10. "Quiero que el hover de las cards se sienta premium, con elevación"

---

## 7. Skills adyacentes

- `deta-coding` → stack backend (Server Actions, Drizzle, Auth.js) — frontend consume, no implementa
- `deta-brand` → logo assets, OG images, PDFs, blog hero images — piezas estáticas fuera de React
- `a11y-audit` → validación WCAG completa, roles ARIA, semántica HTML (más profundo que lo que cubre Motion a11y)

---

## 8. Riesgos de sobre-ingeniería

- **No inventar librerías de componentes** — extender primitivos shadcn v4
- **No tunear physics manualmente** — `visualDuration` + `bounce` son suficientes
- **No aplicar glass en todo** — solo panels flotantes
- **No usar `prefers-color-scheme` para dark mode** — siempre clase `.dark` controlada
- **No mezclar View Transitions + Motion en el mismo elemento** — uno para rutas, otro para micro-UI
- **No sugerir Framer Motion** — la librería se renombró a Motion (`motion/react`)
- **No añadir librerías de animación adicionales** (GSAP, anime.js) — Motion cubre el stack

---

## Decisiones de Claude (override del brief NLM)

- **ACEPTÉ:** `@theme inline` como regla inflexible — alineado con la arquitectura Tailwind v4 del proyecto
- **ACEPTÉ:** `visualDuration + bounce` sobre `mass/stiffness/damping` — más fácil de mantener en equipo
- **ACEPTÉ:** Glass solo en elementos flotantes — validado contra benchmark de DETA Ops actual
- **RECHACÉ:** Delegación a `framer-motion-advanced` para animaciones complejas — innecesario, Motion cubre el 95% de casos DETA
- **AUMENTÉ:** Dark mode FOUC fix — las fuentes lo mencionan pero no lo enfatizan; crítico para Next.js con SSR
- **AUMENTÉ:** Edge case de View Transitions + Motion conflicto — no en las fuentes, pero DETA Ops usa Next.js 16 y ambos patrones estarán presentes
- **AUMENTÉ:** OKLCH en gradientes — Tailwind v4 usa OKLCH internamente y los gradientes cyan/navy se ven grises si no se especifica el espacio de color
