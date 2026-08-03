<!--
  Plantilla 09 — Información de valor adicional
  REGLA CLAVE: incluir SÓLO las secciones donde haya hallazgos reales.
  Si una sección no tiene contenido, OMITIRLA por completo (no dejarla vacía con "Sin hallazgos").
  El único contenido obligatorio (siempre que haya datos) es: Objetos huérfanos · Riesgos detectados · Glosario.
-->

# Información de valor adicional

> Hallazgos transversales útiles para mantenimiento, onboarding y auditoría. Solo se documentan secciones con contenido real.

## Constantes y configuración por entorno

> Solo si hay constantes con prefijo DEV/PRE/PRO o cubiertas por ICF.

| Constant | Tipo | Valor por entorno | Usada por | Notas |
|---|---|---|---|---|
| `{{cons_1}}` | TEXT | DEV: `{{}}` · PRE: `{{}}` · PRO: `{{}}` | `{{lista_callers}}` | {{nota}} |
| `{{cons_2}}` | URL | 🔒 enmascarada | `{{}}` | secreto, no exponer |

## Catálogo de expression rules reutilizables

> Solo expression rules con **>3 callers** o que claramente son utilidades de negocio compartidas. No listar reglas usadas una sola vez.

| Expression Rule | Propósito | Inputs | Output | Callers |
|---|---|---|---|---|
| `{{rule_1}}` | {{qué calcula}} | `{{input_types}}` | `{{output_type}}` | {{n}} ({{lista}}) |
| `{{rule_2}}` | {{}} | `{{}}` | `{{}}` | {{n}} |

## Decision tables

> Reglas de negocio expresadas en decision tables, traducidas a lenguaje natural.

### `{{decision_1}}`

**Cuándo se invoca:** {{}}
**Inputs:** {{lista}}
**Output:** {{}}

**Reglas (resumidas):**

1. Si {{condición_1}}, entonces {{resultado_1}}.
2. Si {{condición_2}}, entonces {{resultado_2}}.

## Sites y páginas

| Site | Páginas | Contenido principal | Dispositivos | Grupos con acceso |
|---|---|---|---|---|
| `{{site_1}}` | {{n}} | Records: `{{}}`, Reports: `{{}}` | Web + Mobile | `{{grupos}}` |

## Plugins / smart services personalizados

| Plugin | Smart services / functions / CS types | Versión | Riesgo |
|---|---|---|---|
| `{{plugin_1}}` | {{lista}} | `{{version}}` | 🟡 dependencia externa, validar disponibilidad en PRO |

## Document templates / Knowledge Centers / Folders

| Objeto | Tipo | Propósito | Usado por |
|---|---|---|---|
| `{{doc_template_1}}` | Document Template | {{propósito}} | `{{PM_o_rule}}` |
| `{{kc_1}}` | Knowledge Center | {{propósito}} | — |

## Tareas humanas

> Inventario de user input tasks, asignación, SLA, escalation.

| Process Model | Tarea | Asignación | SLA | Escalation | Notificación |
|---|---|---|---|---|---|
| `{{pm_1}}` | `{{task_1}}` | grupo `{{}}` | {{}} | {{}} | {{email_o_no}} |

## Emails y notificaciones

| Disparado por | Asunto / plantilla | Destinatarios | Trigger |
|---|---|---|---|
| `{{pm_o_rule}}` | "{{asunto}}" | `{{grupos_o_expresion}}` | {{cuándo}} |

## Manejo de errores

> Exception flows, alert nodes, patrones de retry detectados.

| Objeto | Tipo de manejo | Detalle | Riesgo |
|---|---|---|---|
| `{{pm_1}}` | Exception flow | nodo `{{X}}` → notifica `{{grupo}}` | bajo |
| `{{int_1}}` | Sin retry | 🔴 falla en primer error | alto |

## Mapa de dependencias

> Patrones notables del grafo (Fase 3).

