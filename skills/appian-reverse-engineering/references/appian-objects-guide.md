# Guía de objetos Appian

Patrones para identificar tipos de objetos Appian en artefactos exportados. Úsalo en Fase 1 (inventario) y Fase 4 (técnica).

## Estructura típica de un export Appian

Un export Appian descomprimido suele tener:

- Una carpeta raíz con nombre tipo `<NombreApp>_App.zip` (descomprimida o no).
- Dentro, una estructura por tipo de objeto o un único `application.xml` con todos los objetos referenciados por UUID.
- `import-customization-file*.properties` (ICF) — valores por entorno.
- Formato *Haul* actual: carpetas en **camelCase** — `processModel/`, `recordType/`, `site/`, `content/`, `group/`, `connectedSystem/`, `datatype/` (XSDs de CDTs), `dataStore/`, `application/`. Los exports antiguos usaban guiones (`process-model/`, `record-type/`, `cdt/`); ambos se reconocen con `scripts/parse_export.py --check`.

Si solo tienes un `.zip`, descomprime antes de analizar:

```bash
unzip -d <destino> <export>.zip
```

## Reconocimiento por XML

Cada tipo de objeto Appian tiene tags raíz característicos. Identifica el tipo desde el primer elemento del XML.

| Tipo de objeto Appian | Patrón típico en XML / contenido |
|---|---|
| **Application** | `<application>`, `<applicationDefinition>` |
| **Site** | `<site>`, `<sitePage>` |
| **Portal** | `<portal>`, `<portalPage>` |
| **Record Type** | `<recordType>`, `<recordSource>`, `<sourceType>BUSINESS_DATA_OR_DATABASE`, `<recordFieldList>` |
| **Record Action** | `<recordAction>`, `<actionStartFormType>` |
| **Record View** | `<recordView>`, `<viewDefinition>` |
| **Interface** | `<interface>`, `<interfaceDefinition>`, contenido SAIL con `a!sectionLayout`, `a!formLayout`, `a!localVariables` |
| **Expression Rule** | `<expressionRule>`, `<ruleInputs>`, código SAIL/expresión |
| **Decision** | `<decision>`, `<decisionTable>`, `<inputs>`, `<outputs>`, `<rules>` |
| **Process Model** | `<processModel>` o `.bpmn`. Contiene `<startEvent>`, `<userInputTask>`, `<scriptTask>`, `<gateway>`, `<endEvent>`, `<flow>` |
| **Constant** | `<constant>`, `<value>`, `<typeRef>` |
| **Data Store** | `<dataStore>`, `<jndi>`, `<entities>` |
| **CDT (Custom Data Type)** | `.xsd`, `<xsd:complexType>`, `<xsd:element>` |
| **Connected System** | `<connectedSystem>`, `<connectedSystemType>` (HTTP, OAuth, JDBC, etc.) |
| **Integration** | `<integration>`, referencia a `<connectedSystem>` |
| **Web API** | `<webApi>`, `<httpMethod>`, `<endpointPath>` |
| **Group** | `<group>`, `<groupType>`, `<members>` |
| **Folder** | `<folder>`, `<parentFolder>` |
| **Document** | `<document>` con `<documentVersion>` |
| **Plugin** | `<plugin>`, suele venir como `.jar` con manifest |

## Búsquedas útiles con grep/glob

Una vez tienes la estructura, usa estos patrones para detectar objetos masivamente:

```bash
# Process models
find . -name '*.xml' -exec grep -l '<processModel\b' {} \;
# o por extensión BPMN
find . -name '*.bpmn'

# Interfaces
find . -name '*.xml' -exec grep -l '<interface\b\|a!formLayout\|a!sectionLayout' {} \;

# Expression rules
find . -name '*.xml' -exec grep -l '<expressionRule\b' {} \;

# Records
find . -name '*.xml' -exec grep -l '<recordType\b' {} \;

# Constants
find . -name '*.xml' -exec grep -l '<constant\b' {} \;

# Connected systems
find . -name '*.xml' -exec grep -l '<connectedSystem\b' {} \;

# Integrations
find . -name '*.xml' -exec grep -l '<integration\b' {} \;

# Web APIs
find . -name '*.xml' -exec grep -l '<webApi\b' {} \;

# Sites
find . -name '*.xml' -exec grep -l '<site\b' {} \;

# CDTs (XSDs)
find . -name '*.xsd'

# Data Stores
find . -name '*.xml' -exec grep -l '<dataStore\b' {} \;

# ICF
find . -name 'import-customization-file*.properties'
find . -name '*.icf'
find . -name '*.properties'
```

