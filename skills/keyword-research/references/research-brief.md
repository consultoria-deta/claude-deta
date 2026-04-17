# Research Brief — keyword-research (upgrade)

**Notebook:** acc401ed-9a43-4e7f-b2f4-390407146468 (efímero, borrar al finalizar)
**Fuentes indexadas:** 10
- pytrends-pypi.txt (PyPI docs + README completo)
- ahrefs-keyword-research.txt
- backlinko-keyword-research.txt
- ga4-data-api-quickstart.txt
- gkp-api-overview.txt
- search-console-api.txt
- YT: Keyword Research for SEO in 2026 — Metics Media
- YT: Google Keyword Planner Tutorial 2026 — Surfside PPC
- YT: How to see Organic Traffic in GA4 — Analytics Mania 2025
- YT: B2B Blueprint Keyword Research Tactics — Directive 2024

---

## 1. Conocimiento nuclear (NLM, validado)

1. **GKP da rangos, no volúmenes exactos, en cuentas sin gasto activo** — cuenta nueva de Ads muestra rangos amplios. DETA acaba de activar la cuenta (2026-04-15), así que GKP puede estar en modo rangos por semanas. Confiar en CPC como proxy de intención mientras tanto.
2. **GA4 filtro orgánico exacto:** `session default channel group` EXACTLY MATCHES `Organic Search`. No usar `default channel group` genérico — rompe atribución.
3. **PyTrends rate limit:** ~1,400 requests secuenciales antes de bloqueo. `sleep=60` entre llamadas. Los datos son índices relativos 0-100, NO volúmenes absolutos.
4. **CPC alto = intención comercial B2B** — en servicios profesionales, keyword con volumen bajo pero CPC alto ($8-15 USD) indica demanda pagable real. Es la métrica más confiable disponible en el stack gratuito.
5. **"Start with a website" en GKP** — inyectar URL de competidor para extraer keywords que no aparecen sembrando directo. Útil para reclutamiento y consultoría (dominio competitivo, pocas búsquedas directas del servicio).
6. **Volumen de búsqueda ≠ tráfico** — una página top rankea para ~1,000 variaciones. El volumen de la keyword seed es solo la punta.
7. **Search Console API requiere OAuth 2.0** — no soporta API key genérica para datos de propiedad. En DETA la ruta práctica en v1 es GA4→GSC via linking, no API directa.

---

## 2. Anti-patrones (NLM + Claude)

| Anti-patrón | Por qué falla | Corrección |
|---|---|---|
| Descartar keywords B2B con bajo volumen | El long-tail B2B convierte 3-5x más que head terms genéricos | Priorizar CPC + intent, no solo volumen |
| Consultar PyTrends en bloques grandes sin sleep | Bloqueo de IP, error 429 | sleep=60 entre llamadas, usar timeframe='today 12-m' |
| Confiar en un solo tool para volumen | PyTrends = relativo, GKP = rangos, GA4 = site-only | Triangular las 3 fuentes |
| Calcular Keyword Difficulty sin Ahrefs/Semrush | GKP/PyTrends/GA4 no tienen backlink data | Usar CPC como proxy de competencia pagada |
| Inventar volúmenes cuando no hay datos | Degrada la confianza del output | Marcar explícitamente "volumen no disponible" |

---

## 3. Edge cases

1. **Cuenta Ads nueva sin gasto (DETA actual):** GKP muestra rangos en lugar de números. Solución: reportar el rango + el CPC estimado, priorizar por CPC hasta que la cuenta tenga historial.
2. **Bloqueo PyTrends SSL/rate limit:** Interceptar error, avisar al usuario, esperar 5 min antes de reintentar. No bloquear todo el research por PyTrends solo.
3. **Keywords médicas o altamente reguladas:** GKP suprime resultados. Solución: usar "Start with website" con URL de competidor en lugar de semilla directa.
4. **Sitio sin tráfico orgánico en GA4** (DETA actual — sitio joven): GA4 no devuelve datos históricos de keyword útiles. Documentarlo y priorizar GKP + PyTrends hasta que acumule 3+ meses de tráfico.

