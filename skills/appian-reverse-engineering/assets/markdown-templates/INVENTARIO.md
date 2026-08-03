<!--
  Plantilla INVENTARIO — Inventario completo por tipo de objeto
  Debe cubrir el 100% de los objetos del export.
  Generar en Fase 2 a partir de `scripts/parse_export.py --inventory`.
-->

# Inventario de la aplicación

**Aplicación:** {{nombre_visible}} (`{{nombre_tecnico}}`)
**Ruta del export:** `{{ruta_export}}`
**Fecha de análisis:** {{fecha_iso}}

## Conteo por tipo

| Tipo de objeto | Cantidad |
|---|---|
| Application | 1 |
| Sites | {{N}} |
| Pages / Portals | {{N}} |
| Record Types | {{N}} |
| Record Views | {{N}} |
| Record Actions | {{N}} |
| Related Actions | {{N}} |
| Interfaces | {{N}} |
| Expression Rules | {{N}} |
| Decisions | {{N}} |
| Process Models | {{N}} |
| Constants | {{N}} |
| Data Stores | {{N}} |
| CDTs (XSDs) | {{N}} |
| Connected Systems | {{N}} |
| Integrations | {{N}} |
| Web APIs | {{N}} |
| Groups | {{N}} |
| Group Types | {{N}} |
| Folders (Rules / Documents) | {{N}} |
| Documents | {{N}} |
| Knowledge Centers | {{N}} |
| Plugins | {{N}} |
| ICF files | {{N}} |
| **Total** | **{{TOTAL}}** |

## Records / Record Types

| Nombre técnico | Nombre visible | UUID | Ruta | Descripción | UpdatedOn / By |
|---|---|---|---|---|---|
| `{{rt_1}}` | {{visible}} | `{{uuid}}` | `{{ruta}}` | {{desc}} | `{{date}}` / `{{user}}` |

## CDTs

| Nombre | Namespace | Tabla mapeada | Campos | Ruta |
|---|---|---|---|---|
| `{{cdt_1}}` | `{{namespace}}` | `{{tabla_o_vacio}}` | {{n_campos}} | `{{ruta_xsd}}` |

## Process Models

| Nombre técnico | Nombre visible | UUID | Trigger | Subprocesos | Ruta |
|---|---|---|---|---|---|
| `{{pm_1}}` | {{visible}} | `{{uuid}}` | none/timer/message | {{n}} | `{{ruta}}` |

## Interfaces

| Nombre técnico | UUID | Ruta | Descripción |
|---|---|---|---|
| `{{if_1}}` | `{{uuid}}` | `{{ruta}}` | {{desc}} |

## Expression Rules

| Nombre técnico | UUID | Ruta | Descripción |
|---|---|---|---|
| `{{rule_1}}` | `{{uuid}}` | `{{ruta}}` | {{desc}} |

## Decisions

| Nombre técnico | UUID | Ruta | Descripción |
|---|---|---|---|
| `{{decision_1}}` | `{{uuid}}` | `{{ruta}}` | {{desc}} |

## Integrations

| Nombre técnico | Nombre visible | Método | Endpoint enmascarado | Connected System | Ruta |
|---|---|---|---|---|---|
| `{{int_1}}` | {{visible}} | {{verb}} | `{{url}}` | `{{cs}}` | `{{ruta}}` |

## Connected Systems

| Nombre técnico | Tipo | Base URL enmascarada | Auth | Ruta |
|---|---|---|---|---|
| `{{cs_1}}` | HTTP/OAuth/SAP/… | `{{url}}` | {{auth_type}} | `{{ruta}}` |

## Web APIs

| Nombre técnico | Método | Endpoint Path | Ruta |
|---|---|---|---|
| `{{wa_1}}` | {{verb}} | `/suite/webapi/{{path}}` | `{{ruta}}` |

## Sites

| Nombre técnico | Nombre visible | Páginas | Ruta |
|---|---|---|---|
| `{{site_1}}` | {{visible}} | {{n}} | `{{ruta}}` |

## Groups

| Nombre técnico | Tipo | Grupo padre | Ruta |
|---|---|---|---|
| `{{grupo_1}}` | Custom/System | `{{padre_o_vacio}}` | `{{ruta}}` |

## Constants

| Nombre técnico | Tipo Appian | Valor (o 🔒 enmascarado) | Ruta |
|---|---|---|---|
| `{{cons_1}}` | TEXT/URL/GROUP/USER/… | `{{valor_o_secret}}` | `{{ruta}}` |

## Data Stores

| Nombre técnico | JNDI | Entidades | Ruta |
|---|---|---|---|
| `{{ds_1}}` | `{{jndi}}` | {{lista_cdts}} | `{{ruta}}` |

## Folders / Documents / Knowledge Centers

| Nombre | Tipo | Padre | Ruta |
|---|---|---|---|
| `{{f_1}}` | Folder | `{{padre}}` | `{{ruta}}` |
| `{{d_1}}` | Document | `{{folder}}` | `{{ruta}}` |
| `{{kc_1}}` | Knowledge Center | — | `{{ruta}}` |

## Plugins / Smart services personalizados

| Plugin | Smart services | Functions | CS types | Versión | Ruta |
|---|---|---|---|---|---|
| `{{plugin_1}}` | {{lista}} | {{lista}} | {{lista}} | `{{ver}}` | `{{ruta}}` |

## ICF (configuración por entorno)

| Fichero | Tamaño | Notas |
|---|---|---|
| `import-customization-file-{{env}}.properties` | {{KB}} | {{n_overrides}} overrides |

## Consistencia con `application.xml`

Verificación cruzada: cada UUID declarado en `application.xml` debe corresponder a un XML del export, y viceversa.

| Métrica | Valor |
|---|---|
| UUIDs declarados en `application.xml` | {{N}} |
| Objetos físicos encontrados en el export | {{N}} |
| Declarados sin archivo (faltan en el export) | {{N}} → ver lista abajo |
| Archivos sin declarar en `application.xml` | {{N}} → ver lista abajo |

### Declarados sin archivo

{{Lista de UUIDs que aparecen en `application.xml` pero no tienen un XML correspondiente. Si está vacío, escribir "Ninguno".}}

### Archivos sin declarar

{{Lista de XMLs encontrados que no están en `application.xml`. Si está vacío, escribir "Ninguno".}}

## Notas del inventario

- {{Cualquier anomalía detectada al inventariar: namespaces inconsistentes, XMLs malformados que se ignoraron, etc.}}
- {{Si todos los conteos son consistentes, escribir: "Inventario consistente. 100% de los objetos cubiertos."}}
