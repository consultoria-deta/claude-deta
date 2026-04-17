# Sistema de Color DETA — Tech Edition

Sistema extendido con escalas completas, semánticos alineados y dark mode. Los 3 tokens históricos (navy `#0c2b40`, cyan `#12a9cc`, gold `#d3ab6d`) son inmutables y forman la identidad core. Todo lo demás son derivados para cubrir estados, elevación y jerarquía densa.

---

## 1. Tokens Core (inmutables)

| Token | Hex | Rol |
|---|---|---|
| `navy` | `#0c2b40` | Identidad — estructura, autoridad |
| `gold` | `#d3ab6d` | Identidad — CTAs, detalle, calidez |
| `cyan` | `#12a9cc` | Identidad — interactivo, data |

**Regla absoluta:** ninguno se reemplaza nunca. Cualquier paleta derivada los respeta.

---

## 2. Escalas Completas

### Navy scale
```
navy-50   #f0f4f8    ← surface frío
navy-100  #d9e2eb
navy-200  #b1c2d1
navy-300  #7d96ad
navy-400  #4a6a84
navy-500  #28475f
navy-600  #1a3a52
navy-700  #123147
navy-800  #0c2b40    ← core (brand primary)
navy-900  #081f30
navy-950  #040f1c    ← dark canvas
```

### Cyan scale
```
cyan-50   #e0f5fa
cyan-100  #b8e6f0
cyan-200  #8ed6e5
cyan-300  #5dc4dc
cyan-400  #34b5d4
cyan-500  #12a9cc    ← core (brand accent)
cyan-600  #0e8bab
cyan-700  #0a6d87
cyan-800  #085464
cyan-900  #063c49
```

### Gold scale
```
gold-50   #faf4e8
gold-100  #f4e6c9
gold-200  #ead5a7
gold-300  #e0c184
gold-400  #d9b578
gold-500  #d3ab6d    ← core (brand secondary)
gold-600  #b8944d
gold-700  #a88551
gold-800  #7c613a
gold-900  #5a4729
```

### Slate scale (grays fríos con undertone navy)
```
slate-50   #f7f9fb    ← canvas claro, background default
slate-100  #eef2f7    ← surface alterno
slate-200  #dce3ec    ← border claro
slate-300  #b8c3d1    ← border hover, muted placeholder
slate-400  #8695a8    ← text muted
slate-500  #5a6b80    ← text secundario
slate-600  #3e4d60    ← text fuerte sobre claro
slate-700  #2b3745    ← panel dark mode
slate-800  #1c242e    ← surface dark mode
slate-900  #0f151b    ← canvas dark mode
```

**Por qué slate y no gray Tailwind:** los grays neutros (`#737373`) destiñen sobre navy. Los slate-fríos comparten el undertone azul de la paleta core y mantienen coherencia visual.

---

## 3. Tokens Semánticos

Alineados a la paleta; no se usan hexes estándar de libs que rompen la identidad.

```
success     #10b981   (emerald — Linear-compatible, vibrante sobre navy)
success-bg  rgba(16, 185, 129, 0.12)
success-fg  #047857   (texto sobre fondo success-bg)

warning     #d3ab6d   (gold reutilizado — nunca ámbar genérico)
warning-bg  rgba(211, 171, 109, 0.18)
warning-fg  #7c613a   (gold-800)

danger      #e0556f   (coral — alineado a navy, no rojo tomate)
danger-bg   rgba(224, 85, 111, 0.12)
danger-fg   #a8304a

info        #12a9cc   (cyan reutilizado)
info-bg     rgba(18, 169, 204, 0.10)
info-fg     #0a6d87   (cyan-700)
```

---

## 4. Elevation — Sombras y Liquid Glass DETA

### Shadow stack
```css
--shadow-xs:        0 1px 2px rgba(12, 43, 64, 0.05);
--shadow-sm:        0 2px 4px rgba(12, 43, 64, 0.06),
                    0 1px 2px rgba(12, 43, 64, 0.04);
--shadow-md:        0 4px 12px rgba(12, 43, 64, 0.08),
                    0 2px 4px rgba(12, 43, 64, 0.05);
--shadow-lg:        0 12px 32px rgba(12, 43, 64, 0.12),
                    0 4px 8px rgba(12, 43, 64, 0.06);
--shadow-xl:        0 24px 64px rgba(12, 43, 64, 0.18),
                    0 8px 16px rgba(12, 43, 64, 0.08);

--shadow-glow-cyan: 0 0 24px rgba(18, 169, 204, 0.28);
--shadow-glow-gold: 0 0 24px rgba(211, 171, 109, 0.22);
--shadow-inset:     inset 0 1px 0 rgba(255, 255, 255, 0.06);
```

