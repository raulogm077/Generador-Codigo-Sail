# Plan: Reingeniería inversa de tres niveles (entender · onboarding · rebuild-spec)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `appian-reverse-engineering` produzca, además del onboarding actual, un **Nivel 3 de especificación funcional exhaustiva** (pantallas componente a componente, todas las reglas con su lógica, estados y transiciones, historias de usuario Gherkin, trazabilidad bidireccional y gate de cobertura 100%) suficiente para reconstruir una app Appian legacy desde cero con garantías.

**Architecture:** El conflicto de fondo es que onboarding (síntesis, topes de longitud, sin jerga) y spec (exhaustividad verificable) no caben en los mismos documentos con las mismas reglas (`presentation-rules.md:180,187,225`). Solución: **nueva capa `10-especificacion/` opcional** activada por un argumento `profundidad: onboarding|rebuild` (default `onboarding` = comportamiento actual), generada en una Fase 4.5 por 3 agentes nuevos, con soporte de parser mejorado y un gate de cobertura calculado por script (no "a ojo"). Los documentos 00-09 no cambian de propósito; las reglas de presentación quedan explícitamente acotadas al nivel onboarding.

**Tech Stack:** Markdown (plantillas + agentes), Python 3 stdlib (`parse_export.py`, `check_coverage.py`, `validate_mermaid.py`, tests con `pytest` si está disponible / `python -m unittest` como fallback), Bash (gates).

## Global Constraints

- Raíz de trabajo: `C:\Users\rgmoya\.claude\skills\appian-toolkit\skills\appian-reverse-engineering\` (repo git en `C:\Users\rgmoya\.claude\skills\appian-toolkit\`, remote `https://github.com/raulogm077/Appian-Toolkit`). Commits pequeños y frecuentes en `main`.
- **Cero datos reales**: el fixture de tests es 100% sintético (nombres `DEMO_*`, UUIDs con prefijo `00000000-`). Nada de exports de indra-spain ni OTIEC en el repo.
- **Anti-invención**: toda afirmación funcional del Nivel 3 lleva `Evidencia: {ruta}#{fragmento}` igual que hoy (`execution-principles.md:19`). El SAIL crudo SÍ puede citarse en Nivel 3 (a diferencia de 01-funcional).
- **Enmascarado de secretos** aplica también al Nivel 3 (`security-rules.md`); `detect_secrets.sh` corre sobre `10-especificacion/` igual que sobre el resto.
- Compatibilidad: sin `profundidad` o con `profundidad: onboarding`, la salida debe ser byte-a-byte equivalente a la actual (mismos 11 entregables).
- Python: solo stdlib en scripts de la skill (regla existente). Los tests pueden asumir `pytest` opcional: cada test file debe correr también con `python -m unittest`.
- Convención de nombres intermedios: `inventory.json`, `graph.json`, `coverage.json` (inglés, como el parser — los references se corrigen a esto, no al revés).

---

### Task 1: Fixture de export sintético para tests

**Files:**
- Create: `tests/fixtures/mini-export/` (árbol completo abajo)
- Create: `tests/README.md`

**Interfaces:**
- Produces: un export Haul mínimo pero completo que TODOS los tests posteriores usan como entrada (`tests/fixtures/mini-export/`). Contiene exactamente: 2 interfaces, 2 expression rules, 1 decision, 1 process model, 1 record type, 1 CDT, 1 constant, 1 grupo, 1 integration + connected system, 1 web API, 1 data store.

- [ ] **Step 1: Crear el árbol del fixture**

```
tests/fixtures/mini-export/
├── applicationHaul/DEMO_App.xml
├── contentHaul/
│   ├── DEMO_IFC_SolicitudForm.xml       (interface: form con 4 componentes)
│   ├── DEMO_IFC_SolicitudList.xml       (interface: grid que llama a rule!DEMO_QR_GetSolicitudes)
│   ├── DEMO_QR_GetSolicitudes.xml       (expressionRule: a!queryRecordType con filtro estado)
│   ├── DEMO_VAL_ValidarImporte.xml      (expressionRule: 1 solo caller — debe sobrevivir al catálogo)
│   ├── DEMO_DEC_NivelAprobacion.xml     (decision: 3 filas importe→nivel)
│   └── DEMO_CONS_ESTADOS.xml            (constant: lista "BORRADOR;ENVIADO;APROBADO;RECHAZADO")
├── processModelHaul/DEMO_PM_AprobarSolicitud.xml   (start form → gateway por importe → user task → write)
├── recordTypeHaul/DEMO_RT_Solicitud.xml            (4 campos, 1 relación, 1 action, 1 view)
├── datatypeHaul/DEMO_CDT_Solicitud.xsd
├── dataStoreHaul/DEMO_DS_Principal.xml
├── groupHaul/DEMO_GRP_Aprobadores.xml
├── connectedSystemHaul/DEMO_CS_ERP.xml
└── (integration y webApi dentro de contentHaul: DEMO_INT_EnviarERP.xml, DEMO_WS_ConsultaEstado.xml)
```

