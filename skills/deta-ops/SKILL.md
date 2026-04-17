---
name: deta-ops
description: Contexto y convenciones de DETA Ops (app interna operativa). Actívate con cualquier mención de "DETA Ops", "ops", "app interna", "mission control", o cuando el usuario trabaje en `~/Code/deta-ops`. También cuando pida crear un módulo, fix o feature en la app interna.
---

# DETA Ops — skill de contexto

App interna operativa de DETA Consultores. Sucesor de Mission Control. Centraliza agenda, CRM, cotizador, proyectos y clientes.

## Stack
- Next.js 16 App Router (Turbopack) + React 19.2 + TS strict
- Drizzle ORM + Postgres 17 (Neon, pgvector habilitado)
- next-auth v5 beta + Google OAuth (allowlist `detaconsultores.com`)
- Biome (format + lint, single quotes, no semicolons, trailing commas all, line 100)
- Tailwind CSS v4 con `@theme`
- `@dnd-kit/core` para Kanbans
- Vitest + Playwright
- Repo: `/Users/joelestrada/Code/deta-ops`

## Módulos ya construidos
| Módulo | Ruta | Estado |
|--------|------|--------|
| Auth + sidebar | `app/(app)/layout.tsx` | ✅ |
| Agenda (calendar) | `/calendar` mes/semana | ✅ |
| gCal sync | feature-flag `GCAL_SYNC_ENABLED` | ✅ code-complete |
| CRM leads | `/leads` Kanban + ficha | ✅ |
| Apps Script read | `scripts/sync-leads.mjs` + `docs/apps-script-read.md` | ✅ |
| Cotizador | `/quotes`, PDF flag `QUOTE_PDF_BACKEND` | ✅ |
| Dashboard real | `/` con KPIs | ✅ |
| Tasks Kanban | `/tasks` | ✅ |
| Proyectos | `/projects` + `/projects/[id]` | ✅ |
| Clientes | `/clients` + `/clients/[id]` | ✅ |
| Ingest API | `/api/ingest/{task,lead,project}` + `docs/INGEST.md` | ✅ |

## Convenciones del repo

**Server actions** viven en `lib/<module>/actions.ts` y devuelven siempre:
```ts
type Result<T = null> = { ok: true; data: T } | { ok: false; error: string }
```

**Route handlers** usan `lib/api/errors.ts` (`errorResponse`, `unauthorized`, `notFound`) y guardan sesión con `auth()` de `@/lib/auth` al inicio.

**Schemas zod** viven en `lib/<module>/schema.ts`. Exportan también los enums como `const` (`LEAD_STAGES`, `TASK_STATUSES`).

**Dialogs** (client components) en `components/<module>/<Entity>Dialog.tsx`. Patrón estable:
- `open`/`onClose` controlado por el padre
- `useTransition` + `router.refresh()` tras éxito
- `<form action={handleSubmit}>` con `FormData`
- Estilos con tokens `--color-navy-900`, `--color-cyan-600`, `--color-border`, clase `input`

**Kanbans** usan `@dnd-kit/core` (no sortable). Patrón: `useOptimistic` + server action + `router.refresh()`.

**Server components** hacen todas las queries con drizzle y pasan datos serializados (ISO strings) al client.

## Reglas de ejecución

- ✅ Autorizado: refactors, migrations (`npm run db:generate` → `node --env-file=.env.local scripts/db-apply.mjs`), `npm run verify`, crear ramas `feat/*`, push a ramas feature, `gh pr create`
- ❌ Sin confirmación: push a main, borrar migrations aplicadas, tocar `.env.production`, `vercel --prod`, rotar secrets

## Antes de reportar "listo"

Siempre correr `npm run verify` (typecheck + lint + test + build). Si falla, arreglar antes de commitear.

## Prioridad actual

1. Activar secrets y ejecutar migraciones en Neon (tarea manual del usuario)
2. Pegar Apps Script de `docs/apps-script-read.md` y llenar env vars
3. Probar cada módulo end-to-end en `npm run dev`
4. Siguiente: Fase final (Electron desktop packaging)

## Skills hermanas que se cargan solas
- `deta-agenda` — cuando toque agenda/calendar/gCal
- `deta-crm` — leads, pipeline, interactions
- `deta-cotizador` — quotes, catálogo, PDF
- `deta-kanban-ops` — reglas comunes de Kanbans drag-drop
- `coding` — estándares generales
