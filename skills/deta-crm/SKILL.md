---
name: deta-crm
description: Módulo CRM/Leads de DETA Ops. Actívate con "crm", "lead", "leads", "prospect", "pipeline", "stage", "qualify", "interaction", "apps script", "sheet", o cuando el usuario trabaje en `app/(app)/leads`, `lib/leads`, `components/leads`, `lib/integrations/apps-script.ts`.
---

# DETA Ops — CRM de Leads

Captura leads desde el sitio web (vía Google Sheet) o ingest API; los clasifica por stage y registra interacciones.

## Rutas y archivos

| Qué | Dónde |
|-----|-------|
| Kanban por stage | `app/(app)/leads/page.tsx` + `components/leads/LeadsKanban.tsx` |
| Ficha + timeline | `app/(app)/leads/[id]/page.tsx` + `components/leads/LeadDetail.tsx` |
| CRUD dialog | `components/leads/LeadDialog.tsx` |
| Server actions | `lib/leads/actions.ts` |
| Schema + enums | `lib/leads/schema.ts` (LEAD_STAGES, INTERACTION_TYPES) |
| Route handlers | `app/api/leads/route.ts` + `[id]/route.ts` + `[id]/interactions/route.ts` |
| Sync script | `scripts/sync-leads.mjs` (idempotente por sheetRowId, --dry, --mock) |
| Apps Script cliente | `lib/integrations/apps-script.ts` |
| Docs setup | `docs/apps-script-read.md` |
| Ingest endpoint | `app/api/ingest/lead/route.ts` (idempotente, docs en `docs/INGEST.md`) |

## Schema (drizzle)

Tabla `leads`: `email`, `name`, `phone`, `company`, `source`, `sheetRowId (unique)`, `stage`, `ownerId`, `clientId`, `notes`, `lastInteractionAt`.

Tabla `lead_interactions`: `leadId (cascade)`, `type`, `channel`, `summary`, `createdById`, `occurredAt`, `metadata`.

Stages: `new → contacted → qualified → proposal → won | lost`.
Interaction types: `email | call | meeting | whatsapp | note`.

## Flujos estándar

1. **Ingesta desde Sheet** → Apps Script expone `/exec?action=leads&token=…` → `scripts/sync-leads.mjs` inserta idempotentemente.
2. **Manual** → botón "Nuevo lead" en `/leads` abre `LeadDialog`.
3. **Ingest API** → `POST /api/ingest/lead` con Bearer token (respeta `sheetRowId` para idempotencia).
4. **Progreso de stage** → drag en Kanban dispara `updateLeadStageAction`.
5. **Registrar interacción** → form en ficha. Actualiza `leads.lastInteractionAt` automáticamente.

## Convenciones

- **NO** crear un lead sin `email | name | phone` mínimo (validación en Apps Script).
- `source` esperado: `web | diagnostico | linkedin | referral | manual | ingest | apps-script`.
- Eliminar un lead borra sus interactions en cascade.
- Promover a cliente = crear `clients` con datos del lead + setear `leads.clientId` (pendiente de UI, action no implementada aún).

## Si el usuario pide…

- **"Un nuevo stage"** → editar el enum en `lib/db/schema.ts` (pgEnum), correr `npm run db:generate`, actualizar `LEAD_STAGES` en `lib/leads/schema.ts`, actualizar `STAGE_LABEL` en `LeadsKanban.tsx`.
- **"Convertir lead a cliente"** → crear server action `convertToClientAction(leadId)` en `lib/leads/actions.ts` que: crea row en `clients`, actualiza `leads.clientId`, pone `stage='won'`. Añadir botón en `LeadDetail`.
- **"Ver leads de la última semana"** → agregar filtro `?from=` en `app/api/leads/route.ts` y dropdown en Kanban header.

## Testing manual

1. `node --env-file=.env.local scripts/sync-leads.mjs --mock --dry` → ver 2 leads mock
2. Apps Script real → llenar `APPS_SCRIPT_READ_URL` + `APPS_SCRIPT_READ_TOKEN`, correr sin `--mock`.
3. `/leads` → drag entre columnas, abrir ficha, registrar interaction, ver timeline.
