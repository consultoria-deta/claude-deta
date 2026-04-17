---
name: Mobile UX Brief — deta-frontend
description: Research brief NLM para la sección de mobile UX (calendario + kanban). Notebook efímero 9416f211, 10 fuentes, Prompt 1 ejecutado 2026-04-16.
type: reference
---

# Mobile UX Brief — deta-frontend

> Fuentes indexadas: 10 (2 Medium rechazadas por paywall)
> Notebook: `9416f211` — eliminado después de este brief
> Prompt ejecutado: Brief [✓] / Refinamiento [—] / Adversarial [—]

## 1. Conocimiento nuclear

1. **Gestos naturales como navegación base** — calendarios móviles deben permitir swipe entre días/semanas; clics precisos solos no funcionan en táctil.
2. **Reestructuración vertical** — en mobile el contenido del calendario se organiza verticalmente como columna; eventos se minimizan a puntos de color si es necesario para mantener tap targets accesibles.
3. **Bottom sheet para date picker** — controles de fecha en mobile van en panel inferior (bottom sheet) con scroll, no en modal centrado; optimiza uso con una mano.
4. **Límite de columnas kanban** — máximo 3-4 columnas visibles en mobile; más causa sobrecarga visual y scroll horizontal confuso.
5. **Touch targets y gestos kanban** — swipe-to-complete, long-press para menú contextual, drag-and-drop con touch sensors (no pointer-only).
6. **Estados vacíos proactivos** — calendario o board sin datos no puede ser espacio en blanco; debe comunicar estado y ofrecer CTA para crear.
7. **Flexibilidad de vistas** — toggle día/semana/mes/agenda accesible; cada vista sirve un caso de uso distinto.
8. **Degradación deliberada kanban** — achicar texto de desktop no es suficiente; requiere tarjetas apiladas o progressive disclosure.

## 2. Anti-patrones

| ❌ Qué hacen mal | Por qué falla | ✅ Qué hacer |
|---|---|---|
| Escalar grid de desktop a mobile | Tap targets minúsculos, labels ocultos | Lista vertical de eventos + swipe |
| Controles "añadir/editar" enterrados en menús profundos | Parálisis de decisión, baja participación | Botón "+" siempre visible, 1 toque |
| Color solo para indicar urgencia/estado | Falla en daltonismo, requiere leyenda | Color + ícono + texto juntos |
| Hover tooltips para detalle de tarjeta | Hover no existe en táctil | Tap simple expande detalle |

## 3. Edge cases

1. **Rango de fechas lejano** — seleccionar fecha a meses de distancia con botón "mes siguiente" repetido es frustrante → usar infinite scroll vertical en bottom sheet o atajos ("Últimos 30 días").
2. **Kanban con 10+ columnas** — scroll horizontal oculta contexto → limitar vista mobile a 3-4 con snap-scroll; usar progressive disclosure o secciones colapsables.
3. **Red intermitente** — el usuario arrastra tarjetas o crea eventos offline → cambios se guardan localmente y se sincronizan inteligentemente al reconectar; nunca pérdida silenciosa de datos.

## 4. Estructura propuesta para SKILL.md

**Body principal — secciones a añadir:**
- `### Mobile Calendar Patterns` — arquitectura info (lista vertical vs grid), gestos obligatorios, view toggle, agenda como vista primaria
- `### Mobile Kanban Patterns` — límite columnas (3-4), interacciones a una mano, snap-scroll, touch sensors @dnd-kit
- `### Bottom Sheet Date Picker` — patrón específico con código

**references/ a añadir:**
- `references/research-brief-mobile.md` ← este archivo

## 5. Scripts reutilizables

- **`SwipeableKanbanCard`** — `@dnd-kit/core` con touch sensors configurados; previene bloqueo del scroll vertical.
- **`AgendaView`** — lista vertical de eventos con gradiente que marca "hoy"; alternativa mobile al grid mensual.
- **`BottomSheetDatePicker`** — panel inferior con infinite scroll de meses.
- **CSS scroll snap** — `scroll-snap-type: x mandatory` en contenedor + `scroll-snap-align: start` en columnas.

## 6. Triggers naturales

1. "El drag-and-drop del kanban está roto en mobile, no puedo arrastrar tarjetas"
2. "La vista de mes del calendario se ve diminuta en iPhone"
3. "Necesito un date picker rápido para mobile sin modal gigante"
4. "El kanban en mobile muestra demasiadas columnas, se ve amontonado"
5. "Agrega soporte táctil / swipe para cambiar de semana en el calendario"
6. "Vista agenda / list view para mobile"

## 7. Riesgos de sobre-ingeniería

- No construir lógica de fechas desde cero — usar `react-day-picker` o `<input type="date">` nativo.
- No replicar Gantt/timeline en mobile — demasiada complejidad para pantalla pequeña.
- No más de 2 vistas mobile (día/agenda + mes compacto) — más opciones abruman.
- No hover tooltips — no existen en táctil; usar tap-to-expand.

---

## Decisiones de Claude (override del brief NLM)

- ACEPTÉ: Bottom sheet para date picker — es el patrón correcto para mobile
- ACEPTÉ: Límite 3-4 columnas + snap-scroll — encaja perfectamente con el fix `minmax(85vw,1fr)` ya implementado
- ACEPTÉ: `@dnd-kit/core` touch sensors — ya estamos usando @dnd-kit, solo necesitamos activar TouchSensor junto con PointerSensor
- AUMENTÉ: Agenda view como vista *primaria* en mobile (no secundaria) — el problema del calendario DETA Ops es exactamente este: grilla que no cabe en 375px
- RECHACÉ: Offline-first / sync inteligente — fuera del scope de la skill; es arquitectura de datos, no frontend
- RECHACÉ: `QuickAddInput` con NLP — sobre-ingeniería para DETA Ops actual
