<!--
  Salida esperada (verificación en seco) del agente backlog-writer sobre
  tests/fixtures/mini-export. Una fila por CADA objeto de inventory.json:
  el inventario real del fixture aplana a 19 objetos. CU-01/CU-02 corresponden a las épicas de backlog.md; en una
  ejecución real vendrían de 01-funcional.md.
-->

# Matriz de trazabilidad: DEMO App Solicitudes

| Objeto (tipo) | Caso de uso (01-funcional) | Historias (HU-nnn) | Pantalla/Regla/Estado spec | Estado |
|---|---|---|---|---|
| `DEMO App Solicitudes` (application) | — | — | — | DOCUMENTADO |
| `DEMO_IFC_SolicitudForm` (interface) | CU-01 | HU-001, HU-002, HU-003 | `pantallas/DEMO_IFC_SolicitudForm.md` | DOCUMENTADO |
| `DEMO_IFC_SolicitudList` (interface) | CU-02 | HU-004 | `pantallas/DEMO_IFC_SolicitudList.md` | DOCUMENTADO |
| `DEMO_QR_GetSolicitudes` (expressionRule) | CU-02 | HU-004, HU-005 | `reglas-catalogo.md` | DOCUMENTADO |
| `DEMO_VAL_ValidarImporte` (expressionRule) | CU-01 | HU-001 | `reglas-catalogo.md` | DOCUMENTADO |
| `DEMO_DEC_NivelAprobacion` (decision) | CU-01 | HU-003 | `reglas-catalogo.md` | DOCUMENTADO |
| `DEMO_CONS_ESTADOS` (constant) | CU-01, CU-02 | HU-003, HU-004 | `reglas-catalogo.md` + `estados.md` | DOCUMENTADO |
| `DEMO_INT_EnviarERP` (integration) | CU-01 | HU-003 | `procesos/DEMO_PM_AprobarSolicitud-nodos.md` | DOCUMENTADO |
| `DEMO_WS_ConsultaEstado` (webApi) | CU-02 | HU-005 | — | DOCUMENTADO |
| `DEMO_PM_AprobarSolicitud` (processModel) | CU-01 | HU-001, HU-003 | `procesos/DEMO_PM_AprobarSolicitud-nodos.md` | DOCUMENTADO |
| `DEMO Solicitud` (recordType) | CU-01, CU-02 | HU-001, HU-004 | `estados.md` | DOCUMENTADO |
| `DEMO_CDT_Solicitud` (cdt) | CU-01 | HU-001, HU-003 | — | DOCUMENTADO |
| `DEMO_DS_Principal` (dataStore) | — | HU-004 | — | DOCUMENTADO |
| `DEMO_GRP_Aprobadores` (group) | CU-01 | HU-003 | `estados.md` | DOCUMENTADO |
| `DEMO_CS_ERP` (connectedSystem) | CU-01 | HU-003 | — | DOCUMENTADO |
| `DEMO_CONS_ENTITY_SOLICITUD` (constant) | — | HU-006 | `reglas-catalogo.md` | DOCUMENTADO |
| `DEMO_PM_ReintentarEnvios` (processModel) | CU-03 | HU-006 | `procesos/DEMO_PM_ReintentarEnvios-nodos.md` | DOCUMENTADO |
| `DEMO_SITE_Solicitudes` (site) | CU-01, CU-02 | HU-002, HU-004 | `navegacion.md` | DOCUMENTADO |
| `DEMO_CONS_GRP_APROBADORES` (constant) | CU-01, CU-03 | HU-003, HU-006 | `reglas-catalogo.md` | DOCUMENTADO |

**Cobertura**: 19/19 objetos (100%)
