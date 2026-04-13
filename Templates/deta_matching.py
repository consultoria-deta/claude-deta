"""
deta_matching.py
────────────────────────────────────────────────────────
Script de scoring DETA para candidatos en procesos de reclutamiento.

Flujo de uso con Cowork:
    1. Correr el script — genera un prompt estructurado en stdout
    2. Cowork ejecuta el prompt con Claude
    3. Claude devuelve un JSON con scores por dimensión
    4. Pegar el JSON en stdin → el script calcula el score final

Uso desde terminal:
    python3 deta_matching.py perfil.html cv.txt [transcripcion.txt] [nombre]
    python3 deta_matching.py --test

Uso como módulo:
    from deta_matching import generar_prompt_matching, calcular_score_final

Fórmula con transcripción (score final):
    Score = (exp_tecnica × 0.35) + (comp_blandas × 0.25) +
            (fit_org × 0.20) + (escolaridad × 0.10) + (condiciones × 0.10)

Fórmula sin transcripción (score preliminar):
    Score = (exp_tecnica × 0.50) + (fit_org × 0.30) +
            (escolaridad × 0.10) + (condiciones × 0.10)

Escala de niveles:
    90-100 → Excepcional
    75-89  → Sólido
    60-74  → Con potencial
    45-59  → Marginal
    0-44   → No recomendado

Dependencias: solo stdlib (json, re, sys, pathlib)
"""

import json
import re
import sys
from pathlib import Path


# ─── CONSTANTES ───────────────────────────────────────────────────────────────

PESOS_CON_TRANSCRIPCION = {
    "experiencia_tecnica":  0.35,
    "competencias_blandas": 0.25,
    "fit_organizacional":   0.20,
    "escolaridad":          0.10,
    "condiciones":          0.10,
}

PESOS_SIN_TRANSCRIPCION = {
    "experiencia_tecnica":  0.50,
    "fit_organizacional":   0.30,
    "escolaridad":          0.10,
    "condiciones":          0.10,
}

NIVELES = [
    (90, "Excepcional"),
    (75, "Sólido"),
    (60, "Con potencial"),
    (45, "Marginal"),
    (0,  "No recomendado"),
]

RECOMENDACIONES = {
    "Excepcional":    "Avanzar de inmediato. Candidato que supera las expectativas del perfil.",
    "Sólido":         "Avanzar. Candidato sólido con experiencia y competencias adecuadas.",
    "Con potencial":  "Avanzar con reservas. Validar áreas de brecha en siguiente etapa.",
    "Marginal":       "En espera. Requiere evaluación adicional antes de decidir.",
    "No recomendado": "No continuar. El perfil no se alinea con los requisitos del puesto.",
}


# ─── EXTRACCIÓN Y LECTURA ─────────────────────────────────────────────────────

def extraer_matching_data(perfil_path: str) -> dict:
    """
    Lee el HTML del perfil y extrae el bloque DETA_MATCHING_DATA.
    Retorna el dict parseado. Lanza ValueError si no lo encuentra.
    """
    html = Path(perfil_path).read_text(encoding="utf-8")
    match = re.search(r"<!--DETA_MATCHING_DATA\s*(.*?)\s*-->", html, re.DOTALL)
    if not match:
        raise ValueError(
            f"No se encontró bloque DETA_MATCHING_DATA en: {perfil_path}\n"
            "El bloque debe existir como comentario HTML al final del archivo."
        )
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido en DETA_MATCHING_DATA: {e}") from e


def leer_texto(fuente) -> str:
    """
    Acepta string de texto o ruta a archivo .txt / .pdf.
    Para .pdf usa PyPDF2 si está disponible.
    """
    if not fuente:
        return ""

    path = Path(str(fuente))
    if path.exists():
        if path.suffix.lower() == ".pdf":
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(str(path))
                return "\n".join(p.extract_text() or "" for p in reader.pages)
            except ImportError:
                raise ImportError(
                    "PyPDF2 no instalado. Ejecutar: pip install PyPDF2\n"
                    "O pasar el texto del CV directamente como string."
                )
        return path.read_text(encoding="utf-8")

    return str(fuente)


# ─── GENERACIÓN DE PROMPT ─────────────────────────────────────────────────────

