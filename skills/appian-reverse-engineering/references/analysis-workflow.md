# Flujo operativo de análisis

Detalle operativo de las fases que orquesta `SKILL.md`, con checklists, patrones a buscar y salida esperada. Léelo al inicio del trabajo.

## Mapa de fases (el orden real que ejecuta el orquestador)

| Fase | Qué hace | Quién |
|---|---|---|
| **0 — Elicitación** | Preguntar formatos de salida (MD siempre; PDF/Dashboard opcionales) y **profundidad** (`onboarding` por defecto \| `rebuild`). Guardar en `_intermedio/output_preferences.json`. | Orquestador |
| **1 — Validar export** | Detectar formato Haul o antiguo. | Orquestador |
| **2 — Inventariar** | `INVENTARIO.md` + `_intermedio/inventory.json` + barrido de secretos. | Orquestador |
| **3 — Grafo** | `_intermedio/graph.json`. | Orquestador |
| **4 — Entregables 01→09** | 4.1 `interface-analyzer` (va primero); 4.2 `data-modeler` + `integration-security-analyzer` + `process-modeler` **en paralelo**; 4.3 el orquestador escribe `07-batches.md` y `09-valor-adicional.md`. | Subagentes de `agents/` |
| **4.5 — Especificación (solo `profundidad: rebuild`)** | `parse_export.py --detail` → `_intermedio/detail.json`; luego `interface-spec-writer` + `logic-spec-writer` en paralelo y, al terminar ambos, `backlog-writer`. Produce `10-especificacion/`. | Subagentes |
| **5 — Renderizar diagramas** | Mermaid → SVG con refinamiento iterativo. | Orquestador |
| **6 — Resumen ejecutivo** | `00-resumen-ejecutivo.md` (al final: depende del resto). | Orquestador |
| **6.5 — summary.json** | `build_summary.py` (siempre; lo consumen los publishers). | Orquestador |
| **7 — Publicación opcional** | `pdf-publisher` y/o `dashboard-publisher` según preferencias. | Subagentes |
| **8 — Respuesta final** | Plantilla literal de `response-format.md` + tabla de cobertura. | Orquestador |

**Cierre obligatorio de cualquier ejecución**: `python scripts/check_coverage.py <salida> --mode {onboarding\|rebuild}` debe salir 0. Si sale 1, documenta los objetos que faltan antes de cerrar.

## Convenciones de toda la salida

- **Patrón de evidencia**: `[ruta/fichero#fragmento]` o `[ruta/fichero:línea]`. Relativo a la raíz del export.
- **Estados**: ✅ Confirmado · 🔵 Inferido · 🟡 Pendiente · 🔴 Riesgo.
- **Nivel de confianza**: Alta / Media / Baja.
- **Carpeta de salida**: `<ruta_export>/_doc_generada/`.
- **Ficheros intermedios** (nombres exactos, en inglés): `inventory.json`, `graph.json`, `detail.json`, `coverage.json`, `summary.json`, `output_preferences.json`.

---

## FASE 1 — Validar que la ruta es un export Appian

**Objetivo:** evitar empezar a documentar carpetas que no lo son.

### Acciones

1. Verifica presencia de **al menos uno** de estos indicadores:
   - `application.xml` en la raíz o un nivel debajo.
   - Carpetas `process-model/`, `record-type/`, `cdt/`, `interface/`, `expression-rule/`, `integration/`, `web-api/`, `group/`, `connected-system/`, `data-store/`, `constant/`, `site/`, `decision/`.
   - Archivos con extensión `.bpmn` o XSDs en `cdt/`.
   - `import-customization-file*.properties` (ICF).
2. Si la entrada es un `.zip`, descomprime antes:
   ```bash
   command -v unzip >/dev/null && unzip -q -d <destino> <export>.zip
   ```
   Si `unzip` no está disponible, pide al usuario que lo descomprima manualmente.
3. Si **ninguno** de los indicadores aparece, **detén el flujo** y devuelve al usuario:
   > "La ruta `<ruta>` no parece un export Appian. No he encontrado `application.xml` ni carpetas típicas (`process-model/`, `record-type/`, `cdt/`…). ¿Puedes confirmar que es la carpeta correcta o pasarme una ruta distinta?"
4. Si la validación pasa, crea la carpeta de salida:
   ```bash
   mkdir -p <ruta>/_doc_generada/diagrams
   mkdir -p <ruta>/_doc_generada/08-procesos-bpmn
   ```