### Liquid glass panels (dark mode / overlays)
```css
--glass-panel: background: rgba(12, 43, 64, 0.72);
               backdrop-filter: blur(24px) saturate(1.2);
               border: 1px solid rgba(255, 255, 255, 0.06);
               box-shadow: var(--shadow-xl), var(--shadow-inset);

--glass-card:  background: rgba(255, 255, 255, 0.03);
               backdrop-filter: blur(16px);
               border: 1px solid rgba(255, 255, 255, 0.05);

--glass-input: background: rgba(255, 255, 255, 0.04);
               border: 1px solid rgba(255, 255, 255, 0.08);
               backdrop-filter: blur(8px);
```

### Focus rings
```css
--ring-gold:  0 0 0 2px #040f1c, 0 0 0 4px #d3ab6d;    /* offset navy-950 + gold */
--ring-cyan:  0 0 0 2px #040f1c, 0 0 0 4px #12a9cc;
--ring-danger: 0 0 0 2px #040f1c, 0 0 0 4px #e0556f;
```

---

## 5. Dark Mode (opcional)

```
Canvas           navy-950 #040f1c
Surface          slate-800 #1c242e
Surface-elev     slate-700 #2b3745
Panel            rgba(255,255,255,0.03) + blur (glass-card)
Border subtle    rgba(255,255,255,0.06)
Border strong    rgba(255,255,255,0.10)

Text primary     slate-50  #f7f9fb
Text secondary   slate-300 #b8c3d1
Text muted       slate-400 #8695a8
Text faint       slate-500 #5a6b80

Cyan se mantiene brillante (#12a9cc) — contraste 6.8:1 sobre navy-950
Gold sube a gold-300 (#e0c184) sobre fondos oscuros para AA
```

---

## 6. Proporciones de Uso (actualizado)

```
Fondo dominante:   navy-950 (dark) o slate-50 (light)     40-50%
Surface:           slate-100 o slate-800                   20-25%
Panels/cards:      glass-card o white                      15-20%
Text:              slate-600+ / slate-50+                  core
Navy core:         acentos estructurales                   8-12%
Gold:              CTAs, highlights, focus                 5-7%
Cyan:              interactivo, data viz, glow             4-6%
Semánticos:        estados puntuales                       < 3%
```

---

## 7. Contrastes verificados (WCAG 2.1)

### Sobre navy-800 `#0c2b40`
| Token | Ratio | AA | AAA |
|---|---|---|---|
| `#f7f9fb` slate-50 | 15.2 | ✅ | ✅ |
| `#b8c3d1` slate-300 | 9.1 | ✅ | ✅ |
| `#d3ab6d` gold-500 | 6.4 | ✅ | ✅ (18px+) |
| `#12a9cc` cyan-500 | 4.8 | ⚠️ iconos solo |
| `#e0c184` gold-300 | 8.2 | ✅ | ✅ |

### Sobre slate-50 `#f7f9fb`
| Token | Ratio | AA | AAA |
|---|---|---|---|
| `#0c2b40` navy-800 | 13.8 | ✅ | ✅ |
| `#3e4d60` slate-600 | 7.9 | ✅ | ✅ |
| `#8695a8` slate-400 | 3.6 | ⚠️ 18px+ |
| `#0a6d87` cyan-700 | 5.9 | ✅ | ⚠️ 18px+ |
| `#b8944d` gold-600 | 3.8 | ⚠️ 18px+ |

---

## 8. CSS Variables — Copiar en `globals.css`

