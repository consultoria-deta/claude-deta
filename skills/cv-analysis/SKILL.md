---
name: cv-analysis
description: >
  Skill para scraping de candidatos OCC + scoring CV/Perfil para cualquier vacante.
  Úsalo cuando el usuario pida: extraer candidatos de OCC, descargar CVs, score o
  matching de candidatos, recomendar quién entrevistar, análisis de pool, ranking de
  postulantes, o cualquier combinación de scraping y evaluación de talento. También
  activa cuando el usuario mencione una vacante OCC y quiera saber quiénes valen la pena.
  Si el usuario da un job_id, un perfil de puesto o un CV y pide evaluación, usa este skill.
---

# CV Analysis — OCC Scraping + Matching DETA

Dos fases combinables según lo que pida el usuario:

- **Fase 1 — Scraping:** extrae candidatos de OCC (login MCP → IDs vía API interna → descarga Python playwright → extracción de datos → Sheets)
- **Fase 2 — Matching:** scoring CV/Perfil con fórmula DETA, filtrado de candidatos que no vale la pena entrevistar

Por default correr ambas. Si ya hay CVs descargados, ir directo a Fase 2.

---

## Antes de empezar — recolectar inputs

Preguntar solo lo que falte. No pedir todo si el contexto ya lo da.

| Input | Para qué sirve | Cómo obtenerlo |
|-------|---------------|----------------|
| `JOB_ID` | URL de cada candidato en OCC | De la URL: `.../administrador/{JOB_ID}` |
| `CV_IDS` | Saber a quiénes procesar | Listado explícito, o descubrir via scraping |
| `SHEET_ID` | Escribir resultados | ID del Google Sheet (URL) |
| `CV_DIR` | Guardar CVs descargados | Carpeta en Drive File Stream |
| `PERFIL` | Base del matching | HTML con bloque DETA_MATCHING_DATA, PDF, o descripción libre |
| `CRITERIOS` | Calibrar el scoring | Input de Joel (ver sección Matching) |

---

## Fase 1 — Scraping OCC

**Estrategia download-first:** descargar todos los CVs primero, luego extraer datos de los archivos. Esto es más rápido que esperar la carga de React por cada candidato y produce datos más completos.

### Herramientas

- **MCP Playwright** (`mcp__plugin_playwright_playwright__*`): para login y descubrimiento de IDs.
- **Python playwright** (`playwright.async_api`): para la descarga masiva de CVs. Es más eficiente y confiable que el MCP porque no satura el contexto con snapshots de DOM por cada candidato.

### Paso 1.1 — Login (MCP Playwright)

```
browser_navigate → https://empresa.occ.com.mx/Login
```

Llenar `input[type='email']` + `input[type='password']` → submit.
Verificar redirección a `/hirer-center/`. Si falla: screenshot y reportar.

Credenciales por default:
```
email:    XXXXXXXX
password: XXXXXXXX
```

### Paso 1.2 — Descubrir todos los CV IDs (MCP Playwright)

**Opción A — API interna OCC (preferida, >50 candidatos):**

Con la sesión activa, usar `browser_evaluate` para llamar a la API interna que devuelve todos los IDs en una sola llamada:

```javascript
// Ejecutar en browser_evaluate estando en la página de candidatos
async () => {
  const res = await fetch('/api/amadeus/candidates', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ jobId: JOB_ID, page: 1, pageSize: 500 })
  });
  const data = await res.json();
  return data.candidates?.map(c => c.id) || data;
}
```

Si el response tiene paginación, incrementar `page` hasta agotar resultados. Guardar todos los IDs en `/tmp/occ_ids_{JOB_ID}.txt`.

**Opción B — DOM scraping (fallback):**

Navegar a `https://www.occ.com.mx/empresas/candidatos/administrador/{JOB_ID}` y ejecutar:

```javascript
[...document.querySelectorAll('a[href*="/cv/"]')]
  .map(a => a.href.match(/\/cv\/(\d+)/)?.[1])
  .filter(Boolean)
  .filter((v, i, arr) => arr.indexOf(v) === i)
```

Si hay paginación, navegar página siguiente y repetir hasta agotar IDs. Recolectar todos los IDs antes de descargar cualquier CV.

### Paso 1.3 — Extraer cookies de sesión (MCP Playwright)

Antes de lanzar el script Python, extraer las cookies del browser MCP que tiene la sesión activa:

```javascript
// Ejecutar en browser_evaluate
() => {
  const sr = document.cookie.split('; ').find(c => c.startsWith('_sr='));
  const token = sr ? JSON.parse(atob(decodeURIComponent(sr.split('=').slice(1).join('=')))).passport?.user?.accessToken : null;
  return { cookies: document.cookie, accessToken: token };
}
```

Guardar el string completo de `cookies` para usarlo en el script Python.

### Paso 1.4 — Descargar todos los CVs (Python playwright)

Usar Python playwright headless para la descarga masiva. Evita saturar el contexto con 40+ snapshots de DOM.

