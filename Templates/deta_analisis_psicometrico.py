"""
deta_analisis_psicometrico.py
=============================

Genera el PDF "Análisis DETA" — reporte narrativo cualitativo de 8 páginas
que cruza scores psicométricos con el perfil del puesto. Fase G del
proyecto DETA Psicométricos.

Uso
---
Como módulo Python (desde la skill Cowork):

    from deta_analisis_psicometrico import generar_analisis
    pdf_path = generar_analisis(payload, output_dir)

Como CLI:

    python deta_analisis_psicometrico.py payload.json [output_dir]
    # o leyendo desde stdin
    cat payload.json | python deta_analisis_psicometrico.py - [output_dir]

El payload es el JSON exportado por /api/export/[candidatoId] en
deta-psicometricos, ENRIQUECIDO por Claude (dentro de Cowork o en la
skill local) con los campos narrativos en payload["analisis"].

Contrato del payload
--------------------
{
  "candidato": { "nombre": str, "email": str, "vacante"?: str, "cliente"?: str, "completadoEn": iso8601 },
  "perfilPuesto": { ... (opcional, PerfilPuesto tipado desde lib/matching/types.ts) },
  "perfilPuestoUrl": str | null,
  "scores": { cleaver, kostick, moss, barsit, ipip },  # originales, no se tocan
  "analisis": {
    "resumenEjecutivo": str,
    "recomendacion": "Avanzar" | "Avanzar con reservas" | "No avanzar",
    "perfilEvaluado": str,
    "fortalezas": [str, ...],
    "areasMejora": [str, ...],
    "puntosClave": [ { "titulo": str, "descripcion": str }, ... ],  # 5 ideales
    "ajustePuesto": [ { "competencia": str, "nivel": "alto"|"medio"|"bajo", "comentario": str }, ... ],
    "resumenPorTest": { "cleaver": str, "kostick": str, "moss": str, "barsit": str, "ipip": str },
    "conclusiones": [str, ...]
  },
  "exportadoEn": iso8601
}

Diseño
------
Réplica del layout en `components/reporte/AnalisisDeta.tsx` de
deta-psicometricos. Fondo claro, tokens DETA navy/gold/cyan, tipografía
Playfair Display + Source Sans 3.

- Pág 1  Portada (fondo navy, candidato centrado, fecha)
- Pág 2  Resumen ejecutivo + Recomendación (pill semántica)
- Pág 3  Perfil del puesto (competencias, requisitos)  [si perfilPuesto]
- Pág 4  Ajuste competencia por competencia
- Pág 5  Personalidad + Fortalezas + Áreas a validar
- Pág 6  Puntos clave para el puesto (5 lecturas)
- Pág 7  Resumen por prueba (narrativa de cada instrumento)
- Pág 8  Conclusiones + próximos pasos
"""
from __future__ import annotations

import json
import sys
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# sys.path dual: funciona en macOS (Drive) y en Cowork (/mnt).
HERE = os.path.dirname(os.path.abspath(__file__))
for candidate in (HERE, "/mnt"):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

from deta_pdf_base import (  # type: ignore
    new_doc,
    new_page,
    full_bg,
    draw_header,
    draw_footer,
    text_h1,
    text_h2,
    text_h3,
    text_body,
    text_label,
    text_wrap,
    rule,
    section_tag,
    NAVY,
    GOLD,
    CYAN,
    WHITE,
    SURFACE,
    get_paragraph_styles,
    content_area,
    today_str,
    ensure_dir,
    LOGO_WHITE_PATH,
    LOGO_PNG_PATH,
)
from reportlab.lib.colors import HexColor

# Colores semánticos adicionales (replican /analisis-deta/demo).
SUCCESS_BG   = HexColor("#e5f6ee")
SUCCESS_LINE = HexColor("#10b981")
SUCCESS_TEXT = HexColor("#0f7b3a")

