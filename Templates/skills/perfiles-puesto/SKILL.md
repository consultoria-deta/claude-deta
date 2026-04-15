---
name: perfiles-puesto
description: This skill should be used when the user asks to "crea un perfil de puesto", "perfil del puesto", "descripción de cargo", "job profile", "definir el rol", "estructura organizacional", "dame el perfil de [puesto]", "necesito el perfil para [puesto]", or wants to document a role's responsibilities, KPIs, competencies, or organizational boundaries.
---

# Perfiles de Puesto — DETA

Crear perfiles de puesto profesionales con estructura metodológica completa: objetivo, áreas de efectividad, KPIs, funciones, competencias y fronteras del rol.

Un perfil bien construido delimita el rol, aclara fronteras de responsabilidad y ordena la estructura organizacional.

---

## Estructura Obligatoria

Todo perfil contiene estos 9 elementos:

| # | Elemento | Regla clave |
|---|---|---|
| 1 | Nombre del puesto | Claro, sin abreviaciones |
| 2 | Objetivo del puesto | Verbo + qué logra + para quién |
| 3 | Áreas de efectividad | Tabla con KPI, entregable y peso — máximo 5 áreas |
| 4 | KPI por área | Medible y cuantificable, pesos suman 100% |
| 5 | Entregables por área | Producto concreto y verificable |
| 6 | Funciones por área | Mínimo 5 por área, verbo en infinitivo |
| 7 | Conocimientos técnicos | Herramientas, sistemas, normativas |
| 8 | Competencias blandas | Tabla con peso y nivel A/B/C — exactamente 5 competencias |
| 9 | Fronteras del puesto | Sí corresponde / No corresponde |

---

## Objetivo del Puesto

**Fórmula:** Verbo de acción + qué se logra + para quién o para la organización.

**Ejemplos correctos:**
- "Gestionar las operaciones de cobranza para recuperar cartera vencida y mejorar el flujo de efectivo."
- "Coordinar los procesos de reclutamiento para garantizar que las posiciones se cubran con candidatos calificados en los tiempos requeridos."

**Errores a evitar:**
- Vago: "Apoyar en las tareas del área"
- Sin resultado: "Ser responsable de..."
- Demasiado operativo: "Hacer reportes semanales"

---

## Áreas de Efectividad — Tabla Estratégica

```
| Área de Efectividad | KPI | Entregable | Peso |
|---|---|---|---|
| [nombre del área] | [métrica medible] | [producto concreto] | [X%] |
```

**Reglas:**
- **Máximo 5 áreas por puesto** (default 5, menos si el usuario lo pide)
- Los pesos deben sumar 100%
- Cada área agrupa funciones relacionadas — no mezclar temas distintos
- El KPI debe ser cuantificable ("% de recuperación", no "mejorar la recuperación")

---

## Funciones por Área

**Formato:** Verbo en infinitivo + objeto + contexto

- Mínimo 5 funciones por área de efectividad
- Específicas — evitar "apoyar en..." o "realizar tareas diversas"
- Sin redundancias entre áreas

**Ejemplo:**
- Ejecutar llamadas de seguimiento a clientes con cartera vencida
- Elaborar reportes semanales de estatus de cobranza
- Gestionar acuerdos de pago con clientes en mora

---

## Competencias Blandas

**Escala de niveles:**
- **A** = Dominio avanzado (puede enseñarlo)
- **B** = Aplicación práctica (lo hace solo)
- **C** = Comprensión básica (necesita guía)

**Formato de tabla:**

```
| # | Competencia | Peso | Nivel esperado |
|---|---|---|---|
| 1 | [nombre] | X% | B (4) |
```

Los pesos deben sumar 100%. **Exactamente 5 competencias** (default — menos o más solo si el usuario lo pide explícitamente).

**Competencias frecuentes:** Orientación a resultados, Comunicación efectiva, Análisis y pensamiento lógico, Gestión del tiempo, Liderazgo, Toma de decisiones, Adaptación al cambio.

---

## Fronteras del Puesto

Dos secciones únicamente:

- **Sí le corresponde:** Funciones, decisiones y responsabilidades que son de este puesto — lo que el ocupante puede y debe hacer sin pedir permiso.
- **No le corresponde:** Funciones que son de otros puestos — lo que NO debe hacer aunque tenga capacidad o acceso.

No usar el formato anterior de "Relación con [Área]" con columnas comparativas. Las fronteras se delimitan en función del puesto, no de las relaciones con otros roles.

---

## Requisitos del Perfil

**Obligatorios:** escolaridad mínima, carrera afín, años de experiencia, herramientas o software.

**Deseables:** posgrados, certificaciones, experiencia en industrias complementarias.

---

## Proceso de Creación

1. **Reunir información** — organigrama, funciones del ocupante, procesos del área, objetivos estratégicos
2. **Redactar en borrador** — lenguaje claro, verbos de acción, sin jerga innecesaria
3. **Validar con el cliente** — objetivo claro, áreas coherentes con la realidad, KPIs alcanzables
4. **Revisar consistencia** — sin redundancias entre funciones, fronteras claras, pesos sumando 100%
5. **Exportar a HTML** — usar `perfil-de-puesto.html` con identidad DETA
6. **Convertir a PDF** — con pdfkit (ver sección abajo)

---

## Integración con Template HTML

Para generar el PDF o documento formal, usar:

**Template:** `Agent/templates/perfil-de-puesto.html`

