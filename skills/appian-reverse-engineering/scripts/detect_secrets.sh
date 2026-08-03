#!/usr/bin/env bash
# detect_secrets.sh — Detección de patrones de secretos en una carpeta.
# Uso: bash detect_secrets.sh <ruta>
# Salida: tabla Markdown a stdout. Exit code != 0 si se detecta algo.

set -u
ROOT="${1:-.}"

if [ ! -d "$ROOT" ]; then
  echo "[error] No existe la ruta: $ROOT" >&2
  exit 2
fi

found=0
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

scan() {
  local label="$1"
  local pattern="$2"
  # -I: ignora binarios. -n: número de línea. -E: regex extendida.
  grep -rIEn --exclude-dir='.git' --exclude-dir='node_modules' \
    -- "$pattern" "$ROOT" 2>/dev/null \
    | sed -E 's/(:[0-9]+:).{0,40}(password|passwd|pwd|secret|token|bearer|api[_-]?key|apikey)[[:space:]]*[:=][[:space:]]*.*$/\1 [VALOR ENMASCARADO] propiedad detectada: \2/i' \
    | sed -E 's/(:[0-9]+:).*https?:\/\/[^\/[:space:]:]+:[^@[:space:]]+@.*$/\1 [VALOR ENMASCARADO] URL con credenciales detectada/' \
    | sed -E 's/(:[0-9]+:).*-----BEGIN.*PRIVATE KEY.*$/\1 [VALOR ENMASCARADO] private key PEM detectada/' \
    | while IFS= read -r line; do
        printf '| %s | %s |\n' "$label" "$line" >> "$tmp"
        found=1
      done
}

scan "Password/Secret/Token en propiedad" '(^|[^A-Za-z0-9_])(password|passwd|pwd|secret|api[_-]?key|apikey|token|bearer)[[:space:]]*[:=][[:space:]]*[^[:space:]]+'
scan "URL con credenciales embebidas"     'https?://[^/[:space:]:]+:[^@[:space:]]+@[^[:space:]]+'
scan "JDBC connection string con password" 'jdbc:[a-z]+://[^[:space:]?]+\?[^[:space:]]*password=[^&[:space:]]+'
scan "Private key PEM"                    'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY'
scan "AWS access key id"                  'AKIA[0-9A-Z]{16}'
scan "GitHub PAT"                         'gh[pousr]_[A-Za-z0-9]{36,}'
scan "Slack token"                        'xox[abps]-[A-Za-z0-9-]{10,}'
scan "JWT hardcoded (sospechoso)"         'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'

echo "# Resultado de la búsqueda de secretos en \`$ROOT\`"
echo "_Generado: $(date -Iseconds)_"
echo

if [ -s "$tmp" ]; then
  echo "## Coincidencias detectadas"
  echo
  echo '| Patrón | Ubicación |'
  echo '|---|---|'
  cat "$tmp"
  echo
  echo "**Acción:** documentar como riesgo de seguridad en \`05_riesgos_deuda_tecnica.md\` sin reproducir los valores. Recomendar rotación inmediata y movimiento a vault / variables seguras."
  exit 1
else
  echo "## Sin coincidencias"
  echo "No se han detectado patrones de secretos en la ruta analizada."
  exit 0
fi
