<!--
  Plantilla 06 — APIs expuestas (Web APIs)
  Una entrada por Web API. URL pública, método, auth, body esperado, qué hace, grupos autorizados.
-->

# APIs expuestas

> Endpoints HTTP que esta aplicación expone hacia el exterior (otros sistemas, servicios o clientes).

## Resumen

| Web API | Método | URL pública | Auth | Grupos autorizados | Caso de uso |
|---|---|---|---|---|---|
| `{{wa_1}}` | GET | `/suite/webapi/{{endpoint_1}}` | API key | `{{grupo}}` | {{breve}} |
| `{{wa_2}}` | POST | `/suite/webapi/{{endpoint_2}}` | Basic + grupo | `{{grupo}}` | {{breve}} |

## Detalle por Web API

### `{{wa_NombreTecnico_1}}` — {{nombre_visible}}

| Campo | Valor |
|---|---|
| URL pública | `/suite/webapi/{{endpoint_path}}` |
| Método HTTP | GET / POST / PUT / PATCH / DELETE |
| Autenticación | {{NONE / BASIC / API_KEY / autenticación por grupo Appian}} |
| Grupos autorizados | `{{grupo_1}}`, `{{grupo_2}}` |
| Estado | ✅/🔵 — Evidencia: `{{ruta_xml}}` |

**Parámetros**

| Tipo | Nombre | Obligatorio | Tipo de dato | Descripción |
|---|---|---|---|---|
| query | `{{q_1}}` | Sí / No | string | {{descripción}} |
| path | `{{p_1}}` | Sí | long | {{descripción}} |
| header | `Authorization` | Sí | string | {{esquema}} |

**Body esperado (POST/PUT/PATCH)**

```{{lenguaje}}
{{Estructura esperada del request body. Inferida del SAIL en <expression>.
Si solo hay un único tipo aceptado, mostrar; si admite variantes, listar todas.}}
```

Ejemplo:

```json
{
  "{{campo_1}}": "{{ejemplo}}",
  "{{campo_2}}": {{valor_ejemplo}}
}
```

**Qué hace al invocarse** (del SAIL en `<expression>`)

{{Descripción en prosa breve. Ejemplo: "Recibe un payload con datos del expediente, valida los campos obligatorios contra la regla `rule!{{validador}}`, y lanza el process model `PM_CrearExpediente` con esos datos. Devuelve el ID del expediente creado y un código HTTP 201."}}

**Implementación interna**

| Acción | Objeto invocado |
|---|---|
| Lanzar proceso | `a!startProcess(processModel: cons!{{pm_uuid}}, ...)` → `{{PM_lanzado}}` |
| Validar entrada | `rule!{{regla_validacion}}` |
| Consultar datos | `a!queryRecordType(recordType: recordType!{{record}})` |
| Escritura | `a!writeToDataStoreEntity(...)` |

**Respuesta**

```{{lenguaje}}
{{Estructura de la respuesta.}}
```

| Código HTTP | Cuándo | Body |
|---|---|---|
| 200 / 201 | Éxito | `{{descripción}}` |
| 400 | Validación KO | `{{error_format}}` |
| 401 / 403 | Auth fallida o sin permisos | `{{}}` |
| 500 | Error interno | `{{}}` |

**Caso de uso funcional**

{{Quién la llama y para qué. Si es un cliente externo, qué cliente. Si es otro proceso interno, referenciar el caso de uso de `01-funcional.md`.}}

> Estado: ✅/🔵/🟡 — Evidencia: `{{ruta_xml}}`

---

### `{{wa_NombreTecnico_2}}`

{{Repetir.}}

## Hallazgos

- 🔴 **Web APIs con autorización `All Users` o sin grupo explícito**: {{lista o "ninguna"}}.
- 🔴 **Web APIs sin validación de entrada visible** en el SAIL: {{lista o "ninguna"}}.
- 🟡 **Web APIs que no devuelven códigos HTTP explícitos** (siempre 200): {{lista}}.
- 🟡 **Web APIs cuyo process model destino no parece existir** en el export: {{lista}}.

## Resumen rápido

- Total Web APIs: {{N}}
- Por método: GET={{n}} · POST={{n}} · PUT={{n}} · DELETE={{n}}
- Web APIs públicas (sin grupo restrictivo): {{N}}
- Web APIs con autenticación por grupo Appian: {{N}}
