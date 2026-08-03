# Anti-Invention Protocol

The single biggest cause of broken Appian SAIL output is **invention**: making up a UUID, a field name, a function, a parameter, an enum value, an icon alias, or a business rule because it "sounds right". This file is the protocol for catching invention before it ships.

The principle: **for every identifier you write, you must be able to point to a file where it appears verbatim.** If you cannot point at a file, you are inventing.

---

## What can never be invented

Apply this list strictly. Any time you are about to write one of these, the rule is "verify or ask, never guess".

### 1. UUIDs (record-type, field, relationship)

These are environment-specific. There is no way for you to know them. They look like `{3eb360f5-349c-4b15-bb24-3ca875b72bff}`.

**Source of truth**: `context/data-model-context.md` for the user's environment.

**If `context/data-model-context.md` is the placeholder** (51 lines starting with "# Data Model Context — Placeholder"): no functional output. Either revert to mockup mode (Phase 1, with `local!` sample data) or ask the user for the populated markdown.

**Recovery if you catch yourself**: stop writing. Delete the invented UUID. Replace with either a sample-data `local!` variable (mockup) or a `TODO-DATA-MODEL: Need UUID for X` comment, and surface the missing data to the user.

### 2. Record-type names, field names, relationship names (functional output)

Same source of truth as UUIDs. If `context/data-model-context.md` lists the record type, use the exact name. If not, ask.

**For mockups (Phase 1)**: sample names are fine. `local!cases: a!map(id: 1, title: "Sample Case", status: "Open")` is good — these are mockup data, not record references.

### 3. Function names

Source of truth: `ui-guidelines/reference/schemas/expression-functions-schema.json` plus the function lists embedded in the component schemas.

**Common inventions that don't exist**:
- `a!if(...)` — use `if(...)` (no `a!` prefix). The bare `if` is real and lives in `expression-functions-schema.json`.
- `a!and(...)`, `a!or(...)`, `a!not(...)` — use `and()`, `or()`, `not()`.
- `a!equals(...)` — use `=` operator or `equals()` (no `a!` prefix).
- `a!length(...)` — use `length()`.
- `a!contains(...)` — use `contains()`.
- `a!filter(...)` — does not exist with the `a!` prefix. The bare `filter()` is real, but is rarely the right choice in SAIL — `a!forEach(...)` with a `where:` clause reads better and is the idiomatic pattern. `a!filter` (with prefix) is invented.
- `a!map(...)` for transformation — `a!map` constructs a map (key/value pairs), not a transform. For transformation, use `a!forEach`.
- `a!find(...)` — does not exist. Use `index()` + `wherecontains()`.
- `a!reduce(...)` — does not exist with the `a!` prefix. The bare `reduce()` is real but rarely needed; usually an accumulator pattern in `a!forEach` is clearer.
- `a!richTextImage(...)`, `a!richTextHeader(...)`, `a!richTextListItem(...)` — these **do exist** in Appian (verify against `expression-functions-schema.json`). They are valid children of `a!richTextDisplayField`. Note: `a!richTextHeader` is deprecated by Appian — prefer `a!headingField` for new code (a standalone display field).
- `a!gridImageColumn(...)` — does not exist. Use a regular `a!gridColumn` whose `value` is `a!imageField(...)` or `a!webImage(...)`.

**Recovery**: grep `ui-guidelines/reference/schemas/expression-functions-schema.json` for the closest real function and use that.

### 4. Component parameters

Source of truth: the per-component schema in `ui-guidelines/reference/schemas/*-components-schema.json`.

**Common invented parameters**:
- `a!buttonWidget` has no `align`. Wrap the button in `a!buttonArrayLayout(align: ...)`.
- `a!textField` has no `borderColor`, `backgroundColor`, `fontSize`, `fontWeight`. Styling is fixed.
- `a!sectionLayout` has no `padding`. Use `marginAbove`/`marginBelow` with enum values.
- `a!cardLayout` has no `borderRadius`. Use `shape: "ROUNDED"` etc.
- `a!gridField` has no `pageSize` outside the `pagingSaveInto` context. Use the `pageSize` inside `a!pagingInfo()`.
- `a!stampField` has no `image`. Use `text:` for initials or `icon:` for an icon.

