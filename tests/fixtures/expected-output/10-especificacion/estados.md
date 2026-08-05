<!--
  Salida esperada (verificación en seco) del agente agents/logic-spec-writer.md
  aplicado al fixture tests/fixtures/mini-export.
  Datos 100% sintéticos (DEMO_*, UUIDs 00000000-*).
-->

# Máquina de estados: DEMO Solicitud

**Campo**: `DEMO Solicitud.estado` (Text, obligatorio; también en `DEMO_CDT_Solicitud.estado`) · **Dominio**: `BORRADOR | ENVIADO | APROBADO | RECHAZADO` — origen: constant `DEMO_CONS_ESTADOS` (✅ `content/DEMO_CONS_ESTADOS.xml#value`), confirmado por el campo `estado` del RT/CDT (`recordType/DEMO_RT_Solicitud.xml#fields`, `datatype/DEMO_CDT_Solicitud.xsd#estado`) y por la escritura literal `"APROBADO"` en el PM (`processModel/DEMO_PM_AprobarSolicitud.xml#n4`).

| Desde | Hasta | Disparador (pantalla/proceso/nodo) | Quién puede | Condición (predicado) | Evidencia |
|---|---|---|---|---|---|
| ENVIADO 🔵 | APROBADO | User task "Aprobar o rechazar" (n3) de `DEMO_PM_AprobarSolicitud`; la escritura la ejecuta el script "Marcar APROBADO" (n4) inmediatamente posterior: `pv!solicitud.estado: "APROBADO"` | DEMO_GRP_Aprobadores | Camino evidenciado tras el gateway "¿Nivel?" (n2): `pv!nivelAprobacion = "RESPONSABLE"` | `processModel/DEMO_PM_AprobarSolicitud.xml#n3-n4` |
| — | BORRADOR | 🟡 no identificado (ninguna escritura de `"BORRADOR"` localizada en PMs ni interfaces) | 🟡 | — | dominio: `content/DEMO_CONS_ESTADOS.xml#value` |
| — | ENVIADO | 🟡 no identificado (sin escritura de `"ENVIADO"` localizada). 🔵 Indicio parcial: el botón "Enviar" (submit) de `DEMO_IFC_SolicitudForm` y el arranque `userStart` con ese formulario en `DEMO_PM_AprobarSolicitud` (n0) sugieren el envío, pero la escritura no está en el export | 🟡 | — | dominio: `content/DEMO_CONS_ESTADOS.xml#value` · indicio: `content/DEMO_IFC_SolicitudForm.xml#buttonWidget-Enviar`, `processModel/DEMO_PM_AprobarSolicitud.xml#n0` |
| — | RECHAZADO | 🟡 no identificado (el user task se llama "Aprobar o rechazar", pero solo existe la escritura de `"APROBADO"`; no hay rama de rechazo en el export) | 🟡 | — | dominio: `content/DEMO_CONS_ESTADOS.xml#value` · `processModel/DEMO_PM_AprobarSolicitud.xml#n3` |

**Nota "Desde"**: `ENVIADO` como estado de partida de la aprobación es 🔵 inferido de la descripción del PM — "Aprueba o rechaza una solicitud enviada" (`processModel/DEMO_PM_AprobarSolicitud.xml#description`) — y del filtro por `estado` de `DEMO_QR_GetSolicitudes`; no hay gateway que compare `estado` literalmente.

Diagrama `stateDiagram-v2` omitido — `scripts/validate_mermaid.py` no soporta ese tipo (solo flowchart Tipo A/C y erDiagram Tipo B); la tabla es la fuente de verdad.

## Dominios auxiliares detectados

| Dominio | Valores | Dónde vive | Por qué no es máquina de estados |
|---|---|---|---|
| `nivelAprobacion` | `RESPONSABLE \| DIRECTOR \| COMITE` | PV `nivelAprobacion` de `DEMO_PM_AprobarSolicitud` (escrita en n1); output de `decision!DEMO_DEC_NivelAprobacion`; comparada en el gateway n2 | No persiste en ningún campo de RT/CDT (fuente 1 sin match): es un dato transitorio de enrutado del proceso. Evidencia: `processModel/DEMO_PM_AprobarSolicitud.xml#n1-n2`, `content/DEMO_DEC_NivelAprobacion.xml#rows` |
