<!--
  Salida esperada (verificación en seco) del agente backlog-writer sobre
  tests/fixtures/mini-export. Datos 100% sintéticos (DEMO_*, UUIDs 00000000-*).
  En una ejecución real las épicas heredan los casos de uso de 01-funcional.md;
  aquí CU-01/CU-02 se derivan de los flujos evidenciados en el propio fixture.
-->

# Backlog de reconstrucción: DEMO App Solicitudes

**🎯 TL;DR**: 2 épicas, 5 historias (2 MVP, 2 fase 2, 1 opcional). Todos los criterios derivan de artefactos reales del export: validaciones de `DEMO_VAL_ValidarImporte`, predicados del formulario, filas de `DEMO_DEC_NivelAprobacion`, gateway y nodos de `DEMO_PM_AprobarSolicitud` y dominio de estados de `DEMO_CONS_ESTADOS`.

## Índice

| HU | Título | Épica | Prioridad | Objetos principales |
|---|---|---|---|---|
| HU-001 | Crear y enviar una solicitud | EP-01 | MVP | `DEMO_IFC_SolicitudForm`, `DEMO_VAL_ValidarImporte`, `DEMO_PM_AprobarSolicitud` |
| HU-002 | Justificar importes altos | EP-01 | fase 2 | `DEMO_IFC_SolicitudForm` |
| HU-003 | Aprobar o rechazar una solicitud según su importe | EP-01 | MVP | `DEMO_PM_AprobarSolicitud`, `DEMO_DEC_NivelAprobacion`, `DEMO_GRP_Aprobadores` |
| HU-004 | Consultar solicitudes filtradas por estado | EP-02 | fase 2 | `DEMO_IFC_SolicitudList`, `DEMO_QR_GetSolicitudes` |
| HU-005 | Consultar el estado por API | EP-02 | opcional | `DEMO_WS_ConsultaEstado`, `DEMO_QR_GetSolicitudes` |

---

## Épica EP-01 — Gestión y aprobación de solicitudes (CU-01)

### HU-001: Crear y enviar una solicitud
**Como** solicitante **quiero** registrar una solicitud con solicitante e importe **para** iniciar su aprobación
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado el formulario "Nueva solicitud" con el campo Importe vacío
Cuando pulso "Enviar"
Entonces veo el mensaje "El importe es obligatorio" y el envío se bloquea

Dado una solicitud con importe 0
Cuando pulso "Enviar"
Entonces veo el mensaje "El importe debe ser mayor que cero"

Dado una solicitud con importe 150000
Cuando pulso "Enviar"
Entonces veo el mensaje "El importe supera el maximo permitido (100.000)"

Dado una solicitud válida con solicitante "DEMO Usuario" e importe 800
Cuando pulso "Enviar"
Entonces el proceso DEMO_PM_AprobarSolicitud arranca con la solicitud como parámetro
```
**Objetos que la implementan hoy**: `DEMO_IFC_SolicitudForm` (interface), `DEMO_VAL_ValidarImporte` (expressionRule), `DEMO_PM_AprobarSolicitud` (processModel), `DEMO Solicitud` (recordType), `DEMO_CDT_Solicitud` (cdt) · **Prioridad de reconstrucción**: MVP
**Evidencia de los criterios**: mensajes literales del `if` anidado en `content/DEMO_VAL_ValidarImporte.xml#definition`; `required: true` de Solicitante/Importe, `validations: local!erroresImporte` y botón Enviar con `validate: true` en `content/DEMO_IFC_SolicitudForm.xml#definition`; arranque con formulario en `processModel/DEMO_PM_AprobarSolicitud.xml#n0` (`startType: userStart`, `form: DEMO_IFC_SolicitudForm`) y PV `solicitud` con `parameter="true"`.

### HU-002: Justificar importes altos
**Como** solicitante **quiero** aportar una justificación cuando el importe supera 1.000 **para** cumplir la política de aprobación
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado una solicitud con importe 1500
Cuando el formulario se recalcula
Entonces el campo "Justificacion" es visible y obligatorio

Dado una solicitud con importe 800
Cuando el formulario se recalcula
Entonces el campo "Justificacion" no se muestra
```
**Objetos que la implementan hoy**: `DEMO_IFC_SolicitudForm` (interface) · **Prioridad de reconstrucción**: fase 2
**Evidencia de los criterios**: `showWhen: ri!importe > 1000` y `required: ri!importe > 1000` del `a!paragraphField` "Justificacion" en `content/DEMO_IFC_SolicitudForm.xml#definition`.

### HU-003: Aprobar o rechazar una solicitud según su importe
**Como** aprobador (miembro de `DEMO_GRP_Aprobadores`) **quiero** aprobar o rechazar las solicitudes enviadas con el nivel de aprobación que corresponde a su importe **para** controlar el gasto
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado una solicitud enviada con importe 800
Cuando el proceso calcula el nivel de aprobación
Entonces el nivel es "RESPONSABLE" y el gateway "¿Nivel?" continúa por la rama pv!nivelAprobacion = "RESPONSABLE" hacia la tarea "Aprobar o rechazar"