def generar_prompt_matching(
    perfil_data: dict,
    cv_texto: str,
    transcripcion_texto: str = "",
) -> str:
    """
    Genera el prompt estructurado para que Cowork lo ejecute con Claude.
    Retorna un string listo para copiar/pegar o imprimir en stdout.
    """
    tiene_transcripcion = bool(transcripcion_texto.strip())
    dimensiones_activas = list(
        PESOS_CON_TRANSCRIPCION if tiene_transcripcion else PESOS_SIN_TRANSCRIPCION
    )
    pesos = PESOS_CON_TRANSCRIPCION if tiene_transcripcion else PESOS_SIN_TRANSCRIPCION

    # Construir descripción de dimensiones con criterios
    desc_dimensiones = {
        "experiencia_tecnica": (
            "Experiencia en las áreas de efectividad del puesto, manejo de herramientas "
            "requeridas, profundidad y duración de trayectoria, progresión con resultados concretos."
        ),
        "competencias_blandas": (
            "Evidencia conductual de las competencias del perfil en la entrevista: "
            "ejemplos situación-acción-resultado, consistencia con logros, nivel demostrado vs. requerido."
        ),
        "fit_organizacional": (
            "Alineación motivacional con el tipo de empresa y rol, estilo de trabajo vs. "
            "exigencias del puesto, expectativas de autonomía y crecimiento, señales culturales."
        ),
        "escolaridad": (
            "Cumplimiento del nivel mínimo requerido, afinidad de la carrera, formación "
            "complementaria (posgrado, certificaciones), actualización académica."
        ),
        "condiciones": (
            "Expectativa salarial dentro del rango del perfil, disponibilidad para el esquema "
            "requerido (horario, viajes, presencialidad), disponibilidad de inicio. "
            "Si no hay información, asignar 60 (neutral)."
        ),
    }

    escala = (
        "90-100: Supera los requisitos\n"
        "75-89:  Cumple sólidamente\n"
        "60-74:  Cumple con brechas menores\n"
        "45-59:  Insuficiente — brechas importantes\n"
        "0-44:   Claramente inadecuado"
    )

    # Sección de dimensiones a evaluar
    dims_texto = []
    for dim in dimensiones_activas:
        peso_pct = int(pesos[dim] * 100)
        criterios = desc_dimensiones[dim]
        dims_texto.append(f"- **{dim}** (peso {peso_pct}%): {criterios}")
    dims_bloque = "\n".join(dims_texto)

    # Competencias del perfil
    competencias = perfil_data.get("competencias", [])
    comp_texto = "\n".join(
        f"  - {c.get('nombre', '')} — peso {c.get('peso', '')}% — nivel requerido: {c.get('nivel_requerido', '')}"
        for c in competencias
    ) or "  (no especificadas)"

    # Requisitos
    req = perfil_data.get("requisitos", {})
    req_texto = (
        f"  Escolaridad mínima: {req.get('escolaridad_minima', 'No especificada')}\n"
        f"  Años de experiencia mínima: {req.get('anos_experiencia_min', 'No especificado')}\n"
        f"  Herramientas: {', '.join(req.get('herramientas', [])) or 'No especificadas'}\n"
        f"  Sector: {req.get('sector', 'No especificado')}"
    )

    # Rango salarial
    rango = perfil_data.get("rango_salarial", {})
    if rango.get("min") and rango.get("max"):
        rango_texto = (
            f"  ${rango['min']:,}–${rango['max']:,} {rango.get('moneda', 'MXN')} "
            f"{rango.get('tipo', 'neto')}"
        )
    else:
        rango_texto = "  No especificado"

    # JSON esperado
    json_esperado_dims = ",\n    ".join(
        f'"{dim}": {{"score": 0, "evidencia": ""}}'
        for dim in dimensiones_activas
    )
    json_esperado = "{\n    " + json_esperado_dims + "\n}"

    # Sección de transcripción
    if tiene_transcripcion:
        trans_bloque = f"\n## TRANSCRIPCIÓN DE ENTREVISTA\n\n{transcripcion_texto[:5000]}"
        modo_nota = "Score FINAL (incluye competencias blandas)."
    else:
        trans_bloque = ""
        modo_nota = "Score PRELIMINAR (sin entrevista — no evalúes competencias blandas; esa dimensión requiere entrevista)."

    prompt = f"""Eres un consultor DETA especializado en evaluación de candidatos para procesos de reclutamiento.

Debes evaluar al candidato en las siguientes dimensiones y devolver ÚNICAMENTE un JSON válido. Sin texto adicional, sin markdown, sin explicaciones.

---

## PERFIL DE PUESTO

Puesto: {perfil_data.get('puesto', '')}
Cliente: {perfil_data.get('cliente', '')}

Competencias requeridas:
{comp_texto}

Requisitos:
{req_texto}

Rango salarial:
{rango_texto}

---

## CV DEL CANDIDATO

{cv_texto[:5000]}
{trans_bloque}

---

## INSTRUCCIONES DE EVALUACIÓN

{modo_nota}

Evalúa cada dimensión de 0 a 100 usando esta escala:
{escala}

Dimensiones a evaluar:
{dims_bloque}

Para cada dimensión incluye:
- score: número entero 0-100
- evidencia: 1-2 oraciones concretas con la evidencia del CV o entrevista que justifican el score

---

## FORMATO DE RESPUESTA

Devuelve EXCLUSIVAMENTE este JSON, sin texto antes ni después:

{json_esperado}"""

    return prompt


