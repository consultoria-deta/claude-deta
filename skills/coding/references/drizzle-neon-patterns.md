# Drizzle + Neon (Postgres) — Patrones DETA Ops

## Setup

```bash
npm i drizzle-orm @neondatabase/serverless
npm i -D drizzle-kit
```

`.env.local`:
```
DATABASE_URL=postgresql://...?sslmode=require&channel_binding=require   # pooled
DATABASE_URL_UNPOOLED=postgresql://...?sslmode=require                  # para migrations
```

`lib/db/index.ts`:
```ts
import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import * as schema from './schema'

if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL missing')
const client = neon(process.env.DATABASE_URL)
export const db = drizzle(client, { schema })
```

## Schema — convenciones

`lib/db/schema.ts` es la fuente de verdad. Enums con `pgEnum`:

```ts
import { pgEnum, pgTable, text, timestamp, uuid } from 'drizzle-orm/pg-core'

export const leadStageEnum = pgEnum('lead_stage', [
  'new', 'contacted', 'qualified', 'proposal', 'won', 'lost',
])

export const leads = pgTable('leads', {
  id: uuid('id').defaultRandom().primaryKey(),
  email: text('email'),
  name: text('name'),
  stage: leadStageEnum('stage').notNull().default('new'),
  sheetRowId: text('sheet_row_id').unique(),     // idempotencia
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})
```

Reglas:
- `uuid` con `defaultRandom()` como PK (nunca serial/incremental en DETA Ops)
- `timestamp` con `defaultNow().notNull()` para `createdAt`/`updatedAt`
- FK con `.references(() => table.id, { onDelete: 'cascade' })` cuando el borrado debe propagarse
- `jsonb` para estructuras complejas (items de cotización, metadata)
- Enums exportados también desde `lib/<module>/schema.ts` como `const` para usar en UI:
  ```ts
  export const LEAD_STAGES = ['new','contacted','qualified','proposal','won','lost'] as const
  export type LeadStage = (typeof LEAD_STAGES)[number]
  ```

## Migrations

```bash
# Generar a partir de schema
npm run db:generate    # → drizzle/0001_<name>.sql

# Aplicar a Neon (sin TTY — drizzle-kit push requiere TTY que no tenemos en CI)
node --env-file=.env.local scripts/db-apply.mjs
```

**Regla:** nunca borrar un SQL de `drizzle/` que ya se aplicó en prod. Si hay que revertir, generar una migration nueva que deshaga.

## Queries comunes

```ts
import { and, count, desc, eq, gte, isNotNull, sum } from 'drizzle-orm'

// Select simple
const rows = await db.select().from(leads).where(eq(leads.stage, 'new'))

// Join
const rows = await db
  .select()
  .from(projects)
  .leftJoin(clients, eq(clients.id, projects.clientId))

// Aggregate (dashboard)
const [{ total }] = await db
  .select({ total: sum(quotes.total) })
  .from(quotes)
  .where(eq(quotes.status, 'sent'))

// Insert returning
const [row] = await db.insert(leads).values({ ... }).returning({ id: leads.id })

// Update
await db.update(leads).set({ stage, updatedAt: new Date() }).where(eq(leads.id, id))

// Delete (cascade via schema)
await db.delete(leads).where(eq(leads.id, id))
```

## Server components — dashboard paralelo

```ts
// Varias aggregate queries en paralelo para TTFB bajo
const [activeLeads, tasksToday, quotesDraft] = await Promise.all([
  db.select({ c: count() }).from(leads).where(ne(leads.stage, 'lost')),
  db.select({ c: count() }).from(tasks).where(and(gte(tasks.scheduledAt, start), lte(tasks.scheduledAt, end))),
  db.select({ c: count() }).from(quotes).where(eq(quotes.status, 'draft')),
])
```

## jsonb pitfall

Drizzle `jsonb` en TS espera `T | undefined`, NO `T | null | undefined`. Si tu schema zod permite `null`:

```ts
function normalizeItems(items: QuoteItem[]) {
  return items.map((it) => ({
    ...it,
    ...(it.serviceId ? { serviceId: it.serviceId } : {}),   // strip null
  }))
}
```

## Studio

```bash
npm run db:studio
```

UI local para inspeccionar datos, no editar schema.