**Logo DETA (ya referenciado en el template):**
- Ruta: `Agent/05_JOEL_OPERACION/Marca/logo-deta-white.png` (versión blanca, para fondos oscuros)
- El template ya tiene el `<img src="...">` apuntando a la ruta absoluta en el Drive. No modificar.
- El logo se renderiza correctamente cuando el PDF se genera con Chrome headless (ve sección "Exportar a PDF").

Al completar el HTML, llenar el bloque `DETA_MATCHING_DATA` al final del archivo:

```json
{
  "puesto": "",
  "cliente": "",
  "competencias": [
    {"nombre": "", "peso": 0, "nivel_requerido": "B"}
  ],
  "requisitos": {
    "escolaridad_minima": "",
    "anos_experiencia_min": 0,
    "herramientas": [],
    "sector": ""
  },
  "rango_salarial": {"min": 0, "max": 0, "moneda": "MXN", "tipo": "neto"}
}
```

Este bloque alimenta `deta_matching.py` para calcular el score de matching candidato-puesto.

---

## Errores Comunes

1. **Objetivo vago** — sin verbo, sin resultado, sin métrica
2. **Áreas genéricas** — "Apoyar al área", "Realizar tareas diversas"
3. **KPIs no medibles** — "Mejorar", "Apoyar", "Colaborar"
4. **Pocas funciones** — menos de 5 por área
5. **Competencias sin peso** — no suman 100%
6. **Fronteras borrosas** — se confunde con puestos vecinos
7. **Requisitos irreales** — experiencia mínima inalcanzable para el mercado

---

## Exportar a PDF

El HTML es la fuente de verdad. El PDF es el único entregable que se comparte con el cliente.

### Motor de conversión: Puppeteer (`html_to_pdf.mjs`)

El script `Agent/templates/html_to_pdf.mjs` usa Puppeteer (Chrome headless vía API) para convertir HTML a PDF. A diferencia del CLI de Chrome (`--print-to-pdf`), la API de Puppeteer respeta `displayHeaderFooter: false` — sin fecha, sin URL, sin numeración.

**Por qué Puppeteer y no otra cosa:**
- `wkhtmltopdf` — abandonado, sin builds para Apple Silicon
- Chrome CLI (`--print-to-pdf-no-header`) — el flag no funciona en `--headless=new`
- `reportlab`, `weasyprint`, `xhtml2pdf` — **NUNCA** usarlos para este HTML, pierden todo el CSS

**Ruta del script:** `Agent/templates/html_to_pdf.mjs`

**Dependencias:** `puppeteer` (ya instalado en `Agent/templates/node_modules/`)

### Cómo convertir

Desde Claude Code o terminal:

```bash
node "Agent/templates/html_to_pdf.mjs" "[RUTA_HTML]" "[RUTA_PDF]"
```

Si se omite el segundo argumento, genera el PDF en la misma carpeta con el mismo nombre.

### Lo que hace Cowork

El sandbox de Cowork no tiene acceso a Node ni Puppeteer. Cowork **solo genera el HTML** y al terminar indica al usuario que corra la conversión:

> El perfil está listo:
> - `PerfilPuesto_[Puesto]_[Cliente].html`
>
> Para generar el PDF, corre en tu terminal:
> ```bash
> node "Agent/templates/html_to_pdf.mjs" "[RUTA_COMPLETA_HTML]"
> ```

### Nomenclatura

- HTML: `PerfilPuesto_[Puesto]_[Cliente].html`
- PDF: `PerfilPuesto_[Puesto]_[Cliente].pdf`

### Reglas

- El HTML se mantiene como fuente de verdad — editar siempre el HTML, regenerar el PDF
- El PDF es lo que se comparte con el cliente — nunca el HTML
- **NUNCA** intentar convertir con `reportlab`, `weasyprint`, `xhtml2pdf` ni ningún renderer Python — todos pierden el diseño
- Guardar HTML y PDF en la misma carpeta del reclutamiento
- El bloque `<!--DETA_MATCHING_DATA ... -->` debe ir **después** de `</html>` para que no genere una página en blanco extra

### Reglas de Print Layout (CSS `@media print`)

El template ya incluye reglas de paginación. **No modificarlas ni quitarlas** al generar un perfil:

- `.section { break-inside: avoid }` — las secciones no se parten entre páginas
- `.section-title { break-after: avoid }` — el título siempre va con su contenido (no queda huérfano al fondo)
- `.area-block { break-inside: avoid }` — cada bloque de funciones va completo en una página
- `.boundary { break-inside: avoid }` — cada bloque de frontera va completo
- `.section:has(.competencies-table) { break-before: page }` — Competencias abre en página nueva
- `.section:has(.boundary) { break-before: page }` — Fronteras abre en página nueva
- `.sheet { overflow: visible }` en print — permite que Chrome calcule los breaks correctamente

**Principio:** Un documento ejecutivo DETA nunca corta tablas a la mitad ni deja títulos huérfanos.

---

## Recursos Adicionales

- **`references/ejemplo-completo.md`** — perfil completo de Coordinador Administrativo para referencia
- **`references/competencias.md`** — catálogo de competencias con definiciones y niveles
- **Template HTML:** `Agent/templates/perfil-de-puesto.html`
- **Matching:** `Agent/templates/deta_matching.py` — score candidato-puesto
- **Ejemplos reales en Drive:** `04_Clientes/[Cliente]/04_Perfiles_de_Puesto/`