**Prioridad de descarga:**
1. **Adjunto real** — botón cuyo texto termina en `.pdf`, `.doc` o `.docx` (el archivo que subió el candidato)
2. **Fallback OCC** — botón `"Descarga CV"` (PDF generado por OCC con el perfil del postulante)

El adjunto real es preferible porque contiene más detalle y es el CV que el candidato preparó intencionalmente.

```python
# /tmp/download_cvs_{JOB_ID}.py
import asyncio, os, shutil, re
from pathlib import Path
from playwright.async_api import async_playwright

CV_DIR = "{CV_DIR}"
JOB_ID = "{JOB_ID}"
COOKIE_STR = "{cookie_string_del_paso_1.3}"
CV_IDS = [{lista_de_ids}]

def already_downloaded(cv_id):
    return any(f.startswith(str(cv_id) + '_') for f in os.listdir(CV_DIR))

async def download_cv(page, cv_id):
    url = f"https://www.occ.com.mx/empresas/candidatos/{JOB_ID}/cv/{cv_id}?status=0&o=1&view=app"
    try:
        r = await page.goto(url, wait_until='domcontentloaded', timeout=20000)
        if not r or r.status >= 400:
            print(f"SKIP {cv_id}: HTTP {r.status if r else 'none'}")
            return False
        await asyncio.sleep(3)  # esperar carga de React

        # Prioridad 1: adjunto real (botón con extensión de archivo)
        adjunto = await page.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b =>
                /\\.(pdf|doc|docx)$/i.test(b.textContent.trim()) &&
                !b.textContent.trim().startsWith('Descarga'));
            return btn ? btn.textContent.trim() : null;
        }""")

        if adjunto:
            selector = f'button:has-text("{adjunto}")'
        else:
            try:
                await page.wait_for_selector('button:has-text("Descarga CV")', timeout=5000)
                selector = 'button:has-text("Descarga CV")'
            except:
                print(f"SKIP {cv_id}: sin botón de descarga")
                return False

        async with page.expect_download(timeout=20000) as dl_info:
            await page.click(selector)

        dl = await dl_info.value
        orig = dl.suggested_filename
        tmp = f"/tmp/occ_dl_{cv_id}_{orig}"
        await dl.save_as(tmp)

        clean = re.sub(r'[^\w\-.]', '_', orig)[:80]
        shutil.move(tmp, os.path.join(CV_DIR, f"{cv_id}_{clean}"))
        print(f"OK {cv_id}: {orig}")
        return True
    except Exception as e:
        print(f"ERROR {cv_id}: {e}")
        return False

async def main():
    to_dl = [i for i in CV_IDS if not already_downloaded(i)]
    print(f"Descargando {len(to_dl)}/{len(CV_IDS)} CVs...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(accept_downloads=True)
        cookies = [{'name': k, 'value': v, 'domain': '.occ.com.mx', 'path': '/'}
                   for part in COOKIE_STR.split('; ') if '=' in part
                   for k, v in [part.split('=', 1)]]
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()

        ok, failed = 0, []
        for i, cv_id in enumerate(to_dl, 1):
            print(f"[{i}/{len(to_dl)}] {cv_id}...")
            if await download_cv(page, cv_id): ok += 1
            else: failed.append(cv_id)
            await asyncio.sleep(1)

        await browser.close()
        print(f"\nFin: {ok}/{len(to_dl)} OK. Fallidos: {failed}")

asyncio.run(main())
```

Correr en background: `python3 /tmp/download_cvs_{JOB_ID}.py &`

Monitorear con: `tail -f /tmp/download_cvs_{JOB_ID}.log`

### Paso 1.5 — Extraer datos de CVs descargados

Una vez descargados todos los CVs, extraer texto y parsear contacto:

```bash
# Para .docx
textutil -convert txt -stdout archivo.docx

# Para .pdf
pdftotext archivo.pdf -
# Fallback si pdftotext no está:
python3 -c "import subprocess; print(subprocess.run(['textutil','-convert','txt','-stdout','archivo.pdf'], capture_output=True, text=True).stdout)"
```

De cada CV extraer:
- **Nombre:** primeras 3-5 líneas no vacías suelen contener el nombre
- **Email:** regex `[\w.+-]+@[\w.-]+\.(com|mx|net|org)` — filtrar dominios de plataformas (occ.com, gmail en contextos de firma corporativa sospechosa)
- **Teléfono:** regex `(\+52\s?)?[\d\s\-\(\)]{10,15}` — limpiar espacios y guiones
- **Expectativa salarial:** buscar patrones como `$XX,XXX`, `XX mil`, `expectativa`, `pretensión`

**Fallback si el CV no tiene email:** usar el extractor de React fiber de OCC navegando de nuevo a la página del candidato (ver sección "Extractor React fiber" en Notas operativas).

### Paso 1.6 — Obtener links de Drive

Los archivos en Drive File Stream sincronizan automáticamente. Obtener los webViewLinks vía Drive API:

