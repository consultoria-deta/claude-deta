---
name: deta-pipeline
description: Orquestación completa del pipeline de contenido semanal de DETA. Actívate cuando Joel diga "pipeline", "contenido", "contenido de la semana", "contenido semanal", "qué publicamos", "siguiente blog", "arranca el pipeline", o cualquier variante que implique iniciar el ciclo de producción de contenido. Esta skill reemplaza la necesidad de dar instrucciones paso a paso — corre el flujo completo automáticamente, solo pausando para que Joel elija el tema.
---

# DETA Pipeline — Orquestación de Contenido Semanal

Pipeline end-to-end que produce 1 blog + 4 piezas de distribución + hero image por semana. Corre automáticamente, solo pausa para la decisión del tema.

---

## Flujo completo — 9 pasos

Al activarse, ejecutar estos pasos en orden sin pedir confirmación entre ellos (excepto el Paso 4).

### Paso 1 — Identificar semana y verificar digest

```python
# Determinar semana ISO actual
from datetime import datetime
week = datetime.now().strftime("%Y-W%V")
```

1. Verificar si existe `~/research/output/{week}/digest_*.json`
2. Si **existe** → leerlo y continuar al Paso 2
3. Si **no existe** → correr `python3 ~/research/scrape.py` y esperar a que termine
4. Si el scraping falla → informar el error y detenerse

### Paso 2 — Revisar Google Alerts (opcional, enriquece el digest)

Usar Gmail MCP para extraer links frescos de Google Alerts:

```
gmail_search_messages: "from:googlealerts-noreply@google.com newer_than:7d"
```

1. Leer los últimos 5-7 correos de alertas
2. Extraer los links principales de cada alerta
3. Filtrar: solo links que toquen los 5 pilares DETA
4. Guardar como contexto adicional para el scoring (no es bloqueante — si Gmail MCP no está disponible o no hay alertas, continuar sin ellas)

### Paso 3 — Scoring del digest (NotebookLM)

NotebookLM tiene el contexto completo de DETA (8 posts, tono, pilares). Usarlo para scorear — su scoring será más coherente con la marca que hacer el scoring desde cero.

1. Activar notebook base:
   ```bash
   notebooklm use 94ea12c2-6722-49e0-b62d-4a966137ad80
   ```

2. Indexar el digest de la semana como fuente:
   ```bash
   notebooklm source add ~/research/output/{week}/digest_{date}.md
   ```

3. Pedir scoring al notebook:
   ```bash
   notebooklm ask "Analiza este digest de noticias y videos. Para cada tema relevante, agrupa en 'ideas madre' y scorea con estas 5 dimensiones (1-5):
     - CTA/Conversión (30%): ¿ruta clara a servicio DETA?
     - Pilar DETA (25%): ¿se alinea a uno de los 5 pilares?
     - Oportunidad (20%): ¿es trending, oportuno?
     - Reciclabilidad (12.5%): ¿genera piezas para múltiples canales?
     - Diferenciación (12.5%): ¿DETA puede aportar perspectiva única vs lo que ya publicó?
   
   Solo ideas con score ponderado >= 3.5. Máximo 5. Para cada una incluye:
   rank, idea madre, score, pilar DETA, CTA sugerido, título tentativo de blog, ángulos para LinkedIn/IG/YouTube." \
   --save-as-note --note-title "Shortlist: {date}"
   ```

4. Leer la respuesta y formatear como tabla para Joel.

**Si NotebookLM no está disponible:** Claude hace el scoring inline con los mismos criterios (fallback).

### Paso 4 — Joel elige tema ⏸️

**ÚNICA PAUSA DEL PIPELINE.** Presentar la shortlist y esperar a que Joel diga cuál quiere. Aceptar:
- Un número ("el 2", "vamos con el 3")
- Un nombre ("el de delegación")
- Una combinación ("combina el 1 y el 4")
- "el primero" / "el de mayor score" → tomar el #1

