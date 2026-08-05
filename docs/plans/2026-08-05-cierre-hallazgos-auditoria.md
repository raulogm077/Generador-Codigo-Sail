# Cierre de los 9 hallazgos abiertos de la auditoría — `appian-reverse-engineering`

## Context

Tras implementar el modo `rebuild` del skill de reingeniería inversa (v2.5.0), una **auditoría adversaria** encontró 4 bloqueantes con los 43 tests en verde. Los 4 se cerraron, pero quedaron **9 hallazgos abiertos** (6 "importantes", 3 "menores" con impacto real). Un segundo diagnóstico los ha verificado uno a uno en disco.

El patrón de fondo es siempre el mismo: **evidencia buscada sobre un blob concatenado**, y **documentación que promete lo que el código no hace**. El objetivo de este plan es eliminar ambos, dejando el skill sin contratos rotos y con tests que fallarían si alguien los rompe.

Decisiones de alcance tomadas por el usuario:
1. **Máximo rigor en el gate**: en modo `rebuild`, constantes y sites también exigen **ficha propia** (hoy bastaba una mención). Esto cierra además un hueco real: nadie documenta hoy la navegación de la app.
2. **Reescribir** el cuerpo de `analysis-workflow.md` (solo el 9% está sano; 147 líneas duplican de forma desfasada a los agentes).
3. **Añadir `check_spec_layout.py`**: los invariantes de estructura se validan también sobre salidas reales, no solo sobre el fixture.

**Estado de partida**: 43 tests OK, working tree limpio, repo `appian-toolkit` rama `main`, último commit `75dac24`, publicado en github.com/raulogm077/Appian-Toolkit.

**Hallazgo habilitador**: ningún test existente asserta counts de nodos, aristas ni objetos — el fixture puede crecer sin romper nada.

---

## Ficheros críticos

| Fichero | Papel en este plan |
|---|---|
| `skills/appian-reverse-engineering/scripts/parse_export.py` | M4 (`_sail_references`), M5 (`orphans[:50]`), M6 (regex sin namespace), extracción de sites en `--detail` |
| `skills/appian-reverse-engineering/scripts/check_coverage.py` | I2 (`SHEET_REQUIRED`) |
| `skills/appian-reverse-engineering/scripts/check_spec_layout.py` | **Nuevo** — gate de estructura en runtime |
| `skills/appian-reverse-engineering/references/analysis-workflow.md` | I3 — reescritura de `:33-347` |
| `tests/fixtures/mini-export/` | I5 — 3 objetos nuevos que hospedan los patrones sin cobertura |
| `tests/fixtures/expected-output/` | I4 — layout correcto + fichas que faltan |
| `tests/test_expected_output.py` | **Nuevo** — test de contrato |
| `skills/appian-reverse-engineering/agents/{interface,logic}-spec-writer.md` | I2 — nuevos entregables (navegación, constantes) |

---

## Commits (8, suite verde en cada uno)

### C1 · M4 — `referencedRules` mezcla interfaces, y `--detail` no ve los sites

`_sail_references` (`parse_export.py:676-688`) aplica `rule!([A-Za-z0-9_]+)` sin filtrar por tipo. En Appian **las interfaces también se invocan con `rule!`**, así que `DEMO_IFC_SolicitudList` acaba en `referencedRules` y `interface-spec-writer.md:60` manda enlazarla a `reglas-catalogo.md`, donde nunca tendrá ficha → enlace muerto.

- Reutilizar la desambiguación que **ya existe** en `cmd_graph` (`:541-550`: expressionRule → interface → decision) construyendo `type_by_name` desde el inventario.
- Devolver 4 buckets: `referencedRules`, `referencedInterfaces`, `referencedDecisions`, `referencedUnresolved`. El último es obligatorio: sin él, las referencias a objetos no exportados desaparecerían en silencio (regresión encubierta).
- Añadir `sites` a `--detail` (páginas: nombre, tipo, objeto destino, grupos) — lo necesita la ficha de navegación de C5, y sin datos el agente se lo inventaría.
- Propagar a `interface-spec-writer.md` (3 destinos de enlace distintos), `logic-spec-writer.md` y `pantalla-template.md`.

Tests (+4 en `test_detail.py`): interfaces excluidas de `referencedRules`, capturadas en `referencedInterfaces`, las 4 claves siempre presentes, `sites` con sus páginas.

### C2 · M5 + M6 — huérfanos truncados y tags con namespace

- `parse_export.py:627`: quitar `orphans[:50]`. `backlog-writer.md:81` usa esa lista como evidencia de "objeto muerto" para justificar `DESCARTADO`; truncada, afirma muerte sobre datos incompletos. `hubs[:30]` se mantiene (es un top-N deliberado) pero se documenta como tal.
- `parse_export.py:489,491`: aceptar prefijo de namespace (`<a:processModelUuid>`), alineando con el `strip_ns()` que usa el resto del script. Los exports Haul reales lo llevan; el fixture actual no, así que el test verde no distingue el caso.
- `backlog-writer.md`: la lista es completa → añadir contraste `len(orphans) == stats.orphanCount`.

