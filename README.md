# DETA Skills v2
**Generadas:** 2026-04-10 | **Para:** OpenClaw / Claude Code

## Skills incluidas

| Skill | Descripción | Tipo |
|---|---|---|
| `coding` | TypeScript, Next.js, Supabase, QA, GitHub Actions | Mejorada |
| `deta-design` | Sistema de diseño, tokens de marca, anti-slop | Mejorada |
| `market-research` | Investigación de mercado, SEO, CORE-EEAT, GEO | Mejorada |
| `keyword-research` | Keywords, PyTrends, intent, clusters | Mejorada (YAML corregido) |
| `research-digest` | Research profundo multi-fuente y síntesis ejecutiva | Mejorada |
| `github-workflow` | Git, GitHub, PRs, GitHub Actions, CI/CD | ✨ Nueva |
| `seo-audit` | Auditoría SEO técnica y on-page dedicada | ✨ Nueva |
| `app-builder` | Apps full-stack Next.js + Supabase + Auth | ✨ Nueva |
| `document-suite` | PDF, DOCX, Excel, Sheets unificados | ✨ Nueva |
| `graphic-design` | Assets visuales, OG images, SVG, infografías | ✨ Nueva |

## Instalación

```bash
# Opción 1 — Script automático (recomendado)
cd skills-DETA-v2
chmod +x INSTALL.sh
./INSTALL.sh

# Opción 2 — Manual
cp -r coding deta-design market-research keyword-research research-digest \
      github-workflow seo-audit app-builder document-suite graphic-design \
      ~/.claude/skills/
```

## Verificar instalación

```bash
ls ~/.claude/skills/
# Debe mostrar las 10 carpetas
```

Reiniciar Claude Code después de instalar.