```bash
TOKEN=$(gcloud auth print-access-token)

# Obtener ID de la carpeta CV_DIR en Drive (hacer una sola vez)
FOLDER_ID=$(curl -s \
  "https://www.googleapis.com/drive/v3/files?q=name%3D'CVs'+and+trashed%3Dfalse&fields=files(id,name)" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; f=json.load(sys.stdin)['files']; print(f[0]['id'] if f else '')")

# Listar todos los archivos en la carpeta (hasta 200 por página)
curl -s \
  "https://www.googleapis.com/drive/v3/files?q='${FOLDER_ID}'+in+parents+and+trashed%3Dfalse&fields=files(id,name,webViewLink)&pageSize=200" \
  -H "Authorization: Bearer $TOKEN"
```

Construir un dict `{cv_id: webViewLink}` para usar en el paso de Sheets.

### Paso 1.7 — Escribir en Google Sheets

Autenticación: `gcloud auth print-access-token`

**Nombre correcto del tab:** `Candidatos seleccionados` (con espacio, no `Candidatos`). Siempre entrecomillar en la URL: `'Candidatos%20seleccionados'`.

**Primera escritura (vacante nueva):**
1. `POST .../values/'Candidatos seleccionados'!A1:clear` para limpiar
2. `PUT .../values/'Candidatos seleccionados'!A1` con headers + datos, `valueInputOption=USER_ENTERED`

**Scoring en lotes (append):**
Cuando el scoring corre en múltiples agentes paralelos, cada agente **NO debe limpiar** la hoja — solo encontrar la última fila ocupada y hacer append:
```bash
# Obtener última fila con datos
curl -s "https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/'Candidatos%20seleccionados'!A:A" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys,json; d=json.load(sys.stdin); print(len(d.get('values',[])))
"
# Luego append desde esa fila + 1
```

Columnas estándar: `#, Nombre, Email, Teléfono, CV_ID, Link_OCC, Link_CV_Drive, Score, Nivel, Estado, Notas, Expectativa_Salarial`

- `Link_OCC`: `https://www.occ.com.mx/empresas/candidatos/{JOB_ID}/cv/{cv_id}`
- `Link_CV_Drive`: `=HYPERLINK("webViewLink","Ver CV")` — clickeable en Sheets
- Si el matching ya se corrió, escribir Score/Nivel/Estado en la misma llamada.
- Si se corre después, actualizar columnas H-L por fila con `batchUpdate`.

---

## Fase 2 — Matching CV/Perfil

### Estrategia de ejecución — scoring por agentes en lotes

Con >40 CVs, el scoring en un solo agente satura el contexto. Usar agentes en paralelo:

- **Lote máximo:** 40-50 CVs por agente
- **Lanzar en paralelo** con `Agent(run_in_background=True)` — uno por lote
- Cada agente recibe: lista de IDs, CV_DIR, SHEET_ID, PERFIL, CRITERIOS
- Cada agente hace **append** (no clear) al Sheets — calcular su fila de inicio antes de escribir
- Monitorear con `SendMessage` si tarda más de 5 min

Con 150 candidatos, lanzar 3-4 agentes en paralelo reduce el tiempo total de ~60 min a ~20 min.

### Paso 2.0 — Calibrar con Joel antes de scorear

Hacer estas tres preguntas si no están en el contexto:

1. **¿Qué pesa más para este puesto?** (ej. experiencia comercial sobre conocimiento técnico, o al revés)
2. **¿Hay sectores de experiencia previa que prefieras o que descarten automáticamente?**
3. **¿Cuál es el requisito no negociable (must-have) sin el cual no tiene caso entrevistar?**

Las respuestas se convierten en `CRITERIOS_CLIENTE` y en la lista de `MUST_HAVES`.

### Paso 2.1 — Filtros automáticos always-on

Antes de cualquier otro análisis, verificar dos condiciones. Si no pasan → score 0, estado "Descartado — filtro automático", sin gastar tokens en dimensiones.

**Filtro geográfico**
El candidato debe residir en `CIUDAD_VACANTE`. Si su ubicación en OCC o CV no coincide → descartar automáticamente.
Excepción: solo si Joel indicó explícitamente en el kickoff que acepta candidatos de fuera.

**Filtro salarial**
Si la expectativa del candidato supera el 130% del techo del rango salarial ofrecido → descartar.
- Ejemplo: rango $25,000. Techo = $25,000. 130% = $32,500. Expectativa > $32,500 → descartado.
- Excepción: si el rol incluye comisiones (OTE), evaluar solo el componente fijo.
- Si el candidato no especifica expectativa → no descartar, anotar "sin dato" en condiciones y asumir score 60.

### Paso 2.2 — Filtro must-have (antes de calcular score)

Antes de scorear, verificar si el candidato cumple los must-haves definidos por Joel. Si no cumple alguno → score automático de 0, estado "Descartado — no cumple requisito mínimo", documentar cuál faltó. No gastar tokens calculando dimensiones.

Ejemplos de must-haves típicos:
- "Mínimo 2 años de experiencia en ventas" → verificar en CV
- "Escolaridad mínima: licenciatura" → verificar en CV
- "Disponibilidad para viajar" → verificar si se menciona

### Paso 2.3 — Scoring con fórmula DETA

**Fórmula sin entrevista:**
```
Score = (experiencia_tecnica × 0.50) + (fit_organizacional × 0.20)
      + (escolaridad × 0.10) + (condiciones × 0.10) + (must_haves_bonus × 0.10)
```

