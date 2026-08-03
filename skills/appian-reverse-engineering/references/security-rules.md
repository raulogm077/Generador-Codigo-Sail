# Reglas de seguridad

Detección y enmascarado de secretos antes de escribir cualquier documento o dato en la web.

## Principio

Los artefactos Appian (especialmente ICFs y connected systems) pueden contener:

- Contraseñas en claro.
- Tokens / API keys.
- Certificados privados.
- URLs con credenciales embebidas (`https://user:pass@host`).
- Strings de conexión a BBDD con contraseña.

**Nunca** los reproduzcas en los documentos ni en la web. Detéctalos, enmascáralos y regístralos como **riesgo de seguridad** (sin exponer el valor).

## Patrones de detección (regex orientativos)

Aplica búsquedas como estas al inicio de la Fase 6 y antes de poblar la web:

| Tipo | Patrón |
|---|---|
| Password en propiedades | `(?i)(password\|passwd\|pwd)\s*[:=]\s*[^\s]+` |
| API key | `(?i)(api[_-]?key\|apikey)\s*[:=]\s*[^\s]+` |
| Secret/token | `(?i)(secret\|token\|bearer)\s*[:=]\s*[^\s]+` |
| Credenciales en URL | `https?://[^/\s:]+:[^@\s]+@[^\s]+` |
| String de conexión JDBC | `jdbc:[a-z]+://[^?\s]+\?[^\s]*password=[^&\s]+` |
| AWS access key | `AKIA[0-9A-Z]{16}` |
| Private key PEM | `-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----` |
| GitHub PAT | `gh[pousr]_[A-Za-z0-9]{36,}` |
| Slack token | `xox[abps]-[A-Za-z0-9-]{10,}` |
| JWT (sospechoso si está hardcoded) | `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` |
| Base64 sospechoso (>40 chars en property name `password`/`secret`/`key`) | combinar el nombre de propiedad con el valor |

## Búsqueda recomendada en la carpeta

```bash
# Patrones genéricos
grep -rIEn "(?i)(password|passwd|pwd|secret|api[_-]?key|apikey|token|bearer)[[:space:]]*[:=]" <ruta> 2>/dev/null

# Credenciales en URL
grep -rIEn "https?://[^/[:space:]:]+:[^@[:space:]]+@" <ruta> 2>/dev/null

# Private keys
grep -rIEln "BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY" <ruta> 2>/dev/null

# Cadenas JDBC
grep -rIEn "jdbc:[a-z]+://[^[:space:]?]+\?[^[:space:]]*password=" <ruta> 2>/dev/null
```

Usa `scripts/detect_secrets.sh` para hacer este barrido de forma estandarizada.

## Acción ante un secreto detectado

1. **No copies el valor** a ningún documento ni dato de la web.
2. **Enmascáralo** consistentemente como `***ENMASCARADO***` o `[REDACTED]`.
3. Crea una entrada en `05_riesgos_deuda_tecnica.md` con:
   - **Tipo**: Seguridad — Secreto expuesto.
   - **Evidencia**: ruta del fichero, **sin** el valor; opcionalmente número de línea y nombre de la propiedad.
   - **Impacto**: Alto (potencial exposición de credenciales).
   - **Prioridad**: Crítica si está en una rama/repo público; Alta en cualquier caso.
   - **Recomendación**: rotar la credencial, mover a un vault o gestor de secretos, usar variables de entorno / ICF cifrado.
   - **Responsable sugerido**: Tech lead Appian + responsable de seguridad.
4. En la web, en la sección de Riesgos, muestra "Secreto detectado en `<ruta>`" sin exponer el valor.

## Falsos positivos comunes

Antes de marcar como secreto, descarta:

- **Ejemplos en documentación** o README explícitamente marcados como ejemplo.
- **Valores de prueba** en ficheros `test*` con contraseñas tipo `password123` (igualmente, regístralos como mala práctica si están en repo de producción).
- **Variables placeholder** del tipo `${SECRET_NAME}`, `<<PUT_TOKEN_HERE>>`, `<your-token>`.

Si dudas, regístralo como pendiente de validación con responsable de seguridad.

## Otros patrones de riesgo de seguridad (sin ser secretos)

Detéctalos y márcalos también:

- Objetos Appian con seguridad `Public` o accesibles a `All Users` cuando manejan datos sensibles.
- Connected systems con autenticación `None` apuntando a APIs externas.
- Web APIs con seguridad débil (sin autenticación, accesibles públicamente).
- Process models que envían emails con datos sensibles a destinatarios externos.
- Constants/ICFs con URLs internas expuestas que no deberían serlo.
- SQL en data stores con concatenación de variables (posible SQL injection).
- Expression rules que reciben input de usuario sin validación.

## Política para Markdown

Los entregables son Markdown plano que se renderiza en visores variados (GitHub, VSCode, herramientas internas). Para evitar fugas de información o ejecución no deseada:

- **No incluir bloques HTML crudos** (`<script>`, `<iframe>`, `<style>`) en los entregables.
- **No incluir URLs con credenciales embebidas** (`https://user:pass@host`). Enmascarar siempre.
- **No incluir tokens / secretos** en bloques de código, ni siquiera como ejemplo. Sustituir por `🔒` o `***`.
- **Diagramas Mermaid** se sanean previamente con `scripts/validate_mermaid.py` antes de escribirse (ver `mermaid-rules.md`).

## Comprobación final

Antes de devolver la respuesta:

```bash
bash scripts/detect_secrets.sh <ruta_export>/_doc_generada/
```

Si encuentra algún match en los entregables (no en los originales analizados), **detente y enmascara antes de continuar**.
