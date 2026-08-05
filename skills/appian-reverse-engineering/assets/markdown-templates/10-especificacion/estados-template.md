<!--
  Plantilla Nivel 3 — Máquina de estados (una por entidad con ciclo de vida detectado)
  La rellena el agente logic-spec-writer cruzando 4 fuentes: campos estado|status|fase|stage,
  constants con listas de valores, gateways de PMs / showWhen de interfaces, y decisions
  cuyo output es uno de esos valores.
  Salida: 10-especificacion/estados.md (una máquina por entidad).

  REGLAS:
  - Cada transición lleva su Evidencia: {ruta}#{fragmento}. Cero invención.
  - Transición sin disparador identificado → fila con "Disparador: 🟡 no identificado",
    nunca omitida ni inventada.
  - Secciones obligatorias: sin contenido = "N/A — {motivo}" explícito.
-->

# Máquina de estados: {{entidad}}
**Campo**: {{rt.campo}} · **Dominio**: {{valores, con origen: constant/decision/gateway}}

| Desde | Hasta | Disparador (pantalla/proceso/nodo) | Quién puede | Condición (predicado) | Evidencia |
|---|---|---|---|---|---|
| {{ESTADO_A}} | {{ESTADO_B}} | {{pantalla / PM / nodo — o 🟡 no identificado}} | {{grupo/rol}} | {{predicado SAIL exacto o —}} | {{ruta}}#{{fragmento}} |

{{diagrama mermaid stateDiagram-v2 opcional — validar con validate_mermaid}}