### Salida

- Carpeta `_doc_generada/` lista para llenar.
- Variable interna: versión de Appian detectada de `application.xml` (atributo `@version` si aparece). Si no aparece, queda en `⚠️ no determinado`.

---

## FASE 2 — Inventariar objetos por tipo

**Objetivo:** entender qué hay en el export antes de interpretar nada.

### Acciones

1. **Barrido bruto** con `scripts/inventory.sh <ruta>` para obtener un primer mapa de extensiones y carpetas.
2. **Detección de objetos por contenido** — patrones de identificación en `references/appian-objects-guide.md` (tabla "Reconocimiento por XML"). Recorre TODOS los XML del export.
3. **Inventariado estructurado** con `scripts/parse_export.py --inventory <ruta> --out <ruta>/_doc_generada/_intermedio/inventory.json`. Produce JSON con, por tipo de objeto:
   - `name` (técnico)
   - `displayName` (visible)
   - `uuid` (si está)
   - `path` (relativo al export)
   - `description` (si está)
   - `updatedOn` / `updatedBy` (si están)
4. **Barrido de secretos** con `bash scripts/detect_secrets.sh <ruta>` — guarda salida en `_doc_generada/_intermedio/secretos.md` para alimentar Fase 4 (sección de seguridad y riesgos en `09-valor-adicional.md`).
5. **Detección de ICF**: lista todos los `import-customization-file*.properties` y guarda paths.
6. **Detección de paquetes / módulos** por prefijo de naming dominante. Ejemplos: `APP_Cliente_*`, `MOD_Pedido_*`. Estos prefijos suelen revelar módulos lógicos.

### Salida — `INVENTARIO.md`

Tabla por categoría, en este orden (omite las categorías con cero objetos):

```markdown
## Records
| Nombre técnico | Nombre visible | Ruta | UUID | Descripción | Actualizado | Confianza |
|---|---|---|---|---|---|---|

## CDTs
| Namespace | Nombre | Ruta XSD | Mapeo JPA | Campos | Confianza |

## Process Models
| Nombre técnico | Nombre visible | Ruta | UUID | Trigger | Confianza |

## Interfaces · Expression Rules · Decisions · Integrations · Connected Systems · Web APIs · Groups · Sites · Constants · Data Stores · Documents · Folders · Plugins
... (misma estructura)
```

**Regla:** el inventario es punto de partida, no resultado. No te quedes aquí.

---

## FASE 3 — Construir el grafo de dependencias

**Objetivo:** generar el grafo `objeto → objeto` que alimenta todas las fases siguientes.

### Acciones

1. **Extraer referencias salientes** de cada objeto recorriendo su XML y las expresiones SAIL embebidas. Patrones a buscar en cada fichero:

   | Patrón | Significa |
   |---|---|
   | `rule!<nombre>(` | Llama a expression rule |
   | `cons!<nombre>` | Usa constant |
   | `recordType!<nombre>` | Usa record type |
   | `a!startProcess(processModel: ` | Lanza process model |
   | `<processModel uuid="..."/>` dentro de otro PM | Subproceso |
   | `<connectedSystemRef>...</connectedSystemRef>` | Integration → Connected System |
   | `<dataStore>` referenciado | Process / record → Data Store |
   | `a!queryEntity(entity: cons!<DS>)` | Query a data store |
   | `a!queryRecordType(recordType: recordType!<RT>)` | Query a record |
   | `a!writeToDataStoreEntity` / `a!writeRecords` | Escritura |
   | `a!integrationCall(integration: ` | Llamada a integration |
   | `a!isUserMemberOfGroup(group: cons!<GROUP>)` | Check de seguridad |

2. **Resolver referencias** contra el inventario:
   - Referenciado y existe → arista normal.
   - Referenciado pero NO existe en el inventario → arista a "externa" + marcar 🔴 (dependencia faltante en el export).
   - En el inventario pero NO referenciado por nadie → candidato a **huérfano**, marcar 🟡 para Fase 4 (`09-valor-adicional.md`).

3. **Salida intermedia**: `_doc_generada/_intermedio/graph.json` con `nodes` (objetos) y `edges` (`{from, to, type, evidence}`). Lo produce `scripts/parse_export.py --graph`.

