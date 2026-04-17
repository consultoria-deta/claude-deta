---
name: daily-brief
description: Genera el brief diario de arranque de día para Joel. Lee memoria local (Hot-Cache + Kanbans de proyectos activos) y agenda de Google Calendar, y presenta un resumen accionable priorizado. Triggers: "daily brief", "buenos días", "qué tengo hoy", "arrancar el día", "resumen del día", "brief del día".
---

# Daily Brief

Genera el resumen de arranque de día de Joel. El objetivo es que en 60 segundos de lectura quede claro qué mover hoy y en qué orden.

---

## Paso 1 — Leer estado de proyectos

Leer los siguientes archivos en paralelo:

```
~/.claude/memory/Hot Cache/Hot-Cache.md
~/.claude/projects/-Users-joelestrada/memory/project_deta-ops.md
~/.claude/projects/-Users-joelestrada/memory/project_deta-web.md
~/.claude/projects/-Users-joelestrada/memory/project_deta-render.md
~/.claude/projects/-Users-joelestrada/memory/project_flujo-contenido.md
~/.claude/projects/-Users-joelestrada/memory/project_google-ads.md
~/.claude/projects/-Users-joelestrada/memory/project_agent-templates.md
~/.claude/projects/-Users-joelestrada/memory/project_vacantes-abiertas.md
~/.claude/projects/-Users-joelestrada/memory/project_deta-products.md
```

Si algún archivo no existe, ignorarlo sin avisar.

---

## Paso 2 — Leer agenda de hoy (Google Calendar)

Usar `mcp__claude_ai_Google_Calendar__list_events` con:
- `calendarId`: `consultoria@detaconsultores.com`
- `timeMin`: inicio del día actual (00:00 hora local America/Chihuahua)
- `timeMax`: fin del día actual (23:59 hora local)
- `maxResults`: 10

Si el MCP falla o no está disponible, omitir la sección de agenda sin avisar.

---

## Paso 3 — Extraer y priorizar tareas

De cada `project_*.md`, extraer la sección `## Kanban` y dentro de ella:

**Urgente/Alta (mostrar primero):**
- `### In Progress` — todo lo que está en curso
- `### Todo` con `prio:urgent` o `prio:high`
- `### Todo` con `due:` <= fecha de hoy

**Normal:**
- `### Todo` con `prio:medium` o sin prio explícita
- Limitar a 3 items por proyecto para no saturar

**Ignorar:**
- `### Done`, `### Archived`, `### Backlog`
- Tasks con `prio:low` a menos que tengan `due:` <= hoy

---

## Paso 4 — Calcular foco del día

Identificar las **2-3 acciones más críticas del día** con esta lógica:

1. Tasks con `due:` = hoy o vencidas (due < hoy)
2. Tasks en `### In Progress` de proyectos de alta prioridad
3. Items mencionados explícitamente en Hot-Cache como "pendiente inmediato" o con ⏳
4. Eventos del calendario que requieren preparación

Presentarlos como acciones concretas (verbos en imperativo), no como descripciones.

---

## Paso 5 — Presentar el brief

Formato de salida:

```
# ☀ Daily Brief — [Día, DD de Mes YYYY]

## 🎯 Foco del día
1. [Acción concreta #1]
2. [Acción concreta #2]
3. [Acción concreta #3 — solo si aplica]

## 📅 Agenda
- HH:MM — [título del evento] [sala/link si existe]
[Si no hay eventos: "Sin eventos agendados hoy."]

## 🔥 Urgente / Vencido
**[Proyecto]**
- [ ] [task] [due si aplica]

[Si no hay items urgentes: omitir sección completa]

## 🏗 En progreso
**[Proyecto]**
- [ ] [task]

[Si no hay nada en progreso: omitir sección]

## 📋 Pendientes por proyecto
**[Proyecto]** — [estado en 1 línea del Hot-Cache]
- [ ] [task prio:high o medium, máx 3 por proyecto]

## ⚠ Recordatorios cruzados
[Items del Hot-Cache que no encajan en un solo proyecto — campañas activas, pendientes de verificar, fechas clave próximas]
[Omitir si no hay nada relevante]
```

**Reglas de presentación:**
- Fechas en español natural: "hoy", "mañana", "jue 17" — no ISO
- Si un proyecto no tiene tasks activas, omitirlo de `## 📋 Pendientes` para no inflar
- El brief completo debe poder leerse en < 60 segundos — ser selectivo
- No agregar contexto que Joel ya sabe (no explicar qué es DETA Ops, etc.)
- Si hay items con `due:` vencido (< hoy), marcarlos con `🔴` para visibilidad

---

## Notas operativas

- Esta skill solo lee, nunca escribe ni modifica archivos
- Si el usuario pide "actualizar" o "marcar como hecho" algo del brief, recordarle que use el project file directamente o que lo hará al cierre de sesión
- Si el usuario pregunta por un proyecto específico tras ver el brief, profundizar en ese `project_*.md` directamente