El fit organizacional baja de 30% a 20% sin entrevista porque es difícil leer cultura y motivación solo desde el papel — el 10% restante va a un bonus por cumplimiento explícito de must-haves.

**Escala:**
```
90-100 → Excepcional   | Avanzar de inmediato
75-89  → Sólido        | Avanzar
60-74  → Con potencial | Avanzar con reservas
45-59  → Marginal      | En espera
0-44   → No recomendado| No continuar
```

### Paso 2.4 — Prompt de evaluación por candidato

Usar este template. La sección `CRITERIOS_ADICIONALES` es obligatoria y cambia por vacante:

```
Eres evaluador DETA. Devuelve ÚNICAMENTE el JSON solicitado, sin texto adicional.

## PERFIL DE PUESTO
Puesto: {puesto}
Cliente: {cliente}
Competencias: {lista}
Requisitos: escolaridad mínima {X}, experiencia mínima {Y} años, sector {Z}
Rango salarial: ${min}–${max} MXN neto

## CRITERIOS ADICIONALES DEL CLIENTE
{CRITERIOS_CLIENTE}

Aplica estos criterios al evaluar experiencia_tecnica y fit_organizacional.
Evalúa por compatibilidad de responsabilidades reales, no por coincidencia
exacta de palabras clave o sector. Un candidato de otro sector puede tener
las mismas responsabilidades con diferente vocabulario.

## CV DEL CANDIDATO
{cv_texto[:5000]}

## INSTRUCCIONES
Score PRELIMINAR — sin entrevista. No evalúes competencias blandas.

Para cada dimensión, asigna un score de 0-100 usando estas anclas:
- 90-100: evidencia directa y cuantificada que supera los requisitos
- 75-89:  evidencia clara que cumple sólidamente, con métricas o progresión visible
- 60-74:  cumple con brechas menores o evidencia parcial sin métricas
- 45-59:  evidencia insuficiente o muy genérica
- 0-44:   ausencia de evidencia relevante o perfil claramente no alineado

Dimensiones:
- experiencia_tecnica (50%): trayectoria en áreas del puesto, profundidad, progresión con resultados
- fit_organizacional (20%): señales de alineación motivacional, tipo de empresa, autonomía esperada. **Penalización jerárquica:** si el último puesto del candidato es significativamente más senior que la vacante, bajar este score: 1 nivel arriba (ej. Jefe→Coordinador) → -10 pts; 2+ niveles (Gerente/Director→Coordinador) → -20 pts. Documentar riesgo de sobrecalificación en evidencia.
- escolaridad (10%): nivel mínimo cumplido, afinidad de carrera
- condiciones (10%): expectativa salarial vs rango, disponibilidad. Si no hay datos: 60
- must_haves_bonus (10%): 100 si cumple todos los must-haves, 50 si cumple parcialmente, 0 si no cumple alguno

La evidencia debe ser concreta: citar el puesto, empresa, logro o dato del CV que justifica el score.
No usar afirmaciones genéricas como "tiene experiencia en ventas".

## RESPUESTA (solo JSON):
{
  "experiencia_tecnica": {"score": 0, "evidencia": ""},
  "fit_organizacional":  {"score": 0, "evidencia": ""},
  "escolaridad":         {"score": 0, "evidencia": ""},
  "condiciones":         {"score": 0, "evidencia": ""},
  "must_haves_bonus":    {"score": 0, "evidencia": ""}
}
```

### Paso 2.5 — Output del ranking

```
RANKING — {Puesto} · {Cliente}
Criterios aplicados: {resumen de CRITERIOS_CLIENTE}
Must-haves: {lista}

#1  Nombre Apellido         79.1 / 100  Sólido → Avanzar
    exp_tecnica: 82  fit_org: 75  escolaridad: 70  condiciones: 65  must_haves: 100
    Evidencia clave: [cita concreta del CV]
    ⚠️ [flag si aplica]

DESCARTADOS — no cumplen must-have:
- Nombre (falta: experiencia mínima en ventas) → No entrevistar

NO RECOMENDADOS (score < 45):
- Nombre (32) — perfil técnico/operativo sin evidencia comercial
```

---

## Fase 3 — Reporte HTML interactivo

Al terminar el scoring de todos los candidatos, generar un HTML interactivo con los top 10 y guardarlo en la carpeta `HTMLs scrap` dentro del directorio del reclutamiento.

### Ruta de guardado
`{RECLUTAMIENTO_DIR}/HTMLs scrap/reporte_{puesto}_{cliente}_{YYYYMMDD}.html`

### Datos a incluir
Leer el Sheets final con todos los candidatos y extraer:
- Top 10 por score (solo los que llegaron a scoring, no descartados)
- Para cada candidato: #, Nombre, Email, Teléfono, CV_ID, Link_OCC, Link_CV_Drive, Score, Nivel, Estado, Notas, Expectativa_Salarial
- Resumen de filtros aplicados (cuántos por cada filtro)

### Estructura del HTML

