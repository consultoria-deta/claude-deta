---
name: deta-research
description: Investigación profunda multi-fuente y síntesis ejecutiva para DETA Consultores. Fusiona research de mercado, inteligencia competitiva, validación de nuevos servicios y brief editorial en un solo flujo. Actívate con cualquier mención de: investiga, research, analiza, dame un digest, inteligencia de mercado, due diligence, análisis de industria, análisis de empresa, quiénes son, qué hace [empresa], cómo está el mercado de [X], dame un panorama, benchmark, comparativa, tendencias del sector, informe, reporte de mercado, nuevo servicio, nueva oferta, validar idea, hay mercado para, lanzar [X], quiero ofrecer [X] — y también cuando el usuario necesite preparar una propuesta, pitch, entrar a un cliente nuevo, escribir un artículo, blog, post, brief de contenido, quiero escribir sobre [X], ángulo para el artículo, estructura del post, o preparar contenido editorial para detaconsultores.com.
---

# DETA Research — Investigación y Síntesis

Flujo único de investigación que produce el output correcto según el destino.

---

## Destinos de output

| Destino | Output | `keyword-research` | NotebookLM |
|---|---|---|---|
| `blog` | Brief editorial (ángulo, H2/H3, PAA, keywords, ganchos) | Opcional — enriquece el brief | Sí, si hay fuentes |
| `propuesta` / `pitch` / `cliente` | Research Digest ejecutivo | No | No |
| `nuevo servicio` | Validation Report (demanda + brecha + posicionamiento) | Sí — señal de demanda | No |
| `linkedin` | Ángulos e insights para posts | No | No |
| general (default) | Research Digest ejecutivo | No | No |

El destino se infiere del contexto. Si no es claro, preguntar en una sola línea antes de continuar.

---

## Cuándo usar esta skill vs otras

- **¿Pipeline semanal completo (scraping → scoring → brief → blog → distribución → push)?** → `deta-pipeline` (que llama a esta skill internamente para el brief)
- **¿Keywords, volúmenes, clusters?** → `keyword-research` (o llamarla desde aquí como módulo)
- **¿Auditoría técnica SEO, errores 4xx, CORE-EEAT?** → `market-research`
- **¿Redactar el artículo/post con el brief ya listo?** → `deta-content`
- **¿Solo investigación, brief, o análisis sin el pipeline completo?** → Esta skill

**Desde deta-pipeline:** Cuando esta skill se ejecuta como Paso 5 del pipeline, el tema ya fue elegido y el scoring ya se hizo. Ir directo a la investigación SERP + brief. No repetir scoring.

---

## Flujo de Investigación — 6 Pasos

Común a todos los destinos. Algunos pasos se expanden o contraen según profundidad y destino.

### Paso 1 — Definir Alcance

Antes de buscar, responder:
1. ¿Qué necesito saber exactamente?
2. ¿Destino del output? (blog / propuesta / nuevo servicio / linkedin / general)
3. ¿Nivel de profundidad? (rápido / medio / profundo)
4. ¿Hay empresa, cliente o mercado específico?

**Checkpoint:** Si el destino es ambiguo o el alcance es muy amplio, confirmar con el usuario antes de continuar. Un minuto de alineación evita entregar el digest equivocado.

**Memoria histórica:** Si existe `~/research/output/research-log.tsv`, leerlo antes de iniciar. Si el tema ya aparece con score ≥ 3.5 y `brief_generado=true`, preguntar en una sola línea: "Ya investigué [tema] el [fecha] (score [X]). ¿Re-investigamos o usamos el brief existente?"

**Multi-perspectiva (destino `blog` o `nuevo servicio`):** Antes de elegir el ángulo, cargar `references/multi-perspectiva.md` y evaluar las 4 perspectivas. Si 3+ dicen ⚠️/❌, revisar el ángulo antes de continuar con la investigación profunda.

### Paso 2 — Investigación de Contexto (Broad)

```
web_search: "[tema] México 2025 2026"
web_search: "[industria] tendencias México"
web_search: "[empresa] qué hace"
web_search: "[mercado] tamaño México"
```

**Si el destino es `nuevo servicio` o `blog`:** Correr también `keyword-research` en paralelo para capturar señales de demanda desde el inicio. Los volúmenes de búsqueda son datos de mercado, no solo SEO.

### Paso 3 — Deep Dive en Fuentes Clave

```
web_fetch: [sitios relevantes del paso 2]
web_search: "[empresa] clientes casos de éxito"
web_search: "[empresa] noticias recientes"
web_search: "[competidores] [sector] México líderes"
```

### Paso 4 — Inteligencia Competitiva

```
web_search: "competidores [servicio] México"
web_search: "[competidor 1] vs [competidor 2]"
web_search: "[industria] benchmarks México pyme"
```

