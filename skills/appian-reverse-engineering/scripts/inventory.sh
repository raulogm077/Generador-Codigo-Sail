#!/usr/bin/env bash
# inventory.sh — Inventario inicial de artefactos Appian.
# Uso: bash inventory.sh <ruta>
# Genera salida por stdout. Pensado para alimentar la Fase 1.

set -u
ROOT="${1:-.}"

if [ ! -d "$ROOT" ]; then
  echo "[error] No existe la ruta: $ROOT" >&2
  exit 1
fi

# Ignora ruido típico
IGNORE_PRUNE=(-path '*/.git' -o -path '*/node_modules' -o -path '*/.DS_Store')

echo "# Inventario inicial — $ROOT"
echo "_Generado: $(date -Iseconds)_"
echo

# ---------- Estructura general ----------
echo "## Estructura de carpetas (2 niveles)"
echo '```'
find "$ROOT" -maxdepth 2 -type d \( "${IGNORE_PRUNE[@]}" \) -prune -o -type d -print 2>/dev/null | sort | head -60
echo '```'
echo

# ---------- Conteo por extensión ----------
echo "## Recuento por extensión"
echo '| Extensión | Ficheros |'
echo '|---|---:|'
find "$ROOT" -type f \( "${IGNORE_PRUNE[@]}" \) -prune -o -type f -print 2>/dev/null \
  | sed -n 's/.*\.\([a-zA-Z0-9]\+\)$/\1/p' \
  | tr '[:upper:]' '[:lower:]' \
  | sort | uniq -c | sort -rn | head -30 \
  | awk '{printf "| %s | %s |\n", $2, $1}'
echo

# ---------- Detección de objetos Appian por contenido ----------
echo "## Objetos Appian detectados por contenido"

count_xml_with() {
  local pattern="$1"
  find "$ROOT" -type f -name '*.xml' \( "${IGNORE_PRUNE[@]}" \) -prune -o -type f -name '*.xml' -print 2>/dev/null \
    | xargs -I{} grep -l -E "$pattern" "{}" 2>/dev/null | wc -l | tr -d ' '
}

declare -a PATTERNS=(
  "Application|<application\\b|<applicationDefinition\\b"
  "Site|<site\\b|<sitePage\\b"
  "Portal|<portal\\b|<portalPage\\b"
  "Record Type|<recordType\\b"
  "Record Action|<recordAction\\b"
  "Record View|<recordView\\b"
  "Interface|<interface\\b|a!formLayout|a!sectionLayout"
  "Expression Rule|<expressionRule\\b"
  "Decision|<decision\\b|<decisionTable\\b"
  "Process Model|<processModel\\b"
  "Constant|<constant\\b"
  "Data Store|<dataStore\\b"
  "Connected System|<connectedSystem\\b"
  "Integration|<integration\\b"
  "Web API|<webApi\\b"
  "Group|<group\\b"
  "Folder|<folder\\b"
  "Document|<document\\b"
)

echo '| Tipo de objeto | Cantidad estimada (XMLs con patrón) |'
echo '|---|---:|'
for entry in "${PATTERNS[@]}"; do
  name="${entry%%|*}"
  pattern="${entry#*|}"
  cnt=$(count_xml_with "$pattern")
  echo "| $name | $cnt |"
done
echo

# ---------- CDTs (XSDs) ----------
echo "## CDTs (XSDs)"
xsd_count=$(find "$ROOT" -type f -name '*.xsd' \( "${IGNORE_PRUNE[@]}" \) -prune -o -type f -name '*.xsd' -print 2>/dev/null | wc -l | tr -d ' ')
echo "- Ficheros .xsd detectados: $xsd_count"
echo

# ---------- BPMN ----------
echo "## BPMN"
bpmn_count=$(find "$ROOT" -type f -name '*.bpmn' \( "${IGNORE_PRUNE[@]}" \) -prune -o -type f -name '*.bpmn' -print 2>/dev/null | wc -l | tr -d ' ')
echo "- Ficheros .bpmn detectados: $bpmn_count"
echo

# ---------- ICF y configuración ----------
echo "## Configuración por entorno"
echo '| Tipo | Ficheros |'
echo '|---|---|'
icf_files=$(find "$ROOT" -type f \( -name 'import-customization-file*.properties' -o -name '*.icf' \) 2>/dev/null | head -20)
if [ -n "$icf_files" ]; then
  echo "| ICF | $(echo "$icf_files" | wc -l | tr -d ' ') fichero(s) |"
fi
prop_files=$(find "$ROOT" -type f -name '*.properties' ! -name 'import-customization-file*' 2>/dev/null | head -20)
if [ -n "$prop_files" ]; then
  echo "| .properties (otros) | $(echo "$prop_files" | wc -l | tr -d ' ') fichero(s) |"
fi
echo

# ---------- SQL ----------
echo "## Scripts SQL/DDL"
sql_count=$(find "$ROOT" -type f \( -name '*.sql' -o -name '*.ddl' \) 2>/dev/null | wc -l | tr -d ' ')
echo "- Ficheros SQL/DDL detectados: $sql_count"
echo

# ---------- Documentación previa ----------
echo "## Documentación previa detectada"
find "$ROOT" -type f \( -iname 'README*' -o -name '*.md' -o -name '*.txt' -o -iname '*.pdf' -o -iname '*.docx' \) 2>/dev/null | head -20 \
  | sed 's|^|- |'
echo

# ---------- Prefijos de naming dominantes ----------
echo "## Prefijos de naming detectados en XMLs (top 20)"
find "$ROOT" -type f -name '*.xml' 2>/dev/null \
  | xargs -I{} basename "{}" .xml 2>/dev/null \
  | sed -E 's/[_-].*$//' \
  | sort | uniq -c | sort -rn | head -20 \
  | awk '{printf "- %s (%s veces)\n", $2, $1}'
echo

echo "## Notas"
echo "- Las cantidades por tipo se basan en patrones de contenido y son aproximadas."
echo "- Cruzar con análisis manual antes de afirmar nada."
echo "- Marcar como pendiente cualquier conteo con confianza baja."