Contenido mínimo por XML: estructura Haul real (`<contentHaul>`, `<interface>`, `<definition>` con SAIL embebido…) imitando la que `parse_export.py:26-53` ya reconoce. El SAIL de `DEMO_IFC_SolicitudForm` debe contener, literalmente: `rule!DEMO_VAL_ValidarImporte(ri!importe)`, `rule!DEMO_IFC_SolicitudList()` (para el test de aristas interface→interface), un `a!textField(label: "Solicitante", value: ri!solicitante, saveInto: ri!solicitante, required: true)`, un `showWhen: ri!importe > 1000`, y `recordType!{00000000-0000-0000-0000-000000000001}DEMO Solicitud`.

- [ ] **Step 2: Verificar que el parser actual lo reconoce**

Run: `python skills/appian-reverse-engineering/scripts/parse_export.py --check tests/fixtures/mini-export`
Expected: detecta formato Haul (si falla, ajustar el fixture al formato que el parser espera — el fixture se adapta al parser, no al revés).

- [ ] **Step 3: Commit**

```bash
git add tests/
git commit -m "test: fixture mini-export sintetico para la skill de reingenieria"
```

---

### Task 2: Arreglar resolución de referencias del grafo (bug interfaces-huérfanas) + patrones que faltan

**Files:**
- Modify: `skills/appian-reverse-engineering/scripts/parse_export.py:460-466` (patrones) y `:509-512` (resolución)
- Test: `tests/test_graph.py`

**Interfaces:**
- Consumes: fixture de Task 1.
- Produces: `graph.json` cuyo campo `edges` incluye aristas `interface→interface`, `interface→expressionRule`, y nuevos tipos de arista; `orphans` ya no contiene interfaces llamadas.

- [ ] **Step 1: Test que falla (bug actual)**

