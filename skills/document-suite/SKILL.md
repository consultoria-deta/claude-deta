---
name: document-suite
description: Producción, procesamiento y análisis de documentos: Word (.docx), PDF, Excel (.xlsx) y Google Sheets. Actívate con cualquier mención de: documento, Word, docx, PDF, Excel, xlsx, hoja de cálculo, Sheets, spreadsheet, reporte, informe, propuesta, contrato, minuta, presentación de datos, tabla, exportar, guardar documento, generar reporte, analizar archivo, leer Excel, procesar PDF, crear Word. También actívate cuando el usuario comparta un archivo de cualquiera de estos tipos o pida que algo "quede en un documento".
---

# Document Suite — Producción y Procesamiento de Documentos

Flujo unificado para trabajar con Word, PDF, Excel y Google Sheets. Desde análisis hasta generación de entregables formales.

---

## Dispatch — ¿Qué necesitas hacer?

| Tarea | Herramienta | Sección |
|---|---|---|
| Crear documento Word para cliente | python-docx | → DOCX |
| Generar PDF ejecutivo | ReportLab | → PDF |
| Analizar Excel / crear reporte | openpyxl + pandas | → Excel |
| Leer datos de Google Sheets | gspread | → Sheets |
| Procesar PDF recibido | pdftotext / pypdf | → Leer PDF |
| Exportar a múltiples formatos | Pipeline combinado | → Multi-formato |

### Plantilla por tipo de entregable

| Entregable | Formato | Razón |
|---|---|---|
| Propuesta comercial | PDF | No editable, diseño DETA completo |
| Perfil de puesto | DOCX | El cliente necesita editar |
| Contrato / convenio | DOCX | Requiere firma y edición |
| Reporte de avance | PDF | Presentación ejecutiva |
| Diagnóstico organizacional | PDF | Entregable formal |
| Minuta de reunión | DOCX | El cliente lleva seguimiento |
| Base de datos / tracker | XLSX | Datos que se analizan |
| Plantilla de evaluación | XLSX | El cliente la opera |

---

## DOCX — Documentos Word

### Cuándo usar
- Entregables formales para cliente (propuestas, procedimientos, perfiles de puesto)
- Documentos que el cliente necesita editar
- Solo guardar cuando Joel aprueba explícitamente el contenido

### Flujo
1. Generar contenido en texto primero — Joel aprueba
2. Convertir a DOCX con python-docx
3. Guardar en ruta oficial OpenClaw o entregar como descarga

```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Estilo DETA — colores navy y gold
NAVY = RGBColor(0x0c, 0x2b, 0x40)
GOLD = RGBColor(0xd3, 0xab, 0x6d)

# Título principal
title = doc.add_heading('Título del Documento', 0)
title.runs[0].font.color.rgb = NAVY

# Sección
doc.add_heading('1. Nombre de la Sección', level=1)

# Párrafo body
p = doc.add_paragraph('Contenido del párrafo aquí.')
p.style.font.size = Pt(11)

# Tabla
table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'
header_cells = table.rows[0].cells
header_cells[0].text = 'Columna 1'
header_cells[1].text = 'Columna 2'
header_cells[2].text = 'Columna 3'

# Guardar
doc.save('/tmp/entregable.docx')
```

### Restricciones de guardado
- Solo guardar con aprobación explícita de Joel
- Ruta base: `/Users/joelestrada/Library/CloudStorage/GoogleDrive-.../OpenClaw/`
- No sobrescribir — si existe, proponer v2
- Nunca afirmar que se guardó sin haberlo ejecutado

---

## PDF — Generación Ejecutiva

### Cuándo usar
- Reportes ejecutivos con diseño DETA
- Documentos que NO deben editarse
- Minutas formales, propuestas finales

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.units import pt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Fuentes oficiales DETA
FONT_DIR = "/usr/share/fonts/truetype/google-fonts/"
pdfmetrics.registerFont(TTFont("Lora-Bold", FONT_DIR + "Lora-Italic-Variable.ttf"))
pdfmetrics.registerFont(TTFont("Poppins",   FONT_DIR + "Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Bold", FONT_DIR + "Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Lt",   FONT_DIR + "Poppins-Light.ttf"))

# Uso: display/títulos → "Lora-Bold" | body/UI → "Poppins" o "Poppins-Bold"

# Colores DETA
NAVY = HexColor('#0c2b40')
GOLD = HexColor('#d3ab6d')
CYAN = HexColor('#12a9cc')
GRAY = HexColor('#646478')

# Configuración de página (Carta)
doc = SimpleDocTemplate(
    '/tmp/reporte.pdf',
    pagesize=letter,
    leftMargin=30*pt, rightMargin=30*pt,
    topMargin=30*pt, bottomMargin=50*pt
)

styles = getSampleStyleSheet()

# Estilo título
title_style = ParagraphStyle(
    'DETATitle',
    parent=styles['Normal'],
    fontSize=18,
    fontName='Lora-Bold',
    textColor=NAVY,
    spaceAfter=8*pt,
)

