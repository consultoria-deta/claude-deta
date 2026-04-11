# Next.js Patterns — Coding Skill Reference

## App Router

### Layouts

```tsx
// app/layout.tsx — Root layout (todas las páginas)
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}

// app/servicios/layout.tsx — Layout específico de sección
export default function ServiciosLayout({ children }: { children: React.ReactNode }) {
  return (
    <section>
      <ServicesNav />
      {children}
    </section>
  );
}
```

### Routing dinámico

```tsx
// app/blog/[slug]/page.tsx — Ruta con parámetro
interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);
  
  if (!post) notFound();
  
  return <Article post={post} />;
}

// app/products/[category]/[id]/page.tsx — Múltiples parámetros
export default async function ProductPage({ params }: { params: Promise<{ category: string; id: string }> }) {
  const { category, id } = await params;
  const product = await getProduct(category, id);
  return <ProductDetail product={product} />;
}

// generateStaticParams para SSG
export async function generateStaticParams() {
  const products = await getAllProducts();
  return products.map((product) => ({
    category: product.category,
    id: product.id,
  }));
}
```

### Parallel routes

```tsx
// app/@modal/(.)photo/[id]/page.tsx
// Crea ruta modal que se sobrepone a la principal

// app/photo/[id]/page.tsx — Principal
export default function PhotoPage({ params }: { params: Promise<{ id: string }> }) {
  return <PhotoView id={params.id} />;
}
```

### Intercepting routes

```tsx
// app/@modal/(.)photo/[id]/page.tsx
// Intercepta navegación y muestra modal en vez de página completa

// Útil para lightboxes sin cambiar URL
```

## Data Fetching

### Fetching en Server Components

```tsx
// Forma simple
async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`, {
    next: { revalidate: 3600 }, // ISR: revalidate cada hora
  });
  return res.json();
}

// En componente
export default async function UserProfile({ id }: { id: string }) {
  const user = await getUser(id);
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### Fetching paralelo

```tsx
//Parallel data fetching
async function getUserData(userId: string) {
  const [user, posts, comments] = await Promise.all([
    fetch(`/api/users/${userId}`).then(r => r.json()),
    fetch(`/api/users/${userId}/posts`).then(r => r.json()),
    fetch(`/api/users/${userId}/comments`).then(r => r.json()),
  ]);
  
  return { user, posts, comments };
}
```

### Sequential fetching

```tsx
// Cuando el segundo depende del primero
async function getDashboard() {
  // Primero obtener usuario
  const user = await fetchUser();
  
  // Después obtener datos basados en el usuario
  const stats = await fetchStats(user.tenantId);
  
  return { user, stats };
}
```

## Forms

### Server Actions (form action)

```tsx
// app/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { z } from 'zod';

const ContactSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  message: z.string().min(10),
});

export async function submitContact(formData: FormData) {
  const data = {
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message'),
  };
  
  const result = ContactSchema.safeParse(data);
  if (!result.success) {
    return { error: 'Datos inválidos', details: result.error.flatten() };
  }
  
  await sendEmail(result.data);
  revalidatePath('/contacto');
  redirect('/contacto/gracias');
}
```

```tsx
// Componente
import { submitContact } from '@/app/actions';

export function ContactForm() {
  return (
    <form action={submitContact}>
      <input name="name" type="text" required />
      <input name="email" type="email" required />
      <textarea name="message" required />
      <button type="submit">Enviar</button>
    </form>
  );
}
```

### Form con useActionState

```tsx
'use client';

import { useActionState } from 'react';
import { submitContact } from '@/app/actions';

const initialState = { error: null };

export function ContactForm() {
  const [state, formAction, isPending] = useActionState(submitContact, initialState);
  
  return (
    <form action={formAction}>
      <input name="name" type="text" />
      {state.error && <p className="error">{state.error}</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Enviando...' : 'Enviar'}
      </button>
    </form>
  );
}
```

## Middleware

```typescript
// middleware.ts (en raíz del proyecto)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Añadir header a todas las respuestas
  const response = NextResponse.next();
  response.headers.set('X-Custom-Header', 'value');
  
  // Redirecciones
  if (request.nextUrl.pathname.startsWith('/old-path')) {
    return NextResponse.redirect(new URL('/new-path', request.url));
  }
  
  // Rewrites
  if (request.nextUrl.pathname.startsWith('/blog')) {
    return NextResponse.rewrite(new URL('/blog-proxy', request.url));
  }
  
  return response;
}

// Config para qué paths aplicar
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

## Caching

### fetch caching

```typescript
// Revalidation por tiempo
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 }, // Revalidar cada hora
});

