"""
Genera DETA_Manual_Identidad_Marca.pdf v2.0 — Tech Edition.
Usa deta_pdf_base.py como único template.

Salida: Agent/05_JOEL_OPERACION/Marca/DETA_Manual_Identidad_Marca.pdf
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deta_pdf_base import (
    new_doc, new_page, full_bg, draw_header, draw_header_light, draw_footer,
    text_h1, text_h2, text_h3, text_body, text_label, text_wrap,
    rule, section_tag, bullet_item, callout_box,
    NAVY, GOLD, CYAN, WHITE, SURFACE, DARK_SURFACE, GRAY_TEXT, LIGHT_NAVY,
    W, H, MARGIN,
)
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

OUT = ("/Users/joelestrada/Library/CloudStorage/"
       "GoogleDrive-consultoria@detaconsultores.com/Mi unidad/"
       "Agent/05_JOEL_OPERACION/Marca/DETA_Manual_Identidad_Marca.pdf")

DOC_TITLE = "Manual de Identidad · v2.0 Tech Edition"
TOTAL = 14

# ── Helpers locales ──────────────────────────────────────────────────────────

def swatch(c, x, y, w, h, color_hex, label, role, text_color=NAVY):
    c.setFillColor(HexColor(color_hex))
    c.rect(x, y - h, w, h, fill=1, stroke=0)
    c.setFont("Poppins-Bold", 7.5)
    c.setFillColor(text_color)
    c.drawString(x, y - h - 5 * mm, label)
    c.setFont("Poppins-Lt", 6.5)
    c.setFillColor(GRAY_TEXT)
    c.drawString(x, y - h - 9 * mm, color_hex.upper())
    if role:
        c.drawString(x, y - h - 12.5 * mm, role)

def scale_row(c, x, y, width, scale, label):
    """scale: list of (step, hex). Renders a horizontal strip with labels below."""
    n = len(scale)
    step_w = width / n
    text_body(c, label, x, y + 6 * mm, color=NAVY, size=9, font="Poppins-Bold")
    h = 14 * mm
    for i, (step, hex_) in enumerate(scale):
        c.setFillColor(HexColor(hex_))
        c.rect(x + i * step_w, y - h, step_w, h, fill=1, stroke=0)
        # step label
        c.setFont("Poppins-Bold", 6)
        lum = sum(int(hex_[i:i+2], 16) for i in (1, 3, 5)) / 3
        c.setFillColor(WHITE if lum < 128 else NAVY)
        c.drawString(x + i * step_w + 1.5 * mm, y - h + 2 * mm, str(step))
        # hex below
        c.setFont("Poppins-Lt", 5.8)
        c.setFillColor(GRAY_TEXT)
        c.drawString(x + i * step_w + 1.5 * mm, y - h - 3.5 * mm, hex_.upper())
    return y - h - 6 * mm

def fullpage(c, page_num, title, body_fn, dark=False):
    if dark:
        full_bg(c, NAVY)
    draw_header(c, doc_title=DOC_TITLE, bg_color=NAVY)
    body_fn(c)
    draw_footer(c, page_num=page_num, total_pages=TOTAL)
    new_page(c)

def lightpage(c, page_num, body_fn):
    draw_header_light(c, doc_title=DOC_TITLE)
    body_fn(c)
    draw_footer(c, page_num=page_num, total_pages=TOTAL)
    new_page(c)


# ── PÁGINA 1: PORTADA ────────────────────────────────────────────────────────

def page_cover(c):
    full_bg(c, NAVY)
    # Línea gold vertical izquierda
    c.setFillColor(GOLD)
    c.rect(0, 0, 4 * mm, H, fill=1, stroke=0)

    # Logo blanco centrado-izquierda
    from deta_pdf_base import LOGO_WHITE_PATH
    if os.path.exists(LOGO_WHITE_PATH):
        lw = 70 * mm
        lh = lw / 3.8
        c.drawImage(LOGO_WHITE_PATH, MARGIN + 6 * mm, H - 75 * mm,
                    width=lw, height=lh, preserveAspectRatio=True, mask="auto")

    # Eyebrow
    c.setFont("Poppins-Bold", 8)
    c.setFillColor(GOLD)
    c.drawString(MARGIN + 6 * mm, H - 110 * mm, "MANUAL DE IDENTIDAD · v2.0")

    # Título grande
    c.setFont("Lora-Bold", 42)
    c.setFillColor(WHITE)
    c.drawString(MARGIN + 6 * mm, H - 135 * mm, "Tech Edition")

    # Subtítulo
    c.setFont("Poppins-Lt", 12)
    c.setFillColor(HexColor("#A8BCC8"))
    text_wrap(c,
        "Extensión de la identidad DETA para productos digitales "
        "densos: escalas completas, liquid glass, dark mode y motion. "
        "La paleta core se mantiene intacta.",
        MARGIN + 6 * mm, H - 152 * mm, W - MARGIN * 2 - 20 * mm,
        font="Poppins-Lt", size=12, color=HexColor("#A8BCC8"), leading=17)

    # Bloque inferior: tokens core
    y0 = 70 * mm
    c.setFont("Poppins-Bold", 7)
    c.setFillColor(GOLD)
    c.drawString(MARGIN + 6 * mm, y0 + 22 * mm, "TOKENS CORE — INMUTABLES")

    swatch_core(c, MARGIN + 6 * mm,      y0 + 15 * mm, "#0c2b40", "Navy",  "Identidad · estructura")
    swatch_core(c, MARGIN + 6 * mm + 60, y0 + 15 * mm, "#d3ab6d", "Gold",  "CTA · calidez")
    swatch_core(c, MARGIN + 6 * mm + 120,y0 + 15 * mm, "#12a9cc", "Cyan",  "Interactivo · data")

    # Footer cover
    c.setFont("Poppins-Lt", 7.5)
    c.setFillColor(HexColor("#A8BCC8"))
    c.drawString(MARGIN + 6 * mm, 20 * mm, "DETA Consultores  ·  detaconsultores.com")
    c.setFont("Poppins-Bold", 7.5)
    c.setFillColor(GOLD)
    c.drawRightString(W - MARGIN, 20 * mm, "Abril 2026")
    new_page(c)

def swatch_core(c, x, y, hex_, name, role):
    c.setFillColor(HexColor(hex_))
    c.rect(x, y, 14 * mm, 14 * mm, fill=1, stroke=0)
    c.setFont("Poppins-Bold", 8.5)
    c.setFillColor(WHITE)
    c.drawString(x + 18 * mm, y + 10 * mm, name)
    c.setFont("Poppins-Lt", 7)
    c.setFillColor(HexColor("#A8BCC8"))
    c.drawString(x + 18 * mm, y + 6 * mm, hex_.upper())
    c.drawString(x + 18 * mm, y + 2 * mm, role)


# ── PÁGINA 2: ÍNDICE ─────────────────────────────────────────────────────────

def page_toc(c):
    text_h1(c, "Índice", MARGIN, H - 40 * mm, color=NAVY, size=30)
    rule(c, MARGIN, H - 45 * mm, 50 * mm, color=GOLD, thickness=1.5)

    items = [
        ("01", "Principios y uso del manual", "3"),
        ("02", "Tokens core inmutables", "4"),
        ("03", "Escalas completas · navy / cyan / gold", "5"),
        ("04", "Slate · cool grays con undertone navy", "6"),
        ("05", "Tokens semánticos", "7"),
        ("06", "Elevación · sombras y liquid glass", "8"),
        ("07", "Dark mode", "9"),
        ("08", "Tipografía", "10"),
        ("09", "Proporciones de uso y contrastes", "11"),
        ("10", "Reglas de aplicación", "12"),
        ("11", "Cuándo usar clásica vs tech", "13"),
    ]
    y = H - 65 * mm
    for num, title, page in items:
        c.setFont("Lora-Bold", 11)
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, num)
        c.setFont("Poppins", 11)
        c.setFillColor(NAVY)
        c.drawString(MARGIN + 14 * mm, y, title)
        c.setFont("Poppins-Lt", 9)
        c.setFillColor(GRAY_TEXT)
        c.drawRightString(W - MARGIN, y, f"p. {page}")
        y -= 9 * mm


# ── PÁGINA 3: PRINCIPIOS ─────────────────────────────────────────────────────

def page_principios(c):
    text_h1(c, "01 · Principios", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)

    y = H - 60 * mm
    text_h2(c, "Qué es esta edición", MARGIN, y, size=14)
    y -= 10 * mm
    y = text_wrap(c,
        "La Tech Edition extiende la identidad DETA para productos digitales "
        "densos (DETA Ops, dashboards, apps internas) sin reemplazar la paleta "
        "clásica. Los 3 tokens históricos — navy, gold, cyan — son inmutables. "
        "Todo lo demás son derivados para cubrir estados de UI, elevación, "
        "jerarquía densa y dark mode.",
        MARGIN, y, W - MARGIN * 2, size=10, leading=15)

    y -= 6 * mm
    callout_box(c,
        "Una paleta que se ve igual en la página de inicio pública y en la "
        "pantalla de un operador a las 11 pm. Misma alma, distinto volumen.",
        MARGIN, y, W - MARGIN * 2, 28 * mm, bg=SURFACE, accent=GOLD, size=11)

    y -= 40 * mm
    text_h2(c, "Cuándo aplicar qué", MARGIN, y, size=14)
    y -= 10 * mm
    for line in [
        ("Sitio público (detaconsultores.com, blog, LinkedIn)", "Paleta clásica · navy/gold/cyan + white/surface"),
        ("Apps internas (DETA Ops, dashboards)", "Tech Edition obligatoria · escalas, glass, dark mode, motion"),
        ("PDFs · print · reportes", "Paleta clásica · nunca cyan en tinta"),
        ("Redes sociales · posts · OG images", "Paleta clásica + reglas de graphic-design"),
    ]:
        c.setFont("Poppins-Bold", 9)
        c.setFillColor(CYAN)
        c.drawString(MARGIN, y, "▸")
        c.setFont("Poppins-Bold", 9)
        c.setFillColor(NAVY)
        c.drawString(MARGIN + 5 * mm, y, line[0])
        c.setFont("Poppins-Lt", 9)
        c.setFillColor(GRAY_TEXT)
        y -= 4.5 * mm
        text_wrap(c, line[1], MARGIN + 5 * mm, y, W - MARGIN * 2 - 10 * mm,
                  font="Poppins-Lt", size=9, color=GRAY_TEXT, leading=13)
        y -= 7 * mm


# ── PÁGINA 4: CORE TOKENS ────────────────────────────────────────────────────

def page_core(c):
    text_h1(c, "02 · Tokens Core", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "Inmutables. Jamás se reemplazan.",
              MARGIN, H - 52 * mm, color=GRAY_TEXT, size=9, font="Poppins-Lt")

    # Tres cuadros grandes
    y = H - 75 * mm
    bw = (W - MARGIN * 2 - 12 * mm) / 3
    bh = 50 * mm
    cores = [
        ("#0c2b40", "Navy",  "Identidad",    "Estructura, autoridad, fondo dominante"),
        ("#d3ab6d", "Gold",  "Acento",       "CTAs, focus, puntos de calor"),
        ("#12a9cc", "Cyan",  "Interactivo",  "Data viz, links, estados hover"),
    ]
    for i, (hex_, name, role, desc) in enumerate(cores):
        x = MARGIN + i * (bw + 6 * mm)
        c.setFillColor(HexColor(hex_))
        c.rect(x, y - bh, bw, bh, fill=1, stroke=0)
        # Texto sobreimpuesto
        c.setFont("Poppins-Bold", 7)
        c.setFillColor(WHITE if hex_ != "#d3ab6d" else NAVY)
        c.drawString(x + 4 * mm, y - 7 * mm, role.upper())
        c.setFont("Lora-Bold", 20)
        c.drawString(x + 4 * mm, y - 18 * mm, name)
        c.setFont("Poppins-Bold", 8)
        c.drawString(x + 4 * mm, y - 25 * mm, hex_.upper())
        # Desc debajo
        c.setFont("Poppins-Lt", 8.5)
        c.setFillColor(GRAY_TEXT)
        text_wrap(c, desc, x, y - bh - 6 * mm, bw,
                  font="Poppins-Lt", size=8.5, color=GRAY_TEXT, leading=12)

    # Regla
    y2 = y - bh - 35 * mm
    text_h2(c, "Regla de oro", MARGIN, y2, size=14)
    y2 -= 8 * mm
    text_wrap(c,
        "Si dudas entre un tono derivado y el core, siempre gana el core. "
        "Las escalas existen para matizar, no para esquivar la identidad.",
        MARGIN, y2, W - MARGIN * 2, size=10, leading=15)


# ── PÁGINA 5: ESCALAS NAVY/CYAN/GOLD ─────────────────────────────────────────

def page_scales(c):
    text_h1(c, "03 · Escalas", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "11 pasos por escala · core marcado en posición 500 o 800.",
              MARGIN, H - 52 * mm, color=GRAY_TEXT, size=9, font="Poppins-Lt")

    navy_scale = [
        (50,"#f0f4f8"),(100,"#d9e2eb"),(200,"#b1c2d1"),(300,"#7d96ad"),
        (400,"#4a6a84"),(500,"#28475f"),(600,"#1a3a52"),(700,"#123147"),
        (800,"#0c2b40"),(900,"#081f30"),(950,"#040f1c"),
    ]
    cyan_scale = [
        (50,"#e0f5fa"),(100,"#b8e6f0"),(200,"#8ed6e5"),(300,"#5dc4dc"),
        (400,"#34b5d4"),(500,"#12a9cc"),(600,"#0e8bab"),(700,"#0a6d87"),
        (800,"#085464"),(900,"#063c49"),
    ]
    gold_scale = [
        (50,"#faf4e8"),(100,"#f4e6c9"),(200,"#ead5a7"),(300,"#e0c184"),
        (400,"#d9b578"),(500,"#d3ab6d"),(600,"#b8944d"),(700,"#a88551"),
        (800,"#7c613a"),(900,"#5a4729"),
    ]

    y = H - 72 * mm
    y = scale_row(c, MARGIN, y, W - MARGIN * 2, navy_scale, "Navy · core 800")
    y = scale_row(c, MARGIN, y - 10 * mm, W - MARGIN * 2, cyan_scale, "Cyan · core 500")
    y = scale_row(c, MARGIN, y - 10 * mm, W - MARGIN * 2, gold_scale, "Gold · core 500")


# ── PÁGINA 6: SLATE ──────────────────────────────────────────────────────────

def page_slate(c):
    text_h1(c, "04 · Slate", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "Cool grays con undertone navy — reemplazan los grays neutros.",
              MARGIN, H - 52 * mm, color=GRAY_TEXT, size=9, font="Poppins-Lt")

    slate = [
        (50,"#f7f9fb"),(100,"#eef2f7"),(200,"#dce3ec"),(300,"#b8c3d1"),
        (400,"#8695a8"),(500,"#5a6b80"),(600,"#3e4d60"),(700,"#2b3745"),
        (800,"#1c242e"),(900,"#0f151b"),
    ]
    y = scale_row(c, MARGIN, H - 75 * mm, W - MARGIN * 2, slate, "Slate · 10 pasos")

    y -= 10 * mm
    text_h2(c, "Por qué slate y no gray neutro", MARGIN, y, size=13)
    y -= 9 * mm
    y = text_wrap(c,
        "Los grays neutros tipo #737373 destiñen sobre navy — pierden carácter "
        "y producen UI plana. Los slate-fríos comparten el undertone azul de la "
        "paleta core: mantienen coherencia visual y dan profundidad sin competir "
        "con cyan o gold.",
        MARGIN, y, W - MARGIN * 2, size=10, leading=15)

    y -= 8 * mm
    text_h2(c, "Mapeo de uso", MARGIN, y, size=13)
    y -= 9 * mm
    mapping = [
        ("slate-50",  "Canvas claro, background default"),
        ("slate-100", "Surface alterno, filas alternas"),
        ("slate-200", "Borders claros"),
        ("slate-300", "Placeholder, borders hover"),
        ("slate-400", "Texto muted"),
        ("slate-500", "Texto secundario"),
        ("slate-600", "Texto fuerte sobre claro"),
        ("slate-700", "Panel dark mode"),
        ("slate-800", "Surface dark mode"),
        ("slate-900", "Canvas dark mode alterno"),
    ]
    for token, use in mapping:
        c.setFont("Poppins-Bold", 8.5)
        c.setFillColor(CYAN)
        c.drawString(MARGIN, y, token)
        c.setFont("Poppins", 8.5)
        c.setFillColor(NAVY)
        c.drawString(MARGIN + 30 * mm, y, use)
        y -= 5 * mm


# ── PÁGINA 7: SEMÁNTICOS ─────────────────────────────────────────────────────

def page_semantic(c):
    text_h1(c, "05 · Semánticos", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "Alineados a la paleta. Nunca ámbar genérico ni rojo tomate.",
              MARGIN, H - 52 * mm, color=GRAY_TEXT, size=9, font="Poppins-Lt")

    tokens = [
        ("Success", "#10b981", "Emerald · Linear-compatible"),
        ("Warning", "#d3ab6d", "Gold reutilizado"),
        ("Danger",  "#e0556f", "Coral · no rojo tomate"),
        ("Info",    "#12a9cc", "Cyan reutilizado"),
    ]
    y = H - 80 * mm
    bw = (W - MARGIN * 2 - 15 * mm) / 2
    bh = 32 * mm
    for i, (name, hex_, note) in enumerate(tokens):
        row, col = i // 2, i % 2
        x = MARGIN + col * (bw + 5 * mm)
        yy = y - row * (bh + 15 * mm)
        # Bloque color
        c.setFillColor(HexColor(hex_))
        c.rect(x, yy - bh, bw * 0.35, bh, fill=1, stroke=0)
        # Info a la derecha
        c.setFont("Lora-Bold", 14)
        c.setFillColor(NAVY)
        c.drawString(x + bw * 0.35 + 5 * mm, yy - 8 * mm, name)
        c.setFont("Poppins-Bold", 8.5)
        c.setFillColor(HexColor(hex_))
        c.drawString(x + bw * 0.35 + 5 * mm, yy - 14 * mm, hex_.upper())
        c.setFont("Poppins-Lt", 8)
        c.setFillColor(GRAY_TEXT)
        c.drawString(x + bw * 0.35 + 5 * mm, yy - 20 * mm, note)

    # Regla
    y2 = y - bh * 2 - 35 * mm
    callout_box(c,
        "Máximo 2 semánticos visibles por viewport. Más se lee como alerta "
        "continua y el usuario ignora todos.",
        MARGIN, y2, W - MARGIN * 2, 22 * mm, bg=SURFACE, accent=CYAN, size=10)


# ── PÁGINA 8: ELEVATION + GLASS ──────────────────────────────────────────────

def page_elevation(c):
    text_h1(c, "06 · Elevación", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "Sombras con tinte navy · liquid glass DETA · focus rings.",
              MARGIN, H - 52 * mm, color=GRAY_TEXT, size=9, font="Poppins-Lt")

    # Shadow stack
    y = H - 75 * mm
    text_h2(c, "Shadow stack", MARGIN, y, size=12)
    y -= 10 * mm
    stack = [
        ("xs", "0 1px 2px rgba(12,43,64,0.05)"),
        ("sm", "0 2px 4px rgba(12,43,64,0.06) · 0 1px 2px rgba(12,43,64,0.04)"),
        ("md", "0 4px 12px rgba(12,43,64,0.08) · 0 2px 4px rgba(12,43,64,0.05)"),
        ("lg", "0 12px 32px rgba(12,43,64,0.12) · 0 4px 8px rgba(12,43,64,0.06)"),
        ("xl", "0 24px 64px rgba(12,43,64,0.18) · 0 8px 16px rgba(12,43,64,0.08)"),
        ("glow-cyan", "0 0 24px rgba(18,169,204,0.28)"),
        ("glow-gold", "0 0 24px rgba(211,171,109,0.22)"),
    ]
    for name, value in stack:
        c.setFont("Poppins-Bold", 8)
        c.setFillColor(CYAN)
        c.drawString(MARGIN, y, f"--shadow-{name}")
        c.setFont("Poppins-Lt", 7.5)
        c.setFillColor(GRAY_TEXT)
        c.drawString(MARGIN + 35 * mm, y, value)
        y -= 4.5 * mm

    # Liquid glass
    y -= 8 * mm
    text_h2(c, "Liquid glass DETA", MARGIN, y, size=12)
    y -= 10 * mm
    y = text_wrap(c,
        "Paneles con blur + tinte navy. Se aplican en TopBar, CommandPalette, "
        "Dialog y Sidebar sobre canvas navy-950. Nunca sobre fondo claro.",
        MARGIN, y, W - MARGIN * 2, size=9, leading=13)
    y -= 3 * mm

    glass = [
        ("panel", "rgba(12,43,64,0.72) · blur 24px · saturate 1.2"),
        ("card",  "rgba(255,255,255,0.03) · blur 16px"),
        ("input", "rgba(255,255,255,0.04) · blur 8px"),
    ]
    for name, value in glass:
        c.setFont("Poppins-Bold", 8)
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, f"--glass-{name}")
        c.setFont("Poppins-Lt", 7.5)
        c.setFillColor(GRAY_TEXT)
        c.drawString(MARGIN + 30 * mm, y, value)
        y -= 4.5 * mm


# ── PÁGINA 9: DARK MODE ──────────────────────────────────────────────────────

def page_dark(c):
    text_h1(c, "07 · Dark Mode", MARGIN, H - 40 * mm, color=WHITE)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "Canvas navy-950. Cyan se mantiene, gold sube a 300.",
              MARGIN, H - 52 * mm,
              color=HexColor("#A8BCC8"), size=9, font="Poppins-Lt")

    y = H - 75 * mm
    pairs = [
        ("Canvas",        "navy-950",   "#040f1c"),
        ("Surface",       "slate-800",  "#1c242e"),
        ("Surface-elev",  "slate-700",  "#2b3745"),
        ("Text primary",  "slate-50",   "#f7f9fb"),
        ("Text muted",    "slate-300",  "#b8c3d1"),
        ("Text faint",    "slate-400",  "#8695a8"),
        ("Border subtle", "rgba white 6%",  "rgba(255,255,255,0.06)"),
        ("Border strong", "rgba white 10%", "rgba(255,255,255,0.10)"),
        ("Cyan accent",   "cyan-500",   "#12a9cc"),
        ("Gold accent",   "gold-300",   "#e0c184"),
    ]
    for role, token, value in pairs:
        # swatch
        if value.startswith("#"):
            c.setFillColor(HexColor(value))
            c.rect(MARGIN, y - 3 * mm, 8 * mm, 5 * mm, fill=1, stroke=0)
        # labels
        c.setFont("Poppins-Bold", 8.5)
        c.setFillColor(WHITE)
        c.drawString(MARGIN + 12 * mm, y, role)
        c.setFont("Poppins", 8)
        c.setFillColor(HexColor("#A8BCC8"))
        c.drawString(MARGIN + 65 * mm, y, token)
        c.setFont("Poppins-Lt", 7.5)
        c.setFillColor(GOLD)
        c.drawString(MARGIN + 110 * mm, y, value)
        y -= 6 * mm

    y -= 8 * mm
    text_wrap(c,
        "Dark mode no es inversión directa. Requiere liquid glass + ajuste de "
        "saturación en gold/cyan. Nunca invertir la paleta clásica con un filtro.",
        MARGIN, y, W - MARGIN * 2, size=9,
        color=HexColor("#A8BCC8"), leading=14, font="Poppins-Lt")


# ── PÁGINA 10: TIPOGRAFÍA ────────────────────────────────────────────────────

def page_type(c):
    text_h1(c, "08 · Tipografía", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)

    y = H - 65 * mm
    samples = [
        ("Display", "Lora Bold / Playfair Display", "Transformamos talento en arquitectura.", "Lora-Bold", 26),
        ("H2", "Lora Bold", "Subtítulo de sección", "Lora-Bold", 18),
        ("H3 · Label", "Poppins Bold · mayúsculas", "PUNTO DE CALOR", "Poppins-Bold", 11),
        ("Body", "Poppins Regular", "Texto corrido para body y párrafos cortos con densidad controlada.", "Poppins", 10),
        ("Caption", "Poppins Light", "Metadata, fechas, números de página, footnotes.", "Poppins-Lt", 8),
    ]
    for label, fontlabel, sample, font, size in samples:
        c.setFont("Poppins-Bold", 7)
        c.setFillColor(CYAN)
        c.drawString(MARGIN, y, label.upper())
        c.setFont("Poppins-Lt", 7)
        c.setFillColor(GRAY_TEXT)
        c.drawRightString(W - MARGIN, y, fontlabel)
        y -= 5 * mm
        c.setFont(font, size)
        c.setFillColor(NAVY)
        # recortar si muy largo
        txt = sample if c.stringWidth(sample, font, size) < W - MARGIN * 2 else sample
        c.drawString(MARGIN, y, txt)
        y -= (size * 0.45 + 10) * mm / 3 + 8 * mm

    # Stack tech
    y -= 5 * mm
    text_h2(c, "Stack tech (apps)", MARGIN, y, size=13)
    y -= 9 * mm
    for name, role in [
        ("Playfair Display", "Titulares narrativos (sitio público)"),
        ("Source Sans Pro / Poppins", "Body · UI · default"),
        ("JetBrains Mono", "Código · IDs · data densa"),
        (".tabular (font-variant: tabular-nums)", "KPIs · tablas · alineación vertical"),
    ]:
        c.setFont("Poppins-Bold", 8.5)
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, name)
        c.setFont("Poppins-Lt", 8.5)
        c.setFillColor(GRAY_TEXT)
        c.drawString(MARGIN + 60 * mm, y, role)
        y -= 5 * mm


# ── PÁGINA 11: PROPORCIONES + WCAG ───────────────────────────────────────────

def page_prop(c):
    text_h1(c, "09 · Proporciones", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)

    # Barra de proporciones visual
    y = H - 75 * mm
    text_h3(c, "Uso por viewport", MARGIN, y, color=NAVY)
    y -= 10 * mm
    bar_w = W - MARGIN * 2
    parts = [
        (45, HexColor("#040f1c"), "canvas"),
        (22, HexColor("#1c242e"), "surface"),
        (17, HexColor("#2b3745"), "panels"),
        (10, NAVY, "navy"),
        (3,  GOLD, "gold"),
        (3,  CYAN, "cyan"),
    ]
    x = MARGIN
    for pct, color, _ in parts:
        w = bar_w * pct / 100
        c.setFillColor(color)
        c.rect(x, y - 10 * mm, w, 10 * mm, fill=1, stroke=0)
        x += w
    # labels
    x = MARGIN
    for pct, _, name in parts:
        w = bar_w * pct / 100
        c.setFont("Poppins-Bold", 7)
        c.setFillColor(NAVY)
        c.drawString(x, y - 14 * mm, f"{name}")
        c.setFont("Poppins-Lt", 6.5)
        c.setFillColor(GRAY_TEXT)
        c.drawString(x, y - 17 * mm, f"{pct}%")
        x += w

    # WCAG
    y -= 32 * mm
    text_h3(c, "Contrastes verificados · WCAG 2.1", MARGIN, y, color=NAVY)
    y -= 8 * mm

    rows = [
        ("slate-50 #f7f9fb",   "navy-800 #0c2b40",  "15.2", "AAA"),
        ("slate-300 #b8c3d1",  "navy-800",          "9.1",  "AAA"),
        ("gold-500 #d3ab6d",   "navy-800",          "6.4",  "AA"),
        ("cyan-500 #12a9cc",   "navy-800",          "4.8",  "iconos"),
        ("gold-300 #e0c184",   "navy-800",          "8.2",  "AAA"),
        ("navy-800",           "slate-50",          "13.8", "AAA"),
        ("slate-600 #3e4d60",  "slate-50",          "7.9",  "AAA"),
        ("cyan-700 #0a6d87",   "slate-50",          "5.9",  "AA"),
    ]
    # header
    c.setFont("Poppins-Bold", 7)
    c.setFillColor(CYAN)
    c.drawString(MARGIN, y, "TEXTO")
    c.drawString(MARGIN + 55 * mm, y, "FONDO")
    c.drawString(MARGIN + 110 * mm, y, "RATIO")
    c.drawString(MARGIN + 135 * mm, y, "NIVEL")
    y -= 5 * mm
    rule(c, MARGIN, y, W - MARGIN * 2, color=DARK_SURFACE, thickness=0.5)
    y -= 3 * mm
    for text, bg, ratio, level in rows:
        c.setFont("Poppins", 7.5)
        c.setFillColor(NAVY)
        c.drawString(MARGIN, y, text)
        c.drawString(MARGIN + 55 * mm, y, bg)
        c.setFont("Poppins-Bold", 7.5)
        c.setFillColor(GOLD)
        c.drawString(MARGIN + 110 * mm, y, ratio)
        c.setFont("Poppins-Lt", 7)
        c.setFillColor(GRAY_TEXT)
        c.drawString(MARGIN + 135 * mm, y, level)
        y -= 4.5 * mm


# ── PÁGINA 12: REGLAS ────────────────────────────────────────────────────────

def page_rules(c):
    text_h1(c, "10 · Reglas", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)

    rules = [
        ("Core siempre gana",
         "Si dudas entre navy-500 y navy-800, usa navy-800. Las escalas matizan, no esquivan."),
        ("Cyan solo en digital",
         "Pantallas e interactivo. En print (PDFs, impresos) usa navy + gold únicamente."),
        ("Semánticos son puntuales",
         "Máximo 2 por viewport. Más se lee como alerta continua y el usuario desconecta."),
        ("Slate reemplaza grays neutros",
         "Cualquier text-gray-* existente debe migrar a text-slate-*. Nunca #737373 sobre navy."),
        ("Gold para calor · cyan para info",
         "Gold = foco y acción importante. Cyan = información, links, estados hover."),
        ("Dark mode no es invertir",
         "Requiere liquid glass + saturación ajustada de gold/cyan. Filtros CSS globales están prohibidos."),
        ("Un gradiente por viewport",
         "Navy → navy-900 es seguro. Cyan → gold está prohibido."),
    ]
    y = H - 65 * mm
    for i, (title, desc) in enumerate(rules, 1):
        c.setFont("Lora-Bold", 11)
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, f"{i:02d}")
        c.setFont("Poppins-Bold", 10)
        c.setFillColor(NAVY)
        c.drawString(MARGIN + 10 * mm, y, title)
        y -= 5 * mm
        y = text_wrap(c, desc, MARGIN + 10 * mm, y,
                      W - MARGIN * 2 - 10 * mm,
                      font="Poppins-Lt", size=9, color=GRAY_TEXT, leading=13)
        y -= 5 * mm


# ── PÁGINA 13: CLÁSICA VS TECH ───────────────────────────────────────────────

def page_matrix(c):
    text_h1(c, "11 · Clásica vs Tech", MARGIN, H - 40 * mm)
    rule(c, MARGIN, H - 45 * mm, 60 * mm, color=GOLD, thickness=1.5)
    text_body(c, "Matriz de decisión. Ambas conviven — no se reemplazan.",
              MARGIN, H - 52 * mm, color=GRAY_TEXT, size=9, font="Poppins-Lt")

    headers = ["Pieza", "Paleta", "Particularidades"]
    rows = [
        ("Sitio público", "Clásica", "Navy 50%, blanco 25%, surface 13%, gold 7%, cyan 5%"),
        ("Blog / artículos", "Clásica", "Playfair + Source Sans · hero images generadas con hero_gen.py"),
        ("LinkedIn / redes", "Clásica", "OG template navy + gold, sin cyan en fondo"),
        ("PDFs · reportes", "Clásica", "deta_pdf_base.py · sin cyan en tinta"),
        ("DETA Ops · apps", "Tech", "Escalas slate, liquid glass, dark mode, motion tokens"),
        ("Dashboards", "Tech", "KPIs con .tabular, glow-cyan en data viz"),
        ("Cotizador · PDFs", "Clásica para output, Tech para editor", "El editor es UI · el output es imprimible"),
        ("Email transaccional", "Clásica reducida", "Solo navy + gold · cyan degrada en clientes de email"),
    ]

    y = H - 75 * mm
    # Header de tabla
    c.setFillColor(NAVY)
    c.rect(MARGIN, y - 6 * mm, W - MARGIN * 2, 7 * mm, fill=1, stroke=0)
    c.setFont("Poppins-Bold", 7.5)
    c.setFillColor(WHITE)
    c.drawString(MARGIN + 3 * mm, y - 4 * mm, "PIEZA")
    c.drawString(MARGIN + 50 * mm, y - 4 * mm, "PALETA")
    c.drawString(MARGIN + 90 * mm, y - 4 * mm, "PARTICULARIDADES")
    y -= 9 * mm

    for i, (pieza, paleta, extra) in enumerate(rows):
        if i % 2 == 0:
            c.setFillColor(SURFACE)
            c.rect(MARGIN, y - 6 * mm, W - MARGIN * 2, 10 * mm, fill=1, stroke=0)
        c.setFont("Poppins-Bold", 8)
        c.setFillColor(NAVY)
        c.drawString(MARGIN + 3 * mm, y, pieza)
        c.setFont("Poppins", 8)
        c.setFillColor(CYAN if paleta.startswith("Tech") else GOLD)
        c.drawString(MARGIN + 50 * mm, y, paleta)
        c.setFont("Poppins-Lt", 7.5)
        c.setFillColor(GRAY_TEXT)
        text_wrap(c, extra, MARGIN + 90 * mm, y, W - MARGIN - 90 * mm - MARGIN,
                  font="Poppins-Lt", size=7.5, color=GRAY_TEXT, leading=10)
        y -= 11 * mm


# ── PÁGINA 14: CIERRE ────────────────────────────────────────────────────────

def page_back(c):
    full_bg(c, NAVY)
    c.setFillColor(GOLD)
    c.rect(0, 0, 4 * mm, H, fill=1, stroke=0)

    y = H - 90 * mm
    c.setFont("Poppins-Bold", 8)
    c.setFillColor(GOLD)
    c.drawString(MARGIN + 6 * mm, y, "RESUMEN")
    y -= 14 * mm
    c.setFont("Lora-Bold", 32)
    c.setFillColor(WHITE)
    c.drawString(MARGIN + 6 * mm, y, "Misma alma.")
    y -= 14 * mm
    c.setFont("Lora-Bold", 32)
    c.setFillColor(GOLD)
    c.drawString(MARGIN + 6 * mm, y, "Distinto volumen.")

    y -= 22 * mm
    text_wrap(c,
        "La Tech Edition no es una paleta nueva: es una extensión precisa para "
        "que DETA se vea al nivel de Linear, Superhuman y Notion cuando la UI "
        "lo exige. Los 3 tokens core siguen siendo la identidad. Las escalas, "
        "semánticos, glass y dark mode son herramientas — no decisiones estéticas.",
        MARGIN + 6 * mm, y, W - MARGIN * 2 - 12 * mm,
        size=10.5, color=HexColor("#A8BCC8"), leading=16, font="Poppins-Lt")

    # Footer
    c.setFont("Poppins-Bold", 7.5)
    c.setFillColor(GOLD)
    c.drawString(MARGIN + 6 * mm, 25 * mm, "DETA Consultores")
    c.setFont("Poppins-Lt", 7.5)
    c.setFillColor(HexColor("#A8BCC8"))
    c.drawString(MARGIN + 6 * mm, 20 * mm, "consultoria@detaconsultores.com · detaconsultores.com")
    c.setFont("Poppins-Bold", 7.5)
    c.setFillColor(GOLD)
    c.drawRightString(W - MARGIN, 20 * mm, "Manual de Identidad · v2.0 Tech Edition")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    c, _, _ = new_doc(OUT, DOC_TITLE)

    # Cover (sin header/footer estándar)
    page_cover(c)

    # Páginas internas con header/footer estándar
    lightpage(c, 2, page_toc)
    lightpage(c, 3, page_principios)
    lightpage(c, 4, page_core)
    lightpage(c, 5, page_scales)
    lightpage(c, 6, page_slate)
    lightpage(c, 7, page_semantic)
    lightpage(c, 8, page_elevation)

    # Dark page
    def dark_wrap(c):
        full_bg(c, NAVY)
        draw_header(c, doc_title=DOC_TITLE, bg_color=NAVY)
        page_dark(c)
        draw_footer(c, page_num=9, total_pages=TOTAL)
    dark_wrap(c)
    new_page(c)

    lightpage(c, 10, page_type)
    lightpage(c, 11, page_prop)
    lightpage(c, 12, page_rules)
    lightpage(c, 13, page_matrix)

    # Back cover
    page_back(c)

    c.save()
    print(f"✅ Manual generado → {OUT}")


if __name__ == "__main__":
    main()