**Recovery**: grep the schema; if the parameter isn't there, it doesn't exist. Remove it.

### 5. Enum values

Source of truth: the `validValues` array in the schema.

Common invented enums — see `references/07-claude-ai-inline-validation.md` § The Big Five #3 for the canonical list.

### 6. Icon aliases

Source of truth: `ui-guidelines/reference/rich-text-icon-aliases.md`.

The Appian icon set is a curated subset of Font Awesome with its own naming. Your memory of FA icon names is wrong about half the time. Grep before using.

### 7. Business rules

Source of truth: the user.

If the user said "validate the email", that's not a rule, that's a topic. The rule is the predicate — "email must contain `@` and have a domain with a TLD of length ≥ 2", or "email must end with @company.com", or whatever they actually want. Ask.

**Recovery if you wrote one anyway**: delete the rule. Add a `/* TODO: Confirm rule with user */` comment, and ask in your response.

### 8. Process-variable names (start forms)

Source of truth: `model.json` `process_variables[].variable_name`.

If the form is a start form for a process model and there is no `model.json` available, the `ri!` names you pick will likely not match what the process expects, and the integration will silently fail. Ask for the `model.json` before writing `ri!` declarations.

---

## What can be defaulted (and how)

These you decide yourself. Annotate with `/* ASSUMPTION: ... */` where it would help the user override.

| Item | Default |
|---|---|
| Page background colour | `#F5F6F8` |
| Page header bar background | `#1C2C44` |
| Content card background | `#FFFFFF` |
| Primary theme colour | `"ACCENT"` |
| Standard text colour | `"STANDARD"` |
| Number of sample rows in a mockup grid | 5–8 |
| Sample case numbers / names / dates | Pick realistic statics |
| Sort order | Newest first / most relevant first |
| Default page size | 25 |
| Whether to add an icon to a status indicator or action button | Yes if it improves clarity |
| `labelPosition` when no label is given | `"COLLAPSED"` |

---

## Worked examples — catching invention in real cases

### Example A — Functional request without data model

**User**: "Make this dashboard functional and connect to our Case records."

**Inventing-mode response (broken)**:
```sail
a!queryRecordType(
  recordType: 'recordType!{a1b2c3d4-1234-5678-9abc-def012345678}Case',
  fields: {
    'recordType!{a1b2c3d4-...}Case.fields.{f1234567-...}id',
    'recordType!{a1b2c3d4-...}Case.fields.{f7654321-...}title',
    ...
  }
)
```

This is broken. The UUIDs are invented. They will not match the user's environment. Even if they accidentally matched a real record type, the fields won't.

**Correct response**:
> Before I make this functional, I need the data-model context for your Case record type. Three options:
> 1. Paste / point me to `context/data-model-context.md` if you have one.
> 2. Paste the `recordTypeHaul` XML for the Case record (and any related records) — I'll run the script to extract the UUIDs.
> 3. Give me the record-type name, UUID, and field UUIDs by hand.
>
> Which works?

### Example B — Ambiguous validation rule

**User**: "Make the form, and validate the email field."

**Inventing-mode response (broken)**:
```sail
a!textField(
  label: "Email",
  value: ri!email,
  saveInto: ri!email,
  validations: a!validationMessage(
    message: "Please enter a valid email address",
    validateAfter: "KEYPRESS"
  )
)
```

This passes SAIL validation but doesn't actually validate anything — there's no predicate. Worse, "valid email" is your guess at what the user meant, not theirs.

**Correct response**:
1. Write the field without validation (or with `/* TODO: Confirm validation predicate */`).
2. In your reply, ask: "For the email validation: do you want a format check (basic `<x>@<y>.<z>`), a domain check (must be @ourcompany.com), uniqueness against existing users, or something else?"

### Example C — Icon that "sounds right"

**Tempting**: `a!richTextIcon(icon: "chart-bar-icon")`.

**Check**: grep `ui-guidelines/reference/rich-text-icon-aliases.md` for `chart-bar-icon`. Not found.

**Try alternatives**: grep for `chart-bar`. Found `"bar-chart"`.

**Fix**: `a!richTextIcon(icon: "bar-chart")`.

### Example D — Parameter that "should exist"