```html
<!DOCTYPE html>
<html lang="es">
<!-- Self-contained — sin dependencias externas excepto CDN de Tailwind -->
<head>
  <meta charset="UTF-8">
  <title>Top Candidatos — {Puesto} · {Cliente}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 font-sans p-8">

  <!-- Header -->
  <div class="mb-8">
    <h1>Top 10 Candidatos</h1>
    <p>{Puesto} · {Cliente} · {Fecha}</p>
    <!-- Resumen de filtros: X geo + X salarial + X must-have descartados, X a scoring -->
  </div>

  <!-- Cards top 10 — una card por candidato -->
  <!-- Cada card incluye: nombre, score badge, nivel, estado, dimensiones (barra o números),
       evidencia clave (colapsable), email, teléfono, botones "Ver CV Drive" y "Ver en OCC" -->

  <!-- Tabla completa colapsable con todos los candidatos incluyendo descartados -->

</body>
</html>
```

### Interactividad mínima requerida
- **Ordenar** por score (default), nombre, o nivel con click en columna
- **Expandir/colapsar** evidencia por candidato (accordion)
- **Filtrar** por estado (Entrevistar / Considerar / En espera / Descartado)
- **Botones directos** "Ver CV" (Drive) y "Ver en OCC" — abrir en nueva pestaña
- **Tabla completa** de todos los candidatos al final, colapsable

### Datos de dimensiones
Mostrar los 5 scores dimensionales visualmente (barras de progreso o números):
`exp_técnica · fit_org · escolaridad · condiciones · must_haves`

El HTML debe ser self-contained (sin archivos externos locales) y abrir correctamente desde Finder con doble click.

---

## Fase 4 — Contacto y agendado por WhatsApp

Cierre del flujo: tras aprobación de candidatos, el agente los contacta por WA, pre-califica con 2-3 preguntas, agenda entrevista por Meet e invita por correo.

**Requisitos previos:**
- Bridge WhatsApp corriendo (LaunchAgent `com.deta.whatsapp-bridge`, log en `~/Library/Logs/whatsapp-bridge.log`)
- MCP `whatsapp` cargado en la sesión (ver tools `mcp__whatsapp__*`). Si no aparece, reiniciar Claude Code
- MCP `Google Calendar` nativo de claude.ai conectado (para crear evento + invitar por correo + Meet link)

### Paso 4.0 — Cargar configuración de la vacante

**Antes de nada, leer** `~/.claude/projects/-Users-joelestrada/memory/project_vacantes-abiertas.md` y localizar la entrada YAML de la vacante por `id` o por `cliente + puesto`. De ahí sale todo:

- `sheet_id`, `occ_job_id`, `cv_dir`, `perfil_puesto_path`
- `salario_ofertado`, `salario_umbral_descarte`
- `must_haves`
- `preguntas_prefiltro` (orden + tipo + pregunta + regla_descarte + columna_sheet)
- `ventanas_entrevista`, `attendees_evento`, `calendar_owner`, `contacto_top_n`

Si falta algún campo → preguntar a Joel, completar la ficha en el archivo y continuar. **No improvisar valores.**

### Paso 4.1 — Jalar datos del Sheets

Dos modos de selección, los dos válidos:

- **Modo top-N:** Joel dice "top 5" o equivalente → leer `contacto_top_n` de la ficha (o el número del chat) y tomar los N candidatos de mayor Score.
- **Modo lista específica:** Joel dicta nombres concretos en el chat ("contacta a Juan Pérez, María López y Andrés Ruiz") → buscar esos candidatos en el sheet por nombre (match por primer nombre + apellido paterno; si hay ambigüedad, preguntar a Joel). Ignorar Score.

En cualquiera de los dos modos, extraer para cada candidato seleccionado:

| Campo | Origen | Formato |
|-------|--------|---------|
| nombre | Sheet | primer nombre + apellido paterno |
| telefono | Sheet | normalizar a `521XXXXXXXXXX` (MX), sin `+` |
| email | Sheet | si existe; si no, pedírselo al candidato |
| genero | Sheet columna `Genero` si existe; si no, inferir del primer nombre |

Si falta teléfono o es inválido → marcar `sin contacto` y excluir del envío.

### Paso 4.2 — Inferencia de género (solo pronombres)

- Claramente M: Juan, Carlos, Luis, Pedro, Jorge, Miguel, Raúl, Fernando, etc.
- Claramente F: María, Ana, Laura, Sofía, Carmen, Gabriela, Fernanda, etc.
- Ambiguo (Guadalupe, Andrea, Trinidad, Reyes, Cruz, Alex): `N` → flag `revisar pronombre` en el checkpoint. Para `N`, en el copy se usan formas neutras (`te interesa`, `te acomoda`), ningún adjetivo con `-o/-a`.

### Paso 4.3 — Checkpoint de validación (obligatorio)

Antes del primer envío del lote, presentar a Joel:

