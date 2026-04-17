---
name: deta-agenda
description: Módulo Agenda de DETA Ops. Actívate con "agenda", "calendario", "calendar", "gcal", "google calendar", "task", "tarea", "scheduled", "evento", o cuando el usuario trabaje en `app/(app)/calendar`, `/tasks`, `lib/tasks`, `lib/integrations/gcal.ts`.
---

# DETA Ops — Agenda

Centraliza tareas con scheduledAt/dueDate y sincroniza con Google Calendar.

## Rutas y archivos clave

| Qué | Dónde |
|-----|-------|
| Vista calendario (mes/semana) | `app/(app)/calendar/page.tsx` + `components/calendar/CalendarClient.tsx` |
| Vista Kanban por status | `app/(app)/tasks/page.tsx` + `components/tasks/TasksKanban.tsx` |
| CRUD dialog | `components/tasks/TaskDialog.tsx` |
| Server actions | `lib/tasks/actions.ts` |
| Schema + enums | `lib/tasks/schema.ts` (TASK_STATUSES, TASK_PRIORITIES) |
| Route handlers | `app/api/tasks/route.ts` + `[id]/route.ts` |
| gCal cliente | `lib/integrations/gcal.ts` |
| Sync pull | `app/api/gcal/pull/route.ts` |
| Seed demo | `scripts/seed-tasks.mjs` |

## Schema tareas (drizzle)

Campos: `id`, `projectId`, `title`, `description`, `status`, `priority`, `assigneeId`, `dueDate`, `scheduledAt`, `tags[]`, `source`, `externalRef`, `gcalEventId`, `metadata`, `completedAt`.

Status: `backlog | todo | in_progress | done | archived`
Priority: `low | medium | high | urgent`

## gCal sync

- Flag: `GCAL_SYNC_ENABLED=true` activa todo el pipeline.
- Env: `GCAL_CALENDAR_ID` (default `primary`), access/refresh tokens via session JWT.
- Crear/editar/borrar task con `scheduledAt` → gCal (best-effort; fallos solo loggean, no rompen el action).
- Pull: POST `/api/gcal/pull?days=14` — trae eventos, ignora los que ya tienen `gcalEventId`, archiva cancelados.
- `refreshAccessToken` en `lib/integrations/gcal.ts` es placeholder; implementar cuando se active en producción.

## Patrones importantes

- `createTaskAction` y `updateTaskAction` crean/actualizan/borran el evento gCal **antes** de persistir en DB — así si gCal falla, no dejamos registros huérfanos con eventId inválido.
- `updateTaskStatusAction(id, status)` es la acción específica para el drag del Kanban. Setea `completedAt` cuando status → `done`.
- Vista semana renderiza grid 24h. Vista mes renderiza calendario 6 semanas. Ambas usan `<div>` con tabIndex para evitar button-in-button HTML.

## Cuando el usuario pida crear una vista nueva

- Reutilizar `CalendarClient` si es variante de calendar. Pasarle más props antes que crear otro componente.
- Si es una vista distinta (ej: vista día, vista recursos), crear `components/calendar/<Vista>.tsx` consumiendo el mismo `CalendarTask[]` serializado.

## Debugging gCal

1. `GCAL_SYNC_ENABLED=false` → desactiva todo, útil en local
2. Logs de failure están como `console.warn('[gcal]', ...)` — no lanzan
3. Verificar token en JWT: `session.accessToken`
4. Scopes requeridos: `calendar.events` + `calendar.readonly`