## 🔴 El SAIL exportado viene en FORMATO CANÓNICO (leer antes de documentar nada)

Lo que se ve en el Designer **no** es lo que viaja en el XML. Un export real no contiene ni una sola aparición de `rule!`, `cons!` o `a!textField`. Antes de describir una pantalla o una regla hay que traducir:

| En el Designer (y en la documentación que escribes) | En el XML exportado |
|---|---|
| `a!formLayout(...)`, `a!textField(...)` | `#"SYSTEM_SYSRULES_formLayout_v2"(...)`, `#"SYSTEM_SYSRULES_textField"(...)` |
| `rule!MI_REGLA(x: 1)` | `#"_a-0000f01f-…_2358028"(x: 1)` — por UUID, no por nombre |
| `cons!MI_CONSTANTE` | `#"_a-0000f01f-…_2357817"` |
| `recordType!{uuid}Nombre` | `#"urn:appian:record-type:v1:{uuid}"` |
| `recordType!{uuid}Nombre.fields.{uuid}campo` | `#"urn:appian:record-field:v1:{rtUuid}/{fieldUuid}"` |

Reglas de lectura:

- **`SYSTEM_SYSRULES_<X>` es el componente `a!<X>`.** Quita el prefijo y el sufijo de versión (`_v1`, `_v2`) para nombrar el componente en la ficha: `SYSTEM_SYSRULES_richTextItem_v1` → `a!richTextItem`. El sufijo de versión es de plataforma, no del diseño de la app.
- **Los UUID `#"_a-…"` hay que resolverlos contra el inventario** para saber a qué objeto apuntan. `_intermedio/graph.json` ya lo hace: consulta ahí los callers en vez de leer UUIDs a ojo.
- **`#"urn:appian:record-field:v1:{rtUuid}/{fieldUuid}"`**: el primer UUID es el record type y el segundo el campo. Para nombrar el campo, búscalo en `detail.json`.
- En la documentación **escribe siempre la forma del Designer** (`a!textField`, `rule!MI_REGLA`): es la que el lector reconoce y la que necesita para reconstruir. Deja el UUID solo en la línea de Evidencia.

Ojo también con el **nombre de los process models**: el `<meta>` trae `name` (el del modelo) y `process-name` (la expresión que nombra cada instancia, tipo `="X - " & pp!starttime`). El bueno es el primero.

## Detección de dependencias entre objetos

Patrones de referencia entre objetos en SAIL/expresiones:

| Patrón | Significa |
|---|---|
| `rule!<nombre>(...)` | Invocación a expression rule. |
| `cons!<nombre>` | Uso de constant. |
| `recordType!<nombre>` | Uso de record type. |
| `<nombre>.<campo>` sobre un CDT | Uso de un campo de CDT. |
| `a!startProcess(processModel: ..., ...)` | Lanzamiento de process model desde SAIL. |
| `<processModel uuid="..."/>` dentro de otro process model | Subproceso. |
| `<connectedSystemRef>...</connectedSystemRef>` en integración | Vínculo integration → connected system. |
| Tabla `<jndi>` + nombre de tabla en data store | Vínculo data store → BBDD. |

Para extraer todas las referencias a expression rules de un proyecto:

```bash
grep -rohE 'rule![A-Za-z0-9_]+' <ruta> | sort -u
```

Para referencias a constants:

```bash
grep -rohE 'cons![A-Za-z0-9_]+' <ruta> | sort -u
```

Para referencias a record types:

```bash
grep -rohE 'recordType![A-Za-z0-9_]+' <ruta> | sort -u
```

Cruza estas listas con los objetos detectados en el inventario:

- **Referenciado pero no encontrado** → dependencia externa o falta de paquete (🔴 riesgo de deployment).
- **Encontrado pero no referenciado** → potencial huérfano (🟡 pendiente).

## Heurísticas de criticidad

Un objeto es **crítico** cuando cumple varios de estos criterios:

- Referenciado por >5 objetos distintos.
- Aparece en sites/portals como punto de entrada.
- Maneja decisiones de negocio importantes (process model con muchas ramas).
- Lee/escribe en tablas centrales del modelo de datos.
- Está conectado a integraciones externas.
- Tiene lógica de seguridad (permisos, validación de roles).
- Su naming sugiere centralidad (`*_Main_*`, `*_Master_*`, `*_Core_*`).