```
VALIDACIÓN DE CONTACTO — {puesto} · {cliente}
─────────────────────────────────────────────
Top-N: {N}       Ventana hoy: {HH:MM}-{HH:MM}       Slots 30min: {cantidad}

Preguntas pre-calificación (orden):
  1. [salarial]  {pregunta_1}
                 Regla descarte: {regla_1}
  2. [registro]  {pregunta_2}
                 Columna sheet: {columna}
  3. [agenda]    {pregunta_3}

Tabla de candidatos (con plantilla M1 asignada):
  #  Nombre              Teléfono         Género  Email sheet     Plantilla  Flag
  1  Juan Pérez          5216141234567    M       ana@x.com       A          ok
  2  Guadalupe Ruiz      5216149999999    N       —               B          sin email → pedir
  3  Ana López           5216141111111    F       ana@x.com       C          ok
  ...

Copy del Mensaje 1 (ejemplo con Juan):
  {texto verbatim aquí}
```

Esperar `OK` de Joel. Si pide ajuste (quitar a alguien, cambiar copy, corregir género, cambiar pregunta) → aplicar y volver a presentar. Tras `OK`, los envíos son automáticos.

### Paso 4.3.5 — Humanización (obligatorio antes de cada envío)

Objetivo: que los mensajes no se lean como bot. Aplica a **todos** los mensajes del flujo, no solo al primero.

**a) Typing indicator + delay antes de enviar**

Antes de cada `mcp__whatsapp__send_message`:
1. Activar presencia "escribiendo" con `mcp__whatsapp__set_typing` (o equivalente del bridge). Si la tool no está disponible aún, reportar a Joel y continuar sin typing.
2. Esperar un delay proporcional al largo del mensaje: ~40 ms por carácter, con mínimo 4s y máximo 12s. Un mensaje de 200 chars → ~8s.
3. Desactivar typing y enviar.

En respuestas del candidato, sumar además un retraso inicial de 20–90s antes de arrancar a "escribir" (nadie contesta en 3s). Distribuir con algo de azar para no caer siempre en el mismo número.

**b) Variación de copy — romper uniformidad**

Para cada mensaje del flujo (M1, M2, M3, M4, cierre) mantener **2–3 plantillas** que:
- Conservan la estructura y el contenido crítico (pregunta, pre-calificación, slots, etc.)
- Varían apertura, conectores, puntuación, orden de frases y cierre
- Respetan la voz Joel (ver "Reglas de tono")

Al disparar el lote, asignar plantilla por candidato con una rotación simple (módulo del índice) o aleatoria. Nunca dos candidatos consecutivos con la misma plantilla. Si dos candidatos se conocen o trabajan en la misma empresa (flag en el sheet si aplica), forzar plantillas distintas.

Las plantillas viven en `Paso 4.4` — cada mensaje enumera sus variantes `A/B/C`.

### Paso 4.4 — Scripts verbatim (voz Joel, plantillas A/B/C por mensaje)

Para cada mensaje hay 2–3 plantillas equivalentes. Solo varía `{nombre}`, `{puesto}`, `{cliente}`, y la rotación de plantilla según Paso 4.3.5(b). Formas `-o/-a/-neutro` según género.

#### Mensaje 1 — Saludo + presentación + permiso

Rotar entre las 3 plantillas. Para género `N` usar `trayectoria` en lugar de `experiencia`/`perfil`.

**Plantilla A:**
```
Hola {nombre}. Soy Joel Estrada, de DETA Consultores. Vimos tu perfil
en OCC aplicando a la vacante de {puesto} con {cliente}, y nos llamó
la atención tu experiencia.

¿Tienes unos minutos para tres preguntas rápidas y, si encajamos,
agendar una videollamada?
```

**Plantilla B:**
```
Hola {nombre}, ¿qué tal? Te escribe Joel Estrada de DETA Consultores.
Revisamos tu postulación en OCC para la vacante de {puesto} en
{cliente} y tu experiencia nos pareció interesante.

¿Tendrías un momento para tres preguntas cortas? Si encaja, te
agendo una videollamada.
```

**Plantilla C:**
```
Hola {nombre}. Joel Estrada, de DETA Consultores. Nos llegó tu perfil
desde OCC para {puesto} con {cliente} y queríamos platicar.

Son tres preguntas rápidas y, si hace match, agendamos una
videollamada. ¿Te queda un momento?
```

Esperar respuesta. Si es afirmativa → Mensaje 2. Si es negativa → ver Paso 4.7.

#### Mensaje 2 — Pregunta 1 (salario)

Rotar entre las 2 plantillas:

**Plantilla A:**
```
Gracias. Primera: ¿cuál es tu expectativa salarial mensual? ¿La manejas
en libre (neto en mano) o en bruto?
```

**Plantilla B:**
```
Perfecto. Primero: ¿cuánto buscas de sueldo mensual, y lo tienes
pensado en libre (lo que te llega al banco) o en bruto?
```

**Lógica de descarte salarial (usar sentido común):**

Interpretar la respuesta en contexto mexicano y salarial:
- `"25"`, `"25k"`, `"25 mil"`, `"veinticinco mil"` → mismo valor: 25,000 MXN
- `"25 brutos"`, `"25 mil bruto"`, `"antes de impuestos"` → bruto aclarado, no re-preguntar
- `"25 libres"`, `"25 en mano"`, `"netos"`, `"después de impuestos"`, `"lo que me llega"` → libre aclarado, no re-preguntar
- Solo una cifra sin modalidad → re-preguntar natural usando su misma cifra:
  ```
  ¿Esos {monto_que_dijo} son libres (lo que te llega al banco) o brutos
  (antes de impuestos)?
  ```

