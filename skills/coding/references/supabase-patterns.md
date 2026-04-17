# Supabase — Patrones y Mejores Prácticas

## Setup inicial

```bash
npm install @supabase/supabase-js @supabase/ssr
```

```typescript
// lib/supabase/client.ts — para uso en Client Components
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// lib/supabase/server.ts — para uso en Server Components y Actions
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options))
        },
      },
    }
  )
}
```

---

## Auth — Magic Link

```typescript
// Server Action: enviar magic link
'use server'
export async function signInWithEmail(email: string) {
  const supabase = await createClient()
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
    },
  })
  if (error) throw new Error(error.message)
}

// app/auth/callback/route.ts
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')

  if (code) {
    const supabase = await createClient()
    await supabase.auth.exchangeCodeForSession(code)
  }
  return NextResponse.redirect(`${origin}/dashboard`)
}
```

---

## RLS — Row Level Security

**Regla:** Toda tabla tiene RLS activado. Sin excepción.

```sql
-- Activar RLS en tabla
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Política: usuario solo ve sus propios registros
CREATE POLICY "users_own_projects"
ON projects FOR ALL
USING (auth.uid() = user_id);

-- Política multi-tenant: usuario ve registros de su organización
CREATE POLICY "org_members_see_org_data"
ON projects FOR SELECT
USING (
  organization_id IN (
    SELECT organization_id FROM memberships
    WHERE user_id = auth.uid()
  )
);

-- Política: solo admins pueden insertar
CREATE POLICY "admins_insert"
ON projects FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM memberships
    WHERE user_id = auth.uid() AND role = 'admin'
  )
);
```

---

## Schema — Patrones

```sql
-- Tabla base con auditoría
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER projects_updated_at
  BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Índices para queries frecuentes
CREATE INDEX idx_projects_org ON projects(organization_id);
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status) WHERE status = 'active';
```

---

## Queries — Patrones con TypeScript

```typescript
// Tipos generados desde Supabase (supabase gen types typescript)
import type { Database } from '@/types/supabase'
type Project = Database['public']['Tables']['projects']['Row']

// Query con tipado completo
const { data: projects, error } = await supabase
  .from('projects')
  .select(`
    id,
    name,
    status,
    organizations (
      name,
      logo_url
    )
  `)
  .eq('status', 'active')
  .order('created_at', { ascending: false })
  .limit(20)

if (error) throw new Error(`Error fetching projects: ${error.message}`)

// Insert con manejo de error
const { data: newProject, error: insertError } = await supabase
  .from('projects')
  .insert({ name, organization_id, user_id: user.id })
  .select()
  .single()

if (insertError) throw new Error(insertError.message)
```

---

## Realtime

```typescript
// Suscripción en Client Component
useEffect(() => {
  const channel = supabase
    .channel('projects-changes')
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table: 'projects' },
      (payload) => {
        // actualizar estado local
        setProjects(prev => updateLocalState(prev, payload))
      }
    )
    .subscribe()

  return () => { supabase.removeChannel(channel) }
}, [supabase])
```

---

## Storage

```typescript
// Upload de archivo
const { data, error } = await supabase.storage
  .from('avatars')
  .upload(`${userId}/avatar.png`, file, {
    cacheControl: '3600',
    upsert: true,
  })

// URL pública
const { data: { publicUrl } } = supabase.storage
  .from('avatars')
  .getPublicUrl(`${userId}/avatar.png`)
```

---

## Variables de entorno requeridas

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # solo server-side, nunca exponer
NEXT_PUBLIC_SITE_URL=https://tu-dominio.com
```
