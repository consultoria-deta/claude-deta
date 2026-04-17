---
name: reunion
description: Genera un PDF único con Resumen Ejecutivo + Minuta de Reunión a partir de una transcripción con cliente. Ambas secciones son entregables formales de DETA. Actívate con: "minuta de reunión", "resumen de reunión", "procesa la reunión", "genera documentos de la reunión con [cliente]", "minuta con [cliente]", "resumen ejecutivo de [cliente]", "documenta la reunión con [cliente]".
---

# Reunión con Cliente — Generación de Documento PDF

Procesa una transcripción de reunión y genera un PDF único con dos secciones:
Resumen Ejecutivo (página 1) + Minuta de Reunión (páginas siguientes).
El PDF completo es un entregable formal de DETA — se envía al cliente.
Nunca redefinir colores, fuentes ni estructura — todo viene de `deta_pdf_base.py`.

---

## Flujo de trabajo

```
1. Localizar transcripción en 00_inbox/
2. Extraer datos según estructura de cada sección
3. Generar UN solo PDF con las dos secciones
4. Guardar en output con nomenclatura estándar
5. Confirmar archivo generado
```

---

## 1 — Localizar la transcripción

La transcripción llega en `00_inbox/` con alguno de estos formatos:

```
00_inbox/
  reunion_[Cliente]_[YYYYMMDD].txt
  reunion_[Cliente]_[YYYYMMDD].md
  [Cliente]_reunion.txt
  notas_[Cliente].txt
  transcript_[Cliente].txt
```

**Si hay más de un archivo:** usar el más reciente (por fecha de modificación).
**Si no hay archivo:** preguntar al usuario antes de continuar — nunca asumir.

Para extraer el nombre del cliente: tomar el nombre del archivo o del encabezado
de la transcripción. Normalizar a `NombreCliente` (sin espacios, CamelCase o guiones bajos).

---

## 2 — Reglas de producción (aplicar en todo el documento)

1. **No inventar datos** — si algo no está en la transcripción, omitir la sección o marcarla `[No mencionado]`
2. **Tono DETA** — directo, cálido, sin jerga corporativa ("sinergia", "empoderar", "robusto", "holístico")
3. **Resumen Ejecutivo** — segunda persona: "En la reunión acordamos...", "Tu siguiente paso es..."
4. **Minuta** — tercera persona, redactada profesionalmente para el cliente (entregable formal, no registro interno)
5. **Fechas** — usar `today_str()` de `deta_pdf_base.py`
6. **Nunca** redefinir `NAVY`, `GOLD`, `CYAN` ni fuentes — importar todo desde `deta_pdf_base`
7. **Footer igual en todas las páginas:** `"DETA Consultores · detaconsultores.com"`
8. **Si la transcripción es corta o solo hay notas:** generar igual con lo que haya

---

## 3 — Estructura del PDF

### PÁGINA 1 — Resumen Ejecutivo

**Propósito:** síntesis ejecutiva para el cliente. Máximo 1 página.

| Elemento | Contenido |
|---|---|
| Header | `draw_header(c, doc_title="RESUMEN EJECUTIVO")` — fondo navy, logo blanco |
| Callout box | Acuerdo o decisión más importante de la reunión |
| Contexto | 2 líneas sobre de qué se trató la reunión |
| Puntos clave | 4-6 bullets con `bullet_item()` — concretos, accionables |
| Acuerdos | Con responsable explícito: DETA o cliente |
| Próximos pasos | Con fecha si se mencionaron |
| CTA | Qué necesita decidir o hacer el cliente |
| Footer | `draw_footer(c, page_num=1, total_pages=N, label="DETA Consultores · detaconsultores.com")` |

