# Sistema de Color — DETA Design Reference

## Paleta Principal

### Cyan DETA (Primario)
```
Hex: #12a9CC
RGB: 18, 169, 204
HSL: 193°, 84%, 44%
CMYK: 90, 17, 0, 20
```

**Usos:**
- CTAs y botones primarios
- Links y acentos interactivos
- Iconos y elementos destacados
- Líneas decorativas

### Navy (Secundario)
```
#0f2e36 — Navy oscuro (logo, texto sobre blanco)
#0c2b40 — Navy estándar (headers, fondos)
```

**Usos:**
- Headers y navegación
- Fondos de secciones destacadas
- Texto sobre fondo claro
- Cards con fondo oscuro

### Neutros
```
#000000 — Negro (texto principal)
#4b4b4b — Gris (texto secundario)
#ffffff — Blanco (fondos, texto sobre oscuro)
#f4f6f9 — Gris claro (secciones alternas)
```

## Combinaciones Recomendadas

### Texto sobre fondo blanco
| Color | Ratio de contraste | Accesible AA | Accesible AAA |
|---|---|---|---|
| Negro `#000000` | 21:1 | ✅ | ✅ |
| Navy `#0c2b40` | 13.5:1 | ✅ | ✅ |
| Gris `#4b4b4b` | 7.2:1 | ✅ | ✅ |

### Texto sobre fondo navy
| Color | Ratio de contraste | Accesible AA |
|---|---|---|
| Blanco `#ffffff` | 14.5:1 | ✅ |
| Cyan `#12a9CC` | 4.8:1 | ⚠️ solo para iconos |

### Cyan sobre blanco
| Color | Ratio de contraste | Accesible AA |
|---|---|---|
| Cyan `#12a9CC` | 3.4:1 | ❌ solo para backgrounds |

## Uso por contexto

### Botones
```css
.btn-primary {
  background: var(--deta-cyan);
  color: var(--deta-white);
  border: 2px solid var(--deta-cyan);
}

.btn-primary:hover {
  background: var(--deta-navy-dark);
  border-color: var(--deta-navy-dark);
}

.btn-secondary {
  background: transparent;
  color: var(--deta-navy);
  border: 2px solid var(--deta-navy);
}

.btn-secondary:hover {
  background: var(--deta-navy);
  color: var(--deta-white);
}
```

### Badges y tags
```css
.badge-accent {
  background: rgba(18, 169, 204, 0.1);
  color: var(--deta-cyan);
  border: 1px solid rgba(18, 169, 204, 0.3);
}

.badge-dark {
  background: var(--deta-navy);
  color: var(--deta-white);
}

.badge-gold {
  background: rgba(211, 171, 109, 0.15);
  color: #b8944d;
  border: 1px solid rgba(211, 171, 109, 0.3);
}
```

### Cards con borde
```css
.card-bordered {
  background: var(--deta-white);
  border-left: 4px solid var(--deta-cyan);
  box-shadow: var(--shadow);
}

.card-dark {
  background: var(--deta-navy);
  color: var(--deta-white);
}

.card-gold {
  background: linear-gradient(135deg, var(--deta-navy-dark) 0%, var(--deta-navy) 100%);
  color: var(--deta-white);
  border-top: 4px solid var(--deta-gold);
}
```

## Aplicación en gradientes

```css
.hero-gradient {
  background: linear-gradient(
    135deg,
    var(--deta-navy-dark) 0%,
    var(--deta-navy) 50%,
    var(--deta-cyan) 100%
  );
}

.section-alternate {
  background: linear-gradient(
    180deg,
    var(--bg-secondary) 0%,
    var(--deta-white) 100%
  );
}

.accent-gradient {
  background: linear-gradient(
    90deg,
    var(--deta-cyan) 0%,
    var(--deta-cyan-light) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

## Estados de color para UI

### Éxito
```css
--color-success: #22c55e; /* Verde */
--color-success-bg: rgba(34, 197, 94, 0.1);
```

### Error
```css
--color-error: #ef4444; /* Rojo */
--color-error-bg: rgba(239, 68, 68, 0.1);
```

### Warning
```css
--color-warning: #f59e0b; /* Ámbar */
--color-warning-bg: rgba(245, 158, 11, 0.1);
```

### Info
```css
--color-info: var(--deta-cyan);
--color-info-bg: rgba(18, 169, 204, 0.1);
```

## Sombras con color

```css
.shadow-cyan {
  box-shadow: 0 4px 14px rgba(18, 169, 204, 0.25);
}

.shadow-navy {
  box-shadow: 0 4px 14px rgba(12, 43, 64, 0.25);
}
```
