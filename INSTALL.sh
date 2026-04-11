#!/bin/bash
# DETA Skills v2 — Script de instalación
# Instala las 10 skills en ~/.claude/skills/

set -e

SKILLS_DIR="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE=$(date +%Y%m%d-%H%M%S)

echo "🚀 DETA Skills v2 — Instalador"
echo "================================"
echo ""

# Crear directorio si no existe
mkdir -p "$SKILLS_DIR"

# Backup de skills existentes si hay
if [ -d "$SKILLS_DIR" ] && [ "$(ls -A $SKILLS_DIR 2>/dev/null)" ]; then
  BACKUP_DIR="$HOME/.claude/skills-backup-$DATE"
  echo "📦 Haciendo backup de skills actuales en:"
  echo "   $BACKUP_DIR"
  cp -r "$SKILLS_DIR" "$BACKUP_DIR"
  echo "   ✅ Backup completo"
  echo ""
fi

# Instalar cada skill
SKILLS=(
  "coding"
  "deta-design"
  "market-research"
  "keyword-research"
  "research-digest"
  "github-workflow"
  "seo-audit"
  "app-builder"
  "document-suite"
  "graphic-design"
)

echo "📥 Instalando skills..."
for skill in "${SKILLS[@]}"; do
  if [ -d "$SCRIPT_DIR/$skill" ]; then
    rm -rf "$SKILLS_DIR/$skill"
    cp -r "$SCRIPT_DIR/$skill" "$SKILLS_DIR/$skill"
    echo "   ✅ $skill"
  else
    echo "   ⚠️  $skill — directorio no encontrado, omitido"
  fi
done

echo ""
echo "✅ Instalación completa"
echo ""
echo "Skills instaladas en: $SKILLS_DIR"
echo ""
echo "Para verificar: ls ~/.claude/skills/"
echo ""
echo "Reinicia Claude Code para que las skills se carguen."
