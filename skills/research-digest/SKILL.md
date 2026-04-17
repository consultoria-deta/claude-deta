---
name: research-digest
description: Investigación profunda multi-fuente y síntesis ejecutiva sobre cualquier tema, mercado, empresa, industria o competidor. Actívate con cualquier mención de: investiga, research, analiza, dame un digest, inteligencia de mercado, due diligence, análisis de industria, análisis de empresa, quiénes son, qué hace [empresa], cómo está el mercado de [X], dame un panorama, benchmark, comparativa, tendencias del sector, informe, reporte de mercado. También actívate cuando el usuario necesite preparar una propuesta, pitch o entrar a un cliente nuevo.
---

# Research Digest — Investigación Profunda y Síntesis Ejecutiva

Investiga y consolida información sobre cualquier tema, mercado, empresa o industria. Produce reportes accionables listos para tomar decisiones.

---

## Cuándo usar este flujo vs otros

- **¿Necesitas keywords y volúmenes?** → Usar skill `keyword-research`
- **¿Auditoría técnica de SEO de un sitio?** → Usar skill `market-research` → sección Screaming Frog
- **¿Investigación general de mercado/empresa/industria?** → Esta skill

---

## Flujo de Investigación — 6 Pasos

### Paso 1 — Definir el Alcance
Antes de buscar, responder:
1. ¿Qué exactamente necesito saber?
2. ¿Para qué se va a usar esta información? (propuesta, pitch, estrategia)
3. ¿Cuál es el nivel de profundidad requerido?
4. ¿Hay un cliente/empresa/mercado específico?

### Paso 2 — Investigación de Contexto (Broad)
```
web_search: "[tema] México 2024 2025"
web_search: "[industria] tendencias México"
web_search: "[empresa] qué hace"
web_search: "[mercado] tamaño México"
```

### Paso 3 — Deep Dive en Fuentes Clave
```
firecrawl scrape [sitio relevante del paso 2]   # preferido — maneja JS, Wikipedia, anti-bot básico; fallback: web_fetch
web_search: "[empresa] clientes casos de éxito"
web_search: "[empresa] noticias recientes"
web_search: "[competidores] [sector] México líderes"
```

### Paso 4 — Inteligencia Competitiva
```
web_search: "competidores [servicio] México"
web_search: "[competidor 1] vs [competidor 2]"
web_search: "[competidor] precios servicios"
web_search: "[industria] benchmarks México pyme"
```

### Paso 5 — Datos y Métricas
```
web_search: "[sector] estadísticas México INEGI"
web_search: "[sector] mercado tamaño millones México"
web_search: "[tema] encuesta reporte [año]"
```

### Paso 6 — Síntesis y Entrega
Consolidar hallazgos en el formato de entrega estándar (abajo).

---

## Fuentes por Tipo de Investigación

### Para empresas mexicanas
- LinkedIn de la empresa
- Sitio web oficial
- Google Maps / reseñas
- Redes sociales (Instagram, Facebook)
- Noticias: El Economista, Expansión, Forbes México

### Para industrias / mercados
- INEGI (datos estadísticos MX)
- CONCANACO, CANACINTRA (cámaras empresariales)
- Deloitte/McKinsey/KPMG reportes públicos
- Statista (free tier)
- América Economía

### Para tecnología / startups
- Crunchbase
- TechCrunch México / Contxto
- Product Hunt
- GitHub (para herramientas open source)

### Para tendencias globales con impacto MX
- HBR, McKinsey Insights
- Gartner (reportes públicos)
- Google Trends

---

## Formato de Entrega — Research Digest

```markdown
# Research Digest: [TEMA]
**Fecha:** [fecha] | **Elaborado para:** DETA Consultores | **Profundidad:** [Alta/Media/Rápida]

---

## Resumen Ejecutivo
[3-5 bullets con los hallazgos más importantes. Leer esto debe ser suficiente para tomar la decisión de negocio clave.]

## Contexto del Mercado / Empresa
[Quiénes son, qué hacen, tamaño del mercado, contexto relevante. Datos con fuente.]

## Hallazgos Principales
### [Hallazgo 1]
[Desarrollo con datos y fuente]

### [Hallazgo 2]
...

## Análisis de Competencia
| Competidor | Fortalezas | Debilidades | Oportunidad para DETA |
|---|---|---|---|

## Tendencias Relevantes
[Qué está cambiando en el mercado que afecta la decisión]

## Keywords con Intent Comercial
[Solo si es relevante para la investigación — keywords que el mercado usa]

## Oportunidades Identificadas
[Dónde hay espacio para DETA o el cliente]

## Riesgos y Consideraciones
[Qué puede salir mal, qué hay que validar]

## Recomendaciones
[3-5 acciones concretas priorizadas, no teoría]

## Próximos Pasos para Joel
[Acciones inmediatas y quién hace qué]

## Fuentes
- [URL 1] — [qué dato viene de aquí]
- [URL 2] — ...
```

---

## Niveles de Profundidad

### Rápido (15-20 min de research)
- 5-8 búsquedas web
- Resumen de 1 página
- Trigger: "dame un panorama rápido de X"

### Medio (30-45 min)
- 10-15 búsquedas + 3-5 fetches de páginas
- Reporte completo con todas las secciones
- Trigger: "investiga X para nuestra propuesta"

### Profundo (60+ min)
- 20+ búsquedas, múltiples fuentes primarias
- Reporte ejecutivo + apéndice de datos
- Trigger: "necesito due diligence completo de X"

---

## Reglas de Calidad

1. **Solo hechos verificados** — diferenciar claramente entre "dato confirmado" y "estimado"
2. **Citar fuentes con URL** — cada dato importante tiene su fuente
3. **Priorizar fuentes primarias** — sitio oficial > noticia > blog
4. **No inventar datos** — "información no encontrada" es válido
5. **Ser accionable** — el reporte sirve para tomar decisiones, no solo para leer
6. **Adaptar al contexto DETA** — siempre conectar hallazgos con oportunidades de consultoría
7. **Máximo 2 páginas de resumen ejecutivo** — profundidad va en secciones posteriores
