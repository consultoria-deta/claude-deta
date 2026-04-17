---
name: coding
description: Estándares de código, arquitectura, QA y deploy para proyectos de DETA. Actívate con cualquier mención de: código, TypeScript, Next.js, React, Drizzle, Neon, Supabase, build, deploy, componente, API, base de datos, autenticación, testing, QA, GitHub, PR, CI/CD, bug, error, refactor, arquitectura, backend, frontend, full-stack, server action, Biome, feature flag. También actívate cuando el usuario comparta código para revisar, cuando pida crear una app, página, feature o fix.
---

# Coding — Estándares de Código, Arquitectura y QA

Todo lo que se escribe en código pasa por aquí. El código debe ser correcto, legible, tipado, testeado y libre de errores antes de deploy.

**Referencias:**
- Stack Next.js + patterns → `references/nextjs-patterns.md`
- TypeScript strict → `references/typescript-guide.md`
- Drizzle + Neon (DETA Ops) → `references/drizzle-neon-patterns.md`
- Convenciones DETA Ops (server actions, feature flags, Biome) → `references/deta-ops-conventions.md`
- Supabase (legacy / otros proyectos) → `references/supabase-patterns.md`
- Deploy checklist → `references/deployment-checklist.md`

## Stack por proyecto

| Proyecto | Stack |
|----------|-------|
| DETA Ops | Next.js 16 App Router + Drizzle + Postgres Neon + next-auth v5 + Biome + Tailwind v4 |
| DETA Web (openclaw) | Next.js 14.2 + Tailwind v3 + Apps Script (forms → Sheets) |
| Diagnóstico Express PDF | Cloud Run + WeasyPrint (Python) |
| Agent/Templates | Python (ReportLab, Puppeteer) |

---

## Principios Core

0. **Nivel visual DETA** — para apps de DETA (especialmente DETA Ops), el estándar es Linear/Superhuman/Notion/Apple. "Funcional" o "decente" no son aceptables. Antes de cerrar fase visual: logo real (nunca placeholder), tipografía con contraste real de pesos, mobile 375px sin overflow horizontal, screenshot antes/después. Ver `feedback_deta-ops-visual-bar.md`.
1. **Corregir antes de avanzar** — nunca dejar un error conocido y seguir. El error se arregla ahora.
2. **Server Component por defecto** — `'use client'` solo cuando hay `useState`, `useEffect`, eventos
3. **Nunca `any`** — si el tipo es desconocido, usar `unknown` + narrowing
4. **Un commit = un concepto** — no mezclar 40 archivos de temas distintos en un commit
5. **Build pasa antes de push** — nunca pushear con build roto

---

## TypeScript — Configuración Estricta

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

**Reglas de tipado:**
- Interfaces para objetos, nunca `object` o `{}`
- Props de componentes siempre con interface dedicada: `interface HeroProps { ... }`
- Funciones utilitarias con tipo de retorno explícito
- Array access con bounds check o `noUncheckedIndexedAccess`

---

## Componentes — Arquitectura

### Estructura de carpetas (DETA Ops)
```
app/                      # App Router (routes + layouts)
  (auth)/                 # Group sin sidebar (signin)
  (app)/                  # Group con sidebar (dashboard, leads, tasks, calendar, quotes, projects, clients)
  api/                    # Route handlers
components/<module>/      # Componentes por dominio (leads, tasks, quotes, ...)
lib/
  <module>/               # schema.ts + actions.ts por módulo
  db/                     # schema drizzle + cliente
  auth/                   # next-auth config
  integrations/           # gcal, apps-script, pdf, gmail
  api/errors.ts           # errorResponse, unauthorized, notFound
  ui/                     # design system tokens + primitives
drizzle/                  # migrations generadas (NO borrar aplicadas)
scripts/                  # db-apply, seed, scaffold, sync-leads
```

### Estructura genérica (otros proyectos)
```
components/
  ui/           # Botones, cards, inputs — base reutilizable
  layout/       # Header, Footer, Nav
  [page]/       # Secciones específicas de una página
hooks/          # Custom hooks reutilizables
lib/            # Utilidades, clients, helpers
types/          # Tipos e interfaces globales
```