Si Joel no está conforme con ninguno, ofrecer: "¿Quiero buscar en otra dirección?" y volver al Paso 2 con búsqueda manual.

### Paso 5 — Brief editorial + NotebookLM

Con el tema elegido, generar el brief en dos fases: investigación SERP y enriquecimiento con NotebookLM.

**Fase A — Investigación SERP:**
1. **SERP analysis** — buscar la keyword principal, analizar qué rankea, identificar gaps
2. **PAA (People Also Ask)** — extraer preguntas reales del mercado para H2/H3
3. **Keywords** — principal + 4-5 secundarias naturales para SEO México

**Fase B — NotebookLM (enriquecimiento):**

El notebook permanente de DETA (`94ea12c2-6722-49e0-b62d-4a966137ad80`) contiene los posts publicados del blog. Usarlo para que el brief sea coherente con lo que DETA ya dijo y para inyectar fuentes externas.

1. Activar el notebook base:
   ```bash
   notebooklm use 94ea12c2-6722-49e0-b62d-4a966137ad80
   ```

2. Indexar fuentes relevantes del digest y/o SERP (artículos que aporten datos, estadísticas, perspectivas):
   ```bash
   notebooklm source add "[URL_ARTICULO_1]"
   notebooklm source add "[URL_ARTICULO_2]"
   # También funciona con archivos locales:
   notebooklm source add ~/research/output/{week}/digest_{date}.md
   ```

3. Pedir al notebook un brief editorial contextualizado:
   ```bash
   notebooklm ask "Para un artículo sobre '[TEMA]' dirigido a dueños de PyMEs mexicanas:
     (1) propón 1 ángulo diferenciador respecto a lo que DETA ya publicó sobre temas similares,
     (2) estructura con H2 y H3 basada en estas PAA: [lista PAA del SERP],
     (3) 5 keywords naturales para SEO México,
     (4) 2 ganchos de apertura alternativos,
     (5) 3 datos o estadísticas clave de las fuentes indexadas,
     (6) qué posts existentes del blog de DETA deberían linkarse internamente" \
     --save-as-note --note-title "Brief: [TEMA]"
   ```

4. Usar la respuesta del notebook como input principal del brief. Claude complementa con lo del SERP que el notebook no cubrió.

**Si NotebookLM no está disponible** (auth expirado, error de red): generar el brief solo con SERP + PAA. No es bloqueante, pero pierde la coherencia con posts previos.

**Output:** `~/research/output/{week}/Brief_[Tema]_YYYYMMDD.md`

### Paso 6 — Escribir blog (NotebookLM draft → Claude refina)

Con el brief listo, el blog se escribe en dos pasadas:

**Pasada 1 — Draft de NotebookLM:**

Pedir al notebook (que ya tiene las fuentes indexadas) un primer borrador:
```bash
notebooklm ask "Escribe un artículo de blog de 1,000-1,200 palabras basado en este brief:
  [pegar brief completo o resumen ejecutivo]
  
  Reglas:
  - Tono: directo, segunda persona singular, sin jerga corporativa
  - Estructura: seguir los H2/H3 del brief
  - Incluir datos de las fuentes con atribución
  - Incluir links internos a estos posts existentes: [lista de slugs relevantes]
  - CTA final hacia [servicio DETA del brief]
  - NO usar: sinergia, potenciar, alineación estratégica, integral, innovador" \
  --save-as-note --note-title "Draft: [TEMA]"
```

El draft del notebook tiene la ventaja de estar grounded en las fuentes reales y en el tono de los posts anteriores.

**Pasada 2 — Claude refina:**

Tomar el draft del notebook y aplicar:
- **Filtro anti-AI obligatorio** (de deta-content): perplexity, burstiness, palabras prohibidas, variación de estructura
- **Links internos** verificados — confirmar que los slugs existen en `content/blog/`
- **Expresiones coloquiales mexicanas** donde encajen naturalmente
- **Placeholders** `[CASO:]` donde se necesite una anécdota real de Joel
- **Largo final:** 1,000-1,400 palabras

