---
name: appian-sail-generator
description: Generate Appian SAIL UI expressions from natural-language requirements — both static mockups and functional interfaces wired to live record-type data. Use this skill whenever the user wants to build, design, mock, or generate an Appian interface, form, dashboard, grid, wizard, KPI page, or any SAIL component; whenever they ask to "vibe code" Appian or convert a mockup into a functional interface backed by record types; or whenever they mention `a!localVariables`, `a!queryRecordType`, `a!recordData`, `ri!`, `recordType!`, or paste SAIL expressions and ask for fixes/improvements. Use it even when the user does not say "SAIL" explicitly — phrases like "make an Appian screen to capture X", "I need a dashboard for our Case records", or "connect this mockup to our Employee records" all qualify. The skill knows how to ask follow-up questions when requirements are ambiguous instead of inventing details.
metadata:
  version: 2.4.0
  author: Raúl Gómez Moya
  mcp-server: appian-mcp-server
compatibility: Works in Claude.ai and Claude Code. Phase-2 scripts require Python 3.8+. Optional Mode-A validation requires Appian VPN + MCP server. In Claude Code, ALL six bundled agents (validators + converter + splitter + validation-implementer) ship with the appian-toolkit plugin and are auto-discovered (no install step) and MUST be invoked as native subagents (Mode B) — never inline — when their respective triggers fire.
---

# Appian SAIL Generator

A two-phase workflow for producing Appian SAIL UI expressions (agent-driven in Claude Code, inline in Claude.ai):

- **Phase 1 — Mockup**: generate a static SAIL interface using `local!` variables and `a!map()` sample data. The result is paste-ready in Appian Interface Designer for visual review.
- **Phase 2 — Functional conversion** (optional): transform the mockup into a data-driven interface that queries live record types via `a!queryRecordType()` / `a!recordData()` and uses `ri!` rule inputs for forms.

The skill bundles:
- The full set of UI / logic / conversion guidelines that govern valid SAIL.
- Six specialised sub-agents for generation, conversion, refactoring, and validation.
- Python scripts that convert Appian `recordTypeHaul` XML exports into the data-model context markdown that Phase 2 needs.

---

## 🆕 Appian 26.x awareness (schemas synced 2026-08 against docs 26.6)

Appian Cloud releases monthly (26.1, 26.2, …). The bundled schemas were re-verified against the official docs; highlights the generator must know:

**Interfaces**
- `a!kpiField` — native KPI (25.x+). **Records-only** (`data:` = record type ref / `a!recordData()`): never in mockups; preferred in Phase 2 when the standard look is acceptable. See `display-conversion-kpis.md` § Pattern 0.
- `a!tabLayout` gained `selectedTab`/`selectedTabSaveInto`, and `a!tabItem` gained `id` + `loadBehavior: "ON_LOAD"|"ON_TAB_SELECT"` (26.6). ⚠️ Default is that ALL tabs evaluate on page load; `ON_TAB_SELECT` skips validations until the tab is opened — never on tabs with validated inputs.
- `a!gridField` (read-only): new `selectionStyle` values `CHECKBOX_SUBTLE_HIGHLIGHT`/`SUBTLE_HIGHLIGHT` (26.3), `borderStyle: "LIGHT_WITH_OUTER_BORDERS"` (26.5), and record-only `pagingControls`, `showManageFiltersMenu` (26.5), `smartSearchType: "SEMANTIC"|"LEXICAL"` + `searchFields` (26.6), `similarityScoreThreshold`.
- `a!gridLayout` (editable): drag-and-drop row reordering via `allowRowReordering` + `rowOrderData` + `rowOrderField`. ⛔ `a!gridRowDeletion`/`rowDeletions` never existed — older versions of this skill documented them by mistake.
- `WARN` (yellow) color now valid on tags, stamps and rich text (26.6); stamps gained `size: "EXTRA_TINY"` (26.6).
- AI: `a!chatField` + `a!chatMessage` + `a!callLanguageModel` (advanced/premium tiers; not in portals/offline). Only generate when the user explicitly asks for an AI chat.
- `a!eventHistoryListField` + `a!eventData` — record-events history (records-only; not portals/offline).

**Data Fabric**
- `a!queryRecordByIdentifier(recordType, identifier, fields, relatedRecordData)` — the correct way to fetch ONE record (summary views, UPDATE pre-load). No pagingInfo; ≤250 related rows; composite keys 26.3+; never in loops. See `conversion-queries.md` `{#queries.query-by-identifier}`.
- `a!queryRecordType` also accepts `relatedRecordData`; `fetchTotalCount` **defaults to false** (24r4+) — set true only when `.totalCount` is read (old skill versions wrongly said "always required").
- `a!measure` supports `filters`, `label`, `formatValue`, and `DISTINCT_COUNT`.
- Platform (design-time, affects advice): synced record types no longer have a row limit (26.3); unsynced record types support relationships/record-level security/custom fields on MariaDB/MySQL (26.2) and PostgreSQL (26.5); DB views as source (26.2); composite primary keys (26.3); external documents via record types (26.3+).

**Environment caution**: parameters tagged `introducedIn` 26.x in the schemas may not exist yet in an environment that lags behind (Appian Cloud monthly upgrades are opt-in). If Designer rejects a parameter that is in the schema, verify the environment's version and the function-versions page via the `appian-docs` MCP — don't assume the schema is wrong.

---

## ⚙️ Per-project settings — `.claude/appian-toolkit.local.md` (optional)

At **Step 0.5 (pre-flight)**, check whether `<working-dir>/.claude/appian-toolkit.local.md` exists. If it does, parse its YAML frontmatter and honor these fields for the whole session. If it doesn't, use the defaults silently — never ask the user to create it.

| Field | Effect | Default when absent |
|---|---|---|
| `enabled` | `false` → ignore the whole file | `true` |
| `brand_hex` / `brand_hex_soft` | Project's corporate palette. Use the HEX (never `"ACCENT"`) on `a!buttonWidget.color`, `a!tagItem.backgroundColor`, `a!tabLayout.highlightColor`, `a!stampField.backgroundColor`, `a!cardLayout.decorativeBarColor`, etc. A reference image provided in the request still wins (Step 0.6 extraction). | `null` → Step 0.6 extraction, else `"ACCENT"` |
| `data_model_context` | Path (relative to working dir) of the Phase-2 data-model markdown | `context/data-model-context.md` |
| `output_dir` | Where generated `.sail` files are written | `output` |
| `ai_components_available` | `false` → NEVER generate `a!chatField` / `a!chatMessage` / `a!callLanguageModel` / `a!agentChatField` (environment lacks the advanced/premium AI tier). Validators treat their presence as a blocking error. | `true` |
| `prefer_native_kpis` | Phase 2: convert card KPIs to `a!kpiField` whenever Pattern 0's decision rule allows it (`display-conversion-kpis.md`) | `true` |

