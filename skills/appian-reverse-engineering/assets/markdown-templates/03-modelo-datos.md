<!--
  Plantilla 03 — Modelo de datos
  Sigue las reglas de `references/presentation-rules.md`:
    1. TL;DR arriba
    2. Vista (ER global o índice de subdominios) en el medio
    3. Detalle al pie

  ESTRATEGIA DE PARTICIONAMIENTO (criterio: legibilidad, no número arbitrario):
    - Hasta ~15 entidades: UN ER global con todas. Suficiente.
    - Entre ~15-30: UN ER global con las entidades más conectadas (hubs) + sub-ER por subdominio para el resto.
    - Más de ~30: obligatorio sub-ER por subdominio (cada uno ~8-15 entidades). El ER global pasa a ser un "mapa de subdominios" muy resumido.

  REGLA INVARIABLE: el catálogo en tablas DEBE incluir el 100% de records y CDTs sin truncar.
  La partición afecta solo a los diagramas visuales, no al inventario.
-->

# Modelo de datos

> **TL;DR**: {{N records, N CDTs, N data stores}}. {{Relación principal: p.ej. "El núcleo es RT_Expediente, conectado a RT_Cliente, RT_Documento y RT_Estado"}}.
> Particionado en **{{N}} subdominios** para legibilidad: {{lista corta de subdominios}}.
> Leer la Vista; bajar al Detalle solo para fichas de records/CDTs específicos.

## Vista — Diagrama ER global

> **Si la app tiene hasta ~15 entidades**: muestra todas. **Si tiene más**: muestra las entidades más conectadas (hubs) + sus relaciones principales. Las entidades secundarias están en los sub-diagramas por subdominio (abajo).

> SVG renderizado: `diagrams/modelo-datos.svg`. Si no se pudo renderizar, el bloque Mermaid embebido funciona en GitHub/VSCode/preview Markdown.

```mermaid
erDiagram
  {{ENTIDAD_HUB_1}} ||--o{ {{ENTIDAD_HUB_2}} : "{{relación}}"
  {{ENTIDAD_HUB_1}} ||--|| {{ENTIDAD_HUB_3}} : "{{relación}}"
  {{ENTIDAD_HUB_1}} }o--|| {{ENTIDAD_HUB_4}} : "{{relación}}"
  {{ENTIDAD_HUB_1}} {
    string id PK
    string {{campo_clave_1}}
    string {{campo_FK_clave}} FK
  }
  {{ENTIDAD_HUB_2}} {
    string id PK
    string {{campo_FK}} FK
  }
  {{ENTIDAD_HUB_3}} {
    string id PK
    string nombre
  }
  {{ENTIDAD_HUB_4}} {
    string id PK
    string descripcion
  }
```

## Vista — Sub-diagramas por subdominio

> Cuando la app tiene muchas entidades (típicamente >15), generar **un sub-diagrama por subdominio funcional**. Cada subdominio suele agrupar 8-15 entidades relacionadas. El subdominio se infiere del prefijo de los records (`RT_Expediente_*`, `RT_Cliente_*`, etc.) o de los casos de uso de `01-funcional.md`. Si una entidad pertenece a más de un subdominio, aparece en el principal y se referencia desde los otros.

### Subdominio `{{nombre_subdominio_1}}` ({{N}} entidades)

```mermaid
erDiagram
  {{ENTIDAD_1}} ||--o{ {{ENTIDAD_2}} : "..."
  ...
```

### Subdominio `{{nombre_subdominio_2}}` ({{N}} entidades)

```mermaid
erDiagram
  ...
```

> Si la app tiene pocas entidades (~15 o menos), el ER global ya las contiene todas — omitir esta sección de sub-diagramas.

## Vista — Tabla resumen de records

> Una fila por Record Type. Solo columnas escaneables. Detalle ampliado en la sección "Detalle por Record Type".

| Record Type | Visible | Fuente | CDT asociado | Tabla BBDD | Vistas | Acciones | Estado |
|---|---|---|---|---|---|---|---|
| `{{RT_1}}` | {{visible}} | DB | `{{cdt}}` | `{{tabla}}` | {{N}} | {{N}} | ✅ |
| `{{RT_2}}` | {{visible}} | Expression | — | — | {{N}} | {{N}} | 🔵 |

## Vista — Tabla resumen de CDTs

| CDT | Namespace | Tabla mapeada | Campos | Usado por |
|---|---|---|---|---|
| `{{CDT_1}}` | `{{ns}}` | `{{tabla}}` | {{N}} | `{{lista}}` |
| `{{CDT_2}}` | `{{ns}}` | — | {{N}} | `{{lista}}` |

## Vista — Mapeo de nombres saneados (si aplica)

> Si algún nombre técnico tiene caracteres no compatibles con `erDiagram` (espacios, acentos, guiones), se sustituye en el diagrama. Mapeo:

| Nombre técnico real | Nombre en el diagrama |
|---|---|
| `{{Record real con acento}}` | `{{ENTIDAD_SANEADA}}` |

> Si no hay sustituciones, omitir.

---

## Detalle por Record Type

> Una ficha por Record Type. Saltar a:
{{índice navegable cuando haya >5 records}}

### `{{RT_1}}` — {{nombre_visible}}