### Reglas de props
- Máximo 5 props — si hay más, el componente hace demasiado
- `children` es `ReactNode`, nunca `string`
- `variant` y `className` al final para permitir overrides

### Estilos
- Tailwind classes preferidas sobre inline styles
- Inline styles solo para valores dinámicos imposibles en Tailwind
- Tokens de `deta-brand` siempre — nunca hex inventados inline

---

## Server Actions (DETA Ops)

Todas las mutaciones pasan por server actions en `lib/<module>/actions.ts`. Contrato uniforme:

```ts
'use server'
export type ActionResult<T = null> = { ok: true; data: T } | { ok: false; error: string }

export async function createXAction(formData: FormData): Promise<ActionResult<{ id: string }>> {
  try {
    const session = await auth()
    if (!session?.user) return { ok: false, error: 'unauthorized' }
    const input = createXSchema.parse(normalizeForm(formData))
    const [row] = await db.insert(x).values({ ... }).returning({ id: x.id })
    revalidatePath('/x')
    return { ok: true, data: { id: row.id } }
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'unknown' }
  }
}
```

- **Siempre** `revalidatePath` después de una mutación.
- **Siempre** `auth()` al inicio.
- **Nunca** `throw` en acciones que devuelven `Result` — usa `return { ok: false, error }`.
- Dialogs consumen la acción con `useTransition` + `router.refresh()` en éxito.

## Route handlers

Usan `lib/api/errors.ts`:

```ts
export async function GET(request: Request) {
  const session = await auth()
  if (!session?.user) return unauthorized()
  try {
    const data = await db.select().from(...).where(...)
    return NextResponse.json({ data })
  } catch (error) {
    return errorResponse(error)
  }
}
```

## Feature flags

Lee de env, default seguro:

```ts
export function isGcalEnabled() {
  return process.env.GCAL_SYNC_ENABLED === 'true'
}

export function getPdfBackend(): 'html' | 'weasyprint' {
  return process.env.QUOTE_PDF_BACKEND === 'weasyprint' ? 'weasyprint' : 'html'
}
```

Regla: el flag default debe ser `html`/`false` para que el código funcione localmente sin infra externa.

## Biome (reemplaza ESLint + Prettier)

- Single quotes, no semicolons, trailing commas all, lineWidth 100
- `npx biome check --write` antes de commit
- Reglas estrictas activas:
  - `noShadowRestrictedNames` → evita `escape`, `event`, `name` como nombres de variable
  - `noArrayIndexKey` → usa IDs estables, no índices de array en React keys
  - `noExplicitAny` → usar `unknown` + narrowing
- Config en `biome.json` raíz del repo

## Next.js 16 — breaking changes internalizados

- `cookies()`, `headers()`, `params`, `searchParams` son **async**
- `middleware` se renombró a **`proxy`** (archivo `proxy.ts` en root)
- Parallel routes requieren `default.js`
- `icon`/`opengraph-image` params son async
- ESLint flat config (o usar Biome)
- Turbopack es default en dev

---

## HTML-first → Next/Tailwind

Para páginas con composición visual compleja:

1. Diseñar en HTML/CSS puro standalone
2. Aprobar composición, jerarquía, spacing
3. Portar a Next/Tailwind casi 1:1 — no reinterpretar
4. El HTML aprobado es el master visual

**CSS Translation Strategy:**

| Stack | Cuándo |
|---|---|
| CSS Modules | Diseño complejo, muchas secciones |
| Tailwind + tokens | UI kit, componentes reutilizables |
| Inline styles | Valores dinámicos por prop |

Nunca mezclar stacks en el mismo componente.

---

## Testing — TDD

**Orden obligatorio para features nuevas:**
1. Escribir el test que describe el comportamiento esperado
2. Verificar que falla (RED)
3. Escribir el código mínimo que lo pasa (GREEN)
4. Refactorizar sin romper (REFACTOR)

