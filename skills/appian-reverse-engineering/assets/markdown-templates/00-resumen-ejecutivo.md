<!--
  Plantilla 00 — Resumen ejecutivo
  Generar AL FINAL (consume datos de las demás plantillas).
  Reemplaza todos los {{placeholders}} con datos reales.
  Si no hay evidencia para una sección, escribe explícitamente:
    "No se ha encontrado evidencia suficiente. Pendiente de validación con [rol]."
  No dejes placeholders sin rellenar.
-->

# Resumen ejecutivo

**Aplicación:** {{nombre_visible_aplicacion}} (`{{nombre_tecnico_aplicacion}}`)
**Ruta fuente:** `{{ruta_export}}`
**Fecha de análisis:** {{fecha_iso}}
**Versión de Appian detectada:** {{version_o_no_determinada}}
**Idioma de la documentación:** {{idioma}}

## Pitch (1 párrafo)

{{Pitch funcional en lenguaje de negocio: qué problema resuelve la app, para quién y qué valor aporta. Sin jerga Appian.}}

> Estado: ✅/🔵 — Evidencia: `{{ruta_app_xml}}#description` y `{{otra_ruta}}`

## Volumen del export

| Tipo de objeto | Cantidad |
|---|---|
| Records / Record Types | {{n_records}} |
| CDTs | {{n_cdts}} |
| Process Models | {{n_pm}} |
| Interfaces | {{n_interfaces}} |
| Expression Rules | {{n_rules}} |
| Decisions | {{n_decisions}} |
| Integrations | {{n_integrations}} |
| Connected Systems | {{n_cs}} |
| Web APIs | {{n_webapis}} |
| Sites | {{n_sites}} |
| Groups | {{n_groups}} |
| Constants | {{n_constants}} |
| Data Stores | {{n_datastores}} |
| Documents / Folders | {{n_documents}} |

## Procesos críticos (top 3–5)

| Process Model | Por qué es crítico | Trigger | Subprocesos | Integraciones |
|---|---|---|---|---|
| `{{pm_name_1}}` | {{razón}} | {{trigger}} | {{n}} | {{integraciones}} |
| `{{pm_name_2}}` | {{razón}} | {{trigger}} | {{n}} | {{integraciones}} |

Detalle: ver `08-procesos-bpmn/indice.md`.

## Integraciones críticas (top 3–5)

| Integration | Sistema externo | Método | Endpoint enmascarado | Callers |
|---|---|---|---|---|
| `{{int_1}}` | {{sistema}} | {{verb}} | `{{url_enmascarada}}` | {{quien_la_llama}} |

Detalle: ver `05-integraciones-consumidas.md`.

## APIs expuestas (resumen)

{{N APIs expuestas. Caso de uso principal: ...}}

Detalle: ver `06-apis-expuestas.md`.

## Procesos batch / recurrentes

{{Listar batches con frecuencia humana, o decir explícitamente "No se han detectado procesos recurrentes en el export".}}

Detalle: ver `07-batches.md`.

## Riesgos principales (top 5)

1. 🔴 {{riesgo_1}} — {{evidencia + impacto + recomendación}}
2. 🔴 {{riesgo_2}} — {{...}}
3. 🟡 {{riesgo_3}} — {{...}}

Detalle: ver `09-valor-adicional.md` → sección Riesgos / code smells.

## Objetos huérfanos

{{N objetos declarados pero no referenciados.}} Top 5:

- `{{obj_1}}` ({{tipo}}) — {{ruta}}
- `{{obj_2}}` ({{tipo}}) — {{ruta}}

Detalle: ver `09-valor-adicional.md` → sección Objetos huérfanos.

## Pendientes de validación principales

- 🟡 {{pendiente_1}} — Responsable sugerido: {{rol}}
- 🟡 {{pendiente_2}} — Responsable sugerido: {{rol}}

## Nivel de confianza global

**{{Alto | Medio | Bajo}}** — {{justificación}}

## Cómo seguir

1. Abrir [01-funcional.md](./01-funcional.md) para entender qué hace la app.
2. Abrir [02-arquitectura.md](./02-arquitectura.md) para ver objetos y relaciones.
3. Revisar [08-procesos-bpmn/indice.md](./08-procesos-bpmn/indice.md) para los procesos clave.
4. Para mantenimiento, mirar [09-valor-adicional.md](./09-valor-adicional.md) sección Riesgos / Huérfanos.
