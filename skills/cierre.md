---
name: cierre
description: Cierre de sesión — actualiza archivos de memoria del proyecto activo, Hot-Cache y hace sync al repo consultoria-deta/claude-deta. Usar al terminar una sesión o cuando el usuario lo solicite. Si el usuario dice "sin cache", omitir actualización de Hot-Cache.md.
type: workflow
---

# Cierre de sesión

Ejecutar en orden. Si el usuario dijo **"sin cache"**, omitir el paso 2.

---

## Paso 1 — Actualizar memoria del proyecto activo

Identificar qué proyecto se trabajó en la sesión y actualizar su archivo:

| Proyecto | Archivo |
|----------|---------|
| DETA Web / openclaw / sitio | `~/.claude/projects/-Users-joelestrada/memory/project_deta-web.md` |
| Agent/Templates / entrevistas / PDFs | `~/.claude/projects/-Users-joelestrada/memory/project_agent-templates.md` |
| Diagnóstico Express / Cloud Run | `~/.claude/projects/-Users-joelestrada/memory/project_diagnostico-express-pdf.md` |
| Otro / general | Crear o actualizar el archivo correspondiente |

Escribir solo lo que cambió: completados nuevos, decisiones, pendientes actualizados.
Mantener el mismo formato del archivo existente.

También actualizar la copia en bóveda Obsidian (`~/.claude/memory/Projects/`).

---

## Paso 2 — Actualizar Hot-Cache.md *(omitir si "sin cache")*

Archivo: `~/.claude/memory/Hot Cache/Hot-Cache.md`

Actualizar:
- Mover ítems de "Completado en sesión anterior" a la sección de historial correspondiente
- Agregar nuevos completados de esta sesión con la fecha de hoy
- Actualizar la lista de **Pendiente** — quitar lo que se hizo, agregar lo nuevo

---

## Paso 3 — Sync al repo consultoria-deta/claude-deta

```bash
# 1. Asegurar repo local actualizado
cd /tmp && (test -d claude-deta && cd claude-deta && git pull || gh repo clone consultoria-deta/claude-deta)

# 2. Skills
cp ~/.claude/skills/*.md /tmp/claude-deta/skills/

# 3. Agent/Templates
DRIVE_TEMPLATES="/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates"
rsync -a --delete "$DRIVE_TEMPLATES/" /tmp/claude-deta/Templates/

# 4. Commit y push
cd /tmp/claude-deta
git add .
git diff --cached --quiet || git commit -m "sync: cierre $(date '+%Y-%m-%d')" && git push
```

---

## Paso 4 — Confirmar al usuario

Responder con una línea por ítem:

```
Actualicé memoria: [archivos tocados]
Sync github: skills/ + Templates/ → consultoria-deta/claude-deta
Hot-Cache: actualizado  ← (o "omitido" si "sin cache")
```
