---
name: deta-coding
description: Superskill de desarrollo fullstack para proyectos DETA (DETA Ops, DETA Web). Fusiona coding conventions, deta-brand tokens en código, y mejores prácticas 2026 del stack: Next.js 16 App Router + Drizzle + Neon + Auth.js v5 + Biome + Tailwind v4 + React 19. Cargar para cualquier tarea de código en proyectos DETA.
---

# DETA Coding — Superskill

## Stack canónico DETA Ops

```
Next.js 16 App Router + React 19 + TypeScript strict
Drizzle ORM 0.45+ + @neondatabase/serverless + Postgres 17 Neon
Auth.js v5 (next-auth) + Drizzle adapter + Google OAuth
Biome 2.x (linter + formatter — sin ESLint, sin Prettier)
Tailwind v4 + @tailwindcss/postcss
Zod 4+ para validación de entrada
```

**DETA Web:** Next.js 14.2 + Tailwind v3 (no usar v4 aquí).

---

## Principios — no negociables

1. **Estándar visual DETA:** Linear / Superhuman / Apple HIG. "Funcional" o "decente" = inaceptable. Logo real, tipografía con peso real, mobile 375px sin overflow, screenshot antes/después en fases visuales.
2. **Corregir antes de avanzar** — nunca dejar un error conocido y continuar.
3. **Server Component por defecto** — `'use client'` solo con `useState`, `useEffect`, eventos o APIs de browser.
4. **Nunca `any`** — si el tipo es desconocido, usar `unknown` + narrowing.
5. **Sin ESLint ni Prettier** — Biome exclusivamente. `npx biome check --write` antes de commit.
6. **Build pasa antes de push** — nunca pushear con build roto.
7. **Un commit = un concepto.**

---

## TypeScript — config estricta

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "verbatimModuleSyntax": true
  }
}
```

**`noUncheckedIndexedAccess`:** todo acceso a array/objeto por índice puede ser `undefined` — verificar antes de usar.
**`exactOptionalPropertyTypes`:** `foo?: T` (puede estar ausente) ≠ `foo: T | undefined` (presente pero undefined).
**`verbatimModuleSyntax`:** fuerza `import type` explícito para importaciones de tipo.

---

## Server Actions — patrón unificado

Toda mutación vive en `lib/<module>/actions.ts`. Contrato fijo:

```typescript
'use server'
import type { ActionResult } from '@/lib/types'

export async function createLeadAction(
  formData: FormData,
): Promise<ActionResult<{ id: string }>> {
  try {
    const session = await auth()
    if (!session?.user) return { ok: false, error: 'unauthorized' }

    const input = createLeadSchema.parse({
      name: formData.get('name'),
      email: formData.get('email'),
    })

    const [row] = await db.insert(leads).values(input).returning({ id: leads.id })
    revalidatePath('/leads')
    return { ok: true, data: { id: row.id } }
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'unknown' }
  }
}
```

**Reglas fijas:**
- `auth()` al inicio — siempre, sin excepción.
- Validar input con Zod en el perímetro — nunca confiar en datos del cliente.
- **Verificar ownership del recurso** (IDOR): `if (post.authorId !== session.user.id) return { ok: false, error: 'forbidden' }`.
- `revalidatePath` o `revalidateTag` después de toda mutación.
- Nunca `throw` en acciones que retornan Result — `return { ok: false, error }`.
- Devolver solo los campos que el cliente necesita — nunca el registro crudo de DB.

### Tipo ActionResult

```typescript
// lib/types.ts
export type ActionResult<T = null> =
  | { ok: true; data: T }
  | { ok: false; error: string }
```

### Consumo en Client Component

```typescript
'use client'
import { useActionState } from 'react'
import { createLeadAction } from '@/lib/leads/actions'

export function CreateLeadForm() {
  const [result, action, pending] = useActionState(createLeadAction, null)

  return (
    <form action={action}>
      <input name="name" />
      <button disabled={pending}>{pending ? 'Guardando…' : 'Crear lead'}</button>
      {result && !result.ok && <p className="text-red-500">{result.error}</p>}
    </form>
  )
}
```

### Actualizaciones optimistas

```typescript
import { useOptimistic } from 'react'

const [optimisticStatus, setOptimistic] = useOptimistic(task.status)

