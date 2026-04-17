---
name: deta-proceso-kickoff
description: Onboarding de un proceso de reclutamiento nuevo con el cliente. Indexa materiales del cliente en NotebookLM, extrae síntesis de cultura, estructura del área y perfil real buscado, y genera el brief de kickoff con preguntas para la reunión. Actívate cuando el usuario mencione "nuevo proceso", "arrancar proceso", "kickoff", "nuevo cliente de reclutamiento", "iniciar búsqueda", "reunión de arranque", "levantamiento del perfil" — incluso si no menciona NotebookLM.
---

# Proceso Kickoff — DETA

Prepara el onboarding de un nuevo proceso de reclutamiento indexando los materiales del cliente en NotebookLM antes de la reunión de arranque y del levantamiento del perfil de puesto.

El objetivo: que Claude (o el consultor) llegue al kickoff con contexto profundo del cliente — no solo el JD, sino la cultura, la estructura real y los gaps que el JD no dice.

---

## Cuándo usar

- Se inicia un proceso de reclutamiento nuevo
- El cliente compartió materiales (organigrama, JD anterior, presentación de empresa, políticas)
- Se necesita preparar preguntas de levantamiento o un brief antes de crear el perfil de puesto

**Si el cliente no compartió ningún documento** → ejecutar flujo sin notebook, generar preguntas de kickoff con lo que se sabe del puesto y la industria.

---

## Flujo en Claude Code

```bash
# 1. Crear notebook del proceso
notebooklm create "Reclutamiento: [PUESTO] - [CLIENTE]" --json   # guardar el ID

# 2. Indexar materiales del cliente
notebooklm use [ID]
notebooklm source add [RUTA_ORGANIGRAMA]
notebooklm source add [RUTA_JD_ANTERIOR]
notebooklm source add [RUTA_MATERIALES]                   # repetir por cada doc

# 3. Extraer síntesis de kickoff
notebooklm ask "Analiza los documentos del cliente [CLIENTE] para el puesto [PUESTO]: (1) síntesis de cultura y valores de la empresa, (2) estructura del área donde entra el puesto, (3) qué busca realmente la empresa más allá del JD, (4) posibles gaps o inconsistencias en el perfil descrito, (5) 8 preguntas clave para la reunión de kickoff con el cliente" --save-as-note --note-title "Kickoff: [PUESTO] - [CLIENTE]"
```

Generar `BriefKickoff_[Puesto]_[Cliente]_[YYYYMMDD].md` y guardar el notebook ID para usarlo en las entrevistas.

---

## Flujo en Cowork

Generar el prompt desde:
`~/.claude/memory/DETA/Prompts/cowork/proceso-kickoff.md`

Skill completo de Cowork:
`Agent/Templates/skills/proceso-kickoff.md`

---

## Formato del brief de kickoff

```markdown
# Brief de Kickoff: [PUESTO] — [CLIENTE]
Fecha: [YYYYMMDD]
Notebook ID: [ID]   ← guardar para las entrevistas

## Síntesis del cliente
[cultura, valores, contexto de la empresa en 3-5 líneas]

## Estructura del área
[quién reporta a quién, tamaño del equipo, contexto de la posición]

## Perfil real buscado
[lo que buscan más allá del JD — intangibles, contexto de la búsqueda]

## Gaps o alertas del JD
- [inconsistencia o punto que aclarar]
- [expectativa poco realista o ambigua]

## Preguntas para la reunión de kickoff
1. [pregunta]
2. [pregunta]
...

## Documentos indexados
- [lista de fuentes]
```

---

## Conexión con el workflow de reclutamiento

El notebook creado aquí es el mismo que se usa en el skill `entrevista` y `reporte-pool`.
Al terminar el kickoff, anotar el ID en el brief de proceso para no perderlo:

```
Notebook: [ID]   ← campo en el prompt de entrevista
```

---

## Notas

- Un notebook por proceso/cliente — no eliminarlo hasta cerrar la búsqueda
- Si el cliente no tiene documentos digitales: crear el notebook igual, agregar el JD + notas de la llamada
- El brief de kickoff reemplaza o complementa el levantamiento manual del perfil
- Pasar el brief a `perfiles-puesto` como input para generar el perfil formal
