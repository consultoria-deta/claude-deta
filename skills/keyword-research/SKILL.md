---
name: keyword-research
description: Investigación de keywords con stack completo: Google Keyword Planner (volúmenes reales) + PyTrends (tendencias) + GA4 (queries orgánicas del sitio) + SERP analysis. Actívate con cualquier mención de: keywords, palabras clave, keyword research, volumen de búsqueda, qué busca la gente, términos de búsqueda, tendencias de búsqueda, Google Trends, PyTrends, Keyword Planner, GKP, planificador de palabras, long tail, head terms, intención de búsqueda, intent, comparar keywords, keywords de la competencia, qué keywords usamos en Ads, qué buscan nuestros clientes en Google. También actívate cuando el usuario quiera saber qué palabras usa su mercado para buscar un servicio o cuando necesite keywords para Google Ads o contenido.
---

# Keyword Research — Stack completo DETA

Investigación de palabras clave con datos reales. Tres capas complementarias: GKP para volúmenes, PyTrends para tendencias, GA4 para lo que ya funciona en el sitio.

---

## Stack de herramientas — cuándo usar cada una

| Herramienta | Qué da | Disponibilidad | Cuándo usarla |
|---|---|---|---|
| **Google Keyword Planner (GKP)** | Volúmenes mensuales reales, CPC, competencia | Gratis — cuenta Ads activa 150-883-1637 | Siempre — es la fuente de volumen principal |
| **PyTrends** | Tendencia relativa 0-100, interés por región, related queries | Gratis — script local | Para comparar tendencias, estacionalidad, validar crecimiento |
| **GA4 Data API** | Queries orgánicas reales del sitio, páginas de entrada | Propiedad G-EVQHHSLZ7C | Cuando el sitio ya tiene tráfico (>3 meses) — identificar gaps y winners |
| **web_search + SERP manual** | Tipo de contenido que rankea, PAA, snippets | Gratis | Para análisis de competencia y oportunidad de ranking |
| **Answer Socrates** | Preguntas reales del mercado MX | Gratis — answersocrates.com | Para pillar pages y FAQs |

**Regla DETA actual (sitio joven, cuenta Ads nueva):**
- GKP puede mostrar rangos en lugar de volúmenes exactos hasta que la cuenta acumule historial de gasto
- GA4 sin datos orgánicos suficientes todavía — usar GKP + PyTrends como base
- **CPC es el mejor proxy de intención comercial** cuando el volumen es un rango

---

## Metodología

### Paso 1 — Seeds

Partir de 3-5 términos que describen el servicio. Para DETA, los seeds base son:

```
Reclutamiento:    "reclutamiento de personal chihuahua", "agencia selección personal"
Consultoría:      "consultoría empresarial chihuahua", "consultor pyme mexico"
Capacitación:     "capacitación empresarial chihuahua", "cursos para empresas"
Diagnóstico:      "diagnóstico empresarial", "diagnóstico organizacional pyme"
```

### Paso 2 — GKP: volúmenes y CPC

```bash
# Abrir Google Keyword Planner en ads.google.com
# → Herramientas → Planificador de palabras clave → Descubrir keywords nuevas
# Input: lista de seeds o URL de competidor ("Start with a website")
# Filtros: Idioma = Español, País = México
# Columnas clave: Promedio de búsquedas mensuales, Competencia, CPC (puja parte superior)
```

**Interpretar CPC:**
- CPC > $8 USD = intención comercial alta → prioridad para Ads y landing pages
- CPC $3-8 = intención media → contenido orientado a conversión
- CPC < $3 = informacional → blog, tráfico de awareness

**Cuenta nueva sin historial:** GKP mostrará rangos (1K-10K en lugar de 4,400). Usar el CPC como criterio de priorización hasta tener datos exactos.

### Paso 3 — PyTrends: tendencia y región

```bash
# Comparar tendencias en el mercado MX
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "consultoría empresarial" "reclutamiento de personal" --geo MX

# Comparar múltiples variantes
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "capacitación empresarial" "cursos para empresas" "taller liderazgo" --geo MX
```

**Lo que da PyTrends:**
- Índice 0-100 por semana (12 meses) — NO es número absoluto de búsquedas
- Interés por estado — validar si Chihuahua tiene suficiente volumen local
- Related queries — fuente de long tails no obvios

**Límites técnicos:**
- Rate limit: esperar 30-60s entre llamadas (error 429 si no)
- Si falla related_queries: no es bloqueante, continuar con lo que hay

### Paso 4 — GA4: queries orgánicas reales (cuando aplique)

Solo ejecutar si el sitio tiene >3 meses de tráfico orgánico.

Filtro exacto para SEO orgánico:
```python
# Dimensión requerida: sessionDefaultChannelGroup
# Valor exacto: "Organic Search" (no usar dimensión genérica)
# Ver references/ga4-organic-queries.md para el script completo
```

En GA4 UI: Informes → Adquisición → Adquisición de tráfico → filtrar por "Búsqueda orgánica"

