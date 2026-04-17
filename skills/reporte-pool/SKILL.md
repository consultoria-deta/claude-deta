---
name: reporte-pool
description: Genera el Reporte de Pool de Candidatos en PDF para presentar al cliente al cerrar la fase de entrevistas. Actívate con: "reporte de pool", "reporte de candidatos", "genera el reporte para el cliente", "pool de [puesto]", "cierre del proceso", "presentar candidatos al cliente".
---

# Reporte de Pool — Candidatos para el Cliente

Genera el PDF ejecutivo de candidatos evaluados usando `deta_reporte_pool.py`.
Se usa al cierre de la fase de entrevistas, antes de presentar al cliente.

---

> **NotebookLM — No requerido en este flujo.** No invocar notebooklm en ningún paso. Usar directamente los JSONs sidecar generados por el skill `entrevista`.

## Cuándo usar

Al terminar las entrevistas y tener los datos de todos los candidatos evaluados.
El reporte clasifica automáticamente entre recomendados y descartados.

**No usar** para reportes de un solo candidato — para eso existe el skill `entrevista`.

---

## Inputs

### Métricas del proceso (requeridas — el evaluador las proporciona)

Estas tres métricas se muestran en las tarjetas numéricas grandes de la portada del PDF.
**No se derivan del conteo de la lista de candidatos** — el pool real de CVs recibidos
es mucho mayor al de entrevistados, por lo que el evaluador las declara explícitamente.

| Campo | Tipo | Descripción |
|---|---|---|
| `total_cvs_recibidos` | ✅ int | Total de CVs recibidos en el proceso (incluye no entrevistados) |
| `total_recomendados` | ✅ int | Candidatos que avanzan (recomendado: True en su dict) |
| `total_descartados` | ✅ int | Candidatos descartados en cualquier etapa |

Preguntar al evaluador estos tres valores antes de generar el PDF si no se proporcionan en el prompt.

### Opción A — Desde carpeta (JSON sidecars) ← recomendado

Si el skill de entrevista guardó los `datos_*.json` de cada candidato en la misma carpeta:

```python
candidatos = cargar_candidatos_desde_carpeta("ruta/al/proceso/")
```

Solo necesitas indicar la carpeta. Los JSONs se cargan automáticamente.

### Opción B — Manual

| Input | Requerido | Descripción |
|---|---|---|
| Lista de candidatos | ✅ | Dicts con nombre, scores, competencias, fortalezas, contacto |
| Puesto | ✅ | Nombre exacto del puesto evaluado |
| Cliente | ✅ | Nombre del cliente |
| total_cvs_recibidos | ✅ | Total de CVs recibidos en el proceso |
| total_recomendados | ✅ | Candidatos que avanzan — mostrados en portada |
| total_descartados | ✅ | Candidatos descartados — mostrados en portada |
| cv_path | Opcional | URL de Google Drive / Dropbox o ruta absoluta al CV — genera link clickable en tarjeta |
| Scores DETA | Opcional | Si existen, se integran en portada y tarjetas |

---

## Estructura del PDF generado

| Sección | Contenido |
|---|---|
| Portada (p. 1) | Logo DETA blanco, puesto, cliente, fecha, métricas: `total_cvs_recibidos` / `total_recomendados` / `total_descartados` — valores proporcionados por el evaluador, no contados automáticamente |
| Tarjetas (p. 2..N) | Una página por candidato recomendado: score, escolaridad, competencias, fortalezas, nota, **link al CV** (si `cv_path` existe) |
| Contactos (p. N+1) | Tabla: Nombre / Email / Teléfono / Score / Notas |
| Descartados (p. N+2) | Tabla simple: Nombre / Score / Razón |

---

## Reglas críticas