async function handleStatusChange(newStatus: string) {
  setOptimistic(newStatus)
  await updateTaskStatusAction(task.id, newStatus)
}
```

---

## Data Access Layer (DAL)

Para proyectos de producción con datos sensibles (leads, clientes, cotizaciones), aislar el acceso a datos en `lib/<module>/dal.ts` marcado con `import 'server-only'`:

```typescript
// lib/leads/dal.ts
import 'server-only'
import { cache } from 'react'
import { auth } from '@/lib/auth'
import { db } from '@/lib/db'

export const getCurrentUserLeads = cache(async () => {
  const session = await auth()
  if (!session?.user?.id) return []
  return db.select().from(leads).where(eq(leads.assignedTo, session.user.id))
})
```

- `React.cache()` deduplica queries idénticas dentro de un mismo render pass.
- El DAL devuelve DTOs mínimos — nunca el registro completo.
- Las Server Actions delegan al DAL; no acceden a DB directamente.

---

## Route Handlers — cuándo usarlos

**Usar Route Handlers (`app/api/*/route.ts`) solo para:**
- Webhooks externos (Stripe, Apps Script, servicios de terceros)
- APIs públicas consumidas por clientes externos
- Integraciones con servicios que requieren HTTP explícito

**Webhooks — siempre leer raw body:**

```typescript
export async function POST(request: Request) {
  const body = await request.text() // raw body para verificar firma
  const sig = request.headers.get('stripe-signature') ?? ''
  // verificar firma antes de parsear JSON
  const event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!)
  // ...
}
```

---

## Drizzle + Neon

### Conexión (Vercel-ready)

```typescript
// lib/db/index.ts
import { neonConfig, Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import ws from 'ws'
import * as schema from './schema'

if (process.env.NODE_ENV !== 'production') {
  neonConfig.wsProxy = (host) => `${host}:5433/v1`
  neonConfig.useSecureWebSocket = false
  neonConfig.pipelineTLS = false
  neonConfig.pipelineConnect = false
} else {
  neonConfig.webSocketConstructor = ws
}

const pool = new Pool({ connectionString: process.env.DATABASE_URL })
export const db = drizzle(pool, { schema })
```

**Por qué WebSocket Pool y no HTTP:** Neon HTTP driver no soporta transacciones interactivas. Pool WebSocket funciona para ambas.

### Schema — identity columns (Postgres moderno)

```typescript
import { pgTable, text, timestamp } from 'drizzle-orm/pg-core'

export const leads = pgTable('leads', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  name: text('name').notNull(),
  email: text('email').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})
```

### Transacciones

```typescript
await db.transaction(async (tx) => {
  await tx.insert(leads).values(leadData)
  await tx.insert(events).values({ type: 'lead_created', refId: leadData.id })
})
```

### Migrations

```bash
# Generar migration sin TTY (Vercel / CI)
npx drizzle-kit generate
node --env-file=.env.local scripts/db-apply.mjs

# Nunca borrar migrations ya aplicadas en producción
```

### Preloading (evitar waterfalls)

```typescript
import { cache } from 'react'

export const getProject = cache(async (id: string) => {
  return db.query.projects.findFirst({ where: eq(projects.id, id) })
})

// En la page — iniciar fetch antes de que lo necesite el componente hijo
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  void getProject(id) // preload sin await
  const isAuthorized = await checkAccess(id)
  return isAuthorized ? <ProjectDetail id={id} /> : <Forbidden />
}
```

---

## Auth.js v5

### Split config (obligatorio para Edge)

```typescript
// auth.config.ts — edge-safe, sin Drizzle
import type { NextAuthConfig } from 'next-auth'
import Google from 'next-auth/providers/google'

export const authConfig: NextAuthConfig = {
  providers: [Google],
  pages: { signIn: '/auth/signin' },
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user
      const isPublic = ['/auth/signin', '/api/auth'].some(p => nextUrl.pathname.startsWith(p))
      return isPublic || isLoggedIn
    },
  },
}

// auth.ts — config completa con Drizzle adapter
import NextAuth from 'next-auth'
import { DrizzleAdapter } from '@auth/drizzle-adapter'
import { db } from '@/lib/db'
import { authConfig } from './auth.config'

export const { auth, handlers, signIn, signOut } = NextAuth({
  ...authConfig,
  adapter: DrizzleAdapter(db),
  session: { strategy: 'database' },
  callbacks: {
    ...authConfig.callbacks,
    session({ session, user }) {
      session.user.id = user.id
      return session
    },
  },
})
```

```typescript
// proxy.ts (Next.js 16 — reemplaza middleware.ts)
export { auth as proxy } from './auth.config'
```

### Uso — siempre `auth()`, nunca las APIs v4

```typescript
// Server Component / Server Action / Route Handler — mismo patrón
const session = await auth()
if (!session?.user) return unauthorized()
```

### Variables de entorno

```
AUTH_SECRET=<openssl rand -base64 32>
AUTH_GOOGLE_ID=...
AUTH_GOOGLE_SECRET=...
AUTH_TRUST_HOST=true  # obligatorio detrás de Vercel/proxy
```

---

## React 19 — patrones nuevos

### `ref` como prop — no más `forwardRef`

```typescript
// Antes (React 18)
const Input = forwardRef<HTMLInputElement, InputProps>(({ placeholder }, ref) => (
  <input ref={ref} placeholder={placeholder} />
))

// Ahora (React 19)
function Input({ placeholder, ref }: InputProps & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} placeholder={placeholder} />
}
```

### `<Context>` sin `.Provider`

```typescript
// Antes
<ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>

// Ahora
<ThemeContext value="dark">{children}</ThemeContext>
```

### `use()` — leer contexto condicionalmente

```typescript
import { use } from 'react'

function Heading({ children }: { children: React.ReactNode }) {
  if (!children) return null
  const theme = use(ThemeContext) // puede llamarse después de un return
  return <h1 style={{ color: theme.color }}>{children}</h1>
}
```

---

## Tailwind v4 — reglas DETA Ops

### Setup CSS-first

```css
/* globals.css */
@import "tailwindcss";

