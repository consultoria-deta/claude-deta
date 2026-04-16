---
name: diagrama-flujo
description: Genera diagramas de flujo con calidad visual profesional (estilo Lucidchart) a partir de procedimientos DETA, transcripciones o minutas. Produce un PNG listo para insertar en el PDF del procedimiento. Actívate con: "hazme el diagrama de flujo", "genera el flowchart", "conviérteme el procedimiento en diagrama", "diagrama de flujo de este proceso", "sácame el PNG del flujo", "flowchart con swimlanes", "dibuja el proceso en carriles", "arma el gráfico del flujo operativo".
---

# Diagrama de Flujo — HTML + Playwright → PNG

Convierte un procedimiento estructurado en un diagrama de flujo con swimlanes por actor,
codificación de color por rol, rombos de decisión y flechas semánticas (verde=Sí, rojo=No).
Produce un PNG listo para inyectar en `deta_pdf_base.py`.

> **Pipeline:** Claude genera JSON → `generar_html_grafo.py` → HTML → `render_playwright.py` → PNG

---

## Cuándo delegar a `procedimiento` primero

Si el input llega como texto crudo (transcripción, minuta, notas), pasar primero por la skill
`procedimiento` para estructurarlo en formato "Rol → Acción → Resultado/Destino".
Solo cuando el texto ya tiene esa estructura, proceder directamente con esta skill.

---

## 1 — Formato de entrada (JSON que genera Claude)

```json
{
  "titulo": "Proceso de Ventas",
  "cliente": "Cliente S.A.",
  "fecha": "2026-04-15",
  "roles": ["Vendedor", "Compras", "Facturación", "Almacén"],
  "nodos": [
    {
      "id": "n01",
      "tipo": "inicio",
      "rol": "Vendedor",
      "texto": "Inicio",
      "fila": 1,
      "conexiones": [{"a": "n02", "tipo": "normal", "etiqueta": null}]
    },
    {
      "id": "n02",
      "tipo": "proceso",
      "rol": "Vendedor",
      "texto": "Recibir solicitud de cotización",
      "fila": 2,
      "conexiones": [{"a": "n03", "tipo": "normal", "etiqueta": null}]
    },
    {
      "id": "n03",
      "tipo": "decision",
      "rol": "Vendedor",
      "texto": "¿Existe en catálogo?",
      "fila": 3,
      "conexiones": [
        {"a": "n04", "tipo": "si",  "etiqueta": "Sí"},
        {"a": "n05", "tipo": "no", "etiqueta": "No"}
      ]
    }
  ]
}
```

### Tipos de nodo

| Tipo | Forma visual | Cuándo usarlo |
|---|---|---|
| `inicio` | Rectángulo redondeado NAVY | Primer nodo del flujo |
| `fin` | Rectángulo redondeado NAVY | Último nodo del flujo |
| `proceso` | Rectángulo con color del rol | Acción ejecutada por el rol |
| `decision` | Rombo amarillo | Pregunta Sí/No (o múltiples salidas) |
| `externo` | Rectángulo gris con borde discontinuo | Referencia a otro procedimiento |

### Tipos de conexión

| Tipo | Color de flecha | Cuándo usarlo |
|---|---|---|
| `si` | Verde (#1E8449) | Salida positiva de un rombo de decisión |
| `no` | Rojo (#C0392B) | Salida negativa de un rombo de decisión |
| `normal` | Gris (#555) | Flujo estándar entre pasos |

---

## 2 — Reglas de layout

**Asignación de filas (`fila`):**
- La primera fila es 1
- Pasos secuenciales incrementan fila en 1
- Cuando una decisión bifurca en Sí/No: la rama principal (Sí) continúa en la misma columna con `fila++`; la rama secundaria (No) salta a la columna de destino con la misma fila o siguiente disponible
- Si dos nodos deben ir en la misma fila (actividades paralelas), asignarles el mismo número de fila

**Columna:** determinada automáticamente por el `rol`. El orden de columnas sigue el array `roles`.

**Feedback loops** (una flecha que sube): el script los maneja con una curva de bypass lateral. Solo asegúrate de que las conexiones estén correctamente definidas en el JSON.

---

## 3 — Edge cases

**Múltiples actores en un paso:** asignar el nodo al actor principal. Agregar "(+ RolSecundario)" al texto del nodo.

**Decisión con >2 salidas:** usar tipo `normal` con etiquetas descriptivas ("Stock completo", "Stock parcial", "Sin stock"). El color será gris neutro automáticamente.

**Texto largo en nodo:** máximo ~50 caracteres por línea. Si el texto excede, dividir en dos líneas con `\n`.

---

## 4 — Pipeline completo

```python
import sys, os

# Path dual para Cowork y Claude Code
for _p in [
    "/mnt",
    os.path.expanduser("~/.claude/skills/diagrama-flujo"),
    "/Users/joelestrada/Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates/skills/diagrama-flujo",
]:
    scripts_path = os.path.join(_p, "scripts")
    if os.path.exists(os.path.join(scripts_path, "generar_html_grafo.py")):
        sys.path.insert(0, scripts_path)
        break

from generar_html_grafo import generar_html
from render_playwright import render_png

# 1. JSON generado por Claude (ver sección 1)
data = { ... }  # tu dict

# 2. Generar HTML
html_path = generar_html(data, "/tmp/diagrama.html")

# 3. Renderizar PNG
png_path = render_png(html_path, "/ruta/output/diagrama_flujo.png")

print(f"Diagrama generado: {png_path}")
```

---

## 5 — Integrar el PNG en el PDF del procedimiento

Si el diagrama va como Sección 9 del procedimiento (`deta_procedimiento_base.py`):

```python
from deta_pdf_base import *

# En la sección de flujo del procedimiento:
section_tag(c, "9. FLUJO DEL PROCESO", x, y)
y -= 10 * mm

# Insertar imagen
c.drawImage(
    png_path,
    x, y - 180 * mm,
    width=col_w,
    height=180 * mm,
    preserveAspectRatio=True,
    mask='auto',
)
```

---

## 6 — Dependencias

```bash
pip install playwright
playwright install chromium
```

Verificar antes de renderizar:
```bash
python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"
```

---

## 7 — Confirmación al terminar

```
✅ Diagrama de flujo generado

  🖼  diagrama_flujo_[Proceso]_[Cliente].png — X KB

Nodos: [N total] (procesos: X, decisiones: X, externos: X)
Roles: [lista de roles]
Feedback loops detectados: [N o "ninguno"]
```
