# Research Brief — diagrama-flujo
**Fuentes NLM:** 18 | **Prompts:** Brief [✓] / Refinamiento [—] / Adversarial [—]
**Fecha:** 2026-04-15

---

## 1. Conocimiento nuclear

1. **Motor de renderizado = HTML/CSS + Playwright**, no lenguajes de diagramación puros. Mermaid falla en layouts complejos (>30 nodos) y carece de swimlanes nativos. Draw.io requiere exportación manual. Playwright da control total y exportación headless.
2. **Estructura base = CSS Grid/Flexbox + SVG superpuesto**. Columnas = swimlanes por actor. Nodos = divs posicionados en filas secuenciales. Flechas = SVG paths calculados sobre el grid.
3. **Mapeo estricto de colores por rol.** Cada actor tiene un color fijo. El rol determina la columna y el color del nodo. No negociable.
4. **Convención semántica de formas:** rectángulos = procesos, diamantes = decisiones, flechas verdes = Sí, flechas rojas = No, bloques grises = referencias a procedimientos externos.
5. **Formato de entrada estructurado:** el texto debe llegar en formato DETA "Rol → Acción → Resultado/Destino" antes de renderizar. Si llega sin estructurar, debe pasar primero por la skill `procedimiento`.

---

## 2. Anti-patrones

| Anti-patrón | Por qué falla | En su lugar |
|---|---|---|
| Usar Mermaid/Graphviz para flujos corporativos complejos | Layout caótico >30 nodos, sin swimlanes reales | HTML/CSS + Playwright |
| Solo capturar viewport por defecto | Diagramas de 30+ nodos quedan cortados | `page.screenshot(full_page=True)` |
| Exportar a XML draw.io como pipeline principal | Requiere importación/exportación manual del usuario | PNG por defecto; XML solo si pide "editable" |

---

## 3. Edge cases

1. **Feedback loops largos** (un "No" en nodo 35 regresa al nodo 2): flecha kilométrica que cruza todo el diagrama. → Usar conectores de salto (`[ A ]`) en origen y destino.
2. **Múltiples actores en un paso** ("Vendedor + Gerencia → acción"): rompe el grid de 1 nodo = 1 columna. → Nodo en colspan o tag secundario de co-responsabilidad.
3. **Decisiones con >2 salidas** (stock completo / parcial / sin stock): reglas de color verde/rojo se rompen. → Flechas negras neutras con etiquetas de texto sobre la línea.

---

## 4. Estructura propuesta (progressive disclosure)

```
diagrama-flujo/
├── SKILL.md               ← reglas de mapeo, rol→color, cómo llamar a scripts
├── references/
│   ├── deta_diagram_styles.css   ← tokens de color, grid CSS, clases .diamond .process-box
│   └── diagram_template.html     ← plantilla Jinja2 base (importa CSS, espera JSON)
└── scripts/
    ├── generar_html_grafo.py     ← toma JSON de Claude, inyecta nodos en template, pone JS de flechas
    └── render_playwright.py      ← levanta HTML, full_page screenshot, devuelve PNG
```

---

## 5. Assets reutilizables

- **Mapa de colores fijo** (JSON/CSS): `{"Vendedor": "red", "Compras": "green", ...}` — no regenerar en cada prompt
- **deta_pdf_base.py**: el PNG del diagrama se inyecta en el PDF existente — no hay que cambiar nada del pipeline
- **Plantilla HTML base**: `cabecera 3 columnas + swimlane grid` — Claude genera solo el JSON de nodos, no el HTML completo

---

## 6. Triggers naturales

- "hazme el diagrama de flujo de este procedimiento"
- "genera el flowchart con los colores de [cliente]"
- "conviérteme este documento en un diagrama visual"
- "mapea esta transcripción a un flujo tipo Lucidchart"
- "sácame el PNG del proceso de ventas"
- "actualiza el diagrama con estos nuevos pasos"
- "dibuja el procedimiento en formato de carriles (swimlanes)"
- "arma el gráfico del flujo para pasarlo a PDF"

---

## 7. Skills adyacentes

- **`procedimiento`** (upstream obligatorio): si el input es texto crudo / minuta, pasar primero por `procedimiento` para estructurar en "Rol → Acción → Resultado". `diagrama-flujo` solo renderiza estructura limpia.
- **`deta_pdf_base.py`**: el PNG resultante se inyecta en el PDF del procedimiento como Sección 9.

---

## 8. Riesgos de sobre-ingeniería

- **No** calcular curvas Bézier en Python — delegar a JS incrustado que corra antes de que Playwright tome la foto
- **No** construir exportación bidireccional — si hay cambio, Claude regenera el JSON entero y sobrescribe
- **No** soportar PlantUML/BPMN/Ditaa como formatos de salida — el pipeline HTML→Playwright→PNG es el estándar DETA

---

## Decisiones de Claude (override del brief NLM)

- ACEPTÉ: HTML + Playwright como motor principal — ya probado en DETA, Playwright tiene 203 calls activos
- ACEPTÉ: deta_pdf_base.py para inyección del PNG en el PDF del procedimiento — cero cambio de stack
- ACEPTÉ: input debe pasar por `procedimiento` si llega sin estructurar
- RECHACÉ: exportar a múltiples formatos — complejidad innecesaria para un solo pipeline probado
- RECHACÉ: Graphviz como backend — layout engine no está diseñado para flowcharts de negocio lineales con swimlanes
- AUMENTÉ: edge case de feedback loops — las fuentes no lo documentan explícitamente pero el procedimiento Sapisa lo tiene

