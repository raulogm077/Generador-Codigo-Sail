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
| **4.5 — Especificación (solo `profundidad: rebuild`)** | `parse_export.py --detail` → `_intermedio/detail.json`; luego `interface-spec-writer` + `logic-spec-writer` + `process-modeler` (2ª invocación) en paralelo y, al terminar, `backlog-writer`. Produce `10-especificacion/`. | Subagentes |
| **5 — Renderizar diagramas** | Mermaid → SVG con refinamiento iterativo. | Orquestador |
| **6 — Resumen ejecutivo** | `00-resumen-ejecutivo.md` (al final: depende del resto). | Orquestador |
| **6.5 — summary.json** | `build_summary.py` (siempre; lo consumen los publishers). | Orquestador |
| **7 — Publicación opcional** | `pdf-publisher` y/o `dashboard-publisher` según preferencias. | Subagentes |
| **8 — Respuesta final** | Plantilla literal de `response-format.md` + tabla de cobertura. | Orquestador |

**Cierre obligatorio de cualquier ejecución** — los dos gates deben salir 0:

```bash
python scripts/check_coverage.py    <salida> --mode {onboarding|rebuild}   # ¿está todo documentado?
python scripts/check_spec_layout.py <salida> --mode {onboarding|rebuild}   # ¿está bien formado?
```

## Convenciones de toda la salida

- **Patrón de evidencia**: `[ruta/fichero#fragmento]` o `[ruta/fichero:línea]`. Relativo a la raíz del export.
- **Estados**: ✅ Confirmado · 🔵 Inferido · 🟡 Pendiente · 🔴 Riesgo.
- **Nivel de confianza**: Alta / Media / Baja.
- **Carpeta de salida**: `<ruta_export>/_doc_generada/`.
- **Ficheros intermedios** (nombres exactos, en inglés): `inventory.json`, `graph.json`, `detail.json`, `coverage.json`, `summary.json`, `output_preferences.json`, `secretos.md`, `render_pendiente.txt`.

---

## FASE 0 — Elicitación

Antes de generar nada: preguntar formatos de salida y, si el objetivo huele a reconstrucción/migración, la **profundidad**. Guiones literales y reglas duras en `SKILL.md` § Fase 0. Sin respuesta explícita → solo Markdown y `profundidad: onboarding`. La elección se guarda en `_intermedio/output_preferences.json`.

---

## FASE 1 — Validar que la ruta es un export Appian

**Objetivo:** evitar empezar a documentar carpetas que no lo son.

1. **Método canónico**: `python scripts/parse_export.py --check <ruta>`. Reconoce el formato *Haul* real (carpetas en camelCase: `processModel/`, `recordType/`, `site/`, `content/`, `group/`, `connectedSystem/`, `datatype/`, `dataStore/`, `application/`) y el formato antiguo (`application.xml` en la raíz). También cuenta XSDs de CDTs e ICFs.
2. Si la entrada es un `.zip`, descomprime antes:
   ```bash
   command -v unzip >/dev/null && unzip -q -d <destino> <export>.zip
   ```
   Si `unzip` no está disponible, pide al usuario que lo descomprima manualmente.
3. Si `--check` no reconoce nada, **detén el flujo** y devuelve al usuario:
   > "La ruta `<ruta>` no parece un export Appian. No he encontrado `application.xml` ni las carpetas típicas (`processModel/`, `recordType/`, `content/`…). ¿Puedes confirmar que es la carpeta correcta o pasarme una ruta distinta?"
4. Si la validación pasa, crea la estructura de salida:
   ```bash
   mkdir -p <ruta>/_doc_generada/diagrams
   mkdir -p <ruta>/_doc_generada/08-procesos-bpmn
   ```

**Salida**: carpeta `_doc_generada/` lista, y la versión de Appian detectada de `application.xml` (atributo `@version` si aparece; si no, `⚠️ no determinado`).

---

## FASE 2 — Inventariar objetos por tipo

**Objetivo:** entender qué hay en el export antes de interpretar nada.

