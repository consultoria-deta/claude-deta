---
name: coding
description: Estándares de código, arquitectura, QA y deploy para proyectos de DETA. Actívate con cualquier mención de: código, TypeScript, Next.js, React, Supabase, build, deploy, componente, API, base de datos, autenticación, testing, QA, GitHub, PR, CI/CD, bug, error, refactor, arquitectura, backend, frontend, full-stack. También actívate cuando el usuario comparta código para revisar, cuando pida crear una app, página, feature o fix.
---

# Coding — Estándares de Código, Arquitectura y QA

Todo lo que se escribe en código pasa por aquí. El código debe ser correcto, legible, tipado, testeado y libre de errores antes de deploy.

**Referencias:**
- Stack detallado Next.js → `references/nextjs-patterns.md`
- TypeScript strict → `references/typescript-guide.md`
- Supabase + backend → `references/supabase-patterns.md`
- Deploy checklist → `references/deployment-checklist.md`

---

## Principios Core

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

### Estructura de carpetas
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
- Tokens de `deta-design` siempre — nunca hex inventados inline

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