- **Acoplamientos fuertes detectados:**
  - `{{obj_A}}` ↔ `{{obj_B}}` (referencia bidireccional). 🟡 evaluar refactor.
- **Ciclos:**
  - `{{obj_A}}` → `{{obj_B}}` → `{{obj_C}}` → `{{obj_A}}`. 🔴 riesgo de loop.
- **Hubs** (>5 dependientes):
  - `{{obj_X}}` ({{tipo}}) — usado por {{n}} objetos.

> Si no hay acoplamientos / ciclos / hubs notables, omitir las sub-secciones que no apliquen.

## Objetos huérfanos

> Declarados en el export pero **sin referencias entrantes** detectadas. Candidatos a limpieza. Validar antes de borrar (pueden invocarse desde fuera del export).

| Objeto | Tipo | Ruta | Última modificación |
|---|---|---|---|
| `{{obj_1}}` | Expression Rule | `{{ruta}}` | `{{updatedOn}}` |
| `{{obj_2}}` | Process Model | `{{ruta}}` | `{{updatedOn}}` |
| `{{obj_3}}` | Constant | `{{ruta}}` | `{{updatedOn}}` |

**Recomendación:** validar con el equipo funcional si son legítimamente externos o eliminables.

## Glosario de negocio

> Términos extraídos de nombres y descripciones de records / CDTs / campos. Útil para que un consultor nuevo entienda el vocabulario del cliente.

| Término | Definición inferida | Aparece en |
|---|---|---|
| {{Termino_1}} | {{definición desde descripción de record o campo}} | `{{record}}`, `{{cdt}}` |
| {{Termino_2}} | {{}} | `{{}}` |

## Métricas de la app

| Métrica | Valor |
|---|---|
| Total objetos | {{N}} |
| Líneas de SAIL estimadas | {{N}} |
| Process models con >30 nodos | {{N}} |
| Expression rules con >200 líneas | {{N}} |
| Interfaces con >500 líneas | {{N}} |
| Complejidad ciclomática media (process models) | {{N}} |

## Riesgos / code smells detectados

| # | Riesgo | Severidad | Dónde | Recomendación |
|---|---|---|---|---|
| 1 | URLs / IDs hardcodeados | 🔴 | `{{ruta_1}}`, `{{ruta_2}}` | Mover a constants con ICF |
| 2 | Expression rules >200 líneas | 🟡 | `{{rule_X}}` | Refactor en utilidades |
| 3 | Queries sin paginación | 🔴 | `{{rule_o_pm}}` | Añadir `pagingInfo` |
| 4 | Integraciones sin manejo de error | 🔴 | `{{int_X}}` | Wrapper con retry / fallback |
| 5 | Objetos accesibles por `All Users` | 🔴 | `{{lista}}` | Restringir a grupo específico |
| 6 | Grupos sin miembros | 🟡 | `{{grupos}}` | Validar funcional |
| 7 | Objetos sin seguridad explícita (heredan de folder laxo) | 🟡 | `{{lista}}` | Revisar herencia |
| 8 | Uso de `loggedInUser()` en batches | 🔴 | `{{pm_batch}}` | Anti-patrón Appian |
| 9 | Naming inconsistente (mezcla camel/snake/Pascal) | 🟡 | `{{módulo}}` | Convención de equipo |
| 10 | Reglas duplicadas (nombres similares, código similar) | 🟡 | `{{rule_A}}` y `{{rule_B}}` | Consolidar |

## Versionado

> Última modificación por objeto si el export trae `@updatedOn` / `@updatedBy`.

| Objeto | Tipo | updatedOn | updatedBy |
|---|---|---|---|
| `{{obj_1}}` | {{tipo}} | `{{fecha}}` | `{{usuario}}` |

## Internacionalización

| Objeto | Idiomas detectados | Notas |
|---|---|---|
| `{{interface_1}}` | es, en | propiedades localizadas |

> Si la app es monolingüe, omitir esta sección.
