---
name: keyword-research
description: Investigación de keywords, análisis de volumen de búsqueda, intención de búsqueda y clusters de contenido. Actívate con cualquier mención de: keywords, palabras clave, keyword research, Google Trends, volumen de búsqueda, PyTrends, qué busca la gente, términos de búsqueda, tendencias de búsqueda, interés por región, análisis de búsquedas, comparar keywords, semrush, ahrefs, ubersuggest, intent de búsqueda, long tail, head terms, LSI, related queries. También actívate cuando el usuario quiera saber qué palabras usa su mercado para buscar un servicio.
---

# Keyword Research — Investigación de Palabras Clave

Investigación de keywords con PyTrends, Google Trends y herramientas gratuitas. Diseñada para el mercado mexicano.

---

## Herramientas por Prioridad

| Herramienta | Qué da | Costo | Cómo acceder |
|---|---|---|---|
| **PyTrends** | Interés 0-100, geo, related queries | Gratis | Script local |
| **web_search** | Datos reales, snippets con volumen | Gratis | Tool integrado |
| **Answer Socrates** | Preguntas reales del mercado | Gratis | answersocrates.com |
| **Google Trends web** | Trends + related searches | Gratis | trends.google.com |
| **Ubersuggest** | Volumen estimado, dificultad | Gratis (limitado) | neilpatel.com/ubersuggest |
| **Google KW Planner** | Volumen real | Gratis con cuenta Ads | ads.google.com |

---

## PyTrends — Uso

```bash
# Una keyword, México
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "consultoría organizacional" --geo MX

# Comparar múltiples keywords
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "consultoría organizacional" "diagnóstico empresarial" "reestructura organizacional" \
  --geo MX

# Comparar por país
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "liderazgo empresarial" --geo MX
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "liderazgo empresarial" --geo US
```

**Lo que devuelve PyTrends:**
- Interest Over Time — índice 0-100 por semana (12 meses)
- Interest by Region — top 10 estados con más interés
- Related Queries — consultas asociadas

**Limitaciones importantes:**
- Índice relativo 0-100, NO número de búsquedas absolutas
- Rate limit: esperar 30s entre llamadas para no recibir error 429
- Related queries pueden fallar con 429 — no es bloqueante

---

## Metodología Completa

### Paso 1 — Seed Keywords
Empezar con 3-5 keywords que describen el servicio/tema:
```
"consultoría organizacional México"
"diagnóstico organizacional empresas"
"reestructura organizacional pyme"
```

### Paso 2 — Expansión
Para cada seed keyword, buscar:
- **Head terms** (genéricos, alto volumen): "consultoría organizacional"
- **Long tail** (específicos, bajo volumen, alta conversión): "consultoría organizacional para empresas de manufactura en Monterrey"
- **Preguntas** (informacional): "qué hace una consultora organizacional"
- **Comparativas** (comercial): "consultora organizacional vs coach empresarial"

### Paso 3 — Clasificación por Intent

| Intent | Señales | Tipo de página |
|---|---|---|
| Informacional | qué es, cómo, por qué, guía | Blog, artículo |
| Comercial | mejores, comparar, vs, recomendaciones | Landing, comparativa |
| Transaccional | contratar, cotizar, agendar, precio | Landing con CTA fuerte |
| Navegacional | nombre + empresa/marca | Home, About |

### Paso 4 — Clusters de Contenido

Agrupar keywords por tema. Estructura óptima:

```
PILLAR PAGE (2,000-3,000 palabras)
"Consultoría Organizacional en México: Guía Completa"
  ↓
CLUSTER PAGES (800-1,500 palabras cada una)
├── "Diagnóstico Organizacional: Qué Es y Cómo Funciona"
├── "Reestructura Organizacional: Cuándo y Cómo Hacerla"
├── "KPIs para Empresas en Crecimiento"
└── "Estrategia Comercial para Pyme"
```

### Paso 5 — Priorización

Matriz de decisión:

```
PRIORIDAD 1 → Alto volumen + Alta relevancia para DETA
PRIORIDAD 2 → Alto volumen + Media relevancia (trabajar a mediano plazo)
PRIORIDAD 3 → Bajo volumen + Alta relevancia + intent transaccional (rápida conversión)
PRIORIDAD 4 → Bajo volumen + Baja relevancia (ignorar)
```

---

## Análisis de SERP

Para cada keyword prioritaria, analizar el SERP:

```bash
# Buscar en web_search
web_search: "consultoría organizacional México"
```

Evaluar:
- **¿Qué tipo de contenido rankea?** Blog posts, landing pages, directorios, videos
- **¿Cuántas palabras tienen los top 3?** Indica profundidad esperada
- **¿Hay featured snippet?** Si sí, optimizar para respuesta directa
- **¿Hay People Also Ask?** Usar esas preguntas como H2/H3
- **¿Hay maps pack?** Si sí, optimizar Google Business Profile

---

## Formato de Entrega

```markdown
## Keyword Research: [TEMA]
**Mercado:** México | **Fecha:** [fecha]

### Keywords Principales
| Keyword | Intent | Volumen Est. | Tendencia | Dificultad | Prioridad |
|---|---|---|---|---|---|
| consultoría organizacional México | Comercial | Alto | ↑ Creciendo | Media | ★★★★★ |

### Keywords Long Tail (alta conversión)
| Keyword | Intent | Notas |
|---|---|---|

### Preguntas del Mercado (People Also Ask)
[Lista de preguntas reales que hace el mercado]

### Clusters Recomendados
[Estructura pillar + cluster pages]

### Recomendaciones de Acción
1. [Acción concreta con keyword específica]
2. ...
```

---

## Reglas de Integridad

- **Nunca inventar volúmenes** — si no se encontró dato, decir "volumen no disponible"
- **No más de 20 keywords priorizadas** — calidad sobre cantidad
- **Siempre incluir intent** — el intent determina el tipo de página y CTA
- **Adaptar al mercado mexicano** — español mexicano, contexto local, estacionalidad MX