WARN_BG      = HexColor("#f5ecd6")
WARN_LINE    = HexColor("#d3ab6d")
WARN_TEXT    = HexColor("#8a6b2f")

DANGER_BG    = HexColor("#fbe4e8")
DANGER_LINE  = HexColor("#e0556f")
DANGER_TEXT  = HexColor("#8a2a2a")

GREY_TEXT    = HexColor("#6B7280")
INK          = HexColor("#1a1a2e")
BORDER_SOFT  = HexColor("#e5e7eb")


# ───────────────────────────── util ─────────────────────────────

def _slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii")
    s = "".join(c if c.isalnum() else "-" for c in s.lower())
    return "-".join(p for p in s.split("-") if p)


def _fmt_fecha(iso_or_text: Optional[str]) -> str:
    if not iso_or_text:
        return today_str("%d de %B de %Y")
    try:
        dt = datetime.fromisoformat(iso_or_text.replace("Z", "+00:00"))
        MESES = ["enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return f"{dt.day} de {MESES[dt.month-1]} de {dt.year}"
    except Exception:
        return iso_or_text


def _eyebrow(c, text: str, x: float, y: float):
    text_label(c, text.upper(), x, y, color=GOLD, size=9, tracking=0.3)


def _para(text: str, style_name: str = "body", styles=None) -> Paragraph:
    styles = styles or get_paragraph_styles()
    base = styles.get(style_name) or styles["body"]
    return Paragraph(text, base)


# ──────────────────────── layout helpers ────────────────────────

def _page_cover(c, payload: dict[str, Any]) -> None:
    W, H = A4
    full_bg(c, NAVY)
    # Ambient glow — circulo cyan sutil
    c.setFillColor(HexColor("#12a9cc"))
    c.setFillAlpha(0.15)
    c.circle(W/2, H*0.55, W*0.4, fill=1, stroke=0)
    c.setFillAlpha(1)

    # Logo en header
    try:
        c.drawImage(LOGO_WHITE_PATH, 22*mm, H - 28*mm, height=10*mm, width=40*mm,
                    preserveAspectRatio=True, mask='auto')
    except Exception:
        text_h3(c, "DETA Consultores", 22*mm, H - 25*mm, color=WHITE)

    cand = payload["candidato"]
    perfil = payload.get("perfilPuesto") or {}
    puesto_txt = cand.get("vacante") or perfil.get("puesto") or "Evaluación integrada"
    cliente_txt = cand.get("cliente") or perfil.get("cliente") or "DETA Consultores"

    # Eyebrow
    text_label(c, "ANÁLISIS DETA", W/2, H*0.65, color=GOLD, size=11, tracking=0.45, align='center')
    # Divider
    c.setStrokeColor(GOLD)
    c.setStrokeAlpha(0.4)
    c.setLineWidth(0.8)
    c.line(W/2 - 12*mm, H*0.635, W/2 + 12*mm, H*0.635)
    c.setStrokeAlpha(1)

    # Nombre grande
    c.setFillColor(WHITE)
    c.setFont("PlayfairDisplay-Bold", 44)
    name_lines = _wrap_text(cand.get("nombre","Candidato"), 22)
    y = H*0.55
    for line in name_lines:
        c.drawCentredString(W/2, y, line)
        y -= 52

    # Puesto
    c.setFont("SourceSans3", 18)
    c.drawCentredString(W/2, H*0.40, puesto_txt)
    c.setFillColor(HexColor("#94a3b8"))
    c.setFont("SourceSans3", 11)
    c.drawCentredString(W/2, H*0.37, cliente_txt)

    # Footer portada
    c.setFillColor(HexColor("#7a8b9c"))
    c.setFont("SourceSans3", 8)
    c.drawString(22*mm, 28*mm, "EVALUACIÓN INTEGRADA")
    c.setFillColor(HexColor("#bfc9d4"))
    c.setFont("SourceSans3", 9)
    c.drawString(22*mm, 24*mm, "Psicometría + ajuste al perfil del puesto")

    c.setFillColor(HexColor("#bfc9d4"))
    c.setFont("SourceSans3", 9)
    fecha = _fmt_fecha(cand.get("completadoEn") or payload.get("exportadoEn"))
    c.drawRightString(W - 22*mm, 28*mm, fecha)
    c.setFillColor(HexColor("#7a8b9c"))
    c.setFont("SourceSans3", 8)
    c.drawRightString(W - 22*mm, 24*mm, "CONFIDENCIAL")


def _wrap_text(text: str, max_chars: int) -> list[str]:
    """Partir en líneas tratando de respetar palabras."""
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current = (current + " " + w).strip()
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines or [text]


def _page_resumen(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "01 · Resumen ejecutivo", x, y0)
    analisis = payload["analisis"]
    cand = payload["candidato"]
    first_name = cand.get("nombre","Candidato").split()[0]
    text_h1(c, f"¿Quién es {first_name} y qué tan bien encaja?", x, y0 - 12*mm, color=NAVY, size=22)

    # Caja resumen (SURFACE)
    box_y = y0 - 70*mm
    box_h = 60*mm
    c.setFillColor(SURFACE)
    c.setStrokeColor(BORDER_SOFT)
    c.roundRect(x, box_y, W - 44*mm, box_h, 8, fill=1, stroke=1)
    # Texto del resumen
    p = _para(analisis.get("resumenEjecutivo",""), "body", styles)
    p.wrapOn(c, W - 54*mm, box_h - 12*mm)
    p.drawOn(c, x + 5*mm, box_y + box_h - p.height - 6*mm)

    # Recomendación pill
    rec = analisis.get("recomendacion", "Avanzar con reservas")
    rec_map = {
        "Avanzar": (SUCCESS_BG, SUCCESS_LINE, SUCCESS_TEXT),
        "Avanzar con reservas": (WARN_BG, WARN_LINE, WARN_TEXT),
        "No avanzar": (DANGER_BG, DANGER_LINE, DANGER_TEXT),
    }
    bg, line, txt = rec_map.get(rec, (WARN_BG, WARN_LINE, WARN_TEXT))

    pill_y = box_y - 22*mm
    c.setFillColor(bg)
    c.setStrokeColor(line)
    c.roundRect(x, pill_y, W - 44*mm, 18*mm, 8, fill=1, stroke=1)
    text_label(c, "RECOMENDACIÓN", x + 6*mm, pill_y + 12*mm, color=txt, size=9, tracking=0.25)
    c.setFillColor(txt)
    c.setFont("PlayfairDisplay-Bold", 20)
    c.drawString(x + 6*mm, pill_y + 4*mm, rec)

    draw_footer(c, page_num=2)


def _page_perfil(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "02 · Perfil del puesto evaluado", x, y0)
    perfil = payload.get("perfilPuesto") or {}
    puesto = perfil.get("puesto", payload["candidato"].get("vacante", "Puesto evaluado"))
    cliente = perfil.get("cliente", payload["candidato"].get("cliente", ""))
    sector = (perfil.get("requisitos") or {}).get("sector", "")

    text_h1(c, puesto, x, y0 - 12*mm, color=NAVY, size=22)
    text_body(c, f"{cliente} · Sector {sector}".strip(" ·"), x, y0 - 20*mm, color=GREY_TEXT, size=10)

    # Competencias
    _eyebrow(c, "COMPETENCIAS REQUERIDAS (PESO RELATIVO)", x, y0 - 32*mm)
    comps = perfil.get("competencias", []) or []
    row_y = y0 - 40*mm
    for comp in comps[:7]:
        c.setStrokeColor(BORDER_SOFT)
        c.setFillColor(WHITE)
        c.roundRect(x, row_y - 10*mm, W - 44*mm, 11*mm, 4, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("SourceSans3-Bold", 11)
        c.drawString(x + 4*mm, row_y - 4*mm, comp.get("nombre",""))
        c.setFillColor(GREY_TEXT)
        c.setFont("SourceSans3", 9)
        desc = comp.get("descripcion","") or ""
        if len(desc) > 90:
            desc = desc[:87] + "…"
        c.drawString(x + 4*mm, row_y - 8*mm, desc)
        c.setFillColor(CYAN)
        c.setFont("PlayfairDisplay-Bold", 14)
        c.drawRightString(x + W - 48*mm, row_y - 5*mm, f"{comp.get('peso','?')}%")
        c.setFillColor(GREY_TEXT)
        c.setFont("SourceSans3-Bold", 8)
        c.drawRightString(x + W - 48*mm, row_y - 9*mm, f"NIVEL {comp.get('nivelRequerido','')}")
        row_y -= 13*mm

    # Info blocks (grid 2x2)
    req = perfil.get("requisitos") or {}
    rango = perfil.get("rangoSalarial") or {}
    info_rows = [
        ("ESCOLARIDAD MÍNIMA", req.get("escolaridadMinima", "—")),
        ("EXPERIENCIA MÍNIMA", f"{req.get('anosExperienciaMin','?')}+ años"),
        ("HERRAMIENTAS CLAVE", ", ".join(req.get("herramientas", [])) or "—"),
    ]
    if rango:
        info_rows.append(("RANGO SALARIAL",
            f"${rango.get('min',0):,} – ${rango.get('max',0):,} {rango.get('moneda','MXN')} {rango.get('tipo','')}"))

    col_w = (W - 50*mm) / 2
    base_y = row_y - 10*mm
    for i, (label, value) in enumerate(info_rows):
        col = i % 2
        row = i // 2
        bx = x + col * (col_w + 4*mm)
        by = base_y - row * 18*mm
        c.setStrokeColor(BORDER_SOFT)
        c.setFillColor(WHITE)
        c.roundRect(bx, by - 14*mm, col_w, 14*mm, 4, fill=1, stroke=1)
        text_label(c, label, bx + 4*mm, by - 4*mm, color=GREY_TEXT, size=8, tracking=0.2)
        c.setFillColor(NAVY)
        c.setFont("SourceSans3", 10)
        c.drawString(bx + 4*mm, by - 10*mm, value[:60] + ("…" if len(value) > 60 else ""))

    draw_footer(c, page_num=3)


def _page_ajuste(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "03 · Ajuste a las competencias del puesto", x, y0)
    text_h1(c, "Competencia por competencia", x, y0 - 12*mm, color=NAVY, size=22)

    items = (payload.get("analisis") or {}).get("ajustePuesto", []) or []
    level_map = {
        "alto":  (SUCCESS_BG, SUCCESS_LINE, SUCCESS_TEXT, "ALTO AJUSTE", 0.9),
        "medio": (WARN_BG, WARN_LINE, WARN_TEXT, "AJUSTE MEDIO", 0.55),
        "bajo":  (DANGER_BG, DANGER_LINE, DANGER_TEXT, "AJUSTE BAJO", 0.25),
    }

    row_y = y0 - 25*mm
    for item in items[:6]:
        nivel = (item.get("nivel") or "medio").lower()
        bg, line, txt, label, pct = level_map.get(nivel, level_map["medio"])
        card_h = 22*mm
        c.setStrokeColor(BORDER_SOFT)
        c.setFillColor(WHITE)
        c.roundRect(x, row_y - card_h, W - 44*mm, card_h, 6, fill=1, stroke=1)
        # Competencia
        c.setFillColor(NAVY)
        c.setFont("SourceSans3-Bold", 11)
        c.drawString(x + 4*mm, row_y - 5*mm, item.get("competencia",""))
        # Pill nivel
        pill_x = W - 24*mm - 35*mm
        c.setFillColor(bg)
        c.setStrokeColor(line)
        c.roundRect(pill_x, row_y - 8*mm, 30*mm, 5*mm, 2.5, fill=1, stroke=1)
        c.setFillColor(txt)
        c.setFont("SourceSans3-Bold", 7)
        c.drawCentredString(pill_x + 15*mm, row_y - 6.5*mm, label)
        # Barra
        bar_x = x + 4*mm
        bar_y = row_y - 11*mm
        bar_w = W - 52*mm
        c.setFillColor(BORDER_SOFT)
        c.rect(bar_x, bar_y, bar_w, 1.2*mm, fill=1, stroke=0)
        c.setFillColor(line)
        c.rect(bar_x, bar_y, bar_w * pct, 1.2*mm, fill=1, stroke=0)
        # Comentario
        c.setFillColor(INK)
        c.setFont("SourceSans3", 9)
        comentario = item.get("comentario","")
        lines = _wrap_text(comentario, 95)[:2]
        for i, ln in enumerate(lines):
            c.drawString(x + 4*mm, row_y - 16*mm - i*4*mm, ln)
        row_y -= card_h + 4*mm

    # Nota metodológica
    note_y = 35*mm
    c.setFillColor(HexColor("#e3f4f8"))
    c.setStrokeColor(CYAN)
    c.setStrokeAlpha(0.3)
    c.roundRect(x, note_y, W - 44*mm, 14*mm, 4, fill=1, stroke=1)
    c.setStrokeAlpha(1)
    c.setFillColor(NAVY)
    c.setFont("SourceSans3", 8)
    c.drawString(x + 4*mm, note_y + 8*mm, "Nota metodológica: el ajuste cualitativo se deriva de cruzar resultados psicométricos")
    c.drawString(x + 4*mm, note_y + 4*mm, "con las competencias del perfil; no sustituye la entrevista final ni las referencias.")

    draw_footer(c, page_num=4)


def _page_perfil_evaluado(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "04 · Perfil evaluado", x, y0)
    text_h1(c, "Personalidad y estilo de trabajo", x, y0 - 12*mm, color=NAVY, size=22)

    analisis = payload["analisis"]
    # Parrafo personalidad
    box_y = y0 - 45*mm
    p = _para(analisis.get("perfilEvaluado",""), "body", styles)
    p.wrapOn(c, W - 44*mm, 35*mm)
    p.drawOn(c, x, box_y - p.height + 20*mm)

    # Dos columnas: fortalezas (verde) / áreas (gold)
    col_y = box_y - 25*mm
    col_h = 65*mm
    col_w = (W - 50*mm) / 2

    # Fortalezas
    c.setFillColor(SUCCESS_BG)
    c.setStrokeColor(SUCCESS_LINE)
    c.roundRect(x, col_y - col_h, col_w, col_h, 6, fill=1, stroke=1)
    text_label(c, "✓  FORTALEZAS", x + 4*mm, col_y - 6*mm, color=SUCCESS_TEXT, size=9, tracking=0.2)
    line_y = col_y - 13*mm
    for f in (analisis.get("fortalezas") or [])[:7]:
        bullet_lines = _wrap_text(f, 42)
        for i, bl in enumerate(bullet_lines):
            prefix = "•  " if i == 0 else "   "
            c.setFillColor(INK)
            c.setFont("SourceSans3", 9)
            c.drawString(x + 4*mm, line_y, prefix + bl)
            line_y -= 4*mm
        line_y -= 1*mm

    # Áreas
    ax = x + col_w + 4*mm
    c.setFillColor(WARN_BG)
    c.setStrokeColor(WARN_LINE)
    c.roundRect(ax, col_y - col_h, col_w, col_h, 6, fill=1, stroke=1)
    text_label(c, "△  ÁREAS A VALIDAR", ax + 4*mm, col_y - 6*mm, color=WARN_TEXT, size=9, tracking=0.2)
    line_y = col_y - 13*mm
    for a in (analisis.get("areasMejora") or [])[:7]:
        bullet_lines = _wrap_text(a, 42)
        for i, bl in enumerate(bullet_lines):
            prefix = "•  " if i == 0 else "   "
            c.setFillColor(INK)
            c.setFont("SourceSans3", 9)
            c.drawString(ax + 4*mm, line_y, prefix + bl)
            line_y -= 4*mm
        line_y -= 1*mm

    draw_footer(c, page_num=5)


def _page_puntos_clave(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "05 · Puntos clave para el puesto", x, y0)
    text_h1(c, "Cinco lecturas estratégicas", x, y0 - 12*mm, color=NAVY, size=22)

    puntos = (payload["analisis"].get("puntosClave") or [])[:5]
    row_y = y0 - 28*mm
    for i, p in enumerate(puntos):
        # Número
        c.setFillColor(NAVY)
        c.roundRect(x, row_y - 10*mm, 10*mm, 10*mm, 2, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("SourceSans3-Bold", 10)
        c.drawCentredString(x + 5*mm, row_y - 7*mm, f"{i+1:02d}")
        # Título + descripción
        c.setFillColor(NAVY)
        c.setFont("PlayfairDisplay-Bold", 13)
        c.drawString(x + 14*mm, row_y - 4*mm, p.get("titulo",""))
        c.setFillColor(INK)
        c.setFont("SourceSans3", 9)
        lines = _wrap_text(p.get("descripcion",""), 95)[:3]
        for j, ln in enumerate(lines):
            c.drawString(x + 14*mm, row_y - 9*mm - j*4*mm, ln)
        row_y -= 24*mm

    draw_footer(c, page_num=6)


def _page_resumen_test(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "06 · Resumen por prueba", x, y0)
    text_h1(c, "Interpretación de los cinco instrumentos", x, y0 - 12*mm, color=NAVY, size=22)

    rpt = payload["analisis"].get("resumenPorTest") or {}
    tests = [
        ("Cleaver · DISC", rpt.get("cleaver","")),
        ("Kostick · PAPI", rpt.get("kostick","")),
        ("MOSS · Supervisión", rpt.get("moss","")),
        ("BARSIT · Aptitud", rpt.get("barsit","")),
        ("IPIP Big Five", rpt.get("ipip","")),
    ]
    row_y = y0 - 26*mm
    for label, text in tests:
        card_h = 24*mm
        c.setFillColor(WHITE)
        c.setStrokeColor(BORDER_SOFT)
        c.roundRect(x, row_y - card_h, W - 44*mm, card_h, 4, fill=1, stroke=1)
        text_label(c, label.upper(), x + 4*mm, row_y - 5*mm, color=CYAN, size=9, tracking=0.2)
        c.setFillColor(INK)
        c.setFont("SourceSans3", 9)
        lines = _wrap_text(text, 100)[:3]
        for i, ln in enumerate(lines):
            c.drawString(x + 4*mm, row_y - 10*mm - i*4*mm, ln)
        row_y -= card_h + 3*mm

    draw_footer(c, page_num=7)


def _page_conclusiones(c, payload: dict[str, Any], styles) -> None:
    W, H = A4
    draw_header(c, bg_color=WHITE, doc_title="Análisis DETA")
    x, y0 = 22*mm, H - 35*mm
    _eyebrow(c, "07 · Conclusiones y próximos pasos", x, y0)
    text_h1(c, "Recomendaciones para el proceso", x, y0 - 12*mm, color=NAVY, size=22)

    conclusiones = (payload["analisis"].get("conclusiones") or [])[:6]
    row_y = y0 - 28*mm
    for i, concl in enumerate(conclusiones):
        c.setFillColor(SURFACE)
        c.setStrokeColor(BORDER_SOFT)
        card_h = 16*mm
        c.roundRect(x, row_y - card_h, W - 44*mm, card_h, 4, fill=1, stroke=1)
        # Circulo gold con número
        c.setFillColor(GOLD)
        c.circle(x + 6*mm, row_y - 8*mm, 3*mm, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("SourceSans3-Bold", 9)
        c.drawCentredString(x + 6*mm, row_y - 9.5*mm, str(i+1))
        # Texto
        c.setFillColor(INK)
        c.setFont("SourceSans3", 9)
        lines = _wrap_text(concl, 95)[:2]
        for j, ln in enumerate(lines):
            c.drawString(x + 14*mm, row_y - 6*mm - j*4*mm, ln)
        row_y -= card_h + 3*mm

    # Documentos complementarios
    doc_y = 35*mm
    c.setFillColor(HexColor("#edf2f7"))
    c.setStrokeColor(HexColor("#cbd5e0"))
    c.roundRect(x, doc_y, W - 44*mm, 18*mm, 4, fill=1, stroke=1)
    text_label(c, "DOCUMENTOS COMPLEMENTARIOS", x + 4*mm, doc_y + 14*mm, color=NAVY, size=8, tracking=0.2)
    c.setFillColor(INK)
    c.setFont("SourceSans3", 9)
    c.drawString(x + 4*mm, doc_y + 9*mm, "• Reporte Cuantitativo (scores numéricos detallados por prueba)")
    perfil = payload.get("perfilPuesto") or {}
    perfil_ver = (perfil.get("fecha","") or "")[:7]
    c.drawString(x + 4*mm, doc_y + 5*mm, f"• Perfil del Puesto{' v' + perfil_ver if perfil_ver else ''} ({perfil.get('cliente','—')})")

    draw_footer(c, page_num=8)


# ───────────────────────── API pública ─────────────────────────

def generar_analisis(payload: dict[str, Any], output_dir: Optional[str] = None) -> str:
    """Genera el PDF Análisis DETA a partir del payload enriquecido.

    Args:
        payload: diccionario con candidato, perfilPuesto, scores y analisis (narrativa).
        output_dir: carpeta destino. Si es None, usa ./output/ relativo a cwd.

    Returns:
        path absoluto del PDF generado.
    """
    if "candidato" not in payload:
        raise ValueError("payload debe tener 'candidato'")
    if "analisis" not in payload:
        raise ValueError("payload debe tener 'analisis' con la narrativa. Ver SKILL.md para contrato.")

    cand = payload["candidato"]
    nombre = cand.get("nombre", "Candidato")
    out_dir = Path(output_dir or "./output").resolve()
    ensure_dir(str(out_dir))

    fecha_tag = datetime.now().strftime("%Y%m%d")
    filename = f"AnalisisDETA_{_slugify(nombre)}_{fecha_tag}.pdf"
    out_path = out_dir / filename

    title = f"Análisis DETA — {nombre}"
    c, W, H = new_doc(str(out_path), title=title, author="DETA Consultores")
    styles = get_paragraph_styles()

    _page_cover(c, payload); new_page(c)
    _page_resumen(c, payload, styles); new_page(c)
    _page_perfil(c, payload, styles); new_page(c)
    _page_ajuste(c, payload, styles); new_page(c)
    _page_perfil_evaluado(c, payload, styles); new_page(c)
    _page_puntos_clave(c, payload, styles); new_page(c)
    _page_resumen_test(c, payload, styles); new_page(c)
    _page_conclusiones(c, payload, styles)

    c.save()
    return str(out_path)


def _load_payload(arg: str) -> dict[str, Any]:
    if arg == "-":
        return json.load(sys.stdin)
    with open(arg, "r", encoding="utf-8") as f:
        return json.load(f)


def _main():
    if len(sys.argv) < 2:
        print("Uso: python deta_analisis_psicometrico.py <payload.json|-> [output_dir]", file=sys.stderr)
        sys.exit(1)
    payload = _load_payload(sys.argv[1])
    out_dir = sys.argv[2] if len(sys.argv) >= 3 else None
    path = generar_analisis(payload, out_dir)
    print(path)


if __name__ == "__main__":
    _main()
