---
name: a11y-audit
description: Auditoría de accesibilidad web WCAG 2.1 AA. Verifica contraste de colores, aria-labels, navegación por teclado, jerarquía de headings, alt texts y formularios accesibles. Incluye checks específicos para los tokens de marca DETA. Actívate cuando el usuario mencione "accesibilidad", "a11y", "contraste", "WCAG", "aria", "teclado", "lectores de pantalla", "accesible" — tanto en producción como en localhost.
---

# A11y Audit — Accesibilidad WCAG 2.1 AA

Auditoría de accesibilidad con checks automáticos vía Playwright y axe-core, más verificación manual de los tokens de marca DETA.

---

## Inputs

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `url` | requerido | URL de la página a auditar |
| `scope` | `full` | `full`, `forms`, `navigation`, `contrast` |

---

## Paso 1 — axe-core (automatizado)

```javascript
// Inyectar axe-core e inspeccionar la página completa
await page.addScriptTag({
  url: 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js'
});

const results = await page.evaluate(async () => {
  const r = await axe.run(document, {
    runOnly: {
      type: 'tag',
      values: ['wcag2a', 'wcag2aa']
    }
  });
  return {
    violations: r.violations.map(v => ({
      id:          v.id,
      impact:      v.impact,          // critical, serious, moderate, minor
      description: v.description,
      nodes:       v.nodes.length,
      selector:    v.nodes[0]?.target?.join(', '),
    })),
    passes: r.passes.length,
    incomplete: r.incomplete.length,
  };
});
```

Reportar solo `violations` — agrupar por impacto (`critical` primero).

---

## Paso 2 — Contraste de colores DETA

Verificar estas combinaciones específicas de la marca contra WCAG AA (ratio mínimo 4.5:1 texto normal, 3:1 texto grande):

| Combinación | Ratio esperado | Uso en el sitio |
|-------------|---------------|-----------------|
| Navy `#0c2b40` sobre blanco `#ffffff` | 14.7:1 ✅ | Texto principal |
| Blanco `#ffffff` sobre Navy `#0c2b40` | 14.7:1 ✅ | Headers, footers |
| Gold `#d3ab6d` sobre Navy `#0c2b40` | 3.8:1 ⚠ | Acentos — solo texto grande |
| Gold `#d3ab6d` sobre blanco `#ffffff` | 2.1:1 ❌ | No usar para texto informativo |
| Cyan `#12a9cc` sobre blanco `#ffffff` | 3.1:1 ⚠ | Solo texto grande o decorativo |
| Cyan `#12a9cc` sobre Navy `#0c2b40` | 4.8:1 ✅ | CTAs en fondos navy |

```javascript
// Verificar ratio de contraste de elementos visibles
const contrastIssues = await page.evaluate(() => {
  const getContrastRatio = (hex1, hex2) => {
    const lum = hex => {
      const rgb = parseInt(hex.slice(1), 16);
      const r = (rgb >> 16) / 255, g = (rgb >> 8 & 0xff) / 255, b = (rgb & 0xff) / 255;
      const toLinear = c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
    };
    const l1 = lum(hex1), l2 = lum(hex2);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };
  // Retornar elementos con color computado para verificar
  return Array.from(document.querySelectorAll('p, h1, h2, h3, a, button, label'))
    .map(el => ({
      tag:   el.tagName,
      text:  el.innerText?.slice(0, 40),
      color: getComputedStyle(el).color,
      bg:    getComputedStyle(el).backgroundColor,
    }))
    .filter(el => el.text?.trim());
});
```

---

## Paso 3 — Checks manuales vía Playwright

### Jerarquía de headings

```javascript
const headings = await page.evaluate(() =>
  Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'))
    .map(h => ({ level: h.tagName, text: h.innerText.slice(0, 60) }))
);
// Verificar: exactamente 1 H1, sin saltar niveles (H1→H3 sin H2)
```

### Alt texts en imágenes

```javascript
const images = await page.evaluate(() =>
  Array.from(document.querySelectorAll('img'))
    .map(img => ({ src: img.src.split('/').pop(), alt: img.alt, role: img.role }))
);
// Reportar imágenes sin alt o con alt vacío que no sean decorativas (role="presentation")
```

### Formularios accesibles

```javascript
const inputs = await page.evaluate(() =>
  Array.from(document.querySelectorAll('input, select, textarea'))
    .map(el => ({
      type:        el.type,
      name:        el.name,
      hasLabel:    !!document.querySelector(`label[for="${el.id}"]`) || !!el.closest('label'),
      hasAriaLabel: !!el.getAttribute('aria-label') || !!el.getAttribute('aria-labelledby'),
      placeholder: el.placeholder,
    }))
);
// Reportar inputs sin label explícito ni aria-label
```

### Navegación por teclado

```javascript
// Tab a través de elementos interactivos y verificar focus visible
await page.keyboard.press('Tab');
const focusedEl = await page.evaluate(() => ({
  tag:     document.activeElement?.tagName,
  outline: getComputedStyle(document.activeElement).outlineStyle,
}));
// Si outline es 'none' → falta focus ring visible
```

---

## Checks específicos para detaconsultores.com

| Componente | Qué verificar |
|------------|--------------|
| FAQ accordion (`/reclutamiento`) | `aria-expanded`, `aria-controls` en botones de acordeón |
| FloatingWhatsApp | `aria-label` en el botón flotante, no bloquear contenido en mobile |
| NewsletterForm | Label asociado al input de email, mensaje de error accesible |
| Formulario diagnóstico | Cada pregunta con fieldset/legend o aria-labelledby |
| Formulario contacto | Todos los inputs con label, errores anunciados con aria-live |
| OG images | No afectan a11y en página, pero verificar que no reemplacen contenido visible |

---

## Formato de output en consola

```
── A11Y: [URL] ───────────────────────────────
  axe-core: 2 críticos | 1 serio | 3 moderados | 12 OK

  ❌ CRÍTICO — button-name (3 elementos)
     Botones sin texto accesible: .faq-toggle, .whatsapp-btn, .nav-hamburger

  ❌ CRÍTICO — image-alt (2 elementos)
     Imágenes sin alt: /blog/dueno-cuello-botella.png, /public/logo.svg

  ⚠  SERIO — label (1 elemento)
     Input email del newsletter sin label explícito

  ⚠  CONTRASTE — Gold sobre blanco
     #d3ab6d / #ffffff = 2.1:1 — no usar para texto informativo

  ✅ Jerarquía de headings: 1 H1, secuencia correcta
  ✅ Formulario diagnóstico: todos los inputs con label
  ✅ Focus visible en links y botones principales
```

---

## Notas

- **axe-core** detecta ~30% de issues WCAG automáticamente — el resto requiere revisión manual
- **Gold sobre blanco**: combinación problemática por diseño — documentar como deuda técnica si se usa en texto
- **Cyan sobre blanco**: aceptable solo para texto grande (18px+ o 14px+ bold)
- **Focus ring**: Tailwind reset elimina outline por defecto — verificar que el sitio restaure `:focus-visible`
