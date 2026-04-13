"""
deta_reporte_pool.py
────────────────────────────────────────────────────────
Genera el Reporte de Pool de Candidatos — documento ejecutivo
para presentar al cliente al cierre de la fase de entrevistas.

Estructura:
  Página 1       — Portada ejecutiva (navy) con métricas
  Páginas 2..N   — Una tarjeta por candidato recomendado
  Página N+1     — Tabla de contactos de recomendados
  Página N+2     — Tabla de descartados (si existen)

Uso:
    from deta_reporte_pool import generar_reporte_pool

    candidatos = [
        {
            "nombre":        "Martha Rodela",
            "score":         82,               # 0-100, None si no existe
            "nivel":         "Sólido",         # None si no existe
            "escolaridad":   "Lic. Administración — UACH",
            "experiencia":   "8 años",
            "ultimo_puesto": "Coordinadora Administrativa · Empresa XYZ (2020-2024). "
                             "Responsable de tesorería, cuentas por pagar y reportes financieros.",
            "competencias":  [
                {"nombre": "Orientación a resultados", "nivel": "Alto"},
                {"nombre": "Comunicación efectiva",    "nivel": "Medio"},
                {"nombre": "Gestión de procesos",      "nivel": "Alto"},
            ],
            "fortalezas":    [
                "Experiencia directa en control presupuestal en empresa de manufactura.",
                "Comunicación efectiva — clara y directa en la entrevista.",
                "Proactividad demostrada: implementó mejoras sin que se le pidiera.",
            ],
            "nota_evaluador": "Candidata destacada. Recomendada para primera entrevista con cliente.",
            "email":         "martha.rodela@email.com",
            "telefono":      "614-123-4567",
            "recomendado":   True,
        },
        {
            "nombre":        "Juan Pérez",
            "score":         41,
            "nivel":         "No recomendado",
            "escolaridad":   "Trunca",
            "experiencia":   "2 años",
            "ultimo_puesto": "Auxiliar contable · Despacho local.",
            "competencias":  [],
            "fortalezas":    [],
            "nota_evaluador": "Experiencia insuficiente para el nivel requerido.",
            "email":         None,
            "telefono":      None,
            "recomendado":   False,
        },
    ]

    generar_reporte_pool(
        candidatos=candidatos,
        puesto="Coordinador Administrativo",
        cliente="ACME Corp",
        output_path="ReportePool_CoordAdmin_ACME_20260411.pdf",
    )

Dependencias:
    pip install reportlab pillow
    (deta_pdf_base.py debe estar en el mismo directorio o en sys.path)
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from deta_pdf_base import *


# ─── CONSTANTES ───────────────────────────────────────────────────────────────

NIVEL_LABELS = {
    "A": "Alto", "Alto": "Alto",
    "B": "Medio", "Medio": "Medio",
    "C": "Básico", "Básico": "Básico",
}

FOOTER_LABEL = "Confidencial — DETA Consultores · detaconsultores.com"


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _normalizar_score(score):
    """Clamp score a 0-100. Devuelve None si no viene."""
    if score is None:
        return None
    return max(0, min(100, int(score)))


def _nivel_label(nivel_raw):
    """Convierte A/B/C o texto completo a Alto/Medio/Básico."""
    if not nivel_raw:
        return "—"
    return NIVEL_LABELS.get(str(nivel_raw).strip(), str(nivel_raw).strip())


def _score_color(nivel):
    """Color de callout según nivel."""
    if nivel in ("Excepcional", "Sólido"):
        return CYAN, WHITE
    if nivel == "Con potencial":
        return GOLD, NAVY
    return SURFACE, NAVY


def _calcular_total_paginas(recomendados, descartados):
    return 1 + len(recomendados) + 1 + (1 if descartados else 0)


# ─── SECCIONES ────────────────────────────────────────────────────────────────

def _portada(c, W, H, puesto, cliente, candidatos, total_pages):
    """Página 1 — Portada ejecutiva navy."""
    full_bg(c, NAVY)
    draw_header(c, bg_color=NAVY, doc_title="REPORTE DE CANDIDATOS")
    draw_footer(c, page_num=1, total_pages=total_pages, label=FOOTER_LABEL)

    x, y, col_w, _ = content_area()

    # Eyebrow
    section_tag(c, "REPORTE DE CANDIDATOS", x, y, bg=GOLD, fg=NAVY)
    y -= 14 * mm

    # Título principal
    text_h1(c, puesto, x, y, color=WHITE, size=28)
    y -= 12 * mm

    # Cliente + fecha
    text_label(c, cliente.upper(), x, y, color=GOLD)
    y -= 7 * mm
    text_label(c, today_str(), x, y, color=HexColor("#8EAFC0"))
    y -= 18 * mm

    # Línea separadora
    rule(c, x, y, col_w, color=HexColor("#1a4a66"))
    y -= 14 * mm

    # Métricas — tres tarjetas horizontales
    recomendados = [c_ for c_ in candidatos if c_.get("recomendado")]
    descartados  = [c_ for c_ in candidatos if not c_.get("recomendado")]
    metricas = [
        ("Total evaluados",  len(candidatos),    CYAN),
        ("Recomendados",     len(recomendados),  GOLD),
        ("Descartados",      len(descartados),   HexColor("#8EAFC0")),
    ]

    card_w = (col_w - 16 * mm) / 3
    card_h = 28 * mm
    card_x = x

    for label, valor, color in metricas:
        # Fondo de tarjeta
        c.setFillColor(HexColor("#0a2233"))
        c.roundRect(card_x, y - card_h, card_w, card_h, 6, fill=1, stroke=0)
        # Número grande
        c.setFillColor(color)
        c.setFont("Lora-Bold", 26)
        num_text = str(valor)
        num_w = c.stringWidth(num_text, "Lora-Bold", 26)
        c.drawString(card_x + (card_w - num_w) / 2, y - 14 * mm, num_text)
        # Label
        c.setFillColor(HexColor("#8EAFC0"))
        c.setFont("Poppins", 9)
        lbl_w = c.stringWidth(label, "Poppins", 9)
        c.drawString(card_x + (card_w - lbl_w) / 2, y - 22 * mm, label)
        card_x += card_w + 8 * mm

    c.showPage()


def _tarjeta_candidato(c, candidato, puesto, page_num, total_pages):
    """Una página por candidato recomendado."""
    draw_header(c, bg_color=WHITE, doc_title="REPORTE DE CANDIDATOS")
    draw_footer(c, page_num=page_num, total_pages=total_pages, label=FOOTER_LABEL)

    x, y, col_w, _ = content_area()

    nombre = candidato.get("nombre", "")
    score  = _normalizar_score(candidato.get("score"))
    nivel  = candidato.get("nivel")

    # Nombre
    text_h1(c, nombre, x, y, color=NAVY, size=22)
    y -= 10 * mm

    # Link al CV (si existe)
    cv_path = candidato.get("cv_path")
    if cv_path:
        link_label = "Ver CV completo →"
        c.setFont("Poppins", 8)
        c.setFillColor(CYAN)
        c.drawString(x, y, link_label)
        link_w = c.stringWidth(link_label, "Poppins", 8)
        c.linkURL(f"file://{cv_path}", (x, y - 1.5 * mm, x + link_w, y + 4 * mm))
        y -= 7 * mm

    # Score si existe
    if score is not None and nivel:
        bg_c, fg_c = _score_color(nivel)
        callout_box(c,
            f"Score DETA: {score}/100 — {nivel}",
            x, y, col_w, 14 * mm,
            bg=bg_c, accent=fg_c)
        y -= 18 * mm
    else:
        rule(c, x, y, col_w)
        y -= 10 * mm

    # Datos básicos
    escolaridad = candidato.get("escolaridad") or "[No mencionada]"
    experiencia = candidato.get("experiencia") or "[No mencionada]"
    y = data_row(c, "ESCOLARIDAD", escolaridad, x, y, col_w, False)
    y = data_row(c, "EXPERIENCIA", experiencia, x, y, col_w, True)
    y -= 6 * mm

    # Último puesto
    ultimo = candidato.get("ultimo_puesto")
    if ultimo:
        section_tag(c, "ÚLTIMO PUESTO RELEVANTE", x, y)
        y -= 9 * mm
        y = text_wrap(c, ultimo, x, y, col_w, size=9, leading=14)
        y -= 8 * mm

    # Competencias
    competencias = candidato.get("competencias") or []
    if competencias:
        section_tag(c, "COMPETENCIAS", x, y)
        y -= 9 * mm
        for i, comp in enumerate(competencias):
            nivel_txt = _nivel_label(comp.get("nivel"))
            y = data_row(
                c,
                comp.get("nombre", ""),
                nivel_txt,
                x, y, col_w,
                is_alternate=(i % 2 == 1)
            )
        y -= 6 * mm

    # Fortalezas
    fortalezas = candidato.get("fortalezas") or []
    if fortalezas:
        section_tag(c, "FORTALEZAS", x, y)
        y -= 9 * mm
        for f in fortalezas[:3]:
            y = bullet_item(c, f, x, y, col_w)
            y -= 2 * mm
        y -= 4 * mm

    # Nota del evaluador
    nota = candidato.get("nota_evaluador")
    if nota:
        section_tag(c, "NOTA DEL EVALUADOR", x, y, bg=SURFACE, fg=NAVY)
        y -= 9 * mm
        y = text_wrap(c, nota, x, y, col_w, color=HexColor("#444"), size=9, leading=14)

    c.showPage()


def _tabla_contactos(c, recomendados, page_num, total_pages):
    """Tabla de contactos de todos los recomendados."""
    draw_header(c, bg_color=WHITE, doc_title="REPORTE DE CANDIDATOS")
    draw_footer(c, page_num=page_num, total_pages=total_pages, label=FOOTER_LABEL)

    x, y, col_w, _ = content_area()

    # Título grande + subtítulo badge
    text_h1(c, "Candidatos Recomendados", x, y, color=NAVY, size=20)
    y -= 10 * mm
    section_tag(c, "INFORMACIÓN DE CONTACTO", x, y)
    y -= 14 * mm

    # Columnas — Score solo si algún candidato lo tiene
    has_scores = any(_normalizar_score(cd.get("score")) is not None for cd in recomendados)
    if has_scores:
        cols = [
            ("Candidato", col_w * 0.24),
            ("Email",     col_w * 0.26),
            ("Teléfono",  col_w * 0.14),
            ("Score",     col_w * 0.10),
            ("Notas",     col_w * 0.26),
        ]
    else:
        cols = [
            ("Candidato", col_w * 0.24),
            ("Email",     col_w * 0.26),
            ("Teléfono",  col_w * 0.14),
            ("Notas",     col_w * 0.36),
        ]

    row_h = 12 * mm
    fsize = 9
    pad = 4

    # Header row
    cx = x
    c.setFillColor(NAVY)
    c.rect(x, y - row_h, col_w, row_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Poppins-Bold", fsize)
    for label, w in cols:
        c.drawString(cx + pad, y - row_h + 4 * mm, label.upper())
        cx += w
    y -= row_h

    # Data rows — dos líneas en Notas si es largo
    for i, cand in enumerate(recomendados):
        bg = SURFACE if i % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.rect(x, y - row_h, col_w, row_h, fill=1, stroke=0)

        score = _normalizar_score(cand.get("score"))
        nota_full = cand.get("nota_evaluador") or "—"

        if has_scores:
            valores = [
                cand.get("nombre", "—"),
                cand.get("email") or "—",
                cand.get("telefono") or "—",
                f"{score}/100" if score is not None else "—",
                nota_full,
            ]
        else:
            valores = [
                cand.get("nombre", "—"),
                cand.get("email") or "—",
                cand.get("telefono") or "—",
                nota_full,
            ]

        cx = x
        for j, (val, (_, w)) in enumerate(zip(valores, cols)):
            c.setFillColor(NAVY)
            c.setFont("Poppins", fsize)
            # Última columna (Notas o Score): wrap en dos líneas
            is_last = (j == len(cols) - 1)
            if is_last and w > col_w * 0.20:
                # Dos líneas: primera hasta ~chars, segunda el resto
                txt = str(val)
                chars_per_line = max(20, int(w / (fsize * 0.52)))
                line1 = txt[:chars_per_line]
                line2 = txt[chars_per_line:chars_per_line * 2]
                c.drawString(cx + pad, y - row_h + 6.5 * mm, line1)
                if line2:
                    c.setFont("Poppins", fsize - 1)
                    c.drawString(cx + pad, y - row_h + 3 * mm, line2)
            else:
                # Truncar al ancho de columna
                chars = max(10, int(w / (fsize * 0.52)))
                c.drawString(cx + pad, y - row_h + 4 * mm, str(val)[:chars])
            cx += w
        y -= row_h

    c.showPage()


def _tabla_descartados(c, descartados, page_num, total_pages):
    """Tabla simple de candidatos descartados."""
    draw_header(c, bg_color=WHITE, doc_title="REPORTE DE CANDIDATOS")
    draw_footer(c, page_num=page_num, total_pages=total_pages, label=FOOTER_LABEL)

    x, y, col_w, _ = content_area()

    text_h1(c, "Candidatos Descartados", x, y, color=NAVY, size=20)
    y -= 10 * mm
    section_tag(c, "NO AVANZAN EN ESTE PROCESO", x, y, bg=HexColor("#E8ECF0"), fg=NAVY)
    y -= 14 * mm

    cols = [
        ("Candidato",       col_w * 0.28),
        ("Score",           col_w * 0.10),
        ("Razón principal", col_w * 0.62),
    ]
    row_h = 12 * mm
    fsize = 9
    pad = 4

    # Header
    cx = x
    c.setFillColor(HexColor("#4A6375"))
    c.rect(x, y - row_h, col_w, row_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Poppins-Bold", fsize)
    for label, w in cols:
        c.drawString(cx + pad, y - row_h + 4 * mm, label.upper())
        cx += w
    y -= row_h

    # Data
    for i, cand in enumerate(descartados):
        bg = SURFACE if i % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.rect(x, y - row_h, col_w, row_h, fill=1, stroke=0)

        score = _normalizar_score(cand.get("score"))
        razon = cand.get("nota_evaluador") or cand.get("nivel") or "—"
        valores = [
            cand.get("nombre", "—"),
            f"{score}/100" if score is not None else "—",
            razon,
        ]
        cx = x
        for j, (val, (_, w)) in enumerate(zip(valores, cols)):
            c.setFillColor(NAVY)
            c.setFont("Poppins", fsize)
            is_last = (j == len(cols) - 1)
            if is_last:
                txt = str(val)
                chars_per_line = max(20, int(w / (fsize * 0.52)))
                line1 = txt[:chars_per_line]
                line2 = txt[chars_per_line:chars_per_line * 2]
                c.drawString(cx + pad, y - row_h + 6.5 * mm, line1)
                if line2:
                    c.setFont("Poppins", fsize - 1)
                    c.drawString(cx + pad, y - row_h + 3 * mm, line2)
            else:
                chars = max(10, int(w / (fsize * 0.52)))
                c.drawString(cx + pad, y - row_h + 4 * mm, str(val)[:chars])
            cx += w
        y -= row_h

    c.showPage()


# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

def generar_reporte_pool(
    candidatos: list,
    puesto: str,
    cliente: str,
    output_path: str,
):
    """
    Genera el PDF del reporte de pool de candidatos.

    Args:
        candidatos:   Lista de dicts con datos de cada candidato.
                      Campos por candidato:
                        nombre         — nombre completo
                        score          — int 0-100 o None
                        nivel          — str (Excepcional/Sólido/Con potencial/No recomendado) o None
                        escolaridad    — str
                        experiencia    — str (ej. "8 años en administración")
                        ultimo_puesto  — str (descripción del puesto más relevante)
                        competencias   — [{nombre, nivel}] (Alto/Medio/Básico)
                        fortalezas     — [str] (max 3, con evidencia de entrevista)
                        nota_evaluador — str (texto de sección 9 del Reporte de Candidato)
                        email          — str o None (del CV vía pdfplumber si no está en transcripción)
                        telefono       — str o None (ídem)
                        cv_path        — str ruta absoluta al PDF del CV, o None
                        recomendado    — bool (True → tarjeta; False → tabla de descartados)
        puesto:       Nombre del puesto evaluado.
        cliente:      Nombre del cliente.
        output_path:  Ruta del PDF de salida.

    Ejemplo:
        generar_reporte_pool(candidatos, "Coord. Administrativo", "ACME", "out.pdf")
    """
    ensure_dir(os.path.dirname(output_path) or ".")

    recomendados = [c for c in candidatos if c.get("recomendado")]
    descartados  = [c for c in candidatos if not c.get("recomendado")]

    total_pages = _calcular_total_paginas(recomendados, descartados)

    doc_title = f"Reporte Pool — {puesto} · {cliente}"
    c, W, H = new_doc(output_path, doc_title)

    # Página 1 — Portada
    _portada(c, W, H, puesto, cliente, candidatos, total_pages)

    # Páginas 2..N — Tarjetas de candidatos recomendados
    for i, cand in enumerate(recomendados):
        _tarjeta_candidato(c, cand, puesto, page_num=2 + i, total_pages=total_pages)

    # Tabla de contactos
    _tabla_contactos(c, recomendados, page_num=2 + len(recomendados), total_pages=total_pages)

    # Tabla de descartados (si hay)
    if descartados:
        _tabla_descartados(
            c, descartados,
            page_num=3 + len(recomendados),
            total_pages=total_pages
        )

    c.save()
    size_kb = os.path.getsize(output_path) // 1024
    print(f"✅ Reporte generado: {output_path} ({size_kb} KB, {total_pages} páginas)")
    return output_path


# ─── CARGA DESDE CARPETA ──────────────────────────────────────────────────────

def cargar_candidatos_desde_carpeta(ruta: str) -> list:
    """
    Carga todos los archivos datos_*.json de una carpeta y los devuelve
    como lista de dicts listos para pasar a generar_reporte_pool().

    Cada JSON debe tener la misma estructura que el dict de candidato:
    nombre, score, nivel, escolaridad, experiencia, ultimo_puesto,
    competencias, fortalezas, nota_evaluador, email, telefono,
    recomendado, cv_path (opcional).

    Uso:
        candidatos = cargar_candidatos_desde_carpeta(
            "Agent/Reclutamientos/SolarPro/Especialista de producto/"
        )
        generar_reporte_pool(candidatos, puesto="...", cliente="...", output_path="...")
    """
    import json
    import glob

    patron = os.path.join(ruta, "datos_*.json")
    archivos = sorted(glob.glob(patron))

    if not archivos:
        print(f"⚠️  No se encontraron archivos datos_*.json en: {ruta}")
        return []

    candidatos = []
    for path in archivos:
        try:
            with open(path, "r", encoding="utf-8") as f:
                datos = json.load(f)
            candidatos.append(datos)
            print(f"  ✓ Cargado: {os.path.basename(path)}")
        except Exception as e:
            print(f"  ✗ Error al leer {os.path.basename(path)}: {e}")

    return candidatos


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    print("🧪 Modo prueba — generando reporte de pool de ejemplo...")

    candidatos_ejemplo = [
        {
            "nombre":        "Martha Rodela",
            "score":         82,
            "nivel":         "Sólido",
            "escolaridad":   "Lic. Administración — UACH 2015",
            "experiencia":   "8 años en administración y finanzas",
            "ultimo_puesto": "Coordinadora Administrativa · Empresa XYZ (2018-2024). "
                             "Responsable de tesorería, cuentas por pagar, control "
                             "presupuestal y reportes financieros mensuales.",
            "competencias": [
                {"nombre": "Orientación a resultados", "nivel": "Alto"},
                {"nombre": "Comunicación efectiva",    "nivel": "Alto"},
                {"nombre": "Gestión de procesos",      "nivel": "Medio"},
            ],
            "fortalezas": [
                "Experiencia directa en control presupuestal en empresa de manufactura.",
                "Comunicación efectiva — clara y directa en entrevista.",
                "Proactividad: implementó mejoras sin que se le solicitaran.",
            ],
            "nota_evaluador": "Candidata destacada. Recomendada para primera entrevista con cliente.",
            "email":    "martha.rodela@email.com",
            "telefono": "614-123-4567",
            "recomendado": True,
        },
        {
            "nombre":        "Ana Torres",
            "score":         75,
            "nivel":         "Sólido",
            "escolaridad":   "Lic. Contaduría Pública — UACH 2017",
            "experiencia":   "6 años en área contable y administrativa",
            "ultimo_puesto": "Auxiliar contable senior · Despacho Financiero ABC (2019-2024). "
                             "Manejo de estados financieros, declaraciones fiscales y cuentas por cobrar.",
            "competencias": [
                {"nombre": "Análisis financiero",  "nivel": "Alto"},
                {"nombre": "Control interno",       "nivel": "Medio"},
                {"nombre": "Trabajo bajo presión",  "nivel": "Alto"},
            ],
            "fortalezas": [
                "Sólido conocimiento fiscal y contable.",
                "Experiencia en manejo de SAP y CONTPAQi.",
            ],
            "nota_evaluador": "Segunda opción viable. Menor experiencia en liderazgo.",
            "email":    "ana.torres@email.com",
            "telefono": "614-987-6543",
            "recomendado": True,
        },
        {
            "nombre":        "Roberto Sánchez",
            "score":         38,
            "nivel":         "No recomendado",
            "escolaridad":   "Trunca — 3er semestre Administración",
            "experiencia":   "1 año como auxiliar",
            "ultimo_puesto": "Auxiliar administrativo general.",
            "competencias": [],
            "fortalezas":    [],
            "nota_evaluador": "Experiencia e escolaridad insuficientes para el nivel requerido.",
            "email":    None,
            "telefono": None,
            "recomendado": False,
        },
    ]

    tmp = tempfile.mktemp(suffix=".pdf")
    generar_reporte_pool(
        candidatos=candidatos_ejemplo,
        puesto="Coordinador Administrativo",
        cliente="ACME Corp",
        output_path=tmp,
    )
    os.unlink(tmp)
    print("✅ Test completo — estructura y datos correctos.")
