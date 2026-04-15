---
name: reporte-pool
description: Genera el Reporte de Pool de Candidatos en PDF para presentar al cliente al cerrar la fase de entrevistas. Actívate con: "reporte de pool", "reporte de candidatos", "genera el reporte para el cliente", "pool de [puesto]", "cierre del proceso", "presentar candidatos al cliente".
---

# Reporte de Pool — Candidatos para el Cliente

Genera el PDF ejecutivo de candidatos evaluados usando `deta_reporte_pool.py`.
Se usa al cierre de la fase de entrevistas, antes de presentar al cliente.

---

---

## Paso previo — Comparativa por NotebookLM (opcional)

Si hay notebook activo del proceso, pedir la comparativa antes de generar el PDF.
El resultado enriquece las `nota_evaluador` y el contexto del reporte.

```bash
notebooklm use [NOTEBOOK_ID]

notebooklm ask "Compara a todos los candidatos del proceso [PUESTO] - [CLIENTE] en las 5 dimensiones DETA (experiencia técnica, competencias blandas, fit organizacional, escolaridad, condiciones) y recomienda el orden de presentación al cliente con una justificación breve por candidato" --save-as-note --note-title "Comparativa Pool [PUESTO] [CLIENTE]"
```

Usar la comparativa como contexto adicional al redactar o revisar `nota_evaluador` de cada candidato.

**Si no hay notebook activo → continuar con los JSONs directamente. No bloquear.**

## Cuándo usar

Al terminar las entrevistas y tener los datos de todos los candidatos evaluados.
El reporte clasifica automáticamente entre recomendados y descartados.

**No usar** para reportes de un solo candidato — para eso existe el skill `entrevista`.

---

## Inputs

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
| cv_path | Opcional | Ruta absoluta al PDF del CV — genera link clickable en tarjeta |
| Scores DETA | Opcional | Si existen, se integran en portada y tarjetas |

---

## Estructura del PDF generado

| Sección | Contenido |
|---|---|
| Portada (p. 1) | Logo DETA blanco, puesto, cliente, fecha, métricas: Total / Recomendados / Descartados |
| Tarjetas (p. 2..N) | Una página por candidato recomendado: score, escolaridad, competencias, fortalezas, nota |
| Contactos (p. N+1) | Tabla: Nombre / Email / Teléfono / Score / Notas |
| Descartados (p. N+2) | Tabla simple: Nombre / Score / Razón |

---

## Reglas críticas

- **Score máximo 100** — se normaliza automáticamente si viene mayor
- **Niveles de competencia escritos completos** — Alto / Medio / Básico (no A/B/C)
- **Datos de contacto solo en tabla final** — no en las tarjetas individuales
- **Email y teléfono** — extraerlos del CV con pdfplumber si no están en la transcripción (ver skill entrevista → "extraer_contacto_cv")
- **Notas** — usar la sección 9 del Reporte de Candidato (recomendación y próximos pasos), texto resumido
- **cv_path** — ruta absoluta al PDF del CV; genera link clickable en cada tarjeta
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
        "email":    "[email@dominio.com]",    # None si no existe
        "telefono": "[614-XXX-XXXX]",         # None si no existe
        "cv_path":  "[/ruta/absoluta/CV.pdf]", # None si no existe → sin link
        "recomendado": True,                   # False → va a tabla de descartados
    },
    # ... más candidatos
]

generar_reporte_pool(
    candidatos=candidatos,
    puesto="[PUESTO]",
    cliente="[CLIENTE]",
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