Marca estos objetos con criticidad **Alta** o **Crítica**. En modo `rebuild`, esa marca se refleja en la matriz de trazabilidad `10-especificacion/trazabilidad.md` (una fila por objeto del `inventory.json`, generada por `agents/backlog-writer.md`); en modo `onboarding`, en la tabla de criticidad de `02-arquitectura.md` o `09-valor-adicional.md`.

## Heurísticas de complejidad y deuda

Indicadores de deuda técnica en objetos individuales:

| Indicador | Cómo medirlo |
|---|---|
| Expression rule grande | Líneas del XML > 200; muchos `if`/`choose` anidados. |
| Interface grande | XML con >500 líneas o >30 componentes SAIL. |
| Process model complejo | >30 nodos, >5 gateways, anidamientos profundos de subprocesos. |
| Lógica de negocio en interface | Cálculos pesados con `a!localVariables` que deberían ser regla. |
| Hardcoding | Strings con URLs (`http://`, `https://`), emails, ids de grupo numéricos, valores tipo "PROD"/"DEV" en literal. |
| Duplicidad | Reglas con nombres parecidos (Levenshtein bajo) y XML similar. |
| Sin descripción | Objeto sin elemento de descripción o con descripción vacía. |
| Naming inconsistente | Mezcla de `camelCase`/`snake_case`/`PascalCase` en el mismo módulo. |

## Configuración por entorno (ICF)

Los `import-customization-file*.properties` siguen este formato:

```properties
# Constante por entorno
constant.<uuid_o_nombre>=<valor>

# Connected system credentials/URL por entorno
connectedSystem.<uuid_o_nombre>.<propiedad>=<valor>

# Otras propiedades de objetos
<tipo>.<id>.<propiedad>=<valor>
```

Procésalos para:

- Identificar qué cambia entre entornos.
- Detectar secretos (passwords, tokens, API keys) — ver `security-rules.md`.
- Listar URLs externas.

## Roles típicos en aplicaciones Appian

Para inferir actores cuando el grupo no lo aclara, busca naming típico:

| Grupo típico | Rol funcional |
|---|---|
| `*_Admin*`, `*_Admins*` | Administradores. |
| `*_Manager*` | Gestor / supervisor. |
| `*_Approver*` | Aprobador en flujos de aprobación. |
| `*_Viewer*`, `*_ReadOnly*` | Consulta sin edición. |
| `*_Initiator*`, `*_Requestor*` | Quien arranca un proceso. |
| `*_Operator*`, `*_User*` | Usuario operativo. |
| `All Users`, `Everyone`, `Public` | 🔴 Atención: posible exposición pública. |

Cuando un objeto está accesible por `Public` o por un grupo demasiado amplio, regístralo como riesgo de seguridad.

## Reportes y dashboards

En Appian moderno suelen estar como:

- **Sites** con páginas de dashboard.
- **Interfaces** que combinan `a!chartField`, `a!gridField`, `a!barChartField`.
- **Records** con record views configuradas como dashboards.

Detéctalos por uso intensivo de `chart`, `kpiField`, `grid` y por estar en sitios con nombres tipo `Dashboard`, `Report`, `Analytics`.

## Process HQ / Data Fabric

Si aparecen artefactos con nombres tipo `dataModel/`, `dataPipeline/`, `recordType` con `<dataFabricEnabled>true</dataFabricEnabled>`, márcalo como uso de Data Fabric / Process HQ y documenta:

- Qué records están en Data Fabric.
- Qué relaciones se han definido.
- Qué reportes se han generado.

## Cuándo marcar algo como "pendiente"

Marca como 🟡 pendiente de validación, no como confirmado, cuando:

- El XML del objeto está pero el objeto referenciado no.
- El objeto existe pero su propósito de negocio no es claro y no hay descripción.
- Hay configuración por entorno pero no se ve qué valores reales se usan en producción.
- Hay process models con start events que no parecen invocarse desde ningún lado visible (puede haber un trigger externo no exportado).
- Hay integraciones cuyo destino real (URL) está en ICF y no en el código.
- Hay grupos definidos pero sin miembros visibles.

Cada pendiente debe llevar **responsable sugerido** (funcional / técnico Appian / DBA / responsable del sistema externo).