**Debe ir antes de C3**: sin el fix de namespace, el process model nuevo del fixture no generaría aristas.

Tests (+3 en `test_graph.py`): los dos patrones con prefijo, y `orphans` sin truncar (inventario sintético de 60 objetos, sin tocar disco).

### C3 · I5 + M9 — ejemplares reales de los 5 patrones sin cobertura

`TestNewRefPatterns` (`test_graph.py:69-110`) valida regex contra strings literales: **no comprueba que se cree ninguna arista**. Si alguien borra el cableado de `cmd_graph`, los 5 tests siguen verdes. Solo `connectedSystemRef` tiene ejemplar real en el fixture.

**Decisión: objetos nuevos, no enriquecer los existentes** — `test_detail.py` indexa nodos por id (`n2`, `n3`) del PM actual; tocarlo es riesgo gratis. Y `<processModelUuid>` (subproceso) exige por definición un segundo process model.

Tres ficheros nuevos en `tests/fixtures/mini-export/`:
- `content/DEMO_CONS_ENTITY_SOLICITUD.xml` — constant de tipo Data Store Entity. Obligatoria: `queryEntity`/`writeEntity` resuelven contra `name_index[("constant", X)]`.
- `processModel/DEMO_PM_ReintentarEnvios.xml` — batch nocturno **con namespace declarado**, que hospeda 4 patrones: `a!queryEntity`, `a!isUserMemberOfGroup`, `<a:processModelUuid>` (subproceso a `DEMO_PM_AprobarSolicitud`), `a!writeToDataStoreEntity` y `a!writeRecords`.
- `site/DEMO_SITE_Solicitudes.xml` — 2 páginas (una `RECORD_LIST`, una `INTERFACE`). Ahora **obligatorio**: sin site en el fixture no se puede probar la ficha de navegación de C5. Hoy `siteHaul` tiene 0% de cobertura.

Dos trampas a evitar (fallo silencioso): el prefijo `a:` **debe** llevar su `xmlns:a` declarado en la raíz, o `ET.parse` falla y el objeto desaparece del inventario sin error visible; y `<a:recurrence>` debe llevar texto, no solo hijos, o `hasRecurrence` no se activa. Assert explícito `parseErrors == 0`.

Efecto: 15 → 18 nodos, 7 → ~14 aristas, 8 → ~7 huérfanos. `test_called_interface_not_orphan` sigue verde.

Tests (+8): una arista e2e por patrón, PM raíz que deja de ser huérfano, batch con `startType: timer`, site inventariado con `pageCount`.

**M9** va aquí (los counts solo son definitivos ahora): `tests/README.md:5` "13 objetos" → 18; `:20` borrar la nota obsoleta de que el data store no se inventaría (`test_detail.py:51-60` asserta lo contrario).

### C4 · M7 — anidar las fichas del catálogo

`reglas-catalogo-template.md:20,31`: `## rule!{{nombre}}` y `## decision!{{nombre}}` están al mismo nivel que sus contenedores `## Expression rules` y `## Decisions`, así que no anidan. Pasan a `###`.

`has_own_sheet` (`check_coverage.py:173`) acepta cualquier línea que empiece por `#`, así que **no hay que tocar el gate** — pero sí blindarlo con un test, porque nada impide que alguien "optimice" ese `startswith` a `## `. Las anclas de GitHub no cambian con el nivel, así que los enlaces existentes siguen resolviendo.

Tests (+1): ficha con cabecera `###` cuenta como ficha propia.

### C5 · I2 — ficha propia también para constantes y sites (decisión del usuario)

Hoy `SHEET_REQUIRED = ("interface","expressionRule","decision")` y constantes/sites se cubren con una mención en `spec_blob` — la misma trampa que ya se corrigió para los demás. Además **cero tests** los ejercitan.

- `check_coverage.py`: `SHEET_REQUIRED = REBUILD_EXTRA` (los cinco tipos exigen ficha).
- **Dónde vive cada ficha** (decisión de diseño, para que el rigor no genere fichas de relleno):
  - **Constantes** → nueva sección `## Constantes` en `reglas-catalogo.md`, con `### cons!NOMBRE` por cada una: tipo, valor (enmascarado si es secreto), callers desde el grafo, y para qué sirve (si es un dominio de valores, enlace a `estados.md`). Dueño: `logic-spec-writer` (ya produce ese fichero).
  - **Sites** → nuevo `10-especificacion/navegacion.md` con `## site!NOMBRE` por cada site: páginas (nombre, tipo, objeto destino), grupos con visibilidad, página por defecto. Dueño: `interface-spec-writer` (ya conoce las pantallas y sus callers). Nueva plantilla `navegacion-template.md`.
