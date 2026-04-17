# DETA Ops — Convenciones operativas

Referencia rápida para código dentro de `~/Code/deta-ops`. Complementa a `SKILL.md` y a las skills de dominio (`deta-ops`, `deta-agenda`, `deta-crm`, `deta-cotizador`, `deta-kanban-ops`).

## Módulos y responsabilidades

| Módulo | Schema | Actions | UI raíz |
|--------|--------|---------|---------|
| Leads (CRM) | `lib/leads/schema.ts` | `lib/leads/actions.ts` | `app/(app)/leads/` + `components/leads/` |
| Tasks | `lib/tasks/schema.ts` | `lib/tasks/actions.ts` | `app/(app)/tasks/` + `/calendar/` + `components/{tasks,calendar}/` |
| Quotes | `lib/quotes/schema.ts` | `lib/quotes/actions.ts` | `app/(app)/quotes/` + `components/quotes/` |
| Projects | `lib/projects/schema.ts` | `lib/projects/actions.ts` | `app/(app)/projects/` + `components/projects/` |
| Clients | `lib/clients/schema.ts` (embedded) | `lib/clients/actions.ts` | `app/(app)/clients/` + `components/clients/` |

## Patrón Dialog (client component)

```tsx
'use client'
export function XDialog({ open, onClose, initial }: Props) {
  const router = useRouter()
  const [pending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(formData: FormData) {
    setError(null)
    startTransition(async () => {
      const result = initial?.id
        ? await updateXAction(initial.id, formData)
        : await createXAction(formData)
      if (!result.ok) return setError(result.error)
      onClose()
      router.refresh()
    })
  }
  if (!open) return null
  return <dialog><form action={handleSubmit}>...</form></dialog>
}
```

## Patrón Kanban

Ver skill `deta-kanban-ops`. Resumen: `DndContext` + `useDraggable` + `useDroppable` + `useOptimistic` + server action.

## Tokens CSS

En `app/globals.css` con `@theme`:
```css
--color-navy-900: #0c2b40;
--color-cyan-600: #2a9bb8;
--color-surface: #fff;
--color-surface-subtle: #f4f6f8;
--color-border: #e5e7eb;
--color-ink-muted: #6b7280;
```

Uso: `bg-[var(--color-navy-900)]`, nunca hex inventado inline.

## Scripts clave

| Script | Propósito |
|--------|-----------|
| `npm run dev` | Turbopack dev server |
| `npm run verify` | typecheck + lint + test + build |
| `npm run db:generate` | Nueva migration desde schema |
| `node --env-file=.env.local scripts/db-apply.mjs` | Aplicar migrations a Neon |
| `npm run db:studio` | UI drizzle |
| `node --env-file=.env.local scripts/sync-leads.mjs --dry` | Test sync Apps Script |
| `node --env-file=.env.local scripts/seed-service-catalog.mjs` | Poblar catálogo cotizador |

**Siempre** correr `npm run verify` antes de reportar "listo".

## Autorizaciones

| Acción | Autorizada sin preguntar |
|--------|--------------------------|
| Refactors en el repo | ✅ |
| Crear migration + aplicar a Neon | ✅ |
| Crear rama `feat/*`/`fix/*`/`chore/*` y pushear | ✅ |
| `gh pr create` | ✅ |
| `git push origin main` | ❌ |
| Borrar migrations aplicadas | ❌ |
| Tocar `.env.production` | ❌ |
| `vercel --prod` | ❌ |
| Rotar secrets (`AUTH_SECRET`, `DATABASE_URL`) | ❌ |

## Feature flags vigentes

- `GCAL_SYNC_ENABLED` — activa sync bidireccional con Google Calendar (default off)
- `QUOTE_PDF_BACKEND=html|weasyprint` — html = preview local, weasyprint = microservicio Cloud Run
- `AUTH_ALLOWED_DOMAIN` — dominio permitido para login Google (default permite todos)

## Integraciones externas

- **Apps Script read** (leads del sitio): `docs/apps-script-read.md`, endpoint tokenizado
- **Ingest API** (tokens externos): `docs/INGEST.md`, `POST /api/ingest/{task,lead,project}`
- **gCal**: `lib/integrations/gcal.ts` (placeholder `refreshAccessToken` pendiente para prod)
- **PDF WeasyPrint**: `lib/integrations/pdf.ts` (Cloud Run en `diagnostico-express-pdf-640198914101.us-central1.run.app`)

## Convención de ramas y PRs

- Cada batch/módulo en su propia rama `feat/<nombre>`
- PR con resumen conciso + test plan
- Merge local a main durante sesiones autónomas, push manual del usuario después
