# Paid Amplification — Trigger Rules v1

Reglas para recomendar boost de contenido orgánico a pagado. **v1 = recomendación textual. Joel valida y ejecuta manualmente via `campanas-digitales`.** v2 (2026-04-29) automatizará medición.

---

## Tabla maestra de triggers

| # | Plataforma | Métrica | Umbral | Ventana | Acción recomendada | Presupuesto |
|---|---|---|---|---|---|---|
| 1 | LinkedIn Joel | Interacciones (reacciones + comentarios + shares) | ≥30 | Primeros 45 min | Boost Retargeting LinkedIn Ads | $20 USD / 72h |
| 2 | LinkedIn Empresa | Interacciones | ≥20 | Primeros 60 min | Boost Audiencia ICP (Sponsored Content) | $15 USD / 72h |
| 3 | IG Carousel | Save Rate (saves / alcance) | ≥5% | 24 h post-publicación | Meta Ads Campaign "Engagement" | $30 USD / 7 días |
| 4 | YouTube | Avg View Duration | ≥55% del video | 48 h | Subir como ad asset a PMax (si hay creative) | Variable |
| 5 | Blog (Google Ads) | Sesiones orgánicas en URL | ≥50 | 7 días post-publicación | Extraer H2 como Phrase Match, agregar a campaña Search | +$10/día a campaña existente |

---

## Fuentes y justificación por trigger

### Trigger #1 — LinkedIn Joel velocity
**Fuente:** Matt Gray transcript (video 0H4uouOn7lI), "you need 30+ engagements in the first 45 minutes or the algorithm caps your reach". Confirmado por Pierre Herubel (video 2HSavr17yq0).

**Por qué 30 y no 50:** Matt Gray habla de US market, audiencias de 100k+ seguidores. Joel tiene <5k. Ajuste conservador: 30 es el mínimo que señala "el algoritmo está amplificando", lo suficiente para valer un boost de $20.

**Caveat:** si Joel sube a 20k+ seguidores, re-calibrar a 50.

### Trigger #2 — LinkedIn Empresa
**Fuente:** heurístico derivado. Empresa pages tienen menor alcance orgánico vs personal (2-3x menor), por eso umbral más bajo (20 vs 30).

**Por qué boost a "Audiencia ICP" y no retargeting:** Empresa pages rara vez viralizan — el objetivo es llegar a dueños de PyME que aún no nos conocen, no re-servir a visitantes previos.

### Trigger #3 — IG Carousel save rate
**Fuente:** deta-content (línea 335), varias fuentes indexadas en NLM. Save rate es la "métrica rey" en IG B2B — indica contenido de referencia repetible.

**5% es alto:** promedio IG es 1-2%. 5% señala que el carrusel es "manual de referencia" que la gente guarda para volver.

**Por qué Meta Ads Engagement y no Traffic:** el contenido ya funcionó orgánico; el boost es para **amplificar la señal de autoridad**, no para bajarlo a landing page.

### Trigger #4 — YouTube Avg View Duration
**Fuente:** documentación YouTube Algorithm 2024-2025. 55% retention es el umbral donde el algoritmo empieza a recomendar a audiencias nuevas.

**Por qué condicional a "creative":** PMax requiere 15+ imágenes + 5 videos para funcionar. Si DETA solo tiene 1 video y 5 imágenes, PMax va a generar auto-creatives malos. Skip hasta tener assets.

### Trigger #5 — Blog → Google Ads feedback loop
**Fuente original NLM:** confundía esto con "LCP <2.5s" (condición continua del sitio). Claude redefinió basándose en dynámica real de signal de demanda.

**Por qué 50 sesiones en 7 días:** umbral operativo. Menos de eso es ruido estadístico. Arriba de eso, los H2 del blog son keywords que el mercado busca y está pagando con clicks orgánicos — vale la pena cazarlos también en Search.

**Workflow:** extraer H2s del blog → pasarlos por Keyword Planner → los que tienen volumen razonable agregarlos a campaña Search existente (Diagnóstico Express o Reclutamiento según pilar del blog).

---

## Reglas de composición

Si múltiples triggers se disparan la misma semana:

1. **Priorizar por costo-impacto:** Blog → Google Ads (Trigger 5) tiene mejor ROI que LinkedIn boost porque es feedback loop sostenido, no gasto one-shot.
2. **Presupuesto semanal máximo de boosts orgánicos:** $80 USD. Si los triggers suman más, priorizar #3 (IG) > #1 (LinkedIn Joel) > #2 (LinkedIn Empresa) > #4 (YouTube).
3. **No boostar el mismo post dos veces** — si LinkedIn Joel 1 ya recibió boost martes, no volverlo a boostar jueves.
4. **Excluir si el post tiene CASO:[] no llenado** — boostar contenido con placeholders es quemar dinero.

---

## Caveats conocidos

1. **Todos los umbrales son heurísticos.** DETA no tiene data histórica aún. Primera calibración real: después de 8 semanas publicando consistente (mid-mayo 2026).
2. **LinkedIn API cambia sin aviso.** El umbral de velocity puede perder relevancia si LinkedIn cambia el algoritmo. Re-leer transcripts de Matt Gray / Pierre Herubel cada 6 meses.
3. **Meta Ads iOS 14 tracking:** save rate medido en IG es confiable (in-platform). No confiar en métricas de conversión downstream por ahora.
4. **Los $20/$15/$30 son USD 2026.** Inflación publicitaria alta — re-revisar en 12 meses.

---

## Integración con `campanas-digitales`

Esta skill **recomienda**, `campanas-digitales` **ejecuta**. Handoff:

1. `deta-distribucion` genera tabla de triggers al final del calendario semanal
2. Joel revisa y decide cuáles ejecutar
3. Joel invoca `campanas-digitales`: "ejecuta el boost del trigger #1" — campanas-digitales conoce el setup GTM/Ads y arma la campaña

No automatizar el handoff en v1. v2 puede considerar.

---

## v2 — Medición automática (planeado 2026-04-29)

Para que los triggers se disparen solos necesitamos leer métricas:

| Fuente | Estado | Implementación |
|---|---|---|
| LinkedIn Analytics | ⏳ Verificar costo API v2 | Posible scraping si API es caro |
| GA4 (blog sesiones) | ✅ Ya configurado | Pull via `google-analytics-data` Python client |
| YouTube Data API | ✅ API key ya existe (`~/research/.env`) | Pull via `googleapiclient` |
| Meta Ads Insights (IG saves) | ⏳ Requiere Business asset manager | Instagram Graph API, FB Business Suite |

v2 correrá un script scheduled (launchd) cada 2 horas durante las primeras 48h post-publicación de cada pieza, disparando alertas cuando un trigger se cumple.
