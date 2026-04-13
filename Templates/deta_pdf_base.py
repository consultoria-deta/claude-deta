"""
deta_pdf_base.py
────────────────────────────────────────────────────────
Template base para todos los PDFs de DETA Consultores.
Importar en cualquier script de documento — nunca redefinir
colores, fuentes o estructura de página aquí documentados.

Uso:
    from deta_pdf_base import *
    c, W, H = new_doc("/ruta/output.pdf", "Título del Doc")
    draw_header(c, doc_title="Título del Doc")   # logo se selecciona automáticamente
    draw_footer(c, page_num=1, total_pages=N)
    # ... contenido ...
    c.save()

IMPORTANTE: NO pasar logo_path manualmente. draw_header() selecciona
LOGO_WHITE_PATH o LOGO_PNG_PATH según bg_color. Pasar LOGO_PATH (SVG)
causa UnidentifiedImageError silencioso y cae al fallback de texto.

Dependencias:
    pip install reportlab pillow

Fuentes requeridas (Google Fonts — ya instaladas en el sistema):
    Lora-Italic-Variable.ttf  → Display / Títulos
    Poppins-Regular.ttf       → Body
    Poppins-Bold.ttf          → Labels / énfasis
    Poppins-Light.ttf         → Subtítulos / secundario
    Poppins-Medium.ttf        → Semi-énfasis
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import os
from datetime import datetime

# ─── RUTAS ────────────────────────────────────────────────────────────────────

# Logo oficial — ajusta si cambia la ubicación
LOGO_PATH = (
    "/Users/joelestrada/Library/CloudStorage/"
    "GoogleDrive-consultoria@detaconsultores.com/"
    "Mi unidad/Agent/05_JOEL_OPERACION/Marca/logo-deta-cyan.svg"
)

# PNG oficial para PDFs — 800×327px, RGBA, fondo transparente
# Ruta local (~/.deta/assets/) para que Cowork acceda sin depender de Google Drive montado
# Usar sobre fondos CLAROS (blanco, surface)
LOGO_PNG_PATH = "/Users/joelestrada/.deta/assets/logo-deta-cyan.png"

# PNG blanco — para fondos OSCUROS (navy)
# Nunca usar logo cyan sobre navy ni logo blanco sobre blanco
LOGO_WHITE_PATH = "/Users/joelestrada/.deta/assets/logo-deta-white.png"

# Directorios de fuentes — orden de prioridad: Google Fonts, macOS, Liberation
_FONT_DIRS = [
    "/usr/share/fonts/truetype/google-fonts/",          # Linux (Cloud Run)
    "/System/Library/Fonts/Supplemental/",               # macOS extras
    "/System/Library/Fonts/",                            # macOS sistema
    os.path.expanduser("~/Library/Fonts/"),              # macOS usuario
    "/Library/Fonts/",                                   # macOS global
    "/usr/share/fonts/truetype/liberation/",             # Linux fallback
]

# Mapa de fuentes: nombre DETA → candidatos por prioridad (nombre de archivo)
_FONT_MAP = {
    "Lora-Bold":    ["Lora-Italic-Variable.ttf", "Lora-Bold.ttf",
                     "Georgia Bold.ttf", "LiberationSerif-Bold.ttf"],
    "Poppins":      ["Poppins-Regular.ttf",
                     "Arial.ttf", "LiberationSans-Regular.ttf"],
    "Poppins-Bold": ["Poppins-Bold.ttf",
                     "Arial Bold.ttf", "LiberationSans-Bold.ttf"],
    "Poppins-Lt":   ["Poppins-Light.ttf",
                     "Arial Narrow.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"],
    "Poppins-Md":   ["Poppins-Medium.ttf",
                     "Arial.ttf", "LiberationSans-Regular.ttf"],
}


# ─── REGISTRO DE FUENTES ──────────────────────────────────────────────────────

def _find_font(candidates: list):
    """Busca el primer archivo de fuente disponible en los directorios configurados."""
    for filename in candidates:
        for directory in _FONT_DIRS:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
    return None


def _register_fonts():
    """
    Registra las fuentes DETA buscando en múltiples directorios.
    Funciona en macOS (Arial/Georgia) y Linux/Cloud Run (Poppins/Lora).
    Se llama automáticamente al importar.
    """
    for name, candidates in _FONT_MAP.items():
        path = _find_font(candidates)
        if path:
            pdfmetrics.registerFont(TTFont(name, path))
        else:
            raise FileNotFoundError(
                f"No se encontró ninguna fuente para '{name}'.\n"
                f"Candidatos buscados: {candidates}\n"
                f"Directorios buscados: {_FONT_DIRS}\n"
                "En macOS: instalar Poppins/Lora desde Google Fonts en ~/Library/Fonts/\n"
                "En Linux: sudo apt install fonts-google"
            )

_register_fonts()


# ─── TOKENS DE COLOR ──────────────────────────────────────────────────────────
# Fuente: Manual de Identidad DETA v1.0
# NUNCA usar hex fuera de esta lista en documentos DETA

NAVY        = HexColor("#0c2b40")   # Fondo oscuro, texto principal, header/footer
GOLD        = HexColor("#d3ab6d")   # CTAs, acentos, underlines
CYAN        = HexColor("#12a9cc")   # Íconos, links, elementos interactivos
WHITE       = HexColor("#FFFFFF")   # Canvas principal
SURFACE     = HexColor("#F5F7FA")   # Secciones alternas
DARK_SURFACE= HexColor("#E8ECF0")   # Bordes y separadores sutiles
GRAY_TEXT   = HexColor("#6B7A8D")   # Texto secundario, labels, metadata
LIGHT_NAVY  = HexColor("#0f3852")   # Navy ligeramente más claro (decorativo)

# Fondos que se consideran oscuros — determina qué logo y color de texto usar
FONDOS_OSCUROS = [NAVY, LIGHT_NAVY, HexColor("#081d2a")]


# ─── DIMENSIONES ──────────────────────────────────────────────────────────────

W, H   = A4           # 595.27 × 841.89 pt  (210 × 297 mm)
MARGIN = 18 * mm      # Margen estándar DETA


# ─── FUNCIONES DE PÁGINA ──────────────────────────────────────────────────────

def new_doc(output_path: str, title: str, author: str = "DETA Consultores") -> tuple:
    """
    Crea un nuevo Canvas con metadata DETA.
    Retorna: (canvas, W, H)
    """
    c = rl_canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(title)
    c.setAuthor(author)
    c.setSubject("DETA Consultores — Documento Oficial")
    c.setCreator("DETA PDF System v1.0")
    return c, W, H


def new_page(c):
    """Cierra la página actual e inicia una nueva."""
    c.showPage()


def full_bg(c, color):
    """Rellena toda la página con un color sólido."""
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)


# ─── HEADER ───────────────────────────────────────────────────────────────────

def _is_dark_bg(color) -> bool:
    """True si el color de fondo está en FONDOS_OSCUROS. Determina qué logo y texto usar."""
    return color in FONDOS_OSCUROS


def draw_header(c, logo_path: str = None, doc_title: str = "",
                bg_color=NAVY, height: float = 16 * mm):
    """
    Header estándar DETA:
    - Fondo navy (por defecto) o personalizado
    - Logo blanco sobre fondos oscuros, logo cyan sobre fondos claros
    - Título del documento derecha (opcional)
    - Línea gold inferior

    Selección automática de logo según bg_color:
      NAVY → LOGO_WHITE_PATH   (logo blanco)
      otro → LOGO_PNG_PATH     (logo cyan)
    """
    dark = _is_dark_bg(bg_color)

    # Fondo
    c.setFillColor(bg_color)
    c.rect(0, H - height, W, height, fill=1, stroke=0)

    # Línea gold inferior del header
    c.setFillColor(GOLD)
    c.rect(0, H - height, W, 1.5 * mm, fill=1, stroke=0)

    # Logo — selección automática o override con logo_path
    # NUNCA pasar un SVG como logo_path: ReportLab no lo soporta → falla silencioso
    if logo_path and not logo_path.lower().endswith(".svg"):
        _logo = logo_path
    else:
        _logo = LOGO_WHITE_PATH if dark else LOGO_PNG_PATH

    if _logo and os.path.exists(_logo):
        logo_h = height * 0.55
        logo_w = logo_h * 3.8  # aspect ratio del logo DETA
        logo_y = H - height + (height - logo_h) / 2
        try:
            c.drawImage(_logo, MARGIN, logo_y,
                        width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask="auto")
        except Exception as e:
            import sys
            print(f"[deta_pdf_base] WARN: drawImage falló ({type(e).__name__}: {e}) — usando fallback de texto", file=sys.stderr)
            _draw_text_logo(c, MARGIN, H - height / 2 - 2 * mm, dark=dark)
    else:
        _draw_text_logo(c, MARGIN, H - height / 2 - 2 * mm, dark=dark)

    # Título del documento (derecha)
    if doc_title:
        c.setFont("Poppins-Lt", 7.5)
        title_color = HexColor("#A8BCC8") if dark else GRAY_TEXT
        c.setFillColor(title_color)
        c.drawRightString(W - MARGIN, H - height / 2 - 2.5 * mm, doc_title.upper())


def draw_header_light(c, doc_title: str = "", height: float = 16 * mm):
    """
    Header para documentos con fondo claro (SURFACE o WHITE).
    - Fondo surface (#F5F7FA)
    - Logo cyan (sobre fondo claro)
    - Título en GRAY_TEXT
    - Línea gold inferior
    """
    draw_header(c, doc_title=doc_title, bg_color=SURFACE, height=height)


def _draw_text_logo(c, x, y, dark: bool = True):
    """Fallback de texto si el logo no carga. Adapta color al fondo."""
    c.setFont("Lora-Bold", 11)
    c.setFillColor(WHITE if dark else NAVY)
    c.drawString(x, y, "DETA")
    c.setFont("Poppins-Lt", 8)
    c.setFillColor(GOLD)
    c.drawString(x + 28 * mm, y, "CONSULTORES")


# ─── FOOTER ───────────────────────────────────────────────────────────────────

def draw_footer(c, page_num: int = None, total_pages: int = None,
                label: str = "DETA Consultores",
                height: float = 10 * mm, bg_color=NAVY):
    """
    Footer estándar DETA:
    - Fondo navy
    - "DETA Consultores" + fecha izquierda
    - Número de página derecha
    - Línea gold superior

    IMPORTANTE: total_pages debe calcularse ANTES de iniciar el render.
    Calcularlo durante el render produce resultados incorrectos ("4 / 2").

    Uso correcto:
        total = calcular_paginas(contenido)
        for i in range(total):
            draw_footer(c, page_num=i+1, total_pages=total)
    """
    # Línea gold
    c.setFillColor(GOLD)
    c.rect(0, height, W, 1 * mm, fill=1, stroke=0)

    # Fondo
    c.setFillColor(bg_color)
    c.rect(0, 0, W, height, fill=1, stroke=0)

    # Label izquierda — today_str() garantiza meses en español
    fecha = today_str()
    c.setFont("Poppins", 7)
    c.setFillColor(HexColor("#A8BCC8"))
    c.drawString(MARGIN, height / 2 - 1.5 * mm, f"{label}  ·  {fecha}")

    # Número de página derecha
    if page_num is not None:
        pg_text = f"{page_num}" if total_pages is None else f"{page_num} / {total_pages}"
        c.setFont("Poppins-Bold", 7)
        c.setFillColor(GOLD)
        c.drawRightString(W - MARGIN, height / 2 - 1.5 * mm, pg_text)


# ─── TIPOGRAFÍA — FUNCIONES BASE ──────────────────────────────────────────────

def text_h1(c, text: str, x: float, y: float,
            color=NAVY, size: float = 24):
    """Display / Título principal — Lora Bold"""
    c.setFont("Lora-Bold", size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def text_h2(c, text: str, x: float, y: float,
            color=NAVY, size: float = 16):
    """Subtítulo de sección — Lora Bold"""
    c.setFont("Lora-Bold", size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def text_h3(c, text: str, x: float, y: float,
            color=NAVY, size: float = 11):
    """Etiqueta / sub-sección — Poppins Bold"""
    c.setFont("Poppins-Bold", size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def text_body(c, text: str, x: float, y: float,
              color=NAVY, size: float = 9, font: str = "Poppins"):
    """Texto corrido — Poppins Regular"""
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def text_label(c, text: str, x: float, y: float,
               color=GRAY_TEXT, size: float = 7.5):
    """Metadata / caption — Poppins Light"""
    c.setFont("Poppins-Lt", size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def text_wrap(c, text: str, x: float, y: float,
              max_width: float, font: str = "Poppins",
              size: float = 9, color=NAVY,
              leading: float = 14) -> float:
    """
    Texto con word-wrap manual.
    Retorna la Y final (última línea escrita) para encadenar bloques.
    """
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    cur_y = y
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                c.drawString(x, cur_y, line)
                cur_y -= leading
            line = word
    if line:
        c.drawString(x, cur_y, line)
        cur_y -= leading
    return cur_y


# ─── ELEMENTOS GRÁFICOS ───────────────────────────────────────────────────────

def rule(c, x: float, y: float, width: float,
         color=GOLD, thickness: float = 1):
    """Línea separadora horizontal."""
    c.setStrokeColor(color)
    c.setLineWidth(thickness)
    c.line(x, y, x + width, y)


def section_tag(c, text: str, x: float, y: float,
                bg=CYAN, fg=WHITE, size: float = 6.5):
    """
    Etiqueta de sección con fondo de color.
    Ejemplo: [  HALLAZGOS CLAVE  ]
    """
    c.setFont("Poppins-Bold", size)
    tw = c.stringWidth(text, "Poppins-Bold", size)
    pad = 4 * mm
    c.setFillColor(bg)
    c.rect(x - pad / 2, y - 2 * mm, tw + pad, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(fg)
    c.drawString(x, y + 0.5 * mm, text)


def bullet_item(c, text: str, x: float, y: float,
                max_width: float, dot_color=CYAN,
                font: str = "Poppins", size: float = 9,
                leading: float = 13, text_color=NAVY) -> float:
    """
    Ítem de lista con punto de color.
    Retorna la Y final para encadenar items.

    text_color: color del texto — usar WHITE sobre fondos oscuros.
    """
    # Punto
    c.setFillColor(dot_color)
    c.circle(x + 2 * mm, y + 2.5 * mm, 1.5 * mm, fill=1, stroke=0)
    # Texto
    return text_wrap(c, text, x + 6 * mm, y,
                     max_width - 6 * mm, font, size,
                     text_color, leading)


def callout_box(c, text: str, x: float, y: float,
                width: float, height: float,
                bg=SURFACE, accent=GOLD,
                font: str = "Lora-Bold", size: float = 11):
    """
    Caja de callout con acento lateral gold.
    Usada para hallazgos clave, recomendaciones o citas.
    """
    # Fondo
    c.setFillColor(bg)
    c.rect(x, y - height, width, height, fill=1, stroke=0)
    # Acento izquierdo
    c.setFillColor(accent)
    c.rect(x, y - height, 3 * mm, height, fill=1, stroke=0)
    # Texto
    text_wrap(c, text, x + 6 * mm, y - 6 * mm,
              width - 10 * mm, font, size, NAVY, size * 1.4)


def data_row(c, label: str, value: str,
             x: float, y: float, row_width: float,
             is_alternate: bool = False):
    """
    Fila de datos label | valor para fichas y reportes.
    Alternas con fondo Surface para legibilidad.
    """
    row_h = 8 * mm
    if is_alternate:
        c.setFillColor(SURFACE)
        c.rect(x, y - row_h + 2 * mm, row_width, row_h, fill=1, stroke=0)

    c.setFont("Poppins-Bold", 8)
    c.setFillColor(GRAY_TEXT)
    c.drawString(x + 3 * mm, y, label)

    c.setFont("Poppins", 8.5)
    c.setFillColor(NAVY)
    c.drawString(x + row_width * 0.42, y, value)

    # Línea separadora sutil
    c.setStrokeColor(DARK_SURFACE)
    c.setLineWidth(0.4)
    c.line(x, y - row_h + 2 * mm, x + row_width, y - row_h + 2 * mm)

    return y - row_h  # retorna Y siguiente


# ─── ESTILOS REPORTLAB PLATYPUS ───────────────────────────────────────────────
# Para usar con SimpleDocTemplate + story si se prefiere platypus sobre canvas

def get_paragraph_styles() -> dict:
    """
    Retorna diccionario de estilos Platypus con identidad DETA.
    Uso: styles = get_paragraph_styles()
         story.append(Paragraph("Texto", styles["body"]))
    """
    from reportlab.lib.styles import getSampleStyleSheet
    base = getSampleStyleSheet()

    styles = {
        "h1": ParagraphStyle(
            "DETA_H1", parent=base["Normal"],
            fontName="Lora-Bold", fontSize=22,
            textColor=NAVY, spaceAfter=8 * mm, leading=28,
        ),
        "h2": ParagraphStyle(
            "DETA_H2", parent=base["Normal"],
            fontName="Lora-Bold", fontSize=15,
            textColor=NAVY, spaceAfter=5 * mm, leading=20,
        ),
        "h3": ParagraphStyle(
            "DETA_H3", parent=base["Normal"],
            fontName="Poppins-Bold", fontSize=10,
            textColor=CYAN, spaceAfter=3 * mm, leading=14,
        ),
        "body": ParagraphStyle(
            "DETA_Body", parent=base["Normal"],
            fontName="Poppins", fontSize=9,
            textColor=NAVY, leading=14, spaceAfter=3 * mm,
        ),
        "body_sm": ParagraphStyle(
            "DETA_BodySm", parent=base["Normal"],
            fontName="Poppins", fontSize=8,
            textColor=GRAY_TEXT, leading=12, spaceAfter=2 * mm,
        ),
        "label": ParagraphStyle(
            "DETA_Label", parent=base["Normal"],
            fontName="Poppins-Bold", fontSize=7,
            textColor=GRAY_TEXT, leading=10,
            spaceAfter=1 * mm, spaceBefore=3 * mm,
        ),
        "callout": ParagraphStyle(
            "DETA_Callout", parent=base["Normal"],
            fontName="Lora-Bold", fontSize=11,
            textColor=NAVY, leading=16, spaceAfter=4 * mm,
        ),
    }
    return styles


# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def content_area() -> tuple:
    """
    Retorna (x, y_start, width, height) del área de contenido
    descontando header (16mm) y footer (10mm) y márgenes.
    """
    header_h = 16 * mm
    footer_h = 10 * mm
    x = MARGIN
    y_start = H - header_h - 8 * mm   # 8mm de respiro bajo el header
    content_w = W - 2 * MARGIN
    content_h = H - header_h - footer_h - 16 * mm
    return x, y_start, content_w, content_h


def today_str(fmt: str = "%d de %B de %Y") -> str:
    """Fecha de hoy en español para documentos."""
    meses = {
        "January": "enero", "February": "febrero", "March": "marzo",
        "April": "abril", "May": "mayo", "June": "junio",
        "July": "julio", "August": "agosto", "September": "septiembre",
        "October": "octubre", "November": "noviembre", "December": "diciembre",
    }
    raw = datetime.now().strftime(fmt)
    for en, es in meses.items():
        raw = raw.replace(en, es)
    return raw


def ensure_dir(path: str):
    """Crea el directorio si no existe."""
    os.makedirs(path, exist_ok=True)


# ─── EJEMPLO DE USO ───────────────────────────────────────────────────────────

# if __name__ == "__main__":
#     output = "/tmp/deta_test.pdf"
#     c, W, H = new_doc(output, "Test — DETA Base Template")
#
#     draw_header(c, doc_title="Documento de Prueba")
#     draw_footer(c, page_num=1)
#
#     x, y, col_w, _ = content_area()
#
#     text_h1(c, "Título Principal", x, y)
#     y -= 15 * mm
#     rule(c, x, y, col_w)
#     y -= 8 * mm
#     section_tag(c, "SECCIÓN DE PRUEBA", x, y)
#     y -= 12 * mm
#     y = text_wrap(c,
#         "Este es el texto de cuerpo con word-wrap automático. "
#         "Debe ajustarse al ancho de columna respetando los márgenes DETA.",
#         x, y, col_w, size=9, leading=14)
#     y -= 8 * mm
#     callout_box(c, "Hallazgo clave: El sistema de template funciona.", x, y, col_w, 20 * mm)
#
#     c.save()
#     print(f"✅ Test PDF generado: {output}")
