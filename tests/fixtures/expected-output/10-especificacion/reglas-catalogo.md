<!--
  Salida esperada (verificación en seco) del agente agents/logic-spec-writer.md
  aplicado al fixture tests/fixtures/mini-export.
  Datos 100% sintéticos (DEMO_*, UUIDs 00000000-*).
-->

# Catálogo de reglas: DEMO App Solicitudes

> Una ficha por CADA expression rule y CADA decision del inventario. Sin filtro de callers.

Cobertura: 3/3 reglas (2 expression rules + 1 decision) y 3/3 constantes de `inventory.json`.

## Expression rules

### rule!DEMO_QR_GetSolicitudes

**Firma**: `estado: Text (opcional)` → `List of DEMO Solicitud` 🔵 inferido del SAIL (`a!queryRecordType(…).data`) · **Callers**: DEMO_IFC_SolicitudList (interface), DEMO_WS_ConsultaEstado (webApi) · **Evidencia**: `content/DEMO_QR_GetSolicitudes.xml#definition`
**Lógica (explicada)**: Consulta el record type DEMO Solicitud y devuelve sus filas; si se aporta `ri!estado`, filtra por igualdad sobre el campo `estado`; si no, devuelve todas (hasta el tope de paginación).
**Predicado/algoritmo (exacto)**:

```sail
/* urn:appian:record-type:v1:00000000-0000-0000-0000-000000000011 */
a!queryRecordType(
  recordType: 'recordType!{00000000-0000-0000-0000-000000000011}DEMO Solicitud',
  fields: { 'recordType!{00000000-0000-0000-0000-000000000011}DEMO Solicitud.fields.{00000000-0000-0000-0000-000000000021}solicitante' },
  filters: a!queryFilter(
    field: 'recordType!{00000000-0000-0000-0000-000000000011}DEMO Solicitud.fields.{00000000-0000-0000-0000-000000000024}estado',
    operator: "=",
    value: ri!estado,
    applyWhen: a!isNotNullOrEmpty(ri!estado)
  ),
  pagingInfo: a!pagingInfo(startIndex: 1, batchSize: 100)
).data
```

**Casos límite observables**: `ri!estado` nulo o vacío → el filtro no se aplica (`applyWhen: a!isNotNullOrEmpty(ri!estado)`) y se devuelven todas las solicitudes; tope de 100 filas por `batchSize: 100` (la fila 101 no se devuelve).

### rule!DEMO_VAL_ValidarImporte

**Firma**: `importe: Number (Decimal) (obligatorio)` → `Text | null` 🔵 inferido del SAIL (mensaje de error o `null` si es válido) · **Callers**: DEMO_IFC_SolicitudForm (interface) — 1 solo caller; la ficha existe igualmente (el filtro ">3 callers" está derogado en Nivel 3) · **Evidencia**: `content/DEMO_VAL_ValidarImporte.xml#definition`
**Lógica (explicada)**: Valida el importe con tres comprobaciones en cascada — obligatorio, mayor que cero y no superior a 100.000 — y devuelve el primer mensaje de error aplicable, o `null` si el importe es válido.
**Predicado/algoritmo (exacto)**:

```sail
if(
  a!isNullOrEmpty(ri!importe),
  "El importe es obligatorio",
  if(
    ri!importe <= 0,
    "El importe debe ser mayor que cero",
    if(ri!importe > 100000, "El importe supera el maximo permitido (100.000)", null)
  )
)
```

**Casos límite observables**: `null`/vacío → "El importe es obligatorio"; `importe <= 0` (incluye el 0 exacto y negativos) → "El importe debe ser mayor que cero"; `importe > 100000` → "El importe supera el maximo permitido (100.000)"; `100000` exacto es válido (comparación estricta `>`); valor válido → `null`.

## Decisions

### decision!DEMO_DEC_NivelAprobacion