Con cifra + modalidad aclarada:
   - Si `monto libre > salario_umbral_descarte` → descarte salarial (ver 4.7).
   - Si `monto bruto` → avisar a Joel para conversión, no decidir automático. Guardar y continuar al siguiente paso mientras Joel decide.
   - Si `monto libre ≤ umbral` → pasa al Mensaje 3.

**Registrar en sheet** (crear columna si no existe): `Expectativa_Salarial` (`{monto} {libre|bruto}`).

#### Mensaje 3 — Pregunta 2 (estado laboral actual)

Rotar entre las 2 plantillas:

**Plantilla A:**
```
Perfecto. Segunda: ¿estás trabajando actualmente? Si sí, ¿en qué empresa
y qué puesto?
```

**Plantilla B:**
```
Va. Ahora: ¿ahorita estás trabajando? Si es así, cuéntame en dónde y
qué estás haciendo.
```

**Registrar** en la columna del sheet definida en `preguntas_prefiltro[2].columna_sheet` (para DISAL: `Estado_Laboral_Actual`). Si la columna no existe, **crearla**. Formato: `Sí — {empresa} / {puesto}` o `No`.

**No descarta.** Siempre continuar al Mensaje 4.

#### Mensaje 4 — Pregunta 3 (disponibilidad) + email

Ofrecer hasta 3 slots concretos dentro de la `ventana_entrevista` del día. Rotar entre las 2 plantillas:

**Plantilla A:**
```
Última: tengo disponibilidad hoy para una videollamada de 30 minutos
por Meet en estos espacios:

• {slot A — ej. "3:00 pm"}
• {slot B — ej. "4:30 pm"}
• {slot C — ej. "6:00 pm"}

¿Te queda alguno? Y confírmame por favor tu correo para mandarte la
invitación con el link de Meet.
```

**Plantilla B:**
```
Última: hoy tengo estos horarios para una videollamada de 30 min por
Meet:

• {slot A}
• {slot B}
• {slot C}

¿Cuál te acomoda? Mándame también tu correo para enviarte la
invitación con el Meet.
```

Máximo 3 slots por ofrecimiento. Si ninguno le queda:

```
Sin problema. Déjame checar más espacios y te escribo en unos minutos.
```

Entonces **pausar al candidato y pedir a Joel más ventanas** (ver Paso 4.6). No ofrecer slots no autorizados bajo ningún motivo.

#### Mensaje 5 — Confirmación + evento

Una vez que el candidato da slot + email:

1. **Validar email** (regex básico, no vacío).
2. **Crear evento** con `mcp__claude_ai_Google_Calendar__gcal_create_event`:
   - `calendarId`: valor de `calendar_owner` en la ficha
   - `summary`: `Entrevista DETA · {puesto} · {nombre_candidato}`
   - `description`: texto con cliente, puesto, teléfono del candidato, score, columnas clave del sheet (estado laboral, expectativa salarial)
   - `start` / `end`: slot elegido, 30 min, timezone `America/Mexico_City`
   - `attendees`: `[email_candidato, ...attendees_evento de la ficha]`
   - `conferenceData`: crear Meet automático (pedir `conferenceDataVersion: 1` si el MCP lo expone)
   - `sendUpdates`: `all` — que gcal dispare la invitación por correo al candidato
3. **Confirmar por WA:**
   ```
   Listo, {nombre}. Te agendé para hoy a las {hora}. Ya te llegó al correo
   la invitación con el link de Meet.

   Si por cualquier motivo surge algo, avísame con tiempo.
   ```
4. **Actualizar sheet:** columna `Estado_Contacto` = `Agendado {fecha} {hora}`; columna `Email_Confirmado` = email del candidato; columna `Meet_URL` = link.

### Paso 4.5 — Candidato descarta / no cumple / no responde

- **No quiere continuar (Mensaje 1 negativo):**
  ```
  Gracias por avisarme. Suerte con lo que viene.
  ```
  Sheet: `Estado_Contacto` = `No interesó contacto`.

- **Descartado por filtro salarial (Paso 4.4 Mensaje 2):**
  ```
  Gracias por la claridad, {nombre}. Por ahora la expectativa queda fuera
  del rango de esta vacante, así que la cerramos aquí. Si tenemos otra
  búsqueda que encaje, te escribo.
  ```
  Sheet: `Estado_Contacto` = `Descartado — salarial`.

- **No responde en 24h:** flag a Joel con el candidato pendiente. Sheet: `Estado_Contacto` = `Sin respuesta 24h`. No hacer follow-up automático.

### Paso 4.6 — Ventanas extra (cuando se agotan los slots)

