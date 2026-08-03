#!/usr/bin/env bash
# render_diagrams.sh — Render de diagramas Mermaid (Tipos A/B/C) a SVG.
#
# Estrategia para procesos BPMN (carpeta 08-procesos-bpmn/):
#   - El .bpmn XML semántico (sin layout DI) SIEMPRE se genera por Claude.
#     Se entrega tal cual: el usuario lo abre en Camunda Modeler, draw.io,
#     bpmn.io o Signavio para vista BPMN profesional con layout automático.
#   - El .mmd Tipo C (BPMN-styled con shapes, iconos y colores) es la VISTA
#     PRELIMINAR embebida en el .md. Se renderiza con mmdc a .svg.
#
# Estrategia para arquitectura/datos:
#   - .mmd Tipo A (flowchart) o Tipo B (erDiagram) renderizado con mmdc.
#
# Uso:
#   render_diagrams.sh --check
#       Reporta qué herramientas están disponibles.
#
#   render_diagrams.sh --mermaid <fichero.mmd> [<salida.svg>]
#       Renderiza un único .mmd a SVG.
#
#   render_diagrams.sh --batch <carpeta>
#       Renderiza todos los .mmd de la carpeta (recursivo).
#       Los .bpmn se entregan sin renderizar (son fuente para Camunda/draw.io).
#
# Códigos de salida:
#   0  todo OK
#   1  alguna herramienta no disponible (continúa procesando lo que pueda)
#   2  error de argumentos

set -uo pipefail

# ------------------------------------------------------------
# Configuración de render
# ------------------------------------------------------------
# mmdc usa puppeteer + chrome-headless-shell. En entornos como sandboxes,
# CI o contenedores Docker, Chrome con sandbox falla. Pasamos --no-sandbox
# vía puppeteer-config y forzamos HOME hacia donde esté el cache de chrome.

