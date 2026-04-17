---
name: analisis-psicometrico-deta
description: Genera el PDF "Análisis DETA" narrativo a partir del JSON exportado por deta-psicometricos (/api/export/[id]) + perfil del puesto opcional. Output son 8 páginas fondo claro estilo editorial que cruzan scores con competencias del puesto. Cero costo API — Claude (Cowork o Claude Code) escribe la narrativa, Python arma el PDF con deta_pdf_base.
---

# Skill · Análisis DETA Psicométrico

## Cuándo usar esta skill

Cuando un reclutador necesita entregar al cliente el análisis cualitativo de un candidato ya evaluado en deta-psicometricos. Input: JSON exportado (`/api/export/[candidatoId]`). Output: PDF narrativo de 8 páginas.

Si solo necesitas los scores crudos (sin narrativa), no uses esta skill — el reclutador ya tiene ese PDF desde el dashboard.

## Input

Un JSON que cumple el contrato de `/api/export/[id]` de deta-psicometricos:

```json
{
  "candidato": { "id", "nombre", "email", "vacante"?, "cliente"?, "completadoEn" },
  "perfilPuesto": { ... } | null,
  "perfilPuestoUrl": "url" | null,
  "scores": { "cleaver", "kostick", "moss", "barsit", "ipip" },
  "exportadoEn": "iso8601"
}
```

## Pasos

### 1. Leer el payload

El usuario pega el JSON o provee un path. Carga el JSON completo en memoria. NO inventes scores — usa exactamente los del payload.

### 2. Enriquecer si falta `perfilPuesto`

Si `payload.perfilPuestoUrl` está presente pero `perfilPuesto` es null:

- Llama al Python helper `extraer_matching_data` de `Agent/Templates/deta_matching.py` pasándole la URL del perfil HTML.
- Guarda el resultado en `payload["perfilPuesto"]`.

Si no hay ni URL ni objeto de perfil, genera el PDF sin las secciones 3 y 4 (perfil y ajuste) — avisa al usuario que será un análisis de personalidad puro.

### 3. Escribir la narrativa (la parte creativa)

Añade `payload["analisis"]` con estos campos. **Todos en español neutro, tono profesional DETA, primera persona desde el equipo DETA ("observamos", "sugerimos"), nunca desde el candidato**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `resumenEjecutivo` | string (≤600 chars) | 2-3 oraciones sobre el fit general y la conclusión clave. Menciona el puesto por nombre. |
| `recomendacion` | `"Avanzar" \| "Avanzar con reservas" \| "No avanzar"` | Basado en ajuste agregado al puesto. |
| `perfilEvaluado` | string (≤800 chars) | Párrafo sobre personalidad y estilo de trabajo del candidato, desde IPIP + Cleaver + Kostick. |
| `fortalezas` | `string[]` (4-6 items) | Bullets concretos, cada uno ≤120 chars. Apóyate en los scores. |
| `areasMejora` | `string[]` (3-5 items) | Cosas a validar en entrevista final o proceso, no etiquetas negativas. |
| `puntosClave` | `Array<{titulo, descripcion}>` (exactamente 5) | Lecturas estratégicas para la decisión. Títulos cortos (≤8 palabras), descripción ≤280 chars. |
| `ajustePuesto` | `Array<{competencia, nivel, comentario}>` | Una entrada por cada competencia del `perfilPuesto`. `nivel` ∈ `"alto"\|"medio"\|"bajo"`. `comentario` ≤200 chars explicando por qué con referencia a scores. |
| `resumenPorTest` | `{cleaver, kostick, moss, barsit, ipip}` | 3-4 líneas por test. Interpreta, no transcribas números. |
| `conclusiones` | `string[]` (3-5 items) | Acciones accionables para el proceso: qué indagar en entrevista, qué confirmar con referencias, ajustes al plan de onboarding. |

**Reglas de narrativa:**
- Nunca inventes scores. Si algo no es claro, usa el lenguaje "sugieren/indican/tienden a".
- Refiere al candidato por su primer nombre en resumen ejecutivo y perfil evaluado.
- Evita etiquetas clínicas (no "es narcisista", sino "muestra preferencia por reconocimiento externo").
- El `nivel` de ajuste se deriva de cruzar el `nivelRequerido` de la competencia con los scores relevantes.
- En `resumenPorTest.barsit`, si algún item tiene `__TODO_VERIFY: true` en el schema original, menciona que los items de series numéricas son provisionales y el score total es orientativo.

### 4. Generar el PDF

```python
import sys
sys.path.insert(0, "/mnt")  # Cowork
sys.path.insert(0, str(Path.home() / "Library/CloudStorage/GoogleDrive-consultoria@detaconsultores.com/Mi unidad/Agent/Templates"))  # macOS

from deta_analisis_psicometrico import generar_analisis

pdf_path = generar_analisis(payload, output_dir="./output")
```

El script vive en `Agent/Templates/deta_analisis_psicometrico.py` (Drive). En Cowork está accesible como `/mnt/deta_analisis_psicometrico.py`.

### 5. Entregar

- Nombre del archivo: `AnalisisDETA_<slug-nombre>_<YYYYMMDD>.pdf`
- Sube el PDF a Drive: `Agent/Reclutamientos/<Cliente>/<Vacante>/Reportes/<Nombre>/`
- Devuelve al usuario el path local + link de Drive.

## Estructura del PDF (lo que el script genera)

1. **Portada** — navy dark, logo DETA white, nombre candidato grande, puesto, cliente, fecha. Eyebrow "ANÁLISIS DETA".
2. **Resumen ejecutivo + Recomendación** — Caja con resumen, pill semántica (verde/gold/rojo) con la recomendación.
3. **Perfil del puesto** — Competencias con peso, nivel requerido, escolaridad, experiencia, rango salarial.
4. **Ajuste por competencia** — Una card por competencia con nivel (alto/medio/bajo), barra de ajuste, comentario.
5. **Perfil evaluado** — Párrafo personalidad, luego 2 columnas: fortalezas (verde) / áreas a validar (gold).
6. **Puntos clave** — 5 lecturas estratégicas numeradas.
7. **Resumen por prueba** — 5 cards, una por test, narrativa.
8. **Conclusiones** — Acciones numeradas en tarjetas gold. Documentos complementarios al final.

Todo con tokens DETA (navy #0c2b40, gold #d3ab6d, cyan #12a9cc), tipografía Playfair Display + Source Sans 3, fondo claro (SURFACE #F5F7FA), apto para impresión A4.

## Referencias

- Mockup visual: `deta-psicometricos/app/analisis-deta/demo/page.tsx` + `components/reporte/AnalisisDeta.tsx`
- Script Python: `Agent/Templates/deta_analisis_psicometrico.py`
- PDF base: `Agent/Templates/deta_pdf_base.py`
- Matching helper: `Agent/Templates/deta_matching.py::extraer_matching_data`
- Contrato de export: `deta-psicometricos/app/api/export/[id]/route.ts`
