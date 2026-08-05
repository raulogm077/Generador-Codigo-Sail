<!--
  Plantilla Nivel 3 — Historia de usuario (bloque repetible dentro de backlog.md)
  La rellena el agente backlog-writer a partir de 01-funcional.md, las fichas de pantalla,
  el catálogo de reglas y estados.md. backlog.md agrupa las historias por épicas.
  Formato Gherkin compatible con el del agente appian-functional-analyst (Dado/Cuando/Entonces),
  para que ambos backlogs sean intercambiables.

  REGLAS:
  - Los Given/When/Then se derivan de artefactos REALES (validaciones de pantalla,
    transiciones de estado, gateways) — nunca inventados. Cada criterio cita su Evidencia.
  - ≥2 criterios de aceptación por historia.
  - Cada historia lista los objetos que la implementan hoy.
  - Prioridad MVP = camino feliz de los casos de uso principales.
-->

### HU-{{nnn}}: {{título}}
**Como** {{actor}} **quiero** {{acción}} **para** {{beneficio}}
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado {{estado inicial con datos}}
Cuando {{acción}}
Entonces {{resultado verificable}}
```
**Objetos que la implementan hoy**: {{lista con tipo}} · **Prioridad de reconstrucción**: MVP | fase 2 | opcional
**Evidencia de los criterios**: {{artefacto real del que deriva cada Then: validación de pantalla / transición de estados.md / gateway — con ruta}}