4. **Detección automática de**:
   - **Subprocesos vs procesos raíz**: un PM es raíz si no aparece como `target` de ninguna arista `a!startProcess` y no es subprocess de otro PM.
   - **Process models que son batches**: PM con start event `<recurrence>` o `<timerEvent>`.
   - **Objetos huérfanos**: nodos sin aristas entrantes (excepto puntos de entrada conocidos: Sites, Web APIs, batches).
   - **Acoplamientos fuertes**: nodos con grado entrante o saliente >10.
   - **Ciclos**: ciclos en el grafo de invocación entre process models.

### Salida

- `_intermedio/graph.json` (consumido por las fases siguientes; no es entregable final).
- Lista de candidatos a huérfanos.
- Lista de acoplamientos fuertes y ciclos detectados.

---

## FASE 4 — Generar las secciones 5.1 → 5.9

**Objetivo:** producir los entregables Markdown poblados con datos reales y evidencia.

Orden de generación. Cada uno copia su plantilla base de `assets/markdown-templates/` y la rellena.

### 4.1 — `01-funcional.md` (Explicación funcional)

Lenguaje de negocio, sin jerga Appian. **Tres niveles obligatorios**:

1. **Pitch** (1 párrafo): qué problema resuelve. Inferir de:
   - `application.xml` → `<description>`.
   - Nombre y descripción de records principales.
   - Nombre del módulo principal.
2. **Overview** (≈1 página): procesos funcionales principales y actores. Inferir de:
   - Sites y sus páginas (entrada de usuario).
   - Process models raíz.
   - Grupos definidos = actores.
3. **Detalle por flujo funcional**: para cada caso de uso identificado, paso a paso. Inferir combinando:
   - Site / record action que lo dispara.
   - User input tasks del process model que lo ejecuta.
   - Decisiones (gateways) que marcan ramas.
   - End events que marcan resultado.
   - Notificaciones (emails) emitidas.

Cada caso de uso debe citar los objetos Appian que lo implementan. Estado por afirmación.

### 4.2 — `02-arquitectura.md` (Arquitectura de esta app)

> No documentar la arquitectura genérica de Appian. Centrarse en los objetos reales nombrados y sus relaciones.

1. **Diagrama Mermaid `flowchart`** con nodos = objetos reales y aristas = relaciones de uso, agrupados en capas:
   - **Presentación:** Sites, Pages, Interfaces, Record Views.
   - **Lógica:** Process Models, Expression Rules, Decisions.
   - **Datos:** Record Types, CDTs, Data Stores, tablas.
   - **Integración:** Connected Systems, Integrations, Web APIs.
2. Las aristas se extraen del grafo de la Fase 3.
3. Si el diagrama tiene >30 nodos, divídelo en sub-diagramas por capa o por módulo lógico (usa los prefijos de naming).
4. Pasa cada diagrama por `scripts/validate_mermaid.py` antes de escribirlo. Si no pasa, sustituye por tabla.
5. Render: escribe el `.mmd` en `_doc_generada/diagrams/arquitectura.mmd` y renderiza a SVG en Fase 5.

### 4.3 — `03-modelo-datos.md` (Modelo de datos)

1. **Diagrama ER en Mermaid `erDiagram`** con Record Types, CDTs y sus relaciones:
   - FKs declaradas en XSD (`<xsd:keyref>`).
   - Joins en record types (`<recordRelationship>`).
   - Related records.
2. **Por cada Record Type**:
   | Campo | Tipo | Origen | Nullable | PK/FK | Visible en vista | Filtro |
3. **Por cada Record Type — metadata**: nombre técnico, nombre visible, fuente (`<source>`: DB / servicio / proceso / expresión), CDT asociado, **record views** y campos mostrados, **related actions** (con su process model destino), filtros por defecto, campos clave.
4. **Por cada CDT**: lista de campos con tipo, si está mapeado a tabla (anotaciones JPA `@Table` / `@Column` / `@OneToMany` en el XSD), namespace, dónde se usa (records / process variables / interfaces).

### 4.4 — `04-seguridad-grupos.md` (Seguridad)

1. **Árbol jerárquico** de groups (`<group>` con `<parentGroup>` y `<memberGroups>`). Renderiza como lista anidada Markdown o Mermaid `flowchart TD`.
2. **Tabla por objeto sensible** (Sites, Interfaces, Process Models, Records, Folders, Web APIs):
   | Objeto | Tipo | Viewer | Editor | Administrator | Initiator | Deny |
