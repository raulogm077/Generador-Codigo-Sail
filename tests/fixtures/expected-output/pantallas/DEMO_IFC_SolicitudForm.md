<!-- Referencia esperada (verificación en seco del agente interface-spec-writer sobre tests/fixtures/mini-export) -->

# Pantalla: Nueva solicitud (`DEMO_IFC_SolicitudForm`)
**Tipo**: formulario
**Usada desde**: `DEMO_PM_AprobarSolicitud` (formulario de arranque, nodo «Inicio», y formulario de la user task «Aprobar o rechazar» — `processModel/DEMO_PM_AprobarSolicitud.xml#n0,n3`) · `DEMO_RT_Solicitud` (vista «Resumen» — `recordType/DEMO_RT_Solicitud.xml#view-Resumen`). Sin aristas entrantes en `graph.json` (callers localizados por fallback sobre el export). · **Evidencia**: `content/DEMO_IFC_SolicitudForm.xml`

## Entradas (rule inputs)

| ri! | Tipo | Obligatorio | Origen del valor |
|---|---|---|---|
| `ri!solicitante` | Text | sí | formularios del PM `DEMO_PM_AprobarSolicitud` (mapeo de inputs no declarado en el export) |
| `ri!importe` | Number (Decimal) | sí | formularios del PM `DEMO_PM_AprobarSolicitud` (mapeo de inputs no declarado en el export) |
| `ri!justificacion` | Text | no | formularios del PM `DEMO_PM_AprobarSolicitud` (mapeo de inputs no declarado en el export) |
| `ri!modo` | Text | no | 🟡 no usada en el SAIL de la interfaz — declarada pero sin referencia; candidata a limpieza |

## Variables locales relevantes

| local! | Se inicializa con | Para qué sirve |
|---|---|---|
| `local!erroresImporte` | `rule!DEMO_VAL_ValidarImporte(ri!importe)` | Mensajes de validación del campo Importe (se pasa a `validations:` del componente) |
| `local!listado` | `rule!DEMO_IFC_SolicitudList()` | 🟡 se inicializa pero NO se referencia en el layout — evalúa el listado embebido sin mostrarlo; candidata a limpieza. Evidencia: `content/DEMO_IFC_SolicitudForm.xml#local!listado` |

## Componentes (en orden de aparición, TODOS)

| # | Componente | Etiqueta | Campo/dato origen | Obligatorio | Validaciones (predicado EXACTO) | Visible/editable cuando (predicado) | Al cambiar/guardar (saveInto → efecto) |
|---|---|---|---|---|---|---|---|
| 1 | `a!textField` | Solicitante | `ri!solicitante` | sí (`required: true`) | — | siempre | `ri!solicitante` → actualiza el rule input |
| 2 | `a!floatingPointField` | Importe | `ri!importe` | sí (`required: true`) | `validations: local!erroresImporte` (= `rule!DEMO_VAL_ValidarImporte(ri!importe)`) | siempre | `ri!importe` → actualiza el rule input; re-evalúa validación y visibilidad de Justificacion |
| 3 | `a!paragraphField` | Justificacion | `ri!justificacion` | condicional: `required: ri!importe > 1000` | — | `showWhen: ri!importe > 1000` (visible solo si el importe supera 1000) | `ri!justificacion` → actualiza el rule input |
| 4 | `a!textField` | Registro | `recordType!{00000000-0000-0000-0000-000000000011}DEMO Solicitud` | no | — | `showWhen: false` (oculto fijo) · `readOnly: true` | — (solo lectura, sin saveInto) |

Decorativos: 0 (la pantalla no tiene líneas, espaciadores ni imágenes estáticas).

## Acciones (botones/links)

| Acción | Estilo | Habilitada cuando | Qué hace (submit/proceso/navegación) | Validaciones que dispara |
|---|---|---|---|---|
| Enviar | `SOLID` (primario) | siempre | `submit: true` — envía el formulario (en el PM: completa el start form o la user task «Aprobar o rechazar») | `validate: true` → `required` de Solicitante e Importe, `required` condicional de Justificacion y `local!erroresImporte` |

## Reglas invocadas

| rule! | Para qué | → ficha en reglas-catalogo |
|---|---|---|
| `rule!DEMO_VAL_ValidarImporte` | Devuelve el mensaje de error del importe (obligatorio / > 0 / máximo 100.000) que alimenta `validations:` del campo Importe | [reglas-catalogo.md](../reglas-catalogo.md#ruledemo_val_validarimporte) |
| `rule!DEMO_IFC_SolicitudList` | Es una interfaz, no una expression rule: listado embebido evaluado en `local!listado` (no mostrado en el layout) | ficha de pantalla: [DEMO_IFC_SolicitudList.md](DEMO_IFC_SolicitudList.md) |

## Estados de la pantalla

N/A — ningún predicado de la pantalla depende del estado del registro (`estado`): la visibilidad y obligatoriedad dependen solo de `ri!importe`.

| Estado del registro | Qué se ve / qué cambia |
|---|---|
| — | N/A |

## Criterios de reconstrucción (verificables)

- [ ] Con importe > 1000 el campo Justificación es visible y obligatorio; con importe ≤ 1000 está oculto y no es obligatorio (predicado: `ri!importe > 1000` en `showWhen` y `required`).
- [ ] Con importe vacío el campo Importe muestra "El importe es obligatorio"; con importe ≤ 0, "El importe debe ser mayor que cero"; con importe > 100000, "El importe supera el maximo permitido (100.000)" (evidencia: `content/DEMO_VAL_ValidarImporte.xml#definition`).
- [ ] El botón Enviar es el único botón, primario (`SOLID`), hace submit y bloquea el envío mientras haya validaciones incumplidas (`validate: true`).
- [ ] El campo Registro nunca es visible (`showWhen: false`) y es de solo lectura.
- [ ] Solicitante e Importe son siempre obligatorios (`required: true`).
