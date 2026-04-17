---
name: deta-blog-research
description: Investigación de temas para el blog de DETA usando NotebookLM como pre-procesador. Indexa fuentes, extrae ángulo editorial, estructura H2/H3 y keywords, y genera un brief listo para redacción. Actívate cuando el usuario mencione "artículo", "blog", "post", "investigar tema", "brief de contenido", "quiero escribir sobre", "ángulo para el artículo", "estructura del post", o cuando pida preparar contenido editorial para detaconsultores.com — incluso si no menciona NotebookLM explícitamente.
---

# Blog Research — DETA

Prepara el brief de un artículo indexando fuentes en NotebookLM antes de redactar.
El objetivo: NotebookLM sintetiza las fuentes brutas y Claude recibe un brief compacto en vez de PDFs completos.

**Si no hay fuentes disponibles** y el brief es simple → pasar directamente a `deta-content` sin notebook.

---

## Cuándo usar

- El usuario quiere escribir un artículo para detaconsultores.com
- Hay fuentes disponibles (artículos, PDFs, datos pytrends) que conviene indexar primero
- Se necesita definir ángulo, estructura o keywords antes de redactar

---

## Flujo en Claude Code

```bash
# 1. Crear notebook para el tema
notebooklm create "Blog DETA: [TEMA]" --json      # guardar el ID

# 2. Indexar fuentes
notebooklm use [ID]
notebooklm source add [RUTA_O_URL]          # repetir por cada fuente

# 3. Extraer brief editorial
notebooklm ask "Para un artículo sobre '[TEMA]' dirigido a dueños de PyMEs mexicanas: (1) propón 1 ángulo diferenciador respecto a lo que ya existe, (2) estructura con H2 y H3, (3) 5 keywords naturales para SEO México, (4) 2 ganchos de apertura alternativos, (5) 3 datos o estadísticas clave de las fuentes" --save-as-note --note-title "Brief: [TEMA]"
```

Generar `Brief_[Tema]_[YYYYMMDD].md` con el output y pasarlo a `deta-content` para redacción.

---

## Flujo en Cowork

Generar el prompt desde:
`~/.claude/memory/DETA/Prompts/cowork/blog-investigacion.md`

Skill completo de Cowork:
`Agent/Templates/skills/blog-investigacion.md`

---

## Formato del brief generado

```markdown
# Brief: [TEMA]
Fecha: [YYYYMMDD]

## Ángulo editorial
[diferenciador — qué hace único este artículo frente a lo que ya existe]

## Keyword principal
[keyword]

## Keywords secundarias
[lista de 4-5 keywords]

## Estructura propuesta
### H2: [sección principal]
- H3: [subsección]
- H3: [subsección]
### H2: [sección principal]
- H3: [subsección]

## Gancho de apertura — opción A
[texto de 2-3 oraciones]

## Gancho de apertura — opción B
[texto de 2-3 oraciones]

## Datos clave de las fuentes
- [dato + fuente]
- [dato + fuente]
- [dato + fuente]

## Fuentes indexadas
- [lista]
```

---

## Notas

- Un notebook por artículo — puede eliminarse después de publicar
- Datos de pytrends disponibles como CSV o texto → agregarlos como fuente antes del ask
- El brief es el input para `deta-content`
- Notebook ID no es necesario conservar a largo plazo (a diferencia del notebook de proceso de reclutamiento)
