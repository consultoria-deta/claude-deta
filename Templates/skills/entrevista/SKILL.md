---
name: entrevista
description: Genera dos PDFs estándar DETA a partir de una transcripción de entrevista — Minuta y Reporte de Candidato. Actívate con: "minuta de [nombre]", "procesa entrevista de [nombre]", "genera documentos de [nombre]", "reporte de candidato [nombre]", "procesa la entrevista", "genera los dos documentos", "con scoring", "evalúa al candidato", "score del candidato".
---

# Entrevista — Generación de Documentos PDF desde Transcripción

Procesa una transcripción de entrevista y genera dos PDFs estándar DETA usando `deta_pdf_base.py`.
Nunca redefinir colores, fuentes ni estructura — todo viene del template base.

---

---

## 0 — Notebook del proceso (opcional — ahorra tokens)

Si existe un notebook activo para este proceso de reclutamiento, usarlo para extraer
datos del CV antes del scoring. Esto reemplaza la lectura directa del PDF por Claude.

```bash
# Activar el notebook del proceso (guardado en el JSON del proceso o en el prompt)
notebooklm use [NOTEBOOK_ID]

# Añadir el CV si aún no está como fuente
notebooklm source add [RUTA_CV]

# Extraer datos clave — retorna ~200 palabras en vez de pasar el PDF completo
notebooklm ask "Para [NOMBRE], extrae del CV: nombre completo, email, teléfono, años de experiencia total, último puesto y empresa, escolaridad, y las 5 competencias más relevantes" --save-as-note --note-title "Extracto CV [NOMBRE]"
```

Usar el extracto devuelto como fuente de datos en los pasos 2 y 3 (contacto y scoring).

**Si no hay notebook activo → continuar el flujo normal leyendo el CV directamente.**
No bloquear por ausencia de notebook.

## Flujo de trabajo

```
1. Localizar transcripción en 00_inbox/
2. Si hay perfil de puesto (HTML o PDF) + CV → calcular score DETA
3. Extraer datos de la transcripción por sección
4. Generar Minuta usando deta_pdf_base.py
5. Generar Reporte de Candidato con score integrado (si aplica)
6. Guardar datos_[Nombre]_[YYYYMMDD].json junto a los PDFs (sidecar para pool)
7. Confirmar archivos generados
```

**Inputs opcionales para scoring:**

| Input | Dónde buscarlo | Si no existe |
|---|---|---|
| Perfil de puesto (HTML o PDF) | Ruta que indique el usuario | Omitir score — generar documentos sin él |
| CV del candidato | `00_inbox/` o ruta explícita | Omitir score — generar documentos sin él |

Si se proporcionan ambos → calcular score antes de generar el Reporte de Candidato.
Si falta alguno → continuar el flujo sin score. No bloquear la generación de PDFs.

**Cómo leer el perfil según formato:**

- **HTML con bloque `DETA_MATCHING_DATA`** → usar `deta_matching.py` directamente
- **PDF** → extraer texto con pdfplumber y derivar competencias/requisitos del contenido:

```python
import pdfplumber

def leer_perfil_pdf(ruta_perfil: str) -> str:
    with pdfplumber.open(ruta_perfil) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)
```

Con el texto extraído, Claude evalúa las cinco dimensiones directamente contra el contenido del perfil (sin necesidad de `DETA_MATCHING_DATA`). Aplicar la misma fórmula de scoring que `deta_matching.py`:

| Dimensión | Peso (con transcripción) | Peso (sin transcripción) |
|---|---|---|
| Experiencia técnica | 35% | 50% |
| Competencias blandas | 25% | — |
| Fit organizacional | 20% | 30% |
| Escolaridad | 10% | 10% |
| Condiciones | 10% | 10% |

Escala de niveles:

| Rango | Nivel |
|---|---|
| 90-100 | Excepcional |
| 75-89 | Sólido |
| 60-74 | Con potencial |
| 45-59 | Marginal |
| 0-44 | No recomendado |