Dado una solicitud enviada con importe 5000
Cuando el proceso calcula el nivel de aprobación
Entonces el nivel es "DIRECTOR"

Dado una solicitud enviada con importe 20000
Cuando el proceso calcula el nivel de aprobación
Entonces el nivel es "COMITE"

Dado la tarea "Aprobar o rechazar" asignada al grupo DEMO_GRP_Aprobadores
Cuando el aprobador la completa aprobando
Entonces el estado de la solicitud pasa a "APROBADO" y la solicitud se envía al ERP
```
**Objetos que la implementan hoy**: `DEMO_PM_AprobarSolicitud` (processModel), `DEMO_DEC_NivelAprobacion` (decision), `DEMO_GRP_Aprobadores` (group), `DEMO_IFC_SolicitudForm` (interface, formulario de la tarea), `DEMO_INT_EnviarERP` (integration), `DEMO_CS_ERP` (connectedSystem), `DEMO_CONS_ESTADOS` (constant, dominio del campo estado) · **Prioridad de reconstrucción**: MVP
**Evidencia de los criterios**: filas de `content/DEMO_DEC_NivelAprobacion.xml#rows` (`importe <= 1000 → RESPONSABLE`, `importe > 1000 y importe <= 10000 → DIRECTOR`, `importe > 10000 → COMITE`); gateway n2 con condición `pv!nivelAprobacion = "RESPONSABLE"`, asignación n3 `assignees: DEMO_GRP_Aprobadores`, script n4 `pv!solicitud.estado: "APROBADO"` y nodo n5 `integrationRef: DEMO_INT_EnviarERP` en `processModel/DEMO_PM_AprobarSolicitud.xml#nodes`; "APROBADO" pertenece al dominio `BORRADOR;ENVIADO;APROBADO;RECHAZADO` de `content/DEMO_CONS_ESTADOS.xml#value`.

> ❓ **Pendiente de validación**: el gateway "¿Nivel?" solo tiene flujo saliente hacia la tarea (rama `RESPONSABLE`); el export no evidencia flujo alternativo para `DIRECTOR`/`COMITE` ni el camino de rechazo con estado `RECHAZADO`. No se han inventado criterios para esos caminos.

---

## Épica EP-02 — Consulta y seguimiento (CU-02)

### HU-004: Consultar solicitudes filtradas por estado
**Como** gestor **quiero** ver el listado de solicitudes filtrado por estado **para** hacer seguimiento de su tramitación
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado solicitudes existentes y el filtro de estado con valor "ENVIADO"
Cuando abro el listado
Entonces la grid muestra solo solicitudes con estado ENVIADO, con columnas Solicitante, Importe y Estado

Dado el filtro de estado vacío
Cuando abro el listado
Entonces la consulta no aplica el filtro y la grid muestra todas las solicitudes paginadas de 20 en 20
```
**Objetos que la implementan hoy**: `DEMO_IFC_SolicitudList` (interface), `DEMO_QR_GetSolicitudes` (expressionRule), `DEMO Solicitud` (recordType), `DEMO_DS_Principal` (dataStore, persistencia de la entidad consultada) · **Prioridad de reconstrucción**: fase 2
**Evidencia de los criterios**: `a!queryFilter(field: ...estado, operator: "=", value: ri!estado, applyWhen: a!isNotNullOrEmpty(ri!estado))` en `content/DEMO_QR_GetSolicitudes.xml#definition`; columnas Solicitante/Importe/Estado y `pageSize: 20` en `content/DEMO_IFC_SolicitudList.xml#definition`.

### HU-005: Consultar el estado por API
**Como** sistema externo **quiero** consultar el estado de una solicitud vía HTTP **para** integrar el seguimiento sin acceder a Appian
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado una solicitud existente
Cuando llamo por GET al endpoint solicitudes/estado
Entonces la API devuelve el resultado de consultar las solicitudes con rule!DEMO_QR_GetSolicitudes

Dado el parámetro estado informado en la llamada
Cuando la API ejecuta la consulta
Entonces el filtro por estado se aplica sobre el campo estado del record DEMO Solicitud
```
**Objetos que la implementan hoy**: `DEMO_WS_ConsultaEstado` (webApi), `DEMO_QR_GetSolicitudes` (expressionRule) · **Prioridad de reconstrucción**: opcional
**Evidencia de los criterios**: `httpMethod: GET`, `endpointPath: solicitudes/estado` y descripción "Llama a rule!DEMO_QR_GetSolicitudes" en `content/DEMO_WS_ConsultaEstado.xml`; filtro condicional por estado en `content/DEMO_QR_GetSolicitudes.xml#definition`.
