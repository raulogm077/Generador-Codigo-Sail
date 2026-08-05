<!-- Referencia esperada (verificación en seco del agente interface-spec-writer sobre tests/fixtures/mini-export) -->

# Pantalla: Solicitudes (`DEMO_IFC_SolicitudList`)
**Tipo**: listado (componente reutilizable: no tiene layout de página propio y se invoca con `rule!` desde otra interfaz)
**Usada desde**: `DEMO_IFC_SolicitudForm` (arista `ruleRef` en `graph.json`; evaluada en `local!listado` sin mostrarse en el layout del caller) · **Evidencia**: `content/DEMO_IFC_SolicitudList.xml`

## Entradas (rule inputs)

| ri! | Tipo | Obligatorio | Origen del valor |
|---|---|---|---|
| `ri!estadoFiltro` | Text | no | caller: `DEMO_IFC_SolicitudForm` la invoca sin argumentos (`rule!DEMO_IFC_SolicitudList()`) → llega null y el filtro de estado no se aplica |

## Variables locales relevantes

| local! | Se inicializa con | Para qué sirve |
|---|---|---|
| `local!solicitudes` | `rule!DEMO_QR_GetSolicitudes(estado: ri!estadoFiltro)` | Datos del grid: solicitudes filtradas por estado (si `ri!estadoFiltro` viene informado) |

## Componentes (en orden de aparición, TODOS)

| # | Componente | Etiqueta | Campo/dato origen | Obligatorio | Validaciones (predicado EXACTO) | Visible/editable cuando (predicado) | Al cambiar/guardar (saveInto → efecto) |
|---|---|---|---|---|---|---|---|
| 1 | `a!gridField` | Solicitudes | `data: local!solicitudes` · `pageSize: 20` | no | — | siempre | — (grid de solo lectura, sin selección ni saveInto) |
| 2 | `a!gridColumn` | Solicitante | `fv!row.solicitante` | — | — | siempre | — |
| 3 | `a!gridColumn` | Importe | `fv!row.importe` | — | — | siempre | — |
| 4 | `a!gridColumn` | Estado | `fv!row.estado` | — | — | siempre | — |

Decorativos: 0 (la pantalla no tiene líneas, espaciadores ni imágenes estáticas).

## Acciones (botones/links)

N/A — la pantalla no tiene botones ni links: es un listado de solo lectura sin acciones.

| Acción | Estilo | Habilitada cuando | Qué hace (submit/proceso/navegación) | Validaciones que dispara |
|---|---|---|---|---|
| — | — | — | N/A | — |

## Reglas invocadas

| rule! | Para qué | → ficha en reglas-catalogo |
|---|---|---|
| `rule!DEMO_QR_GetSolicitudes` | Consulta las solicitudes (query al record type `DEMO Solicitud`) con filtro opcional por estado; alimenta `local!solicitudes` | [reglas-catalogo.md](../reglas-catalogo.md#ruledemo_qr_getsolicitudes) |

## Estados de la pantalla

N/A — el render no cambia según el estado del registro: `estado` se usa solo como filtro de datos (`ri!estadoFiltro`) y como columna visible del grid.

| Estado del registro | Qué se ve / qué cambia |
|---|---|
| — | N/A |

## Criterios de reconstrucción (verificables)

- [ ] Con `estadoFiltro` nulo o vacío el grid muestra solicitudes de todos los estados; con `estadoFiltro` = "ENVIADO" solo las de estado ENVIADO (el filtro se aplica con `applyWhen: a!isNotNullOrEmpty(ri!estado)` en la query — evidencia: `content/DEMO_QR_GetSolicitudes.xml#definition`).
- [ ] El grid pagina de 20 en 20 (`pageSize: 20`).
- [ ] Las columnas son exactamente, y en este orden: Solicitante, Importe, Estado.
- [ ] El grid es de solo lectura: sin selección, sin edición inline y sin acciones por fila.
