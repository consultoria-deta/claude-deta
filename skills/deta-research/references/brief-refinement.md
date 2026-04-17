# Brief Refinement — Loop Adversarial

Refina el brief generado mediante un ciclo de Crítica → Síntesis → Guard. Produce un brief verificado, no solo generado.

## Cuándo activar

Después del Paso 5 del flujo blog ("Claude refina") cuando:
- El brief viene de NotebookLM y Joel aún no lo ha revisado
- La investigación fue media o profunda (10+ búsquedas)
- El tema es estratégico (pilar DETA, CTA a servicio clave)

En investigaciones rápidas (5-8 búsquedas), saltar directo al **Guard Mecánico** es suficiente.

---

## Ciclo de Refinamiento

### Fase 1 — Crítica Interna

Leer el brief generado y atacarlo en 3 dimensiones. Esta crítica es interna — no se entrega a Joel.

**Dimensión A: Ángulo editorial**
- ¿El ángulo propuesto está ya cubierto por los primeros 3 resultados del SERP identificados en el Paso 4?
- ¿Qué hace ÚNICO este artículo vs lo que ya existe? Si no hay diferenciador claro → marcar como FATAL.
- ¿El ángulo conecta la experiencia real de una PyME con un problema nombrable?

**Dimensión B: CTA y conversión**
- ¿El CTA fluye naturalmente desde el contenido o aparece añadido al final sin conexión?
- ¿El servicio DETA mencionado resuelve exactamente el problema que plantea el artículo?
- Si el CTA es genérico ("contáctanos") → marcar como MAYOR y proponer el servicio específico.

**Dimensión C: Estructura y preguntas reales**
- ¿Los H2 propuestos responden las PAA extraídas en el Paso 5?
- ¿Hay al menos un H2 que aborde "por qué lo que ya estás haciendo no funciona"?
- ¿Los ganchos de apertura crean tensión o solo describen el tema sin hook?

Formato de crítica:
```
DEBILIDAD-1 [FATAL|MAYOR|MENOR]: [qué sección del brief] — [por qué falla]
DEBILIDAD-2 [FATAL|MAYOR|MENOR]: ...
VEREDICTO: [el punto más crítico en una línea]
```

### Fase 2 — Síntesis

Generar versión mejorada del brief que:
- Mantiene todo lo que funcionó bien
- Corrige las debilidades FATAL y MAYOR
- No añade secciones nuevas innecesarias — mejora lo que hay

Si hay ≥ 2 debilidades FATAL → regenerar las secciones afectadas por completo.
Si solo hay MENOR → ajustes puntuales, no reescritura.

---

## Guard Mecánico — siempre, sin excepción

Antes de entregar el brief a Joel, verificar los 6 campos obligatorios:

```
✅ keyword_principal     — definida, en español de México
✅ H2s                   — mínimo 3, al menos 1 viene de PAA real del SERP
✅ datos_con_fuente       — mínimo 2, con URL verificable (no "según expertos")
✅ cta_servicio_deta      — servicio específico + ruta de conversión explícita
✅ gancho_apertura        — mínimo opción A (2-3 oraciones con tensión o dato concreto)
✅ angulo_diferenciador   — 1 línea que explique qué hace único este artículo
```

Si falla algún campo → regenerar ese campo específico (1 reintento).
Si sigue fallando → entregar con `⚠️ INCOMPLETO: [campo]` visible al inicio del brief.

---

## Test de los 3 segundos

El brief listo debe poder responder estas preguntas de forma inmediata:
1. ¿Por qué alguien buscaría este artículo en Google?
2. ¿Por qué DETA es quien debe escribirlo?
3. ¿Qué hace el lector después de leerlo?

Si las 3 respuestas son obvias al leer el brief → listo para pasar a `deta-content`.
