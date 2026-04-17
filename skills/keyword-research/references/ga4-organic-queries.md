# GA4 Organic Queries — Script y configuración

## Filtro correcto para tráfico orgánico

El campo exacto es `sessionDefaultChannelGroup` con valor `"Organic Search"` (case-sensitive, EXACT match). Usar dimensiones genéricas o variantes rompe la atribución.

## Script GA4 Data API

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, FilterExpression,
    Filter, StringFilter
)

PROPERTY_ID = "properties/XXXXXXXXX"  # G-EVQHHSLZ7C → buscar el ID numérico en GA4 Admin

client = BetaAnalyticsDataClient()

request = RunReportRequest(
    property=PROPERTY_ID,
    dimensions=[
        Dimension(name="sessionDefaultChannelGroup"),
        Dimension(name="landingPage"),
    ],
    metrics=[
        Metric(name="sessions"),
        Metric(name="conversions"),
    ],
    dimension_filter=FilterExpression(
        filter=Filter(
            field_name="sessionDefaultChannelGroup",
            string_filter=StringFilter(
                match_type=StringFilter.MatchType.EXACT,
                value="Organic Search"
            )
        )
    ),
    date_ranges=[{"start_date": "90daysAgo", "end_date": "today"}],
    order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
    limit=50
)

response = client.run_report(request)
for row in response.rows:
    landing = row.dimension_values[1].value
    sessions = row.metric_values[0].value
    conversions = row.metric_values[1].value
    print(f"{landing}: {sessions} sesiones, {conversions} conversiones")
```

## Autenticación

Requiere credenciales de servicio o OAuth 2.0. Para acceso rápido:

```bash
gcloud auth application-default login
pip install google-analytics-data
```

## Nota para DETA (sitio joven)

El sitio detaconsultores.com empezó a generar tráfico orgánico en 2026. Los primeros 3 meses de datos serán escasos. Usar GKP + PyTrends como fuente principal hasta tener al menos 90 días de sesiones orgánicas significativas.

## Acceso alternativo (sin API)

GA4 → Informes → Adquisición → Adquisición de tráfico → filtrar canal = "Búsqueda orgánica" → exportar CSV con páginas de destino y sesiones.