- Actualizar `SKILL.md` (árbol de salida de la Fase 4.5 y mapa de subagentes) y los checklists de ambos agentes.

Tests (+7 en `test_coverage.py`), incluidos los dos discriminantes: una constante citada **solo** en los documentos 00-09 no basta; un site sin ficha da exit 1.

### C6 · I4 + M8 — expected-output con layout correcto y test de contrato

`tests/fixtures/expected-output/` son 7 ficheros que **ningún test consume** (0 referencias en todo el repo) y que ya contradicen 3 contratos: `pantallas/` cuelga de la raíz en vez de `10-especificacion/` (lo que rompe sus enlaces `../reglas-catalogo.md`), falta `procesos/` pese a que su propia `trazabilidad.md:21,23` la referencia, y `indice.md:9` cita `DEMO_RT_Solicitud` (nombre de **fichero**) cuando el nombre técnico real es `DEMO Solicitud`.

- `git mv pantallas/ 10-especificacion/pantallas/` — con eso los enlaces `../` resuelven solos, sin editarlos.
- Crear `10-especificacion/procesos/{PM}-nodos.md` (2, siguiendo `pm-nodos-template.md`), `navegacion.md` y la sección de constantes (C5).
- Corregir los nombres técnicos (M8) y actualizar `trazabilidad.md` a 18/18.

**Test de contrato — `tests/test_expected_output.py`** (decisión: cero comparación byte-a-byte; la salida de un LLM varía). Copia a un tmpdir, ejecuta el parser del fixture y valida invariantes:

1. **Ancla**: `check_coverage.py --mode rebuild` sale 0. Esto detecta el bug de layout **por construcción** (con `pantallas/` en la raíz, `in_spec_dir()` da `False` y las interfaces salen en `missing`).
2. No hay `pantallas/` ni `procesos/` en la raíz; sí bajo `10-especificacion/`.
3. **Enlaces**: todo link relativo resuelve a fichero existente.
4. **Anclas**: todo `#fragmento` interno existe como heading slugificado.
5. **Cobertura cruzada con el inventario**: una ficha por interfaz, una `{PM}-nodos.md` por process model, un `### rule!X` por regla.
6. **Trazabilidad ↔ inventario**: nombres de la 1ª columna == nombres del inventario; `**Cobertura**: N/N` coincide.
7. **Alias prohibidos** (M8 en forma genérica): para todo objeto cuyo `stem` de fichero ≠ `name`, ese stem no aparece entrecomillado como si fuera un nombre de objeto. Se calcula del inventario, no se hardcodea.
8. **Plantilla e higiene**: las secciones obligatorias de `pantalla-template.md`, ≥1 criterio `- [ ]`, cero `{{`/`TODO`/`xxx`.

Añadir `_doc_generada/` al `.gitignore`: hoy `test_graph`/`test_detail` la crean dentro del fixture y solo la borran en `tearDownClass` — un crash deja el repo sucio.

### C7 · `check_spec_layout.py` — el gate de estructura en runtime (decisión del usuario)

Los invariantes 2, 3, 4 y 8 de C6 protegen el fixture, pero la salida real de una ejecución no los pasa por ningún sitio. Extraerlos a un script que el orquestador ejecute en la validación final, junto a `check_coverage.py`:

```bash
python scripts/check_spec_layout.py {salida} --mode rebuild
```

Comprueba: layout de `10-especificacion/`, enlaces y anclas rotos, secciones obligatorias por tipo de ficha, placeholders sin rellenar. Exit 1 con lista de problemas. Solo stdlib.

Cablearlo en `SKILL.md` (Validación final) y en `response-format.md`. Tests propios (+6) con casos positivos y negativos por invariante.

### C8 · I3 — reescritura de `analysis-workflow.md`

Se conserva `:1-31` (mapa de fases, ya sano) y se reescribe `:33-347` → **~160 líneas**.

**Primero rescatar** (~70 líneas de contenido único, verificado que no está en ningún otro fichero), **después** reescribir:

