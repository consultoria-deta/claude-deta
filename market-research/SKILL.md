---
name: market-research
description: Investigación de mercado, auditoría SEO, inteligencia competitiva y estrategia de contenidos para DETA Consultores. Actívate con cualquier mención de: investigación de mercado, research, competencia, competidores, SEO, posicionamiento, keywords, palabras clave, Google Trends, tendencias, mercado, industria, sector, auditoría de sitio, análisis de sitio, Screaming Frog, estrategia digital, contenido, blog, artículo, cliente potencial, propuesta, diagnóstico de mercado, inteligencia competitiva, análisis de industria. También actívate cuando el usuario diga "investiga", "analiza el mercado", "qué está haciendo la competencia" o "quiero posicionar".
---

# Market Research — Investigación de Mercado y SEO

Skill de inteligencia competitiva, keyword research y estrategia de contenidos para DETA Consultores.

**Referencias:**
- Metodología completa de keyword research → `references/keyword-methodology.md`
- SEO técnico y Screaming Frog → `references/seo-technical.md`
- Análisis de competencia → `references/competitor-analysis.md`
- Estrategia de contenidos → `references/content-strategy.md`

---

## Cuándo usar cada referencia

- ¿Investigación desde cero? → Seguir el flujo de 5 fases abajo
- ¿Solo keywords? → Ir directo a `references/keyword-methodology.md`
- ¿Auditoría técnica de un sitio? → `references/seo-technical.md`
- ¿Analizar competidores? → `references/competitor-analysis.md`
- ¿Planear contenido editorial? → `references/content-strategy.md`

---

## Flujo de Investigación — 5 Fases

### Fase 1 — Warmup: entender el mercado
```
Objetivo: Contexto del mercado antes de buscar keywords
Herramientas: web_search
Queries tipo:
  "¿qué es [sector] en México?"
  "[sector] tendencias 2025 México"
  "empresas [sector] México líderes"
```

### Fase 2 — Trends: validar interés temporal
```bash
# Script local si está disponible
python3 ~/google-workspace-operations/src/keywords/keywordResearch.py \
  "keyword1" "keyword2" --geo MX

# Alternativa: Google Trends web directo
# trends.google.com → comparar keywords en México
```

### Fase 3 — Keywords: generar y clasificar
Fuentes gratuitas (en orden de confiabilidad):
1. PyTrends — tendencias e interés geo
2. web_search + Answer Socrates — preguntas reales
3. Google Autocomplete — sugerencias naturales
4. Reddit/Quora MX — intent real del usuario
5. Ubersuggest free tier — volumen estimado

### Fase 4 — Competencia: quién está ahí
```
web_search: "keyword + Mexico site:.mx"
web_search: "mejor [servicio] Mexico"
Revisar: primeras 10 posiciones
Analizar: tipo de contenido, profundidad, CTA, UX
```

### Fase 5 — Oportunidades: dónde hay huecos
```
Cruzar: keywords de alto interés + baja competencia
Identificar: ángulos sin cubrir en el mercado
Proponer: estrategia de entrada concreta
```

---

## Clasificación de Keywords por Intent

| Intent | Descripción | Ejemplo DETA |
|---|---|---|
| Informacional | Busca información | "qué es diagnóstico organizacional" |
| Comercial | Investiga antes de comprar | "mejores consultoras México" |
| Transaccional | Listo para actuar | "cotizar consultoría organizacional" |
| Navegacional | Busca marca específica | "DETA Consultores contacto" |

**Regla:** Priorizar intent comercial + transaccional para landing pages. Informacional para blog y SEO de largo plazo.

---

## Matriz de Priorización

```
                    ALTO VOLUMEN          BAJO VOLUMEN
ALTA RELEVANCIA     ★★★★★ PRIORIDAD 1    ★★★ PRIORIDAD 3
BAJA RELEVANCIA     ★★★★ PRIORIDAD 2     ★  PRIORIDAD 4
```

---

## Framework CORE-EEAT — Calidad de Contenido

Para cada pieza de contenido que se produzca o recomiende, evaluar:

**CORE (Relevancia y Calidad):**
- [ ] **C**onsistency — ¿el contenido es consistente con la marca y el expertise de DETA?
- [ ] **O**riginality — ¿aporta perspectiva original o es solo reempaque?
- [ ] **R**elevance — ¿responde exactamente lo que busca el usuario?
- [ ] **E**xpertise — ¿demuestra conocimiento real del tema?

