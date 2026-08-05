<!--
  Plantilla Nivel 3 — Detalle por nodo de un process model (complemento del BPMN)
  La rellena process-modeler en modo rebuild a partir de detail.json.
  Salida: 10-especificacion/procesos/{PM}-nodos.md (una por PM).
  Complementa a 08-procesos-bpmn/{PM}.md: mismo id de nodo que el BPMN.

  REGLAS:
  - TODOS los nodos del PM tienen ficha (nº de fichas == nº de nodos del BPMN).
  - Las expresiones (script tasks, condiciones de gateway) se copian EXACTAS del XML.
  - Toda ficha lleva Evidencia: {ruta}#{fragmento}. Cero invención.
  - Secciones obligatorias: sin contenido = "N/A — {motivo}" explícito.
-->

# {{PM}} — detalle por nodo

## Process variables

| PV | Tipo | ¿Parámetro? | Quién la escribe | Quién la lee |
|---|---|---|---|---|
| `{{pv}}` | {{tipo}} | {{sí/no}} | {{nodo(s) o start form}} | {{nodo(s)/gateway(s)}} |

## Ficha por nodo (TODOS los nodos, mismo id que el BPMN)

### {{nodo_id}} — {{nombre}} ({{tipo}})
- Entradas: {{ac!/pv! → origen}} · Salidas: {{→ pv!}}
- Configuración relevante: {{asignación, escalation/SLA, formulario (→ ficha de pantalla), expresión del script task EXACTA}}
- Evidencia: {{ruta_xml}}#{{nodo_id}}
