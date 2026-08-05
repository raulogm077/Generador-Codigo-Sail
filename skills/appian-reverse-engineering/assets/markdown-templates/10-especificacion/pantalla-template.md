<!--
  Plantilla Nivel 3 — Ficha de pantalla (una por CADA interfaz del inventory.json)
  La rellena el agente interface-spec-writer a partir de detail.json + graph.json.
  Salida: 10-especificacion/pantallas/{interfaz}.md

  REGLAS (opuestas a las de onboarding 00-09):
  - Aquí la jerga SAIL es OBLIGATORIA, no prohibida: los predicados (showWhen, required,
    validations) se copian EXACTOS del SAIL y después se explican en una frase.
  - Cobertura de componentes 100%: se recorre el árbol SAIL completo. Los componentes
    puramente decorativos (línea, espaciador) se agrupan en una única fila "decorativos: N".
  - TODAS las secciones son obligatorias: sección sin contenido = "N/A — {motivo}" explícito,
    nunca omitida ni dejada vacía.
  - Toda afirmación lleva Evidencia: {ruta}#{fragmento}. Cero invención.
  - Si una parte no se pudo analizar (p. ej. interfaz >100KB troceada): sección
    "NO ANALIZADO: {qué y por qué}" — nunca truncar en silencio.
-->

# Pantalla: {{nombre_visible}} (`{{nombre_tecnico}}`)
**Tipo**: formulario | listado | dashboard | wizard | componente reutilizable
**Usada desde**: {{callers desde graph.json}} · **Evidencia**: {{ruta_xml}}

## Entradas (rule inputs)

| ri! | Tipo | Obligatorio | Origen del valor |
|---|---|---|---|
| `ri!{{nombre}}` | {{tipo}} | {{sí/no}} | {{quién lo pasa: caller/proceso/record action}} |

## Variables locales relevantes

| local! | Se inicializa con | Para qué sirve |
|---|---|---|
| `local!{{nombre}}` | {{expresión inicial}} | {{propósito}} |

## Componentes (en orden de aparición, TODOS)

| # | Componente | Etiqueta | Campo/dato origen | Obligatorio | Validaciones (predicado EXACTO) | Visible/editable cuando (predicado) | Al cambiar/guardar (saveInto → efecto) |
|---|---|---|---|---|---|---|---|
| 1 | {{a!textField}} | {{Solicitante}} | {{ri!solicitante}} | {{sí/no}} | {{predicado SAIL exacto o —}} | {{predicado SAIL exacto o siempre}} | {{ri!solicitante → efecto}} |

## Acciones (botones/links)

| Acción | Estilo | Habilitada cuando | Qué hace (submit/proceso/navegación) | Validaciones que dispara |
|---|---|---|---|---|
| {{Enviar}} | {{PRIMARY}} | {{predicado o siempre}} | {{submit / arranca PM / navega a}} | {{lista o —}} |

## Reglas invocadas

| rule! | Para qué | → ficha en reglas-catalogo |
|---|---|---|
| `rule!{{DEMO_VAL_Ejemplo}}` | {{qué aporta a esta pantalla}} | [reglas-catalogo.md](../reglas-catalogo.md#rule{{nombre_anchor}}) |

## Estados de la pantalla

{{si la pantalla rinde distinto según estado del registro: tabla estado → qué se ve}}

| Estado del registro | Qué se ve / qué cambia |
|---|---|
| {{ESTADO}} | {{diferencias: campos ocultos, solo lectura, acciones deshabilitadas}} |

## Criterios de reconstrucción (verificables)

- [ ] {{ej: con importe > 1000 el campo Justificación es visible y obligatorio}}
- [ ] {{cada criterio debe poder comprobarse contra la app reconstruida sin abrir el export}}
