---
name: deta-distribucion
description: Capa delgada de reglas que resuelve el calendario semanal de distribución de contenido DETA. Recibe un tema + 8 piezas ya producidas (1 blog + 3 LinkedIn Joel + 2 LinkedIn Empresa + 1 IG Carousel + 1 YouTube) y devuelve un calendario autoritativo con fechas, horas B2B LATAM, dependencias resueltas, link policy por pieza y recomendaciones de paid amplification. NO genera copy, NO automatiza publicación, NO propone opciones — DECIDE. Activa con: "resuelve dependencias", "calendariza", "asigna horarios", "link policy", "schedule de la semana", "cuándo publicar cada cosa", "validar orden", "trigger rules de ads", "distribución de [tema]", "acomoda los posts". También se auto-invoca desde `deta-pipeline` en Paso 7-8 para sustituir el calendario hardcoded por un calendario calculado con dependencias.
---

# DETA Distribución — Capa de Reglas de Calendario Multi-Plataforma

Resuelve el calendario semanal de distribución para DETA Consultores aplicando dependencias, link policy y ventanas B2B LATAM. Fork del hardcoded que vivía en `deta-pipeline` Paso 7.

**Por qué existe:** el calendario estaba hardcoded en `deta-pipeline` sin razonar sobre dependencias. Causó el bug 2026-04-15: LinkedIn Joel 1 Martes pedía link al blog que salía Miércoles. Esta skill codifica el DAG temporal que ningún framework público (COPE, Hub-Spoke, Content Waterfall) codifica para B2B LATAM.

---

## Input esperado

```yaml
topic: "Crecer vs Consolidar"         # tema del blog ancla
slug: "crecer-vs-consolidar"          # slug del blog
pilar: "estrategia"                   # uno de los 5 pilares DETA
run_date: "2026-04-15"                # fecha cuando corre la skill (YYYY-MM-DD)
pieces:
  blog:            { ready: true, path: "content/blog/crecer-vs-consolidar.md" }
  linkedin_joel_1: { ready: true, path: "~/research/output/2026-W16/LinkedIn-Joel-1_...md" }
  linkedin_joel_2: { ready: true, path: "..." }
  linkedin_joel_3: { ready: true, path: "..." }
  linkedin_empresa_1: { ready: true }
  linkedin_empresa_2: { ready: true }
  ig_carousel:     { ready: true }
  youtube:         { ready: false }   # video sin editar → edge case
```

Si alguna pieza `ready: false`, aplicar edge case correspondiente (ver sección Edge Cases).

---

## Output — Calendario autoritativo

Siempre esta tabla markdown, en este orden exacto:

```markdown
## Calendario Semana [ISO] — [topic]

| # | Fecha | Hora (CST) | Pieza | Canal | Depende de | Link policy | Paid trigger |
|---|---|---|---|---|---|---|---|
| 1 | YYYY-MM-DD Mar | 09:00 | LinkedIn Joel 1 | LinkedIn personal | — | Sin link (teaser). Blog no existe aún. | Si ≥30 interacciones en 45 min → boost $20 |
| 2 | YYYY-MM-DD Mié | 07:00 | Blog publish | detaconsultores.com | — | — | — |
| 3 | YYYY-MM-DD Mié | 09:00 | LinkedIn Empresa 1 | LinkedIn empresa | Blog (#2) | Link al blog en primer comentario | Si ≥20 interacciones en 60 min → boost $15 |
| 4 | YYYY-MM-DD Mié | 11:00 | YouTube publish | YouTube | Blog (#2) | Descripción: link a blog + Diagnóstico Express | — (orgánico puro v1) |
| 5 | YYYY-MM-DD Jue | 09:00 | LinkedIn Joel 2 | LinkedIn personal | Blog (#2) | Link al blog en primer comentario | Si ≥30 interacciones en 45 min → boost $20 |
| 6 | YYYY-MM-DD Jue | 11:00 | IG Carousel | Instagram | — (no estricta) | CTA "Link en bio" | Si ≥5% save rate en 24h → boost Meta $30 |
| 7 | YYYY-MM-DD Vie | 09:00 | LinkedIn Joel 3 | LinkedIn personal | — | Pregunta cierre, sin link obligatorio | Si ≥30 interacciones en 45 min → boost $20 |
| 8 | YYYY-MM-DD Vie | 11:00 | LinkedIn Empresa 2 | LinkedIn empresa | Blog (#2) | Link al blog en primer comentario | — |

## Violaciones detectadas
[Lista de piezas que violan reglas, o "Ninguna"]

## Notas de amplificación
[Recomendaciones de boost basadas en dependencias o patrones del tema]
```

---

## Lógica de fechas — cálculo dinámico (NO hardcode)

