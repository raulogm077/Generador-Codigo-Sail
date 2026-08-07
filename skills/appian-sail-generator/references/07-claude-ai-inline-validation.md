# Claude.ai Inline Validation Protocol — No Subagents

This file is the canonical playbook for validating generated SAIL **when running in Claude.ai (or any other environment without the `Agent` tool)**. In those environments, the agents in `agents/` are not delegable — they are instruction sheets you read and execute yourself.

In Claude Code with subagents available, prefer the proper delegation path described in `SKILL.md` Step 4 Mode B. This file is for everything else.

---

## TL;DR — the three-pass scan

For every generated `.sail` file, run these three passes in order. Stop and fix when a pass finds issues. Don't skip ahead.

1. **Pass 1 — Schema validation** (functions, parameters, enum values vs `ui-guidelines/reference/schemas/*.json`)
2. **Pass 2 — Icon validation** (every `icon: "..."` vs `ui-guidelines/reference/rich-text-icon-aliases.md`)
3. **Pass 3 — Structural review** (`references/04-validation-checklist.md` § Manual scan + `references/06-common-syntax-errors.md` 14 categories)

Then run the **Final Output Gate** in `SKILL.md` Step 4.5 before responding to the user.

---

## Pre-flight (run before writing any SAIL)

Before generating, confirm the following with explicit reasoning. These map to the Hard STOP signals in `SKILL.md` § Core principle.

1. **Functional vs mockup**: Did the user say "functional", "dynamic", "use real data", "connect to <RecordType>", "with our records"? If yes → check `context/data-model-context.md`. If it's a placeholder or missing → STOP, ask the user.
2. **Form intent**: If the request is a form, is it CREATE / UPDATE / both / a start form? If unclear → ask.
3. **Business rules**: For every rule the user mentioned, is the predicate exact enough to encode? If not → ask.
4. **Relationships**: For every related-record field shown in the UI, is the relationship name in `data-model-context.md`? If not → read it or ask.

Then load these files into context **before writing**:

- **Always load**: `ui-guidelines/reference/schemas/layouts-schema.json` (the page layout vocabulary) **and** `ui-guidelines/reference/schemas/expression-functions-schema.json` (60 core functions like `if`, `and`, `or`, `index`, `length`, `contains`, `a!isNotNullOrEmpty`, `a!defaultValue`, `a!match`, `tointeger`, `todate`, `tostring`, etc. **plus** 39 sub-components like `a!richTextItem`, `a!richTextIcon`, `a!localVariables`, `a!save`, `a!forEach`, `a!map`, `a!validationMessage`, `a!sortInfo`, `a!gridRowLayout`, all `*Link` types, all `cardTemplate*` types, `a!chartSeries`). These two files cover ~80% of what any non-trivial SAIL touches.
- For each component category used, the matching `ui-guidelines/reference/schemas/*-components-schema.json` (see § "Open the relevant schema files" below for which file holds which component).
- If using icons: `ui-guidelines/reference/rich-text-icon-aliases.md`.
- The matching `ui-guidelines/layouts/*.md` for your top-level layout.
- The matching `ui-guidelines/components/*.md` for non-trivial components.
- The matching `ui-guidelines/patterns/*.md` for cross-cutting patterns.
- For dynamic logic: `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` first, then the topic file.

Don't skip these even if you "remember" the schema. Your memory is wrong often enough that the cost of grepping is much smaller than the cost of broken output.

---

## Pass 1 — Schema validation (inline)

**Goal**: every function name, parameter name, and enumerated value in the generated file exists in `ui-guidelines/reference/schemas/*.json`.

**Method**:

