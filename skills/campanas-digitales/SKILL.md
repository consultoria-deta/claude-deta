---
name: campanas-digitales
description: Experto en campañas digitales de pago — Google Ads, Meta Ads, configuración de conversiones, GTM, Quality Score, Performance Max, Smart Bidding. Activa cuando el usuario mencione: campañas, Google Ads, anuncios pagados, SEM, PPC, conversiones, GTM, tag de seguimiento, Quality Score, CPC, ROAS, CPA, Performance Max, AI MAX, keyword research para campañas, landing page para anuncios, presupuesto de campaña, o cualquier acción de publicidad digital. DETA-aware: conoce el sitio, los servicios, las landing pages y la cuenta (Customer ID 150-883-1637). Úsalo para diseñar, configurar, auditar u optimizar cualquier campaña digital de DETA.
---

# Campañas Digitales — DETA Consultores

Skill especializado para planear, configurar y optimizar campañas de Google Ads para DETA Consultores. Integra el contexto del sitio, los servicios, el stack de tracking y las mejores prácticas 2026.

---

## Contexto DETA — lo que ya está listo

| Variable | Valor |
|----------|-------|
| Sitio | https://detaconsultores.com |
| GA4 | G-EVQHHSLZ7C (instalado, dataLayer activo) |
| GTM | ❌ Pendiente instalar |
| Google Ads Customer ID | 150-883-1637 |
| Conversion Tag (AW-) | ❌ Pendiente — crear acción de conversión primero |
| Aviso de privacidad | ✅ /aviso-de-privacidad (LFPDPPP compliant) |

### Landing pages disponibles

| Servicio | URL | CTA de conversión | Performance Desktop | Mobile LCP |
|----------|-----|-------------------|---------------------|-----------|
| Diagnóstico Express | /diagnostico-express | Formulario 5 preguntas | 98/100 | 3.5s ⚠ |
| Reclutamiento | /reclutamiento | "Hablemos de tu vacante" | 100/100 | — |
| Capacitación | /capacitacion | "Solicita una propuesta" | 100/100 | — |
| Contacto | /contacto | Formulario de contacto | — | — |

### Audiencia objetivo
Dueños y directores de PyMEs en Chihuahua (y México en general) con 10-100 empleados que están en proceso de crecimiento y necesitan estructura organizacional, reclutamiento estratégico o capacitación de equipos.

---

## Arquitectura de campaña recomendada (fase inicial)

Para un presupuesto inicial de arranque, priorizar así:

```
Campaña 1 — Reclutamiento Estratégico [ALTA PRIORIDAD]
  ↳ Keyword intent: "empresa reclutamiento chihuahua", "agencia selección personal"
  ↳ Landing: /reclutamiento
  ↳ Conversión: clic en "Hablemos de tu vacante" → /contacto (form submit)
  ↳ Bidding: Maximize Conversions → migrar a Target CPA cuando haya 30+ conv/mes

Campaña 2 — Diagnóstico Express [ALTA PRIORIDAD]
  ↳ Keyword intent: "consultoría empresarial gratis", "diagnóstico empresa"
  ↳ Landing: /diagnostico-express
  ↳ Conversión: form submit del diagnóstico (5 preguntas completadas)
  ↳ Bidding: Maximize Conversions

Campaña 3 — Capacitación Empresarial [MEDIA]
  ↳ Keyword intent: "capacitación empresas chihuahua", "cursos liderazgo equipos"
  ↳ Landing: /capacitacion
  ↳ Conversión: clic en "Solicita una propuesta" → form submit /contacto
  ↳ Bidding: Maximize Conversions
```

**Regla de presupuesto 70-20-10:**
- 70% a campaña con mejores resultados probados
- 20% a escalar la segunda mejor
- 10% a experimentar (PMax o AI MAX)

---

## Setup de conversiones — flujo obligatorio antes de activar

El orden importa. Nada de anuncios sin conversiones configuradas.

### Paso 1 — Instalar GTM

```html
<!-- En app/layout.tsx, dentro del <head>, antes del cierre -->
<Script id="gtm-head" strategy="beforeInteractive">
  {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','GTM-XXXXXXX');`}
</Script>

<!-- En el <body>, inmediatamente después del tag de apertura -->
<noscript>
  <iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
    height="0" width="0" style="display:none;visibility:hidden"></iframe>