```python
# tests/test_graph.py
import json, subprocess, sys, unittest
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "mini-export"
SCRIPT = Path(__file__).parents[1] / "skills/appian-reverse-engineering/scripts/parse_export.py"

class TestGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT), "--all", str(FIXTURE)], check=True)
        out = FIXTURE / "_doc_generada" / "_intermedio"
        cls.graph = json.loads((out / "graph.json").read_text(encoding="utf-8"))

    def edges(self):
        return {(e["from"], e["to"]) for e in self.graph["edges"]}

    def test_interface_call_creates_edge(self):
        # rule!DEMO_IFC_SolicitudList dentro de DEMO_IFC_SolicitudForm debe resolver a la INTERFAZ
        self.assertIn(("DEMO_IFC_SolicitudForm", "DEMO_IFC_SolicitudList"), self.edges())

    def test_called_interface_not_orphan(self):
        self.assertNotIn("DEMO_IFC_SolicitudList", self.graph["orphans"])

    def test_rule_edge_still_works(self):
        self.assertIn(("DEMO_IFC_SolicitudForm", "DEMO_VAL_ValidarImporte"), self.edges())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar y ver fallar** — `python -m unittest tests/test_graph.py -v` → FAIL en `test_interface_call_creates_edge` (hoy `rule!X` solo se resuelve contra `name_index[("expressionRule", X)]`).

- [ ] **Step 3: Fix mínimo en `parse_export.py`**

En la resolución de `rule!X` (`:509-512`), probar en orden: `("expressionRule", X)` → `("interface", X)` → `("decision", X)`. Añadir a los patrones de extracción (`:460-466`) los que `analysis-workflow.md:95-108` documenta y no están: `a!queryEntity`, `a!writeToDataStoreEntity`, `a!writeRecords`, `<connectedSystemRef>`, `<processModelUuid>` (subprocesos), `a!isUserMemberOfGroup` (arista objeto→grupo, tipo `security`).

- [ ] **Step 4: Verificar en verde** — `python -m unittest tests/test_graph.py -v` → PASS (3/3).

- [ ] **Step 5: Commit** — `git commit -m "fix(reverse-engineering): rule! resuelve interfaces y decisions; +6 patrones de referencia al grafo"`

---

### Task 3: Extracción estructurada para el Nivel 3 (`--detail`)

**Files:**
- Modify: `skills/appian-reverse-engineering/scripts/parse_export.py`
- Test: `tests/test_detail.py`

**Interfaces:**
- Produces: `parse_export.py --detail {ruta}` escribe `_intermedio/detail.json` con, por objeto:
  - recordType: `fields: [{name, type, required}]`, `relationships: [{name, target, type}]`, `views: [name]`, `actions: [name]`
  - interface: `ruleInputs: [{name, type}]`, `referencedRules: []`, `referencedRecordTypes: []`, `sail: "<contenido completo>"` (enmascarado con las mismas reglas de `:154-179`)
  - processModel: `processVariables: [{name, type, isParameter}]`, `nodes: [{id, name, type, assignees?, expressionSummary?}]`
  - decision: `inputs`, `outputs`, `rows: [{conditions, result}]`
  - constant: `value` (enmascarado si aplica), para detectar dominios de estados
  - **Nuevo tipo**: `dataStoreHaul` añadido a `HAUL_TO_TYPE` (`:26-37`) y a `cmd_check` (`:203`) — hoy los data stores NO se inventarían.
- Este `detail.json` es el insumo de los agentes de Fase 4.5 (Tasks 7-9): dejan de re-parsear XML gigante a mano.

- [ ] **Step 1: Test que falla**

```python
# tests/test_detail.py (mismo esqueleto que test_graph)
    def test_record_type_fields(self):
        rt = self.detail["recordTypes"]["DEMO_RT_Solicitud"]
        names = [f["name"] for f in rt["fields"]]
        self.assertIn("estado", names)

    def test_interface_rule_inputs(self):
        ifc = self.detail["interfaces"]["DEMO_IFC_SolicitudForm"]
        self.assertIn("importe", [ri["name"] for ri in ifc["ruleInputs"]])
        self.assertIn("DEMO_VAL_ValidarImporte", ifc["referencedRules"])

    def test_pm_process_variables(self):
        pm = self.detail["processModels"]["DEMO_PM_AprobarSolicitud"]
        self.assertTrue(any(pv["name"] == "solicitud" for pv in pm["processVariables"]))

    def test_datastore_inventoried(self):
        inv = json.loads((self.out / "inventory.json").read_text(encoding="utf-8"))
        self.assertTrue(any(o["type"] == "dataStore" for o in inv["objects"]))