---

## 1 — Localizar la transcripción

La transcripción llega en `00_inbox/` con alguno de estos formatos:

```
00_inbox/
  entrevista_[Nombre]_[YYYYMMDD].txt
  entrevista_[Nombre]_[YYYYMMDD].md
  [Nombre]_entrevista.txt
  transcript_[Nombre].txt
```

**Si hay más de un archivo:** usar el más reciente (por fecha de modificación).
**Si no hay archivo:** preguntar al usuario antes de continuar — nunca asumir.

Para extraer el nombre del candidato: tomar el nombre del archivo o del encabezado de la transcripción. Normalizar a `Nombre_Apellido` (sin espacios, guiones bajos).

---

## 2 — Reglas de producción (aplicar en los tres documentos)

1. **No inventar datos** — si algo no está en la transcripción, omitir la sección o marcarla como `[No mencionado]`
2. **No parafrasear en exceso** — citas directas del candidato entre comillas cuando sea relevante
3. **Tono DETA** — directo, profesional, sin jerga corporativa vacía ("sinergia", "empoderar", "robusto")
4. **Fechas** — usar `today_str()` de `deta_pdf_base.py` para consistencia
5. **Nunca** redefinir `NAVY`, `GOLD`, `CYAN` ni fuentes — importar todo desde `deta_pdf_base`
6. **Confidencialidad** — agregar en footer: "Documento confidencial — DETA Consultores"

---

## 3 — Documento 1: Minuta de Entrevista

**Propósito:** Registro fiel de lo que ocurrió en la sesión. Sin interpretación — hechos y dichos.

**Nomenclatura:** `Minuta_[Nombre]_[YYYYMMDD].pdf`

### Secciones

| Sección | Contenido | Fuente |
|---|---|---|
| Encabezado | Candidato, Puesto, Fecha, Entrevistador | Transcripción / metadatos |
| Participantes | Nombres y roles de todos los presentes | Transcripción |
| Contexto | Empresa del candidato, puesto actual, motivo de contacto | Transcripción |
| Desarrollo | Cronología de temas tratados — sin evaluación | Transcripción |
| Compromisos | Próximos pasos acordados en la sesión | Transcripción |
| Observaciones | Aspectos logísticos o de contexto relevantes | Transcripción |

### Estructura de página

```python
from deta_pdf_base import *

def generar_minuta(transcripcion: dict, output_path: str):
    c, W, H = new_doc(output_path, f"Minuta — {transcripcion['nombre']}")

    draw_header(c, doc_title="MINUTA DE ENTREVISTA")
    draw_footer(c, page_num=1, label="Confidencial — DETA Consultores")

    x, y, col_w, _ = content_area()

    # Título
    text_h1(c, f"Minuta — {transcripcion['nombre']}", x, y)
    y -= 10 * mm
    rule(c, x, y, col_w)
    y -= 8 * mm

    # Ficha de datos
    y = data_row(c, "CANDIDATO",     transcripcion['nombre'],       x, y, col_w, False)
    y = data_row(c, "PUESTO",        transcripcion['puesto'],        x, y, col_w, True)
    y = data_row(c, "FECHA",         transcripcion['fecha'],         x, y, col_w, False)
    y = data_row(c, "ENTREVISTADOR", transcripcion['entrevistador'], x, y, col_w, True)
    y -= 8 * mm

    # Secciones de contenido
    for seccion, contenido in transcripcion['secciones'].items():
        section_tag(c, seccion.upper(), x, y)
        y -= 10 * mm
        y = text_wrap(c, contenido, x, y, col_w, size=9, leading=14)
        y -= 8 * mm
        if y < 40 * mm:          # salto de página si queda poco espacio
            new_page(c)
            draw_header(c, doc_title="MINUTA DE ENTREVISTA")
            draw_footer(c, page_num=2, label="Confidencial — DETA Consultores")
            x, y, col_w, _ = content_area()

    c.save()
```

