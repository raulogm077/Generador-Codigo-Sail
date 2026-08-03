<!--
  Plantilla 05 — Integraciones consumidas
  Una entrada por Integration y por Connected System. Endpoints, métodos, auth (enmascarada), callers.
-->

# Integraciones consumidas

> Cada Integration object y cada Connected System del export, con su contrato técnico y quién la invoca.

## Resumen

| Integration | Connected System | Sistema externo | Método | Callers |
|---|---|---|---|---|
| `{{int_1}}` | `{{cs_1}}` | {{sistema}} | {{verb}} | {{n callers}} |
| `{{int_2}}` | `{{cs_2}}` | {{sistema}} | {{verb}} | {{n callers}} |

## Connected Systems

> Conectores reusables hacia sistemas externos.

### `{{cs_NombreTecnico_1}}`

| Campo | Valor |
|---|---|
| Nombre visible | {{nombre_visible}} |
| Tipo | HTTP / OAuth 2.0 / Salesforce / SAP / JDBC / plugin custom — `{{tipo_exacto}}` |
| Base URL | `{{url_enmascarada_si_lleva_credenciales}}` |
| Auth type | NONE / BASIC / OAUTH2_CLIENT_CREDENTIALS / OAUTH2_AUTH_CODE / API_KEY |
| Credenciales | 🔒 Enmascaradas (referenciadas desde ICF: `{{clave_icf}}`) |
| Timeout | {{timeout_o_default}} |
| Estado | ✅/🔵/🟡 — Evidencia: `{{ruta_xml}}` |

**Propósito (inferido):** {{qué sistema externo es y qué se intercambia con él}}

**Integrations que lo usan:** `{{int_1}}`, `{{int_2}}`.

---

### `{{cs_NombreTecnico_2}}`

{{Repetir.}}

## Integrations

> Llamadas concretas a endpoints de los Connected Systems.

### `{{int_NombreTecnico_1}}` — {{nombre_visible}}

| Campo | Valor |
|---|---|
| Sistema externo | {{sistema}} |
| Connected System | `{{cs_asociado}}` |
| Método HTTP | GET / POST / PUT / PATCH / DELETE |
| Endpoint | `{{base_url_enmascarada}}{{path}}` |
| Estado | ✅/🔵 — Evidencia: `{{ruta_xml}}` |

**Parámetros**

| Tipo | Nombre | Valor / Origen | Notas |
|---|---|---|---|
| path | `{{p_1}}` | `{{origen, p. ej. ri!idCliente}}` | — |
| query | `{{q_1}}` | `{{cons!FILTRO_DEFAULT}}` | — |
| header | `Authorization` | `{{cons!TOKEN_X}}` 🔒 | enmascarado |
| header | `Content-Type` | `application/json` | — |

**Request body**

```{{lenguaje_o_pseudocódigo}}
{{Estructura extraída de <requestBody>/<expression> del Integration XML.
Si es SAIL, mostrar la forma del payload, no el SAIL crudo.
Si hay valores que parecen secretos, enmascararlos.}}
```

**Response / output mapping**

```{{lenguaje_o_pseudocódigo}}
{{Estructura esperada de respuesta. Si la integración tiene <responseMapping>, mostrar el mapeo.}}
```

**Códigos de error contemplados**

- {{código_o_caso}} → {{cómo lo maneja el caller}}
- {{Si no hay manejo explícito, marcar como 🔴 riesgo y mover a 09-valor-adicional.md.}}

**Quién la invoca** (del grafo de Fase 3)

| Caller | Tipo | Contexto |
|---|---|---|
| `{{pm_1}}` | Process Model | nodo `{{nodo_id}}` |
| `{{rule_1}}` | Expression Rule | invocación directa |
| `{{interface_1}}` | Interface | botón / acción `{{descripción}}` |

---

### `{{int_NombreTecnico_2}}`

{{Repetir.}}

## Configuración por entorno (ICF)

> Overrides de URL, credenciales y otros parámetros por entorno.

| Connected System / Constant | Propiedad | DEV | PRE | PRO | Notas |
|---|---|---|---|---|---|
| `{{cs_1}}` | baseUrl | `{{url_dev_enmascarada}}` | `{{url_pre}}` | `{{url_pro}}` | — |
| `{{cs_1}}` | clientId | 🔒 | 🔒 | 🔒 | Enmascarados |
| `{{cs_1}}` | clientSecret | 🔒 | 🔒 | 🔒 | Enmascarados |

> Si solo hay un ICF, mostrar solo la columna correspondiente. Si no hay ICF, omitir esta sección.

## Hallazgos

- 🔴 {{Integraciones sin manejo de error explícito}}: {{lista}}.
- 🟡 {{Integraciones con timeout muy alto o muy bajo}}: {{lista}}.
- 🟡 {{Integraciones cuyo endpoint vive en una constant con valor vacío}}: {{lista}} — pendiente con DevOps.
- ✅ {{Integraciones bien encapsuladas en expression rules `INT_*`}}: {{lista}}.

## Resumen rápido

- Total Integrations: {{N}}
- Total Connected Systems: {{N}}
- Sistemas externos distintos: {{N}} ({{lista corta}})
- Integraciones sin caller detectado en el export (🟡 huérfanas): {{N}}
- Integraciones con secretos enmascarados: {{N}}