**Tempting**: `a!buttonWidget(label: "Submit", align: "RIGHT", ...)`.

**Check**: open `ui-guidelines/reference/schemas/button-components-schema.json` and look up `a!buttonWidget`. There is no `align` parameter.

**Fix**: wrap the button: `a!buttonArrayLayout(align: "END", buttons: { a!buttonWidget(label: "Submit", ...) })`.

### Example E — Function that's "Claude-like"

**Tempting**: `a!filter(local!items, fn(item, item.status = "Open"))`.

**Check**: this is JavaScript thinking. SAIL has no `a!filter` and no inline lambdas.

**Fix**: use `a!forEach` with `where:`:
```sail
a!forEach(
  items: local!items,
  expression: fv!item,
  where: fv!item.status = "Open"
)
```
Or pre-filter into a `local!` variable.

---

## The catch-yourself loop

While generating, if you find yourself about to type one of these — STOP, grep, verify or ask:

- `"<some-uuid-pattern>"` → never invent.
- `recordType!<some-name>` → only if `data-model-context.md` lists it.
- `.fields.<some-uuid>` → only if listed.
- `icon: "..."` → grep the aliases file first.
- A parameter name that "feels right" → grep the schema first.
- A function name that "feels right" → grep the schema first.
- A business rule predicate the user didn't state → ask.

The grep takes 2 seconds. Fixing broken SAIL after the fact takes 10 minutes plus user frustration.

---

## V8 components — common inventions to refuse

These components were added in V8. They look superficially similar to older ones but have **non-obvious parameter shapes**. Each row is an invention by analogy that will fail. Verified against Appian 26.4 docs and the per-category schemas in `ui-guidelines/reference/schemas/`.

### `a!toggleField` and `a!booleanCheckboxField`

| Invention | Reality |
|---|---|
| `label: "..."` | Both use `choiceLabel:` (singular). They have NO `label`/`labelPosition`/`instructions`. |
| `labelPosition: "ABOVE"` | Does not exist on these. |
| `instructions: "..."` | Does not exist. The choice label is the only label. |
| `choiceValues: {true, false}` | Boolean field — no `choiceValues`. `value:` is Boolean. |
| `choicePosition: "BEFORE"` / `"AFTER"` | Values are `"START"` / `"END"` only. |

Full valid set: `choiceLabel, helpTooltip, value, saveInto, showWhen, required, requiredMessage, validations, validationGroup, disabled, accessibilityText, marginAbove, marginBelow, choicePosition`.

### `a!signatureField`

| Invention | Reality |
|---|---|
| `validations: {...}` | Does not exist on `a!signatureField`. Only `requiredMessage` for the required validation. |
| Using it on a detail page or wizard step without `a!submitUploadedFiles()` | Signature appears to capture but never persists. Either move to a start/task form or wrap save in `a!submitUploadedFiles()`. |
| `multiple: true` | Cannot upload multiple signatures, ever. Single signature only. |
| `acceptedFileTypes: {"png", "jpg"}` | Always `.png`. The format is fixed. |
| `buttonStyle: "ACCENT"` / `"SOLID"` | Valid values: `"PRIMARY"`, `"SECONDARY"` (default), `"STANDARD"`, `"LINK"`. Not the button-widget vocabulary. |
| `buttonSize: "MEDIUM"` | Valid values: `"SMALL"` (default), `"STANDARD"`, `"LARGE"`. No `"MEDIUM"`. |

Full valid set (20 params): `label, labelPosition, instructions, helpTooltip, target, fileName, fileDescription, value, saveInto, required, requiredMessage, buttonStyle, buttonSize, readOnly, disabled, validationGroup, accessibilityText, showWhen, marginAbove, marginBelow`.

### `a!gaugeField` and the three primaryText helpers