**Si NotebookLM no está disponible:** Claude escribe el blog completo desde el brief, sin draft previo. Funciona pero pierde la capa de grounding en fuentes.

**Output:** `~/research/output/{week}/Blog_[Tema]_YYYYMMDD.md`

### Paso 7 — Distribución multicanal

**⚠️ IMPORTANTE:** El calendario de fechas/horas/dependencias NO se resuelve aquí. Este paso solo **genera el copy** de las 7 piezas. El calendario autoritativo lo entrega `deta-distribucion` en el Paso 8.5.

Generar **7 piezas de distribución** a partir del blog — la semana completa de contenido. Seguir las reglas de canal de `deta-content`:

**LinkedIn Joel — 3 posts (Mar / Jue / Vie):**

| # | Día | Archivo | Ángulo |
|---|-----|---------|--------|
| 1 | Martes | `LinkedIn-Joel-1_[Tema]_YYYYMMDD.md` | Historia personal / experiencia con cliente — incluye link al blog en primer comentario |
| 2 | Jueves | `LinkedIn-Joel-2_[Tema]_YYYYMMDD.md` | Lección aprendida / contraste antes/después — ángulo distinto al martes |
| 3 | Viernes | `LinkedIn-Joel-3_[Tema]_YYYYMMDD.md` | Pregunta provocadora / reflexión corta — formato más ligero para cerrar semana |

Reglas Joel: gancho en línea 1, segunda persona, tono directo. Cada post debe funcionar independiente — alguien que solo vea uno debe entender el valor.

**LinkedIn Empresa — 2 posts (Mié / Vie):**

| # | Día | Archivo | Ángulo |
|---|-----|---------|--------|
| 1 | Miércoles | `LinkedIn-Empresa-1_[Tema]_YYYYMMDD.md` | Dato + insight del blog — más formal, CTA a servicio DETA |
| 2 | Viernes | `LinkedIn-Empresa-2_[Tema]_YYYYMMDD.md` | Metodología / proceso / framework — posiciona a DETA como experto |

Reglas Empresa: tono institucional pero no corporativo, siempre con CTA a servicio.

**Otras piezas:**

| Pieza | Archivo | Reglas clave |
|---|---|---|
| **IG Carousel** | `IG-Carousel_[Tema]_YYYYMMDD.md` | 7-10 slides, texto por slide, gancho en slide 1, CTA en última |
| **YouTube Guión** | `YouTube-Guion_[Tema]_YYYYMMDD.md` | 5-8 min explainer, timestamps, hook primeros 10 seg |

**Regla de links:** El link al blog NUNCA va en el body de ningún post de LinkedIn. Va en el primer comentario. Mencionarlo explícitamente en cada archivo.

**Variación obligatoria:** Los 5 posts de LinkedIn deben usar ángulos y formatos diferentes entre sí. No repetir el mismo gancho, la misma estructura ni el mismo CTA. Extraer distintas facetas del tema del blog.

Todos los archivos van a `~/research/output/{week}/`

**Nombrar archivos sin fecha hardcoded:** usar `LinkedIn-Joel-1_[Tema]_[slug].md` (no incluir YYYYMMDD). La fecha la asigna `deta-distribucion` en Paso 8.5.

### Paso 8 — Hero image + mover blog al repo

1. **Generar hero image:**
   ```bash
   python3 ~/research/hero_gen.py --pilar [pilar] --slug [slug]
   ```
   Esto crea `~/research/output/{week}/hero-[slug].png`

2. **Copiar hero a repo:**
   ```bash
   cp ~/research/output/{week}/hero-[slug].png ~/deta-web/public/blog/
   ```

