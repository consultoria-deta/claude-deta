# Deployment Checklist — Coding Skill Reference

## Pre-deployment

### Código

- [ ] Build pasa sin errores: `pnpm build`
- [ ] TypeScript sin errores: `pnpm type-check`
- [ ] ESLint sin warnings críticos
- [ ] Tests pasan (si hay tests)
- [ ] No console.log en código de producción
- [ ] No hardcoded URLs (usar variables de entorno)

### SEO

- [ ] Title tags únicos por página (50-60 chars)
- [ ] Meta descriptions únicas por página (150-160 chars)
- [ ] H1 único por página
- [ ] Alt text en todas las imágenes
- [ ] Schema markup en homepage
- [ ] Open Graph tags para social sharing
- [ ] Canonical URLs configuradas
- [ ] sitemap.xml generado
- [ ] robots.txt configurado

### Imágenes

- [ ] Formato WebP con fallback JPG/PNG
- [ ] Dimensiones explícitas (width/height)
- [ ] Lazy loading en imágenes below the fold
- [ ] Priority loading en hero image
- [ ] Imágenes optimizadas (calidad 80-85%)
- [ ] Tamaño máximo: 200KB por imagen

### Performance

- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1
- [ ] Fonts con display: swap
- [ ] CSS minificado
- [ ] JS bundle split por página

## Variables de entorno

### Requeridas (production)

```bash
# .env.production
NEXT_PUBLIC_SITE_URL=https://tudominio.com
DATABASE_URL=postgresql://...
# Añadir todas las variables obligatorias
```

### Opcionales

```bash
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_ANALYTICS_ID=
```

### Locales (nunca commitear)

```bash
# .env.local (en .gitignore)
DATABASE_URL=postgresql://...
API_SECRET_KEY=xxx
```

## Vercel Setup

### 1. Conectar repo

1. Ir a vercel.com/dashboard
2. New Project → Import Git Repository
3. Seleccionar repo de GitHub
4. Framework: Next.js (auto-detect)
5. Root Directory: `.` (o la carpeta del proyecto)

### 2. Configurar build

```
Build Command: pnpm build
Output Directory: .next
Install Command: pnpm install --frozen-lockfile
```

### 3. Environment Variables

1. En Vercel dashboard → Project → Settings → Environment Variables
2. Añadir cada variable con su valor correcto
3. Para production: valores de producción
4. Para preview/development: valores de staging

### 4. Dominio personalizado

1. Project Settings → Domains
2. Añadir: tudominio.com
3. Configurar DNS:
   - A record: 76.76.21.21 (Vercel)
   - CNAME: cname.vercel.com

## GitHub Actions

### Workflow básico

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm type-check
      - run: pnpm lint
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

### Secrets en GitHub

1. Settings → Secrets and variables → Actions
2. New repository secret:
   - VERCEL_TOKEN (de vercel.com/settings/tokens)
   - VERCEL_ORG_ID (del output de `vercel env pull`)
   - VERCEL_PROJECT_ID (del output de `vercel env pull`)
   - DATABASE_URL

## Post-deployment

### Verificación

- [ ] Sitio carga correctamente
- [ ] Rutas funcionan (/servicios, /contacto, etc.)
- [ ] Formularios submit correctamente
- [ ] API routes responden
- [ ] HTTPS activo
- [ ] SSL certificate válido
- [ ] Favicon visible
- [ ] 404 page custom funciona

### Monitoreo

- [ ] Google Analytics o alternativa configurada
- [ ] Sentry o error tracking configurado
- [ ] Uptime monitoring activo
- [ ] Vercel Analytics habilitado

### Caché

- [ ] Vercel Cache headers configurados
- [ ] Static assets con cache headers correctos
- [ ] ISR/SSR cache configurado apropiadamente

## Rollback

### Rápido

1. Vercel Dashboard → Deployments
2. Seleccionar deployment anterior
3. Click "..." → "Promote to Production"

### Con Git

```bash
# Revertir a commit anterior
git revert HEAD
git push origin main

# O crear branch de hotfix
git checkout -b hotfix
git revert <bad-commit>
git push origin hotfix
# Crear PR y merge
```

## Troubleshooting

### Build falla

```
Error: pnpm install failed
→ Verificar pnpm-lock.yaml existe y es correcto
→ Verificar node-version en package.json

Error: Module not found
→ Verificar imports son case-sensitive
→ Verificar path aliases en tsconfig.json

Error: TypeScript error
→ Correr pnpm type-check localmente
→ Verificar strict mode no rechazó algo que pasaba antes
```

### Deployment lento

- Reducir tamaño de node_modules
- Usar --frozen-lockfile para cache más rápido
- Verificar no hay install script muy largo

### Errores runtime

- Revisar logs en Vercel Dashboard → Functions
- Verificar todas las variables de entorno están configuradas
- Revisar que DATABASE_URL es correcto para producción