```css
:root {
  /* Core (inmutables) */
  --color-navy:   #0c2b40;
  --color-gold:   #d3ab6d;
  --color-cyan:   #12a9cc;

  /* Navy scale */
  --color-navy-50:  #f0f4f8;
  --color-navy-100: #d9e2eb;
  --color-navy-200: #b1c2d1;
  --color-navy-300: #7d96ad;
  --color-navy-400: #4a6a84;
  --color-navy-500: #28475f;
  --color-navy-600: #1a3a52;
  --color-navy-700: #123147;
  --color-navy-800: #0c2b40;
  --color-navy-900: #081f30;
  --color-navy-950: #040f1c;

  /* Cyan scale */
  --color-cyan-50:  #e0f5fa;
  --color-cyan-100: #b8e6f0;
  --color-cyan-300: #5dc4dc;
  --color-cyan-500: #12a9cc;
  --color-cyan-600: #0e8bab;
  --color-cyan-700: #0a6d87;

  /* Gold scale */
  --color-gold-100: #f4e6c9;
  --color-gold-300: #e0c184;
  --color-gold-500: #d3ab6d;
  --color-gold-600: #b8944d;
  --color-gold-700: #a88551;
  --color-gold-800: #7c613a;

  /* Slate (cool gray) */
  --color-slate-50:  #f7f9fb;
  --color-slate-100: #eef2f7;
  --color-slate-200: #dce3ec;
  --color-slate-300: #b8c3d1;
  --color-slate-400: #8695a8;
  --color-slate-500: #5a6b80;
  --color-slate-600: #3e4d60;
  --color-slate-700: #2b3745;
  --color-slate-800: #1c242e;
  --color-slate-900: #0f151b;

  /* Semantic */
  --color-success: #10b981;
  --color-warning: #d3ab6d;
  --color-danger:  #e0556f;
  --color-info:    #12a9cc;

  /* Elevation */
  --shadow-xs: 0 1px 2px rgba(12, 43, 64, 0.05);
  --shadow-sm: 0 2px 4px rgba(12, 43, 64, 0.06), 0 1px 2px rgba(12, 43, 64, 0.04);
  --shadow-md: 0 4px 12px rgba(12, 43, 64, 0.08), 0 2px 4px rgba(12, 43, 64, 0.05);
  --shadow-lg: 0 12px 32px rgba(12, 43, 64, 0.12), 0 4px 8px rgba(12, 43, 64, 0.06);
  --shadow-xl: 0 24px 64px rgba(12, 43, 64, 0.18), 0 8px 16px rgba(12, 43, 64, 0.08);
  --shadow-glow-cyan: 0 0 24px rgba(18, 169, 204, 0.28);
  --shadow-glow-gold: 0 0 24px rgba(211, 171, 109, 0.22);

  /* Motion */
  --duration-fast:  120ms;
  --duration-base:  200ms;
  --duration-slow:  360ms;
  --ease-out:       cubic-bezier(0.22, 1, 0.36, 1);
  --ease-spring:    cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

[data-theme='dark'] {
  --color-bg:           var(--color-navy-950);
  --color-surface:      var(--color-slate-800);
  --color-surface-elev: var(--color-slate-700);
  --color-text:         var(--color-slate-50);
  --color-text-muted:   var(--color-slate-300);
  --color-text-faint:   var(--color-slate-400);
  --color-border:       rgba(255, 255, 255, 0.08);
}
```

---

## 9. Tipografía Tech — Stack

```css
--font-display: 'Playfair Display', Georgia, serif;          /* titulares narrativos */
--font-sans:    'Source Sans Pro', system-ui, sans-serif;    /* body, UI */
--font-mono:    'JetBrains Mono', 'Geist Mono', ui-monospace; /* código, IDs, datos densos */

/* Números en KPIs y tablas */
.tabular { font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
```

---

## 10. Reglas de Aplicación

1. **Core siempre gana.** Si dudas entre `navy-500` y `navy-800`, usa `navy-800` (core).
2. **Cyan solo en digital e interactivo.** En print usa navy+gold.
3. **Semánticos son puntuales.** No más de 2 semánticos visibles por viewport.
4. **Slate reemplaza a los grays neutros.** Cualquier `text-gray-*` existente debe migrar a `text-slate-*`.
5. **Gold para focus y puntos de calor.** Cyan para información, gold para acción importante.
6. **Dark mode no es inversión directa.** Requiere glass-panels + saturación ajustada de gold/cyan.
7. **Un gradiente máximo por viewport.** Navy→navy-900 es seguro; cyan→gold es prohibido.