---

## 4. Estructura propuesta (Claude override)

```
SKILL.md — flujo principal: cuándo usar cada herramienta, metodología, formato de entrega
references/
  research-brief.md       — este archivo
  gkp-guide.md           — setup GKP API + autenticación + ejemplos
  ga4-organic-queries.md — filtro exacto + script GA4 Data API
  b2b-intent-guide.md    — clasificación intent para PyMEs mexicanas
scripts/
  pytrends_wrapper.py    — con sleep, geo=MX, retries
  gkp_keywords.py        — query GKP por seed o por URL competidor
  ga4_organic.py         — pull organic queries desde GA4
```

---

## 5. Scripts reutilizables

### pytrends_wrapper.py (base)
```python
from pytrends.request import TrendReq
import time

def get_trends(keywords: list, geo='MX', timeframe='today 12-m', sleep=60):
    pt = TrendReq(hl='es-MX', tz=360, retries=2, backoff_factor=0.5)
    pt.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
    time.sleep(sleep)
    return {
        'interest_over_time': pt.interest_over_time(),
        'interest_by_region': pt.interest_by_region(),
        'related_queries': pt.related_queries()
    }
```

### GA4 organic filter (JSON asset)
```json
{
  "dimensionFilter": {
    "filter": {
      "fieldName": "sessionDefaultChannelGroup",
      "stringFilter": { "matchType": "EXACT", "value": "Organic Search" }
    }
  }
}
```

---

## 6. Triggers naturales

1. "keywords", "palabras clave", "keyword research"
2. "qué busca la gente cuando quiere [servicio]"
3. "volumen de búsqueda de [término]"
4. "Google Trends / PyTrends / tendencias"
5. "Keyword Planner / GKP / planificador de palabras"
6. "qué keywords usamos para Google Ads"
7. "long tail", "intent", "intención de búsqueda"
8. "qué buscan en Google nuestros clientes"
9. "comparar keywords", "¿cuál keyword tiene más búsquedas?"
10. "palabras clave de la competencia"

---

## 7. Skills adyacentes

| Skill | Relación |
|---|---|
| `deta-research` | Recibe keyword seeds → genera SERP analysis + PAA + brief editorial |
| `campanas-digitales` | Recibe keywords de alta intención → estructura ad groups + negative list |
| `seo-audit` | Audita qué keywords ya rankea el sitio — input para identificar gaps |
| `deta-content` | Recibe clusters → genera contenido optimizado por intent |

---

## 8. Riesgos de sobre-ingeniería

- **No calcular KD propio** — sin Ahrefs/Semrush no hay datos de backlinks. CPC es el proxy correcto.
- **No automatizar OAuth de Search Console** — requiere consentimiento manual; la skill debe pedir el token al usuario, no intentar resolverlo.
- **No incluir cache manager** — demasiado infraestructura; documentar el límite mensual de GKP y que el usuario lo gestione.
- **No expandir a mercados fuera de MX** — DETA opera en México. Agregar multi-geo requeriría otro análisis.

---

## Decisiones de Claude (override del brief NLM)

- **ACEPTÉ:** Rate limits documentados, GA4 filtro exacto, CPC como proxy B2B, edge case cuenta nueva, KD sin backlinks
- **RECHACÉ:** `gkp_cache_manager.py` — infraestructura innecesaria para una skill; proxy SSL rotation — fuera del stack DETA; `geo_mappings.json` — hardcodear MX es suficiente
- **MATIZZO:** OAuth GSC → en v1, la ruta práctica es GA4→GSC link, no API directa. Documentar como "futuro v2".
- **AUMENTÉ:** Contexto DETA específico (3 servicios con seed keywords, Chihuahua+MX, dueños PyME 10-100 emp), estado actual de la cuenta (activa pero nueva → GKP en rangos), integración explícita con `deta-research` + `campanas-digitales`, nota sobre GA4 sin historial (sitio joven)