</noscript>
```

Reemplazar `GTM-XXXXXXX` con el ID real del contenedor.

### Paso 2 — Crear conversión en Google Ads

1. Google Ads → Objetivos → Conversiones → **Nueva acción de conversión**
2. Tipo: **Sitio web**
3. Por landing page:
   - `/diagnostico-express` → evento: "form_submit_diagnostico"
   - `/contacto` → evento: "form_submit_contacto"
   - `/reclutamiento` → clic en botón WhatsApp/CTA
4. Copiar **Conversion ID** (`AW-XXXXXXXXXX`) y **Conversion Label** por acción

### Paso 3 — Configurar tag en GTM

En GTM, crear 3 tags (una por conversión):
- Tipo: **Google Ads Conversion Tracking**
- Conversion ID: `AW-XXXXXXXXXX`
- Conversion Label: el label específico de cada acción
- Trigger: disparar en el evento correspondiente (`form_submit`, `button_click`)

### Paso 4 — Verificar con GTM Preview

Antes de publicar, entrar al modo Preview de GTM → navegar el sitio → completar un formulario → confirmar que el tag se dispara. Solo publicar cuando todos los tags disparen correctamente.

---

## Bidding strategy por etapa

| Etapa | Conversiones/mes | Estrategia | Por qué |
|-------|-----------------|------------|---------|
| Arranque | 0-30 | Maximize Conversions | Dejar que Google aprenda sin restricción de CPA |
| Estabilización | 30-50 | Target CPA (conservador) | Poner límite una vez que hay datos suficientes |
| Escala | 50+ | Target CPA optimizado / Target ROAS | Optimizar por valor de conversión |
| Avanzado | 100+ | Value-Based Bidding + LTV | Enseñar a Google cuál lead vale más |

**Regla crítica para B2B:** No optimizar solo por "form submit". Integrar CRM para pasar conversiones de calidad (MQL→SQL→Cliente) de vuelta a Google. Advertisers que importan conversiones offline reportan 31% menos costo por lead.

---

## Quality Score — los 3 pilares

Google evalúa 3 componentes: CTR esperado, relevancia del anuncio y experiencia de landing page.

### Landing page experience (el más importante para DETA)

Actualmente:
- ✅ Desktop performance excelente (98-100/100)
- ⚠ Mobile LCP 3.5s en /diagnostico-express — **fix antes de activar Ads** (Google penaliza LCP > 3s)
- ✅ Contenido relevante y específico por servicio
- ✅ CTAs claros sobre el fold
- ✅ Precio visible en /reclutamiento y /capacitacion

Objetivo: Quality Score ≥ 7. Pasar de QS 4 a 8 reduce el CPC ~26%.

### Ad relevance

Cada grupo de anuncios debe tener:
- Keywords con el mismo intento de búsqueda
- Headline 1 con la keyword exacta o variante cercana
- Headline 2 con diferenciador (ej: "Desde Chihuahua", "Sin compromiso")
- Headline 3 con CTA ("Agenda tu diagnóstico", "Hablemos")
- Description 1: propuesta de valor concreta
- Description 2: prueba social o resultado cuantificado

### RSAs (Responsive Search Ads)

No sobre-pinar headlines. Pinar más de 8 reduce la efectividad 35-40%. Dejar libertad al algoritmo para encontrar las combinaciones óptimas — solo pinar los elementos de cumplimiento legal o brand si aplica.

---

## Performance Max (PMax) — cuándo y cómo usarlo

**Cuándo:** Solo después de tener conversiones estables (50+/mes) y creative assets de calidad.

**Para DETA en 2026:**
- PMax funciona bien para servicios locales con targeting geográfico (Chihuahua + México)
- Requiere mínimo: 15-20 imágenes, 5-10 videos, 15-20 headlines
- Sin videos propios → PMax generará automáticos de baja calidad → **no activar sin videos**
- Configurar "Bid primarily for new customers" para evitar que gaste en retargeting puro

**AI MAX for Search (nuevo en 2026):**
- Enhancement layer sobre campañas Search (no reemplaza PMax)
- Expande keywords automáticamente basado en contexto de landing page
- Requiere: 30+ conversiones/mes, ≥$750/día de presupuesto para funcionar bien
- Activar solo como experimento (50/50 split, 4 semanas mínimo) antes de adoptar

---

## Herramientas esenciales

| Herramienta | Para qué | Costo |
|-------------|----------|-------|
| **Google Ads Editor** | Editar campañas en bulk, offline | Gratis |
| **Google Keyword Planner** | Volúmenes y sugerencias de keywords | Gratis (con cuenta activa) |
| **Optmyzr** | Automatización, alertas, optimizaciones | $208+/mes |
| **Keywordme** | Gestión de search terms, negative keywords | $12/mes |
| **Semrush** | Competitor intelligence, keyword research | $129+/mes |
| **SpyFu** | Ver qué keywords usa la competencia en Ads | $39+/mes |
| **ClickCease** | Protección contra click fraud | $$$  |
| **Hotjar / Clarity** | Comportamiento del usuario en landing pages | Gratis (Clarity) |

**Para arrancar DETA:** Solo necesitas Google Ads Editor + Google Keyword Planner + Microsoft Clarity (gratis, heatmaps en landing pages).

---

## Keyword research — framework para DETA

### Intención de búsqueda por servicio

**Reclutamiento:**
```
Alta intención: "reclutamiento de personal chihuahua", "agencia selección personal mexico", 
               "empresa headhunter chihuahua", "contratar personal chihuahua"
