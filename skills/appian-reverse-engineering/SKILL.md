---
name: appian-reverse-engineering
description: Reingenieria inversa de aplicaciones Appian a partir de su carpeta exportada. Produce 11 documentos Markdown (funcional, arquitectura, modelo de datos, seguridad, integraciones, APIs, batches, BPMN por process model, valor adicional, inventario, resumen ejecutivo) mas diagramas SVG y BPMN 2.0 validados. Opcionalmente (preguntando antes) un PDF maquetado o un dashboard web. Funciona offline sobre el export desempaquetado. Usala siempre que el usuario apunte a una carpeta con un export Appian (formato Haul con applicationHaul, processModelHaul, recordTypeHaul, siteHaul, contentHaul, etc. o formato antiguo con application.xml), mencione documentar, hacer onboarding, reingenieria inversa o entender una app Appian heredada, pase XMLs de objetos Appian (records, CDTs, process models, integrations, web APIs, interfaces, expression rules), o pida un diagrama BPMN, modelo ER o mapa de integraciones de Appian, aunque no diga literalmente reingenieria inversa. Tiene ademas un modo `rebuild` (especificacion de reconstruccion) que se activa cuando el usuario quiere reconstruir, rehacer de cero, migrar o reimplementar una app Appian existente, o pide una especificacion funcional detallada, historias de usuario, criterios de aceptacion, maquinas de estados, spec de pantallas o matriz de trazabilidad a partir del export.
---

# Appian Reverse Engineering

Reconstruye documentación funcional, técnica y de arquitectura útil a partir de un **export de aplicación Appian** descomprimido (paquete del Application Designer). El objetivo no es inventariar: es producir documentación que permita a un consultor nuevo entender qué hace la app, cómo está construida, qué integraciones tiene, qué procesos ejecuta y qué riesgos arrastra.

Genera **11 entregables Markdown** y **diagramas** (Mermaid SVG para arquitectura/datos, BPMN 2.0 XML para procesos) en una carpeta de salida única dentro del propio export.

---

## Argumentos esperados

```
[ruta_export_appian] [idioma] [salida] [profundidad]
```

| Argumento | Obligatorio | Default | Significado |
|---|---|---|---|
| `ruta_export_appian` | Sí | — | Carpeta del export Appian descomprimido. Si el usuario no la indica, **pregúntala antes de empezar**. |
| `idioma` | No | `español` | Idioma de salida. |
| `salida` | No | `{ruta_export_appian}/_doc_generada/` | Carpeta de salida. |
| `profundidad` | No | `onboarding` | `onboarding` = los 11 entregables de siempre. `rebuild` = añade la capa `10-especificacion/` (Fase 4.5): spec de reconstrucción exhaustiva. |

Si la ruta no se proporciona o no parece un export Appian válido, **detente y pregunta** antes de generar nada.

---

## Cuándo activarse

- Carpeta con export Appian descomprimido o `.zip` (formato Haul moderno o `application.xml` antiguo).
- Mención de: documentar app Appian, onboarding, reingeniería inversa, "qué hace esta app", entender app Appian heredada, generar BPMN / modelo de datos / mapa de integraciones.
- Carpetas con sufijos típicos: `processModel/`, `recordType/`, `site/`, `content/`, `group/`, `connectedSystem/`, `datatype/`, `application/`, `.xsd` de CDTs, `import-customization-file`.

---

## Arquitectura de subagentes (patrón Anthropic)

Esta skill **delega trabajo a 9 subagentes especializados** definidos en `agents/`. Cada agente es un fichero `.md` con instrucciones para un rol concreto — el mismo patrón que usa el `skill-creator` oficial de Anthropic.

**Por qué subagentes y no un único Claude haciendo todo:**

- **Especialización**: cada agente carga sólo el contexto que necesita. `data-modeler` no lee `bpmn-mapping.md`; `process-modeler` no lee reglas de seguridad. Mejor calidad por agente.
- **Paralelismo**: 3 de los 4 agentes de Fase 4 pueden ejecutarse en paralelo (sin dependencias mutuas).
- **Context window pequeño**: cada subagente trabaja con sólo su parcela; el orquestador principal mantiene el plano general.
- **Mantenibilidad**: SKILL.md mantiene la visión global; los agentes encapsulan el "cómo" de cada parcela.

### Cómo invocar a un subagente — patrón obligatorio

**En Claude Code / entornos con Agent tool nativa:**