---

## 4 — Documento 2: Reporte de Candidato

**Propósito:** Documento completo para expediente. Incluye todo lo relevante para decisiones de contratación o seguimiento.

**Nomenclatura:** `ReporteCandidato_[Nombre]_[YYYYMMDD].pdf`

### Secciones

| Sección | Contenido |
|---|---|
| 1. Datos generales | Nombre completo, puesto actual, empresa, contacto si se mencionó |
| 2. Trayectoria profesional | Experiencia relevante mencionada en la entrevista — cronológica |
| 3. Motivaciones y expectativas | Qué busca, por qué cambiaría, qué valora en un empleador |
| 4. Competencias observadas | Habilidades técnicas y blandas evidenciadas — con cita de soporte |
| 5. Áreas de desarrollo | Gaps identificados — redactar con respeto y objetividad |
| 6. Cultura y fit organizacional | Señales de alineación o desalineación con los valores DETA |
| 7. Pretensiones económicas | Solo si se mencionaron explícitamente — nunca estimar |
| 8. Evaluación general | Tabla: criterio / nivel (Alto/Medio/Bajo) / comentario |
| 9. Recomendación y próximos pasos | Decisión, razón, acción concreta y fecha si aplica |

### Tabla de evaluación general (sección 8)

```python
# Criterios estándar — omitir filas sin información suficiente
CRITERIOS_EVALUACION = [
    "Experiencia técnica",
    "Liderazgo",
    "Comunicación",
    "Adaptabilidad",
    "Alineación cultural",
    "Potencial de crecimiento",
]

# Renderizar con data_row() alternando color de fila
y_actual = y
for i, criterio in enumerate(criterios_con_datos):
    y_actual = data_row(
        c, criterio, nivel_y_comentario,
        x, y_actual, col_w,
        is_alternate=(i % 2 == 1)
    )

# Si hay score DETA disponible — agregar al final de la tabla
if score_data:
    score_texto = f"{score_data['score_total']}/100 — {score_data['nivel']}"
    y_actual = data_row(c, "SCORE DETA", score_texto,
                        x, y_actual, col_w, is_alternate=True)
```

### Recomendación (sección 9) — callout con color según nivel

```python
# Si hay score DETA, el callout usa color según nivel
if score_data:
    nivel = score_data["nivel"]
    bg_color = CYAN  if nivel in ["Excepcional", "Sólido"] else \
               GOLD  if nivel == "Con potencial"            else SURFACE
    fg_color = WHITE if nivel in ["Excepcional", "Sólido"] else NAVY
    callout_box(c,
        f"Score DETA: {score_data['score_total']}/100 — {nivel}",
        x, y, col_w, 18 * mm,
        bg=bg_color, accent=fg_color
    )
```

---

## 5 — Output esperado

```
00_inbox/output/
  Minuta_[Nombre]_[YYYYMMDD].pdf
  ReporteCandidato_[Nombre]_[YYYYMMDD].pdf
  datos_[Nombre]_[YYYYMMDD].json          ← sidecar para reporte de pool
```

Donde `[YYYYMMDD]` es la fecha de generación (no la de la entrevista), usando:

```python
from datetime import datetime
fecha_hoy = datetime.now().strftime("%Y%m%d")
nombre_normalizado = nombre.replace(" ", "_")

rutas = {
    "minuta":    f"00_inbox/output/Minuta_{nombre_normalizado}_{fecha_hoy}.pdf",
    "reporte":   f"00_inbox/output/ReporteCandidato_{nombre_normalizado}_{fecha_hoy}.pdf",
    "datos_json": f"00_inbox/output/datos_{nombre_normalizado}_{fecha_hoy}.json",
}
```

Crear el directorio si no existe:

```python
from deta_pdf_base import ensure_dir
ensure_dir("00_inbox/output/")
```

### JSON sidecar — guardar junto al PDF