1. **Barrido bruto** con `scripts/inventory.sh <ruta>` (primer mapa de extensiones y carpetas; las cantidades son aproximadas).
2. **Inventariado estructurado**: `scripts/parse_export.py --inventory <ruta> --out <ruta>/_doc_generada/_intermedio/inventory.json`. Por objeto: `name` (técnico), `displayName` (visible), `uuid`, `path`, `description`, `updatedOn`/`updatedBy` si están, más metadatos por tipo (startType de PMs, method/endpoint de integraciones, fieldCount de records…).
3. **Barrido de secretos**: `bash scripts/detect_secrets.sh <ruta>` → guarda salida en `_intermedio/secretos.md`, que alimenta la sección de riesgos de `09-valor-adicional.md`.
4. **Detección de ICF**: lista todos los `import-customization-file*.properties` y guarda sus rutas.
5. **Detección de paquetes / módulos** por prefijo de naming dominante (`APP_Cliente_*`, `MOD_Pedido_*`). Esos prefijos suelen revelar los módulos lógicos de la app.
6. Cómo reconocer cada tipo de objeto en su XML: `references/appian-objects-guide.md`.

**Salida — `INVENTARIO.md`**: tabla por categoría (omite las categorías vacías) siguiendo `assets/markdown-templates/INVENTARIO.md`, que incluye además el conteo por tipo y el cruce de consistencia con `application.xml`.

**Regla:** el inventario es punto de partida, no resultado. No te quedes aquí.

---

## FASE 3 — Construir el grafo de dependencias

**Objetivo:** generar el grafo `objeto → objeto` que alimenta todas las fases siguientes. Lo produce `scripts/parse_export.py --graph`.

**Patrones de referencia** que se extraen de cada XML y de las expresiones SAIL embebidas:

| Patrón | Significa |
|---|---|
| `rule!<nombre>(` | Llama a expression rule, **interfaz o decision** (se desambigua contra el inventario) |
| `cons!<nombre>` | Usa constant |
| `recordType!<nombre>` / urn de record type | Usa record type |
| `a!startProcess(processModel: ` | Lanza process model |
| `<processModelUuid>` dentro de otro PM | Subproceso |
| `<connectedSystemRef>…</connectedSystemRef>` | Integration → Connected System |
| `a!queryEntity(entity: cons!<DS>)` | Query a data store |
| `a!queryRecordType(recordType: recordType!<RT>)` | Query a record |
| `a!writeToDataStoreEntity` / `a!writeRecords` | Escritura |
| `a!integrationCall(integration: ` | Llamada a integration |
| `a!isUserMemberOfGroup(…)` | Check de seguridad |

> 🔴 **Los patrones de arriba son la sintaxis del Designer, y un export real NO la contiene.** El XML trae la forma canónica: `#"_a-…uuid…"` en vez de `rule!`/`cons!`, `#"SYSTEM_SYSRULES_textField"` en vez de `a!textField`, y `#"urn:appian:record-field:v1:{rt}/{campo}"` para los campos. El parser resuelve las dos formas; **tú tienes que saber leer la canónica** antes de describir una pantalla — tabla de traducción en `appian-objects-guide.md`.

Y las **referencias estructurales**, que no viajan en SAIL sino en tags y atributos del XML — sin ellas el formulario principal de una app puede salir huérfano pese a estar en un site, en un start event y en una vista de record:

| Patrón | Significa |
|---|---|
| `<form>` / `<formRef>` en un nodo | Process model → interfaz (start form o formulario de tarea) |
| `<integrationRef>` en un nodo | Process model → integration |
| `<assignees>` / `<assignee>` | Tarea humana → grupo |
| `<view interface="…">` | Record type → interfaz (record view) |
| `<action process="…">` | Record type → process model (related action) |
| `<page objectUuid="…">` | Site → record type / interfaz que expone |
| `<visibilityGroup>` | Site → grupo con acceso |
| `<entity cdt="…">` | Data store → CDT |
| Constante de tipo *Data Store Entity* | Su valor `{dataStore}.{entidad}` la vincula a su data store |

Los tags XML se reconocen **con o sin prefijo de namespace** (`<a:processModelUuid>` también casa).

