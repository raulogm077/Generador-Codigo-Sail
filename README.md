---
name: appian-sail-generator
description: Generate Appian SAIL UI expressions from natural-language requirements — both static mockups and functional interfaces wired to live record-type data. Use this skill whenever the user wants to build, design, mock, or generate an Appian interface, form, dashboard, grid, wizard, KPI page, or any SAIL component; whenever they ask to "vibe code" Appian or convert a mockup into a functional interface backed by record types; or whenever they mention `a!localVariables`, `a!queryRecordType`, `a!recordData`, `ri!`, `recordType!`, or paste SAIL expressions and ask for fixes/improvements. Use it even when the user does not say "SAIL" explicitly — phrases like "make an Appian screen to capture X", "I need a dashboard for our Case records", or "connect this mockup to our Employee records" all qualify. The skill knows how to ask follow-up questions when requirements are ambiguous instead of inventing details.
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
 
Where sub-agent delegation is available (Claude Code via the `Task` tool), the generation work can be delegated. Otherwise follow the same instructions inline.
 
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
In Claude Code with `Task` tool available, delegate the conversion to the `sail-dynamic-converter` agent (`subagent_type: sail-dynamic-converter`). In Claude.ai or any environment without subagents, read `agents/sail-dynamic-converter.md` and follow its instructions yourself inline. Either way, the converter logic:
- Replaces `local!` arrays with `a!queryRecordType()` / `a!recordData()`.
- Transforms form fields to `ri!` rule inputs (and matches process-model `process_variables` exactly when the interface is a start form with a `model.json` available).
- Adds null-safe field-access patterns.
- Converts custom search/filter UX into `showSearchBox`/`userFilters` where appropriate.
- Resolves `TODO-CONVERTER` comments.
The converter requires an existing mockup file. Output goes to `output/<descriptive-name>-functional.sail`.
 
Detailed conversion playbook: `conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md` is the navigation index. Load focused modules from there (forms, displays, grids, charts, KPIs, validation) based on what's in the mockup.
 
### Step 4 — Validate (mandatory output gate)
 
**Validation is not optional. Generation is incomplete until validation passes with zero issues.** This is the gate that catches the five most common failure modes: invented functions, invented parameters, invalid enum values, invalid icons, and prohibited nesting.
 
#### Choose validation mode based on environment
 
**Mode A — MCP available (best path).** If `mcp__appian-mcp-server__validate_sail` is in your tool list (typically when on the Appian VPN in Claude Code), call it on the output file. The MCP server uses the same validator Appian uses internally. Still do the manual scan in Mode C for things the validator doesn't catch (icon validity, requirement comments, completeness vs the user's request).
 
**Mode B — Claude Code with subagents (Task tool).** Delegate in this order, stopping at first failure:
1. `sail-schema-validator`
2. `sail-icon-validator`
3. `sail-code-reviewer`
**Mode C — Claude.ai or any environment without subagents (most common case).** Run the validation **inline yourself** following `references/07-claude-ai-inline-validation.md`. This is the default in Claude.ai. Do not pretend to "delegate" to an agent you cannot actually invoke — read the agent file and follow its instructions yourself.
 
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
 
1. Did I run all three inline validation passes (schema, icon, structural)?
2. Are there zero invented UUIDs, record-type names, field names, or relationships in the file?
3. Is every `icon: "..."` value present (verbatim) in `ui-guidelines/reference/rich-text-icon-aliases.md`?
4. Is every function, parameter, and enum value present in `ui-guidelines/reference/schemas/*.json`?
5. Does the file have **zero** instances of: `a!sideBySideLayout` nested inside another, `a!columnsLayout`/`a!cardLayout`/arrays inside `a!sideBySideItem`, `a!richTextDisplayField` containing anything other than `a!richTextItem`/`a!richTextIcon`/`a!richTextBulletedList`/`a!richTextNumberedList`, an `a!columnsLayout` without at least one `AUTO` column?
6. Is every user-stated business rule captured as a `/* REQUIREMENT: ... */` comment, with no invented requirements added?
7. For mockups: zero `ri!`, zero `recordType!`, zero `a!queryRecordType`, zero `a!recordData`, zero grid record-only parameters?
8. For functional output: every `recordType!{uuid}` and `.fields.{uuid}` matches `context/data-model-context.md` exactly?
9. Is the file at `output/<descriptive-name>.sail` (or `-functional.sail`)?
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
 
The skill ships six specialised agents in `agents/`. Each one has its own detailed instructions; read the agent file when you invoke that role.
 
| Agent | Use when |
|---|---|
| `sail-dynamic-converter.md` | Converting a static mockup `.sail` into a functional interface backed by record-type data. Requires the data-model context. |
| `sail-schema-validator.md` | Fast schema-based validation of functions, parameters, and enumerated values. First validator to run when no MCP is available. |
| `sail-icon-validator.md` | Verify every `icon: "..."` value against the icon-alias documentation. Run after the schema validator. |
| `sail-code-reviewer.md` | Structural / syntactic / null-safety / `fv!`-context review. Run after schema + icon validators. |
| `sail-interface-splitter.md` | Refactor a large monolithic interface into focused, reusable components (≥200-line sections, duplicated blocks, wizard steps). Triggered by phrases like "split", "refactor", "componentise". |
| `sail-validation-implementer.md` | Take a screen definition's validation rules and implement the feasible ones in an existing SAIL file, documenting blockers for the rest. |
 