# Estilo body
body_style = ParagraphStyle(
    'DETABody',
    parent=styles['Normal'],
    fontSize=9,
    fontName='Poppins',
    textColor=HexColor('#1e1a2e'),
    leading=12,
)

content = []
content.append(Paragraph('Título del Reporte', title_style))
content.append(Spacer(1, 12*pt))
content.append(Paragraph('Contenido del reporte...', body_style))

# Tabla
data = [['Columna 1', 'Columna 2', 'Columna 3']]
data.append(['Dato 1', 'Dato 2', 'Dato 3'])

table = Table(data, colWidths=[184*pt, 184*pt, 184*pt])
content.append(table)

doc.build(content)
```

### Leer PDF recibido
```python
import subprocess

# Extraer texto
result = subprocess.run(
    ['pdftotext', '-layout', '/path/to/file.pdf', '-'],
    capture_output=True, text=True
)
text = result.stdout

# Si pdftotext no está disponible, usar pypdf
from pypdf import PdfReader
reader = PdfReader('/path/to/file.pdf')
text = '\n'.join(page.extract_text() for page in reader.pages)
print(text[:3000])  # preview
```

---

## Excel — Análisis y Creación

### Leer Excel existente
```python
from openpyxl import load_workbook

# Siempre read_only=True para archivos grandes
wb = load_workbook('/path/to/file.xlsx', read_only=True)
print('Hojas:', wb.sheetnames)

ws = wb.active
# Preview primeras 5 filas
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i >= 5: break
    print(row)

wb.close()
```

### Crear Excel nuevo con datos
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = 'Reporte'

# Colores DETA
NAVY_FILL = PatternFill(start_color='0c2b40', end_color='0c2b40', fill_type='solid')
GOLD_FILL = PatternFill(start_color='d3ab6d', end_color='d3ab6d', fill_type='solid')
LIGHT_FILL = PatternFill(start_color='F5F7FA', end_color='F5F7FA', fill_type='solid')

# Header row con estilo
headers = ['Nombre', 'Valor', 'Status', 'Fecha']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color='FFFFFF')
    cell.fill = NAVY_FILL
    cell.alignment = Alignment(horizontal='center')

# Datos
data = [
    ['Proyecto Alpha', 45000, 'Activo', '2025-01-15'],
    ['Proyecto Beta', 32000, 'En revisión', '2025-02-01'],
]

for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        if row_idx % 2 == 0:
            cell.fill = LIGHT_FILL

# Ajustar ancho de columnas
for col in ws.columns:
    max_length = max(len(str(cell.value or '')) for cell in col)
    ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 4

wb.save('/tmp/reporte.xlsx')
print('Excel guardado en /tmp/reporte.xlsx')
```

### Analizar datos con pandas
```python
import pandas as pd

df = pd.read_excel('/path/to/file.xlsx', engine='openpyxl')
print(df.shape)           # (filas, columnas)
print(df.dtypes)          # tipos de datos
print(df.describe())      # estadísticas básicas
print(df.isnull().sum())  # valores vacíos por columna
```

---

## Google Sheets — Leer y Escribir

```python
import gspread
from google.oauth2.service_account import Credentials

# Auth con service account
creds = Credentials.from_service_account_file(
    '~/.openclaw/gws-credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
client = gspread.authorize(creds)

# Abrir por URL o nombre
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/xxx')
ws = sheet.worksheet('Hoja1')

# Leer todos los datos
data = ws.get_all_records()  # lista de dicts con headers como keys
print(f"{len(data)} filas")

# Leer rango específico
values = ws.get('A1:D10')

# Escribir datos
ws.update('A1', [['Header 1', 'Header 2'], ['dato1', 'dato2']])

# Append fila
ws.append_row(['nuevo', 'dato', '2025-01-15'])
```

---

## Pipeline Multi-Formato

Para cuando se necesita entregar el mismo contenido en múltiples formatos:

```python
# 1. Generar datos/contenido en Python
content = {
    'titulo': 'Reporte Q1 2025',
    'resumen': 'Los resultados del trimestre...',
    'tabla': [['Métrica', 'Valor'], ['Ventas', '$45,000']],
}

# 2. Excel — para datos que se analizarán
generar_excel(content, '/tmp/reporte-q1.xlsx')

# 3. PDF — para presentación ejecutiva
generar_pdf(content, '/tmp/reporte-q1.pdf')

# 4. DOCX — para el cliente que necesita editar
generar_docx(content, '/tmp/reporte-q1.docx')
```

---

## Reglas de Entrega

1. **Aprobar contenido antes de generar archivo** — nunca crear el archivo directamente
2. **Confirmar ruta de guardado** — preguntar dónde quiere el usuario el archivo
3. **Verificar que el archivo existe** antes de decir "guardado"
4. **No sobrescribir** — si ya existe, proponer nombre con fecha o v2
5. **PDF = no editable** — si el cliente necesita editar, usar DOCX
6. **Colores DETA** — todo documento mantiene la identidad visual