Para destino `blog`: analizar también qué ya rankea en el SERP para la keyword objetivo — tipo de contenido, profundidad, estructura, gaps.

### Paso 5 — Datos y Métricas

```
web_search: "[sector] estadísticas México INEGI"
web_search: "[sector] mercado tamaño millones México"
web_search: "[tema] encuesta reporte [año]"
```

Para destino `blog`: buscar también People Also Ask (PAA) — las preguntas reales del mercado se convierten en H2/H3 del artículo.

### Paso 6 — Síntesis y Entrega

**Filtro de relevancia DETA:** Todo tema seleccionado debe conectar con al menos 1 servicio de DETA (diagnóstico express, estructura organizacional, proceso comercial, finanzas/BSC). Si el tema es interesante pero no tiene CTA natural hacia un servicio de DETA, descartarlo o replantearlo hasta que lo tenga. Contenido sin ruta de conversión no entra al pipeline.

**Importante:** El CTA no tiene que ser a un servicio existente. Si un tema tiene potencial de conversión alto hacia estrategia, diagnóstico, estructura, comercial o finanzas — aunque DETA no tenga ese servicio formalizado hoy — priorizarlo. Joel sabe implementar metodologías nuevas.

### Scoring de contenido (aplicar al revisar digest de scraping)

Al analizar el digest del pipeline de scraping, scorear cada tema candidato con estas 5 dimensiones:

| Dimensión | Qué mide | Peso |
|---|---|---|
| **CTA / Conversión** | ¿Tiene ruta clara a servicio DETA (existente o potencial)? | 30% |
| **Pilar DETA** | ¿Se alinea a uno de los 5 pilares de contenido? | 25% |
| **Oportunidad** | ¿Es trending, oportuno, tiene gancho noticioso? | 20% |
| **Reciclabilidad** | ¿La idea madre genera piezas para múltiples canales? | 12.5% |
| **Diferenciación** | ¿DETA puede aportar perspectiva única? | 12.5% |

Score 1-5 por dimensión, ponderado = max 5.0. Solo presentar a Joel los que pasen de **3.5** con propuesta de pieza + CTA ya definidos.

**Output del scoring:** tabla rankeada con score, dimensiones, propuesta de pieza por canal, y CTA sugerido. Joel elige de la shortlist.

**Registro TSV:** Al finalizar cualquier investigación, hacer append a `~/research/output/research-log.tsv` (crear si no existe):
```
fecha	tema	score_total	destino	brief_path	publicado
2026-04-15	[tema]	[score]	[blog|propuesta|nuevo servicio|general]	[ruta o ""]	false
```
Si el archivo no tiene header todavía, añadir la línea de encabezado primero.

Consolidar hallazgos en el formato del destino (ver abajo). El output debe ser accionable: quien lo lea debe poder tomar una decisión o dar el siguiente paso sin necesidad de más investigación.

---

## Fuentes por Tipo de Investigación

### Estructura de archivos — por semana
Todo output del pipeline se organiza por semana ISO en `~/research/output/`:

```
output/
├── 2026-W16/
│   ├── digest_2026-04-13.md
│   ├── digest_2026-04-13.json
│   ├── Brief_Crecer-vs-Consolidar_20260413.md
│   ├── Blog_Crecer-vs-Consolidar_20260413.md
│   ├── shortlist_2026-04-13.md    (si se genera)
│   └── shortlist_2026-04-13.json
├── 2026-W17/
│   └── ...
```

Convención de nombres:
- Digests: `digest_YYYY-MM-DD.{md,json}`
- Briefs: `Brief_[Tema]_YYYYMMDD.md`
- Blog final: `Blog_[Tema]_YYYYMMDD.md`
- Shortlists: `shortlist_YYYY-MM-DD.{md,json}`

Esta carpeta tiene symlink en Obsidian (`DETA > Contenido > output`) para que Joel vea todo sin copiar archivos.

### Pipeline automatizado de scraping
Antes de buscar manualmente, revisar si ya hay datos frescos del pipeline (`~/research/output/`). El scraping corre 2x/semana (Lun + Jue) y alimenta:

| Fuente | Qué captura | Acceso |
|---|---|---|
| **Google News RSS** | Noticias industria MX, PyME, consultoría | feedparser — sin credenciales |
| **YouTube Data API v3** | Videos trending en nichos PyME/business, preguntas en títulos | API key en `~/research/.env` |
| **Google Alerts** | Alertas diarias de 5 temas clave al correo | Gmail MCP → `from:googlealerts-noreply@google.com` |
| **Reddit API** | Tendencias en 15 subreddits business/PyME | ⏳ Pendiente aprobación (praw + credenciales en `.env`) |

**Flujo de alertas:** Gmail MCP → extraer links de correos de Google Alerts → links relevantes se indexan en NotebookLM como fuentes.