| Invention | Reality |
|---|---|
| `primaryText: a!richTextIcon(icon: "...")` | Crashes. Use `a!gaugeIcon(icon: "...")` inside primaryText. |
| `primaryText: text(...)` for a percentage | Use `a!gaugePercentage()` — no parameters, auto-formats from gauge's `percentage:`. |
| `primaryText: text(numerator) & "/" & text(denominator)` | Use `a!gaugeFraction(denominator: N)` — numerator is auto-computed from gauge's `percentage:`. |
| `a!gaugeFraction(numerator: 25, denominator: 26)` | `a!gaugeFraction` has ONLY `denominator`. There is no `numerator` parameter. |
| `a!gaugePercentage(value: 80)` | `a!gaugePercentage` takes **no parameters**. |
| `a!gaugeField(color: "WARNING")` | Valid values: `"ACCENT"`, `"POSITIVE"`, `"NEGATIVE"`, `"WARN"`, hex. Note `"WARN"` not `"WARNING"`. |
| `a!gaugeIcon(color: "BRIGHT_RED")` | Same enum as gauge (`ACCENT`/`POSITIVE`/`NEGATIVE`), or hex. Also accepts the `fv!percentage` reference for conditional colouring. |

Full valid sets:
- `a!gaugeField`: `label, labelPosition, instructions, helpTooltip, percentage, primaryText, secondaryText, color, size, align, accessibilityText, showWhen, tooltip, marginAbove, marginBelow`
- `a!gaugeFraction`: `denominator` (only)
- `a!gaugeIcon`: `icon, altText, color`
- `a!gaugePercentage`: (none)

### Picker fields (`a!pickerFieldRecords`, `a!pickerFieldUsers`, `a!pickerFieldGroups`, `a!pickerFieldUsersAndGroups`)

| Invention | Reality |
|---|---|
| `a!pickerFieldRecords` without `recordType:` | `recordType:` is **required**. Use the record-type literal: `recordType: 'recordType!{uuid}Case'`. |
| Expecting `saveInto` to receive a single value | All pickers **always save an array**, even with `maxSelections: 1`. Use `index(local!sel, 1, null)` to extract single value. |
| `recordTypes: {...}` (plural) | The parameter is singular `recordType:` — only ONE record type per picker. |
| `a!pickerFieldUsers` with `recordType:` | User pickers don't take a record type; use `groupFilter:` to scope. |
| `groupFilter: "GroupName"` (as text) | `groupFilter:` is a Group reference (typically `cons!MY_GROUP` or `togroup(id)`), not a string. |
| `showRecordLinks: false` on a user/group picker | Only `a!pickerFieldRecords` has `showRecordLinks`. |

Full valid sets:
- `a!pickerFieldRecords` (21 params): `label, labelPosition, instructions, helpTooltip, placeholder, maxSelections, recordType, filters, value, saveInto, required, requiredMessage, readOnly, disabled, validations, validationGroup, accessibilityText, showWhen, showRecordLinks, marginAbove, marginBelow`
- `a!pickerFieldUsers` / `a!pickerFieldGroups` / `a!pickerFieldUsersAndGroups` (19 params each, same set): `label, instructions, required, requiredMessage, readOnly, disabled, maxSelections, groupFilter, value, validations, validationGroup, saveInto, labelPosition, placeholder, helpTooltip, accessibilityText, showWhen, marginAbove, marginBelow`

### "By Index" choice fields (`a!dropdownFieldByIndex`, `a!radioButtonFieldByIndex`, `a!checkboxFieldByIndex`, `a!multipleDropdownFieldByIndex`)

| Invention | Reality |
|---|---|
| `choiceValues: {...}` | These components do NOT have `choiceValues`. They operate on **1-based indices**. Only `choiceLabels:` defines the options; the index of the selected label is the saved value. |
| `value: "Open"` (string) | `value:` is **Integer** (or `List of Integer` for multi-select). The integer is the 1-based index into `choiceLabels`. |
| `searchDisplay: "ALWAYS"` | Valid values are `"AUTO"` (default), `"ON"`, `"OFF"`. |
| Expecting 0-based indices | All indices are **1-based**. `choiceLabels[1]` is the first label. |
| `marginAbove`/`marginBelow` on these | Surprisingly, the four `*ByIndex` components do NOT have `marginAbove`/`marginBelow` in their docs/schema. The standard layout-margin enum doesn't apply here. |