@theme {
  --color-navy: #0c2b40;
  --color-gold: #d3ab6d;
  --color-cyan: #12a9cc;
  --font-display: 'Playfair Display', Georgia, serif;
  --font-sans: 'Source Sans 3', system-ui, sans-serif;
}
```

### Variables CSS — sintaxis v4

```html
<!-- v3 (roto en v4) -->
<div class="bg-[var(--color-navy)]">

<!-- v4 correcto -->
<div class="bg-(--color-navy)">
```

### Renombres críticos v3 → v4

| v3 | v4 |
|---|---|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `blur-sm` | `blur-xs` |
| `rounded-sm` | `rounded-xs` |
| `ring` | `ring-3` |
| `outline-none` | `outline-hidden` |
| `bg-opacity-50` | `bg-black/50` |
| `flex-shrink-*` | `shrink-*` |
| `flex-grow-*` | `grow-*` |

### Border — especificar color siempre

```html
<!-- v4: border sin color = currentColor (no gray-200 como en v3) -->
<div class="border border-slate-200">  <!-- siempre explícito -->
```

---

## Tokens DETA en código

### CSS variables core (en globals.css de cada proyecto)

```css
:root {
  --color-primary: #0c2b40;    /* navy */
  --color-secondary: #d3ab6d;  /* gold */
  --color-accent: #12a9cc;     /* cyan */
  --color-surface: #F5F7FA;
  --color-text-primary: #1A1A2E;
  --color-text-muted: #6B7280;
  --color-border: rgba(12,43,64,0.1);
}
```

### Tech Edition — DETA Ops (dark mode canvas)

```css
/* Canvas oscuro para DETA Ops */
--canvas: #040f1c;          /* navy-950 */
--surface: #0c2b40;         /* navy */
--surface-elevated: #0f3347;

/* Liquid glass */
--glass-panel: rgba(12,43,64,0.72);
--glass-card: rgba(255,255,255,0.03);
--glass-input: rgba(255,255,255,0.04);