**NotebookLM base permanente:** `notebooklm use 94ea12c2-6722-49e0-b62d-4a966137ad80` — contiene los 8 posts publicados del blog de DETA. Este notebook es acumulativo: cada semana se le agregan fuentes nuevas (artículos del SERP, digest, etc.) y crece como base de conocimiento de la marca. NO crear notebooks nuevos por tema — usar siempre este.

### Para empresas mexicanas
- LinkedIn, sitio web oficial, Google Maps/reseñas
- El Economista, Expansión, Forbes México

### Para industrias / mercados
- INEGI · CONCANACO · CANACINTRA
- Deloitte/McKinsey/KPMG reportes públicos · Statista (free) · América Economía

### Para tecnología / startups
- Crunchbase · TechCrunch México / Contxto · Product Hunt · GitHub

### Para tendencias globales con impacto MX
- HBR · McKinsey Insights · Gartner reportes públicos · Google Trends

---

## Formatos de Entrega

---

### Destino: `blog`

**Flujo:**
1. SERP analysis — qué ya rankea, qué tipo de contenido, qué gaps existen
2. PAA — extraer preguntas reales del mercado para estructurar H2/H3
3. Panel de perspectivas — cargar `references/multi-perspectiva.md` y evaluar ángulo antes de comprometerse (si no se hizo en Paso 1)
4. Indexar fuentes relevantes en el notebook permanente de DETA
5. Pedir brief + draft al notebook
6. Refinar con loop adversarial — cargar `references/brief-refinement.md` (Crítica → Síntesis → Guard)
7. Guard mecánico — verificar 6 campos obligatorios antes de entregar (ver `references/brief-refinement.md`)

**NotebookLM — notebook permanente (NO crear uno nuevo):**
```bash
notebooklm use 94ea12c2-6722-49e0-b62d-4a966137ad80
notebooklm source add [URL_O_ARCHIVO]   # repetir por fuente relevante del SERP/digest
notebooklm ask "Para un artículo sobre '[TEMA]' dirigido a dueños de PyMEs mexicanas:
  (1) propón 1 ángulo diferenciador respecto a lo que DETA ya publicó,
  (2) estructura con H2 y H3 basada en estas PAA: [lista],
  (3) 5 keywords naturales para SEO México,
  (4) 2 ganchos de apertura alternativos,
  (5) 3 datos o estadísticas clave de las fuentes,
  (6) qué posts existentes del blog deberían linkarse internamente" \
  --save-as-note --note-title "Brief: [TEMA]"
```

El notebook permanente ya tiene los 8 posts publicados, digests anteriores, y fuentes acumuladas. Esto garantiza coherencia con lo que DETA ya dijo.

**Si NotebookLM no está disponible:** generar el brief con SERP + PAA sin notebook. Funciona pero pierde coherencia con posts previos.

**Output:** `Brief_[Tema]_[YYYYMMDD].md`

```markdown
# Brief: [TEMA]
Fecha: [YYYYMMDD]

## Ángulo editorial
[diferenciador — qué hace único este artículo vs lo que ya rankea]

## SERP — qué hay y qué falta
[tipo de contenido que domina + gaps identificados]

## Keyword principal
[keyword]

## Keywords secundarias
[4-5 keywords]

## People Also Ask — preguntas del mercado
- [pregunta 1]
- [pregunta 2]
- [pregunta 3]

## Estructura propuesta
### H2: [sección — puede venir de PAA]
- H3: [subsección]
### H2: [sección]
- H3: [subsección]

## Gancho de apertura — opción A
[2-3 oraciones]

## Gancho de apertura — opción B
[2-3 oraciones]

## Datos clave
- [dato + fuente]
- [dato + fuente]

## CTA natural
Servicio DETA: [diagnóstico-express / servicios / metodología / contacto]
Ruta de conversión: [cómo el lector pasa de este contenido a interactuar con DETA]

## Hero image
Pilar: [estrategia / organizacion / comercial / finanzas / talento]
Visual hint: [descripción corta de la metáfora visual — ej: "caos convergiendo a orden", "embudo con partículas", "dashboard con tendencia creciente"]

## Fuentes indexadas
- [lista]
```

El brief es el input para `deta-content` (o para el Paso 6 de `deta-pipeline` si viene del pipeline). Las fuentes quedan en el notebook permanente — no eliminar.

**Hero image:** El pilar determina la metáfora visual base. El slug genera una variante única. Para generar: `python3 ~/research/hero_gen.py --pilar [pilar] --slug [slug]`. La imagen se guarda automáticamente en `~/research/output/YYYY-WNN/hero-[slug].png`.

---

### Destino: `nuevo servicio`

El objetivo es validar si hay mercado antes de invertir en desarrollar la oferta. La demanda de búsqueda es la señal más objetiva disponible sin hacer entrevistas.

