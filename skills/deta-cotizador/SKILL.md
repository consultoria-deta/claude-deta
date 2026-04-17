---
name: deta-cotizador
description: Módulo Cotizador de DETA Ops. Actívate con "quote", "cotización", "cotizador", "pdf", "weasyprint", "catalog", "catálogo", "servicio", o cuando el usuario trabaje en `app/(app)/quotes`, `lib/quotes`, `components/quotes`, `lib/integrations/pdf.ts`, `app/api/service-catalog`.
---

# DETA Ops — Cotizador

Genera cotizaciones con catálogo de servicios y exporta a PDF (via WeasyPrint feature-flag).

## Rutas y archivos

| Qué | Dónde |
|-----|-------|
| Listado | `app/(app)/quotes/page.tsx` |
| Editor nuevo | `app/(app)/quotes/new/page.tsx` + `components/quotes/QuoteEditor.tsx` |
| Editor edición | `app/(app)/quotes/[id]/page.tsx` |
| Server actions | `lib/quotes/actions.ts` |
| Schema + enums | `lib/quotes/schema.ts` (QUOTE_STATUSES, quoteItemSchema) |
| Totales | `lib/quotes/totals.ts` (computeTotals, formatCurrency) |
| Template HTML | `lib/quotes/template.ts` (renderQuoteHtml, escHtml) |
| PDF backend | `lib/integrations/pdf.ts` (getPdfBackend, renderPdf) |
| API quotes | `app/api/quotes/route.ts` + `[id]/route.ts` + `[id]/pdf/route.ts` |
| API catálogo | `app/api/service-catalog/route.ts` + `[id]/route.ts` |
| Seed catálogo | `scripts/seed-service-catalog.mjs` |

## Schema

Tabla `quotes`: `clientId`, `projectId`, `number`, `status`, `items (jsonb)`, `subtotal`, `taxRate`, `tax`, `total`, `validUntil`, `notes`, `createdById`.

Tabla `service_catalog`: `name`, `description`, `unit`, `unitPrice`, `active`.

Status: `draft → sent → accepted | rejected | expired`.

Item shape: `{ serviceId?, name, quantity, unitPrice, discount, description? }`.

## Patrones importantes

- **`normalizeItems()`** en `actions.ts` strip-ea `serviceId: null` porque drizzle jsonb exige `string | undefined`, no null.
- **`RowItem = QuoteItem & { _uid: string }`** en `QuoteEditor` — keys estables en lista (evita `noArrayIndexKey` de Biome). Strip `_uid` antes de enviar al API: `items.map(({ _uid, ...rest }) => rest)`.
- **`escHtml()`** (no `escape`, reservado) escapa `&<>"'` en el template HTML.
- **computeTotals(items, taxRate=0.16)** — IVA MX por default. Devuelve `{ subtotal, tax, total }`.
- **Catálogo soft-delete**: `active=false` en vez de DELETE.

## PDF flag

- `QUOTE_PDF_BACKEND=html` (default) → GET `/api/quotes/[id]/pdf` devuelve HTML renderizado (preview directo en browser).
- `QUOTE_PDF_BACKEND=weasyprint` → POST a `WEASYPRINT_URL` con header `Authorization: Bearer $WEASYPRINT_TOKEN`, devuelve PDF binario.
- `getPdfBackend()` lee env; `renderPdf(html)` hace la llamada.

## Branding del template

- Playfair Display para títulos, navy-900 como color primario.
- Logo DETA embebido (data URL o URL pública configurada).
- Footer con número de cotización + `validUntil`.

## Si el usuario pide…

- **"Agregar campo a item"** → actualizar `quoteItemSchema` en `lib/quotes/schema.ts`, `ItemRow` en `QuoteEditor.tsx`, y `renderQuoteHtml` en `template.ts`.
- **"Nuevo status"** → editar `QUOTE_STATUSES` + `pgEnum` en `lib/db/schema.ts` + `db:generate`.
- **"Descuento por cotización completa"** (no por item) → agregar campo `globalDiscount` en schema, ajustar `computeTotals`.
- **"Enviar cotización por email"** → server action que arma PDF + manda con Resend (no implementado).

## Testing manual

1. `node --env-file=.env.local scripts/seed-service-catalog.mjs` → pobla 5 servicios base.
2. `/quotes/new` → agregar items desde catálogo, ver totales, guardar.
3. Botón PDF en editor → abre `/api/quotes/[id]/pdf`.
4. Con `QUOTE_PDF_BACKEND=weasyprint` → requiere Cloud Run corriendo.
