# NLM Research Phase — Prompts detallados

Prompts específicos para la Fase 2 del skill-creator-deta. Cópialos y adapta el `[BRACKET]` al contexto de la skill.

---

## Prompt 1 — Superskill Brief (principal)

Ejecutar después de indexar todas las fuentes en el notebook efímero:

```
notebooklm ask "Actúa como arquitecto de prompts / skills para Claude. Tengo indexadas [N] fuentes sobre '[DOMINIO DE LA SKILL]'. Quiero construir una skill llamada '[NOMBRE]' que [OBJETIVO EN UNA LÍNEA].

Analiza las fuentes y devuélveme un 'superskill brief' con ESTA estructura exacta:

## 1. Conocimiento nuclear
Los 5-10 puntos que la skill DEBE saber de este dominio. No opiniones — hechos operativos que, si se ignoran, la skill falla. Cita la fuente de cada punto.

## 2. Anti-patrones
Errores comunes que las fuentes documentan o que se infieren. Cada uno con: qué hace la gente mal + por qué falla + qué hacer en su lugar.

## 3. Edge cases
Situaciones donde una implementación genérica rompe. Mínimo 3. Para cada una: descripción, síntoma, manejo recomendado.

## 4. Estructura propuesta
Cómo organizar SKILL.md vs references/ vs scripts/. Qué va en cada nivel del progressive disclosure. Si el dominio es complejo, sugiere subdivisiones por variante (ej: por proveedor, por framework, por tipo de input).

## 5. Scripts o assets reutilizables
Código, plantillas o datos que aparecen repetidos en las fuentes y que la skill debería bundlear en lugar de reinventar cada vez. Si no detectas nada, dilo explícitamente.

## 6. Triggers naturales
Frases reales que un usuario diría cuando necesita esta skill. Mezcla formales y coloquiales. Mínimo 8.

## 7. Skills adyacentes
Qué otras skills debería conocer o delegarles trabajo. Si no sabes qué skills existen, describe las capacidades externas necesarias en lugar de nombrar skills concretas.

## 8. Riesgos de sobre-ingeniería
Qué cosas NO deben entrar a la skill aunque parezcan útiles. Dominios donde la skill podría extralimitarse.

Sé concreto. No uses frases genéricas de consultor. Si una fuente se contradice con otra, dilo y explica cuál es más confiable y por qué." \
--save-as-note --note-title "Superskill Brief — [NOMBRE]"
```

---

## Prompt 2 — Refinamiento (opcional, si el brief 1 sale flojo)

Si el primer brief es vago o no aterriza, pedir un segundo pase específico:

```
notebooklm ask "El brief anterior tiene debilidades en [SECCIÓN]. Reescribe solo esa sección con:
- Ejemplos concretos de las fuentes (citas textuales cortas)
- Números, plazos, umbrales específicos donde aplique
- Nombres propios (herramientas, frameworks, personas citadas)
Evita generalidades. Si la evidencia en las fuentes es débil, dilo explícitamente en lugar de inventar." \
--save-as-note --note-title "Superskill Brief — [NOMBRE] — Refinamiento [SECCIÓN]"
```

---

## Prompt 3 — Crítica adversarial (opcional, para skills de alta criticidad)

Para skills donde el costo de errores es alto (reclutamiento, cliente, financiera), pedir un pase adversarial después del brief:

```
notebooklm ask "Ahora actúa como revisor crítico. Tomaste el brief anterior y lo pasas a un ingeniero que va a implementar la skill. Identifica:

1. Afirmaciones del brief que NO están respaldadas por las fuentes indexadas
2. Puntos donde las fuentes se contradicen y el brief escondió la contradicción
3. Supuestos implícitos del brief que pueden ser falsos en contexto DETA (PyMEs mexicanas, operación DETA Consultores)
4. Qué información clave falta en las fuentes y deberíamos conseguir antes de construir la skill

Sé duro. Tu trabajo es evitar que construyamos una skill frágil." \
--save-as-note --note-title "Superskill Brief — [NOMBRE] — Adversarial"
```

---

## Qué hacer con las respuestas

1. Leer las 3 (o 1, si no usaste refinamiento/adversarial)
2. Fusionar manualmente en un solo `research-brief.md` — no dejar 3 archivos separados
3. Al final del brief, agregar sección **"Decisiones de Claude"**:
   ```markdown
   ## Decisiones de Claude (override del brief NLM)
   
   - ACEPTÉ: [punto X] — razón
   - RECHACÉ: [punto Y] — razón (ej: no aplica al stack DETA, contradice convención Z)
   - AUMENTÉ: [punto Z] — razón (ej: NLM no consideró integración con skill W)
   ```
4. Guardar como `[skill-nueva]/references/research-brief.md`

---

## Troubleshooting

| Síntoma | Causa probable | Fix |
|---|---|---|
| NLM devuelve generalidades | Pocas fuentes o fuentes muy homogéneas | Agregar 2-3 fuentes de ángulos distintos (ej: crítica del dominio, caso de fracaso) |
| NLM contradice hechos conocidos | Fuentes viejas o de baja calidad | Filtrar fuentes, priorizar docs oficiales y repos con mantenimiento reciente |
| Brief demasiado largo (>3000 palabras) | Prompt muy abierto | Re-pedir con límite de palabras por sección |
| NLM inventa citas de fuentes | Auth expirado o fuentes mal indexadas | `notebooklm source list` y verificar que están presentes |