### Paso 5 — Clasificación por intent

| Intent | Señales en la keyword | Tipo de página |
|---|---|---|
| Transaccional (BoFu) | contratar, cotizar, agendar, precio, chihuahua + servicio | Landing con CTA fuerte |
| Comercial (MoFu) | mejores, comparar, vs, recomendaciones, cómo elegir | Landing comparativa |
| Informacional (ToFu) | qué es, cómo, por qué, guía, para pymes | Blog, artículo |
| Navegacional | nombre + empresa/marca | Home, About |

**Regla B2B:** En consultoría y reclutamiento, el volumen bajo NO descarta la keyword. Una keyword con 200 búsquedas/mes y CPC de $12 es más valiosa que una con 5,000 búsquedas y CPC de $0.50.

### Paso 6 — Clusters de contenido

```
PILLAR PAGE (2,000-3,000 palabras)
"Consultoría Empresarial en Chihuahua: Guía para Dueños de PyME"
  ↓
CLUSTER PAGES (800-1,500 palabras)
├── "Diagnóstico Organizacional: Cómo Identificar tu Cuello de Botella"
├── "Reclutamiento Estratégico para PyMEs: Cómo Contratar sin Adivinar"
├── "Capacitación de Equipos: Cuándo y Cómo Hacerlo"
└── "Flujo de Caja para PyME: Guía Práctica"
```

### Paso 7 — Priorización

```
PRIORIDAD 1 → CPC alto + intención transaccional + keyword específica (geo o servicio)
PRIORIDAD 2 → Volumen medio + CPC medio + intención comercial
PRIORIDAD 3 → Volumen bajo + CPC alto + long tail (rápida conversión)
SKIP        → Volumen alto + CPC bajo + informacional genérico (blog solo si tiempo)
```

---

## "Start with a website" — truco competencia

Cuando las seeds directas dan poco, inyectar URL de competidor en GKP:

1. GKP → "Descubrir keywords" → "Empezar con un sitio web"
2. Pegar URL de competidor (ej: consultora líder en Chihuahua)
3. GKP extrae las keywords que rankea ese sitio — muchas no aparecen en seeds directas
4. Filtrar por CPC > $3 y relevancia para DETA

---

## Análisis de SERP

Para cada keyword prioritaria:

```
web_search: "[keyword] México"
```

Evaluar:
- ¿Qué tipo de contenido rankea? Blog posts, landing pages, directorios
- ¿Cuántas palabras tienen los top 3? → profundidad requerida
- ¿Hay Featured Snippet? → optimizar respuesta directa en H2
- ¿Hay People Also Ask? → usar esas preguntas como H2/H3 del blog
- ¿Hay Maps Pack? → señal de intención local → Google Business Profile

---

## Formato de entrega

```markdown
## Keyword Research: [TEMA/SERVICIO]
**Herramientas usadas:** GKP + PyTrends + [GA4 si aplica]
**Mercado:** México (Chihuahua foco) | **Fecha:** [fecha]

### Keywords Principales (BoFu + MoFu)
| Keyword | Intent | Vol. Mensual | CPC Est. | Tendencia | Prioridad |
|---|---|---|---|---|---|
| reclutamiento de personal chihuahua | Transaccional | 480 | $9.20 | → Estable | ★★★★★ |

### Keywords Long Tail (alta conversión)
| Keyword | Intent | Vol. | CPC | Notas |
|---|---|---|---|---|

### Preguntas del Mercado (People Also Ask)
- [Pregunta real extraída del SERP]

### Clusters Recomendados
[Pillar + cluster con prioridad]

### Recomendaciones de Acción
1. Para Ads: [keyword + match type + landing]
2. Para contenido: [pillar page sugerida]
3. Para Search Console: [keyword a monitorear]
```

---

## Reglas de integridad

- **Nunca inventar volúmenes** — si GKP da rango, reportar el rango. Si PyTrends no da número absoluto, decirlo.
- **No calcular Keyword Difficulty** — sin Ahrefs/Semrush no hay datos de backlinks. Usar CPC como proxy de competencia pagada.
- **Máximo 20 keywords priorizadas** — calidad sobre cantidad
- **Siempre incluir intent** — determina tipo de página y CTA
- **Adaptar al mercado mexicano** — español mexicano, contexto local, estacionalidad MX

---

## Skills que coordina

| Siguiente paso | Skill |
|---|---|
| SERP deep dive + People Also Ask + brief editorial | `deta-research` |
| Estructura de ad groups + negative keywords para Ads | `campanas-digitales` |
| Auditar qué keywords ya rankea el sitio | `seo-audit` |
| Generar contenido optimizado por intent | `deta-content` |

---

## Referencias técnicas

- `references/research-brief.md` — brief NLM + decisiones de diseño
- `references/ga4-organic-queries.md` — script GA4 Data API con filtro correcto
- Script PyTrends: `~/google-workspace-operations/src/keywords/keywordResearch.py`