**Resolución de referencias** contra el inventario:
- Referenciado y existe → arista normal.
- Referenciado pero NO existe → dependencia faltante en el export, marcar 🔴.
- En el inventario pero NO referenciado por nadie → candidato a **huérfano**, marcar 🟡 para `09-valor-adicional.md`.

**Detección automática** (lo que `cmd_graph` calcula de verdad; si cambias los umbrales en el script, cámbialos aquí):
- **Subprocesos vs procesos raíz**: un PM es raíz si no es `target` de ninguna arista `startProcess` ni subproceso de otro PM.
- **Batches**: PM con start event `<recurrence>` o `<timerEvent>` (`hasRecurrence` en el inventario).
- **Objetos huérfanos**: nodos con grado entrante 0, excluyendo los tipos que son puntos de entrada por naturaleza (`application`, `site`, `webApi`, `portal`) y los process models con recurrencia.
- **Acoplamientos fuertes** (`hubs`): grado entrante **≥ 5** (`HUB_MIN_INDEGREE`). Cada hub trae también su grado saliente (`out`).
- **Ciclos** (`cycles`): componentes fuertemente conexas del subgrafo de **invocación** (`ruleRef`, `startProcess`, `subprocess`, `recordAction`, `form`). Las aristas de datos y estructura se excluyen a propósito: que un record type tenga como vista una interfaz que consulta ese mismo record es normal en Appian, no un ciclo.

**Cómo leer la salida**: `orphans` es la lista **completa**; `hubs` es un **top-30** por grado entrante, por diseño. Huérfano significa *"el parser no encontró quién lo llama"*, no *"nadie lo llama"* — antes de declarar muerto un objeto, cruza con un `grep` de su nombre en el export (ver `agents/backlog-writer.md`).

---

## FASE 4 — Entregables 01→09 vía subagentes

**El orquestador no escribe estos documentos**: los delega. Cada agente lleva su método, sus anti-patrones y su checklist; no los dupliques aquí.

| Documento | Quién lo escribe | Plantilla | Referencia de apoyo |
|---|---|---|---|
| `01-funcional.md`, `02-arquitectura.md` | `agents/interface-analyzer.md` | `assets/markdown-templates/01-*`, `02-*` | `mermaid-rules.md` |
| `03-modelo-datos.md` + ERs | `agents/data-modeler.md` | `03-modelo-datos.md` | `mermaid-rules.md` (Tipo B) |
| `04-seguridad-grupos.md`, `05-integraciones-consumidas.md`, `06-apis-expuestas.md` | `agents/integration-security-analyzer.md` | `04-*`, `05-*`, `06-*` | `security-rules.md` |
| `08-procesos-bpmn/*` | `agents/process-modeler.md` | `08-procesos-bpmn/pm-template.md`, `indice.md` | `bpmn-mapping.md` |
| `07-batches.md`, `09-valor-adicional.md` | **el orquestador** (agregaciones) | `07-batches.md`, `09-valor-adicional.md` | ver abajo |

Orden: **4.1** `interface-analyzer` primero (los demás lo citan) → **4.2** los otros tres en paralelo (un único turno con varias llamadas `Agent`) → **4.3** el orquestador agrega. Patrón de invocación en `SKILL.md` § Fase 4.

### 07-batches.md (lo escribe el orquestador)

Por cada process model con start event temporal/recurrente:
- Nombre, descripción, propósito funcional.
- **Frecuencia**: extraer `<recurrence>` del start event y traducirla a lenguaje humano ("todos los días a las 02:00") **y** a cron equivalente cuando aplique.
- **Próximas 3 ejecuciones** si es calculable desde la recurrencia.
- Procesos hijos que dispara (`a!startProcess` o nodos de subproceso).
- Data stores e integraciones que toca (del grafo).
- Volumetría esperada si es inferible: presencia de paginación (`a!queryEntity` con `pagingInfo`), `batchSize`.

### 09-valor-adicional.md (lo escribe el orquestador)

**Solo incluir secciones donde haya hallazgos reales**. Si no hay datos para una, **omítela**.

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