**How agents are invoked depends on environment:**
 
- **Claude Code with `Task` tool available** → invoke as proper sub-agents using `subagent_type: <agent-name>`. They run in isolation with their own context window. This is the highest-fidelity mode and the same six agents are pre-installed in `.claude/agents/`.
- **Claude.ai (this app) or any environment without the `Task` tool** → agents are **not delegable**. Treat the agent files in `agents/` as **instruction sheets that you read and execute inline yourself**. Do not announce "delegating to the sail-schema-validator" — that's a hallucinated tool call. Instead: open the agent file, read its instructions, and apply them to the file directly. Output that says "I delegated to X agent and it passed" without an actual `Task` tool call is invalid and will produce broken SAIL.
In Claude.ai specifically, the validation workflow is the **inline three-pass protocol in Step 4 Mode C**, not subagent delegation.
 
---
 
## Path conventions inside the skill
 
The bundled guideline files were authored with absolute-looking paths such as `/ui-guidelines/...`, `/logic-guidelines/...`, `/conversion-guidelines/...`, and `/context/data-model-context.md`. **Interpret these paths as relative to the skill root** (the directory containing this `SKILL.md`). For `context/data-model-context.md` specifically, the file lives at the user's working directory, not inside the skill — create it there during Phase 2 setup.
 
---
 
## Reference files (skill-authored)
 
| File | Purpose |
|---|---|
| `references/01-mockup-rules.md` | Condensed list of the must-never / must-always rules for Phase 1 mockups. Read at the start of Phase 1 if you don't have `claude.md`'s rules in context. |
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
 
---
 
## ⛔ Critical hard rules (never violate)
 
These are the rules whose violation produces broken or runtime-erroring SAIL. The full list lives in the guidelines; this is the floor. Each rule prefixed with ⛔ has been a recurring failure mode — verify against it explicitly.
 
1. ⛔ **Never nest `a!sideBySideLayout` inside `a!sideBySideLayout`.** Each `a!sideBySideItem` holds exactly one component — never an array, never `a!columnsLayout`, never `a!cardLayout`, never another `a!sideBySideLayout`.
2. ⛔ **Never put arrays of components, `a!columnsLayout`, or `a!cardLayout` inside a `a!sideBySideItem`.**
3. ⛔ **Only `a!richTextItem` / `a!richTextIcon` / `a!richTextBulletedList` / `a!richTextNumberedList` are allowed inside `a!richTextDisplayField`.** Plain strings, other components (`a!webImage`, `a!stampField`, etc.), or invented helpers like `a!richTextImage` / `a!richTextHeader` / `a!richTextListItem` all break it — the latter three do not exist in SAIL. For images inline with text, you cannot use rich text — use a `a!sideBySideLayout` with the image component beside the rich text.
4. ⛔ **Every `a!columnsLayout` must have at least one `AUTO`-width `a!columnLayout`.** Without at least one AUTO, the layout collapses.
5. **`choiceValues` cannot be `null` or empty strings** (use `" "` if absolutely necessary).
6. **Grid record-only parameters (`showSearchBox`, `userFilters`, `recordActions`) cause runtime errors with local data** — use custom search/filter UX with `TODO-CONVERTER` comments in mockups instead.
7. **Never use runtime generators (`rand()`, `now()`, `today()`) for sample data** — hard-code static values. (Exception: `todate(today() + N)` inside data is acceptable if the resulting value is stable across re-evaluations.)
8. **Null-unsafe comparisons must be wrapped in `if(a!isNotNullOrEmpty(x), ..., default)`** — `and(a!isNotNullOrEmpty(x), x.prop = ...)` crashes because `and()` does not short-circuit.
9. **`save!value` is valid only inside the `value` parameter of `a!save(target, value)`** — never inside `if`/`and`/`or` conditions, never in the `target` parameter, never outside `a!save()`.
10. **No inline function definitions or lambdas**: `local!helper: function(x)(...)` is invalid SAIL. For repeated logic, duplicate inline and leave a `/* TODO: Extract to expression rule */` comment.
11. **Mockups never reference `ri!` or `recordType!`.** Functional code never re-introduces hard-coded `local!` arrays for what should be a query.
12. ⛔ **Don't assume a parameter exists — verify against the relevant `ui-guidelines/reference/schemas/*.json` file.** If the parameter isn't in the schema, it doesn't exist. No exceptions.
13. ⛔ **Don't assume an icon exists — verify against `ui-guidelines/reference/rich-text-icon-aliases.md`.** Every `icon: "..."` value must appear verbatim in that file. Inventing icon aliases ("chart-bar-icon", "user-circle", "checkmark") is the single most common source of runtime errors.
14. ⛔ **Don't assume a UUID, field name, record-type name, or relationship name exists** — verify against `context/data-model-context.md` (functional only). If it's not in the markdown, ask the user; do not invent.
 