3. **Matriz RACI** simplificada: filas = grupos, columnas = capacidades funcionales identificadas en la Fase 4.1 (ver dashboard X, iniciar proceso Y, administrar record Z).
4. **Reglas de seguridad embebidas** detectadas en SAIL — recorrer expression rules e interfaces buscando:
   - `a!isUserMemberOfGroup(group: cons!<GROUP>)`.
   - `loggedInUserHasRole(...)`.
   - Visibilidad condicional (`showWhen: a!isUserMemberOfGroup(...)`).
   - Asignaciones dinámicas de tarea (`assignTo: cons!<GROUP>` o expresión).
   Cada hallazgo cita ruta del fichero origen.

### 4.5 — `05-integraciones-consumidas.md`

Por cada **Integration** y **Connected System**:

- Nombre técnico y nombre visible.
- Sistema externo y propósito (inferido del nombre, descripción y URL base).
- Tipo de Connected System (HTTP, OAuth 2.0, Salesforce, SAP, JDBC, plugin custom).
- **Endpoint** completo (base URL del Connected System + path del Integration) + método HTTP.
- Parámetros de path / query / headers.
- **Estructura del request body** (extraída del `<requestBody>`).
- **Autenticación** — enmascarar valores: Basic / OAuth client credentials / API key header / token referenciado por constant. Si la auth viene de ICF y el ICF está vacío, anotarlo como `⚠️ no determinado`.
- **Estructura del response / output mapping**.
- **Quién la invoca** (calle del grafo): process models / expression rules / interfaces que la usan.

### 4.6 — `06-apis-expuestas.md`

Por cada **Web API**:

- URL pública: `/suite/webapi/<endpointPath>` + método HTTP.
- Autenticación requerida (Basic, API key, autenticación por grupo).
- Parámetros de query / path / header.
- **Body de petición esperado** (estructura + ejemplo si es deducible del `<expression>`).
- **Qué hace al invocarse**: extraer del `<expression>` los `a!startProcess`, `rule!`, `a!writeToDataStoreEntity` que ejecuta. Resumir como flujo.
- **Respuesta**: estructura del return + códigos HTTP (200 / 4xx / 5xx) que puede emitir.
- **Grupos autorizados** (rolemap) y caso de uso funcional asociado.

### 4.7 — `07-batches.md`

Por cada process model con start event temporal/recurrente:

- Nombre, descripción, propósito funcional.
- **Frecuencia**: extraer `<recurrence>` del start event. Traducir a:
  - Lenguaje humano: "todos los días a las 02:00", "cada lunes a las 09:00".
  - Cron equivalente cuando aplique.
- **Próximas N ejecuciones** humanas (N=5) si es calculable desde la recurrencia.
- Procesos hijos que dispara (`a!startProcess` o sub-process nodes).
- Data stores e integraciones que toca (del grafo).
- Volumetría esperada si es inferible: presencia de paginación (`a!queryEntity` con `pagingInfo`), `batchSize`.

### 4.8 — `08-procesos-bpmn/`

> Traducir el dibujo nativo de Appian a **BPMN 2.0 estándar**. Ver `references/bpmn-mapping.md` para mapeo completo, plantillas y estrategia de render.

Por cada process model del inventario:

1. Lee `<pm:node>` con `type` y `acProperties`.
2. Lee flujos en `<pm:flow source="..." target="..."/>`.
3. Detecta lanes (actores) y pools (sistemas externos) — ver `bpmn-mapping.md`.
4. Aplica la tabla de mapeo Appian → BPMN 2.0.
5. Decide estrategia de render por complejidad (Mermaid simple / Mermaid con prefijos lane / BPMN XML).
6. Escribe `_doc_generada/08-procesos-bpmn/<PM_NOMBRE>.mmd` o `.bpmn`.
7. Render a SVG en Fase 5.

**Índice obligatorio** `08-procesos-bpmn/indice.md` con tabla por PM:

| Process Model | Trigger | Actores (lanes) | Sistemas externos (pools) | Subprocesos invocados | Integraciones que llama | Data Stores que toca | Padre (quién lo invoca) | Diagrama |

Más una **vista de grafo de procesos** (Mermaid `flowchart LR`) con las relaciones padre-hijo-hermano entre todos los process models.

### 4.9 — `09-valor-adicional.md`

**Solo incluir secciones donde haya hallazgos reales**. Para cada una, si no hay datos, **omítela**.