## FASE 4.5 — Especificación de reconstrucción (solo `profundidad: rebuild`)

Si `output_preferences.json` tiene `"depth": "onboarding"`, **salta esta fase entera**.

1. `python scripts/parse_export.py --detail <ruta> --out <salida>/_intermedio/detail.json`.
2. En paralelo: `interface-spec-writer` (pantallas + navegación, por lotes de ~10 interfaces), `logic-spec-writer` (reglas + decisions + constants + estados) y `process-modeler` en su 2ª invocación (fichas por nodo).
3. Al terminar los tres: `backlog-writer` (historias Gherkin + matriz de trazabilidad).

**Regla que invierte la del nivel onboarding**: aquí la jerga SAIL es **obligatoria** y los predicados se copian **exactos**. Los topes de longitud de `presentation-rules.md` **no aplican** a `10-especificacion/`: manda la exhaustividad (ver `execution-principles.md` § 11). Detalle de la orquestación en `SKILL.md` § Fase 4.5.

---

## FASE 5 — Renderizar diagramas

1. `scripts/render_diagrams.sh --check` para saber si hay `mmdc`.
2. **Iterative refinement, obligatorio**: cada bloque Mermaid pasa por `scripts/validate_mermaid.py` antes de escribirse. Si falla: refinar → re-validar, **máximo 3 iteraciones**. Tras la 3ª, sustituir por una **tabla equivalente** con la misma información.
3. `scripts/render_diagrams.sh --batch <salida>` convierte `.mmd` → `.svg`.
4. **Si `mmdc` no está disponible** (degradación elegante):
   - Deja el fichero fuente `.mmd` en su sitio.
   - Embebe el contenido también dentro del Markdown asociado (en bloque ` ```mermaid ` para que GitHub/VSCode lo rendericen al vuelo).
   - Registra en `_intermedio/render_pendiente.txt` qué quedó sin renderizar.
5. Los `.bpmn` **se entregan como XML tal cual**, no se renderizan aquí: el usuario los abre en Camunda Modeler, draw.io o demo.bpmn.io.

Tipos de diagrama y sus reglas (A: flowchart, B: erDiagram, C: lanes con subgraph): `references/mermaid-rules.md`.

---

## FASE 6 — Resumen ejecutivo

`00-resumen-ejecutivo.md`, ≤ 2 páginas, **se escribe al final** porque depende del resto. Criterios de selección:

1. Pitch de la aplicación (2-4 frases, sin jerga Appian).
2. Volumen por tipo de objeto.
3. **Procesos críticos**: top 3-5 por grado entrante en el grafo y por criticidad de negocio.
4. **Integraciones críticas**: top 3-5 (las que sostienen un flujo principal o tocan sistemas externos de negocio).
5. APIs expuestas y batches, con una línea cada uno.
6. **Riesgos top 5** de `09-valor-adicional.md`, con severidad.
7. Objetos huérfanos (top 5) y pendientes principales.
8. Nivel de confianza global, coherente con la tabla de cobertura de `coverage.json`.

---

## FASE 6.5 — Consolidar `summary.json`

`python scripts/build_summary.py <salida>` produce `_intermedio/summary.json` (inventario + grafo + métricas + hallazgos normalizados). **Siempre se genera**: es barato y lo consumen los publishers de la Fase 7.

---

## FASE 7 — Publicación opcional

Según `output_preferences.json`:
- `pdf: true` → `agents/pdf-publisher.md` → `EXPORT.pdf`.
- `dashboard: true` → `agents/dashboard-publisher.md` → `dashboard/index.html`.
- Ambos false → saltar.

Si se piden los dos, pueden ir **en paralelo**.

---

## FASE 8 — Respuesta final

Devolver al usuario la **plantilla literal de `references/response-format.md`**, sin saludos ni comentarios añadidos. Incluye la tabla de cobertura copiada de `_intermedio/coverage.json` (no se escribe a mano) y el resultado de ambos gates.

Antes de responder, completa el checklist de **Validación final** de `SKILL.md`: los dos gates en 0, secretos enmascarados, cero placeholders, y nada escrito fuera de `_doc_generada/`.