La skill recibe `run_date` y calcula las 3 fechas ancla:

```python
from datetime import datetime, timedelta

def anchor_week(run_date: str) -> dict:
    """Calcula Martes/Miércoles/Jueves/Viernes de la semana apropiada.
    Regla: si run_date es Lun-Mar → esta semana. Si Mié-Dom → próxima semana.
    El blog siempre cae en miércoles.
    """
    d = datetime.strptime(run_date, "%Y-%m-%d")
    dow = d.weekday()  # 0=Lun, 1=Mar, 2=Mié...
    # Si corremos lunes/martes antes de publicar, esta semana
    if dow <= 1:
        monday = d - timedelta(days=dow)
    else:
        # Miércoles o después → próxima semana (no podemos rehacer esta)
        monday = d + timedelta(days=(7 - dow))
    return {
        "tuesday":   (monday + timedelta(days=1)).strftime("%Y-%m-%d"),
        "wednesday": (monday + timedelta(days=2)).strftime("%Y-%m-%d"),
        "thursday":  (monday + timedelta(days=3)).strftime("%Y-%m-%d"),
        "friday":    (monday + timedelta(days=4)).strftime("%Y-%m-%d"),
    }
```

Esta función vive en `references/date-logic.md` con tests. Claude la ejecuta inline o vía script.

**Regla crítica:** si `run_date` es miércoles o después, la skill reporta "Semana actual muerta, calendario para próxima semana" y lo deja explícito en la salida.

---

## DAG de dependencias (el core)

Ver `references/dependency-dag.md` para el grafo completo y justificación. Resumen:

```
Node 0 (Mar 09:00) LinkedIn Joel 1 ─── teaser sin link
                                    │
Node 1 (Mié 07:00) Blog publish ────┼───► es el HUB
                                    │
                                    ├──► Node 2 (Mié 09:00) LinkedIn Empresa 1
                                    ├──► Node 3 (Mié 11:00) YouTube
                                    ├──► Node 4 (Jue 09:00) LinkedIn Joel 2
                                    └──► Node 7 (Vie 11:00) LinkedIn Empresa 2

Node 5 (Jue 11:00) IG Carousel ────── no estricta (link en bio)
Node 6 (Vie 09:00) LinkedIn Joel 3 ── cierre, sin link obligatorio
```

**Aristas (dependencias):** una pieza solo puede publicar si todas sus dependencias están `published=true`. Si el blog falla en publicar miércoles 7am, **toda la cadena se bloquea** hasta resolverse. La skill debe detectar el bloqueo y proponer degradación (ver edge cases).

---

## Link policy — reglas por canal

Aplicar al generar el output, no negociable:

| Canal | Dónde va el link | Qué link |
|---|---|---|
| Blog | N/A (es el destino) | — |
| LinkedIn Joel | **Primer comentario**, nunca caption | Blog del miércoles si existe |
| LinkedIn Empresa | **Primer comentario** | Blog del miércoles |
| IG Carousel | Bio (dice "Link en bio") | `/blog` índice o blog específico |
| YouTube | Descripción línea 1-2 | Blog + `/diagnostico-express` |

**Por qué primer comentario en LinkedIn:** links en caption reducen alcance ~60% (algoritmo suprime tráfico externo). Confirmado en deta-content y transcripts Matt Gray + Pierre Herubel.

---

## Horarios B2B LATAM — ventanas óptimas

Horas en CST (Chihuahua). Fuente: heurística Matt Gray + Pierre Herubel adaptada a LATAM PyME:

| Ventana | Horas | Uso |
|---|---|---|
| Mañana alta | 08:30-09:30 | Posts principales (Joel 1-3, Empresa 1-2) |
| Mid-morning | 11:00-12:00 | Posts secundarios, YouTube, IG |
| ❌ Evitar | 13:00-14:30 | Hora de comida MX, engagement colapsa |
| ❌ Evitar | 16:00+ | B2B LATAM ya no está en LinkedIn |

No programar nada después de 14:30. Viernes tarde es muerte garantizada.

---

## Paid amplification — trigger rules v1

Ver `references/paid-triggers.md` para detalle. La skill **recomienda** basándose en umbrales, no ejecuta. La ejecución la hace Joel + `campanas-digitales` skill.

**Triggers activos v1:**

| Trigger | Señal | Acción recomendada |
|---|---|---|
| LinkedIn Velocity (Joel) | ≥30 interacciones en primeros 45 min | Boost $20 retargeting 72h |
| LinkedIn Empresa | ≥20 interacciones en primeros 60 min | Boost $15 audiencia ICP |
| IG Save Rate | ≥5% saves/alcance en 24h | Meta Ads Engagement $30 |
| Google Ads (post blog) | Blog recibe ≥50 sesiones orgánicas en 7 días | Extraer H2 del blog, añadir como Phrase Match a Search |