```python
def generar_resumen_ejecutivo(c, datos: dict, total_pages: int):
    draw_header(c, doc_title="RESUMEN EJECUTIVO")
    draw_footer(c, page_num=1, total_pages=total_pages,
                label="DETA Consultores · detaconsultores.com")

    x, y, col_w, _ = content_area()

    # Título
    text_h1(c, f"Resumen Ejecutivo — {datos['cliente']}", x, y)
    y -= 8 * mm
    text_label(c, datos['fecha_reunion'], x, y, color=GRAY_TEXT)
    y -= 10 * mm
    rule(c, x, y, col_w)
    y -= 10 * mm

    # Callout — acuerdo o decisión principal
    if datos.get('acuerdo_principal'):
        callout_box(c, datos['acuerdo_principal'], x, y, col_w, 20 * mm)
        y -= 26 * mm

    # Contexto
    if datos.get('contexto'):
        section_tag(c, "CONTEXTO", x, y)
        y -= 10 * mm
        y = text_wrap(c, datos['contexto'], x, y, col_w, size=9, leading=14)
        y -= 8 * mm

    # Puntos clave
    if datos.get('puntos_clave'):
        section_tag(c, "PUNTOS CLAVE", x, y)
        y -= 10 * mm
        for punto in datos['puntos_clave']:
            y = bullet_item(c, punto, x, y, col_w)
            y -= 3 * mm
        y -= 5 * mm

    # Acuerdos
    if datos.get('acuerdos'):
        section_tag(c, "ACUERDOS", x, y)
        y -= 10 * mm
        for acuerdo in datos['acuerdos']:
            y = bullet_item(c, acuerdo, x, y, col_w, dot_color=GOLD)
            y -= 3 * mm
        y -= 5 * mm

    # Próximos pasos
    if datos.get('proximos_pasos'):
        section_tag(c, "PRÓXIMOS PASOS", x, y)
        y -= 10 * mm
        for paso in datos['proximos_pasos']:
            y = bullet_item(c, paso, x, y, col_w, dot_color=CYAN)
            y -= 3 * mm
        y -= 5 * mm

    # CTA
    if datos.get('cta'):
        section_tag(c, "TU SIGUIENTE PASO", x, y, bg=GOLD, fg=NAVY)
        y -= 10 * mm
        y = text_wrap(c, datos['cta'], x, y, col_w,
                      font="Poppins-Bold", size=9, color=NAVY, leading=14)
```

---

### PÁGINAS 2+ — Minuta de Reunión

**Propósito:** registro formal y completo de la sesión. Entregable profesional para el cliente.

| Elemento | Contenido |
|---|---|
| Header | `draw_header(c, doc_title="MINUTA DE REUNIÓN")` |
| Ficha de datos | Cliente, Empresa, Fecha, Participantes, Objetivo — con `data_row()` |
| CONTEXTO | Situación actual del cliente o proyecto |
| DESARROLLO | Cronología fiel de temas tratados — redactada profesionalmente |
| ACUERDOS | Compromisos concretos con responsable explícito |
| PRÓXIMOS PASOS | Acciones con responsable y fecha si existen |
| OBSERVACIONES | Datos de contexto relevantes |
| Footer | `"DETA Consultores · detaconsultores.com"` — paginación 2/N, 3/N... |