/* Motion */
--duration-fast: 120ms;
--duration-base: 200ms;
--duration-slow: 360ms;
--ease-out: cubic-bezier(0.22, 1, 0.36, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Logo — regla de uso

```typescript
// Sobre fondo oscuro/navy → logo blanco
<img src="/logo-deta-white.svg" alt="DETA" className="h-8" />

// Sobre fondo claro → logo cyan
<img src="/logo-deta-cyan.svg" alt="DETA" className="h-8" />

// Nunca logo cyan sobre fondo navy — el contraste desaparece
```

### Iconos — Lucide React exclusivamente

```typescript
import { ChevronRight, Plus, Trash2 } from 'lucide-react'

// stroke siempre 1.5 — tamaño 24px contenido, 20px elementos pequeños
<ChevronRight className="size-5 stroke-[1.5] text-cyan-400" />
```

---

## Biome — config canónica DETA

```json
{
  "$schema": "https://biomejs.dev/schemas/2.0.0/schema.json",
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "all",
      "semicolons": "asNeeded"
    }
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "organizeImports": { "enabled": true }
}
```

```bash
# Antes de cada commit
npx biome check --write
```

---

## Estructura de carpetas — DETA Ops

```
app/
  (auth)/          # signin — sin sidebar
  (app)/           # rutas protegidas con sidebar
    layout.tsx
    page.tsx       # dashboard
    leads/
    tasks/
    calendar/
    quotes/
    projects/
    clients/
  api/
    auth/[...nextauth]/route.ts
    ingest/        # endpoints tokenizados externos
components/
  <module>/        # por dominio: leads/, tasks/, quotes/…
  chrome/          # AppShell, Sidebar, TopBar, MobileNav
  ui/              # primitivos: Button, Card, Badge, Dialog…
lib/
  <module>/
    schema.ts      # tipos Zod + inferencia
    actions.ts     # server actions
    dal.ts         # data access layer (server-only)
  db/
    index.ts       # cliente drizzle+neon
    schema.ts      # schema drizzle
  auth/            # auth.ts + auth.config.ts
  api/
    errors.ts      # errorResponse, unauthorized, notFound
  types.ts         # ActionResult<T> y tipos globales
drizzle/           # migrations generadas — nunca borrar aplicadas
scripts/           # db-apply.mjs, seed-*.mjs, scaffold.mjs
```

---

## Caching — cuándo y cómo

```typescript
// React.cache() — deduplicar queries en el mismo render pass
import { cache } from 'react'

export const getTaskById = cache(async (id: string) => {
  return db.query.tasks.findFirst({ where: eq(tasks.id, id) })
})

// unstable_cache — persistir resultado entre requests (ISR-like)
import { unstable_cache } from 'next/cache'

export const getCachedStats = unstable_cache(
  async () => db.select({ count: count() }).from(leads),
  ['lead-stats'],
  { tags: ['leads'], revalidate: 300 },
)

// revalidateTag — invalidar desde una action
revalidateTag('leads')

// dynamic = 'force-dynamic' — para rutas que siempre deben ser frescas
export const dynamic = 'force-dynamic'
```

---

## GitHub workflow — DETA Ops

```
main         → producción (protegida — hook bloquea push directo)
feat/nombre  → features nuevas
fix/nombre   → bugs
chore/nombre → config, deps
```

```bash
# Antes de abrir PR
npm run verify   # typecheck + lint + test + build

# Crear PR
gh pr create --title "feat(leads): add sync button" --body "..."
```

Claude puede: crear ramas `feat/*` / `fix/*` / `chore/*`, pushear a esas ramas, abrir PRs.
Claude NO puede: `git push origin main`, borrar migrations aplicadas, tocar `.env.production`.

---

## QA — checklist antes de PR

- [ ] `npm run verify` sin errores (typecheck + biome + vitest + build)
- [ ] Sin `console.log`, `any`, `TODO` sin issue
- [ ] `auth()` llamado en toda server action y route handler
- [ ] Ownership del recurso verificado (no solo autenticación)
- [ ] `revalidatePath` / `revalidateTag` después de cada mutación
- [ ] Mobile 375px sin scroll horizontal
- [ ] Logo DETA real (no placeholder)
- [ ] Tokens DETA — sin hex inventados inline

---

## Referencias

- `references/research-brief.md` — brief NLM completo con fuentes
- `references/server-actions.md` — patrones avanzados de mutaciones
- `references/drizzle-neon.md` — schema, queries, transacciones
- `references/auth-patterns.md` — Auth.js v5 edge cases
- `references/tailwind-v4.md` — migración completa v3→v4
