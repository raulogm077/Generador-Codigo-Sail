# DEMO_PM_AprobarSolicitud — detalle por nodo

> Complemento del BPMN de `08-procesos-bpmn/`. Los ids coinciden con los del `.bpmn`.
> **Evidencia**: `processModel/DEMO_PM_AprobarSolicitud.xml`

## Process variables

| PV | Tipo | ¿Parámetro? | Quién la escribe | Quién la lee |
|---|---|---|---|---|
| `solicitud` | `DEMO_CDT_Solicitud` | Sí (entrada) | el start form (`DEMO_IFC_SolicitudForm`) | `n1`, `n4`, `n5` |
| `nivelAprobacion` | Text | No | `n1` (script) | `n2` (gateway) |
| `resultado` | Text | No | `n3` (tarea de usuario) | — (fin) |

## Ficha por nodo (TODOS los nodos)

### n0 — Inicio (start)
- Tipo de arranque: `userStart` — lo lanza una persona desde el site.
- Formulario: `DEMO_IFC_SolicitudForm` → ficha en [../pantallas/DEMO_IFC_SolicitudForm.md](../pantallas/DEMO_IFC_SolicitudForm.md)
- Salidas: `pv!solicitud` con los datos del formulario.

### n1 — Calcular nivel de aprobación (script)
- Entradas: `pv!solicitud.importe`
- Expresión **exacta**: `pv!nivelAprobacion: rule!DEMO_DEC_NivelAprobacion(importe: pv!solicitud.importe)`
- Salidas: `pv!nivelAprobacion` ∈ {RESPONSABLE, DIRECTOR, COMITE} → ver [../reglas-catalogo.md](../reglas-catalogo.md)

### n2 — ¿Nivel? (gateway)
- Condición **exacta**: `pv!nivelAprobacion = "RESPONSABLE"`
- 🟡 El export solo declara una condición: la rama alternativa (DIRECTOR/COMITE) no está modelada como flujo separado. Al reconstruir hay que decidir si se añaden ramas por nivel.

### n3 — Aprobar o rechazar (userInput)
- Asignado a: `DEMO_GRP_Aprobadores`
- Formulario: `DEMO_IFC_SolicitudForm`
- Salidas: `pv!resultado`
- 🟡 Sin SLA ni escalado declarados en el export.

### n4 — Marcar APROBADO (script)
- Expresión **exacta**: `pv!solicitud.estado: "APROBADO"`
- Transición de estado: `ENVIADO → APROBADO` → ver [../estados.md](../estados.md)

### n5 — Enviar al ERP (integration)
- Integración: `DEMO_INT_EnviarERP` (POST a `https://erp.example.local/api/solicitudes`)
- 🔴 Sin manejo de error declarado: si la integración falla, el proceso continúa a `n6`. El batch `DEMO_PM_ReintentarEnvios` existe precisamente para compensarlo.

### n6 — Fin (end)
- Sin salidas.

## Criterios de reconstrucción (verificables)

- [ ] Con importe ≤ 1000, `nivelAprobacion` vale `RESPONSABLE` y el gateway toma la rama declarada.
- [ ] La tarea de aprobación solo la ve un miembro de `DEMO_GRP_Aprobadores`.
- [ ] Al aprobar, el estado pasa a `APROBADO` **antes** de llamar al ERP.
