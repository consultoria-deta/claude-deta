# Print Export Guide — DETA Design Reference

## Sistema de medición

Para PDFs generados con reportlab:

| Milimetros | Puntos | Pulgadas |
|---|---|---|
| 1mm | 2.835pt | 0.039in |
| 1pt | 0.353mm | 0.0139in |

**Margen estándar DETA:**
- Top/Bottom: 0.5 inch (~36pt)
- Left/Right: 0.6 inch (~43pt)

## El problema

El HTML de DETA está diseñado para browser:
- Unidades px
- flexbox centering con `min-height: 100vh`
- Imágenes en píxeles

Los motores de print (Chrome print-to-PDF, WeasyPrint, wkhtmltopdf) interpretan estas unidades diferente, lo que produce documentos de tamaño incorrecto o contenido recortado.

## Espaciado estándar para reportlab (basado en documentos DETA)

### Tamaños de fuente

| Elemento | Tamaño |
|---|---|
| Título documento | 18-20pt |
| Subtítulo documento | 10-11pt |
| Título sección | 10-12pt |
| Body text | 9-10pt |
| Tabla header | 8pt |
| Tabla body | 8pt |
| Footer | 7pt |

### spaceBefore / spaceAfter

| Elemento | Antes | Después |
|---|---|---|
| Título sección (H1) | 8pt | 4pt |
| Título subsección (H2) | 6pt | 2pt |
| Body paragraph | 1pt | 1pt |
| Bullet | 1pt | 1pt |
| Tabla | 4pt | 4pt |
| HRFlowable divisor | 2pt | 2pt |

**Regla CRÍTICA: No exaggerar el espaciado.** Los títulos de sección son compactos.spaceBefore=14pt para H1 es excesivo. Máximo: 8-10pt.

### Ejemplo de tabla compacta (OK)

```python
t.setStyle(TableStyle([
    ('TOPPADDING', (0,0), (-1,0), 4),    # header: 4pt
    ('BOTTOMPADDING', (0,0), (-1,0), 4),
    ('TOPPADDING', (0,1), (-1,-1), 3),     # body: 3pt
    ('BOTTOMPADDING', (0,1), (-1,-1), 3),
]))
```

**MAL (espaciado exagerado):**

```python
# NO HACER ESTO
('TOPPADDING', (0,0), (-1,0), 14),
('BOTTOMPADDING', (0,0), (-1,0), 14),
('TOPPADDING', (0,1), (-1,-1), 10),
('BOTTOMPADDING', (0,1), (-1,-1), 10),
```

### Tabla estratégica para perfiles de puesto

```python
col_widths = [1.8*inch, 1.5*inch, 2.5*inch, 0.6*inch]  # ~6.4 inch total
# Headers en navy, filas alternadas, línea cyan bajo header
```

## Soluciones por caso de uso

### Caso 1: PNG desde Browser (Playwright)

**Mejor para:** Diapositivas, reconocimientos, documentos donde se necesita imagen fija.

```javascript
// Capturar a resolución de print (300 DPI para carta)
// Carta: 8.5" × 11" × 300 = 2550 × 3300 px
await page.setViewportSize({ width: 2550, height: 3300 });

// Esperar a que carguen las fuentes
await page.waitForTimeout(1000);

const element = await page.locator('.document-container').first();
await element.screenshot({
  path: 'output.png',
  type: 'png',
});
```

**Nota:** Si el HTML usa `vh`, reemplazarlo por `%` o `rem` antes del screenshot.

### Caso 2: PDF desde Playwright

```javascript
const pdf = await page.pdf({
  format: 'Letter',
  printBackground: true,
  margin: { top: '0', right: '0', bottom: '0', left: '0' },
  landscape: false,
});

await fs.writeFileSync('output.pdf', pdf);
```

### Caso 3: PDF con WeasyPrint

WeasyPrint interpreta px como puntos (72 DPI). Convertir antes:

```python
import re

def convert_px_to_pt(css: str) -> str:
    """Convierte px a pt para WeasyPrint (1px = 0.75pt)"""
    def replace_px(match):
        px_val = int(match.group(1))
        pt_val = px_val * 0.75
        return f'{pt_val}pt'
    
    return re.sub(r'(\d+)px', replace_px, css)

# Ejemplo
original = """
.card { width: 1200px; padding: 24px; }
.hero { font-size: 48px; }
"""

converted = convert_px_to_pt(original)
# .card { width: 900pt; padding: 18pt; }
# .hero { font-size: 36pt; }
```

### Caso 4: HTML Print con @media print

Para documentos que se imprimen directamente desde browser:

```css
@media print {
  @page {
    size: Letter;
    margin: 0;
  }

  :root {
    font-size: 12pt; /* Convertir rem a pt */
  }

  body {
    background: white !important;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }

  .no-print {
    display: none !important;
  }

  .card, .badge, .btn {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
}
```

## Checklist antes de exportar

- [ ] ¿El documento usa unidades relativas (rem, %) en vez de px para dimensiones?
- [ ] ¿Las fuentes están cargadas (Google Fonts o locales)?
- [ ] ¿`print-color-adjust: exact` está en elementos con color de fondo?
- [ ] ¿Hay `break-inside: avoid` en cards y secciones importantes?
- [ ] ¿El contenido no está centrado con `min-height: 100vh`?
- [ ] ¿Probaste en viewport del tamaño correcto antes de exportar?

## Conversión rápida de px a pt

| px | pt |
|---|---|
| 8px | 6pt |
| 12px | 9pt |
| 16px | 12pt |
| 24px | 18pt |
| 32px | 24pt |
| 48px | 36pt |
| 64px | 48pt |
| 96px | 72pt |
| 1200px | 900pt |
| 850px | 637.5pt |

**Regla:** `pt = px × 0.75`
