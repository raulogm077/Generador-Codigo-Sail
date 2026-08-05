<!--
  Plantilla Nivel 3 — Catálogo de reglas (expression rules + decisions)
  La rellena el agente logic-spec-writer a partir de detail.json + graph.json.
  Salida: 10-especificacion/reglas-catalogo.md

  REGLAS:
  - TODAS las expression rules, decisions y constants del inventario, SIN filtro de
    callers: este nivel deroga explícitamente la regla ">3 callers" de
    09-valor-adicional.md (una regla con 1 solo caller también tiene su ficha).
  - El SAIL crudo SÍ se cita en Nivel 3, enmascarado si contiene secretos (security-rules.md).
  - Toda ficha lleva Evidencia: {ruta}#{fragmento}. Sección sin contenido = "N/A — {motivo}".
  - NIVELES: `##` para las tres secciones contenedoras, `###` para cada ficha.
    El gate (check_coverage.py) reconoce la ficha por el PREFIJO TIPADO de su
    cabecera — `rule!`, `decision!`, `cons!` — a cualquier nivel de `#`. Sin ese
    prefijo NO cuenta como ficha: `### DEMO_VAL_Importe` o "## Constantes usadas:
    DEMO_CONS_X" son menciones, y el objeto seguirá saliendo en `missing`.
-->

# Catálogo de reglas: {{aplicación}}

> Una ficha por CADA expression rule, CADA decision y CADA constant del inventario. Sin filtro de callers.

## Expression rules

### rule!{{nombre}}
**Firma**: {{inputs con tipo}} → {{output}} · **Callers**: {{lista}} · **Evidencia**: {{ruta}}
**Lógica (explicada)**: {{prosa breve}}
**Predicado/algoritmo (exacto)**:
```sail
{{SAIL relevante, enmascarado si contiene secretos}}
```
**Casos límite observables**: {{null-handling, listas vacías, defaults}}

## Decisions

### decision!{{nombre}}
**Firma**: {{inputs con tipo}} → {{output}} · **Callers**: {{lista}} · **Evidencia**: {{ruta}}
**Lógica (explicada)**: {{prosa breve}}
**Tabla de decisión (completa — TODAS las filas condición→resultado)**:

| # | Condiciones (inputs) | Resultado |
|---|---|---|
| 1 | {{condición fila 1}} | {{resultado fila 1}} |
| 2 | {{condición fila 2}} | {{resultado fila 2}} |
| {{n}} | {{…las N filas reales, ninguna resumida}} | {{…}} |

**Casos límite observables**: {{fila default / valores fuera de rango / null-handling}}

## Constantes

> Una ficha por CADA constant del inventario. Para reconstruir hace falta el **valor**,
> no solo saber que existe: una constant suele ser un dominio de estados, un umbral de
> negocio, una entidad de data store o un endpoint por entorno.

### cons!{{nombre}}
**Tipo**: {{typeRef}} · **Callers**: {{lista desde graph.json}} · **Evidencia**: {{ruta}}
**Valor**: `{{valor real, o 🔒 Enmascarado si es un secreto}}`
**Para qué sirve**: {{qué representa en el negocio}}
**Nota de reconstrucción**: {{si es un dominio de valores → enlace a estados.md; si es
una entidad de data store → qué tabla; si varía por entorno → márcalo y remite al ICF}}