| Rescate | De | Por qué es único |
|---|---|---|
| Tabla de las 16 secciones de `09-valor-adicional.md` con la columna "cómo extraerla" | `:275-296` | **Crítico**: ese documento lo escribe el orquestador, no hay agente, y la plantilla solo tiene los títulos |
| Tabla de 12 patrones de referencia SAIL/XML | `:112-127` | `appian-objects-guide.md` solo tiene 8 |
| Heurísticas de detección automática (raíz vs subproceso, batch, huérfano, acoplamiento, ciclos) | `:136-141` | No están en ningún sitio |
| Guía de extracción de batches | `:242-253` | Alinear "próximas N=5" → **3** (`07-batches.md:30`) |
| Descompresión, mensaje literal de rechazo, `mkdir -p` de la salida | `:44-55` | — |
| Campos de `inventory.json`, `_intermedio/secretos.md`, módulos por prefijo | `:74-81` | — |
| Fallback triple sin `mmdc` | `:311-313` | — |
| Metadata de Record Type y anotaciones JPA · auth desde ICF vacío · columnas del `indice.md` · versión desde `@version` | `:200-201`, `:226`, `:271-273`, `:60` | Van como **micro-ediciones a sus ficheros destino** (`data-modeler.md`, `integration-security-analyzer.md`, plantilla del índice) |

**Estructura destino**: una sección por fase real (0, 1, 2, 3, 4, 4.5, 5, 6, 6.5, 7, 8). La FASE 4 pasa de 147 líneas duplicadas a ~20 (tabla documento → agente → plantilla + patrón `Agent({...})`), porque hoy **no menciona los subagentes ni una vez** y está escrita en imperativo para un ejecutor único, contradiciendo `SKILL.md:39-88`.

Correcciones incluidas: carpetas Haul en camelCase (hoy lista el formato antiguo `process-model/`), `parse_export.py --check` como método canónico, Iterative Refinement de la Fase 5 (hoy perdido), puntero roto `:345` → `references/response-format.md`, y eliminación de la numeración fósil "5.1 → 5.9".

---

## Riesgos y orden

| Riesgo | Mitigación |
|---|---|
| Prefijo `a:` sin `xmlns:a` → el PM desaparece del inventario **en silencio** | Namespace declarado + assert `parseErrors == 0` |
| El fixture namespaced llega antes que el fix de regex | **C2 antes que C3** (dependencia dura) |
| Filtrar `referencedRules` hace desaparecer referencias no resueltas | Bucket `referencedUnresolved` |
| `expected-output` reescrito dos veces | **C3 y C4 antes que C6** |
| Alguien "optimiza" `has_own_sheet` a `## ` | Test con `###` que lo fija |
| El rigor de C5 genera fichas de relleno | Constantes y sites tienen ubicación natural definida (catálogo / navegación), no fichero por objeto |
| I3 borra bloques únicos antes de rescatarlos | El commit hace **primero** las micro-ediciones de destino; la grep-checklist verifica que nada se perdió |
| **Modo onboarding roto** | Ninguna tarea toca `ONBOARDING_REQUIRED` ni los agentes de Fase 4; el fixture solo crece |

Progresión: 43 → 47 (C1) → 50 (C2) → 58 (C3) → 59 (C4) → 66 (C5) → ~76 (C6) → ~82 (C7) → ~82 (C8).

---

## Verificación

**En cada commit:**
```bash
python -m unittest discover tests -v
```

**End-to-end del modo rebuild** (tras C7):
```bash
python skills/appian-reverse-engineering/scripts/parse_export.py --all tests/fixtures/mini-export --out-dir /tmp/e2e/_intermedio
python skills/appian-reverse-engineering/scripts/parse_export.py --detail tests/fixtures/mini-export --out /tmp/e2e/_intermedio/detail.json
cp -r tests/fixtures/expected-output/* /tmp/e2e/
python skills/appian-reverse-engineering/scripts/check_coverage.py /tmp/e2e --mode rebuild     # exit 0
python skills/appian-reverse-engineering/scripts/check_spec_layout.py /tmp/e2e --mode rebuild  # exit 0
```

**Prueba negativa obligatoria** (un gate que no puede fallar no es un gate): retirar una ficha de pantalla, una de constante y una de site → los tres casos deben dar **exit 1** nombrando el objeto que falta.

**Modo onboarding intacto:**
```bash
python skills/appian-reverse-engineering/scripts/check_coverage.py /tmp/e2e --mode onboarding   # exit 0
git diff --stat 75dac24..HEAD -- skills/appian-reverse-engineering/assets/markdown-templates/0*
```
Lo segundo debe mostrar **solo** los cambios autorizados en `03-modelo-datos.md` y `08-procesos-bpmn/`.

**Coherencia documental (C8):**
```bash
grep -rn "secciones 5.1\|Formato de la respuesta final al usuario\|process-model/\|record-type/" skills/appian-reverse-engineering/   # 0 resultados
grep -rn "render_pendiente\|secretos.md\|@version\|acoplamiento" skills/appian-reverse-engineering/                                   # deben seguir existiendo
```

**Cierre**: `git push`, versión `2.5.1` en `plugin.json` y `marketplace.json`, y actualizar la memoria del proyecto con el estado final.

Queda fuera (pendiente ya identificado): probar el modo `rebuild` contra un export real de una app `RGM_*` de indra-spain.