**TL;DR**: {{una línea funcional: qué representa este record y para qué se usa}}.

| Campo | Valor |
|---|---|
| Nombre técnico | `{{RT_1}}` |
| Nombre visible | {{visible}} |
| Fuente | DB / Service / Process / Expression |
| CDT asociado | `{{CDT}}` |
| Tabla BBDD | `{{tabla_o_vacio}}` |
| Data Source | `{{datasource_id}}` |
| Data Fabric | Sí / No |
| Total vistas | {{N}} |
| Total acciones | {{N}} |
| Estado | ✅/🔵 — Evidencia: `{{ruta}}` |

**Campos clave**

> Semántica de campos: `Obligatorio` sale de `detail.json` (`fields[].required`); `Dominio/valores` del cruce con constants/máquinas de estados (con evidencia); `Default` y `Regla de cálculo` de defaults/expresiones observados en XML o SAIL. Celda sin evidencia → `—` (nunca se omite la columna).

| Campo | Tipo | Visible | Key | Obligatorio | Dominio/valores | Default | Regla de cálculo | Notas |
|---|---|---|---|---|---|---|---|---|
| `id` | long | Sí | Sí | Sí | — | — | — | PK |
| `{{campo_2}}` | string | Sí | No | {{Sí/No}} | {{p.ej. `BORRADOR/ENVIADO/...` — Evidencia: `{{ruta_constant}}`}} | {{valor o —}} | {{expresión que lo calcula o —}} | {{descripción breve}} |

**Record Views**

| Vista | Interface asociada | Campos mostrados |
|---|---|---|
| `{{vista_1}}` | `{{interface}}` | {{lista breve}} |

**Record Actions**

| Action | Process Model destino | Grupos que la pueden invocar |
|---|---|---|
| `{{action_1}}` | `{{PM_destino}}` | `{{grupos}}` |

**Related Records**

- → `{{RT_Otro}}` vía `{{join_descripción}}`.

**Sub-entidades del record** (User filters · Custom fields · Record events)

> Sección obligatoria en cada ficha. Si el XML del RT los declara, listarlos. Si el parser no los expone aún, buscar por tag directamente en el XML; si tampoco así se puede determinar → fila `🟡 no analizado — {{motivo}}`. Si el XML no declara ninguno → una fila `— (el XML no declara ninguna)`.

| Sub-entidad | Nombre | Configuración relevante | Evidencia |
|---|---|---|---|
| User filter | `{{filtro_1}}` | {{campo filtrado + opciones o expresión}} | `{{ruta_xml}}#{{tag}}` |
| Custom field | `{{campo_custom_1}}` | {{tipo + expresión de cálculo}} | `{{ruta_xml}}#{{tag}}` |
| Record events | {{configurado / no configurado}} | {{RT de historial de eventos + acciones monitorizadas}} | `{{ruta_xml}}#{{tag}}` |

**Notas relevantes** (si aplica):
- {{nota_1}}

---

### `{{RT_2}}`

{{Repetir.}}

---

## Detalle por CDT

> Saltar a: {{índice navegable cuando haya >5 CDTs}}

### `{{CDT_1}}`

**TL;DR**: {{para qué se usa este CDT}}.

| Campo | Valor |
|---|---|
| Namespace | `{{ns}}` |
| Fichero | `{{ruta_xsd}}` |
| Mapeo BBDD | Sí (tabla `{{tabla}}`) / No |
| Anotaciones JPA | {{lista_clave}} |
| Total campos | {{N}} |

**Campos**

> Mismas columnas de semántica que en la ficha de Record Type. `Obligatorio` sale del XSD (`minOccurs`, ya expuesto como `required` en `detail.json`); celda sin evidencia → `—` (nunca se omite la columna).

| Nombre | Tipo XSD | Columna BBDD | PK/FK | Obligatorio | Dominio/valores | Default | Regla de cálculo | Comentario |
|---|---|---|---|---|---|---|---|---|
| `id` | xsd:long | id | PK | Sí | — | — | — | — |
| `{{campo_2}}` | xsd:string | {{col}} | — | {{Sí/No}} | {{valores con evidencia o —}} | {{default del XSD o —}} | {{expresión o —}} | {{descripción}} |

**Relaciones declaradas**

- `{{campo_FK}}` → CDT `{{CDT_Otro}}` (`@ManyToOne`)

**Dónde se usa**
- Records: {{lista}}
- Process Variables: {{lista}}
- Interfaces: {{lista}}

---

### `{{CDT_2}}`

{{Repetir.}}

---

## Detalle de Data Stores

| Data Store | JNDI / Data Source | Entidades configuradas | Estado |
|---|---|---|---|
| `{{DS_1}}` | `{{jndi}}` | `{{lista_CDTs}}` | ✅ |

---

## Resumen rápido

- Total Record Types: {{N}} · CDTs: {{N}} · Data Stores: {{N}}.
- Records con Data Fabric: {{N}}.
- Records sin CDT asociado (views derivadas o calculadas): {{N}}.
- CDTs sin Record asociado (modelo interno): {{N}}.
- Subdominios identificados: {{lista}}.
- Hubs del modelo (entidades con más relaciones): `{{top_3}}`.
- Hallazgos: {{N riesgos / N pendientes}}.