Full valid sets:
- `a!dropdownFieldByIndex` (16): `label, labelPosition, instructions, required, disabled, choiceLabels, placeholder, value, validations, saveInto, validationGroup, requiredMessage, helpTooltip, accessibilityText, showWhen, searchDisplay`
- `a!multipleDropdownFieldByIndex` (16): same as above
- `a!radioButtonFieldByIndex` (17): `label, instructions, required, disabled, choiceLabels, value, validations, saveInto, validationGroup, requiredMessage, labelPosition, choiceLayout, helpTooltip, accessibilityText, showWhen, choiceStyle, choicePosition`
- `a!checkboxFieldByIndex` (18): adds `align` to the radio set

### `a!videoField` and `a!webContentField`

| Invention | Reality |
|---|---|
| `a!videoField(url: "...")` | Parameter is `videos:` — a list of `a!webVideo(source: "...")` objects, not a URL string. |
| `a!videoField(source: "...")` | Wrong shape. Wrap in `a!webVideo(source: "...")` and pass as a single-element list to `videos:`. |
| `a!webContentField(url: "...")` | The URL parameter is `source:`, NOT `url:`. |
| `a!webContentField(height: "AUTO")` | Valid values: `"SHORT"`, `"MEDIUM"` (default), `"TALL"`. No `"AUTO"`. |
| `a!videoField` with `height:` / `source:` | These don't exist on `a!videoField`. Sizing is controlled by the parent layout. |

Full valid sets:
- `a!videoField` (9): `label, labelPosition, instructions, videos, helpTooltip, accessibilityText, showWhen, marginAbove, marginBelow`
- `a!webContentField` (13): `label, labelPosition, instructions, helpTooltip, showWhen, source, showBorder, height, altText, disabled, accessibilityText, marginAbove, marginBelow`

### `a!tabLayout` and `a!tabItem`

| Invention | Reality |
|---|---|
| `a!tabLayout(items: {...})` | Container parameter is `tabs:`. `items:` is what `sideBySideLayout` uses. |
| `a!tabLayout(selectedTab: 1)` | There is no `selectedTab` parameter. The active tab is managed by the user interaction; the layout does not expose a manual selector. |
| `highlightColor: "STANDARD"` | Valid values: `"ACCENT"` (default) or a hex code (`#RRGGBB` or `#RRGGBBAA` for transparency). No `"STANDARD"`. |
| `contentsPadding: "AUTO"` | Valid values: standard 6-value margin enum (`"NONE"`, `"EVEN_LESS"`, `"LESS"`, `"STANDARD"` (default), `"MORE"`, `"EVEN_MORE"`). |
| Putting `a!tabLayout` inside `a!sideBySideLayout` / editable grid / read-only grid | Forbidden. Restructure with `a!columnsLayout` or use the custom tabs pattern (`ui-guidelines/patterns/tabs.md`). |
| `a!tabItem(content: ...)` (singular) | The parameter is `contents:` (plural). Components inside go in an array. |
| `a!tabItem(disabled: true)` | There is no `disabled:`. Use `showWhen: false` to hide a tab; you can't gray it out. |

Full valid sets:
- `a!tabLayout` (6): `tabs, showWhen, marginAbove, marginBelow, highlightColor, contentsPadding`
- `a!tabItem` (6): `label, icon, contents, showWhen, validations, validationGroup`

---

When in doubt about any of the above: verify against the per-category schema in `ui-guidelines/reference/schemas/` or the official docs at `https://docs.appian.com/suite/help/26.4/<Component_Name>_Component.html`. Never invent by analogy with similar components — these new components were intentionally designed with smaller surface areas than their siblings.

---

## When the user pushes back

Sometimes users say things like "just use placeholder UUIDs, I'll fix them later" or "guess what the rule should be, we'll iterate".

This is almost always the wrong call. Reasoning:
- Placeholder UUIDs will silently look correct in the file but produce empty data at runtime. The user won't catch them until much later, in a worse context (a stakeholder demo).
- Guessed business rules become "what Claude generated", which then becomes the de facto spec, which is worse than no rule.

The right answer is one of:
- For UUIDs: revert to mockup mode with `local!` sample data and a clear note in the response that this is mockup-only until they provide the data-model context.
- For rules: leave the field unvalidated with a `/* TODO: Confirm rule */` comment.

If the user explicitly accepts the risk and asks again, then mark the invented values prominently with `/* INVENTED — replace before production */` and note them in your response. Don't bury them.
