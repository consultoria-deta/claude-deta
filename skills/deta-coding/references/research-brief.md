# Research Brief — deta-coding superskill

> Generado 2026-04-16. NLM notebook: `32661852-e983-4bd0-91e0-c29eff6cd301` (efímero).
> 15 fuentes indexadas: Next.js 16 docs, Drizzle docs, Auth.js v5 docs, React 19, Tailwind v4, Biome, TypeScript TSConfig, Neon guides, artículos de comunidad 2025-2026.

---

## 1. Conocimiento nuclear

1. **Promesas en params/searchParams (Next.js 15+):** `params` y `searchParams` son promesas — DEBEN resolverse con `await`. Retornan `undefined` si se leen de forma síncrona.
2. **Server Actions para mutaciones internas:** Para interacciones UI → servidor, usar Server Actions. Route Handlers se reservan para webhooks, APIs públicas e integraciones externas.
3. **Patrón Result Type:** Las Server Actions NUNCA lanzan errores no controlados ni devuelven strings. Devuelven `ActionResult<T>` tipado que `useActionState` puede consumir.
4. **Auth.js v5 — función `auth()` unificada:** `getServerSession`, `getToken`, `getSession` están obsoletos. Una sola función `auth()` exportada desde `auth.ts` cubre todos los contextos.
5. **Split config para Edge:** El Drizzle adapter no es compatible con Edge runtime. La config de Auth.js se divide en `auth.config.ts` (edge-safe, solo providers) y `auth.ts` (con adapter + db).
6. **Drizzle + Neon serverless:** En Vercel no se puede usar TCP nativo. Usar `@neondatabase/serverless` con `neon-http` para queries simples o `Pool` con WebSocket para transacciones.
7. **React 19 — forwardRef obsoleto:** `ref` se pasa como prop normal. `forwardRef` queda en desuso. `<Context>` reemplaza `<Context.Provider>`.
8. **Tailwind v4 — CSS-first config:** `@import "tailwindcss"` reemplaza las tres directivas `@tailwind`. Config en `@theme {}` en CSS, no en JS. Sin `postcss-import` ni `autoprefixer`.
9. **Server Components por defecto:** `'use client'` solo cuando hay `useState`, `useEffect`, eventos del browser o APIs del cliente.
10. **TypeScript — `verbatimModuleSyntax`:** Fuerza `import type` explícito, eliminando ambigüedades entre importaciones de valor y tipo.

---

## 2. Anti-patrones

| Anti-patrón | Por qué falla | Fix |
|---|---|---|
| Route Handler para mutaciones UI internas | Latencia extra, tipos duplicados, rompe el modelo mental | Server Action pasado a `<form action={...}>` o Client Component |
| `authOptions` monolítico en middleware | Drizzle adapter no es Edge-compatible → crash en Vercel | Separar `auth.config.ts` (edge-safe) + `auth.ts` (con adapter) |
| `getServerSession(authOptions)` en v5 | API obsoleta desde Auth.js v5 | `const session = await auth()` |
| Lanzar `throw` en Server Actions que retornan Result | Rompe el tipo de retorno; `useActionState` no puede manejarlo | `return { ok: false, error: 'mensaje' }` |
| Driver TCP nativo en Vercel serverless | Agota conexiones — "Too many connections" | `@neondatabase/serverless` con HTTP o WebSocket pool |
| `forwardRef` en React 19 | Obsoleto — TS lo marca como deprecated | Pasar `ref` como prop normal en funciones componente |
| `bg-[var(--mi-color)]` en Tailwind v4 | Sintaxis de corchetes ambigua en v4 | `bg-(--mi-color)` — sintaxis de paréntesis |
| `border border-gray-200` asumido — solo `border` | Default de border color en v4 es `currentColor`, no `gray-200` | Especificar color explícito siempre |
| `bg-opacity-*`, `text-opacity-*` | Eliminados en v4 | `bg-black/50`, `text-black/50` |
| ESLint + Prettier | Stack DETA usa Biome como único linter/formatter | `biome check --write` — nada más |

---

## 3. Edge cases

1. **Agotamiento de conexiones en Vercel serverless:** Sin `@neondatabase/serverless`, cada función crea una conexión TCP nueva → "Too many connections". Fix: usar `Pool` de Neon con `neonConfig.webSocketConstructor = WebSocket` en producción.

2. **OAuth callback URL detrás de proxy/Vercel:** El callback de Google OAuth falla con URL incorrecta cuando hay un reverse proxy. Fix: `AUTH_TRUST_HOST=true` para que Auth.js confíe en `X-Forwarded-Host`.

3. **Webhook raw body corrompido:** Si se usa `await request.json()` antes de verificar la firma de Stripe/webhook, la verificación criptográfica falla. Fix: `await request.text()` para leer el raw body antes de parsear.

4. **Tailwind v4 — gradientes en dark mode:** `dark:via-transparent` no resetea el gradiente en v4. Fix: `dark:via-none` para volver a gradiente de dos colores.

