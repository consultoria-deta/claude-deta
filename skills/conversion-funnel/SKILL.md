---
name: conversion-funnel
description: >
  Estrategia de conversión y flujo de leads para el sitio web de DETA.
  Actívate con cualquier mención de: CTA, botón, lead, funnel, conversión,
  flujo de usuario, siguiente paso, formulario, contacto, WhatsApp, diagnóstico,
  llamada a la acción, captar cliente, generar leads, usuario no convierte,
  dónde mando al usuario, navegación, UX de conversión.
---

# Conversion Funnel — DETA Consultores

## El Funnel de DETA

El objetivo de cada página es mover al usuario hacia el siguiente paso.
Nunca dejar al usuario sin un camino claro.
Entrada orgánica / anuncio
↓
HOMEPAGE (/)
Objetivo: generar interés + credibilidad
CTA primario: /diagnostico-express
CTA secundario: /servicios
↓
SERVICIOS (/servicios)
Objetivo: entender qué hace DETA + identificarse
CTA primario: /metodologia
CTA secundario: /contacto
↓
METODOLOGÍA (/metodologia)
Objetivo: reducir fricción + generar confianza
CTA primario: /diagnostico-express
CTA secundario: /contacto
↓
DIAGNÓSTICO EXPRESS (/diagnostico-express)
Objetivo: captar lead cualificado
CTA único: /contacto (con contexto del resultado)
↓
CONTACTO (/contacto)
OBJETIVO FINAL: Agendar llamada o enviar mensaje
Acción: Calendly embed + formulario + WhatsApp
## Reglas de CTA por Página

### Cantidad
- Máximo 2 CTAs por sección
- 1 primario (botón dorado sólido) + 1 secundario (outline o link)
- Nunca 3 CTAs visibles en el mismo viewport

### Textos de CTA por etapa del funnel

| Etapa | CTA Primario | CTA Secundario |
|---|---|---|
| Homepage hero | "Agenda tu diagnóstico" | "Conoce nuestros servicios →" |
| Homepage mid | "Descarga el Diagnóstico Express gratis" | "Conoce cómo trabajamos →" |
| Homepage cierre | "Agenda tu diagnóstico" | "Escríbenos por WhatsApp" |
| /servicios cierre | "Ver cómo trabajamos" | "Agenda una llamada" |
| /metodologia cierre | "Descarga tu Diagnóstico Express" | "Habla con nosotros" |
| /diagnostico-express | "Quiero hablar con DETA sobre mis resultados" | — |
| /contacto | Calendly embed | Formulario como alternativa |

### Links de navegación interna obligatorios

Cada página debe linkear a las siguientes en orden de funnel:
- Homepage → /servicios, /metodologia, /diagnostico-express, /contacto
- /servicios → /metodologia, /contacto
- /metodologia → /diagnostico-express, /contacto
- /diagnostico-express → /contacto
- /blog/[post] → /diagnostico-express (siempre al final del post)

## WhatsApp Flotante

Presente en TODAS las páginas. Configuración:

```tsx
// components/FloatingWhatsApp.tsx
const WHATSAPP_URL = "https://wa.me/526144273762?text=Hola%2C%20me%20interesa%20conocer%20los%20servicios%20de%20DETA%20Consultores"

// Estilos: fixed bottom-6 right-6 z-50
// Color: #25D366 (verde WhatsApp)
// Ícono: MessageCircle de lucide-react, stroke 1.5, 28px
// Tooltip: "Escríbenos por WhatsApp"
// Visible: siempre en mobile, delay 3s en desktop
```

## Navbar CTA

El botón "Agenda tu diagnóstico" en el navbar va SIEMPRE a `/contacto`.
Es el CTA de mayor intención — no al diagnóstico express.
El diagnóstico express es para usuarios de menor intención que aún no están listos para hablar.

## Checklist de Conversión por Página

Antes de considerar una página completa:
- [ ] Existe al menos 1 CTA claro antes del fold
- [ ] Existe al menos 1 CTA al final de la página
- [ ] El CTA primario apunta al siguiente paso del funnel
- [ ] El CTA secundario es una alternativa de menor fricción
- [ ] No hay secciones sin salida (dead ends)
- [ ] El botón de WhatsApp flotante está presente
- [ ] /blog posts terminan con CTA a /diagnostico-express
