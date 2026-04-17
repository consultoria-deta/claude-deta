# DAG de Dependencias + Lógica de Fechas + Edge Cases

## DAG — Grafo completo

```
              ┌─────────────────────────────────────┐
              │  Node 1 (Mié 07:00) Blog publish    │ ← HUB
              │  Auto-deploy GitHub Actions         │
              └──────┬──────┬──────┬──────┬─────────┘
                     │      │      │      │
    ┌────────────────┘      │      │      └───────────────┐
    ▼                       ▼      ▼                      ▼
Node 2 (Mié 09:00)     Node 3  Node 4 (Jue 09:00)    Node 7 (Vie 11:00)
LinkedIn Empresa 1     (Mié    LinkedIn Joel 2       LinkedIn Empresa 2
  CTA→blog comentario  11:00)    CTA→blog comentario   CTA→blog comentario
                       YouTube
                       desc→blog + /diagnostico

Node 0 (Mar 09:00) LinkedIn Joel 1 ─ teaser SIN link (blog no existe aún)
Node 5 (Jue 11:00) IG Carousel ─── "Link en bio" (blog en bio desde Mié)
Node 6 (Vie 09:00) LinkedIn Joel 3 ─ cierre reflexivo, link opcional
```

**Aristas:**
- Node 0 → ninguna (es la única pieza pre-blog)
- Node 1 → ninguna (se publica sola por cron)
- Node 2, 3, 4, 7 → **dependen de Node 1** (blog debe estar live)
- Node 5 → depende débilmente de Node 1 (bio funciona sin pero mejor con)
- Node 6 → ninguna

**Validación del DAG:** es acíclico. Blog (Node 1) es el único nodo con out-degree alto.

---

## Función `anchor_week(run_date)`

```python
from datetime import datetime, timedelta

def anchor_week(run_date: str) -> dict:
    """
    Calcula las 4 fechas ancla (Mar/Mié/Jue/Vie) de la semana apropiada.

    Regla:
    - Si run_date cae Lun-Mar: usa ESTA semana (todavía hay tiempo)
    - Si run_date cae Mié-Dom: usa PRÓXIMA semana (esta ya no se puede rehacer)

    Args:
        run_date: fecha de corrida en formato "YYYY-MM-DD"

    Returns:
        dict con keys tuesday, wednesday, thursday, friday (strings "YYYY-MM-DD")
    """
    d = datetime.strptime(run_date, "%Y-%m-%d")
    dow = d.weekday()  # 0=Lun ... 6=Dom

    if dow <= 1:  # Lun o Mar
        monday = d - timedelta(days=dow)
        week_label = "actual"
    else:  # Mié en adelante
        monday = d + timedelta(days=(7 - dow))
        week_label = "próxima"

    return {
        "tuesday":   (monday + timedelta(days=1)).strftime("%Y-%m-%d"),
        "wednesday": (monday + timedelta(days=2)).strftime("%Y-%m-%d"),
        "thursday":  (monday + timedelta(days=3)).strftime("%Y-%m-%d"),
        "friday":    (monday + timedelta(days=4)).strftime("%Y-%m-%d"),
        "week_label": week_label,
    }

# Tests (ejecutar mentalmente al modificar)
# anchor_week("2026-04-13") → Lun → semana actual → Mar 14, Mié 15, Jue 16, Vie 17
# anchor_week("2026-04-14") → Mar → semana actual → Mar 14, Mié 15, Jue 16, Vie 17
# anchor_week("2026-04-15") → Mié → próxima semana → Mar 21, Mié 22, Jue 23, Vie 24
# anchor_week("2026-04-18") → Sáb → próxima semana → Mar 21, Mié 22, Jue 23, Vie 24
```

---

## Edge Cases — los 5 escenarios + manejo

### 1. Feriado MX cae miércoles

**Detección:** comparar `wednesday` del anchor_week contra lista de feriados MX (BCOM / INEGI):
1 enero, 5 feb, 21 mar, 1 may, 16 sep, 20 nov, 25 dic, días de elección federal.