**Flujo:**
1. Definir la hipótesis: ¿qué problema resuelve el servicio y para quién?
2. Correr `keyword-research` — volúmenes como proxy de demanda (señal viable: interés consistente en PyTrends MX)
3. Analizar SERP — ¿quién ya ofrece esto? ¿cómo lo posicionan?
4. Identificar brecha — ¿qué no está cubierto o mal servido?
5. Proponer posicionamiento diferenciado para DETA

**Output:** `ValidationReport_[Servicio]_[YYYYMMDD].md`

```markdown
# Validation Report: [SERVICIO]
Fecha: [YYYYMMDD]

## Hipótesis
[Problema que resuelve · Segmento objetivo · Propuesta de valor inicial]

## Señales de Demanda
[Datos de PyTrends MX — keywords relacionadas, tendencia, volumen relativo]
[Conclusión: demanda alta / media / baja / no validada]

## Landscape Competitivo
| Competidor | Oferta | Posicionamiento | Precio aprox. |
|---|---|---|---|

## Brechas Identificadas
[Qué no está cubierto, qué hace mal la competencia, dónde hay espacio]

## Posicionamiento Sugerido para DETA
[Diferenciador concreto + a quién va dirigido + por qué DETA puede ganarlo]

## Riesgos
[Qué puede salir mal, qué asumir antes de lanzar]

## Recomendación
[Lanzar / Pilotar con un cliente / Investigar más / Descartar — con justificación]

## Próximos Pasos
[Acciones concretas priorizadas]

## Fuentes
- [URL] — [qué dato viene de aquí]
```

---

### Destino: `propuesta` / `pitch` / `cliente` / general

**Output:** `ResearchDigest_[Tema]_[YYYYMMDD].md`

```markdown
# Research Digest: [TEMA]
**Fecha:** [fecha] | **Elaborado para:** DETA Consultores | **Profundidad:** [Alta/Media/Rápida]

## Resumen Ejecutivo
[3-5 bullets — leer esto debe ser suficiente para la decisión clave]

## Contexto del Mercado / Empresa
[Quiénes son, qué hacen, tamaño, contexto. Datos con fuente.]

## Hallazgos Principales
### [Hallazgo 1]
[Desarrollo con datos y fuente]

## Análisis de Competencia
| Competidor | Fortalezas | Debilidades | Oportunidad para DETA |
|---|---|---|---|

## Tendencias Relevantes
[Qué está cambiando que afecta la decisión]

## Oportunidades Identificadas
[Dónde hay espacio para DETA o el cliente]

## Riesgos y Consideraciones
[Qué puede salir mal, qué validar]

## Recomendaciones
[3-5 acciones concretas priorizadas]

## Próximos Pasos para Joel
[Acciones inmediatas]

## Fuentes
- [URL] — [qué dato viene de aquí]
```

---

### Destino: `linkedin`

**Output:** inline — lista de 3-5 ángulos con:
- El insight central
- Por qué resuena con la audiencia PyME
- Formato sugerido (historia / dato / pregunta / contraste)
- CTA natural hacia servicio DETA (diagnóstico-express / servicios / metodología / contacto)

---

## Niveles de Profundidad

| Nivel | Búsquedas | Output | Trigger |
|---|---|---|---|
| Rápido | 5-8 | 1 página | "dame un panorama rápido de X" |
| Medio | 10-15 + 3-5 fetches | Reporte completo | "investiga X para nuestra propuesta" |
| Profundo | 20+ + múltiples fuentes primarias | Reporte + apéndice de datos | "due diligence completo de X" |

---

---

## References

| Archivo | Cuándo cargar |
|---|---|
| `references/multi-perspectiva.md` | Paso 1 o 3 cuando destino es `blog` o `nuevo servicio` |
| `references/brief-refinement.md` | Paso 6-7 del flujo blog — después de generar el brief |

---

## Reglas de Calidad

1. **Solo hechos verificados** — diferenciar claramente dato confirmado vs estimado
2. **Citar fuentes con URL** — cada dato importante tiene su fuente
3. **Priorizar fuentes primarias** — sitio oficial > noticia > blog
4. **No inventar datos** — "información no encontrada" es válido
5. **Ser accionable** — el output sirve para tomar decisiones, no solo para leer
6. **Conectar con DETA** — todo contenido debe tener ruta de conversión clara hacia un servicio DETA (diagnóstico-express, estructura organizacional, proceso comercial, finanzas/BSC). Sin CTA natural → no entra al pipeline
7. **Máximo 2 páginas de resumen ejecutivo** — la profundidad va en secciones posteriores
8. **Checkpoint antes de generar** — si el alcance cambió durante la investigación, confirmar destino antes de escribir el output final