Media intención: "cómo reclutar personal", "proceso de selección de personal pyme"
Negativas: "empleos", "trabajo", "vacantes", "curriculum"
```

**Capacitación:**
```
Alta intención: "capacitación empresarial chihuahua", "cursos para empresas chihuahua",
               "taller liderazgo equipos de trabajo"
Media intención: "cómo capacitar a mi equipo", "desarrollo organizacional"
Negativas: "gratis", "en línea", "certificación individual", "universidad"
```

**Diagnóstico / Consultoría:**
```
Alta intención: "consultoría empresarial chihuahua", "consultor pyme mexico",
               "consultoría organizacional chihuahua"
Media intención: "cómo mejorar mi empresa", "problemas de organización empresa"
Negativas: "software", "crm", "erp", "app"
```

### Match types recomendados en 2026

- **Phrase match** como base — balance entre control y alcance
- **Exact match** para las keywords de mayor costo o mayor intención
- **Broad match** solo en campañas maduras con Smart Bidding activo (el algoritmo necesita datos para usarlo bien)

---

## Checklist pre-lanzamiento

Antes de activar el primer anuncio:

- [ ] GTM instalado y verificado en producción
- [ ] Acción de conversión creada en Google Ads (AW-XXXXXXXXXX)
- [ ] Tag de conversión disparando correctamente en GTM Preview
- [ ] GA4 linking activado con Google Ads (Goals → Import)
- [ ] Mobile LCP /diagnostico-express < 2.5s
- [ ] Negative keyword list cargada (mínimo: empleos, trabajo, curriculum, gratis, universidad)
- [ ] Presupuesto diario definido (mínimo recomendado: 5-10x CPC estimado por keyword)
- [ ] Extensiones de anuncio configuradas: sitelinks, callouts, structured snippets
- [ ] Aviso de privacidad accesible desde landing page ✅ (ya está)
- [ ] Número de WhatsApp/teléfono visible en landing page

---

## Métricas a monitorear semanalmente

| Métrica | Objetivo inicial | Alarma si... |
|---------|-----------------|--------------|
| CTR | > 3% (Search) | < 1% |
| Quality Score | ≥ 7 | < 5 |
| CPC | Benchmark por keyword | > 2x benchmark de sector |
| Tasa de conversión | > 2% | < 0.5% |
| Costo por lead | Establecer después de 30 conv. | > 3x precio objetivo |
| Impression Share | > 50% en keywords clave | < 20% por presupuesto |

---

## Skills que coordina

| Tarea dentro de Ads | Skill a cargar |
|---------------------|---------------|
| Investigar keywords, volúmenes, competencia | `keyword-research` |
| Redactar headlines, descriptions y CTAs de anuncios (RSAs) | `deta-content` |
| Assets visuales para Display / Performance Max | `deta-brand` |
| Verificar LCP/CWV de landing page antes de activar | `performance-audit` |
| Recibir triggers de amplification de contenido orgánico | `deta-distribucion` — entrega tabla de posts candidatos a boost (LinkedIn ≥30 interacciones/45min, IG ≥5% save rate/24h, Blog ≥50 sesiones/7 días). Esta skill los ejecuta operativamente. Ver `deta-distribucion/references/paid-triggers.md` |

Cargar la skill correspondiente cuando la tarea lo requiera — no asumir que el flujo de Ads abarca la ejecución de copy, brand o performance sin invocarlas.

---

## NotebookLM — fuente de conocimiento

Para profundizar en cualquier táctica, el notebook está cargado con 300+ fuentes:

```bash
notebooklm use a7055e94-4805-4497-a3e5-996280f0de3f
notebooklm ask "¿Cómo configurar Target CPA para una empresa de servicios profesionales con presupuesto < $500 USD/mes?"
```

---

## Flujo de sesión típica

1. **¿Qué quiere el usuario?** — nueva campaña / optimizar existente / setup tracking / keyword research / auditoría
2. **¿Cuál es el estado actual?** — verificar si GTM/AW- están instalados, cuántas conversiones hay, qué campañas corren
3. **Priorizar según el checklist pre-lanzamiento** — si falta tracking, eso va primero
4. **Entregar pasos accionables** — código concreto para GTM, estructura de campaña, lista de keywords, no recomendaciones genéricas