1. Open the relevant schema files based on what components you used. **Where each component actually lives** (verified by inspecting each JSON):

   - **`layouts-schema.json`** (22 components, page-level layout): `a!headerContentLayout`, `a!formLayout`, `a!wizardLayout`, `a!wizardStep`, `a!paneLayout`, `a!pane`, `a!columnsLayout`, `a!columnLayout`, `a!sectionLayout`, `a!cardLayout`, `a!cardGroupLayout`, `a!sideBySideLayout`, `a!sideBySideItem`, `a!boxLayout`, `a!billboardLayout`, `a!fullOverlay`, `a!barOverlay`, `a!columnOverlay`, `a!tabLayout`, `a!tabItem`, `a!headerTemplateImage`. Also: `a!editableGridLayout` is an informational alias for `a!gridLayout` — use `a!gridLayout(...)` in actual code; docs refer to it as "Editable Grid".

   - **`input-components-schema.json`** (27 form inputs): `a!textField`, `a!paragraphField`, `a!styledTextEditorField`, `a!integerField`, `a!floatingPointField`, `a!dateField`, `a!dateTimeField`, `a!timeField`, `a!dropdownField`, `a!radioButtonField`, `a!checkboxField`, `a!barcodeField`, `a!cardChoiceField`, `a!fileUploadField`, `a!encryptedTextField`, `a!pickerFieldUsers`, `a!pickerFieldGroups`, `a!pickerFieldUsersAndGroups`, `a!pickerFieldRecords`, `a!toggleField`, `a!booleanCheckboxField`, `a!signatureField`, `a!multipleDropdownField`, `a!dropdownFieldByIndex`, `a!multipleDropdownFieldByIndex`, `a!radioButtonFieldByIndex`, `a!checkboxFieldByIndex`.

   - **`button-components-schema.json`** (3 only — note `a!recordActionField` is NOT here): `a!buttonWidget`, `a!buttonArrayLayout`, `a!buttonLayout`.

   - **`display-components-schema.json`** (20 read-only displays — note `a!richTextItem`/`a!richTextIcon` are NOT here): `a!richTextDisplayField`, `a!stampField`, `a!headingField`, `a!progressBarField`, `a!tagField`, `a!linkField`, `a!recordActionField`, `a!imageField`, `a!gaugeField`, `a!milestoneField`, `a!horizontalLine`, `a!documentViewerField`, `a!timeDisplay`, `a!messageBanner`, `a!gaugeFraction`, `a!gaugeIcon`, `a!gaugePercentage` (gauge sub-components — used inside `a!gaugeField` `primaryText`), `a!videoField`, `a!webContentField`, `a!kpiField` (records-only — never in mockups).

   - **`grid-components-schema.json`** (16 grid + query): `a!gridField`, `a!gridLayout`, `a!gridColumn`, `a!pagingInfo`, `a!queryRecordType`, `a!queryRecordByIdentifier`, `a!selectionFields`, `a!recordData`, `a!relatedRecordData`, `a!aggregationFields`, `a!measure`, `a!grouping`, `a!queryFilter`, `a!queryLogicalExpression`, `a!eventHistoryListField` (records-only), `a!eventData`. (Note: `a!gridImageColumn` does NOT exist.)

   - **`chart-components-schema.json`** (13 charts + configs): `a!columnChartField`, `a!pieChartField`, `a!lineChartField`, `a!barChartField`, `a!areaChartField`, `a!scatterChartField`, and their matching `a!*ChartConfig` pairs, **`a!colorSchemeCustom`** (custom-colors helper for any chart's `colorScheme:` parameter).

   - **`expression-functions-schema.json`** (the big one — 39 sub-components + 60 core functions):
     - **Rich text sub-components** (these live HERE, not in display): `a!richTextItem`, `a!richTextIcon`, `a!richTextBulletedList`, `a!richTextNumberedList`, **`a!richTextHeader`** (h1-h6 inside richTextDisplayField), **`a!richTextImage`** (icon-sized inline images inside richTextDisplayField), **`a!richTextListItem`** (nested list items inside bulleted/numbered lists). NOTE: do not confuse `a!richTextImage` (inline, used inside richTextDisplayField) with `a!imageField` (standalone display field).
     - **Local-variable / save / loop / map**: `a!localVariables`, `a!save`, `a!forEach`, `a!map`, `a!update`, `a!flatten`, `a!match`.
     - **Grid sub-components**: `a!gridRowLayout`, `a!gridLayoutHeaderCell`, `a!gridLayoutColumnConfig`. (NOTE: `a!gridRowDeletion` does NOT exist — delete rows via a richText trash-link column, never via a `rowDeletions` parameter.)
     - **Links**: `a!dynamicLink`, `a!safeLink`, `a!recordLink`, `a!userRecordLink`, `a!authorizationLink`, `a!documentDownloadLink`, `a!processTaskLink`, `a!startProcessLink`, `a!submitLink`.
     - **Images** (inside text/cards, not as standalone fields): `a!webImage`, `a!documentImage`, `a!userImage`, `a!webVideo`.
     - **Card templates**: `a!cardTemplateBarTextStacked`, `a!cardTemplateBarTextJustified`, `a!cardTemplateTile`.
     - **Tag / validation / chart helpers**: `a!tagItem`, `a!validationMessage`, `a!chartSeries`, `a!chartCustomColorScheme`, `a!chartReferenceLine`, `a!sortInfo`, `a!recordActionItem`, `a!isPageWidth`, `a!headerTemplateFull`, `a!headerTemplateSimple`, `a!sidebarTemplate`.
     - **Core functions** (no `a!` prefix): `if`, `and`, `or`, `not`, `isnull`, `index`, `length`, `append`, `concat`, `text`, `today`, `now`, `todate`, `todatetime`, `tointeger`, `todecimal`, `tostring`, `upper`, `lower`, `trim`, `contains`, `where`, `wherecontains`, `union`, `difference`, `intersection`, `sum`, `average`, `min`, `max`, `round`, `mod`, `todatasubset`, `filter`, `reduce`, `merge`, `datetime`, `date`, `user`, `loggedInUser`, `touser`, `group`.
     - **`a!`-prefixed helpers**: `a!defaultValue`, `a!isNullOrEmpty`, `a!isNotNullOrEmpty`, `a!addDateTime`, `a!subtractDateTime`.

   **The lookup discipline**: don't assume which file a component is in. The above list was verified by inspecting each schema file's `components` and `expressionFunctions` keys. If a name isn't in the lists above, it likely doesn't exist — grep all schemas to confirm before using it.

2. For every `a!<functionName>(...)` call in the generated file:
   - Confirm `<functionName>` is a key in one of the schema files.
   - If you cannot find it: it does not exist. Remove the call or replace with a real function.

3. For every parameter inside the call (e.g. `label: "..."`, `value: ...`, `style: "..."`):
   - Confirm the parameter name appears in the function's parameter list in the schema.
   - If the parameter has a `validValues` array (enum), confirm the value you used is in that array.
   - If not: it's invalid. Replace with a valid value or remove the parameter.

**Common invented parameters that trip people up**:
- `a!buttonWidget` does NOT have `align`. Wrap the button in `a!buttonArrayLayout(align: ...)`.
- `a!textField` does NOT have `borderColor`. Style is fixed.
- `a!sectionLayout` `marginAbove`/`marginBelow` values are `"NONE"`, `"EVEN_LESS"`, `"LESS"`, `"STANDARD"`, `"MORE"`, `"EVEN_MORE"`. Not `"SMALL"`, not `"LARGE"`.
- `a!columnLayout` `width` is `"AUTO"`, `"NARROW_PLUS"`, `"NARROW"`, `"MEDIUM"`, `"MEDIUM_PLUS"`, `"WIDE"`. Not `"FIXED"`, not pixel values.
- `a!richTextItem` `align` is `"LEFT"`, `"CENTER"`, `"RIGHT"`. Not `"START"`, not `"END"`.
- Button `style` is `"OUTLINE"`, `"GHOST"`, `"LINK"`, `"SOLID"`. Not `"PRIMARY"`, not `"ACCENT"` (those go in `color`).

**Common invented function names** (these don't exist):
- `a!if(...)` — use `if(...)` (no `a!` prefix).
- `a!and(...)`, `a!or(...)`, `a!not(...)` — use `and()`, `or()`, `not()`.
- `a!length(...)` — use `length()`.
- `a!contains(...)` — use `contains()`.
- `a!filter(...)` — there is no native filter, use `a!forEach(...)` with `where:` clause.

---

## Pass 2 — Icon validation (inline)

**Goal**: every `icon: "..."` value in the generated file appears verbatim in `ui-guidelines/reference/rich-text-icon-aliases.md`.

**Method**:

1. Grep the generated `.sail` file for `icon:` — list every occurrence and the string value.
2. For each string value: grep `ui-guidelines/reference/rich-text-icon-aliases.md` for the **exact** string.
3. If the string is not present: it's an invented icon. Replace with a verified alias from the file (search for synonyms by category — see the file's table of contents) or remove the `icon:` parameter.

**Frequently-invented icons that do NOT exist** (real examples seen in broken output):
- `"chart-bar-icon"`, `"chartbar"`, `"bar-chart-icon"` — use `"bar-chart"`.
- `"user-circle"` — use `"user"` or `"user-circle-o"` (check file for exact aliases).
- `"checkmark"` — use `"check"`.
- `"close-icon"`, `"x-icon"` — use `"close"` or `"times"`.
- `"trash-can"` — use `"trash"`.
- `"arrow-right-icon"` — use `"arrow-right"`.
- `"settings-icon"` — use `"cog"` or `"gear"` (check file).

The aliases file is the **single source of truth**. Memory of common Font Awesome names is unreliable — Appian's icon set is a curated subset with its own naming.

---

## Pass 3 — Structural review (inline)

**Goal**: catch the structural / nesting / null-safety / context errors that the schema and icon checks miss.

**Method**: walk `references/04-validation-checklist.md` § Manual scan checklist top to bottom, then walk `references/06-common-syntax-errors.md` and check each of the 14 categories against the file.

Pay particular attention to the **Big Five** below.

---

## The Big Five — most common failure modes

These five account for the majority of broken-output reports. Build the habit of checking each one explicitly on every generation.

### #1 — Invented functions / parameters

**Symptom**: Appian Designer says "Unknown function `a!XYZ`" or "Property `XYZ` does not exist on `a!textField`".

**Detection**: Pass 1 above. Schema lookup for every function and every parameter.

**Fix**: If the function/parameter doesn't exist, remove it. Don't try a similar-sounding name — grep the schema for what does exist and use that.

### #2 — Invented icons

**Symptom**: Icon doesn't render in Appian; sometimes the whole rich-text section breaks.

**Detection**: Pass 2 above.

**Fix**: Replace with a verified alias from `rich-text-icon-aliases.md`.

### #3 — Invalid enum values

**Symptom**: "Value `X` is not in the list of valid values for parameter `Y`".

**Detection**: When checking parameters in Pass 1, also check that any string-literal value matches the parameter's `validValues` array if one is declared.

**Common offenders**:
- Button `style: "PRIMARY"` → invalid. Use `"OUTLINE"`/`"GHOST"`/`"LINK"`/`"SOLID"`.
- `marginAbove: "SMALL"` → invalid. Use `"NONE"`/`"EVEN_LESS"`/`"LESS"`/`"STANDARD"`/`"MORE"`/`"EVEN_MORE"`.
- `spacing: "less"`/`"more"` → invalid (case mismatch and not in the enum).
- `labelPosition: "TOP"` → check schema; the values are `"ABOVE"`/`"ADJACENT"`/`"COLLAPSED"`/`"JUSTIFIED"`. `"TOP"` is invalid.
- `align: "START"`/`"END"` → invalid. Use `"LEFT"`/`"CENTER"`/`"RIGHT"`.

### #4 — Prohibited nesting (sideBySide / columns / richText)

**Symptom**: "Cannot evaluate property", "Invalid component nesting", layout renders empty, or the whole expression fails to load.

**Detection**: Scan for:
- `a!sideBySideLayout` inside `a!sideBySideItem` → forbidden.
- `a!columnsLayout` inside `a!sideBySideItem` → forbidden.
- `a!cardLayout` inside `a!sideBySideItem` → forbidden.
- Array `{...}` of components inside `a!sideBySideItem` → forbidden (only one component per item).
- Anything other than `a!richTextItem` / `a!richTextIcon` / `a!richTextBulletedList` / `a!richTextNumberedList` / `a!richTextHeader` / `a!richTextImage` / `a!richTextListItem` inside `a!richTextDisplayField` `value:` → forbidden. Note: `a!richTextHeader` is deprecated by Appian — prefer `a!headingField` (a standalone display component, not nested inside richText) for new code. `a!richTextImage` and `a!richTextListItem` are current and supported.
- `a!columnsLayout` without at least one `a!columnLayout(width: "AUTO", ...)` → forbidden.

**Fix**: Restructure. For row-of-items layouts, use `a!columnsLayout` (which can nest other `a!columnsLayout`) rather than abusing `a!sideBySideLayout`. For inline text+icon, use `a!richTextDisplayField` with `a!richTextIcon` + `a!richTextItem`.

### #5 — Invented UUIDs / record-type names / fields / relationships

**Symptom**: Appian says "record type does not exist" or "field does not exist" or returns null data when the user expects rows.

**Detection**: For every `recordType!{uuid}` or `.fields.{uuid}` or `[relationship]` occurrence, verify it exists verbatim in `context/data-model-context.md`. If `context/data-model-context.md` is the placeholder (51 lines starting with "# Data Model Context — Placeholder"), then the entire output should not have any functional record references and should be a mockup only.

**Fix**: This is the most expensive error class because the user only finds out when they paste and the data is wrong/missing. Prevention is the only real fix: never produce a functional file without a populated `data-model-context.md`. If you find invented identifiers in your output, delete them and either ask the user for the real ones or revert to mockup mode.

---

## After all passes pass

Run the **Final Output Gate** in `SKILL.md` Step 4.5. Every question must be "yes" before responding.

If the output passes everything, present it briefly:
- Where the file is (`output/<name>.sail`).
- Any `TODO-CONVERTER`, `TODO-DATA-MODEL`, or `TODO` comments that block real-world use, and what the user needs to do.
- What follow-up commands look like.

If the user pastes an Appian Designer error after the output: follow `SKILL.md` Step 6 (error-fix workflow), and re-run all three passes after the fix.
