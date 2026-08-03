<!--
  Plantilla 07 — Procesos batch / recurrentes
  Process models con start event temporal o recurrente.
  Frecuencia humana + cron + próximas N ejecuciones si calculable.
-->

# Procesos batch / recurrentes

> Process models que se disparan solos por temporizador o recurrencia, sin intervención humana.

> Si el export no contiene ningún process model con start event temporal, este documento debe contener exactamente: "No se han detectado procesos recurrentes en el export." y omitir el resto de secciones.

## Resumen

| Process Model | Frecuencia humana | Cron equivalente | Próxima ejecución | Volumetría estimada |
|---|---|---|---|---|
| `{{pm_batch_1}}` | {{Cada lunes a las 08:00}} | `0 8 * * 1` | {{ISO_date}} | {{filas/llamadas estimadas}} |
| `{{pm_batch_2}}` | {{Cada hora en horario laboral}} | `0 9-18 * * 1-5` | {{ISO_date}} | {{}} |

## Detalle por batch

### `{{pm_NombreTecnico_1}}` — {{nombre_visible}}

| Campo | Valor |
|---|---|
| Propósito funcional | {{para qué se ejecuta este batch}} |
| Trigger | Timer Start Event |
| Frecuencia (lenguaje humano) | {{traducción de `<recurrence>` a algo legible}} |
| Cron equivalente | `{{cron}}` o "No traducible directamente a cron — `{{razón}}`" |
| Próximas 3 ejecuciones | {{Si se puede calcular: lista. Si no: "No determinable desde el export."}} |
| Owner / responsable | {{grupo o "no determinado"}} |
| Estado | ✅/🔵 — Evidencia: `{{ruta_xml}}#start-node` |

**Qué hace (paso a paso funcional)**

1. {{paso 1}}
2. {{paso 2}}
3. {{paso 3}}

**Procesos hijos que dispara**

| Subproceso | Asíncrono / síncrono | Notas |
|---|---|---|
| `{{PM_hijo_1}}` | sync | {{notas}} |
| `{{PM_hijo_2}}` | async | {{notas}} |

**Data stores / integraciones que toca**

| Objeto | Operación |
|---|---|
| `{{record/datastore}}` | lectura / escritura |
| `{{integration}}` | llamada saliente |

**Volumetría esperada (inferida)**

{{Si el process model tiene `a!queryEntity` con `pagingInfo`, indicar el tamaño de batch.
Si no hay paginación visible, marcar como 🟡 riesgo y derivar a `09-valor-adicional.md`.}}

| Indicador | Valor | Fuente |
|---|---|---|
| Batch size | `{{N}}` | `{{ruta}}#nodo` |
| Paginación | Sí / No | `{{ruta}}` |
| Filtro de fecha | Sí ({{campo}}) / No | `{{ruta}}` |

**Manejo de errores**

- {{exception flow detectado / alert / retry}} — {{evidencia}}
- {{Si no hay manejo, marcar como 🔴 y mover a `09-valor-adicional.md`.}}

> Estado: ✅/🔵/🟡 — Evidencia: `{{ruta_xml}}`

---

### `{{pm_NombreTecnico_2}}`

{{Repetir.}}

## Hallazgos

- 🔴 **Batches que llaman a `a!queryEntity` sin paginación**: {{lista}}.
- 🔴 **Batches sin manejo de errores explícito**: {{lista}}.
- 🟡 **Batches con frecuencia muy alta** (intra-horaria) que podrían saturar BBDD o sistemas externos: {{lista}}.
- 🟡 **Batches cuya frecuencia no es traducible a cron** (p. ej. recurrencias con condiciones de calendario laboral): {{lista}}.
- 🟡 **Batches que usan `fn!loggedInUser()` o variables de contexto humano**: 🔴 anti-patrón. {{lista}}.

## Resumen rápido

- Total batches detectados: {{N}}
- Frecuencia diaria: {{N}} · semanal: {{N}} · mensual: {{N}} · ad-hoc: {{N}}
- Riesgos top: {{breve}}
