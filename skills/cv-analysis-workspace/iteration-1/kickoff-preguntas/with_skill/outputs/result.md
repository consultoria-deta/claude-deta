# CV Analysis Skill — Kickoff Response

## Task recibido

> "quiero analizar los candidatos que tengo en OCC para la vacante de Gerente de Operaciones, el job_id es 88776 y el sheet es 1BxkZ9QwertySheetId456"

---

## Preguntas realizadas antes de proceder

El skill tiene en contexto `JOB_ID = 88776` y `SHEET_ID = 1BxkZ9QwertySheetId456`. Faltan los inputs de Fase 2 (Matching). Antes de scorear, el skill requiere calibrar criterios con Joel (Paso 2.0). Las tres preguntas obligatorias son:

1. **¿Qué pesa más para este puesto?** (ej. experiencia operativa sobre liderazgo de equipos, o al revés)
2. **¿Hay sectores de experiencia previa que prefieras o que descarten automáticamente?**
3. **¿Cuál es el requisito no negociable (must-have) sin el cual no tiene caso entrevistar?**

También falta confirmar:

- **`CV_DIR`** — ¿en qué carpeta de Drive quieres guardar los CVs descargados?
- **`PERFIL`** — ¿tienes un perfil de puesto en HTML, PDF o descripción libre para Gerente de Operaciones? (necesario para el matching)

---

## Respuesta completa del skill

Tengo `job_id = 88776` y `sheet_id = 1BxkZ9QwertySheetId456`. Voy a correr Fase 1 (scraping OCC) y Fase 2 (matching) en secuencia.

Antes de arrancar el scoring necesito calibrar los criterios para Gerente de Operaciones:

1. **¿Qué pesa más para este puesto?** Por ejemplo: ¿experiencia en gestión de operaciones / procesos sobre liderazgo de equipos grandes, o al revés? ¿Importa más el sector o los resultados cuantificados?

2. **¿Hay sectores de experiencia previa que prefieras o que descarten automáticamente?** Por ejemplo: manufactura, logística, servicios, retail — ¿alguno que sea preferido o que sea un no-go?

3. **¿Cuál es el requisito no negociable (must-have) sin el cual no tiene caso entrevistar?** Por ejemplo: mínimo X años en puesto de Gerencia, gestión de equipos de más de N personas, P&L a su cargo, etc.

Mientras me das esas respuestas, puedo arrancar ya el scraping de Fase 1 para no perder tiempo. ¿Procedo con el login a OCC y la extracción de candidatos del job 88776?