**Importante:** v1 deja esto como **recomendación en texto**, Joel valida manual. v2 (2026-04-29) integrará LinkedIn Analytics API + GA4 + YouTube Data para medición automática. Ver sección "Retrospectiva v2" abajo.

---

## Edge cases

Ver `references/edge-cases.md` para detalle. Resumen de los 5 más comunes:

### 1. Feriado MX cae en miércoles
Blog sigue publicando (auto-deploy), pero LinkedIn Empresa 1 + YouTube se corren al jueves. Viernes comprimido se vuelve jueves. Sábado queda libre.

### 2. Pieza Martes con CTA "lee el blog" (bug original 2026-04-15)
LinkedIn Joel 1 con link al blog que aún no existe. Skill detecta y **alerta**: "Pieza viola DAG temporal. Recomendación: reescribir como teaser ('mañana publico esto'), sin link. Link va en el Joel 2 del jueves."

### 3. YouTube no está editado el miércoles
Remover node 3 del calendario. Publicar YouTube cuando esté listo, mover al siguiente miércoles como "bono" de la semana nueva. Blog del miércoles sigue. LinkedIn Empresa 1 mantiene CTA al blog (no al video).

### 4. Corrida late-week (jue/vie/sáb/dom)
Semana actual muerta. Calendario genera fechas próxima semana. Reportar explícito.

### 5. Blog no está listo cuando se corre la skill
Reportar "Blog es dependencia crítica — producir antes de calendarizar". No generar calendario parcial.

---

## Violaciones — cómo detectarlas

La skill debe leer los archivos de cada pieza (path en input) y chequear:

1. **LinkedIn sin link en body pero sí en comentario implícito:** caption contiene `http://` o `https://` → violación. Output: "Pieza #X tiene URL en caption, mover a primer comentario."
2. **Pieza con `[CASO:]` placeholder:** violación "no publicable", Joel debe llenar.
3. **Fecha en nombre del archivo no coincide con calendario calculado:** alerta "archivo dice YYYYMMDD pero calendario dice YYYYMMDD'". El archivo se queda, solo se reporta.
4. **CTA apunta a URL que no existe al momento de publicar** (blog no publicado aún): violación.

---

## Retrospectiva v2 — stub

**Estado v1:** Esta skill entrega calendario prospectivo. NO mide resultados.

**v2 (planeado 2026-04-29):**
- Integrar LinkedIn Analytics API (verificar costo — posible $$ en API v2)
- Pull GA4 por post (blog traffic by URL)
- Pull YouTube Data API (views, retention) — ya tenemos API key en `~/research/.env`
- Output adicional: "Retrospectiva Semana [N-1]" con qué pegó, qué no, ajustes al calendario siguiente
- Trigger real de paid (no solo recomendación)

Pendiente confirmar con Joel: costo LinkedIn Analytics API. Si es alto, considerar scraping de LinkedIn sales navigator o export manual semanal.

---

## Cuándo NO usar esta skill

- **Corrida de pipeline completa:** usa `deta-pipeline`, que internamente invoca a esta skill en Paso 7-8.
- **Edición de copy:** usa `deta-content`.
- **Configurar campañas paid:** usa `campanas-digitales`. Esta skill solo recomienda triggers.
- **Research de tema:** usa `deta-research`.

---

## Skills adyacentes

| Skill | Relación |
|---|---|
| `deta-pipeline` | **Upstream** — produce las 8 piezas y llama a esta skill para calendarizarlas. |
| `deta-content` | **Peer** — define reglas de copy por canal. Esta skill asume que el copy ya cumple. |
| `campanas-digitales` | **Downstream** — recibe triggers de paid amplification para ejecución. |
| `market-research` | **Peer** — GEO + CORE-EEAT del blog como hub. Esta skill asume el blog ya cumple. |
| `keyword-research` | **Peer** — intent por canal. Esta skill asume el copy ya mapeó keywords. |

---

## Archivos relacionados

- `references/dag-and-dates.md` — DAG completo + función `anchor_week()` + edge cases con manejo paso a paso
- `references/paid-triggers.md` — umbrales detallados, fuentes, caveats
- `references/research-brief.md` — brief original de NLM + decisiones de Claude

## Documentación de origen

Esta skill fue construida con `skill-creator-deta` el 2026-04-15.
- Notebook research: eliminado post-creación (efímero). Brief conservado en `references/research-brief.md`.
- Fuentes originales: 12 (6 SERP + 2 YouTube + 4 internas DETA)
- Gap novedoso: DAG de dependencias no está codificado en ningún framework público — valor agregado de esta skill.
