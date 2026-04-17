# Research Brief — deta-distribucion

Brief generado por NotebookLM el 2026-04-15 a partir de 12 fuentes indexadas, con decisiones de override de Claude al final.

Notebook efímero: `44d2b72b-1c9b-4885-9b25-eac0005f4cf2` (ya eliminado).

---

## Fuentes indexadas (12)

**Externas — SERP:**
1. Weidert — Repurposing Content 2025 Guide B2B (https://www.weidert.com/blog/repurposing-content)
2. Animalz — Hubs vs Pillars (https://www.animalz.co/blog/hubs-vs-pillars)
3. CMI — B2B Content Marketing Benchmarks 2025 (https://contentmarketinginstitute.com/b2b-research/b2b-content-marketing-trends-research-2025)
4. Multibrain — Cross-posting vs Repurposing (https://multibrain.net/cross-posting-vs-repurposing-content-whats-the-difference-and-which-is-right-for-you/)
5. Fame — B2B Repurposing Strategies (https://www.fame.so/post/content-repurposing-strategies)

**Externas — YouTube transcripts:**
6. Matt Gray — "How to beat the new LinkedIn algorithm in 16 minutes" (2025-12, video 0H4uouOn7lI)
7. Pierre Herubel — "LinkedIn Content Strategy Framework 2026" (2026-02, video 2HSavr17yq0)

**Internas DETA:**
8. `deta-pipeline/SKILL.md`
9. `deta-content/SKILL.md`
10. `campanas-digitales/SKILL.md`
11. `project_flujo-contenido.md`
12. `LinkedIn-Joel_Crecer-vs-Consolidar_20260415.md` (ejemplo Semana 16)

**Fuentes descartadas:**
- Medium Content Waterfall → error al parsear URL
- HubSpot AI Workflow video → redundante con Matt Gray + Herubel
- SlideShare COPE crítica → contexto histórico, no aplicable

---

## Brief de NLM — secciones 1-10

### 1. Conocimiento nuclear
- Blog es "Hub" inamovible: auto-publica miércoles 7am CST. Toda pieza que lo referencie publica *después*.
- Algoritmo LinkedIn penaliza URLs en caption ~60%. Link obligatorio en primer comentario.
- Velocity engagement LinkedIn: primeros 45 min deciden alcance. Target ≥30 interacciones.
- Save rate es la métrica rey en IG carousel B2B.
- Asimetría plataformas: cross-posting idéntico = spam algorítmico.
- ❌ **Regla inventada por NLM:** "70% experto / 15% Joel / 15% conversión PAS". Claude la rechaza — DETA ya define mix por pipeline (3+2+1+1 por semana).

### 2. Anti-patrones
- Cross-posting ciego → atomización
- TOFU/MOFU/BOFU genérico → Authority First
- Optimizar Ads por form submits crudos → conversiones offline CRM

### 3. Edge cases (aceptados)
1. Feriado en miércoles → desplazar bloque
2. Pieza martes con CTA al blog (bug original) → teaser sin link
3. Video YouTube retrasado → remover node, mover a semana siguiente

### 4. Estructura propuesta
- `SKILL.md`: definición + DAG + output
- `references/`: link policy, horarios, triggers
- `scripts/`: vacío (capa de reglas, no ejecuta publicación)

### 5. Scripts reutilizables
- Link Policy Enforcement (función inline)
- Matriz de salida markdown estándar

### 6. Triggers naturales (aceptados 8)
Ver description de la skill.

### 7. Skills adyacentes (aceptado)
- Upstream: deta-pipeline
- Peer: deta-content
- Downstream: campanas-digitales

### 8. Sobre-ingeniería (aceptado)
- No genera copy
- No propone múltiples opciones
- No orquesta APIs

### 9. DAG de dependencias (aceptado, ajustado)
NLM propuso 8 nodos con fechas fijas. Claude ajusta:
- ❌ Fechas hardcoded (martes 2026-04-15, etc.) → ✅ fechas dinámicas vía `anchor_week(run_date)`
- ❌ YouTube a las 9am miércoles + Empresa 1 a las 11:30 → ✅ Empresa 1 primero a las 9am (mismo día que blog, CTA al blog recién publicado), YouTube a las 11am

### 10. Paid amplification triggers
- ✅ 30 interacciones/45 min LinkedIn (Matt Gray citable)
- ✅ 5% save rate IG 24h (estándar industria)
- ❌ "LCP <2.5s + dwell >2:30 min" como trigger de Ads → esto es *condición continua* del sitio, no trigger por pieza. Claude redefine: trigger Google Ads = ≥50 sesiones orgánicas al blog en 7 días → extraer H2 como Phrase Match.

---

## Decisiones de Claude (override del brief NLM)

### Acepté
- DAG de 8 nodos
- Link policy primer comentario LinkedIn
- Umbral 30 interacciones/45 min
- 5% save rate IG
- Horarios B2B LATAM 8:30-9:30 y 11:00-12:00
- Edge cases 1-3 del brief
- Anti-patrones (cross-posting, TOFU generico)
- Sobre-ingeniería (no copy, no APIs, no opciones)

### Rechacé
- **Mix 70/15/15 PAS** — NLM lo inventó, DETA ya fija el mix por pipeline (3 Joel + 2 Empresa + 1 IG + 1 YT). No repetir reglas que ya codifica otra skill.
- **Fechas hardcoded** (2026-04-15 martes, etc.) — skill debe calcular dinámicamente según `run_date`. De lo contrario el bug se repite cuando Joel corra el pipeline en viernes.
- **"LCP<2.5s como trigger Ads"** — NLM confundió condición continua con trigger por pieza. Redefiní a ≥50 sesiones orgánicas del blog en 7 días.
- **YouTube 9am + Empresa 1 11:30** (mismo miércoles) — invertí: Empresa 1 a las 9am (aprovecha ventana morning alta, CTA al blog recién salido), YouTube 11am.

### Aumenté
- **Cálculo dinámico de fechas** (`anchor_week()` en `references/date-logic.md`)
- **Manejo de corrida late-week** (edge case 4): si se corre miércoles en adelante, semana actual muerta, calendarizar próxima.
- **Stub v2 retrospectiva** con plan concreto (LinkedIn Analytics API pendiente por costo, GA4 y YouTube Data listos).
- **Detección de violaciones** en piezas existentes (URLs en caption, `[CASO:]` sin llenar, fecha archivo vs calendario).
- **Blog no listo → no calendarizar** (edge case 5): bloqueo crítico explícito, no generar calendario parcial.
- **Integración desde deta-pipeline** Paso 7-8 como invocación principal (el brief la trataba como skill independiente).

---

## Gaps no resueltos

1. **Costo LinkedIn Analytics API** — pendiente verificar antes de v2. Si es prohibitivo, fallback a export manual.
2. **Benchmarks de velocidad engagement B2B LATAM** — los 30/45 vienen de Matt Gray (US market). Ajustar con datos propios DETA después de 8 semanas publicando.
3. **Instagram Reels vs Carousel trigger** — esta skill solo cubre Carousel. Reels requiere metrics diferentes (watch rate, completion) — cuando se active IG Reels semanal, extender skill.
