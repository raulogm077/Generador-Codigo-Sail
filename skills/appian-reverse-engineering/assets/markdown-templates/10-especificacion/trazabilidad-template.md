<!--
  Plantilla Nivel 3 — Matriz de trazabilidad bidireccional
  La rellena el agente backlog-writer a partir de inventory.json + 01-funcional.md +
  backlog.md + las fichas de 10-especificacion/.
  Salida: 10-especificacion/trazabilidad.md
  Es la matriz que check_coverage.py --mode rebuild verifica (exit 0 obligatorio).

  REGLAS:
  - Una fila por CADA objeto del inventory.json, sin excepciones.
  - Estado admite EXACTAMENTE dos valores: DOCUMENTADO | DESCARTADO: {motivo} — nada más.
  - El {motivo} de un DESCARTADO cita su Evidencia: {ruta}#{fragmento}
    (p. ej. objeto muerto: 0 callers en graph.json y sin trigger propio).
  - Celda sin correspondencia (p. ej. objeto técnico sin caso de uso) = "—", nunca vacía.
-->

# Matriz de trazabilidad: {{aplicación}}

| Objeto (tipo) | Caso de uso (01-funcional) | Historias (HU-nnn) | Pantalla/Regla/Estado spec | Estado |
|---|---|---|---|---|
| `{{DEMO_Objeto}}` ({{tipo}}) | {{CU-nn o —}} | {{HU-nnn, HU-nnn o —}} | {{ficha en 10-especificacion/ o —}} | DOCUMENTADO |
{{una fila por CADA objeto del inventory.json; Estado ∈ DOCUMENTADO | DESCARTADO: {motivo} — nada más}}

**Cobertura**: {{X}}/{{X}} objetos (100%)