```
Agent({
  description: "Generate {entregable}",
  subagent_type: "general-purpose",
  prompt: {contenido de agents/{rol}.md} + 
          "\n\nInputs:\n- Export path: {ruta}\n- Output path: {ruta_salida}\n- Read inventory.json: {ruta}" +
          "\n\nReport back: paths of generated files + count of validation warnings."
})
```

Lanza los subagentes **en paralelo** en un único turno (multiple Agent calls en el mismo mensaje) cuando no haya dependencias.

**En Claude.ai (sin Agent tool nativa):**

Lee `agents/{rol}.md` y aplica sus instrucciones tú mismo, secuencialmente. Resultado funcionalmente equivalente, sólo más lento.

### Mapa de subagentes

| Subagente | Genera | Dependencias |
|---|---|---|
| `agents/interface-analyzer.md` | `01-funcional.md`, `02-arquitectura.md` | Fase 3 (grafo). Va **primero** — los demás lo citan. |
| `agents/data-modeler.md` | `03-modelo-datos.md` + ERs por subdominio | Fase 3 (grafo). Puede ir en paralelo con security/process. |
| `agents/integration-security-analyzer.md` | `04-seguridad-grupos.md`, `05-integraciones-consumidas.md`, `06-apis-expuestas.md` | Fase 3 (grafo). Puede ir en paralelo con data/process. |
| `agents/process-modeler.md` | `08-procesos-bpmn/*` (BPMN 2.0 + Mermaid + MD por PM) y, **en modo `rebuild`, `10-especificacion/procesos/{PM}-nodos.md`** (segunda invocación en Fase 4.5.1, cuando ya existe `detail.json`) | Fase 3 (grafo). Necesita conocer integraciones para etiquetar nodos — lánzalo **después** o en paralelo con integration-security-analyzer si el grafo ya identifica integraciones. |
| `agents/interface-spec-writer.md` | `10-especificacion/pantallas/*` y `navegacion.md` (**solo `rebuild`**) | Fase 4.5. Necesita `detail.json`. Paralelizable por lotes de ~10 interfaces. |
| `agents/logic-spec-writer.md` | `10-especificacion/reglas-catalogo.md` (reglas + decisions + **constants**), `estados.md` (**solo `rebuild`**) | Fase 4.5. Necesita `detail.json`. Paralelo con interface-spec-writer. |
| `agents/backlog-writer.md` | `10-especificacion/backlog.md`, `trazabilidad.md` (**solo `rebuild`**) | Fase 4.5. **Después** de los dos anteriores + `01-funcional.md`. |
| `agents/pdf-publisher.md` | `EXPORT.pdf` (opcional) | Todos los `.md` finalizados + `summary.json`. |
| `agents/dashboard-publisher.md` | `dashboard/index.html` (opcional) | Todos los `.md` finalizados + `summary.json`. |

**Documentos generados directamente por el orquestador (sin subagente):**
- `INVENTARIO.md` (Fase 2)
- `07-batches.md` y `09-valor-adicional.md` (Fase 4, agregaciones del trabajo de los agentes)
- `00-resumen-ejecutivo.md` (Fase 6)
- `_intermedio/summary.json` (Fase 6.5, consumido por publishers)

---

## Flujo de trabajo (Fase 0 + 7 fases base + 2 fases opcionales)

Detalle operativo en `references/analysis-workflow.md`. Aquí el esqueleto.

### Fase 0 — Elicitación de salidas (OBLIGATORIA antes de Fase 1)

Antes de empezar a generar nada, **pregunta al usuario qué formato(s) de salida quiere**. Las salidas Markdown siempre se generan; PDF y Dashboard son opcionales.

Patrón de pregunta (adapta al idioma):

```
"Voy a documentar la app Appian. Además de los 11 documentos Markdown
que siempre genero, ¿quieres alguna salida adicional?

  1. 📄 PDF profesional — un único PDF maquetado con portada, índice,
     secciones temáticas, diagramas embebidos y resumen ejecutivo.
  2. 🖥️ Dashboard web interactivo — single-file HTML autocontenido con
     métricas, buscador, gráficos navegables y filtros.
  3. 📁 Sólo los .md (más rápido).

Puedes elegir varias. Si dudas, recomiendo sólo .md primero."
```

**Pregunta también la profundidad** cuando el usuario mencione *reconstruir*, *migrar*, *rehacer de cero*, *rebuild*, *especificación* o *pasar a otra plataforma* — o cuando el objetivo declarado no sea solo entender la app:

```
"¿Con qué profundidad?

  A. Onboarding (por defecto) — los 11 documentos: entender la app,
     arquitectura, procesos, datos, integraciones y riesgos.
  B. Rebuild (especificación) — todo lo anterior MÁS 10-especificacion/:
     ficha de CADA pantalla componente a componente, catálogo del 100% de
     reglas con su lógica, máquinas de estados, historias de usuario con
     criterios de aceptación y matriz de trazabilidad. Sirve para
     reconstruir la app desde cero.

El modo B multiplica tiempo y tokens (una ficha por interfaz)."
```

**Reglas duras:**
- **No asumas.** Sin respuesta explícita → solo Markdown y `profundidad: onboarding`.
- **Confirma coste** si la app es grande (más de 50 PMs o más de 100 interfaces): PDF/Dashboard añaden 30-90s y tokens extra; el modo `rebuild` puede multiplicar por 3-5 el trabajo total.
- Si el proyecto tiene `.claude/appian-toolkit.local.md`, **mira `enabled` antes que nada**: con `enabled: false` ignora el fichero entero — ni `re_depth` ni el cuerpo — y pregunta la profundidad como si no existiera. Es el interruptor de apagado del toolkit para ese proyecto; si `re_depth` siguiera aplicándose, el interruptor no apagaría.
- Si está habilitado y trae `re_depth:` (`onboarding` | `rebuild`), úsalo como default **sin preguntar** la profundidad. Esquema completo del fichero, con todos los campos y sus defaults: `../appian-sail-generator/SKILL.md` § *Per-project settings*.
- Guarda elección en `_intermedio/output_preferences.json`:
  ```json
  { "markdown": true, "pdf": false, "dashboard": false, "depth": "onboarding", "askedAt": "{ISO}" }
  ```

### Fase 1 — Validar export

Acepta el **formato real *Haul*** (carpetas `application/`, `processModel/`, `recordType/`, `site/`, `content/`, `group/`, `connectedSystem/`, `datatype/`) o el **formato antiguo** con `application.xml` en raíz. Valida con `python3 scripts/parse_export.py --check {ruta}`.

### Fase 2 — Inventariar

Recorre carpetas y XMLs → `INVENTARIO.md`. Usa `scripts/inventory.sh` para barrido bruto y `scripts/parse_export.py --inventory` para inventariado estructurado (genera `_intermedio/inventory.json`). Ejecuta `scripts/detect_secrets.sh` en paralelo — los hallazgos van a riesgos de `09-valor-adicional.md`.

### Fase 3 — Grafo de dependencias

`scripts/parse_export.py --graph` genera `_intermedio/graph.json` a partir de referencias SAIL/XML (`rule!`, `cons!`, `recordType!`, `a!startProcess`, `connectedSystemRef`, etc.). Es el insumo principal de la Fase 4.

### Fase 4 — Generar entregables vía subagentes en paralelo

**Patrón Anthropic — Sequential workflow orchestration + paralelismo:**

**Paso 4.1** — Lanza **interface-analyzer** primero (los demás lo citan):

```
Agent({
  description: "Producir 01-funcional + 02-arquitectura",
  subagent_type: "general-purpose",
  prompt: {contenido de agents/interface-analyzer.md} + inputs
})
```

**Paso 4.2** — Cuando interface-analyzer termina, lanza los **3 agentes restantes EN PARALELO** (un único turno con 3 Agent calls):

```
Agent({ ..., prompt: {agents/data-modeler.md} + inputs })
Agent({ ..., prompt: {agents/integration-security-analyzer.md} + inputs })
Agent({ ..., prompt: {agents/process-modeler.md} + inputs })
```

**Paso 4.3** — Cuando los 3 terminan, el orquestador escribe `07-batches.md` y `09-valor-adicional.md` directamente (agregaciones).

### Fase 4.5 — Especificación de reconstrucción (SOLO si `profundidad: rebuild`)

Si `output_preferences.json` tiene `"depth": "onboarding"`, **salta esta fase entera**.

**Paso 4.5.0** — Extraer el detalle estructurado que los agentes de spec necesitan:

```bash
python scripts/parse_export.py --detail {ruta} --out {salida}/_intermedio/detail.json
```

**Paso 4.5.1** — Lanzar **en paralelo** (un único turno). Son **tres** agentes: `process-modeler` se re-invoca aquí porque en la Fase 4.2 aún no existía `detail.json`, y es quien conoce los nodos:

```
Agent({ ..., prompt: {agents/interface-spec-writer.md} + inputs })   # por lotes de ~10 interfaces
Agent({ ..., prompt: {agents/logic-spec-writer.md} + inputs })
Agent({ ..., prompt: {agents/process-modeler.md} + inputs +
        "MODO: rebuild. Ejecuta SOLO el paso de ficha por nodo: produce
         10-especificacion/procesos/{PM}-nodos.md por cada process model
         (process variables + una ficha por CADA nodo del BPMN que ya
         generaste en la Fase 4.2). NO regeneres los .bpmn/.mmd/.md." })
```

**Paso 4.5.2** — Cuando ambos terminan, lanzar `backlog-writer` (necesita las fichas + `01-funcional.md`):

```
Agent({ ..., prompt: {agents/backlog-writer.md} + inputs })
```

**Regla que invierte la del nivel onboarding**: en `10-especificacion/` la jerga SAIL es **obligatoria** y los predicados se copian **exactos**. Los topes de longitud de `presentation-rules.md` **no aplican** aquí: manda la exhaustividad. Salida:

```
10-especificacion/
├── pantallas/{interfaz}.md (una por CADA interfaz) + indice.md
├── navegacion.md             (una ficha por CADA site: páginas y su destino)
├── reglas-catalogo.md        (100% de expression rules, decisions y constants)
├── estados.md                (máquinas de estados por entidad)
├── procesos/{PM}-nodos.md    (process variables + ficha por nodo)
├── backlog.md                (historias con Gherkin)
└── trazabilidad.md           (matriz bidireccional objeto ↔ requisito)
```

### Fase 5 — Renderizar diagramas con Iterative Refinement

**Patrón Anthropic — Iterative refinement**: cada bloque Mermaid se valida, si falla se refina, se re-valida; hasta 3 iteraciones máximo. Tras la 3ª, se sustituye por tabla equivalente.

1. `scripts/render_diagrams.sh --batch {ruta}/_doc_generada/` → renderiza `.mmd` a `.svg` con `mmdc`.
2. Para cada `.mmd` que falle render: ejecutar `scripts/validate_mermaid.py` para identificar issue, refinar el bloque, re-validar.
3. Si tras 3 iteraciones aún falla → sustituir por tabla equivalente con la misma información.
4. `.bpmn` XML se entregan tal cual (no se renderizan a SVG aquí — Camunda Modeler / draw.io / demo.bpmn.io los renderizan al abrir).

### Fase 6 — Resumen ejecutivo

`00-resumen-ejecutivo.md` con: volumen por tipo, riesgos top, integraciones críticas, procesos críticos, pendientes principales. **Se escribe al final** porque depende del resto.

### Fase 6.5 — Consolidar summary.json

`python3 scripts/build_summary.py {ruta_salida}` produce `_intermedio/summary.json` (inventario + grafo + métricas + hallazgos normalizados). **Siempre se genera** — es barato y los publishers lo consumen.

### Fase 7 — Publicación opcional según `output_preferences.json`

- Si `pdf: true` → `Agent({ ..., prompt: {agents/pdf-publisher.md} })` → `EXPORT.pdf`.
- Si `dashboard: true` → `Agent({ ..., prompt: {agents/dashboard-publisher.md} })` → `dashboard/index.html`.
- Si ambos false → saltar.

Estos dos publishers también pueden ir **en paralelo** si ambos están solicitados.

### Fase 8 — Respuesta final

Devolver al usuario la plantilla literal de `references/response-format.md`. No añadas saludos ni comentarios.

---

## Recursos de la skill

Carga estos archivos cuando los necesites — **no todos a la vez**. Sigue progressive disclosure.