```python
def generar_minuta(c, datos: dict, page_start: int, total_pages: int):
    """
    Genera las páginas de minuta a partir de page_start.
    Maneja saltos de página automáticos cuando y < 40mm.
    """
    pagina_actual = page_start

    draw_header(c, doc_title="MINUTA DE REUNIÓN")
    draw_footer(c, page_num=pagina_actual, total_pages=total_pages,
                label="DETA Consultores · detaconsultores.com")

    x, y, col_w, _ = content_area()

    # Título
    text_h1(c, "Minuta de Reunión", x, y)
    y -= 10 * mm
    rule(c, x, y, col_w)
    y -= 8 * mm

    # Ficha de datos
    campos = [
        ("CLIENTE",       datos.get('cliente', '')),
        ("EMPRESA",       datos.get('empresa', '')),
        ("FECHA",         datos.get('fecha_reunion', '')),
        ("PARTICIPANTES", datos.get('participantes', '')),
        ("OBJETIVO",      datos.get('objetivo', '')),
    ]
    for i, (label, valor) in enumerate(campos):
        if valor:
            y = data_row(c, label, valor, x, y, col_w, is_alternate=(i % 2 == 1))
    y -= 10 * mm

    def salto_si_necesario(y_actual):
        nonlocal pagina_actual
        if y_actual < 40 * mm:
            new_page(c)
            pagina_actual += 1
            draw_header(c, doc_title="MINUTA DE REUNIÓN")
            draw_footer(c, page_num=pagina_actual, total_pages=total_pages,
                        label="DETA Consultores · detaconsultores.com")
            _, y_nuevo, _, _ = content_area()
            return y_nuevo
        return y_actual

    # Secciones de contenido
    secciones = [
        ("CONTEXTO",        datos.get('contexto_minuta')),
        ("DESARROLLO",      datos.get('desarrollo')),
        ("ACUERDOS",        datos.get('acuerdos_minuta')),
        ("PRÓXIMOS PASOS",  datos.get('proximos_pasos_minuta')),
        ("OBSERVACIONES",   datos.get('observaciones')),
    ]

    for nombre_seccion, contenido in secciones:
        if not contenido:
            continue
        y = salto_si_necesario(y)
        section_tag(c, nombre_seccion, x, y)
        y -= 10 * mm
        if isinstance(contenido, list):
            for item in contenido:
                y = bullet_item(c, item, x, y, col_w)
                y -= 3 * mm
                y = salto_si_necesario(y)
        else:
            y = text_wrap(c, contenido, x, y, col_w, size=9, leading=14)
        y -= 8 * mm
```

---

## 4 — Generar el PDF único

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
from deta_pdf_base import *
from datetime import datetime

def generar_reunion(ruta_transcripcion: str, output_dir: str = "00_inbox/output/"):
    """
    Punto de entrada principal.
    Lee la transcripción, extrae datos y genera el PDF único.
    """
    ensure_dir(output_dir)

    # Extraer datos de la transcripción
    datos = extraer_datos(ruta_transcripcion)   # implementar según la transcripción

    # Calcular total de páginas (estimación: 1 resumen + 2-4 minuta)
    # Ajustar según contenido real
    total_pages = estimar_paginas(datos)

    # Nomenclatura
    fecha_hoy = datetime.now().strftime("%Y%m%d")
    cliente_slug = datos['cliente'].replace(" ", "_")
    output_path = f"{output_dir}Reunion_{cliente_slug}_{fecha_hoy}.pdf"

    # Crear documento
    c, W, H = new_doc(output_path, f"Reunión — {datos['cliente']}")

    # Página 1: Resumen Ejecutivo
    generar_resumen_ejecutivo(c, datos, total_pages)

    # Páginas 2+: Minuta
    new_page(c)
    generar_minuta(c, datos, page_start=2, total_pages=total_pages)

    c.save()
    return output_path, total_pages
```

**Nomenclatura de salida:**
```python
from datetime import datetime
fecha_hoy = datetime.now().strftime("%Y%m%d")
cliente_slug = cliente.replace(" ", "_")
output_path = f"00_inbox/output/Reunion_{cliente_slug}_{fecha_hoy}.pdf"
```

---

## 5 — Output esperado

```
00_inbox/output/
  Reunion_[Cliente]_[YYYYMMDD].pdf
```

Crear el directorio si no existe:
```python
from deta_pdf_base import ensure_dir
ensure_dir("00_inbox/output/")
```

---

## 6 — Confirmación al terminar

```
✅ Documento generado en 00_inbox/output/

  📄 Reunion_[Cliente]_[YYYYMMDD].pdf — X KB
     Página 1: Resumen Ejecutivo
     Páginas 2-N: Minuta de Reunión

Fuente: [nombre del archivo de transcripción]
Cliente: [Nombre completo]
Reunión: [fecha]
```

Si el documento no pudo generarse, reportarlo explícitamente.

---

## 7 — Dependencias

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
from deta_pdf_base import *
```

```bash
pip install reportlab pillow
```

Verificar antes de generar:
```bash
cd ".../Agent/templates/" && python3 -c "from deta_pdf_base import *; print('✅ Template OK')"
```
