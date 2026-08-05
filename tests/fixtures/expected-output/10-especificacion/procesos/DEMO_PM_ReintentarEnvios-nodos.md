# DEMO_PM_ReintentarEnvios — detalle por nodo

> Batch nocturno. Complemento del BPMN de `08-procesos-bpmn/`. Los ids coinciden con los del `.bpmn`.
> **Evidencia**: `processModel/DEMO_PM_ReintentarEnvios.xml`

## Process variables

| PV | Tipo | ¿Parámetro? | Quién la escribe | Quién la lee |
|---|---|---|---|---|
| `pendientes` | `DEMO_CDT_Solicitud` | No | `b1` (query) | `b4` (escritura) |
| `reintentos` | Number (Integer) | No | — | — |

> 🟡 `reintentos` está declarada pero ningún nodo la lee ni la escribe: candidata a variable muerta. Al reconstruir, o se implementa el contador de reintentos o se elimina.

## Ficha por nodo (TODOS los nodos)

### b0 — Inicio programado (start)
- Tipo de arranque: `timer` · Recurrencia **exacta**: `FREQ=DAILY;BYHOUR=2;BYMINUTE=0` (diario a las 02:00).
- Ver también [../../07-batches.md](../../07-batches.md).

### b1 — Leer solicitudes pendientes (script)
- Expresión **exacta**:
  ```sail
  pv!pendientes: a!queryEntity(
    entity: cons!DEMO_CONS_ENTITY_SOLICITUD,
    query: a!query(
      filter: a!queryFilter(field: "estado", operator: "=", value: "APROBADO"),
      pagingInfo: a!pagingInfo(startIndex: 1, batchSize: 500)
    )
  ).data
  ```
- Accede por **data store entity**, no por record type → ver `cons!DEMO_CONS_ENTITY_SOLICITUD` en [../reglas-catalogo.md](../reglas-catalogo.md).
- 🔴 `batchSize: 500` fijo, sin bucle de paginación: si hay más de 500 pendientes, el resto no se reintenta nunca.

### b2 — ¿Ejecutor autorizado? (gateway)
- Condición **exacta**: `a!isUserMemberOfGroup(username: loggedInUser(), groups: cons!DEMO_GRP_Aprobadores)`
- 🔴 Un batch se ejecuta con el usuario diseñador, no con un usuario de negocio: comprobar pertenencia a grupo aquí es un antipatrón. Al reconstruir, revisar si la condición debe desaparecer.

### b3 — Reprocesar aprobación (subProcess)
- Subproceso: `DEMO_PM_AprobarSolicitud` (uuid `00000000-0000-0000-0000-000000000009`).
- Ficha del subproceso: [DEMO_PM_AprobarSolicitud-nodos.md](DEMO_PM_AprobarSolicitud-nodos.md)

### b4 — Guardar resultado del reintento (script)
- Expresión **exacta**:
  ```sail
  a!writeToDataStoreEntity(
    dataStoreEntity: cons!DEMO_CONS_ENTITY_SOLICITUD,
    valueToStore: pv!pendientes
  )
  ```
- Escribe el lote entero, sin filtrar por resultado del subproceso.

### b5 — Sincronizar registros (script)
- Expresión **exacta**: `a!writeRecords(records: 'recordType!{00000000-0000-0000-0000-000000000011}DEMO Solicitud'())`
- Convive con la escritura por entidad de `b4`: **dos vías de escritura sobre los mismos datos**. Decisión pendiente al reconstruir.

### b6 — Fin (end)
- Sin salidas.

## Criterios de reconstrucción (verificables)

- [ ] El batch arranca solo a las 02:00 diarias, sin intervención manual.
- [ ] Solo procesa solicitudes en estado `APROBADO`.
- [ ] Cada solicitud procesada pasa por el subproceso de aprobación antes de escribirse.