| Archivo | Cuándo leerlo |
|---|---|
| `references/execution-principles.md` | **Antes de Fase 4**. Lectura obligatoria. 10 principios + reglas de presentación + status labels. |
| `references/response-format.md` | **Al final**. Plantilla literal de la respuesta al usuario + criterios de aceptación. |
| `references/analysis-workflow.md` | Al inicio. Detalle operativo de las 8 fases con checklists. |
| `references/appian-objects-guide.md` | Antes de Fase 2 (cómo reconocer cada objeto Appian) y durante Fase 4. |
| `references/bpmn-mapping.md` | Antes de invocar `process-modeler`. Estrategia híbrida BPMN XML + Mermaid Tipo C. Mapeo Appian → BPMN 2.0. |
| `references/mermaid-rules.md` | Antes de generar **cualquier** diagrama Mermaid. Tipos A, B, C. |
| `references/security-rules.md` | Al inicio de Fase 2 y antes de escribir cualquier documento. Patrones de detección y enmascarado. |
| `references/presentation-rules.md` | Antes de Fase 4. 10 reglas operativas de distribución y legibilidad. |
| `agents/interface-analyzer.md` | Como prompt del subagente de Fase 4.1. |
| `agents/data-modeler.md` | Como prompt del subagente de Fase 4.2. |
| `agents/integration-security-analyzer.md` | Como prompt del subagente de Fase 4.2. |
| `agents/process-modeler.md` | Como prompt del subagente de Fase 4.2. |
| `agents/interface-spec-writer.md` | Prompt del subagente de Fase 4.5 (solo `rebuild`). |
| `agents/logic-spec-writer.md` | Prompt del subagente de Fase 4.5 (solo `rebuild`). |
| `agents/backlog-writer.md` | Prompt del subagente de Fase 4.5, tras los dos anteriores (solo `rebuild`). |
| `agents/pdf-publisher.md` | Como prompt del subagente de Fase 7 (si `pdf: true`). |
| `agents/dashboard-publisher.md` | Como prompt del subagente de Fase 7 (si `dashboard: true`). |
| `assets/markdown-templates/*.md` | Como base de cada documento de la Fase 4. **Cópialos** a `_doc_generada/` y rellénalos con datos reales. |
| `scripts/inventory.sh` | Fase 2. Primer barrido bruto. |
| `scripts/parse_export.py` | Fase 2-3. Inventariado estructurado + grafo. Soporta formato Haul y antiguo. |
| `scripts/build_summary.py` | Fase 6.5. Consolida `summary.json`. |
| `scripts/detect_secrets.sh` | Fase 2 y antes de escribir documentos. |
| `scripts/render_diagrams.sh` | Fase 5. Renderiza `.mmd` → `.svg` con `mmdc`. |
| `scripts/validate_mermaid.py` | Después de cada bloque Mermaid, antes de escribirlo. Soporta tipos A (flowchart), B (`erDiagram`) y C (lanes con `subgraph`). |
| `scripts/check_coverage.py` | **Validación final, siempre.** Gate de cobertura por tipo de objeto. Exit 1 = faltan objetos por documentar. |
| `scripts/check_spec_layout.py` | **Validación final, siempre.** Gate de estructura: layout, enlaces/anclas rotos, secciones de plantilla, placeholders. Exit 1 = documentos mal formados. |

---

## Estructura de salida (11 entregables)

Todo en `{ruta_export}/_doc_generada/`:

```
_doc_generada/
├── 00-resumen-ejecutivo.md
├── 01-funcional.md
├── 02-arquitectura.md            (+ diagrams/arquitectura.svg)
├── 03-modelo-datos.md            (+ diagrams/modelo-datos.svg)
├── 04-seguridad-grupos.md
├── 05-integraciones-consumidas.md
├── 06-apis-expuestas.md
├── 07-batches.md
├── 08-procesos-bpmn/             (un .bpmn + .mmd + .md por PM)
│   ├── indice.md
│   ├── {PM_1}.bpmn / .mmd / .md
│   └── ...
├── 09-valor-adicional.md
└── INVENTARIO.md

# Solo con `profundidad: rebuild` (Fase 4.5):
10-especificacion/
├── pantallas/{interfaz}.md (una por CADA interfaz) + indice.md
├── navegacion.md
├── reglas-catalogo.md
├── estados.md
├── procesos/{PM}-nodos.md
├── backlog.md
└── trazabilidad.md
```

Resumen rápido por documento (detalle en `references/analysis-workflow.md`):

| Doc | Contiene |
|---|---|
| `00-resumen-ejecutivo.md` | Hallazgos clave: volumen, integraciones críticas, procesos críticos, riesgos top, pendientes. |
| `01-funcional.md` | 3 niveles: **Pitch** · **Overview** · **Detalle por flujo**. Lenguaje de negocio, sin jerga Appian. |
| `02-arquitectura.md` | Arquitectura **de esta app concreta**. Diagrama Mermaid con nodos = objetos reales, agrupados por capas. |
| `03-modelo-datos.md` | Diagrama ER + tabla por Record Type + tabla por CDT. Cobertura 100%. |
| `04-seguridad-grupos.md` | Árbol jerárquico de groups + tabla por objeto sensible + matriz RACI grupos↔capacidades. |
| `05-integraciones-consumidas.md` | Por Integration: endpoint, método, auth (enmascarada), request/response, callers. |
| `06-apis-expuestas.md` | Por Web API: URL pública, método, auth, body, qué hace, grupos autorizados, caso de uso. |
| `07-batches.md` | Process models con start event temporal: nombre, frecuencia + cron, próximas ejecuciones, procesos hijos. |
| `08-procesos-bpmn/` | BPMN 2.0 por process model + `indice.md` con relaciones. |
| `09-valor-adicional.md` | **Sólo secciones con hallazgos reales**: constantes, expression rules reutilizables, decisions, sites, plugins, emails, errores, huérfanos, glosario, métricas, riesgos. |
| `INVENTARIO.md` | Tabla por categoría: nombre técnico, nombre visible, ruta XML/XSD, confianza, observaciones. |