// Revalidation permanente (solo en build)
const staticData = await fetch('https://api.example.com/static', {
  next: { revalidate: false }, // Nunca revalidar
});

// Tag-based revalidation
const data = await fetch('https://api.example.com/products', {
  next: { tags: ['products'] },
});

// Revalidar por tag
import { revalidateTag } from 'next/cache';
revalidateTag('products');
```

### Route segment caching

```typescript
// app/products/page.tsx
export const revalidate = 3600; // Revalidar cada hora

// app/products/[id]/page.tsx
export const dynamicParams = true; // Generar bajo demanda si no está en generateStaticParams
export const revalidate = false; // Siempre dynamic

// Forzar static
export const dynamic = 'force-static';
```

## Error handling

### Error boundaries

```tsx
// app/error.tsx (error boundary a nivel de segmento)
'use client';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Algo salió mal</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Reintentar</button>
    </div>
  );
}

// app/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h1>404 — Página no encontrada</h1>
    </div>
  );
}
```

### try/catch en Server Components

```tsx
async function getData() {
  try {
    const data = await fetchRiskyData();
    return { data, error: null };
  } catch (error) {
    if (error instanceof NetworkError) {
      return { data: null, error: 'Error de red' };
    }
    return { data: null, error: 'Error desconocido' };
  }
}
```

## Streaming

### Suspense boundaries

```tsx
import { Suspense } from 'react';

function ProductPage({ id }: { id: string }) {
  return (
    <div>
      <ProductHeader />
      <Suspense fallback={<ProductSkeleton />}>
        <ProductDetails id={id} />
      </Suspense>
      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews id={id} />
      </Suspense>
    </div>
  );
}
```

### Loading states

```tsx
// app/dashboard/loading.tsx — Se muestra mientras carga cualquier ruta hija
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 w-1/3 rounded" />
      <div className="h-4 bg-gray-200 w-1/2 rounded mt-4" />
    </div>
  );
}
```

## Authentication

### Middleware para auth

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token');
  
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}
```

### Session en Server Components

```typescript
// lib/auth.ts
import { cookies } from 'next/headers';

export async function getSession() {
  const cookieStore = await cookies();
  const token = cookieStore.get('auth-token');
  
  if (!token) return null;
  
  try {
    return await verifyToken(token.value);
  } catch {
    return null;
  }
}

// Uso en Server Component
async function DashboardPage() {
  const session = await getSession();
  
  if (!session) {
    redirect('/login');
  }
  
  return <Dashboard user={session.user} />;
}
```

## Image optimization

```tsx
import Image from 'next/image';

export function OptimizedImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={800}
      height={600}
      sizes="(max-width: 768px) 100vw, 50vw"
      quality={85}
      placeholder="blur" // Si hay blurDataURL
      blurDataURL={src.replace(/\.(jpg|png)$/, '.blur')}
    />
  );
}
```

## Environment variables

### Naming conventions

```bash
# Público (visible en browser) — NEXT_PUBLIC_
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXX

# Privado (solo server)
DATABASE_URL=postgresql://...
API_SECRET=xxx
```

### Acceso en código

```typescript
// Server (API routes, Server Components)
const dbUrl = process.env.DATABASE_URL;

// Client (solo con NEXT_PUBLIC_)
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
```

## Streaming con fetch

```typescript
// Streaming de datos con ReadableStream
export async function GET() {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const data = await fetchLargeDataset();
      
      for (const item of data) {
        controller.enqueue(encoder.encode(JSON.stringify(item) + '\n'));
      }
      
      controller.close();
    },
  });
  
  return new Response(stream, {
    headers: { 'Content-Type': 'application/json' },
  });
}
```