The markdown **body** of the file is free-form project context (environment name, constraints, verified-capability notes) — read it and respect it. Do **not** store Appian version numbers in the frontmatter (no version pinning in configs; verify feature availability at generation time via `appian-docs` or `appian-dev validateExpression`). Template: `examples/appian-toolkit.local.md.example`. The file is user-local: when the project uses git, `.claude/*.local.md` belongs in `.gitignore`.

---

## ⛔ Core principle: Ask before inventing — STOP signals

This is non-negotiable. SAIL is unforgiving — invented UUIDs, invented field names, invented record types, or invented business rules will produce broken interfaces and untrustworthy code.

### Hard STOP signals (do not generate, ask first)

If **any** of these is true, stop and ask the user before writing a single line of SAIL:

1. **Functional/dynamic request without data model** — the user said "functional", "dynamic", "use real data", "connect to <RecordType>", "with our records", or "make it work with the data", **AND** `context/data-model-context.md` is either missing or still a placeholder. → Ask for the markdown, the `recordTypeHaul` XML, or the record-type + field UUIDs by hand. **Never invent a UUID. Ever.**
2. **Form without intent** — the request says "form for X" but doesn't specify CREATE vs UPDATE vs both, or doesn't say whether it's a start form for a process model. → Ask: create/update/both? Start form (need `model.json`)?
3. **Vague business rule** — the user mentioned a rule but the details are too vague to encode (e.g. "validate the email", "limit to admins", "show only relevant cases"). → Ask for the exact predicate.
4. **Relationship traversal without confirmed name** — UI shows a field from a related record but you don't have the relationship name from `data-model-context.md`. → Ask, or read the markdown. **Never invent a relationship.**
5. **Ambiguous single-component vs full-page** — request like "a case management interface" where it's unclear whether the user wants one widget or a whole page. → Ask one short clarifying question.

### Auto-defaults (do NOT ask)

These you decide yourself with sensible defaults aligned to the guidelines, and note in code/comments:

- Colour scheme (use the palette in `references/01-mockup-rules.md` § 6).
- Pixel widths, spacing values, default page sizes, sort orders.
- Specific sample-data values (case numbers, names, dates) — pick realistic-looking statics.
- Whether to add icons in obvious places (status indicators, action buttons).
- 5–8 sample rows for a grid unless asked otherwise.

Asking too much is as bad as asking too little. See `references/05-elicitation-guide.md` for the full playbook (default-then-confirm patterns, batched questions, anti-patterns).

### The invention test (apply when tempted to "fill in a gap")

Before writing any identifier, run this test:
- Is it a **UUID**? → NEVER invent. Stop and ask.
- Is it a **record-type name / field name / relationship name**? → NEVER invent if functional. For mockups, sample names are fine.
- Is it an **icon alias**? → NEVER invent. Grep `ui-guidelines/reference/rich-text-icon-aliases.md` first.
- Is it a **function name or parameter**? → NEVER invent. Grep `ui-guidelines/reference/schemas/*.json` first.
- Is it a **business rule**? → NEVER invent. Ask the user.
- Is it sample-data text, a colour, or a default sort order? → Default is fine, annotate with `/* ASSUMPTION: ... */`.

Full anti-invention protocol with worked examples: `references/08-anti-invention-protocol.md`.

---

## Workflow

### Step 0 — Categorise the request

Read the user's request and classify it before reading any further guideline files.

**Single component vs full page** — the literal wording is the strongest signal:
- "A grid that shows…" / "a card group of…" / "a chart of…" → **single component** (output: just `a!gridLayout(...)`, `a!cardGroupLayout(...)`, etc.)
- "A page / dashboard / interface / screen / wizard / form for…" → **full page** (output: `a!headerContentLayout` / `a!formLayout` / `a!wizardLayout` / `a!paneLayout` wrapping content)

**Mockup vs functional**:
- Default to **mockup only** unless the user explicitly says "functional", "dynamic", "use our records", "connect to <RecordType>", or "make it work with real data".
- If the user says "make a functional dashboard for our Cases" in a single shot, do Phase 1 then Phase 2 — but ask for the data-model-context before starting Phase 2 if you don't have it (see Step 3).

If categorisation is ambiguous (e.g. "a case management interface" — page or component? mockup or functional?), ask one short clarifying question. Don't ask three.

### ⚙️ Step 0.4 — Subagent availability check (Claude Code only, no install needed)

**Why this is now trivial.** This skill ships inside the `appian-toolkit` plugin, which bundles the six validator/converter subagents (`sail-schema-validator`, `sail-icon-validator`, `sail-code-reviewer`, `sail-dynamic-converter`, `sail-interface-splitter`, `sail-validation-implementer`) at the plugin root, in `../../agents/`. **Claude Code discovers plugin agents automatically** — there is no install step, no copy into `~/.claude/agents/`, and no restart. Earlier versions of this skill shipped an installer script that copied the agents into `~/.claude/agents/`, because skill-bundled agents were not discoverable; packaging as a plugin removed that failure mode entirely, and the script was deleted in v2.6.0. **Never copy agent files by hand** — a user-level copy shadows the plugin's and then drifts from it.

**When to skip.** Skip entirely in Claude.ai (no `Agent` tool with `subagent_type` — nothing to check).

**What to do:**

1. **Check the subagent list.** Read your system prompt's "Available agent types". If `sail-schema-validator`, `sail-icon-validator`, and `sail-code-reviewer` are present → go to Step 0.5. This is the expected case.

2. **If they are missing**, the plugin has not loaded. Do **not** try to install anything. Ask the user to run `/reload-plugins`, or to restart Claude Code. Verify the plugin is enabled with:
   ```bash
   claude plugin list
   ```
   It should show `appian-toolkit@skills-dir` as enabled.

3. **If the user cannot reload now**, fall back to spawning `general-purpose` with the agent file content loaded inline as instructions — functionally equivalent but slower. Read each agent's instructions from `../../agents/sail-<role>.md`.

**Never fall through to Mode C (inline validation) in Claude Code just because a subagent looks unregistered.** Reloading the plugin is always the correct fix.

### 🛑 Step 0.5 — PRE-FLIGHT GATE (mandatory, before any other step)

**This gate is a precondition for writing SAIL. If you cannot answer "yes" to every question below, do not proceed to Step 1.** Skipping this gate is the most common cause of broken output.

Walk through this checklist explicitly — don't just "feel" your way through it:

#### Gate A — Anti-invention check
- [ ] If the request is **functional/dynamic**, do I have `context/data-model-context.md` populated with real record-type definitions (not the placeholder)? If no → STOP, ask the user (Hard STOP #1).
- [ ] If the request is a **form**, do I know whether it's CREATE / UPDATE / both / a start form? If no → STOP, ask (Hard STOP #2).
- [ ] If the user mentioned a **specific business rule or validation**, do I have its exact predicate? If no → STOP, ask (Hard STOP #3).
- [ ] If the UI shows a **related-record field**, do I have the relationship name from `data-model-context.md`? If no → STOP, read or ask (Hard STOP #4).

#### Gate B — Schema-file loading (read these BEFORE writing SAIL)
Load these files into context now. Do not write any SAIL until they are loaded:

- [ ] **Always**: `ui-guidelines/reference/schemas/layouts-schema.json` — the layout vocabulary.
- [ ] If using **icons** (any `icon: "..."` value): `ui-guidelines/reference/rich-text-icon-aliases.md`. This is non-optional. Icons are validated by exact string match against this file.
- [ ] If using **form inputs** (text/dropdown/date/radio/checkbox/etc.): `ui-guidelines/reference/schemas/input-components-schema.json`.
- [ ] If using **buttons**: `ui-guidelines/reference/schemas/button-components-schema.json`.
- [ ] If using **grids**: `ui-guidelines/reference/schemas/grid-components-schema.json`.
- [ ] If using **charts**: `ui-guidelines/reference/schemas/chart-components-schema.json`.
- [ ] If using **read-only displays** (tags, stamps, rich text, images): `ui-guidelines/reference/schemas/display-components-schema.json`.
- [ ] If using **arrays, loops, null checks, pattern matching, dates, or grid selection**: `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` first, then the specific topic file.

#### Gate C — Instruction-file loading
- [ ] Top-level layout instructions: the matching `ui-guidelines/layouts/*.md` for your chosen layout (`form-layout-instructions.md`, `wizard-layout-instructions.md`, `pane-layout-instructions.md`, or `header-content-layout-instructions.md`).
- [ ] Non-trivial components: load `ui-guidelines/components/*.md` for grids, charts, rich text, etc.
- [ ] Cross-cutting patterns: load `ui-guidelines/patterns/*.md` for KPI rows (`kpis.md`), card lists (`card_lists.md`), tabs (`tabs.md`), messages (`messages.md`) if used.

#### Gate D — Rule recall
- [ ] I have the floor rules from `references/01-mockup-rules.md` in mind (or in context).
- [ ] I know the 14 categories in `references/06-common-syntax-errors.md` and will check against them before declaring done.

**The rule applied while writing**: for every parameter you set on every component, that parameter and (if enumerated) its value must appear in the schema. If you cannot find it: stop, re-grep the schema, and if it's genuinely absent — do not use it.

Detailed pre-flight protocol with grep commands: `references/07-claude-ai-inline-validation.md` § Pre-flight.

### 🎨 Step 0.6 — Visual reference analysis (mandatory when the user provides a reference image)

**Skip this step only if there is no reference image.** When the user attaches a screenshot, mockup, or any visual reference, structural fidelity is not enough — colour, shape and material fidelity matter too. Skipping this step is the most common cause of "no syntax errors but it doesn't look like the design" feedback.

Before writing any SAIL, answer each question explicitly:

#### 0.6.A — Extract the brand palette

- [ ] What is the **dominant brand / accent colour** in the reference (active tabs, primary buttons, badges, selected pills)? → write it down as a 6-digit HEX (e.g. `#7C3AED`). If the colour is desaturated/light too (badge backgrounds, hover states), capture both the saturated and the soft tint (e.g. `#7C3AED` + `#EDE9FE`).
- [ ] What is the **page background**? (Often a near-white gray like `#F5F6F8`, or pure white.)
- [ ] What is the **secondary/muted text colour**? (Often a mid-gray like `#6B7280`.)
- [ ] Are there **status colours** in the design (success green, warning amber, error red)? → capture those HEX too.

Record the palette as a comment at the top of the generated `.sail` file:

```
/* PALETTE — extracted from reference image
 *   brand:        #7C3AED
 *   brand-soft:   #EDE9FE
 *   page-bg:      #F5F6F8
 *   text-muted:   #6B7280
 */
```

#### 0.6.B — Use HEX, not `"ACCENT"`, for any element that must match the brand colour

`"ACCENT"` inherits the **environment's theme colour**, which is set per Appian site / portal — it is **not guaranteed to match the reference image**. When the user provided a reference, every element that visually carries the brand colour must use the HEX explicitly:

| Where | Use HEX instead of `"ACCENT"` |
|---|---|
| `a!buttonWidget(color: ...)` for primary/CTA buttons | ✅ |
| `a!tagItem(backgroundColor: ...)` for branded badges | ✅ |
| `a!tabLayout(highlightColor: ...)` for the active tab underline | ✅ |
| `a!cardLayout(borderColor: ..., decorativeBarColor: ...)` for highlighted cards | ✅ |
| `a!stampField(backgroundColor: ..., contentColor: ...)` for circular icon stamps | ✅ |
| `a!richTextItem(color: ...)` for branded inline text/links | ✅ |
| `a!gaugeField(color: ...)` / `a!progressBarField(color: ...)` | ✅ |
| `a!sectionLayout(labelColor: ...)` for branded section headings | ✅ |

`"ACCENT"` is still fine when the **user did not provide a reference** (the mockup just adopts whatever theme the environment has).

#### 0.6.C — Identify non-standard shapes and pick the closest native equivalent

Look at the reference for any visual primitive that `a!buttonWidget` / `a!cardLayout` / `a!tagField` don't render by default. Common patterns:

| Reference pattern | Closest SAIL equivalent | Note |
|---|---|---|
| Primary button (any corner radius) | `a!buttonWidget(style: "SOLID" or "OUTLINE", color: "#HEX")` | Button **corner radius (sharp / rounded / pill) is configured at the Appian site level**, not in SAIL — trust the site config, don't try to force a different radius via stamp/richText tricks. |
| Filled circular icon chip (avatar-like) | `a!stampField(icon: "...", backgroundColor: "#HEX", contentColor: "#FFFFFF", shape: "ROUNDED", size: "SMALL")` | Use stamps for non-clickable circular badges. Add `link:` if it must be clickable. |
| Pill-shaped tag with brand fill | `a!tagItem(text: "...", backgroundColor: "#HEX")` inside `a!tagField` | Tags are pills by default. |
| Selected/unselected toggle group (e.g. Dine In / To Go / Delivery) | `a!buttonWidget` with `style: if(local!sel = "X", "SOLID", "LINK")` + `color: if(...)` returning HEX or `"SECONDARY"` | Inline ternary on `style` and `color`. |
| Edge-to-edge photo at the top of a card | Outer `a!cardLayout(padding: "NONE")` containing `a!imageField(size: "GALLERY", marginBelow: "NONE")` followed by an inner `a!cardLayout(style: "TRANSPARENT", padding: "STANDARD")` for the text | Card-in-card is the only way to mix "no padding for the image" with "padding for the text". |
| Pure circular interactive icon (no button chrome) | `a!richTextDisplayField(value: a!richTextIcon(icon: "...", color: "#HEX", link: a!dynamicLink(...)))` | `a!richTextIcon` supports `link:` directly. |
| Small circular avatar thumbnail | `a!imageField(images: a!webImage(source: "..."), size: "EXTRA_SMALL", style: "AVATAR")` | `style: "AVATAR"` is the documented way to get circular images. |

If the reference uses a shape that has **no acceptable native equivalent**, document the gap as a `/* TODO-DESIGN: ... */` comment and pick the closest match.

#### 0.6.D — Decide what to do about real photographs

The reference often shows real photos (product shots, food, faces). For a mockup:

- [ ] If the photos are decorative and you have **stable public URLs** (specific Unsplash photo IDs, brand asset URLs), use them via `a!webImage(source: "https://...")`. Avoid random/keyword URLs that resolve to different images on each load.
- [ ] If you don't have stable URLs, use **placeholder URLs that obviously look like placeholders** (e.g. `placehold.co/600x400/HEX/HEX?text=Edamame`) so the user immediately understands they need to swap them. Don't try to fake real photos with text-on-coloured-box placeholders that look "almost right" — they are visually misleading.
- [ ] **Tell the user explicitly** in the summary that images are the one thing a SAIL mockup cannot match pixel-perfectly without real Appian documents (`a!documentImage(document: cons!...)`).

#### Pass criterion

When all four sub-gates above are answered, paste the palette comment at the top of the file and proceed. If the user did not provide a reference image, skip this entire step.

### Step 1 — Plan the layout (full page only)

Skip for single components.

Choose top-level layout in this order of preference:
1. **`a!formLayout`** — single-step create/update forms.
2. **`a!wizardLayout`** — multi-step forms with `validations` per step.
3. **`a!paneLayout`** — full-height (100vh) split views where panes scroll independently (e.g. master/detail inbox).
4. **`a!headerContentLayout`** — everything else (dashboards, list pages, detail pages).

Read the matching layout instruction file from `ui-guidelines/layouts/` (e.g. `form-layout-instructions.md`) before writing the layout — it has templates, parameter rules, and width guidance.

Plan content arrangement:
- `a!columnsLayout` for major page sections (always at least one `AUTO` column per layout).
- `a!sideBySideLayout` for icon-plus-text or label-plus-value groupings (one component per side-by-side item — never an array, never another sideBySide).
- `a!cardLayout` for content blocks. **Don't** wrap `a!cardGroupLayout` or lists of cards in an outer card — too much boxiness.

### Step 2 — Generate the mockup (Phase 1)

#### 🛑 Schema-first gate (mandatory, before writing any SAIL)

**Do not write a single line of SAIL before loading the relevant schema files.** Schemas are the only source of truth for which parameters exist on which components and which enumerated values each parameter accepts. Writing first and validating later is how syntax errors reach the user.

Mandatory loads, in order:

1. **Always load**: `ui-guidelines/reference/schemas/layouts-schema.json` — the layout vocabulary of every page.
2. **Load based on the components you'll use** (pick all that apply):
   - Forms with inputs → `ui-guidelines/reference/schemas/input-components-schema.json`.
   - Action buttons → `ui-guidelines/reference/schemas/button-components-schema.json`.
   - Read-only displays (tags, stamps, richText, images) → `ui-guidelines/reference/schemas/display-components-schema.json`.
   - Grids → `ui-guidelines/reference/schemas/grid-components-schema.json`.
   - Charts → `ui-guidelines/reference/schemas/chart-components-schema.json`.
   - Dynamic logic (`a!forEach`, `a!match`, array helpers) → `ui-guidelines/reference/schemas/expression-functions-schema.json`.
3. **Then load instruction files** for the specific components you'll instantiate — `ui-guidelines/layouts/*.md` for the top-level layout, `ui-guidelines/components/*.md` for non-trivial components (grids, charts, rich text), `ui-guidelines/patterns/*.md` for KPI rows, card lists, tabs, messages.
4. **If you'll use icons**: grep `ui-guidelines/reference/rich-text-icon-aliases.md` for every alias before writing it. Inventing icon names is one of the top causes of broken expressions.
5. **If you'll use arrays, loops, null checks, pattern matching, dates, or grid selection**: read `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` first, then load the specific topic file it points to.

**The check applied while writing**: for every parameter you set on every component, that parameter and (if enumerated) its value must appear in the schema. If you cannot find it: stop, re-grep the schema, and if it's genuinely absent — do not use it.

#### Delegation

Where sub-agent delegation is available (Claude Code via the `Agent` tool), the generation work can be delegated. Otherwise follow the same instructions inline.

Mockup rules (the absolute floor — see `references/01-mockup-rules.md` for the full list):

| Rule | Why |
|---|---|
| All expressions start with `a!localVariables()` | Required by SAIL |
| Sample data uses `local!` + `a!map()` only | Mockups are pure UX prototypes |
| Never use `ri!`, `recordType!`, `a!queryRecordType`, `a!recordData` | Phase 2 introduces these |
| Initialise control parameters as locals: `local!isUpdate: false()`, `local!cancel: false()` | Phase 2 transforms them to `ri!` |
| No `rule!` or `cons!` references unless the user names a specific one | Inline all logic |
| Use static hard-coded sample values — no `rand()`, no `now()`, no `today()` | Sample data must be stable across re-evaluations |
| Empty arrays must be type-initialised: `tointeger({})`, `touniformstring({})`, etc. | Untyped `{}` breaks `contains()`/`wherecontains()` |
| Null-safe comparisons use `if(...)`, not `and(...)` | `and()` does not short-circuit in SAIL |
| Operators use function syntax: `or(a,b)` not `a or b` | SAIL is not JavaScript |
| Inside grid columns, only `fv!row` is valid | Not `fv!index`, not `fv!item` |
| Inside `a!forEach`, use `fv!item`, `fv!index`, `fv!isFirst`, `fv!isLast` | `fv!row` is grid-only |

Write the output to `output/<descriptive-name>.sail` (create the `output/` directory at the working-directory level if it doesn't exist).

Annotate with comments — use the four canonical prefixes:
- `/* REQUIREMENT: ... */` — user-stated business rules.
- `/* TODO-CONVERTER: ... */` — work for the Phase 2 converter (field-setting, transform `local!` → `ri!`, convert custom search to `showSearchBox`, etc.).
- `/* TODO-DATA-MODEL: ... */` — fields or relationships that don't exist yet in the data model.
- `/* TODO: ... */` — process-model work (send email, configure webhook) that isn't a SAIL concern.

### Step 3 — Convert to functional (Phase 2, optional)

Only run this when the user has explicitly asked for a functional/dynamic/data-driven interface.

**Pre-flight check — the data-model context.** Phase 2 needs `context/data-model-context.md` containing the record-type UUIDs, field UUIDs, relationships, and actions. Three scenarios:

1. **User has the markdown already** — they paste it, point to a file, or it's already at `context/data-model-context.md`. Proceed.
2. **User has `recordTypeHaul` XML exports** (single XML files or a whole Appian application export ZIP) but no markdown. Generate it:
   ```bash
   # Single XML
   python scripts/xml_to_appian_recordtype_md.py path/to/record.xml -o context/data-model-context.md

   # Directory of XMLs or a zipped Appian application export
   python scripts/map_xml_to_appian_recordtype_md.py path/to/recordtype-xml-folder/
   python scripts/map_xml_to_appian_recordtype_md.py path/to/application-export.zip
   ```
   The `map_*` script produces one `data-model-context-<snake_case>.md` per record type; concatenate them into `context/data-model-context.md` if Phase 2 needs several record types.
3. **User has neither markdown nor XMLs** — they need to provide the record-type names, field names + UUIDs, data types, and relationship names + UUIDs manually, or export the records from Appian first. **Do not invent UUIDs.** Stop and ask.

**In Claude Code with `Agent` tool available, delegate the conversion to the `sail-dynamic-converter` agent as a subagent — this is required, not optional.** Invocation:
```
Agent(subagent_type="sail-dynamic-converter", description="...", prompt="...")
```
If `sail-dynamic-converter` is not in your `subagent_type` list, run `/reload-plugins` (Step 0.4) so the appian-toolkit plugin registers all six bundled agents. **Do not fall back to inline execution when the subagent is merely unregistered.** In Claude.ai or any environment without the `Agent` tool at all, then and only then, read `../../agents/sail-dynamic-converter.md` and follow its instructions yourself inline. Either way, the converter logic:
- Replaces `local!` arrays with `a!queryRecordType()` / `a!recordData()`.
- Transforms form fields to `ri!` rule inputs (and matches process-model `process_variables` exactly when the interface is a start form with a `model.json` available).
- Adds null-safe field-access patterns.
- Converts custom search/filter UX into `showSearchBox`/`userFilters` where appropriate.
- Resolves `TODO-CONVERTER` comments.

The converter requires an existing mockup file. Output goes to `output/<descriptive-name>-functional.sail`.

Detailed conversion playbook: `conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md` is the navigation index. Load focused modules from there (forms, displays, grids, charts, KPIs, validation) based on what's in the mockup.

### Step 4 — Validate (mandatory output gate)

**Validation is not optional. Generation is incomplete until validation passes with zero issues.** This is the gate that catches the five most common failure modes: invented functions, invented parameters, invalid enum values, invalid icons, and prohibited nesting.

#### 🚦 Mode selection — strict precedence (the order matters)

**Discover your mode by walking these three checks in order, top down. Stop at the first one that's true. Do NOT skip down to Mode C because it's faster or feels easier — Mode C exists only as a fallback when the higher modes are technically unavailable, and observed failure rates with Mode C are materially higher (e.g. invalid icon aliases slip through because human pattern-matching against a 1.139-entry catalog isn't reliable).**

1. **Mode A — MCP `validate_sail`**. If `mcp__appian-mcp-server__validate_sail` is in your tool list (typical when on the Appian VPN in Claude Code), it's the highest-fidelity validator because the Appian server runs the same checks the Designer runs. **Always supplement with Mode B's icon + code-review passes** because the MCP validator focuses on grammar, not icon catalog presence or 14-category structural review.

2. **Mode B — Subagent delegation via Agent tool (this is the default in Claude Code)**. Required when (a) you have the `Agent` tool and (b) `sail-schema-validator`, `sail-icon-validator`, `sail-code-reviewer` appear in your available `subagent_type` list. Spawn all three **in parallel in a single message** for efficiency. **This is non-negotiable when the agents are registered.**

   **Why exactly these three and not all six?** The validation gate runs *only* the three validation-purpose agents. The other three bundled agents (`sail-dynamic-converter`, `sail-interface-splitter`, `sail-validation-implementer`) have different triggers documented in their own workflow steps — running them at Step 4 would be incorrect:
   - `sail-dynamic-converter` belongs in **Step 3** (Phase 1 → Phase 2 conversion). Invoking it at validation time would attempt to convert a mockup that may not need conversion.
   - `sail-interface-splitter` is **on-demand**, fired when the user says "split" / "refactor" / "componentise" or when an interface has clearly grown past the ≥200-line splittable threshold.
   - `sail-validation-implementer` is **on-demand**, fired when the user provides a screen definition with validation rules and asks to wire them into an existing SAIL file.

   Each of those three, when their trigger fires, is also a mandatory subagent invocation in Claude Code — see the unified Agents table further down. The point of separating them is so the validation gate stays fast (three parallel reviewers) and focused, while the other three only spin up when there's actual work for them.

   If the agents are NOT in your subagent list, go back to **Step 0.4**: ask the user to run `/reload-plugins` so the appian-toolkit plugin registers its bundled agents, then resume here. **Do not fall through to Mode C just because the subagents aren't registered yet** — installing them is a one-shot setup cost that pays back every future invocation.

   If the user cannot restart in the current session, the acceptable bridge is to spawn `general-purpose` Agent three times in parallel, each loaded with the corresponding `../../agents/sail-<role>.md` content as its prompt. This is functionally equivalent to Mode B and still beats Mode C.

3. **Mode C — Inline self-validation (Claude.ai only, or any environment without `Agent` tool at all)**. This is the only legitimate use of Mode C: when subagent delegation is **technically unavailable**, not when it's merely inconvenient. Follow `references/07-claude-ai-inline-validation.md` precisely. The agent files in `agents/*.md` are then read as instruction sheets and executed inline — this is slower and more error-prone than the subagent path because you are simultaneously the author and the reviewer of the SAIL, so blind spots persist.

**Common anti-pattern to avoid:** picking Mode C in Claude Code because "the inline scan is faster." Mode C in Claude Code is a regression from the available tooling — every time it's been chosen as a shortcut, real issues have leaked through (recent example: two invalid `icon: "close"` references that the icon-validator subagent flagged immediately on a cross-check against `rich-text-icon-aliases.md`, but that an inline scan declared OK from memory).

The inline protocol is a three-pass scan over the generated `.sail` file:

**Pass 1 — Schema validation (every function and parameter)**
- For every `a!*(...)` call: confirm the function name exists in `ui-guidelines/reference/schemas/*.json`.
- For every parameter inside it: confirm the parameter name exists for that function in the schema.
- For every enumerated value (style, color, align, labelPosition, spacing, marginAbove, etc.): confirm the value is in the schema's `validValues` for that parameter.
- Method: open each relevant schema file; for each component you used, locate it in the schema and verify every key/value pair.

**Pass 2 — Icon validation (every `icon:` string)**
- Grep the generated file for `icon:` occurrences.
- For each one, grep `ui-guidelines/reference/rich-text-icon-aliases.md` for the exact alias string.
- If the alias is not in the file: it's invalid. Replace with a valid alias (search the file for a synonym) or remove the icon.
- Run this even on icons you "know" exist — Appian icon names are unique and your memory is unreliable.

**Pass 3 — Structural / null-safety / context review**
- Walk `references/04-validation-checklist.md` § Manual scan checklist top to bottom.
- Walk `references/06-common-syntax-errors.md` and check each of the 14 categories against the file.
- Pay particular attention to the five most common failure modes (see `references/07-claude-ai-inline-validation.md` § The Big Five).

#### Pass criteria — all must be true before declaring done

- Every function used exists in `ui-guidelines/reference/schemas/`.
- Every parameter set exists for its function in the schema.
- Every enumerated value matches the parameter's `validValues`.
- Every `icon: "..."` is an alias from `rich-text-icon-aliases.md`.
- Every structural rule from `references/04-validation-checklist.md` § Manual scan checklist passes.
- No syntax errors from the catalog in `references/06-common-syntax-errors.md` are present.
- No invented UUIDs, record types, fields, relationships, or business rules.

If any check fails, **fix and re-validate**. Do not present output to the user that hasn't passed.

### 🚦 Step 4.5 — FINAL OUTPUT GATE (binary, mandatory)

Before sending the response to the user, answer each of these out loud (in your reasoning). Every answer must be "yes". If any is "no": go back and fix; do not present.

0. **Validation mode honesty check.** Did I pick the highest mode actually available to me? Specifically: in Claude Code with the `Agent` tool, did I delegate to the three sail-* subagents (Mode B), or did I fall through to Mode C without first checking that the appian-toolkit plugin is loaded? If the latter — STOP and go back to Step 0.4. Mode C in Claude Code is not an acceptable shortcut.

0a. **Subagent invocation evidence.** If I used Mode B, did I get three distinct reports back (one per validator) within this conversation? If I claim "Mode B" but cannot point to three actual `Agent` tool invocations and their returned reports, that's a confabulation — go back and actually invoke them.

1. Did I run all three inline validation passes (schema, icon, structural)?
2. Are there zero invented UUIDs, record-type names, field names, or relationships in the file?
3. Is every `icon: "..."` value present (verbatim) in `ui-guidelines/reference/rich-text-icon-aliases.md`?
4. Is every function, parameter, and enum value present in `ui-guidelines/reference/schemas/*.json`?
5. Does the file have **zero** instances of: `a!sideBySideLayout` nested inside another, `a!columnsLayout`/`a!cardLayout`/arrays inside `a!sideBySideItem`, `a!richTextDisplayField` containing anything other than `a!richTextItem`/`a!richTextIcon`/`a!richTextBulletedList`/`a!richTextNumberedList`, an `a!columnsLayout` without at least one `AUTO` column?
6. Is every user-stated business rule captured as a `/* REQUIREMENT: ... */` comment, with no invented requirements added?
7. For mockups: zero `ri!`, zero `recordType!`, zero `a!queryRecordType`, zero `a!recordData`, zero grid record-only parameters?
8. For functional output: every `recordType!{uuid}` and `.fields.{uuid}` matches `context/data-model-context.md` exactly?
9. Is the file at `output/<descriptive-name>.sail` (or `-functional.sail`)?
10. If a reference image was provided: did I extract a brand HEX from it and use it (not `"ACCENT"`) on every brand-coloured parameter (`a!buttonWidget.color`, `a!tagItem.backgroundColor`, `a!tabLayout.highlightColor`, `a!stampField.backgroundColor`, `a!richTextItem.color`, etc.); annotate the palette as a top-of-file comment; pick documented native equivalents from `references/01-mockup-rules.md` § 8.3 for any non-standard visual primitives (circular icons, edge-to-edge images, pill toggles); and tell the user explicitly that photographs are the one element a mockup can't match without real Appian documents? (See `references/01-mockup-rules.md` § 8 and Step 0.6 above.)

If a "no" surfaces here, fixing is cheaper than shipping broken SAIL. Do the fix.

### Step 5 — Present and iterate

Tell the user:
- Where the file is (`output/<name>.sail`).
- Any `TODO-CONVERTER`, `TODO-DATA-MODEL`, or `TODO` comments that block real-world use, and what the user needs to do about each.
- What follow-up commands look like ("paste the Appian designer error and I'll fix it", "now make it functional and connect to Case", "split this into reusable components", "add a filter dropdown for status").

Iterate by editing the existing `.sail` file rather than regenerating from scratch.

### Step 6 — Error-fix workflow (when the user pastes an Appian Designer error)

This is the most common iteration path. The protocol:

1. **Read the existing `.sail` file** referenced in the conversation. Do not start from scratch.
2. **Locate the error**:
   - If the error message mentions a line number, jump there.
   - If the error mentions a component name or parameter, grep for it.
   - If the error is structural ("invalid nesting", "cannot evaluate property"), scan top-down for the matching pattern.
3. **Match the error to `references/06-common-syntax-errors.md`** — most Appian Designer errors map to one of the 14 categories there. Apply the canonical fix.
4. **If the error doesn't match the catalog**: grep the relevant guideline file (`logic-guidelines/*` for runtime/logic, `ui-guidelines/*` for component/layout, `conversion-guidelines/*` for record-type integration) — the error text usually contains the function or parameter name to grep for.
5. **Fix in place** using `str_replace` on the existing file. Don't regenerate the whole expression — preserve everything that wasn't broken.
6. **Re-run validation** (Step 4) before responding. Re-validation often surfaces secondary issues the first error hid.
7. **Tell the user** what the root cause was and what changed, briefly. If the error was a category from `06-common-syntax-errors.md`, name the category — it helps the user recognise the pattern next time.

When in doubt about the cause, ask the user to share the exact error text rather than guessing. Don't "fix" something that wasn't broken.

---

## Agents

The skill ships **six** specialised agents in `agents/`. Each has its own detailed instructions; read the agent file when you invoke that role. In Claude Code, **all six MUST be invoked as native subagents** (`Agent(subagent_type=...)`) when their trigger fires — never inline. The only exception is Claude.ai (no `Agent` tool at all), where inline execution is the only option.

### Unified trigger table — when does each agent fire?

| Agent | When it fires (trigger) | Where in workflow | Subagent invocation in Claude Code |
|---|---|---|---|
| `sail-schema-validator` | Always, after generating any `.sail` file | **Step 4 — Validation Gate** | **REQUIRED** — spawn in parallel with the other two validators |
| `sail-icon-validator` | Always, after generating any `.sail` file | **Step 4 — Validation Gate** | **REQUIRED** — spawn in parallel with the other two validators |
| `sail-code-reviewer` | Always, after generating any `.sail` file | **Step 4 — Validation Gate** | **REQUIRED** — spawn in parallel with the other two validators |
| `sail-dynamic-converter` | User asks for "functional" / "dynamic" / "use real data" / "connect to <RecordType>" interface, AND a mockup `.sail` file exists | **Step 3 — Phase 1 → Phase 2** | **REQUIRED** — one invocation when conversion is triggered |
| `sail-interface-splitter` | User says "split" / "refactor" / "componentise" / "break this up into reusable parts", OR generated SAIL has ≥200-line repeated blocks that warrant extraction | **On-demand** (after Step 4 passes; never as part of initial generation) | **REQUIRED** — one invocation when refactor is triggered |
| `sail-validation-implementer` | User provides a screen definition with validation rules + an existing SAIL file, and asks to wire the rules into the file | **On-demand** (Step 5 follow-up, or fresh request) | **REQUIRED** — one invocation when the task fires |

**Common confusion:** "If Mode B at the validation gate spawns three subagents, shouldn't all six run there?" → **No.** The three validators run at the gate because they review the just-generated SAIL. The other three perform *transformations* (convert, split, implement) that are different workflow stages with different inputs and triggers. Running them at the validation gate would mean either (a) performing a conversion the user didn't ask for, (b) splitting an interface that's still being authored, or (c) implementing validation rules that haven't been provided. Each runs when its own trigger fires — and *when it does*, it must run as a subagent in Claude Code, same rule as the validators.

**Concrete invocation pattern** (Claude Code, Phase 1 → Phase 2 example):
```
# Step 3 trigger fires (user said "now make it functional"):
Agent(subagent_type="sail-dynamic-converter", description="Convert mockup to functional", ...)

# Step 4 trigger fires automatically after Step 3 produces output:
[parallel in single message]
Agent(subagent_type="sail-schema-validator", ...)
Agent(subagent_type="sail-icon-validator", ...)
Agent(subagent_type="sail-code-reviewer", ...)
```

If any of these six is missing from your `subagent_type` list when its trigger fires, run **Step 0.4** (`/reload-plugins`) — the plugin ships all six. **Do not fall back to inline execution just because the subagent is unregistered.**

**How agents are invoked depends on environment:**

- **Claude Code with `Agent` tool available** → invoke as proper sub-agents using `subagent_type: <agent-name>`. They run in isolation with their own context window. **This is the required mode in Claude Code** (Mode B in Step 4). The agents ship at the root of the appian-toolkit plugin and are auto-discovered by Claude Code — no install step. If they are not listed, ask the user to run `/reload-plugins`; do not fall back to inline validation.
- **Claude.ai (this app) or any environment without the `Agent` tool** → agents are **not delegable**. Treat the agent files in `../../agents/` as **instruction sheets that you read and execute inline yourself**. Do not announce "delegating to the sail-schema-validator" — that's a hallucinated tool call. Instead: open the agent file, read its instructions, and apply them to the file directly. Output that says "I delegated to X agent and it passed" without an actual `Agent` tool call is invalid and will produce broken SAIL.

In Claude.ai specifically, the validation workflow is the **inline three-pass protocol in Step 4 Mode C**, not subagent delegation.

**Why this matters (lessons learned).** Earlier versions of this skill described the validators as "pre-installed in `.claude/agents/`", which is true for the *bundled* `.claude/agents/` inside the skill folder but **not** for the user-level `~/.claude/agents/` that Claude Code actually reads. The gap caused real bugs to ship — e.g. `icon: "close"` (not in the Appian icon catalog; should be `"times"`) passed an inline scan but would have been caught instantly by the cross-check the icon-validator subagent performs. v2.3 closes the gap structurally: the skill and its agents now ship together in the `appian-toolkit` plugin, where Claude Code discovers agents automatically. No install step can be skipped because there is none.

---

## Path conventions inside the skill

The bundled guideline files were authored with absolute-looking paths such as `/ui-guidelines/...`, `/logic-guidelines/...`, `/conversion-guidelines/...`, and `/context/data-model-context.md`. **Interpret these paths as relative to the skill root** (the directory containing this `SKILL.md`). For `context/data-model-context.md` specifically, the file lives at the user's working directory, not inside the skill — create it there during Phase 2 setup.

---

## Reference files (skill-authored)

| File | Purpose |
|---|---|
| `references/01-mockup-rules.md` | Condensed list of the must-never / must-always rules for Phase 1 mockups. Read at the start of Phase 1 — it is the canonical short form of the mockup rules. |
| `references/02-conversion-workflow.md` | High-level Phase 2 playbook with decision points. Use alongside `conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`. |
| `references/03-data-model-context-format.md` | What the `data-model-context.md` file must look like, with examples, and how to generate it from `recordTypeHaul` XML. |
| `references/04-validation-checklist.md` | Universal validation checklist to run before declaring output done. |
| `references/05-elicitation-guide.md` | The question playbook: what to ask, in what order, when to default vs ask. |
| `references/06-common-syntax-errors.md` | **Catalog of common SAIL syntax errors with canonical fixes.** First place to look when validation fails or the user pastes an Appian Designer error. Also a final self-check pass before declaring output done. |
| `references/07-claude-ai-inline-validation.md` | **The inline validation protocol for Claude.ai (no subagents).** Three-pass scan + the "Big Five" failure modes with detection patterns and fixes. Use this in Step 4 Mode C. |
| `references/08-anti-invention-protocol.md` | **The anti-invention protocol.** What can/cannot be invented; worked examples for each Hard STOP signal; how to recover when you catch yourself about to invent. |
| `examples/data-model-context-example.md` | A real `data-model-context.md` (from the OTIEC application) showing the expected format. |
| `examples/mockup-form-example.sail` | A clean reference mockup of a form (`a!formLayout`). Shows expected structure, `local!` patterns, control-parameter setup, and `TODO-CONVERTER` placement. |
| `examples/mockup-dashboard-example.sail` | A clean reference mockup of a dashboard (`a!headerContentLayout` with KPIs + grid). Shows columns layout, side-by-side composition, and custom search/filter pattern. |

### Component instruction files (skill-bundled)

These cover individual components and combinations of related components. Read the file whose component(s) you're using.

| File | Components covered |
|---|---|
| `ui-guidelines/layouts/form-layout-instructions.md` | `a!formLayout` + all titleBar templates (`a!headerTemplateSimple`, `a!headerTemplateFull`, `a!headerTemplateImage`, `a!sidebarTemplate`) |
| `ui-guidelines/layouts/wizard-layout-instructions.md` | `a!wizardLayout` + `a!wizardStep` + titleBar templates |
| `ui-guidelines/layouts/header-content-layout-instructions.md` | `a!headerContentLayout` |
| `ui-guidelines/layouts/pane-layout-instructions.md` | `a!paneLayout` + `a!pane` |
| `ui-guidelines/layouts/card-layout-instructions.md` | `a!cardLayout` + `a!cardGroupLayout` |
| `ui-guidelines/layouts/columns-layout-instructions.md` | `a!columnsLayout` + `a!columnLayout` |
| `ui-guidelines/layouts/sidebyside-layout-instructions.md` | `a!sideBySideLayout` + `a!sideBySideItem` |
| `ui-guidelines/layouts/tab-layout-instructions.md` | `a!tabLayout` + `a!tabItem` |
| `ui-guidelines/components/button-instructions.md` | `a!buttonWidget`, `a!buttonArrayLayout`, `a!buttonLayout` |
| `ui-guidelines/components/grid-field-instructions.md` | `a!gridField` (read-only / record-backed grids) |
| `ui-guidelines/components/grid-layout-instructions.md` | `a!gridLayout` (editable grids) |
| `ui-guidelines/components/rich-text-instructions.md` | `a!richTextDisplayField` + `a!richTextItem` / `a!richTextIcon` / `a!richTextBulletedList` / `a!richTextNumberedList` / `a!richTextImage` / `a!richTextListItem` / `a!richTextHeader` (deprecated) |
| `ui-guidelines/components/stamp-field-instructions.md` | `a!stampField` |
| `ui-guidelines/components/card-choice-field-instructions.md` | `a!cardChoiceField` |
| `ui-guidelines/components/chart-instructions.md` | All chart fields + chart configs + `a!colorSchemeCustom` |
| `ui-guidelines/components/image-field-instructions.md` | `a!imageField` |
| `ui-guidelines/components/tabular-data-display-pattern.md` | Tabular data display patterns |
| `ui-guidelines/components/toggle-field-instructions.md` | `a!toggleField` |
| `ui-guidelines/components/boolean-checkbox-instructions.md` | `a!booleanCheckboxField` |
| `ui-guidelines/components/signature-field-instructions.md` | `a!signatureField` (start forms / tasks only) |
| `ui-guidelines/components/record-and-user-pickers-instructions.md` | `a!pickerFieldRecords`, `a!pickerFieldUsers`, `a!pickerFieldGroups`, `a!pickerFieldUsersAndGroups` |
| `ui-guidelines/components/gauge-instructions.md` | `a!gaugeField` + `a!gaugeFraction` / `a!gaugeIcon` / `a!gaugePercentage` |
| `ui-guidelines/components/by-index-choice-fields-instructions.md` | `a!dropdownFieldByIndex`, `a!multipleDropdownFieldByIndex`, `a!radioButtonFieldByIndex`, `a!checkboxFieldByIndex` + `a!multipleDropdownField` |
| `ui-guidelines/components/video-and-web-content-instructions.md` | `a!videoField`, `a!webContentField` |

For components not in this table, the schema file (`ui-guidelines/reference/schemas/*-components-schema.json`) is the complete reference.

---

## ⛔ Critical hard rules (never violate)

These are the rules whose violation produces broken or runtime-erroring SAIL. The full list lives in the guidelines; this is the floor. Each rule prefixed with ⛔ has been a recurring failure mode — verify against it explicitly.

1. ⛔ **Never nest `a!sideBySideLayout` inside `a!sideBySideLayout`.** Each `a!sideBySideItem` holds exactly one component — never an array, never `a!columnsLayout`, never `a!cardLayout`, never another `a!sideBySideLayout`.
2. ⛔ **Never put arrays of components, `a!columnsLayout`, or `a!cardLayout` inside a `a!sideBySideItem`.**
3. ⛔ **Only `a!richTextItem` / `a!richTextIcon` / `a!richTextBulletedList` / `a!richTextNumberedList` / `a!richTextImage` / `a!richTextListItem` / `a!richTextHeader` are allowed inside `a!richTextDisplayField`.** Plain strings, other components (`a!webImage`, `a!stampField`, etc.) all break it — they must not appear inside richText. Note: `a!richTextHeader` is deprecated by Appian; prefer `a!headingField` (a standalone display field, NOT nested in richText) for new code. For non-icon images inline with text, use `a!richTextImage` with an `image` produced by `a!documentImage` / `a!userImage` / `a!webImage`; the standalone `a!imageField` cannot appear inside richText.
4. ⛔ **Every `a!columnsLayout` must have at least one `AUTO`-width `a!columnLayout`.** Without at least one AUTO, the layout collapses.
5. **`choiceValues` cannot be `null` or empty strings** (use `" "` if absolutely necessary).
6. **Record-only parameters and components cause runtime errors with local data** — grids: `showSearchBox`, `userFilters`, `recordActions`, `pagingControls`, `showManageFiltersMenu`, `smartSearchType`, `searchFields`, `similarityScoreThreshold`, `loadDataAsync`; components: `a!kpiField`, `a!eventHistoryListField`. In mockups use custom search/filter UX and card-based KPIs with `TODO-CONVERTER` comments instead.
7. **Never use runtime generators (`rand()`, `now()`, `today()`) for sample data** — hard-code static values. (Exception: `todate(today() + N)` inside data is acceptable if the resulting value is stable across re-evaluations.)
8. **Null-unsafe comparisons must be wrapped in `if(a!isNotNullOrEmpty(x), ..., default)`** — `and(a!isNotNullOrEmpty(x), x.prop = ...)` crashes because `and()` does not short-circuit.
9. **`save!value` is valid only inside the `value` parameter of `a!save(target, value)`** — never inside `if`/`and`/`or` conditions, never in the `target` parameter, never outside `a!save()`.
10. **No inline function definitions or lambdas**: `local!helper: function(x)(...)` is invalid SAIL. For repeated logic, duplicate inline and leave a `/* TODO: Extract to expression rule */` comment.
11. **Mockups never reference `ri!` or `recordType!`.** Functional code never re-introduces hard-coded `local!` arrays for what should be a query.
12. ⛔ **Don't assume a parameter exists — verify against the relevant `ui-guidelines/reference/schemas/*.json` file.** If the parameter isn't in the schema, it doesn't exist. No exceptions.
13. ⛔ **Don't assume an icon exists — verify against `ui-guidelines/reference/rich-text-icon-aliases.md`.** Every `icon: "..."` value must appear verbatim in that file. Inventing icon aliases ("chart-bar-icon", "user-circle", "checkmark") is the single most common source of runtime errors.
14. ⛔ **Don't assume a UUID, field name, record-type name, or relationship name exists** — verify against `context/data-model-context.md` (functional only). If it's not in the markdown, ask the user; do not invent.
