---
name: deta-debugging
description: Playbook de debugging sistemático específico para DETA Ops y proyectos DETA. Actívate con "debug", "bug", "error", "no funciona", "falla", "unauthorized", "401", "500", "hydration", "typecheck", "migration", "drizzle", "unauthorized en server action", cuando un test truena, cuando el usuario reporta comportamiento inesperado, o cuando hay build/verify roto.
---

# DETA Debugging — Playbook

Proceso de debugging adaptado a los stacks y bugs recurrentes de DETA. Basado en `superpowers:systematic-debugging` pero con atajos por síntoma para nuestros proyectos.

## Regla de oro

```
NO HAY FIX SIN ROOT CAUSE.
```

Parchar el síntoma en DETA casi siempre crea otro bug en otra capa (Apps Script → Sheet → action → DB → UI). Identifica la capa antes de tocar código.

## Fases (mínimo viable)

1. **Evidencia** — leer el error completo, reproducir, hacer diff con lo que sí funciona (módulo hermano, commit anterior)
2. **Hipótesis única** — "creo que es X en capa Y porque Z"
3. **Fix mínimo** — 1 cambio. Si falla, nueva hipótesis, NO apilar fixes
4. **Verificar** — `npm run verify` + probar en browser o con curl

Si después de 3 intentos sigue roto → detente y cuestiona la arquitectura. No "uno más".

## Atajos por síntoma (DETA)

### `unauthorized` en server action cuando SÍ hiciste login
- **Capa**: `lib/auth.ts` + middleware/proxy
- Check: ¿`proxy.ts` existe y tiene `matcher` correcto? (en Next.js 16 se llama `proxy`, no `middleware`)
- Check: ¿`AUTH_SECRET` está en `.env.local`?
- Check: ¿`app/(app)/layout.tsx` hace `redirect('/signin')` si no hay sesión? Si no, usuarios sin login ven las páginas pero las actions tiran unauthorized.
- Check: cookie de sesión presente en DevTools → Application → Cookies

### Apps Script devuelve HTML en vez de JSON
- Signo: `SyntaxError: Unexpected token '<'` al hacer `response.json()`
- Causa más común: no redesplegaste después de editar (`Deploy → Manage deployments → pencil → New version`)
- Otra: la función `doGet` no existe o tiene error de sintaxis
- Diagnóstico rápido:
  ```bash
  curl -sL "URL" | grep -oE 'No se encontró[^<]*|Error[^<]*'
  ```
- Más en `deta-crm` skill + `docs/apps-script-read.md`

### Drizzle migration no aplica
- `drizzle-kit push` requiere TTY → usar `node --env-file=.env.local scripts/db-apply.mjs`
- Si dice "relation already exists": verifica el `drizzle/meta/_journal.json` vs lo que hay en Neon (`npm run db:studio`)
- Nunca borres un SQL aplicado — genera una migration nueva que lo deshaga

### Server action devuelve `{ok:false, error:'unknown'}`
- El `catch` está tragando el error real. Diagnóstico:
  ```ts
  } catch (error) {
    console.error('[createXAction]', error)   // temporal
    return { ok: false, error: error instanceof Error ? error.message : 'unknown' }
  }
  ```
- Revisa la consola del `npm run dev` — el server action log sale ahí

### `POST /api/xxx 401` en logs del dev server
- Client-side fetch sin cookie de sesión → pasa cuando el usuario recarga y la cookie expira, o cuando el fetch llama a una API protegida desde un Storybook/iframe
- Fix: preferir server actions sobre fetch a route handlers para operaciones autenticadas
- Si el endpoint es público (ingest, webhooks), usar `verifyIngestToken` o similar

### gCal falla al crear evento
- Flag `GCAL_SYNC_ENABLED=true`? Si está en `false` (default), el create no intenta el API call — tu código DB debería funcionar igual
- Token expirado: `lib/integrations/gcal.ts` tiene `refreshAccessToken` placeholder. En prod hay que implementarlo
- Scopes: requiere `calendar.events` + `calendar.readonly` en el OAuth client
- Los fallos de gCal NO deben romper el action — se loggean como `console.warn('[gcal]', ...)`

### PDF vacío / error al descargar
- `QUOTE_PDF_BACKEND` no setteado → default es `html`, devuelve HTML plano (preview funciona, descarga no)
- `weasyprint` seleccionado pero `WEASYPRINT_URL`/`WEASYPRINT_TOKEN` no configurados → 500
- Cloud Run caído: `curl -I $WEASYPRINT_URL/health`

### Biome rompe el build
- `noShadowRestrictedNames` → renombra variables llamadas `escape`, `event`, `name`, `length`
- `noArrayIndexKey` → en React: usa un `_uid` estable, no el índice del `.map((_, i) => key={i})`
- `noExplicitAny` → cambia a `unknown` + narrowing
- Auto-fix: `npx biome check --write`

### Hydration mismatch
- Revisa `Date` sin formato ISO, timezones, `Math.random()` en SSR
- El server component debe pasar datos serializados al client (ISO strings, no Date objects)

### Build truena pero dev funciona
- Turbopack dev es más permisivo que `next build`
- Corre `npm run build` local para reproducir
- Causa común: import cíclico, tipo any implícito, env var requerida faltante

### `verify` falla en typecheck pero no encuentras el error
- `npx tsc --noEmit` directo → ves todos los errores
- Si es en un archivo de `node_modules`, seguramente falta un types package (`npm i -D @types/xxx`)

## Evidencia antes de fix

Cuando el bug cruza varias capas (UI → action → DB → integración externa), añade logs temporales en cada frontera:

```ts
// UI (client)
console.log('[dialog] submitting', Object.fromEntries(formData))

// Action (server)
console.log('[action] input parsed', input)
console.log('[action] db returned', row)

// Integration
console.log('[gcal] event created', gcalEventId)
```

Ejecuta UNA VEZ para ver qué capa falla. Luego quita los logs.

## Red flags — detente

- "Solo pruebo esto a ver si jala" → vuelve a Fase 1
- Apilando fixes sobre el mismo síntoma → root cause está en otra capa
- "3 fixes y cada uno rompe algo diferente" → la arquitectura es el problema, no el código
- Cambiar `catch` a `console.log(error)` y olvidar quitarlo
- Commit con `verify` roto prometiendo arreglar después

## Tooling

```bash
# Ver logs del dev server
tail -f /tmp/claude-*/bu*/output   # si lo iniciaste en background

# Inspeccionar DB
npm run db:studio

# Probar Apps Script
curl -sL "$APPS_SCRIPT_READ_URL?action=leads&token=$APPS_SCRIPT_READ_TOKEN"

# Probar ingest
curl -X POST http://localhost:3000/api/ingest/lead \
  -H "Authorization: Bearer $INGEST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test"}'

# Full verify
npm run verify
```

## Escalation

- Si el bug cruza repos (deta-ops + openclaw + apps-script), marca en memoria:
  ```
  [memory] project_deta-ops.md + project_deta-web.md — bug cross-repo <breve>
  ```
- Si reproduce intermitentemente → instrumenta antes de fixear
- Si no puedes reproducir local → el bug es de env/infra, no de código