Si un candidato no puede en ninguna ventana autorizada:
1. Mandar el mensaje puente ("Déjame checar más espacios…").
2. Decirle a Joel en chat: `{nombre}` pidió otra ventana. Ventanas actuales autorizadas agotadas para él. ¿Qué ventanas extra autorizas?
3. Esperar a que Joel dicte ventanas nuevas. Agregarlas a la ficha en `project_vacantes-abiertas.md`.
4. Retomar al candidato con el Mensaje 4 usando los nuevos slots.

Nunca inventar horas ni ofrecer "cuando te acomode" abierto.

### Paso 4.7 — Cierre de la fase

Cuando todos los candidatos del lote quedaron en estado terminal (agendado, descartado, no interesó, sin respuesta):

1. Asegurar que todas las columnas quedaron escritas en el sheet: `Estado_Contacto`, `Expectativa_Salarial`, `Estado_Laboral_Actual`, `Email_Confirmado`, `Meet_URL`.
2. Reportar a Joel un resumen en un bloque:
   ```
   CIERRE CONTACTO — {puesto} · {cliente} · {fecha}
   Agendados: N   {nombre1 → hora, nombre2 → hora, …}
   Descartados salarial: N   {nombres}
   No interesó: N   {nombres}
   Sin respuesta: N   {nombres}
   ```
3. Actualizar el Kanban en `project_vacantes-abiertas.md`: mover la task "Contactar top 5" a Done.
4. **Fin.** Recordatorios, reagendas, dudas del candidato antes de la entrevista → las maneja Joel manualmente.

### Reglas de tono (voz Joel — aplica a todos los mensajes)

Ver `deta-content` sección Anti-AI Flavor. Resumen operativo:

**Evitar siempre:**
- "Espero", "ojalá", "quedo atento/a", "estamos en contacto", "excelente día"
- Emojis
- Párrafos largos, muletillas hedging ("vale la pena destacar")
- Dos preguntas en un mismo mensaje (salvo la de slot + email, que van juntas por eficiencia)
- Dos mensajes seguidos sin esperar respuesta del candidato

**Usar:**
- Frases cortas, directas
- Contracciones naturales ("no me queda", "te escribo", "avísame")
- Segunda persona singular
- Cierres escuetos sin desearles nada

---

## Metodología de desarrollo

Este skill se construyó combinando **skill-creator** (iteración estructurada con evals) + **NotebookLM** (síntesis de fuentes externas de hiring science + archivos internos DETA). El flujo recomendado para futuras iteraciones:
1. `deta-research` → llenar NLM con fuentes relevantes (metodologías de selección, frameworks de scoring, skills DETA relacionadas)
2. Pedir digest al notebook → incorporar insights al draft del skill
3. `skill-creator` → test cases with/without skill en paralelo → grading → viewer → iterar

Esto evita que el skill quede anclado a un solo caso de uso o a intuición sin base metodológica.

---

## Notas operativas

- **Leer .docx:** `textutil -convert txt -stdout archivo.docx` en macOS
- **Leer .pdf:** `pdftotext archivo.pdf -` (si está instalado) o `textutil -convert txt -stdout archivo.pdf`
- **Sin perfil HTML:** si el perfil llega como PDF, extraer texto y derivar requisitos — no bloquear el proceso
- **Sheets scope:** el token de `gcloud` necesita el scope `drive` además de `spreadsheets`
- **Prompt del notebook:** `~/.claude/memory/DETA/Prompts/cowork/cv-matching.md`

### Extractor React fiber (fallback para email)

Si el CV descargado no contiene email, navegar de nuevo a la página del candidato y ejecutar este JS para extraer el email desde el estado interno de React:

```javascript
async () => {
  function getFiberEmails(el) {
    const key = Object.keys(el).find(k =>
      k.startsWith('__reactInternalInstance') || k.startsWith('__reactFiber'));
    if (!key) return [];
    function searchProps(props, depth) {
      if (!props || depth > 8) return [];
      const results = [];
      for (const [k, v] of Object.entries(props)) {
        if (typeof v === 'string') {
          const m = v.match(/[\w.+-]+@[\w.-]+\.(com|mx|net|org)/g);
          if (m) results.push(...m.filter(e =>
            !e.includes('occ.com') && !e.includes('cobrowse') &&
            !e.includes('sentry') && !e.includes('google')));
        }
        if (v && typeof v === 'object' && !v.nodeType && !v.stateNode)
          results.push(...searchProps(v.props || v, depth + 1));
      }
      return results;
    }
    const fiber = el[key];
    for (const f of [fiber, fiber?.alternate]) {
      if (!f) continue;
      const r = searchProps(f.memoizedProps, 0);
      if (r.length) return [...new Set(r)];
    }
    return [];
  }
  const btn = [...document.querySelectorAll('button')]
    .find(b => b.innerText.includes('Datos de contacto'));
  if (btn) { btn.click(); await new Promise(r => setTimeout(r, 1500)); }
  const emailEls = [...document.querySelectorAll('[data-testid="contact-email__data-cv"]')];
  return [...new Set(emailEls.flatMap(el => getFiberEmails(el)))];
}
```

Los emails de OCC NO están en el DOM — están en el estado interno de React. Si `emails` viene vacío, el candidato genuinamente no tiene email registrado.