```bash
# Unit tests con Vitest
npm run test

# E2E con Playwright
npx playwright test

# Coverage
npm run test:coverage
```

**Qué testear:**
- Funciones de negocio críticas → unit tests
- Flujos de usuario clave → E2E (login, onboarding, checkout)
- Componentes con lógica → integration tests

---

## GitHub Workflow

### Branches
```
main          → producción (protegida)
feat/nombre   → features nuevas
fix/nombre    → bugs
chore/nombre  → configuración, deps
```

### Commits semánticos
```
feat(homepage): add hero section
fix(auth): correct token expiration check
refactor(card): extract to shared component
chore(deps): update next to 15.2
docs(readme): add setup instructions
perf(images): add lazy loading to gallery
```

### Pull Request checklist
- [ ] Build pasa sin errores
- [ ] Tests pasan
- [ ] Sin `console.log` ni `any` sin justificar
- [ ] Descripción clara del cambio y por qué
- [ ] Screenshots si hay cambios visuales

### GitHub Actions — CI automático
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run type-check
      - run: npm run build
      - run: npm run test
```

### Claude Code Review en PRs
```yaml
# .github/workflows/claude-review.yml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--model claude-sonnet-4-6"
```

---

## Deploy Pipeline

### App nueva desde cero
```bash
# 1. Scaffold
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# 2. Git init
git init && git add -A && git commit -m "chore: init project"

# 3. GitHub repo
gh repo create <nombre> --private --source . --remote origin --push

# 4. Deploy inicial
npx vercel --prod

# 5. Env vars
vercel env add DATABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
```

### Edit workflow — App existente
```bash
git checkout main && git pull
# ... hacer cambios ...
npm run build          # verificar antes de commit
git add -A && git commit -m "feat: descripción"
git push
vercel --prod
```

---

## SEO On-Page — Checklist

Por cada página en Next.js, verificar en `page.tsx`:

```typescript
export const metadata: Metadata = {
  title: 'Keyword Principal | DETA Consultores',  // 50-60 chars
  description: 'Descripción con keyword y CTA. Agenda tu diagnóstico...', // 150-160 chars
  keywords: ['keyword principal', 'keyword 2', 'keyword 3'],
  openGraph: {
    title: '...',
    description: '...',
    type: 'website',
    url: 'https://detaconsultores.com/pagina',
    siteName: 'DETA Consultores',
  },
  twitter: { card: 'summary_large_image', title: '...', description: '...' },
}
```

**Jerarquía heading obligatoria:**
- Un solo H1 por página con keyword principal
- H2s con keywords secundarias (3-5 por página)
- No saltar niveles (H1 → H3 sin H2)

---

## QA — Checklist de Deploy

### Antes de commit
- [ ] `npm run build` sin errores
- [ ] `npm run type-check` sin errores
- [ ] Sin `console.log` ni `any` injustificado
- [ ] Sin imports no utilizados

### Antes de push
- [ ] Mobile (375px) se ve correcto
- [ ] Desktop (1280px) se ve correcto
- [ ] Todos los links funcionan
- [ ] Sin placeholder, TODO, XXX
- [ ] Teléfono y email son reales

### Antes de deploy a producción
- [ ] GitHub Actions pasan ✅
- [ ] Vercel preview deploy OK
- [ ] Verificar site en producción
- [ ] Assets (imágenes, fuentes) cargan
- [ ] OG image visible al compartir link

---

## Progress Updates durante builds largos

Si un build o deploy toma >30 segundos, dar updates cada 30-60s:
```
🔄 Iniciando build...
📦 Dependencias instaladas, compilando TypeScript...
🚀 Subiendo a Vercel...
✅ Deploy completo → https://...
```

No dejar al usuario sin información.

---

## Dependencias — Reglas

1. No agregar dependencia sin justificar con una razón concreta
2. Verificar que no venga ya en Next.js o Tailwind
3. `npm install` después de cualquier cambio a `package.json`
4. Nunca hardcodear secrets — todo en `.env.local` y `vercel env`