- **Score máximo 100** — se normaliza automáticamente si viene mayor
- **Niveles de competencia escritos completos** — Alto / Medio / Básico (no A/B/C)
- **Datos de contacto solo en tabla final** — no en las tarjetas individuales
- **Email y teléfono** — extraerlos del CV con pdfplumber si no están en la transcripción (ver skill entrevista → "extraer_contacto_cv")
- **Notas** — usar la sección 9 del Reporte de Candidato (recomendación y próximos pasos), texto resumido
- **cv_path** — acepta ruta absoluta (`/ruta/al/CV.pdf`) o URL (`https://drive.google.com/...`, `https://dropbox.com/...`); genera link clickable en la tarjeta del candidato. Si es `None`, no mostrar link.
- **Métricas de portada** — usar siempre `total_cvs_recibidos`, `total_recomendados`, `total_descartados` tal como los declaró el evaluador. No recalcular desde la lista de candidatos.
- **Sin referencias a herramientas internas** — no mencionar OCC, ATS, portales de empleo
- **Footer:** "Confidencial — DETA Consultores · detaconsultores.com"
- **Paginación:** pre-calculada antes de generar — nunca "4 de 2"
- **Tabla de contactos:** incluye Score solo si al menos un candidato tiene score; si ninguno tiene, la columna se omite y las Notas toman el espacio

---

## Cómo usarlo

### Opción A — Desde carpeta (recomendado)

```python
import sys
import os as _os
for _p in [
    "/mnt",
    "/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates",
]:
    if _os.path.exists(_os.path.join(_p, "deta_pdf_base.py")):
        sys.path.insert(0, _p)
        break
from deta_reporte_pool import generar_reporte_pool, cargar_candidatos_desde_carpeta

carpeta = "[RUTA_PROCESO]"  # donde están los datos_*.json

candidatos = cargar_candidatos_desde_carpeta(carpeta)

generar_reporte_pool(
    candidatos=candidatos,
    puesto="[PUESTO]",
    cliente="[CLIENTE]",
    total_cvs_recibidos=150,   # ← declarar explícitamente; no derivar de len(candidatos)
    total_recomendados=5,      # ← candidatos que avanzan
    total_descartados=145,     # ← descartados en cualquier etapa
    output_path=f"{carpeta}/ReportePool_[Puesto]_[Cliente]_[YYYYMMDD].pdf",
)
```

### Opción B — Manual

```python
import sys
import os as _os
for _p in [
    "/mnt",
    "/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates",
]:
    if _os.path.exists(_os.path.join(_p, "deta_pdf_base.py")):
        sys.path.insert(0, _p)
        break
from deta_reporte_pool import generar_reporte_pool

candidatos = [
    {
        "nombre":        "[NOMBRE]",
        "score":         82,              # None si no hay score
        "nivel":         "Sólido",        # None si no hay score
        "escolaridad":   "[ESCOLARIDAD]",
        "experiencia":   "[X años en Y]",
        "ultimo_puesto": "[Puesto · Empresa (año-año). Descripción breve.]",
        "competencias":  [
            {"nombre": "[Competencia]", "nivel": "Alto"},
            {"nombre": "[Competencia]", "nivel": "Medio"},
        ],
        "fortalezas": [
            "[Fortaleza 1 — con evidencia de la entrevista]",
            "[Fortaleza 2]",
            "[Fortaleza 3]",
        ],
        "nota_evaluador": "[Nota breve del evaluador]",
        "email":    "[email@dominio.com]",                          # None si no existe
        "telefono": "[614-XXX-XXXX]",                               # None si no existe
        "cv_path":  "https://drive.google.com/file/d/[ID]/view",   # URL o ruta absoluta; None → sin link
        "recomendado": True,                                        # False → va a tabla de descartados
    },
    # ... más candidatos
]

generar_reporte_pool(
    candidatos=candidatos,
    puesto="[PUESTO]",
    cliente="[CLIENTE]",
    total_cvs_recibidos=150,   # ← proporcionado por el evaluador
    total_recomendados=5,
    total_descartados=145,
    output_path="[RUTA_OUTPUT]/ReportePool_[Puesto]_[Cliente]_[YYYYMMDD].pdf",
)
```

---

## Output

```
ReportePool_[Puesto]_[Cliente]_[YYYYMMDD].pdf
```

Guardar en la carpeta del reclutamiento del cliente:
```
Agent/Reclutamientos/[Cliente]/[Puesto]/
```

---

## Script

`Agent/templates/deta_reporte_pool.py`

Verificar antes de usar:
```bash
cd ".../Agent/templates/" && python3 deta_reporte_pool.py
```
Debe generar un PDF de prueba de 5 páginas sin errores.