# ─── CÁLCULO DE SCORE FINAL ───────────────────────────────────────────────────

def calcular_score_final(
    perfil_data: dict,
    scores_json: dict,
    cv_texto: str,
    tiene_transcripcion: bool,
    candidato_nombre: str = "",
) -> dict:
    """
    Recibe el dict de scores de Claude y calcula el score ponderado final.

    Args:
        perfil_data: dict extraído del bloque DETA_MATCHING_DATA
        scores_json: dict con dimensiones → {score, evidencia} (respuesta de Claude)
        cv_texto: texto del CV para detectar flags
        tiene_transcripcion: si hay entrevista determina qué fórmula usar
        candidato_nombre: nombre del candidato para el output

    Returns:
        Diccionario completo con score_total, nivel, dimensiones, flags, recomendacion
    """
    pesos = PESOS_CON_TRANSCRIPCION if tiene_transcripcion else PESOS_SIN_TRANSCRIPCION

    dimensiones_resultado = {}
    for dim, peso in pesos.items():
        dim_data = scores_json.get(dim, {})
        score = max(0, min(100, int(dim_data.get("score", 60))))
        dimensiones_resultado[dim] = {
            "score":     score,
            "peso":      peso,
            "ponderado": round(score * peso, 2),
            "evidencia": str(dim_data.get("evidencia", "")),
        }

    score_total = round(sum(d["ponderado"] for d in dimensiones_resultado.values()), 1)
    nivel = _determinar_nivel(score_total)
    flags = _generar_flags(perfil_data, cv_texto, dimensiones_resultado)

    return {
        "candidato":     candidato_nombre or "Candidato",
        "puesto":        perfil_data.get("puesto", ""),
        "cliente":       perfil_data.get("cliente", ""),
        "score_total":   score_total,
        "nivel":         nivel,
        "modo":          "completo" if tiene_transcripcion else "preliminar",
        "dimensiones":   dimensiones_resultado,
        "recomendacion": RECOMENDACIONES.get(nivel, ""),
        "flags":         flags,
    }


# ─── LÓGICA AUXILIAR ──────────────────────────────────────────────────────────

def _determinar_nivel(score: float) -> str:
    for minimo, nivel in NIVELES:
        if score >= minimo:
            return nivel
    return "No recomendado"


def _generar_flags(perfil_data: dict, cv_texto: str, dimensiones: dict) -> list:
    """Genera alertas automáticas basadas en datos del perfil y scores."""
    flags = []

    rango = perfil_data.get("rango_salarial", {})
    if rango.get("max"):
        for s in re.findall(r"\$\s*([\d,]+)", cv_texto):
            try:
                valor = int(s.replace(",", ""))
                if valor > rango["max"] * 1.15:
                    flags.append(
                        f"Expectativa salarial posiblemente fuera de rango "
                        f"(detectado: ${valor:,} / máximo: ${rango['max']:,} {rango.get('tipo', '')})"
                    )
                    break
            except ValueError:
                pass

    if dimensiones.get("escolaridad", {}).get("score", 100) < 60:
        flags.append("Escolaridad por debajo del mínimo requerido — validar con el cliente")

    if dimensiones.get("experiencia_tecnica", {}).get("score", 100) < 50:
        flags.append("Experiencia técnica insuficiente — considerar no avanzar")

    if dimensiones.get("condiciones", {}).get("score", 100) < 50:
        flags.append("Condición bloqueadora identificada — validar disponibilidad y salario")

    return flags


