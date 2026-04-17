---
name: market-research
description: SEO técnico y calidad de contenido para detaconsultores.com. Actívate cuando el usuario mencione: auditoría SEO, Screaming Frog, errores 4xx, links rotos, titles duplicados, CORE-EEAT, GEO optimization, AI Overviews, on-page checklist, schema.org, canonical, robots.txt, indexación técnica, o cuando quiera verificar la salud técnica del sitio antes de publicar o después de cambios importantes. NO activar para investigación de mercado general, keywords o briefs de contenido — esos van a deta-research o keyword-research.
---

# Market Research — SEO Técnico y Calidad de Contenido

Auditoría técnica del sitio, framework de calidad de contenido y optimización para motores de IA.

---

## Cuándo usar esta skill vs otras

- **¿Investigar empresa, mercado o industria?** → `deta-research`
- **¿Keywords, volúmenes, intent, clusters?** → `keyword-research`
- **¿Salud técnica del sitio, errores, calidad de contenido?** → Esta skill

---

## Screaming Frog — Auditoría Técnica

```bash
# Audit completo headless
/Applications/Screaming\ Frog\ SEO\ Spider.app/Contents/MacOS/ScreamingFrogSEOSpider \
  --crawl https://detaconsultores.com \
  --headless \
  --output-folder /tmp/deta-seo-$(date +%Y%m%d)
```

**Qué revisar en los CSVs:**
- 4xx errors — links rotos
- 3xx chains — redirecciones largas
- Titles duplicados o vacíos
- Meta descriptions duplicadas o >160 chars
- H1 duplicados o faltantes
- Imágenes sin alt text
- Páginas noindex accidentales

---

## SEO On-Page — Checklist

Para cada página antes de publicar:

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

## Framework CORE-EEAT — Calidad de Contenido

Evaluar antes de publicar cualquier pieza de contenido:

**CORE (Relevancia):**
- [ ] **C**onsistency — ¿coherente con la marca y el expertise de DETA?
- [ ] **O**riginality — ¿aporta perspectiva original o es solo reempaque?
- [ ] **R**elevance — ¿responde exactamente lo que busca el usuario?
- [ ] **E**xpertise — ¿demuestra conocimiento real del tema?

**E-E-A-T (Autoridad):**
- [ ] **E**xperience — ¿cita experiencia real con clientes?
- [ ] **E**xpertise — ¿el autor tiene credenciales verificables?
- [ ] **A**uthoritativeness — ¿otras fuentes lo referencian?
- [ ] **T**rustworthiness — ¿tiene datos verificables, no solo opiniones?

**Score mínimo para publicar: 6/8 criterios cumplidos.**

---

## GEO — Generative Engine Optimization

Para que DETA sea citada en ChatGPT, Perplexity y Google AI Overviews:

**Señales de citabilidad:**
- Contenido estructurado con encabezados claros
- Respuestas directas a preguntas específicas (formato PAA)
- Datos y estadísticas con fuente citada
- Definiciones claras de términos del sector
- Bloques de ~150 palabras para ser extraídos fácilmente

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

## Análisis de Competencia SEO

Usar solo para evaluar competidores en términos de posicionamiento orgánico, no para inteligencia de mercado general (eso va en `deta-research`):

1. **Presencia orgánica:** ¿aparece en keywords objetivo? ¿cuántas páginas indexadas?
2. **Tipo de contenido:** blog, casos de éxito, guías — frecuencia y profundidad
3. **Huecos:** qué intent no cubren, dónde hay oportunidad de ranking
4. **Tecnología:** BuiltWith.com para ver su stack
