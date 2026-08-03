# Formato de la respuesta final al usuario

Plantilla obligatoria de la respuesta que devuelve la skill **al terminar** todas las fases. Rellena cada bloque con datos reales del análisis. **No añadas párrafos genéricos antes o después** — el usuario quiere salida operativa, escaneable.

---

## Plantilla literal

```markdown
# Reingeniería inversa Appian completada

## Carpeta de salida
`<ruta>/_doc_generada/`

## Documentos generados
- _doc_generada/00-resumen-ejecutivo.md
- _doc_generada/01-funcional.md
- _doc_generada/02-arquitectura.md  (+ diagrams/arquitectura.svg)
- _doc_generada/03-modelo-datos.md  (+ diagrams/modelo-datos.svg)
- _doc_generada/04-seguridad-grupos.md
- _doc_generada/05-integraciones-consumidas.md
- _doc_generada/06-apis-expuestas.md
- _doc_generada/07-batches.md
- _doc_generada/08-procesos-bpmn/indice.md  (+ N diagramas)
- _doc_generada/09-valor-adicional.md
- _doc_generada/INVENTARIO.md

## Métricas de la app analizada
- Records: N · CDTs: N · Process Models: N · Integrations: N · Web APIs: N · Groups: N · Constants: N · Interfaces: N · Expression Rules: N · Sites: N
- Líneas totales de SAIL inspeccionadas: N

## Nivel de confianza global
Alto / Medio / Bajo — [justificación breve]

## Principales funcionalidades reconstruidas
- ...

## Principales objetos críticos
- ...

## Principales riesgos detectados
- ...

## Pendientes de validación
- ...

## Render de diagramas
- Mermaid (`.mmd`): N generados · N renderizados a SVG con `mmdc` · N embebidos (mmdc no disponible)
- BPMN (`.bpmn`): N generados como fuente. Abre en Camunda Modeler, draw.io o demo.bpmn.io.
- Diagramas saneados / sustituidos por tabla: N / N

## Seguridad
- Secretos detectados en el export: Sí (N) / No
- Secretos enmascarados en la salida: Sí / No aplica
- Riesgos de seguridad documentados: Sí (N) / No

## Salidas adicionales generadas (si aplica)
- 📄 PDF: `<ruta>/_doc_generada/EXPORT.pdf` (solo si `pdf: true` en `output_preferences.json`)
- 🖥️ Dashboard: `<ruta>/_doc_generada/dashboard/index.html` (solo si `dashboard: true`)

## Siguiente paso recomendado
1. Abrir `_doc_generada/00-resumen-ejecutivo.md`.
2. Revisar `_doc_generada/08-procesos-bpmn/indice.md` para entender el orquestado de procesos.
3. Validar los pendientes con el equipo funcional/técnico responsable.
```

---

## Reglas duras

- **No añadas saludos** ("Aquí tienes...", "Espero que te sirva...").
- **No expliques lo que hiciste** — los `.md` ya lo explican. La respuesta es un índice operativo.
- **Cifras concretas**, no rangos ni aproximaciones ("Records: 42", no "Records: ~40").
- **Lista exacta de documentos generados** — si has omitido alguno por falta de evidencia (p. ej. `07-batches.md` sin batches), márcalo como "(omitido — no hay process models con start event temporal)".
- **Nivel de confianza global** sintetiza el estado del análisis. Justifica en una línea: "Alto: 95% de objetos con evidencia confirmada", "Medio: 60% inferidos por nombre, validación funcional requerida".

---

## Criterios de aceptación (cuándo la skill ha hecho bien su trabajo)

Sobre un export real, la skill se considera correcta cuando:

- Identifica el 100% de records, CDTs, process models, integrations, web APIs, groups y constants del export.
- Genera los 11 entregables y todos los diagramas renderizan o quedan listados como pendientes de render.
- Cada integración consumida queda documentada con endpoint, método, auth y caller.
- Cada Web API expuesta queda documentada con URL, método, auth, body, qué dispara y grupos autorizados.
- Cada process model tiene su BPMN renderizado y enlazado en `08-procesos-bpmn/indice.md`.
- El árbol de grupos y la matriz de seguridad es consistente con `rolemap.xml` / `<roleMap>` de cada objeto.
- No hay secciones vacías ni placeholders.
- `09-valor-adicional.md` incluye al menos: objetos huérfanos, riesgos detectados y glosario.
