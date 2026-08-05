<!--
  Plantilla Nivel 3 — Navegación (sites y sus páginas)
  La rellena el agente interface-spec-writer a partir de detail.json (sección `sites`)
  + graph.json. Salida: 10-especificacion/navegacion.md

  REGLAS:
  - Una ficha por CADA site del inventario. Sin este documento, la reconstrucción
    tendría todas las pantallas pero no sabría cómo se llega a ellas.
  - NIVELES: `#` título, `##` por site (el gate reconoce la ficha por su cabecera).
  - Toda ficha lleva Evidencia: {ruta}#{fragmento}. Sección sin contenido = "N/A — {motivo}".
-->

# Navegación: {{aplicación}}

> Una ficha por CADA site. Las páginas enlazan a la ficha de pantalla correspondiente
> (`pantallas/{interfaz}.md`) o al record type que listan.

## site!{{nombre}}

**URL stub**: `/{{urlStub}}` · **Visible para**: {{grupos}} · **Evidencia**: {{ruta}}

### Páginas (en orden de aparición, TODAS)

| # | Página | Tipo | Objeto destino | → ficha | Visible para |
|---|---|---|---|---|---|
| 1 | {{nombre}} | RECORD_LIST \| INTERFACE \| REPORT \| ACTION \| WEB_CONTENT | `{{objeto}}` | {{`pantallas/x.md` o el record type}} | {{grupo o «todos los del site»}} |

**Página de inicio**: {{cuál se abre por defecto, o 🟡 no determinado}}

### Criterios de reconstrucción (verificables)

- [ ] {{ej: un usuario del grupo Aprobadores entra en /demo-solicitudes y ve 2 páginas
      en este orden: Solicitudes, Nueva solicitud}}
- [ ] {{ej: la página Solicitudes muestra el listado del record type X con sus filtros
      por defecto}}