**E-E-A-T (Señales de autoridad):**
- [ ] **E**xperience — ¿cita experiencia real con clientes?
- [ ] **E**xpertise — ¿el autor tiene credenciales verificables?
- [ ] **A**uthoritativeness — ¿otras fuentes lo referencian?
- [ ] **T**rustworthiness — ¿tiene datos verificables, no solo opiniones?

**Score mínimo para publicar: 6/8 criterios cumplidos.**

---

## GEO — Generative Engine Optimization

Los motores de IA (ChatGPT, Perplexity, Google AI Overviews) están cambiando el tráfico. Para que DETA sea citada:

**Señales de citabilidad:**
- Contenido estructurado con encabezados claros
- Respuestas directas a preguntas específicas (PAA format)
- Datos y estadísticas con fuente citada
- Definiciones claras de términos del sector
- Contenido de 134-167 palabras por bloque para ser extraído fácilmente

**robots.txt — permitir crawlers AI:**
```
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /
```

---

## SEO On-Page — Checklist

Para cada página:
- [ ] Title tag: keyword al inicio, 50-60 chars, formato `Keyword | DETA Consultores`
- [ ] Meta description: 150-160 chars, keyword + CTA
- [ ] Un solo H1 con keyword principal
- [ ] H2s con keywords LSI (3-5 por página)
- [ ] URL slug corto con keyword: `/consultoria-organizacional-mexico`
- [ ] Alt text en imágenes con descripción real
- [ ] Links internos a páginas relacionadas
- [ ] Schema.org cuando aplique (ProfessionalService, Article, FAQ)
- [ ] Canonical URL
- [ ] Sitemap actualizado

---

## Análisis de Competencia — Qué Investigar

1. **Presencia orgánica:** ¿aparece en keywords objetivo? ¿cuántas páginas indexadas?
2. **Tipo de contenido:** blog, casos de éxito, guías, videos — frecuencia y profundidad
3. **Fortalezas:** en qué son buenos, qué keywords dominan
4. **Debilidades:** dónde hay huecos, qué intent no cubren
5. **Tecnología:** BuiltWith.com para ver su stack

---

## Screaming Frog — Auditoría Técnica

```bash
# Audit completo headless
/Applications/Screaming\ Frog\ SEO\ Spider.app/Contents/MacOS/ScreamingFrogSEOSpider \
  --crawl https://detaconsultores.com \
  --headless \
  --output-folder /tmp/deta-seo-$(date +%Y%m%d)

# Qué revisar en los CSVs:
# - 4xx errors (links rotos)
# - 3xx chains (redirecciones largas)
# - Titles duplicados o vacíos
# - Meta descriptions duplicadas o >160 chars
# - H1 duplicados o faltantes
# - Imágenes sin alt text
# - Páginas noindex accidentales
```

---

## Formato de Entrega — Research Report

```markdown
# Investigación de Mercado: [TEMA]
**Fecha:** [fecha] | **Prepared for:** DETA Consultores

## Resumen Ejecutivo
[2-3 párrafos con los hallazgos más importantes y la oportunidad clave]

## Contexto del Mercado
[Tamaño, tendencias, datos reales con fuentes]

## Keywords Priorizadas
| Keyword | Intent | Volumen est. | Dificultad | Prioridad |
|---|---|---|---|---|

## Análisis de Competencia
[Tabla con competidores, fortalezas, debilidades, oportunidad]

## Score CORE-EEAT del Mercado
[Evaluación de qué tan bien cubierto está el tema — dónde hay huecos]

## Estrategia de Contenidos Recomendada
[Pillar page + clusters propuestos]

## Próximos Pasos
[3-5 acciones concretas priorizadas]

## Fuentes
[URLs de donde viene cada dato]
```

---

## Reglas de Entrega

1. **Nunca inventar datos** — si no se encontró, decir "datos no disponibles"
2. **Citar fuentes** — URL de donde viene cada dato importante
3. **Ser accionable** — recomendaciones concretas, no teoría
4. **Priorizar** — dar las 15-20 keywords más relevantes, no 200
5. **Incluir intent** — siempre decir qué intent tiene cada keyword y por qué importa
6. **Adaptar al buyer persona** — empresarios de pyme en crecimiento en México