3. **Crear markdown del blog en el repo** — `~/deta-web/content/blog/[slug].md` con frontmatter completo:
   ```yaml
   ---
   title: ""
   seoTitle: ""         # max 60 chars, keyword al inicio
   description: ""      # max 160 chars
   category: ""         # Estrategia | Organización | Comercial | Finanzas
   date: "YYYY-MM-DD"   # fecha de creación
   publishDate: "YYYY-MM-DD"  # fecha de publicación (ver calendario abajo)
   readTime: "X min"
   heroImage: "/blog/hero-[slug].png"
   heroAlt: ""
   pilar: ""            # estrategia | organizacion | comercial | finanzas | talento
   ogDescription: ""
   ctaHeadline: ""
   ctaText: ""
   ctaPrimary: "/diagnostico-express"
   ctaPrimaryLabel: "Diagnóstico Express Gratis"
   ctaSecondary: "/metodologia"
   ctaSecondaryLabel: "Conoce la Metodología"
   featured: false      # true solo si reemplaza al featured actual
   ---
   ```

4. **publishDate:** NO asignar aquí. Lo calcula `deta-distribucion` en Paso 8.5 basado en `run_date` (función `anchor_week()`).

### Paso 8.5 — Calendario autoritativo (`deta-distribucion`)

Invocar skill `deta-distribucion` con:

```yaml
topic: "[Tema]"
slug: "[slug]"
pilar: "[pilar]"
run_date: "YYYY-MM-DD"  # fecha actual
pieces:
  blog:              { ready: true, path: "~/deta-web/content/blog/[slug].md" }
  linkedin_joel_1:   { ready: true, path: "~/research/output/{week}/LinkedIn-Joel-1_[slug].md" }
  linkedin_joel_2:   { ready: true, path: "..." }
  linkedin_joel_3:   { ready: true, path: "..." }
  linkedin_empresa_1: { ready: true, path: "..." }
  linkedin_empresa_2: { ready: true, path: "..." }
  ig_carousel:       { ready: true, path: "..." }
  youtube:           { ready: false, path: "..." }  # false si Joel aún no graba
```

La skill devuelve:
1. Tabla calendario (fechas, horas CST, dependencias, link policy por pieza)
2. Violaciones detectadas (piezas que rompen el DAG — ej: Joel 1 con link al blog que no existe aún)
3. Triggers de paid amplification recomendados

**Acciones post-deta-distribucion:**
- Si hay violaciones: invocar `deta-content` para reescribir esas piezas, luego re-correr deta-distribucion
- Si calendario OK: **actualizar `publishDate` del blog** al miércoles que calculó deta-distribucion
- **Renombrar archivos de distribución** añadiendo fechas reales al nombre (ej: `LinkedIn-Joel-1_[slug]_20260422.md`)

### Paso 9 — Push a main + actualizar memoria

1. **Git:**
   ```bash
   cd ~/deta-web
   git add content/blog/[slug].md public/blog/hero-[slug].png
   git commit -m "feat(blog): add [título corto]"
   unset GITHUB_TOKEN && git push
   ```

2. **Actualizar calendario en memoria:**
   - `~/.claude/memory/DETA/Contenido/calendario-semana-setup.md` — actualizar con las piezas generadas, estados, archivos
   - `~/.claude/projects/-Users-joelestrada/memory/project_flujo-contenido.md` — actualizar estado
   - Copiar a bóveda Obsidian: `~/.claude/memory/Projects/flujo-contenido.md`

3. **Limpiar NotebookLM — mantener solo posts publicados:**
   ```bash
   # Listar fuentes actuales
   notebooklm source list
   # Eliminar fuentes temporales (digests, artículos SERP de esta semana)
   notebooklm source delete-by-title "digest_2026-04-13"
   notebooklm source delete-by-title "[título artículo SERP]"
   # Agregar el blog recién publicado como fuente permanente
   notebooklm source add ~/deta-web/content/blog/[slug].md
   ```
   **El notebook siempre debe tener solo los posts publicados del blog.** Nada de digests viejos, artículos SERP, ni fuentes temporales. Esto garantiza que el scoring de la semana siguiente no se contamine con noticias pasadas.

