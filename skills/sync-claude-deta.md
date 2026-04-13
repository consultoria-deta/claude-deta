---
name: sync-claude-deta
description: Sincronizar archivos locales (skills, HTMLs, templates) al repo consultoria-deta/claude-deta en GitHub para backup y acceso desde internet vía GitHub Pages
type: workflow
---

# Sync → consultoria-deta/claude-deta

## Repo
- **GitHub:** https://github.com/consultoria-deta/claude-deta
- **GitHub Pages:** https://consultoria-deta.github.io/claude-deta/
- **Local (trabajo):** `/tmp/claude-deta` (clonar si no existe)

## Estructura de carpetas

| Carpeta repo | Fuente local | Contenido |
|---|---|---|
| `Features/` | `~/Desktop/*.html` o donde esté | HTMLs de features, prototipos, referencia visual |
| `skills/` | `~/.claude/skills/*.md` | Skills activas de Claude Code |
| `Templates/` | `~/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates/` | Templates HTML, scripts Python de Cowork |

---

## Paso 1 — Preparar repo local

```bash
# Si es la primera vez en la sesión o no existe /tmp/claude-deta:
cd /tmp && rm -rf claude-deta && gh repo clone consultoria-deta/claude-deta

# Si ya existe, solo actualizar:
cd /tmp/claude-deta && git pull
```

## Paso 2 — Copiar archivos según lo que el usuario quiera subir

### Subir un HTML a Features/
```bash
cp ~/Desktop/nombre-archivo.html /tmp/claude-deta/Features/
```

### Sincronizar una skill específica
```bash
cp ~/.claude/skills/nombre-skill.md /tmp/claude-deta/skills/
```

### Sincronizar todas las skills
```bash
cp ~/.claude/skills/*.md /tmp/claude-deta/skills/
```

### Sincronizar Agent/Templates (código y templates de Cowork)
```bash
DRIVE_TEMPLATES="/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates"
rsync -a --delete "$DRIVE_TEMPLATES/" /tmp/claude-deta/Templates/
```

## Paso 3 — Commit y push

```bash
cd /tmp/claude-deta
git add .
git commit -m "tipo: descripción breve"
git push
```

Convenciones de commit:
- `feat:` — archivo nuevo
- `update:` — versión actualizada de algo existente
- `remove:` — archivo eliminado

## Paso 4 — Verificar URL en GitHub Pages

El archivo queda accesible en:
```
https://consultoria-deta.github.io/claude-deta/Features/nombre-archivo.html
```

Pages tarda ~1 min en reflejar cambios nuevos.

---

## Cuándo ejecutar este sync

- Al terminar de trabajar un HTML/feature importante
- Cuando se modifica una skill relevante
- Al final de sesiones largas donde hubo cambios en templates o skills
- Cuando el usuario pide explícitamente hacer backup o subir algo al repo