---

## Dependencias opcionales

Comprueba al inicio de Fase 5 con `scripts/render_diagrams.sh --check`.

| Herramienta | Para | Si falta |
|---|---|---|
| `xmllint` | Validar `.bpmn` + parseo XML rápido | Usa Python `xml.etree.ElementTree`. |
| `@mermaid-js/mermaid-cli` (`mmdc`) | Renderizar `.mmd` → `.svg` | Deja `.mmd` embebido en `.md`. GitHub/VSCode lo renderizan al vuelo. |
| `unzip` | Descomprimir export `.zip` | Pide al usuario que lo descomprima. |

**BPMN se entrega como XML siempre**, sin renderizar a SVG en la skill. El usuario los abre en Camunda Modeler, draw.io, demo.bpmn.io o Signavio.

---

## Validación final (antes de devolver respuesta)

**0. Gate de cobertura — obligatorio y calculado, no "a ojo":**

```bash
python scripts/check_coverage.py {ruta}/_doc_generada --mode {onboarding|rebuild}
```

Debe salir **0**. Si sale 1, imprime los objetos que faltan: documéntalos y vuelve a ejecutarlo. **Adjunta la tabla de cobertura en la respuesta final.** En modo `rebuild`, un objeto solo puede quedar fuera si aparece en `10-especificacion/trazabilidad.md` como `DESCARTADO: {motivo}`.

**0-bis. Gate de estructura — también obligatorio:**

```bash
python scripts/check_spec_layout.py {ruta}/_doc_generada --mode {onboarding|rebuild}
```

Comprueba lo que la cobertura no ve: layout de `10-especificacion/`, enlaces y anclas rotos, secciones obligatorias de cada ficha de pantalla, criterios de reconstrucción verificables y placeholders sin rellenar. Debe salir **0**.

1. Existen los 11 ficheros en `{ruta}/_doc_generada/` (+ `10-especificacion/` si `profundidad: rebuild`).
2. `08-procesos-bpmn/` tiene un `.bpmn`/`.mmd`/`.md` por process model + `indice.md` los lista todos.
3. Cada diagrama Mermaid pasó por `scripts/validate_mermaid.py`. Los rechazados están sustituidos por tabla.
4. `scripts/detect_secrets.sh` no encuentra secretos sin enmascarar en los entregables — **incluida `10-especificacion/`**, donde se cita SAIL literal.
5. No hay placeholders ni texto genérico (`lorem ipsum`, `TBD`, `xxx`).
6. No has escrito nada fuera de `{ruta}/_doc_generada/`.
7. Cada conclusión importante tiene `Evidencia: {ruta}#{fragmento}` o está marcada como pendiente con responsable.
8. Las secciones de `09-valor-adicional.md` sin contenido real están **omitidas**, no incluidas vacías.

**Si alguna validación falla**, fíjala y re-valida antes de cerrar. No devuelvas respuesta con validaciones rotas.

---

## Resumen — qué hace bien la skill

- **No inventa**: cada hallazgo va con evidencia (ruta + fragmento) y status (✅/🔵/🟡/🔴).
- **Subagentes especializados**: 9 agentes en `agents/` — 3 en paralelo en Fase 4, 3 mas en Fase 4.5 (modo rebuild) y 2 publishers opcionales.
- **Iterative Refinement** en diagramas: validar → refinar → re-validar → fallback a tabla.
- **Progressive disclosure**: SKILL.md sólo orquesta; los detalles están en `references/`.
- **Degradación elegante**: sin `mmdc`, embebe `.mmd`. Sin `xmllint`, usa Python.
- **Trazabilidad**: cada documento enlaza al XML/XSD del que se extrajo.
- **Cero relleno**: secciones vacías se omiten; nunca placeholders.