4. **Crear eventos en Google Calendar** para las piezas de distribución:

   Usar `gcal_create_event` con calendarId `consultoria@detaconsultores.com`, timezone `America/Chihuahua`. **Usar las fechas/horas exactas que entregó `deta-distribucion` en Paso 8.5** — no hardcodear. El calendario calculado ya resolvió dependencias y puede haber desplazado piezas por feriados o edge cases.

   Color por canal:
   - LinkedIn (Joel + Empresa): 7 (Peacock)
   - YouTube (grabación): 6 (Tangerine)
   - IG Carousel: 4 (Flamingo)

   Duración default: 30 min por post, 1.5h para grabación YouTube.

   Cada evento incluye en la descripción:
   - Ruta al archivo con el copy (`~/research/output/{week}/[archivo].md`)
   - Instrucciones clave (llenar [CASO:], link en comentario, etc.)
   - Reminder: popup 30 min antes

5. **Reportar a Joel:**
   - Blog publicado con publishDate [fecha]
   - Hero image en el repo
   - 7 piezas de distribución en `~/research/output/{week}/` (3 LinkedIn Joel + 2 LinkedIn Empresa + IG + YouTube)
   - 7 eventos creados en Google Calendar
   - Piezas con `[CASO:]` que Joel necesita llenar

---

## Calendario de publicación semanal

Una vez elegido el tema, asignar fechas a cada pieza:

| Canal | Día | Notas |
|---|---|---|
| LinkedIn Joel 1 | Martes | Historia personal, link al blog en primer comentario |
| Blog | Miércoles | publishDate, auto-deploy 7am CST |
| LinkedIn Empresa 1 | Miércoles | Dato + insight, mismo día que el blog |
| YouTube | Miércoles | Joel graba con guión |
| LinkedIn Joel 2 | Jueves | Lección / contraste, ángulo distinto al martes |
| IG Carousel | Jueves | Diseñar slides con deta-brand |
| LinkedIn Joel 3 | Viernes | Pregunta / reflexión corta, cierre de semana |
| LinkedIn Empresa 2 | Viernes | Metodología / framework, posiciona expertise |
| Reel 30s (opcional) | Sábado | Si Joel lo pide |

---

## Manejo de errores

| Situación | Qué hacer |
|---|---|
| No hay digest y scrape.py falla | Informar error, sugerir correr manualmente |
| Gmail MCP no disponible | Continuar sin alertas, no es bloqueante |
| NotebookLM auth expirado | Correr `notebooklm login` y reintentar. Si Joel no puede hacer login ahora, continuar sin notebook |
| NotebookLM no disponible | Generar brief sin notebook, solo con SERP + PAA. Blog sin draft previo — Claude escribe directo |
| hero_gen.py falla | Informar error, continuar sin hero (Joel puede generarla después) |
| Git push falla | Informar error, dejar los archivos listos localmente |
| Score < 3.5 en todos los temas | Informar a Joel, ofrecer buscar manualmente o esperar al siguiente digest |

---

## Lo que esta skill NO hace

- **No publica en redes sociales** — Joel publica LinkedIn, IG, YouTube manualmente
- **No reemplaza la revisión de Joel** — los `[CASO:]` requieren anécdotas reales
- **No diseña slides de IG** — genera el copy, el diseño es tarea de `deta-brand`
- **No edita video** — genera el guión, Joel graba y edita en DaVinci Resolve

---

## Modo rápido

Si Joel dice "pipeline rápido" o "solo el blog", ejecutar solo Pasos 1-6 + 8-9 (sin distribución multicanal).

Si Joel dice "solo distribución" o "distribución de [slug]", leer el blog existente y ejecutar solo Paso 7.