**Firma**: `importe: Number (Decimal)` → `nivel: Text` · **Callers**: DEMO_PM_AprobarSolicitud (processModel, nodo n1 "Calcular nivel de aprobacion") · **Evidencia**: `content/DEMO_DEC_NivelAprobacion.xml#rows`
**Lógica (explicada)**: Asigna el nivel de aprobación requerido según el tramo del importe: hasta 1.000 lo aprueba el responsable, hasta 10.000 el director y por encima el comité.
**Tabla de decisión (completa — TODAS las filas condición→resultado)**:

| # | Condiciones (inputs) | Resultado |
|---|---|---|
| 1 | `importe <= 1000` | `RESPONSABLE` |
| 2 | `importe > 1000 y importe <= 10000` | `DIRECTOR` |
| 3 | `importe > 10000` | `COMITE` |

**Casos límite observables**: los tres tramos son contiguos y sin solapamientos (fronteras exactas: 1000 → RESPONSABLE, 10000 → DIRECTOR); no hay fila default declarada; 🟡 comportamiento con `importe` nulo no evidenciado en el export — pendiente de validación funcional.

---

## Constantes

### cons!DEMO_CONS_ESTADOS
**Tipo**: Text · **Callers**: ninguno — huérfana en `graph.json` (🟡, ver nota) · **Evidencia**: `content/DEMO_CONS_ESTADOS.xml#value`
**Valor**: `BORRADOR;ENVIADO;APROBADO;RECHAZADO`
**Para qué sirve**: dominio cerrado del campo `estado` de una solicitud. Es la fuente de verdad de los cuatro estados del ciclo de vida.
**Nota de reconstrucción**: los valores viajan separados por `;` en una sola constant de tipo Text (no es una lista tipada). Ver la máquina de estados completa en [estados.md](estados.md).
**🟡 Pendiente de validación**: ningún objeto del export la referencia — el gateway del PM compara contra el literal `"RESPONSABLE"` y el script escribe `"APROBADO"` a pelo, sin pasar por la constant. **No se descarta**: el dominio que declara coincide con el campo `estado` del record type y con los literales escritos en el proceso, así que o la usa un objeto no exportado o la app tiene los estados duplicados en literales (deuda técnica a confirmar con el equipo). Responsable sugerido: técnico Appian.

### cons!DEMO_CONS_GRP_APROBADORES
**Tipo**: Group · **Callers**: `DEMO_PM_ReintentarEnvios` (gateway `b2`, `a!isUserMemberOfGroup`) · **Evidencia**: `content/DEMO_CONS_GRP_APROBADORES.xml#value`
**Valor**: `DEMO_GRP_Aprobadores`
**Para qué sirve**: es la referencia al grupo de aprobadores desde SAIL. En Appian no existe literal `group!X`, así que un grupo solo se puede nombrar en una expresión a través de una constante como esta.
**Nota de reconstrucción**: al reconstruir hay que crear **primero** el grupo y **después** la constante que lo apunta; si se invierte el orden la constante queda sin valor y el gateway del batch evalúa siempre a falso (nadie pasa el control de autorización) sin dar error.

### cons!DEMO_CONS_ENTITY_SOLICITUD
**Tipo**: Data Store Entity · **Callers**: `DEMO_PM_ReintentarEnvios` (nodos `b1` queryEntity y `b4` writeToDataStoreEntity) · **Evidencia**: `content/DEMO_CONS_ENTITY_SOLICITUD.xml#value`
**Valor**: `DEMO_DS_Principal.solicitud`
**Para qué sirve**: apunta a la entidad `solicitud` del data store principal, mapeada al CDT `DEMO_CDT_Solicitud` (tabla `DEMO_SOLICITUD`).
**Nota de reconstrucción**: el batch accede a los datos por **data store entity**, no por record type — al reconstruir hay que decidir si se unifica todo en Data Fabric o se mantiene el acceso por entidad.
