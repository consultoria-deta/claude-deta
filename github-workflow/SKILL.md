---
name: github-workflow
description: Git workflow, GitHub, Pull Requests, code review y CI/CD con GitHub Actions para proyectos de DETA. Actívate con cualquier mención de: git, github, commit, push, pull, branch, merge, PR, pull request, code review, conflicto, rebase, stash, tag, release, CI/CD, GitHub Actions, pipeline, workflow yaml, deploy automático, integración continua, entrega continua, repositorio, fork, clone. También actívate cuando el usuario quiera conectar Claude Code a GitHub para automatización.
---

# GitHub Workflow — Git, GitHub y CI/CD

Flujo completo de trabajo con Git y GitHub. Desde el primer commit hasta CI/CD automatizado con GitHub Actions y Claude Code como reviewer.

---

## Flujo Diario — Feature Development

```bash
# 1. Siempre partir de main actualizado
git checkout main && git pull

# 2. Crear branch para la feature
git checkout -b feat/nombre-descriptivo

# 3. Trabajar, hacer commits frecuentes
git add -A
git commit -m "feat(scope): descripción clara del cambio"

# 4. Build local pasa antes de push
npm run build && npm run type-check

# 5. Push y abrir PR
git push -u origin feat/nombre-descriptivo
gh pr create --title "feat: descripción" --body "## Qué cambia\n...\n## Screenshots\n..."

# 6. Después de merge
git checkout main && git pull
git branch -d feat/nombre-descriptivo
```

---

## Commits Semánticos — Referencia

```
feat(scope):     nueva funcionalidad
fix(scope):      corrección de bug
refactor(scope): refactorización sin cambio funcional
docs(scope):     solo documentación
style(scope):    formato, espacios, punto y coma
perf(scope):     mejora de performance
test(scope):     agregar o corregir tests
chore(scope):    configuración, deps, build tools
ci(scope):       cambios en CI/CD
```

**Ejemplos buenos:**
```
feat(homepage): add testimonials section with carousel
fix(auth): correct magic link redirect URL in production
refactor(card): extract CardHeader to separate component
chore(deps): upgrade next from 14.2 to 15.1
ci(actions): add Claude Code review on PR open
perf(images): add next/image with lazy loading
```

**Ejemplos malos:**
```
fix stuff          # demasiado vago
update files       # no dice qué ni por qué
WIP                # no debe llegar a main
FINAL FINAL        # señal de proceso roto
```

---

## Branches — Convención

```
main              → producción, siempre deployable, protegida
feat/nombre       → feature nueva
fix/nombre        → corrección de bug
refactor/nombre   → refactor sin feature nueva
chore/nombre      → config, deps, tooling
docs/nombre       → solo documentación
hotfix/nombre     → fix urgente directo a main
```

**Reglas:**
- Nunca trabajar directo en `main`
- Branches vivir máximo 3-5 días — PRs pequeños y frecuentes
- Nombres en minúsculas, guiones, descriptivos: `feat/supabase-auth-magic-link`

---

## Pull Requests — Template

```markdown
## ¿Qué hace este PR?
[Descripción clara y concisa del cambio]

## ¿Por qué se hace este cambio?
[Contexto: qué problema resuelve]

## Tipo de cambio
- [ ] Nueva feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Docs
- [ ] Config/chore

## Checklist
- [ ] Build pasa sin errores
- [ ] Type-check pasa
- [ ] Tests pasan (si aplica)
- [ ] Sin console.log ni any injustificado
- [ ] Mobile y desktop verificados (si hay cambio visual)

## Screenshots
[Si hay cambios visuales, incluir antes/después]
```

---

## GitHub Actions — CI Automático

### CI básico (build + type-check + tests)
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, 'feat/**', 'fix/**']
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run type-check

      - name: Build
        run: npm run build

      - name: Run tests
        run: npm run test
        if: always()
```

### Claude Code Review en cada PR
```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  claude-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--model claude-sonnet-4-6 --max-turns 3"
```

**Setup una vez:**
```bash
# En Claude Code terminal
/install-github-app
# Seguir el wizard interactivo
```

### Deploy a Vercel en merge a main
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        run: |
          npm i -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }} --yes
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## Branch Protection — Configurar en GitHub

En Settings → Branches → Add rule para `main`:
- [x] Require pull request reviews before merging (1 reviewer)
- [x] Require status checks to pass (CI workflow)
- [x] Require branches to be up to date
- [x] Include administrators

---

## Comandos Útiles de Emergencia

```bash
# Deshacer último commit (sin perder cambios)
git reset --soft HEAD~1

# Deshacer cambios en un archivo
git checkout -- archivo.tsx

# Guardar trabajo temporalmente
git stash
git stash pop

# Ver qué cambió
git diff
git log --oneline -10

# Resolver conflicto de merge
git merge main                     # traer cambios de main
# Resolver conflictos manualmente en el editor
git add .
git commit -m "merge: resolve conflicts with main"

# Rebase interactivo (limpiar commits antes de PR)
git rebase -i HEAD~3               # últimos 3 commits

# Hotfix urgente en producción
git checkout main && git pull
git checkout -b hotfix/descripcion
# ... hacer el fix ...
npm run build                      # verificar
git add -A && git commit -m "hotfix: descripción"
git push
gh pr create --title "hotfix: descripción"
```

---

## .gitignore — Template Next.js + Supabase

```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Next.js
.next/
out/
build/

# Environment variables — NUNCA commitear
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts

# OS
.DS_Store
Thumbs.db

# Debug
npm-debug.log*
yarn-debug.log*
```

---

## Configuración de Secrets en GitHub

```bash
# Agregar secrets via GitHub CLI
gh secret set ANTHROPIC_API_KEY
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID
# Seguir prompts para pegar el valor
```

O en GitHub UI: Settings → Secrets and variables → Actions → New repository secret

---

## Reglas de Oro

1. **Nunca pushear a main directo** — todo pasa por PR
2. **Build roto = no se mergea** — el CI protege main
3. **PRs pequeños y frecuentes** — mejor 5 PRs de 50 líneas que 1 de 250
4. **Un PR = un propósito** — no mezclar feature + refactor + fix en el mismo PR
5. **Commit con contexto** — el mensaje explica el *qué* y el *por qué*