| Sección | Cómo extraerla |
|---|---|
| Constantes y configuración por entorno | Cruzar `<constant>` con ICFs. Detectar prefijos DEV/PRE/PRO en nombres. |
| Catálogo de expression rules de negocio reutilizables | Reglas con grado entrante alto en el grafo. Listar propósito + inputs/outputs + callers top. |
| Decision tables | Por cada `<decision>` o `<decisionTable>`, interpretar reglas en lenguaje natural. |
| Sites y páginas | Por cada `<site>`: qué muestra cada page, a qué record/interfaz apunta, dispositivos, grupos con acceso. |
| Plugins / smart services personalizados | Detectar referencias a smart services no nativos (no en la lista oficial de Appian). |
| Document templates / Knowledge Centers / Folders | Inventario y propósito. |
| Tareas humanas | Inventario de user input tasks: asignación, SLA, escalation. |
| Emails / notificaciones | Smart services Send Email: asunto, plantilla, gatillo, destinatarios. |
| Manejo de errores | Exception flows, alert nodes, retry en integraciones. |
| Mapa de dependencias | Acoplamientos fuertes y ciclos detectados en Fase 3. |
| Objetos huérfanos | Sin aristas entrantes y sin ser punto de entrada. Input directo para limpieza. |
| Glosario de negocio | Extraído de nombres y descripciones de records / CDT / campos. |
| Métricas de la app | Nº objetos por tipo, líneas SAIL, complejidad ciclomática estimada de procesos. |
| Riesgos / code smells | URLs/IDs hardcodeados, expresiones SAIL >200 líneas, queries sin paginación, integraciones sin manejo de error, grupos sin miembros, objetos sin seguridad explícita, `loggedInUser()` en batches. |
| Versionado | `@updatedOn` / `@updatedBy` por objeto si están. |
| Internacionalización | Idiomas presentes en propiedades de interfaces / records. |

---

## FASE 5 — Renderizar diagramas

**Objetivo:** convertir `.mmd` y `.bpmn` en `.svg` para que el lector los vea inline en GitHub / VSCode / preview Markdown.

### Acciones

Llama a `bash scripts/render_diagrams.sh --batch <ruta>/_doc_generada/`. El script:

1. Detecta `mmdc` (mermaid-cli) → renderiza todos los `.mmd` (Tipos A/B/C) a `.svg`.
2. Los `.bpmn` XML se **entregan tal cual** — son fuente abrible en Camunda Modeler, draw.io o demo.bpmn.io, que calculan el layout automáticamente y muestran iconos BPMN auténticos.
3. Si falta `mmdc`:
   - Deja el fichero fuente `.mmd` en su sitio.
   - Embebe el contenido también dentro del Markdown asociado (en bloque ` ```mermaid` para que GitHub/VSCode rendericen on-the-fly).
   - Registra en `_intermedio/render_pendiente.txt` qué quedó sin renderizar.

### Salida

- `_doc_generada/diagrams/arquitectura.svg` (+ `.mmd`)
- `_doc_generada/diagrams/modelo-datos.svg` (+ `.mmd`)
- `_doc_generada/08-procesos-bpmn/<PM>.svg` para cada PM
- `_intermedio/render_pendiente.txt` con los pendientes.

---

## FASE 6 — Resumen ejecutivo

**Objetivo:** sintetizar los hallazgos en `00-resumen-ejecutivo.md` para que un manager lo lea en 5 minutos.

Se hace **al final** porque depende del resto.

### Contenido (≤ 2 páginas)

1. **Propósito de la aplicación** (1 párrafo, del Pitch del §4.1).
2. **Volumen**: nº de objetos por tipo (tabla compacta).
3. **Procesos críticos** (top 3-5): los process models con mayor grado entrante + los que tocan integraciones críticas.
4. **Integraciones críticas** (top 3-5): las más invocadas + las que mueven más datos.
5. **Riesgos top** (top 5-10) con criticidad: secretos expuestos, exposición pública indebida, integraciones sin manejo de error, objetos huérfanos en gran cantidad.
6. **Pendientes de validación top** (top 5): qué hay que clarificar con el responsable funcional para cerrar la documentación.
7. **Nivel de confianza global**: Alto / Medio / Bajo + justificación.
8. **Próximos pasos recomendados** (3 puntos accionables).

---

## FASE 7 — Devolver el índice al usuario

Devuelve la respuesta final con el formato exacto descrito en la sección "Formato de la respuesta final al usuario" del `SKILL.md`. No improvises.

Antes de cerrar, pasa por el checklist de "Validación final" del `SKILL.md`. Si falla alguno, corrige y vuelve a validar.