def _imprimir_resultado(r: dict):
    """Imprime el score final con formato legible en consola."""
    linea = "─" * 62
    nivel_emoji = {
        "Excepcional":    "🟢",
        "Sólido":         "🟢",
        "Con potencial":  "🟡",
        "Marginal":       "🟠",
        "No recomendado": "🔴",
    }.get(r["nivel"], "⚪")
    modo_label = "(preliminar — sin entrevista)" if r["modo"] == "preliminar" else "(score final)"

    print(f"\n{linea}")
    print(f"  MATCHING DETA — {r['puesto']} · {r['cliente']}")
    print(f"  Candidato: {r['candidato']}")
    print(linea)
    print(f"  Score total:  {r['score_total']} / 100  {nivel_emoji} {r['nivel']}  {modo_label}")
    print(linea)
    print("  Dimensiones:")
    for dim, datos in r["dimensiones"].items():
        barra = "█" * (datos["score"] // 10) + "░" * (10 - datos["score"] // 10)
        print(
            f"    {dim:<24} {datos['score']:>3}/100  [{barra}]"
            f"  ×{datos['peso']}  = {datos['ponderado']:>5.1f}"
        )
        if datos["evidencia"]:
            print(f"    {'':24}  → {datos['evidencia']}")
    print(linea)
    print(f"  Recomendación: {r['recomendacion']}")
    if r["flags"]:
        print(f"\n  ⚠️  Alertas:")
        for flag in r["flags"]:
            print(f"     • {flag}")
    print(linea)


# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

def correr_matching(
    ruta_perfil: str,
    ruta_cv: str,
    ruta_transcripcion: str = None,
    candidato_nombre: str = "",
):
    """
    Flujo completo de matching para uso desde terminal o Cowork:

    1. Extrae datos del perfil HTML
    2. Lee CV y transcripción
    3. Genera el prompt y lo imprime en stdout
    4. Espera el JSON de scores por stdin (pegado de la respuesta de Claude)
    5. Calcula y muestra el score final

    Args:
        ruta_perfil: ruta al HTML con bloque DETA_MATCHING_DATA
        ruta_cv: ruta al archivo .txt/.pdf del CV
        ruta_transcripcion: ruta a la transcripción de entrevista (opcional)
        candidato_nombre: nombre del candidato para el output
    """
    # Preparar datos
    perfil_data = extraer_matching_data(ruta_perfil)
    cv_texto = leer_texto(ruta_cv)
    trans_texto = leer_texto(ruta_transcripcion) if ruta_transcripcion else ""
    tiene_trans = bool(trans_texto.strip())

    # Generar e imprimir el prompt
    prompt = generar_prompt_matching(perfil_data, cv_texto, trans_texto)

    sep = "=" * 62
    print(f"\n{sep}")
    print("  PROMPT PARA COWORK — copiar y ejecutar con Claude")
    print(sep)
    print(prompt)
    print(sep)

    # Leer JSON de respuesta por stdin
    print("\nPega el JSON de respuesta de Claude y presiona Enter dos veces:")
    print("(o Ctrl+D para terminar)\n")

    lineas = []
    try:
        while True:
            linea = input()
            lineas.append(linea)
    except EOFError:
        pass

    respuesta_raw = "\n".join(lineas).strip()

    # Extraer JSON aunque venga con texto adicional
    json_match = re.search(r"\{.*\}", respuesta_raw, re.DOTALL)
    if not json_match:
        print("❌ No se encontró JSON válido en la respuesta. Abortando.")
        sys.exit(1)

    try:
        scores_json = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        sys.exit(1)

    # Calcular y mostrar score final
    resultado = calcular_score_final(
        perfil_data=perfil_data,
        scores_json=scores_json,
        cv_texto=cv_texto,
        tiene_transcripcion=tiene_trans,
        candidato_nombre=candidato_nombre,
    )
    _imprimir_resultado(resultado)
    return resultado


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    if len(sys.argv) >= 2 and sys.argv[1] == "--test":
        import tempfile, os

        print("🧪 Modo prueba — validando sin API key...")

        perfil_test = {
            "puesto": "Coordinador Administrativo",
            "cliente": "ACME Corp",
            "fecha": "2026-04-11",
            "competencias": [
                {"nombre": "Orientación a resultados", "peso": 30, "nivel_requerido": "B"},
                {"nombre": "Comunicación efectiva",    "peso": 30, "nivel_requerido": "B"},
                {"nombre": "Gestión de procesos",      "peso": 40, "nivel_requerido": "C"},
            ],
            "requisitos": {
                "escolaridad_minima": "Licenciatura en Administración",
                "anos_experiencia_min": 3,
                "herramientas": ["Excel", "SAP"],
                "sector": "Industrial",
            },
            "rango_salarial": {"min": 15000, "max": 25000, "moneda": "MXN", "tipo": "neto"},
        }
        html_test = (
            "<!DOCTYPE html>\n<html><body></body>\n"
            "<!--DETA_MATCHING_DATA\n"
            + json.dumps(perfil_test, ensure_ascii=False, indent=2)
            + "\n-->\n</html>"
        )
        cv_test = (
            "Carlos López, Lic. Administración UACH 2018. "
            "4 años coordinador administrativo en manufactura. "
            "Excel avanzado, SAP FI/CO. Expectativa: $22,000 netos."
        )

        # Test 1: extracción
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
            f.write(html_test)
            tmp = f.name
        data = extraer_matching_data(tmp)
        os.unlink(tmp)
        assert data["puesto"] == "Coordinador Administrativo"
        print("✅ Test 1 — extraer_matching_data: OK")

        # Test 2: prompt generation (sin transcripción → score preliminar)
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
            f.write(html_test)
            tmp = f.name
        perfil_data = extraer_matching_data(tmp)
        os.unlink(tmp)
        prompt = generar_prompt_matching(perfil_data, cv_test)
        assert "experiencia_tecnica" in prompt
        assert "EXCLUSIVAMENTE" in prompt
        assert "competencias_blandas" not in prompt  # no debe estar sin transcripción
        print("✅ Test 2 — generar_prompt_matching (preliminar): OK")

        # Test 3: prompt con transcripción → incluye competencias_blandas
        prompt_final = generar_prompt_matching(perfil_data, cv_test, "Candidato comunicativo y proactivo.")
        assert "competencias_blandas" in prompt_final
        print("✅ Test 3 — generar_prompt_matching (final con transcripción): OK")

        # Test 4: calcular_score_final con scores mock
        scores_mock = {
            "experiencia_tecnica":  {"score": 82, "evidencia": "4 años en coordinación administrativa."},
            "fit_organizacional":   {"score": 75, "evidencia": "Motivaciones alineadas con el puesto."},
            "escolaridad":          {"score": 90, "evidencia": "Licenciatura en Administración afín."},
            "condiciones":          {"score": 80, "evidencia": "Expectativa salarial dentro del rango."},
        }
        resultado = calcular_score_final(perfil_data, scores_mock, cv_test, False, "Carlos López")
        assert resultado["score_total"] == round(82*0.50 + 75*0.30 + 90*0.10 + 80*0.10, 1)
        assert resultado["nivel"] in ["Sólido", "Con potencial", "Excepcional"]
        print("✅ Test 4 — calcular_score_final: OK")

        # Test 5: niveles
        for score, esperado in [(95, "Excepcional"), (80, "Sólido"), (65, "Con potencial"),
                                 (50, "Marginal"), (30, "No recomendado")]:
            assert _determinar_nivel(score) == esperado
        print("✅ Test 5 — _determinar_nivel (5 niveles): OK")

        # Test 6: output formateado
        _imprimir_resultado(resultado)
        print("✅ Test 6 — _imprimir_resultado: OK")

        print("\n✅ Todos los tests pasaron. Script listo para usarse con Cowork.")

    elif len(sys.argv) < 3:
        print(
            "Uso:\n"
            "  python3 deta_matching.py <perfil.html> <cv.txt> [transcripcion.txt] [nombre]\n"
            "  python3 deta_matching.py --test\n"
            "\nEl script genera el prompt para Cowork, luego espera el JSON de respuesta por stdin."
        )
        sys.exit(1)

    else:
        ruta_perfil   = sys.argv[1]
        ruta_cv       = sys.argv[2]
        ruta_trans    = sys.argv[3] if len(sys.argv) > 3 else None
        nombre        = sys.argv[4] if len(sys.argv) > 4 else ""
        correr_matching(ruta_perfil, ruta_cv, ruta_trans, nombre)