5. **Server Action closure con variables sensibles:** Variables capturadas en closures de Server Actions se envían cifradas al cliente y de vuelta. No confiar solo en el cifrado — filtrar datos sensibles en el DAL antes de exponerlos.

---

## 4. Estructura propuesta

```
deta-coding/
├── SKILL.md                    ← reglas inflexibles + stack + patrones core
└── references/
    ├── research-brief.md       ← este archivo
    ├── server-actions.md       ← ActionResult<T>, DAL, seguridad, useActionState
    ├── drizzle-neon.md         ← conexión, transacciones, schema, migrations
    ├── auth-patterns.md        ← split config, Google OAuth, session, edge
    ├── tailwind-v4.md          ← migración, @theme, utility renames, CSS vars
    └── deta-tokens-code.md     ← CSS vars DETA, liquid glass, tokens en Tailwind
```

---

## 5. Scripts reutilizables

### ActionResult<T> — contrato unificado de Server Actions

```typescript
// lib/types.ts
export type ActionResult<T = null> =
  | { ok: true; data: T }
  | { ok: false; error: string }
```

### Drizzle + Neon connection (Vercel-ready)

```typescript
// lib/db/index.ts
import { neonConfig, Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import ws from 'ws'
import * as schema from './schema'

if (process.env.NODE_ENV === 'production') {
  neonConfig.webSocketConstructor = ws
} else {
  neonConfig.wsProxy = (host) => `${host}:5433/v1`
  neonConfig.useSecureWebSocket = false
  neonConfig.pipelineTLS = false
  neonConfig.pipelineConnect = false
}

const pool = new Pool({ connectionString: process.env.DATABASE_URL })
export const db = drizzle(pool, { schema })
```

### Auth.js v5 split config

```typescript
// auth.config.ts — edge-safe
import type { NextAuthConfig } from 'next-auth'
import Google from 'next-auth/providers/google'

export const authConfig: NextAuthConfig = {
  providers: [Google],
  pages: { signIn: '/auth/signin' },
}

// auth.ts — full config con Drizzle adapter
import NextAuth from 'next-auth'
import { DrizzleAdapter } from '@auth/drizzle-adapter'
import { db } from '@/lib/db'
import { authConfig } from './auth.config'

export const { auth, handlers, signIn, signOut } = NextAuth({
  ...authConfig,
  adapter: DrizzleAdapter(db),
  session: { strategy: 'database' },
})
```

---

## 6. Triggers naturales

1. "Inicia un formulario para crear/editar [X] con Server Actions y Zod"
2. "Configura Auth.js v5 con Drizzle y Neon sin que rompa en Edge"
3. "Este componente usa `useFormState` y `forwardRef`, pásalo a React 19"
4. "Quiero que el cambio de estado se vea instantáneo con `useOptimistic`"
5. "Crea la tabla [X] en Drizzle para PostgreSQL"
6. "Hay un error de `params.id` no es asíncrono en Next.js"
7. "Migra este componente a Tailwind v4 — los gradientes en dark mode fallan"
8. "Necesito un webhook público que escuche Stripe con verificación de firma"
9. "Abre una PR para [feature]"
10. "Corre el verify antes de mergear"

---

## 7. Skills adyacentes

- `deta-frontend` → diseño visual, motion, liquid glass, composición espacial
- `deta-brand` → tokens específicos DETA, assets estáticos, OG images, PDFs
- `deta-ops` → skill operativa de la app — cómo crear tasks/leads/proyectos vía API

---

## 8. Riesgos de sobre-ingeniería

- **No sugerir ESLint ni Prettier** — stack usa Biome exclusivamente
- **No sugerir Context Providers globales** — React 19 + Server Components hacen innecesarios los Providers masivos
- **No crear Route Handlers para datos UI** — Server Actions directamente
- **No sugerir UI libs pesadas** (MUI, Bootstrap) — Tailwind v4 + primitivos propios
- **No agregar validación para escenarios imposibles** — confiar en el stack y los tipos TS

---

## Decisiones de Claude (override del brief NLM)

- **ACEPTÉ:** Split auth config — alineado con la arquitectura actual del proyecto
- **ACEPTÉ:** `ActionResult<T>` con `{ ok: true/false }` — mantengo la convención del proyecto (`ok` en lugar de `success`) para no romper code existente
- **ACEPTÉ:** `neon-http` como driver primario para queries simples (menos overhead), WebSocket Pool solo para transacciones
- **RECHACÉ:** `ActionResult` con estado inicial `{ success: null }` de NLM — innecesario; `useActionState` maneja estado inicial sin ese tercer estado
- **AUMENTÉ:** Sección de seguridad con IDOR check — las fuentes lo mencionan pero no lo enfatizan suficiente para una app que maneja leads/clientes reales
- **AUMENTÉ:** Integración de tokens DETA brand en el contexto de código — el NLM no tenía fuentes DETA-específicas
