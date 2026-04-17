---
name: skill-creator-deta
description: Construye "superskills" DETA — skills con una fase de investigación profunda en NotebookLM antes de escribir el SKILL.md. Úsala cuando el usuario quiera crear una skill nueva que requiera research previo, indexar fuentes, explorar opciones tecnológicas, o diseñar un flujo complejo desde cero. Actívate con: "skill nueva", "crea una skill", "investiga y crea", "superskill", "research para skill", "quiero una skill que haga X", "diseña el flujo de", "qué opciones hay para hacer X como skill".
---

# Skill Creator DETA

Extensión de `skill-creator` que agrega una **Fase 0 de investigación con NotebookLM** antes de escribir el SKILL.md.
La fase NLM produce un brief estructurado que informa las decisiones de diseño — evita construir sobre suposiciones.

> **Base:** sigue todo el flujo de `skill-creator` (draft → test → review → iterate).
> **Diferencia:** inserta la Fase 0 antes de escribir el primer draft.

---

## Cuándo usar la Fase NLM vs. saltarla

| Situación | Hacer |
|---|---|
| Dominio nuevo, pocas fuentes internas, múltiples opciones tecnológicas | Fase NLM completa (Prompts 1 + 2 + 3) |
| Skill de mejora incremental sobre algo que ya funciona | Solo Prompt 1 (brief rápido) |
| Skill puramente operativa, flujo ya claro, sin investigación pendiente | Saltarse Fase NLM, ir directo a `skill-creator` |

Si hay duda → hacer Fase NLM. El costo es bajo; el costo de construir mal es alto.

---

## Fase 0 — Investigación NLM

### 0.1 — Scraping y fuentes

Antes de abrir NotebookLM, reunir mínimo **10 fuentes** sobre el dominio de la skill.
Para dominios tecnológicos o con muchas opciones: **15+ fuentes**.

Fuentes válidas (en orden de prioridad):
1. Documentación oficial de las herramientas candidatas
2. Repositorios GitHub con ejemplos reales
3. Comparativas técnicas / benchmarks
4. Casos de uso reales (blogs de ingeniería, Stack Overflow threads relevantes)
5. Documentos internos DETA (procedimientos, skills existentes, transcripciones)

Hacer scraping con `firecrawl scrape` cuando las páginas no son indexables directamente (Wikipedia, sitios con JS, anti-bot básico). Fallback: WebFetch para URLs simples.

```bash
# Scrape y agregar como fuente a NLM
firecrawl scrape [URL] > /tmp/fuente.md
notebooklm source add /tmp/fuente.md

# O agregar URL directamente si NLM la acepta
notebooklm source add [URL]

# Añadir archivo local
notebooklm source add [/ruta/archivo.pdf]
```

> Firecrawl corre local en `http://localhost:3002` (self-hosted, sin costo). Asegurarse de que los contenedores estén corriendo: `docker ps | grep firecrawl`.

### 0.2 — Ejecutar los prompts del brief

Los 3 prompts están en `references/nlm-research-phase.md`. Leerlo antes de ejecutar.

Flujo:
1. Ejecutar **Prompt 1** (Superskill Brief) — siempre
2. Si el brief sale vago o incompleto → ejecutar **Prompt 2** (Refinamiento)
3. Si la skill es de alta criticidad (reclutamiento, financiera, datos de cliente) → ejecutar **Prompt 3** (Adversarial)

### 0.3 — Consolidar en research-brief.md

Después de los prompts NLM:
1. Fusionar las respuestas en un solo `research-brief.md`
2. Agregar sección **"Decisiones de Claude"** al final:

```markdown
## Decisiones de Claude (override del brief NLM)

- ACEPTÉ: [punto X] — razón
- RECHACÉ: [punto Y] — razón
- AUMENTÉ: [punto Z] — razón
```

3. Guardar como `[skill-nueva]/references/research-brief.md`
4. Presentar al usuario un resumen de las **3-5 opciones principales** que emergen del brief antes de escribir el SKILL.md

---

## Fase 1 — Diseño y escritura

Con el brief aprobado, seguir el flujo estándar de `skill-creator`:

1. **Capturar intención** — confirmar objetivo, triggers, output esperado
2. **Escribir SKILL.md draft** — basado en el brief, no desde cero
3. **Test cases** — 2-3 prompts realistas
4. **Iterar** con feedback del usuario

Ver el SKILL.md de `skill-creator` para el detalle completo de cada paso.

---

## Convenciones DETA para el SKILL.md resultante

### Frontmatter obligatorio

```yaml
---
name: [nombre-kebab-case]
description: [qué hace] + [cuándo usarla] + triggers naturales en español
---
```

### Estructura de carpetas

```
[skill-nueva]/
├── SKILL.md
├── references/
│   ├── research-brief.md   ← output de la Fase NLM
│   └── [otros-refs].md
└── scripts/                ← solo si hay código reutilizable
```

### Dos copias — regla obligatoria

Toda skill que también use Cowork necesita dos copias reales (no symlinks — virtiofs no los soporta):

| Copia | Ruta | Para |
|---|---|---|
| Drive | `Agent/Templates/skills/[skill]/` | Cowork |
| Local | `~/.claude/skills/[skill]/` | Claude Code |

Si la skill es solo para Claude Code (no Cowork): solo copia local.

Al terminar, confirmar qué copias se crearon.

### Tono y estilo

- Instrucciones en imperativo, en español
- Explicar el **por qué** de cada regla — no solo el qué
- Si hay código Python: respetar el patrón de `sys.path` dual (`/mnt` + ruta macOS)
- Si produce PDFs: usar siempre `deta_pdf_base.py`, nunca redefinir tokens de color

---

## Confirmación al terminar

```
✅ Skill [nombre] creada

  📄 SKILL.md
  📋 references/research-brief.md
  [scripts/ si aplica]

Fuentes NLM indexadas: [N]
Prompts ejecutados: Brief [✓] / Refinamiento [✓/—] / Adversarial [✓/—]
Copias: Drive [✓/—] · ~/.claude/skills/ [✓]
Triggers validados: [lista de 3-5 frases]
```

---

## Referencias

- `references/nlm-research-phase.md` — los 3 prompts detallados para NotebookLM
- `skill-creator` (plugin) — flujo base de draft → test → iterate → optimize