**Síntoma:** B2B LATAM reduce engagement 80% en feriado.

**Manejo:**
1. Blog se publica igual por cron (auto-deploy no sabe de feriados)
2. Desplazar Node 2 (LinkedIn Empresa 1) y Node 3 (YouTube) al jueves
3. Jueves se vuelve "miércoles compactado": Empresa 1 09:00, YouTube 11:00, IG se mueve a viernes
4. Viernes original (Joel 3, Empresa 2) se compacta a sábado mañana o se salta

### 2. Pieza Martes con CTA "lee el blog" (bug original 2026-04-15)

**Detección:** leer `LinkedIn-Joel-1_*.md`, buscar patrones: "lee el artículo", "en el blog", "link abajo", "publiqué", URL a detaconsultores.com/blog.

**Síntoma:** El link daría 404 o lleva a blog anterior (no relacionado con la pieza).

**Manejo:**
- La skill **rechaza** la pieza como violación del DAG temporal
- Reporta en sección "Violaciones detectadas":
  ```
  Pieza #0 (LinkedIn Joel 1) viola DAG: CTA apunta a blog que se publica después.
  Recomendación: reescribir como teaser puro ("Mañana libero el artículo sobre..."), sin link.
  El link se coloca en Joel 2 (jueves) cuando el blog ya está live.
  ```
- `deta-content` toma el bastón y reescribe

### 3. YouTube no está editado el miércoles

**Detección:** `pieces.youtube.ready == false` en el input.

**Síntoma:** Rompe node 3 del DAG. Si lo forzamos a subir placeholder, el calendario miente.

**Manejo:**
1. Remover Node 3 del calendario de esta semana
2. Mover YouTube al **miércoles siguiente** como "bono" de la semana nueva — va a competir con el blog de esa semana, aceptar el tradeoff
3. LinkedIn Empresa 1 mantiene CTA al blog (no al video). Si el copy original apuntaba al video, reescribir.
4. Reportar: "YouTube desplazado a [fecha próxima semana]. Compacta semana X+1."

### 4. Corrida late-week (jue/vie/sáb/dom)

**Detección:** `run_date.weekday() >= 2` → `week_label == "próxima"` desde `anchor_week()`.

**Síntoma:** Joel piensa que está planeando esta semana, pero ya pasó el punto de no retorno.

**Manejo:**
- Salida de la skill incluye **banner explícito** al inicio:
  ```
  ⚠️ Semana actual (ISO W[N]) está muerta. Calendario calculado para semana próxima (ISO W[N+1]).
  Si querías publicar esta semana, no es posible — los martes/miércoles ya pasaron.
  ```
- Las fechas en la tabla reflejan próxima semana

### 5. Blog no está listo cuando se corre la skill

**Detección:** `pieces.blog.ready == false` o el archivo markdown no existe.

**Síntoma:** No hay hub → DAG colapsa completo. Todas las dependencias quedan huérfanas.

**Manejo:**
- **Bloqueo crítico:** la skill NO genera calendario parcial
- Salida única:
  ```
  ❌ BLOQUEADO: Blog es dependencia raíz del DAG. 6 de 8 piezas dependen de él.
  Acción requerida: producir blog antes de calendarizar.
  Una vez listo, re-correr esta skill con pieces.blog.ready=true.
  ```
- No hacer el calendario "a medias" — genera más confusión que ayuda

---

## Invariantes que la skill debe verificar

Antes de emitir el calendario, checar:

| Invariante | Qué significa | Acción si falla |
|---|---|---|
| DAG acíclico | No hay ciclos | Bug en skill, reportar |
| Blog precede a sus dependientes en el tiempo | Node 1 antes que 2,3,4,7 | Reordenar |
| Ninguna pieza LinkedIn tiene URL en el body | Link policy | Reportar violación |
| Fechas están en formato ISO y no son del pasado | Sanity check | Recalcular |
| Hora de cada pieza está dentro de ventanas 08:30-12:00 | Fuera = engagement bajo | Mover a siguiente ventana disponible |