PUPPETEER_CONFIG_TMP="$(mktemp -t puppeteer-config-XXXXXX.json)"
cat > "$PUPPETEER_CONFIG_TMP" <<EOF
{"args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]}
EOF

# Detectar HOME correcto para chrome cache.
# mmdc se queja si no encuentra la versión específica de chrome-headless-shell
# que dice su puppeteer-core; preferimos la ubicación que tenga la versión más
# antigua (131.x es la habitual de @mermaid-js/mermaid-cli; 148.x es de otros
# tooling más nuevo y mmdc no la reconoce). Si solo hay una, esa.
CHROME_HOME=""
for candidate in "/home/claude" "$HOME" "/root" "/tmp"; do
  if [ -d "$candidate/.cache/puppeteer/chrome-headless-shell" ]; then
    # Verificar que tenga al menos una versión instalada
    if ls "$candidate/.cache/puppeteer/chrome-headless-shell/"linux-131.* >/dev/null 2>&1; then
      CHROME_HOME="$candidate"
      break
    fi
  fi
done
# Si no encontramos la 131.x, caemos a cualquier cache disponible
if [ -z "$CHROME_HOME" ]; then
  for candidate in "$HOME" "/home/claude" "/root"; do
    if [ -d "$candidate/.cache/puppeteer/chrome-headless-shell" ]; then
      CHROME_HOME="$candidate"
      break
    fi
  done
fi

cleanup() { rm -f "$PUPPETEER_CONFIG_TMP"; }
trap cleanup EXIT

# ------------------------------------------------------------
# Detección de herramientas
# ------------------------------------------------------------

has_cmd() { command -v "$1" >/dev/null 2>&1; }

HAS_MMDC=0
HAS_XMLLINT=0
HAS_DOT=0

if has_cmd mmdc; then HAS_MMDC=1; fi
if has_cmd xmllint; then HAS_XMLLINT=1; fi
if has_cmd dot; then HAS_DOT=1; fi

# ------------------------------------------------------------
# Comando: --check
# ------------------------------------------------------------

cmd_check() {
  echo "Estado de herramientas de render:"
  echo ""
  echo "  Mermaid (render principal: arquitectura, modelo de datos, BPMN-styled)"
  if [ "$HAS_MMDC" -eq 1 ]; then
    echo "    ✓ mmdc (Mermaid CLI) disponible"
    if [ -n "$CHROME_HOME" ]; then
      echo "    ✓ Chrome cache encontrado en: $CHROME_HOME/.cache/puppeteer"
    else
      echo "    ⚠ Chrome cache no encontrado. mmdc puede necesitar:"
      echo "       npx puppeteer browsers install chrome-headless-shell"
    fi
  else
    echo "    ✗ mmdc NO disponible — instala con:"
    echo "       npm install -g @mermaid-js/mermaid-cli"
    echo "    Sin mmdc: los diagramas quedarán embebidos como bloques mermaid en los .md"
    echo "    (GitHub/VSCode/preview Markdown los renderizan al vuelo)."
  fi
  echo ""
  echo "  BPMN 2.0 XML (siempre se genera, no requiere render)"
  echo "    ✓ Los .bpmn semánticos se entregan tal cual."
  echo "      Abre en: Camunda Modeler, draw.io, bpmn.io, Signavio."
  echo "      Estas herramientas calculan el layout automáticamente y muestran"
  echo "      iconos BPMN auténticos (círculos start/end, rombos gateway, etc.)."
  echo ""
  echo "  Utilidades complementarias"
  if [ "$HAS_XMLLINT" -eq 1 ]; then
    echo "    ✓ xmllint disponible (validación de .bpmn)"
  else
    echo "    - xmllint NO disponible (opcional, mejora detección de errores XML)"
  fi
  if [ "$HAS_DOT" -eq 1 ]; then
    echo "    ✓ dot (Graphviz) disponible (alternativa para diagramas densos)"
  else
    echo "    - dot NO disponible (opcional)"
  fi
  echo ""
  if [ "$HAS_MMDC" -eq 1 ]; then
    echo "Estado global: ✅ Render completo."
    echo "  - .mmd → .svg con mmdc."
    echo "  - .bpmn → se entrega como fuente para abrir en modelador BPMN."
  else
    echo "Estado global: 🟡 Sin mmdc: los .mmd quedarán embebidos en los .md."
    echo "  Sigue siendo legible en GitHub/VSCode. Los .bpmn se entregan igual."
  fi
}

# ------------------------------------------------------------
# Render Mermaid (tipos A, B, C)
# ------------------------------------------------------------

render_mermaid() {
  local in="$1"
  local out="${2:-${in%.mmd}.svg}"
  if [ "$HAS_MMDC" -ne 1 ]; then
    write_pending "$in" "$out" "mmdc no instalado. El bloque mermaid sigue embebido en el .md asociado."
    return 1
  fi

  # Detectar el tipo de diagrama por la primera línea no vacía
  local first
  first="$(grep -m1 -E '\S' "$in" | tr -d '[:space:]')"
  local theme="default"
  local bg="white"

  # Tipo C (BPMN-styled): usa default + fondo blanco para que las lanes se vean amarillas
  # Tipo A/B: neutral + transparente para integración limpia
  if grep -q "classDef startNode" "$in"; then
    theme="default"
    bg="white"
  else
    theme="neutral"
    bg="transparent"
  fi

  local mmdc_env=""
  if [ -n "$CHROME_HOME" ]; then
    mmdc_env="HOME=$CHROME_HOME"
  fi

  if env $mmdc_env mmdc -i "$in" -o "$out" -t "$theme" -b "$bg" -p "$PUPPETEER_CONFIG_TMP" 2>/tmp/mmdc.err; then
    echo "  ✓ $in → $out (tema: $theme)"
    return 0
  else
    echo "  ✗ Falló render de $in:" >&2
    sed 's/^/      /' /tmp/mmdc.err >&2
    write_pending "$in" "$out" "mmdc falló. Revisa la sintaxis Mermaid o usa GitHub/VSCode preview."
    return 1
  fi
}

# ------------------------------------------------------------
# Pending marker
# ------------------------------------------------------------

write_pending() {
  local in="$1"
  local out="$2"
  local msg="$3"
  local pending="${in}.render-pending.txt"
  cat > "$pending" <<EOF
Render pendiente para: $in
Salida esperada: $out
Motivo: $msg

Cómo resolver:
  - Si falta mmdc: instala con:  npm install -g @mermaid-js/mermaid-cli
  - Reintentar:                 $(basename "$0") --mermaid $in $out
  - Alternativa: el bloque mermaid sigue embebido en el .md asociado;
    GitHub, VSCode y la mayoría de previewers Markdown lo renderizan al vuelo.

Generado por render_diagrams.sh
EOF
  echo "  ⚠ Render pendiente. Marcador escrito en $pending"
}

# ------------------------------------------------------------
# Batch
# ------------------------------------------------------------

cmd_batch() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    echo "ERROR: $dir no existe o no es directorio" >&2
    return 2
  fi
  local total=0 ok=0 pending=0

  while IFS= read -r -d '' f; do
    total=$((total + 1))
    if render_mermaid "$f"; then ok=$((ok + 1)); else pending=$((pending + 1)); fi
  done < <(find "$dir" -name '*.mmd' -print0)

  # Informar de los .bpmn (no se renderizan, son fuente)
  local bpmn_count
  bpmn_count="$(find "$dir" -name '*.bpmn' -type f | wc -l)"

  echo ""
  echo "Resumen batch:"
  echo "  Mermaid (.mmd):  $total ficheros, $ok renderizados, $pending pendientes."
  echo "  BPMN (.bpmn):    $bpmn_count ficheros entregados como fuente (abre en Camunda/draw.io)."

  if [ "$pending" -gt 0 ]; then return 1; fi
  return 0
}

# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

main() {
  if [ "$#" -lt 1 ]; then
    sed -n '2,35p' "$0" | sed 's/^# \{0,1\}//'
    return 2
  fi
  case "$1" in
    --check)
      cmd_check
      ;;
    --mermaid)
      shift
      if [ "$#" -lt 1 ]; then echo "Falta fichero .mmd" >&2; return 2; fi
      render_mermaid "$@"
      ;;
    --batch)
      shift
      if [ "$#" -lt 1 ]; then echo "Falta carpeta" >&2; return 2; fi
      cmd_batch "$1"
      ;;
    -h|--help)
      sed -n '2,35p' "$0" | sed 's/^# \{0,1\}//'
      ;;
    *)
      echo "Argumento desconocido: $1" >&2
      return 2
      ;;
  esac
}

main "$@"
