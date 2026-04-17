---
name: app-builder
description: Construcción de aplicaciones web completas con Next.js, Supabase, autenticación, base de datos y deploy en Vercel. Actívate con cualquier mención de: construir app, crear aplicación, nueva app, dashboard, portal, sistema, plataforma, SaaS, multi-tenant, autenticación, login, base de datos, backend, API routes, server actions, Supabase, PostgreSQL, admin panel, gestión de usuarios, roles, permisos. También actívate cuando el usuario describa una app con usuarios, datos o lógica de negocio.
---

# App Builder — Aplicaciones Full-Stack con Next.js + Supabase

Construcción de aplicaciones web completas: desde el scaffold hasta producción. Stack: Next.js App Router + Supabase + Vercel.

**Referencias de código:**
- Patrones Supabase detallados → ver skill `coding` → `references/supabase-patterns.md`
- Patrones Next.js → ver skill `coding` → `references/nextjs-patterns.md`

---

## Fases de Construcción de una App

### Fase 1 — Definición (antes de escribir código)

Responder estas preguntas primero:

1. **¿Qué hace la app?** — En una oración
2. **¿Quiénes son los usuarios?** — Roles: admin, user, viewer, etc.
3. **¿Cuáles son las entidades principales?** — Tablas en la DB
4. **¿Qué acciones pueden hacer?** — CRUD por entidad y por rol
5. **¿Es multi-tenant?** — ¿Cada organización ve solo sus datos?
6. **¿Qué integraciones necesita?** — Email, pagos, terceros

### Fase 2 — Schema de Base de Datos

Diseñar el schema antes de tocar el frontend:

```sql
-- Estructura base para app multi-tenant
-- 1. Organizations (tenants)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Memberships (relación users ↔ organizations)
CREATE TABLE memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, organization_id)
);

-- 3. Entidad principal de ejemplo
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  created_by UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived')),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_memberships_user ON memberships(user_id);
CREATE INDEX idx_memberships_org ON memberships(organization_id);
CREATE INDEX idx_projects_org ON projects(organization_id);
CREATE INDEX idx_projects_status ON projects(status, organization_id);

-- RLS en todas las tablas
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Políticas RLS multi-tenant
CREATE POLICY "members_see_own_org"
ON organizations FOR SELECT
USING (id IN (
  SELECT organization_id FROM memberships WHERE user_id = auth.uid()
));

CREATE POLICY "members_see_org_projects"
ON projects FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM memberships WHERE user_id = auth.uid()
));

CREATE POLICY "admins_manage_projects"
ON projects FOR ALL
USING (organization_id IN (
  SELECT organization_id FROM memberships
  WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
));
```

### Fase 3 — Estructura de Carpetas

```
src/
  app/
    (auth)/
      login/page.tsx
      signup/page.tsx
      auth/callback/route.ts
    (dashboard)/
      layout.tsx          ← sidebar + nav compartido
      page.tsx            ← dashboard home
      [feature]/
        page.tsx
        [id]/page.tsx
    api/
      [route]/route.ts    ← solo si necesita API pública
  components/
    ui/                   ← botones, inputs, cards base
    layout/               ← sidebar, header, nav
    [feature]/            ← componentes de cada feature
  lib/
    supabase/
      client.ts           ← browser client
      server.ts           ← server client
    utils.ts
  types/
    supabase.ts           ← tipos generados
    app.ts                ← tipos de la app
  hooks/
    use-user.ts
    use-organization.ts
```

### Fase 4 — Autenticación

```typescript
// app/(auth)/login/page.tsx
'use client'
import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const supabase = createClient()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback` }
    })
    setSent(true)
  }

  if (sent) return <p>Revisa tu email para el link de acceso</p>

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="tu@email.com"
        required
      />
      <button type="submit">Entrar</button>
    </form>
  )
}

// app/auth/callback/route.ts
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const supabase = await createClient()
    await supabase.auth.exchangeCodeForSession(code)
  }
  return NextResponse.redirect(`${origin}${next}`)
}
```

### Fase 5 — Middleware de Protección

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createServerClient } from '@supabase/ssr'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return request.cookies.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options))
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  // Redirigir usuarios no autenticados
  if (!user && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Redirigir usuarios autenticados fuera del login
  if (user && request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return supabaseResponse
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api/webhook).*)'],
}
```

### Fase 6 — Server Actions (operaciones de datos)

```typescript
// app/(dashboard)/projects/actions.ts
'use server'
import { createClient } from '@/lib/supabase/server'
import { revalidatePath } from 'next/cache'

export async function createProject(formData: FormData) {
  const supabase = await createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('No autenticado')

  const name = formData.get('name') as string
  const organization_id = formData.get('organization_id') as string

  const { data, error } = await supabase
    .from('projects')
    .insert({ name, organization_id, created_by: user.id })
    .select()
    .single()

  if (error) throw new Error(error.message)

  revalidatePath('/dashboard/projects')
  return data
}
```

---

## Scaffold Rápido

```bash
# 1. Crear proyecto Next.js
npx create-next-app@latest nombre-app \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*"

cd nombre-app

# 2. Instalar Supabase
npm install @supabase/supabase-js @supabase/ssr

# 3. Variables de entorno
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
NEXT_PUBLIC_SITE_URL=http://localhost:3000
EOF

# 4. Generar tipos de TypeScript desde Supabase
npx supabase gen types typescript \
  --project-id xxx \
  --schema public > src/types/supabase.ts

# 5. Git + GitHub
git init && git add -A && git commit -m "chore: init app"
gh repo create nombre-app --private --source . --remote origin --push

# 6. Deploy inicial
npx vercel --prod
```

---

## Patrones de UI para Dashboards

### Layout con Sidebar
```typescript
// app/(dashboard)/layout.tsx
export default function DashboardLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  )
}
```

### Data Table con Server Component
```typescript
// app/(dashboard)/projects/page.tsx
import { createClient } from '@/lib/supabase/server'

export default async function ProjectsPage() {
  const supabase = await createClient()
  const { data: projects } = await supabase
    .from('projects')
    .select('*')
    .order('created_at', { ascending: false })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Proyectos</h1>
      <ProjectsTable projects={projects ?? []} />
    </div>
  )
}
```

---

## Checklist de Launch

- [ ] RLS activado en todas las tablas
- [ ] Middleware protege todas las rutas del dashboard
- [ ] Tipos TypeScript generados desde Supabase
- [ ] Build sin errores (`npm run build`)
- [ ] Variables de entorno en Vercel
- [ ] Auth callback URL en Supabase dashboard
- [ ] Email templates personalizados en Supabase
- [ ] Error boundaries en rutas críticas
- [ ] Loading states en todas las operaciones async
- [ ] OG image y metadata en cada página pública