```

- [ ] **Step 2: Ver fallar** → `--detail` no existe.
- [ ] **Step 3: Implementar `cmd_detail()`** reutilizando los parsers existentes (`:348-433`), ampliándolos: los XSD ya se leen (`:411-433`) — añadir `minOccurs` → `required`; los PM ya exponen nodos (`:242-254`) — añadir `<pm:processVariables>`.
- [ ] **Step 4: Verificar en verde** y que `--all` sigue funcionando igual (regresión: `test_graph.py` en verde).
- [ ] **Step 5: Commit** — `"feat(reverse-engineering): parse_export --detail (campos RT, ri! de interfaces, PVs de PM, decisions, dataStoreHaul)"`

---

### Task 4: Gate de cobertura calculado — `check_coverage.py`

**Files:**
- Create: `skills/appian-reverse-engineering/scripts/check_coverage.py`
- Test: `tests/test_coverage.py`

**Interfaces:**
- Produces: `python check_coverage.py {ruta_salida} --mode onboarding|rebuild` → escribe `_intermedio/coverage.json` y sale con exit 1 si no cumple. Contrato:
  - Lee `inventory.json` y escanea todos los `.md` de `_doc_generada/` buscando cada objeto por nombre técnico.
  - `--mode onboarding`: exige 100% de recordTypes, CDTs, processModels, integrations, webApis, groups, dataStores (lo que hoy promete `response-format.md:83` MÁS data stores); interfaces/rules solo se reportan (informativo).
  - `--mode rebuild`: exige además 100% de interfaces, expressionRules, decisions, constants y sites — cada uno debe aparecer en `10-especificacion/` o estar en `trazabilidad.md` marcado `DESCARTADO: {motivo}` (p. ej. objeto muerto confirmado).
  - Salida legible: tabla por tipo `documentados/total` + lista exacta de los que faltan.

- [ ] **Step 1: Test que falla** — generar una `_doc_generada` mínima en tmp con 1 RT documentado y 1 no documentado; asertar exit code 1 y que `coverage.json["missing"]["recordType"]` contiene el que falta. Test 2: con todos documentados → exit 0.
- [ ] **Step 2: Ver fallar.** — el script no existe.
- [ ] **Step 3: Implementar** (stdlib; matching por nombre técnico exacto y por UUID como fallback).
- [ ] **Step 4: Verde.**
- [ ] **Step 5: Commit** — `"feat(reverse-engineering): gate de cobertura check_coverage.py (modos onboarding/rebuild)"`

---

### Task 5: `validate_mermaid.py` — soportar Tipos B y C (hoy los rechaza por diseño)

**Files:**
- Modify: `skills/appian-reverse-engineering/scripts/validate_mermaid.py:26-28,82-90`
- Test: `tests/test_mermaid.py`

**Interfaces:**
- Produces: acepta `erDiagram` (Tipo B: sin tope de 30 nodos, valida sintaxis de relaciones `||--o{`) y `flowchart` con `subgraph` (Tipo C: subgraphs permitidos, se validan aperturas/cierres emparejados). El saneado actual del Tipo A no cambia.

- [ ] **Step 1: Tests que fallan** — `test_er_diagram_accepted` (un `erDiagram` de 3 entidades pasa), `test_subgraph_lanes_accepted` (el ejemplo literal de `mermaid-rules.md:86-100` pasa), `test_type_a_unchanged` (un flowchart de 31 nodos sigue rechazándose).
- [ ] **Step 2: Ver fallar** (los dos primeros).
- [ ] **Step 3: Implementar**: dispatch por cabecera; `MAX_NODES=30` solo aplica a Tipo A sin subgraph (alineado con `mermaid-rules.md:47-52` y arreglando de paso la contradicción de `presentation-rules.md:226`, que se corrige en Task 13).
- [ ] **Step 4: Verde** (3/3).
- [ ] **Step 5: Commit** — `"fix(reverse-engineering): validate_mermaid soporta erDiagram (B) y subgraph/lanes (C)"`

---

### Task 6: Plantillas del Nivel 3 (`assets/markdown-templates/10-especificacion/`)

**Files:**
- Create: `assets/markdown-templates/10-especificacion/pantalla-template.md`
- Create: `assets/markdown-templates/10-especificacion/reglas-catalogo-template.md`
- Create: `assets/markdown-templates/10-especificacion/estados-template.md`
- Create: `assets/markdown-templates/10-especificacion/pm-nodos-template.md`
- Create: `assets/markdown-templates/10-especificacion/historia-template.md`
- Create: `assets/markdown-templates/10-especificacion/trazabilidad-template.md`

**Interfaces:**
- Produces: las 6 plantillas que los agentes de Tasks 7-9 rellenan. Secciones obligatorias (no opcionales — a diferencia de `09-valor-adicional.md`, aquí "sección vacía" = "N/A explícito con motivo").

- [ ] **Step 1: `pantalla-template.md`** — por interfaz:

```markdown
# Pantalla: {{nombre_visible}} (`{{nombre_tecnico}}`)
**Tipo**: formulario | listado | dashboard | wizard | componente reutilizable
**Usada desde**: {{callers desde graph.json}} · **Evidencia**: {{ruta_xml}}

## Entradas (rule inputs)
| ri! | Tipo | Obligatorio | Origen del valor |
## Variables locales relevantes
| local! | Se inicializa con | Para qué sirve |
## Componentes (en orden de aparición, TODOS)
| # | Componente | Etiqueta | Campo/dato origen | Obligatorio | Validaciones (predicado EXACTO) | Visible/editable cuando (predicado) | Al cambiar/guardar (saveInto → efecto) |
## Acciones (botones/links)
| Acción | Estilo | Habilitada cuando | Qué hace (submit/proceso/navegación) | Validaciones que dispara |
## Reglas invocadas
| rule! | Para qué | → ficha en reglas-catalogo |
## Estados de la pantalla
{{si la pantalla rinde distinto según estado del registro: tabla estado → qué se ve}}
## Criterios de reconstrucción (verificables)
- [ ] {{ej: con importe > 1000 el campo Justificación es visible y obligatorio}}
```

- [ ] **Step 2: `reglas-catalogo-template.md`** — TODAS las expression rules y decisions (sin filtro de callers; deroga explícitamente el `>3 callers` de `09:23` en este nivel):

```markdown
## rule!{{nombre}}
**Firma**: {{inputs con tipo}} → {{output}} · **Callers**: {{lista}} · **Evidencia**: {{ruta}}
**Lógica (explicada)**: {{prosa breve}}
**Predicado/algoritmo (exacto)**:
```sail
{{SAIL relevante, enmascarado si contiene secretos}}
```
**Casos límite observables**: {{null-handling, listas vacías, defaults}}
```

Para decisions: tabla completa de filas condición→resultado (las 3 del fixture, las N reales).

- [ ] **Step 3: `estados-template.md`** — por entidad con ciclo de vida:

```markdown
# Máquina de estados: {{entidad}}
**Campo**: {{rt.campo}} · **Dominio**: {{valores, con origen: constant/decision/gateway}}
| Desde | Hasta | Disparador (pantalla/proceso/nodo) | Quién puede | Condición (predicado) | Evidencia |
{{diagrama mermaid stateDiagram-v2 opcional — validar con validate_mermaid}}
```

- [ ] **Step 4: `pm-nodos-template.md`** — complemento por PM (cierra el hueco `bpmn-mapping.md:238` vs `pm-template.md`):

```markdown
# {{PM}} — detalle por nodo
## Process variables
| PV | Tipo | ¿Parámetro? | Quién la escribe | Quién la lee |
## Ficha por nodo (TODOS los nodos, mismo id que el BPMN)
### {{nodo_id}} — {{nombre}} ({{tipo}})
- Entradas: {{ac!/pv! → origen}} · Salidas: {{→ pv!}}
- Configuración relevante: {{asignación, escalation/SLA, formulario (→ ficha de pantalla), expresión del script task EXACTA}}
```

- [ ] **Step 5: `historia-template.md`** — formato compatible con el que produce `appian-functional-analyst` (mismo Gherkin):

```markdown
### HU-{{nnn}}: {{título}}
**Como** {{actor}} **quiero** {{acción}} **para** {{beneficio}}
**Criterios de aceptación** (Given/When/Then, ≥2 por historia, derivados de validaciones/estados/gateways REALES):
```gherkin
Dado {{estado inicial con datos}}
Cuando {{acción}}
Entonces {{resultado verificable}}
```
**Objetos que la implementan hoy**: {{lista con tipo}} · **Prioridad de reconstrucción**: MVP | fase 2 | opcional
```

- [ ] **Step 6: `trazabilidad-template.md`** — matriz bidireccional (resuelve la referencia colgante de `appian-objects-guide.md:143`):

```markdown
| Objeto (tipo) | Caso de uso (01-funcional) | Historias (HU-nnn) | Pantalla/Regla/Estado spec | Estado |
{{una fila por CADA objeto del inventory.json; Estado ∈ DOCUMENTADO | DESCARTADO: {motivo} — nada más}}
```

- [ ] **Step 7: Verificación** — grep: cada plantilla contiene "Evidencia"; `pantalla-template.md` contiene "predicado EXACTO"; `trazabilidad-template.md` contiene "CADA objeto".
- [ ] **Step 8: Commit** — `"feat(reverse-engineering): 6 plantillas del nivel 3 (rebuild-spec)"`

---

### Task 7: Agente `interface-spec-writer.md`

**Files:**
- Create: `skills/appian-reverse-engineering/agents/interface-spec-writer.md`

**Interfaces:**
- Consumes: `detail.json` (Task 3), `graph.json`, plantilla `pantalla-template.md` (Task 6).
- Produces: `10-especificacion/pantallas/{interfaz}.md` — **una por CADA interfaz** del inventario; `10-especificacion/pantallas/indice.md` con tabla resumen.

Reglas clave a escribir en el agente (contrapunto deliberado de `interface-analyzer.md:89,:123`):
- **Aquí la jerga SAIL es obligatoria, no prohibida**: los predicados (`showWhen`, `required`, `validations`) se copian EXACTOS del SAIL, luego se explican en una frase.
- Cobertura de componentes 100%: se recorre el árbol SAIL completo; los componentes puramente decorativos (línea, espaciador) se agrupan en una fila "decorativos: N".
- Interfaces >100KB: trocear por secciones del layout, nunca truncar en silencio; si algo no se pudo analizar → sección "NO ANALIZADO: {qué y por qué}".
- Paralelizable: el orquestador lanza lotes de ~10 interfaces por invocación de agente.
- Checklist de salida: nº de fichas == nº de interfaces en inventory.json; cada ficha con ≥1 criterio de reconstrucción verificable; 0 menciones sin evidencia.

- [ ] **Step 1: Escribir el agente** (estructura homóloga a `data-modeler.md`: misión / inputs / método / anti-patrones / checklist).
- [ ] **Step 2: Verificación en seco contra el fixture**: ejecutar el agente (o inline) sobre `mini-export` → deben salir 2 fichas; la de `DEMO_IFC_SolicitudForm` debe contener `ri!importe > 1000` literal y el criterio "Justificación visible y obligatoria cuando importe > 1000".
- [ ] **Step 3: Commit** — `"feat(reverse-engineering): agente interface-spec-writer (fichas de pantalla 100%)"`

---

### Task 8: Agente `logic-spec-writer.md` (reglas + decisions + estados)

**Files:**
- Create: `skills/appian-reverse-engineering/agents/logic-spec-writer.md`

**Interfaces:**
- Consumes: `detail.json`, `graph.json`, plantillas `reglas-catalogo-template.md` + `estados-template.md`.
- Produces: `10-especificacion/reglas-catalogo.md` (TODAS las rules/decisions) y `10-especificacion/estados.md` (una máquina por entidad con ciclo de vida detectado).

Método de detección de estados a escribir en el agente: (1) campos llamados `estado|status|fase|stage` en RTs/CDTs; (2) constants con listas de valores (`DEMO_CONS_ESTADOS`); (3) valores comparados en gateways de PMs y en `showWhen` de interfaces; (4) decisions cuyo output es uno de esos valores. Cruzar las 4 fuentes; transición sin disparador identificado → fila con `Disparador: 🟡 no identificado`.

- [ ] **Step 1: Escribir el agente.**
- [ ] **Step 2: Verificación contra fixture**: `reglas-catalogo.md` contiene `DEMO_VAL_ValidarImporte` (1 solo caller — antes desaparecía) con su SAIL; `estados.md` contiene los 4 estados de `DEMO_CONS_ESTADOS` y la transición `ENVIADO→APROBADO` disparada por el user task del PM.
- [ ] **Step 3: Commit** — `"feat(reverse-engineering): agente logic-spec-writer (catalogo de reglas 100% + maquinas de estados)"`

---

### Task 9: Agente `backlog-writer.md` (historias + trazabilidad)

**Files:**
- Create: `skills/appian-reverse-engineering/agents/backlog-writer.md`

**Interfaces:**
- Consumes: `01-funcional.md` (casos de uso), fichas de Task 7, catálogo/estados de Task 8, `inventory.json`.
- Produces: `10-especificacion/backlog.md` (épicas → historias HU-nnn con Gherkin) y `10-especificacion/trazabilidad.md` (matriz de Task 6, TODAS las filas).

Reglas clave: los Given/When/Then se derivan de artefactos reales (validaciones de pantalla, transiciones de estado, gateways) — nunca inventados; cada historia lista sus objetos; prioridad MVP = camino feliz de los casos de uso principales; la matriz cierra con la línea `Cobertura: X/X objetos (100%)` que `check_coverage.py --mode rebuild` verificará.

- [ ] **Step 1: Escribir el agente** (alinear formato Gherkin con el del agente `appian-toolkit:appian-functional-analyst` para que ambos backlogs sean intercambiables).
- [ ] **Step 2: Verificación contra fixture**: ≥3 historias; una debe ser "aprobar solicitud" con un Then derivado del gateway de importe; `trazabilidad.md` tiene 13 filas (los 13 objetos del fixture) y todas DOCUMENTADO.
- [ ] **Step 3: Commit** — `"feat(reverse-engineering): agente backlog-writer (historias Gherkin + matriz de trazabilidad)"`

---

### Task 10: Enriquecer process-modeler (PVs + ficha por nodo)

**Files:**
- Modify: `skills/appian-reverse-engineering/agents/process-modeler.md`
- Modify: `assets/markdown-templates/08-procesos-bpmn/pm-template.md`

**Interfaces:**
- Produces: en modo `rebuild`, process-modeler rellena además `10-especificacion/procesos/{PM}-nodos.md` usando `pm-nodos-template.md` (Task 6) y `detail.json`. En modo `onboarding`, `pm-template.md` gana UNA tabla nueva (process variables) y nada más — el paso a paso narrativo no cambia.

- [ ] **Step 1: Añadir a `pm-template.md`** la tabla `## Process variables` (| PV | Tipo | ¿Parámetro? |) tras "Datos clave".
- [ ] **Step 2: Añadir a `process-modeler.md`** la instrucción condicional por modo + checklist: "en rebuild, nº de fichas de nodo == nº de nodos del BPMN".
- [ ] **Step 3: Verificación contra fixture** (modo rebuild): `DEMO_PM_AprobarSolicitud-nodos.md` existe y tiene ficha del gateway con su condición exacta.
- [ ] **Step 4: Commit** — `"feat(reverse-engineering): process-modeler documenta PVs y ficha por nodo en modo rebuild"`

---

### Task 11: Enriquecer data-modeler (semántica de campos + sub-entidades de record)

**Files:**
- Modify: `skills/appian-reverse-engineering/agents/data-modeler.md`
- Modify: `assets/markdown-templates/03-modelo-datos.md:126-130` (ficha de campo) y `:176-179` (ficha CDT)

**Interfaces:**
- Produces: ficha de campo con columnas nuevas `Obligatorio | Dominio/valores | Default | Regla de cálculo` (rellenas desde `detail.json` + cruce con constants/estados; vacío → `—`, nunca omitido). Sección nueva por RT: `User filters`, `Custom fields`, `Record events` (si existen en el XML; si el parser no los expone aún, el agente los busca por tag y si no puede → `🟡 no analizado`).

- [ ] **Step 1: Ampliar la plantilla** (columnas + sección).
- [ ] **Step 2: Ampliar el agente** (de dónde sale cada columna; anti-patrón: "inventar dominio de valores no evidenciado").
- [ ] **Step 3: Verificación contra fixture**: la ficha de `DEMO_RT_Solicitud.estado` tiene Dominio = los 4 valores con evidencia en `DEMO_CONS_ESTADOS`.
- [ ] **Step 4: Commit** — `"feat(reverse-engineering): modelo de datos con obligatoriedad, dominios y sub-entidades de record"`

---

### Task 12: Orquestación — argumento `profundidad`, Fase 4.5, gates y respuesta final

**Files:**
- Modify: `skills/appian-reverse-engineering/SKILL.md` (argumentos, Fase 0, nueva Fase 4.5, validación final)
- Modify: `references/response-format.md` (métricas de cobertura reales)
- Modify: `references/execution-principles.md` (principio nuevo: "en Nivel 3, exhaustividad > síntesis")

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: contrato de orquestación completo del modo rebuild.

- [ ] **Step 1: Argumentos** — añadir `profundidad` (`onboarding` default | `rebuild`) a la tabla de `SKILL.md:20-24`. La Fase 0 pregunta también la profundidad cuando el usuario menciona "reconstruir/migrar/rebuild/spec"; coste avisado: el modo rebuild multiplica tiempo y tokens (una ficha por interfaz). Guardar en `output_preferences.json` (`"depth": "rebuild"`). Si el proyecto tiene `.claude/appian-toolkit.local.md` con `re_depth:`, usarlo como default sin preguntar.
- [ ] **Step 2: Fase 4.5 (solo rebuild)** — tras la Fase 4: `parse_export.py --detail` → lanzar en paralelo `interface-spec-writer` (por lotes) + `logic-spec-writer`; al terminar ambos, `backlog-writer` (necesita 01 + fichas). Actualizar el mapa de subagentes (`SKILL.md:69-78`) con los 3 nuevos.
- [ ] **Step 3: Validación final** — sustituir el checklist `SKILL.md:270-278` puntos de cobertura por: "ejecuta `python scripts/check_coverage.py {salida} --mode {profundidad}` → exit 0 obligatorio; adjunta la tabla de cobertura". `detect_secrets.sh` corre también sobre `10-especificacion/`.
- [ ] **Step 4: `response-format.md`** — en la respuesta final, sustituir el "Nivel de confianza global" a ojo por la tabla real de `coverage.json` (documentados/total por tipo) + confianza calculada. Ampliar el criterio `:83` a TODOS los tipos en modo rebuild.
- [ ] **Step 5: Verificación** — correr el flujo completo contra el fixture en modo rebuild: existen `10-especificacion/{pantallas/(2+indice), reglas-catalogo.md, estados.md, procesos/1, backlog.md, trazabilidad.md}` y `check_coverage.py --mode rebuild` sale 0. En modo onboarding: los 11 entregables de siempre y nada más.
- [ ] **Step 6: Commit** — `"feat(reverse-engineering): modo rebuild (Fase 4.5, 3 agentes nuevos, gate de cobertura en la respuesta)"`

---

### Task 13: Consistencia y deuda documental del propio skill

**Files:**
- Modify: `references/analysis-workflow.md` (reescritura: Fase 0-8 alineadas con SKILL.md, subagentes mencionados, `inventory.json`/`graph.json` bien escritos)
- Modify: `references/security-rules.md:57` y `scripts/detect_secrets.sh:53` (referencia a `05_riesgos_deuda_tecnica.md` → `09-valor-adicional.md`)
- Modify: `references/presentation-rules.md` (encabezado nuevo: "estas reglas aplican a los documentos 00-09 e INVENTARIO — NO a `10-especificacion/`, donde manda la exhaustividad"; corregir tope Tipo B a "sin techo" alineado con `mermaid-rules.md`)
- Modify: `references/appian-objects-guide.md:143` (la "matriz de trazabilidad" ahora existe: enlazar a `10-especificacion/trazabilidad.md`)

- [ ] **Step 1: Aplicar las 4 correcciones.**
- [ ] **Step 2: Verificación** — greps: 0 apariciones de `inventario.json|grafo.json|05_riesgos_deuda_tecnica` en todo el skill; `analysis-workflow.md` menciona "Fase 0" y "Fase 4.5".
- [ ] **Step 3: Commit** — `"docs(reverse-engineering): alinear references con el pipeline real y acotar presentation-rules al nivel onboarding"`

---

### Task 14: Prueba end-to-end y cierre

**Files:**
- Modify: `README.md` del repo (sección de reingeniería: mencionar los 2 modos)
- Modify: `.claude-plugin/plugin.json` (version 2.5.0)

- [ ] **Step 1: E2E onboarding** — fixture completo en modo onboarding: 11 entregables, `check_coverage.py --mode onboarding` exit 0, `detect_secrets.sh` limpio, tests `python -m unittest discover tests -v` todos en verde.
- [ ] **Step 2: E2E rebuild** — fixture en modo rebuild: Nivel 3 completo + gate exit 0.
- [ ] **Step 3: Prueba real (manual, con el usuario)** — ejecutar modo rebuild contra un export real pequeño de una app `RGM_*` de indra-spain y revisar juntos si con `10-especificacion/` en la mano se podría reconstruir una pantalla sin abrir el export. Éste es el criterio de aceptación humano del plan.
- [ ] **Step 4: README + versión + commit final** — `"release: appian-toolkit 2.5.0 — reingenieria inversa con modo rebuild-spec"` y push.

---

## Self-Review (hecho al redactar)

- **Cobertura de los 3 objetivos**: entender → sin cambios (00-09); onboarding → intacto + correcciones de bugs que hoy lo degradan (huérfanos falsos, diagramas rechazados); rebuild → Tasks 3-12 (pantallas 100%, reglas 100%, estados, historias, trazabilidad, gate calculado). Los 10 huecos del diagnóstico están mapeados: #1→T6/T7, #2→T6/T8, #3→T4/T12, #4→T2, #5→T5, #6→T6/T9, #7→T6/T9, #8→T3/T8/T11, #9→T13, #10→T3/T10.
- **Sin placeholders**: cada plantilla lleva sus columnas exactas; cada test su aserción; cada fix su ubicación fichero:línea.
- **Consistencia de nombres**: `detail.json`, `coverage.json`, `--mode onboarding|rebuild`, `10-especificacion/` usados idénticos en todas las tareas.
