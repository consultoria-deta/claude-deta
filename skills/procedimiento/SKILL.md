---
name: procedimiento
description: Genera procedimientos con identidad DETA en DOCX + PDF usando python-docx. Detecta el modo de entrada automáticamente (transcripción, notas, diagrama, actualización o combinación). Actívate con: "crea un procedimiento", "documenta el proceso de", "procedimiento de [nombre]", "actualiza el procedimiento", "convierte esto en procedimiento", "genera el procedimiento para [cliente]".
---

# Procedimiento — Generación de Documentos con Identidad DETA

Procesa cualquier fuente de información (transcripción, notas, diagrama o DOCX existente)
y genera un procedimiento formal en DOCX + PDF usando `deta_procedimiento_base.py`.
Nunca inventar políticas, responsabilidades ni pasos — marcar con `[Pendiente]` lo que falte.

---

## Flujo de trabajo

```
1. Detectar modo de entrada (ver Modos abajo)
2. Extraer y estructurar información en el dict de datos
3. Llamar a generar_procedimiento() del template base
4. Confirmar rutas de DOCX y PDF generados
```

---

## 1 — Modos de entrada (detección automática)

| Modo | Fuente | Operación |
|---|---|---|
| **Transcripción** | Grabación o transcripción de sesión de trabajo | Extraer objetivo, alcance, políticas, responsabilidades y pasos desde el texto |
| **Notas sueltas** | Bullets, notas informales, texto no estructurado | Interpretar intención, estructurar en 9 secciones, marcar con [Pendiente] lo que no esté claro |
| **Diagrama en texto** | Descripción textual de un flujo (pasos, decisiones, actores) | Convertir en procedimiento estructurado, inferir políticas y responsabilidades |
| **Actualización** | DOCX o PDF existente + descripción del cambio | Mantener estructura, actualizar secciones modificadas, incrementar versión |
| **Combinación** | Cualquier mezcla de los anteriores | Fusionar fuentes, priorizar la más reciente, marcar conflictos con [Verificar con cliente] |

**Reglas transversales a todos los modos:**
- Si una sección no tiene información suficiente → `[Pendiente — completar con cliente]`
- Nunca inventar políticas, responsabilidades ni pasos
- Tono DETA: directo, claro, sin jerga innecesaria
- Los pasos siempre en formato: `Rol → Acción → Resultado/Destino`
- Todo el texto del cuerpo (párrafos, bullets) va justificado — `WD_ALIGN_PARAGRAPH.JUSTIFY`. Ya implementado en `deta_procedimiento_base.py` v2.0 via `_add_body`, `_add_bullet` y el estilo Normal base.

---

## 2 — Estructura del documento (9 secciones)

| # | Sección | Tipo de contenido |
|---|---|---|
| 1 | Objetivo | Texto: qué estandariza o regula el procedimiento |
| 2 | Alcance | Texto: a quién y qué aplica |
| 3 | Políticas | Lista de bullets: reglas que gobiernan el proceso |
| 4 | Definiciones | Tabla: término → definición |
| 5 | Responsabilidades | Tabla: rol → descripción de sus responsabilidades |
| 6 | Propiedad | Texto: quién es el dueño del proceso |
| 7 | Procedimiento | Subsecciones con pasos en formato Rol → Acción → Resultado |
| 8 | Historial de versiones | Tabla auto-generada (no editar manualmente) |
| 9 | Flujo | Placeholder Lucidchart — se inserta manualmente después |

---

## 3 — Dict de datos

```python
datos = {
    "nombre":   "Nombre del proceso",           # str — para nomenclatura y header
    "cliente":  "NombreCliente",                # str — para nomenclatura
    "version":  1,                              # int — 1 si es nuevo; incrementar en actualización
    "objetivo": "...",                          # str
    "alcance":  "...",                          # str
    "politicas": [                              # list[str]
        "Política 1",
        "Política 2",
    ],
    "definiciones": {                           # dict{str: str}
        "Término": "Definición",
    },
    "responsabilidades": {                      # dict{str: str}
        "Rol": "Descripción de responsabilidades",
    },
    "propiedad": "Responsable del proceso",     # str
    "procedimiento": [                          # list[dict]
        {
            "titulo": "7.1 Nombre del paso o subsección",
            "pasos": [                          # list[str | dict]
                "Rol → Acción → Resultado",
                {                              # sub-subsección opcional
                    "titulo": "A. Subtipo",
                    "pasos": ["Rol → Acción → Resultado"]
                }
            ]
        }
    ],
    "cambios_version": "Descripción del cambio para el historial",  # str
}
```

---

## 4 — Modo actualización (Modo 4)

Cuando la fuente es un DOCX o PDF existente:

```python
import pdfplumber  # si la fuente es PDF

def leer_procedimiento_pdf(ruta_pdf: str) -> str:
    with pdfplumber.open(ruta_pdf) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)

# Si es DOCX:
from docx import Document
def leer_procedimiento_docx(ruta_docx: str) -> str:
    doc = Document(ruta_docx)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
```

Con el texto extraído:
1. Reconstruir el dict `datos` desde el contenido existente
2. Aplicar los cambios descritos por el usuario en las secciones correspondientes
3. Incrementar `version` en 1
4. Documentar el cambio en `cambios_version`

---

## 5 — Dependencias

```python
import sys, os as _os
for _p in [
    _os.path.expanduser("~/mnt/Agent/Templates"),   # Cowork sandbox
    "/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates",
]:
    if _os.path.exists(_os.path.join(_p, "deta_procedimiento_base.py")):
        sys.path.insert(0, _p)
        break
from deta_procedimiento_base import generar_procedimiento
```

```bash
pip install python-docx docx2pdf
```

Verificar antes de generar:
```bash
python3 -c "from deta_procedimiento_base import generar_procedimiento; print('✅ Template OK')"
```

---

## 6 — Output

Guardar en la carpeta del cliente o en `00_inbox/output/` según indique el usuario.

```python
from deta_procedimiento_base import generar_procedimiento

docx_path, pdf_path = generar_procedimiento(datos, output_dir)
```

**Nomenclatura:**
```
Procedimiento_[NombreCorto]_[Cliente]_v[N].docx
Procedimiento_[NombreCorto]_[Cliente]_v[N].pdf
```

---

## 7 — Confirmación al terminar

```
✅ Procedimiento generado

  📄 Procedimiento_[Nombre]_[Cliente]_v[N].docx — X KB
  📄 Procedimiento_[Nombre]_[Cliente]_v[N].pdf  — X KB

Modo detectado: [transcripción / notas / diagrama / actualización / combinación]
Secciones con [Pendiente]: [lista o "ninguna"]
```

Si el PDF no pudo generarse (sin Word ni LibreOffice), reportarlo y entregar solo el DOCX.