Después de generar el Reporte de Candidato, guardar un JSON con todos los datos
estructurados del candidato. Este archivo alimenta automáticamente `cargar_candidatos_desde_carpeta()`
en `deta_reporte_pool.py` al generar el reporte de pool.

```python
import json

datos_candidato = {
    "nombre":        nombre_completo,
    "score":         score_data["score_total"] if score_data else None,
    "nivel":         score_data["nivel"]       if score_data else None,
    "escolaridad":   datos["escolaridad"],
    "experiencia":   datos["anos_experiencia"],
    "ultimo_puesto": datos["ultimo_puesto"],
    "competencias": [
        {"nombre": c["nombre"], "nivel": c["nivel"]}
        for c in datos.get("competencias_observadas", [])
    ],
    "fortalezas":    datos.get("fortalezas", []),
    "nota_evaluador": datos.get("recomendacion_y_proximos_pasos", ""),
    # Contacto — extraer del CV con pdfplumber si no se menciona en la transcripción
    "email":    datos.get("email"),
    "telefono": datos.get("telefono"),
    "cv_path":  ruta_cv if ruta_cv else None,
    "recomendado": datos.get("recomendado", False),   # True / False
}

with open(rutas["datos_json"], "w", encoding="utf-8") as f:
    json.dump(datos_candidato, f, ensure_ascii=False, indent=2)
```

**Campo `recomendado`:** extraerlo de la sección 9 del reporte.
- `True` → candidato avanza (recomendado, confirmado, aprobado para entrevista)
- `False` → descartado, en espera sin decisión, o condicional

**Campo `email` / `telefono`:** buscar en este orden:
1. Transcripción de entrevista (si el candidato lo mencionó)
2. CV del candidato — extraer con `pdfplumber`:

```python
import pdfplumber, re

def extraer_contacto_cv(ruta_cv):
    email, telefono = None, None
    with pdfplumber.open(ruta_cv) as pdf:
        texto = " ".join(p.extract_text() or "" for p in pdf.pages[:2])
    m_email = re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', texto)
    m_tel   = re.search(r'(\+52\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', texto)
    if m_email: email    = m_email.group()
    if m_tel:   telefono = m_tel.group()
    return email, telefono
```

**Campo `cv_path`:** ruta absoluta al PDF del CV si existe, `None` si no.

**Campo `nota_evaluador`:** texto de la sección 9 del Reporte de Candidato (recomendación y próximos pasos). Incluir la decisión y el contexto de acción, no solo el nivel.

---

## 6 — Confirmación al terminar

Al finalizar la generación, reportar:

```
✅ Tres archivos generados en 00_inbox/output/

  📄 Minuta_[Nombre]_[YYYYMMDD].pdf           — X KB
  📄 ReporteCandidato_[Nombre]_[YYYYMMDD].pdf  — X KB
  📋 datos_[Nombre]_[YYYYMMDD].json            — sidecar para reporte de pool

Fuente: [nombre del archivo de transcripción]
Candidato: [Nombre completo]
Puesto evaluado: [puesto]
Score DETA: XX/100 — [Nivel]       ← incluir solo si se calculó
Recomendado: Sí / No / En espera
```

Si algún documento no pudo generarse (datos insuficientes), reportarlo explícitamente en lugar de omitirlo en silencio.

---

## 7 — Dependencias

```python
# Al inicio de cualquier script que use este skill:
import sys
import os as _os
for _p in [
    "/mnt",
    "/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates",
]:
    if _os.path.exists(_os.path.join(_p, "deta_pdf_base.py")):
        sys.path.insert(0, _p)
        break
from deta_pdf_base import *
```

**Dependencias del sistema:**
```bash
pip install reportlab pillow
```

**Template base:** `deta_pdf_base.py` en `Agent/templates/`
Verificar que funciona antes de generar documentos:
```bash
cd ".../Agent/templates/" && python3 -c "from deta_pdf_base import *; print('✅ Template OK')"
```
