# Appian Toolkit — Generador de Código SAIL

Plugin de [Claude Code](https://claude.com/claude-code) para **generar, validar y hacer reingeniería inversa de Appian SAIL**. Sincronizado con las novedades de Appian 26.x en interfaces y Data Fabric (schemas verificados contra la documentación oficial vía MCP `appian-docs`).

## Qué incluye

| Componente | Qué hace |
|---|---|
| **Skill `appian-sail-generator`** | Genera interfaces SAIL en dos fases: mockup estático (`local!` + `a!map()`) listo para pegar en Interface Designer, y conversión funcional conectada a record types (`a!queryRecordType`, `a!recordData`, `a!queryRecordByIdentifier`, `ri!`). Incluye schemas JSON de ~140 funciones SAIL, catálogo de 1.100+ iconos, y guías de layouts, componentes, lógica y null-safety. |
| **Skill `appian-reverse-engineering`** | A partir de un export Appian (formato Haul), produce 11 documentos de análisis (funcional, arquitectura, modelo de datos, seguridad, integraciones, APIs…), diagramas BPMN 2.0 y SVG. Enmascara secretos automáticamente. |
| **Agente `appian-functional-analyst`** | Análisis funcional: transcripciones y requisitos dispersos → documentación estructurada, pantallas, historias de usuario. |
| **6 subagentes SAIL** | `sail-schema-validator`, `sail-icon-validator`, `sail-code-reviewer` (gate de validación en paralelo), `sail-dynamic-converter` (mockup → funcional), `sail-interface-splitter` (refactor en componentes), `sail-validation-implementer` (implementa validaciones de una definición de pantalla). |
| **Scripts Python** | Convierten exports `recordTypeHaul` (XML o ZIP) en el markdown de contexto de modelo de datos que necesita la Fase 2. |

## Instalación

Como marketplace de Claude Code (recomendado):

```bash
claude plugin marketplace add raulogm077/Generador-Codigo-Sail
```

```bash
claude plugin install appian-toolkit@generador-codigo-sail
```

O clonando el repo y cargándolo directamente:

```bash
git clone https://github.com/raulogm077/Generador-Codigo-Sail.git
```

```bash
claude --plugin-dir ./Generador-Codigo-Sail
```

**Requisitos**: Claude Code. Opcionales: Python 3.8+ (scripts de Fase 2), MCP `appian-docs` (consultas a documentación oficial) y un MCP de Appian con `validateExpression` para validación contra entorno real.

## Uso rápido

- *"Hazme un dashboard de casos con KPIs y un grid"* → mockup estático en `output/<nombre>.sail`.
- *"Ahora hazlo funcional y conéctalo a mis records"* → necesita el modelo de datos (ver abajo); produce `output/<nombre>-functional.sail`.
- *"Divide esta interfaz en componentes reutilizables"* → `sail-interface-splitter`.
- Pega un error del Interface Designer → el skill lo mapea contra su catálogo de 14 categorías de errores comunes y lo corrige in situ.

**Modelo de datos (Fase 2)**: genera `context/data-model-context.md` en tu proyecto desde un export de record types:

```bash
python scripts/xml_to_appian_recordtype_md.py mi-record.xml -o context/data-model-context.md
```

El plugin **nunca inventa UUIDs** — si no tiene el modelo de datos, se detiene y lo pide.

## Settings por proyecto (opcional)

Crea `.claude/appian-toolkit.local.md` en tu proyecto (plantilla en `skills/appian-sail-generator/examples/appian-toolkit.local.md.example`):

```markdown
---
brand_hex: "#0050A0"            # paleta corporativa (HEX, nunca "ACCENT")
data_model_context: "context/data-model-context.md"
output_dir: "output"
ai_components_available: true    # false → nunca genera a!chatField/a!callLanguageModel
prefer_native_kpis: true         # Fase 2: a!kpiField nativo cuando aplica
---
# Notas libres del proyecto (entorno, convenciones…)
```

Este fichero es local (está en `.gitignore`) y no se versiona.

## Novedades v2.4.0 — sincronización con Appian 26.x

- **Corregido**: `a!gridRowDeletion`/`rowDeletions` no existen en Appian (se documentaban por error); `fetchTotalCount` NO es obligatorio (por defecto `false` desde 24r4 — solo cuando se lee `.totalCount`).
- **Nuevos en schemas**: `a!kpiField`, `a!queryRecordByIdentifier`, `a!selectionFields`, `a!eventHistoryListField`+`a!eventData`, `a!chatField`+`a!callLanguageModel` (IA), charts records-powered (`data`+`config`).
- **Parámetros 26.x**: `a!tabLayout(selectedTab)`, `a!tabItem(id, loadBehavior)`, grids con `smartSearchType`/`searchFields`/`showManageFiltersMenu`, `selectionStyle` sutiles, `borderStyle: LIGHT_WITH_OUTER_BORDERS`, reordenación de filas en grids editables, color `WARN`, stamp `EXTRA_TINY`.
- Los parámetros nuevos llevan `introducedIn` en los schemas; si tu entorno va por detrás (las upgrades mensuales de Appian Cloud son opt-in), verifica disponibilidad vía `appian-docs`.

## Estructura

```
.claude-plugin/          plugin.json + marketplace.json
agents/                  7 agentes (validadores, conversor, splitter, analista funcional)
skills/
  appian-sail-generator/     SKILL.md, schemas JSON, guías UI/lógica/conversión, scripts, ejemplos
  appian-reverse-engineering/ SKILL.md, agentes propios, plantillas de documentos, scripts
```

## Autor y licencia

Raúl Gómez Moya — [raulogm077](https://github.com/raulogm077)

Sin licencia de uso explícita por ahora (todos los derechos reservados). Abre un issue si quieres usarlo más allá de consulta.
