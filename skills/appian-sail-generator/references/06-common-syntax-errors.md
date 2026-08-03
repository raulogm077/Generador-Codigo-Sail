# Common Syntax Errors — Catalog and Fixes

This file is the **fastest path to fixing a broken SAIL expression**. When the user pastes an Appian Designer error, or when validation flags an issue, scan this file first — most errors map to a small set of root causes.

Errors are grouped by category. Each entry shows the symptom, the root cause, and the canonical fix. Cross-references to the detailed guideline files are provided when more context is needed.

---

## 1. Operator / keyword syntax

### Symptom: "Invalid syntax near `and`" / "Unexpected token `or`"

**Cause:** Using SQL/JavaScript-style operators as keywords.

```sail
/* ❌ WRONG */
if(a > 0 and b < 10, "yes", "no")
if(a or b, ...)

/* ✅ RIGHT */
if(and(a > 0, b < 10), "yes", "no")
if(or(a, b), ...)
```

Operators are functions: `and(a, b)`, `or(a, b)`, `not(a)`, `equals(a, b)`. Never keywords.

### Symptom: "Unexpected `//`" / "Expected `*/`"

**Cause:** Wrong comment syntax.

```sail
/* ❌ WRONG */
// This is a comment

/* ✅ RIGHT */
/* This is a comment */
```

SAIL uses `/* ... */`. No `//`, no `#`.

### Symptom: "Expected `"`" / String not terminated

**Cause:** Escaping double quotes with backslash instead of doubling.

```sail
/* ❌ WRONG */
"He said \"hello\""

/* ✅ RIGHT */
"He said ""hello"""
```

---

## 2. Function variables (`fv!`) — wrong context

### Symptom: "Variable `fv!index` is not defined" (inside a grid column)

**Cause:** `fv!index` does not exist in grid `columns:`. Only `fv!row` is available there.

```sail
/* ❌ WRONG — inside a!gridColumn value */
a!textField(value: fv!index)

/* ✅ RIGHT — use grid selection to get index */
selectionValue: local!selected,
selectionSaveInto: local!selected,
/* Then access via index(local!selected, 1, null) elsewhere */
```

Full reference: `logic-guidelines/grid-selection-patterns.md`.

### Symptom: "Variable `fv!item` is not defined"

**Cause:** Using `fv!item` outside `a!forEach()`. `fv!item` exists only inside `a!forEach`.

```sail
/* ❌ WRONG — inside grid column */
a!textField(value: fv!item.name)

/* ✅ RIGHT — inside grid column */
a!textField(value: fv!row.name)

/* ✅ RIGHT — inside a!forEach */
a!forEach(items: local!users, expression: a!textField(value: fv!item.name))
```

Context cheat-sheet:
- Inside grid `columns:` → only `fv!row`.
- Inside `a!forEach()` → `fv!item`, `fv!index`, `fv!isFirst`, `fv!isLast`.
- Inside `a!save()` value parameter → `save!value` (also restricted; see below).

---

## 3. `save!value` misuse

### Symptom: "Variable `save!value` is not defined" / runtime error

**Cause:** `save!value` is valid **only** inside the `value` parameter of `a!save(target, value)`. Anywhere else fails.

```sail
/* ❌ WRONG — in a condition */
if(save!value = "X", ..., ...)

/* ❌ WRONG — as target */
a!save(save!value, "new")

/* ❌ WRONG — outside a!save */
local!foo: save!value

/* ✅ RIGHT */
saveInto: a!save(local!status, save!value)

/* ✅ RIGHT — with conditional inside value */
saveInto: a!save(local!status, if(save!value = "X", "X-mapped", save!value))
```

Full reference: `logic-guidelines/choice-field-patterns.md`.

---

## 4. Null safety — short-circuit failures

### Symptom: "Cannot evaluate property `foo` on null"

**Cause:** Using `and()` for null safety. `and()` evaluates **all** arguments — it does not short-circuit.

```sail
/* ❌ WRONG — crashes when local!case is null */
showWhen: and(a!isNotNullOrEmpty(local!case), local!case.status = "Open")

/* ✅ RIGHT — if() short-circuits */
showWhen: if(a!isNotNullOrEmpty(local!case), local!case.status = "Open", false())
```

Universal pattern:

| Scenario | Pattern |
|---|---|
| Comparison with nullable | `if(a!isNotNullOrEmpty(var), var = X, false())` |
| Property access | `if(a!isNotNullOrEmpty(obj), obj.prop, default)` |
| Function parameter | `function(a!defaultValue(var, default))` |
| Grid selection access | `index(selection, 1, null)` then check |
| Boolean `not()` on nullable | `not(a!defaultValue(var, false()))` |

Full reference: `logic-guidelines/null-safety-quick-ref.md`.

---

## 5. Array / list type issues

### Symptom: "Type mismatch" with `contains()`, `wherecontains()`, `union()`

**Cause:** Untyped empty array `{}` is "List of Variant", not the type the function expects.

```sail
/* ❌ WRONG — {} is List of Variant */
contains({}, "X")
local!ids: {}

/* ✅ RIGHT — type-initialise */
contains(touniformstring({}), "X")
local!ids: tointeger({})
```

Type initialisers:
- `tointeger({})` — IDs, counts, numeric selections.
- `touniformstring({})` — text arrays. **Not `tostring({})`** — that merges to one string.
- `toboolean({})`, `todate({})`, `todatetime({})`, `todecimal({})`, `totime({})`, `touser({})`, `togroup({})`.

Full reference: `logic-guidelines/array-type-initialization-guidelines.md`.

### Symptom: "Cannot convert Interval to Number"

**Cause:** Comparing the result of date subtraction (which is an Interval) directly to a number.

```sail
/* ❌ WRONG */
if(now() - fv!row.timestamp < 1, ...)

/* ✅ RIGHT */
if(tointeger(now() - fv!row.timestamp) < 1, ...)
```

### Symptom: "Cannot use Date in arithmetic"

**Cause:** Date arithmetic produces unexpected types — wrap in `todate()` / `todatetime()`.

```sail
/* ❌ WRONG */
local!due: today() + 7

/* ✅ RIGHT */
local!due: todate(today() + 7)
```

Full reference: `logic-guidelines/datetime-handling.md`.

---

## 6. Choice field (radio / checkbox / dropdown) errors

### Symptom: "`choiceValues` cannot contain null values"

**Cause:** Empty string or `null` in `choiceValues`.

```sail
/* ❌ WRONG */
choiceLabels: {"All", "Open", "Closed"},
choiceValues: {"", "Open", "Closed"}

/* ✅ RIGHT — use a non-empty placeholder or omit the "All" entry */
choiceLabels: {"Open", "Closed"},
choiceValues: {"Open", "Closed"}

/* OR — for "All", use placeholder + filter logic */
placeholder: "All",
choiceLabels: {"Open", "Closed"},
choiceValues: {"Open", "Closed"}
```

### Symptom: Single checkbox unchecked but `showWhen` still true

**Cause:** Initialising the local to `false()` instead of leaving it uninitialised (null).

```sail
/* ❌ WRONG */
local!agreeToTerms: false(),  /* choiceValues: {true()} */

/* ✅ RIGHT */
local!agreeToTerms,  /* uninitialised = unchecked */

/* Then check with isNotNullOrEmpty, NOT contains */
showWhen: a!isNotNullOrEmpty(local!agreeToTerms)
```

Full reference: `logic-guidelines/choice-field-patterns.md`.

---

## 7. Layout / nesting errors

### Symptom: "`sideBySideLayout` cannot contain `sideBySideLayout`" / runtime nesting error

**Cause:** Common nesting mistakes.

| ❌ Wrong | ✅ Right |
|---|---|
| `a!sideBySideLayout` inside another `a!sideBySideLayout` | Restructure as a single `a!sideBySideLayout` with more `items`, or use `a!columnsLayout` |
| `a!columnsLayout` inside `a!sideBySideItem` | Move the columns out; keep side-by-side flat |
| `a!cardLayout` inside `a!sideBySideItem` | Move the card out; side-by-side items hold single inline components |
| Array of components inside one `a!sideBySideItem` | Each `a!sideBySideItem` holds **one** component; split into multiple items |
| `a!columnsLayout` with no `AUTO`-width column | Make at least one column `AUTO` |

### Symptom: "`richTextDisplayField` contains invalid child"

**Cause:** Only `a!richTextItem`, `a!richTextIcon`, `a!richTextBulletedList`, `a!richTextNumberedList`, `a!richTextImage`, `a!richTextListItem`, and `a!richTextHeader` are allowed inside `a!richTextDisplayField`. Plain strings or other display/input components (e.g. `a!textField`, `a!stampField`, `a!imageField`) are not valid children. Note: `a!richTextHeader` is deprecated by Appian — prefer `a!headingField` for new code (it is a standalone display field, not a richText child).

```sail
/* ❌ WRONG — textField is not a richText child */
a!richTextDisplayField(value: {
  a!textField(...)
})

/* ❌ WRONG — imageField cannot live inside richText. Use a!richTextImage */
a!richTextDisplayField(value: {
  a!imageField(images: a!documentImage(document: ...))
})

/* ✅ RIGHT — text styling */
a!richTextDisplayField(value: {
  a!richTextItem(text: "Hello", style: "STRONG")
})

/* ✅ RIGHT — inline image */
a!richTextDisplayField(value: {
  "Status: ",
  a!richTextImage(
    image: a!documentImage(document: a!iconIndicator(icon: "CHECK_CIRCLE"))
  )
})
```

Full reference: `ui-guidelines/components/rich-text-instructions.md`.

---

## 8. Grid-specific errors

### Symptom: "`sortField` is not unique" / sort not working

**Cause:** Two columns using the same `sortField`, or `sortField` on a computed column.

```sail
/* ❌ WRONG — two columns same sortField */
a!gridColumn(label: "Title", sortField: "name", value: fv!row.name),
a!gridColumn(label: "Display Name", sortField: "name", value: concat(fv!row.firstName, " ", fv!row.lastName))

/* ❌ WRONG — sortField on computed column */
a!gridColumn(label: "Full Name", sortField: "fullName", value: concat(fv!row.firstName, " ", fv!row.lastName))

/* ✅ RIGHT */
a!gridColumn(label: "Title", sortField: "name", value: fv!row.name),
/* Computed column has NO sortField */
a!gridColumn(label: "Full Name", value: concat(fv!row.firstName, " ", fv!row.lastName))
```

Rule: `sortField` matches the **primary** field in `value:`, unique across columns, **never on computed/expression columns**.

### Symptom: "`showSearchBox` is invalid for non-record data" / runtime error

**Cause:** Grid record-only parameters used with local data (mockup mode).

```sail
/* ❌ WRONG — local data with record-only parameters */
a!gridLayout(
  data: local!cases,        /* local data */
  showSearchBox: true(),    /* record-only! */
  userFilters: {...},       /* record-only! */
  recordActions: {...}      /* record-only! */
)

/* ✅ RIGHT — in a mockup, custom search/filter UX with TODO-CONVERTER */
/* TODO-CONVERTER: Convert to showSearchBox: true */
a!textField(label: "Search", value: local!searchText, saveInto: local!searchText),
a!gridLayout(data: local!cases, ...)
```

After Phase 2 conversion to record-backed data, `showSearchBox` / `userFilters` / `recordActions` become valid.

---

## 9. Button errors

### Symptom: "`style: "PRIMARY"` is not a valid value"

**Cause:** Using legacy/invalid `style` value.

```sail
/* ❌ WRONG */
a!buttonWidget(label: "Submit", style: "PRIMARY")

/* ✅ RIGHT — combine style + color */
a!buttonWidget(label: "Submit", style: "SOLID", color: "ACCENT")
```

| Valid `style` | Valid `color` |
|---|---|
| `"OUTLINE"`, `"GHOST"`, `"LINK"`, `"SOLID"` | `"ACCENT"`, `"SECONDARY"`, `"NEGATIVE"`, `#RRGGBB` |

### Symptom: "`a!buttonWidget` outside `a!buttonArrayLayout`"

**Cause:** Buttons must be wrapped.

```sail
/* ❌ WRONG */
contents: { a!buttonWidget(...) }

/* ✅ RIGHT */
contents: { a!buttonArrayLayout(buttons: { a!buttonWidget(...) }) }
```

---

## 10. Icon errors

### Symptom: "Icon `home` is not a valid alias" / "Invalid icon name"

**Cause:** Inventing an icon name. SAIL accepts only specific aliases.

**Fix:** Grep `ui-guidelines/reference/rich-text-icon-aliases.md` for the icon you need. Common confusions:

| Tried | Correct alias |
|---|---|
| `"home"` | `"home"` is valid, but check casing — aliases are lowercase |
| `"user"` | `"user"` (valid); related: `"user-circle"`, `"user-plus"` |
| `"settings"` | `"cog"` or `"gear"` (depending on era) |
| `"trash"` | `"trash"` (valid); also `"trash-o"` |
| `"x"` | `"times"` |
| `"checkmark"` | `"check"` or `"check-circle"` |

When in doubt: grep first, ask second.

---

## 11. Mockup-only invariants (Phase 1 leakage of Phase 2 patterns)

### Symptom: "Rule input `ri!foo` is not defined" / "Record type `recordType!Bar` is not defined"

**Cause:** Mockup used `ri!` or `recordType!` references — but mockups are pure local-data prototypes. These references only become valid after Phase 2 conversion (where the interface is bound to rule inputs and an environment with record types).

```sail
/* ❌ WRONG — in a mockup */
local!data: a!queryRecordType(recordType: 'recordType!Case', ...).data

/* ✅ RIGHT — in a mockup */
local!data: {
  a!map(id: 1, title: "Case A", status: "Open"),
  a!map(id: 2, title: "Case B", status: "Closed")
}
```

If the user wants record data, run **Phase 2 conversion** (see `references/02-conversion-workflow.md`).

### Symptom: Mockup re-evaluates differently each time

**Cause:** Runtime generators (`rand()`, `now()`, `today()`) in sample data.

```sail
/* ❌ WRONG */
local!caseId: "CASE-" & text(rand(10000), "0000")
local!submitted: today()

/* ✅ RIGHT — static hard-coded */
local!caseId: "CASE-5847"
local!submitted: date(2025, 1, 15)
```

---

## 12. Parameter / value not in schema

### Symptom: "Parameter `size: "MEDIUM"` is not allowed for `a!tagField`"

**Cause:** Using a value that *looks* reasonable but isn't in the component's `validValues`.

**Fix:** Open the relevant schema in `ui-guidelines/reference/schemas/*.json` and check the `validValues` array for that parameter on that exact component.

```sail
/* a!tagField "size" accepts only "SMALL", "STANDARD" — not "MEDIUM" / "LARGE" */
a!tagField(text: "Open", size: "STANDARD")  /* ✅ */
```

Per-component value sets vary. **Never assume**:
- `"MEDIUM"` is universally valid.
- `"ACCENT"` works in every `color:` parameter.
- `"LEFT"` / `"START"` are interchangeable (`richTextItem.align` is `LEFT/CENTER/RIGHT`, not `START/END`).

If the schema says a value isn't there, it's not there. Grep `ui-guidelines/reference/schemas/<schema-file>.json` for the parameter and read the allowed list.

---

## 13. Inline function / lambda attempts

### Symptom: "Unexpected `function` keyword" / "Invalid syntax"

**Cause:** Trying to define a helper function inline.

```sail
/* ❌ WRONG — SAIL has no lambdas */
local!calcColor: function(status)(
  if(status = "Open", "POSITIVE", "STANDARD")
)

/* ❌ WRONG — variable cannot store rule reference */
local!helper: rule!myColorHelper

/* ✅ RIGHT — duplicate inline */
/* In column 1 */
color: if(fv!row.status = "Open", "POSITIVE", "STANDARD"),
/* In column 2 (same logic, duplicated) */
color: if(fv!row.status = "Open", "POSITIVE", "STANDARD"),

/* Leave a TODO if duplicated 3+ times */
/* TODO: Extract to expression rule — status colour logic appears in N places */
```

---

## 14. Expression / variable scope errors

### Symptom: "Variable `local!foo` is not defined"

**Cause:** Variable used outside the `a!localVariables` that declares it, or misspelled.

```sail
/* ❌ WRONG */
a!localVariables(
  local!searchText: "",
  a!textField(value: local!searchTxt)  /* typo */
)

/* ✅ RIGHT — names match exactly */
a!localVariables(
  local!searchText: "",
  a!textField(value: local!searchText, saveInto: local!searchText)
)
```

### Symptom: "Variable `local!foo` declared but never used"

**Cause:** Dead variable — declare it only if it's referenced somewhere.

```sail
/* ✅ Either remove it, or mark it */
a!localVariables(
  /* UNUSED — reserved for future filter feature */
  local!futureFilter: tointeger({}),
  /* ... */
)
```

---

## 15. New-component-specific errors (toggle, boolean checkbox, signature, gauge, pickers, by-index, video, web content, tabs)

These errors are specific to components added in V8. They are easy to miss because the components look superficially similar to older ones with different parameter shapes.

### 15.1 `a!toggleField` / `a!booleanCheckboxField` — wrong label parameter

**Symptom:** "Parameter `label` is not allowed for `a!toggleField`" or the toggle renders without any label text.

**Cause:** Both components use `choiceLabel:` (singular, like a single checkbox), NOT `label:` / `labelPosition:` / `instructions:`. They do not inherit the standard label set.

```sail
/* ❌ WRONG */
a!toggleField(
  label: "Enable notifications",
  labelPosition: "ABOVE",
  value: local!enabled,
  saveInto: local!enabled
)

/* ✅ RIGHT */
a!toggleField(
  choiceLabel: "Enable notifications",
  value: local!enabled,
  saveInto: local!enabled
)
```

Same shape for `a!booleanCheckboxField`. When in doubt: toggle/boolean-checkbox have only `choiceLabel`, no `label`/`labelPosition`/`instructions`.

### 15.2 `a!toggleField` used inside a form

**Symptom:** Visual works in mockup; in production a form submission re-validates poorly or the field doesn't honour required-message UX as expected.

**Cause:** `a!toggleField` is for **immediate-effect settings** (dark mode, "show inactive users"). For form acceptance (terms, agreements, opt-in), use `a!booleanCheckboxField`.

```sail
/* ❌ WRONG — toggle for form acceptance */
a!formLayout(
  contents: { a!toggleField(choiceLabel: "I accept the terms", value: local!agree, saveInto: local!agree, required: true) }
)

/* ✅ RIGHT — boolean checkbox for form acceptance */
a!formLayout(
  contents: { a!booleanCheckboxField(choiceLabel: "I accept the terms", value: local!agree, saveInto: local!agree, required: true) }
)
```

### 15.3 `a!signatureField` used outside a start form / task form

**Symptom:** Signature appears to capture in the UI but nothing persists to the target folder, or you get an error about file submission.

**Cause:** `a!signatureField` only persists natively in **start forms or task forms** (with `submit: true` on the submit button). Anywhere else the signature lives in a temp folder and is auto-deleted after 30 days.

```sail
/* ❌ WRONG — signature on a detail page or wizard step without submit flow */
a!sectionLayout(contents: { a!signatureField(target: cons!SIG_FOLDER, value: local!sig, saveInto: local!sig) })

/* ✅ RIGHT — signature in a start/task form */
a!formLayout(
  contents: { a!signatureField(target: cons!SIG_FOLDER, value: local!sig, saveInto: local!sig, required: true) },
  buttons: a!buttonLayout(primaryButtons: { a!buttonWidget(label: "Submit", style: "SOLID", submit: true) })
)

/* ✅ RIGHT — signature outside a form: wrap save in a!submitUploadedFiles() */
a!buttonWidget(
  label: "Save signature",
  saveInto: a!submitUploadedFiles(
    onSuccess: a!save(local!ok, true),
    onError: a!save(local!ok, false)
  )
)
```

**Other signature pitfalls** that look like validator issues but aren't:
- `validations` parameter does not exist on signatureField. Use `requiredMessage` only.
- User (or portal service account) must have **Editor** permissions on the `target` folder.

### 15.4 `a!gaugeField.primaryText` — wrong helper used

**Symptom:** `primaryText` shows hand-built text instead of the intended fraction/percentage/icon, OR a runtime error mentioning richText.

**Cause:** `primaryText` accepts plain text or one of three dedicated helpers: `a!gaugeFraction`, `a!gaugePercentage`, `a!gaugeIcon`. It does **not** accept `a!richTextIcon` (which crashes) and should not be hand-built with `text()`/`concat()`.

```sail
/* ❌ WRONG — richTextIcon inside gauge (runtime error) */
a!gaugeField(percentage: 80, primaryText: a!richTextIcon(icon: "check"), color: "POSITIVE")

/* ❌ WRONG — hand-built fraction string */
a!gaugeField(percentage: 25/26*100, primaryText: text(25) & "/" & text(26))

/* ❌ WRONG — hand-built percentage */
a!gaugeField(percentage: 78, primaryText: text(round(78), "0") & "%")

/* ✅ RIGHT */
a!gaugeField(percentage: 80, primaryText: a!gaugeIcon(icon: "check"), color: "POSITIVE")
a!gaugeField(percentage: 25/26*100, primaryText: a!gaugeFraction(denominator: 26))
a!gaugeField(percentage: 78, primaryText: a!gaugePercentage())
```

### 15.5 `a!gaugeFraction` — invented `numerator` parameter

**Symptom:** "Parameter `numerator` is not allowed for `a!gaugeFraction`".

**Cause:** `a!gaugeFraction` accepts only `denominator`. The numerator is **computed automatically** from the parent gauge's `percentage:`.

```sail
/* ❌ WRONG */
primaryText: a!gaugeFraction(numerator: 25, denominator: 26)

/* ✅ RIGHT — gauge percentage drives the numerator */
percentage: 25/26 * 100,                        /* drives numerator (rounded) */
primaryText: a!gaugeFraction(denominator: 26)   /* shows "25/26" */
```

### 15.6 `*ByIndex` field — passing value instead of index

**Symptom:** Selection appears empty, or `saveInto` receives a string instead of an integer.

**Cause:** `a!dropdownFieldByIndex`, `a!radioButtonFieldByIndex`, `a!checkboxFieldByIndex`, `a!multipleDropdownFieldByIndex` operate on **1-based indices**, not on values. `value:` and `saveInto:` are Integer (or List of Integer for multi-select), not Text. There is no `choiceValues` parameter.

```sail
/* ❌ WRONG — treating index field like a value field */
a!dropdownFieldByIndex(
  choiceLabels: {"Open", "In Progress", "Closed"},
  choiceValues: {"open", "in_progress", "closed"},  /* parameter does not exist */
  value: local!status,                              /* expects Integer, got Text */
  saveInto: local!status
)

/* ✅ RIGHT — index-based selection */
a!dropdownFieldByIndex(
  choiceLabels: {"Open", "In Progress", "Closed"},
  value: local!statusIndex,           /* Integer; 1=Open, 2=In Progress, 3=Closed */
  saveInto: local!statusIndex
)

/* If you need the value, look it up after: */
local!statusValue: index({"open", "in_progress", "closed"}, local!statusIndex, "")
```

### 15.7 `a!pickerFieldRecords` — missing `recordType:` parameter

**Symptom:** "Required parameter `recordType` is missing" or the picker never shows suggestions.

**Cause:** `recordType:` is **required**. Without it the picker has nothing to search against. Use the record-type literal (`'recordType!{uuid}Name'`), not a string name.

```sail
/* ❌ WRONG */
a!pickerFieldRecords(label: "Case", value: local!case, saveInto: local!case)

/* ✅ RIGHT */
a!pickerFieldRecords(
  label: "Case",
  recordType: 'recordType!{uuid}Case',
  value: local!case,
  saveInto: local!case
)
```

Note: `value` and `saveInto` always receive an **array** of selected records, even if `maxSelections: 1`. Use `index(local!case, 1, null)` to get the single value.

### 15.8 `a!videoField` / `a!webContentField` — wrong source parameter

**Symptom:** "Parameter `url`/`source` is not allowed" or the component renders empty.

**Cause:**
- `a!videoField` requires `videos:` — an array of `a!webVideo(...)` objects, not a URL string directly.
- `a!webContentField` requires `source:` — a Safe URI, **not** `url:`.

```sail
/* ❌ WRONG */
a!videoField(label: "Intro", url: "https://example.com/intro.mp4")
a!webContentField(label: "Map", url: "https://maps.example.com")

/* ✅ RIGHT */
a!videoField(label: "Intro", videos: { a!webVideo(source: "https://example.com/intro.mp4") })
a!webContentField(label: "Map", source: "https://maps.example.com")
```

### 15.9 `a!tabLayout` — wrong parameter name (`items` instead of `tabs`)

**Symptom:** "Parameter `items` is not allowed for `a!tabLayout`" or the tabs render empty.

**Cause:** The container parameter is `tabs:`, not `items:` (which is what `a!sideBySideLayout` uses). Easy slip if you came from a side-by-side or column layout.

```sail
/* ❌ WRONG */
a!tabLayout(items: { a!tabItem(label: "One", contents: {...}) })

/* ✅ RIGHT */
a!tabLayout(tabs: { a!tabItem(label: "One", contents: {...}) })
```

### 15.10 `a!tabLayout` nested inside a forbidden container

**Symptom:** Runtime error about layout containment, or odd rendering.

**Cause:** `a!tabLayout` cannot be nested inside `a!sideBySideLayout`, an editable grid layout, or a read-only grid. If you need tab-like UX in those places, use the custom card-based pattern in `ui-guidelines/patterns/tabs.md`.

```sail
/* ❌ WRONG */
a!sideBySideLayout(items: { a!sideBySideItem(item: a!tabLayout(tabs: {...})) })

/* ✅ RIGHT — move the tabLayout outside sideBySide, or use the custom tabs pattern */
```

### 15.11 `a!tabItem.icon` — invented alias

Same rule as any other `icon:` value: every alias must appear verbatim in `ui-guidelines/reference/rich-text-icon-aliases.md`. Grep before writing.

---

## How to use this catalog

1. **When the user pastes an Appian Designer error** → scan the symptom list, find the closest match, apply the fix.
2. **When validation reports an issue** → same.
3. **When writing fresh SAIL** → use this list as a self-check pass before declaring done.
4. **When stuck on an error not listed here** → grep the relevant guideline file (`logic-guidelines/*` for logic/runtime, `ui-guidelines/*` for component/layout, `conversion-guidelines/*` for record-type integration).

A single pass through this catalog after generation catches the vast majority of syntax errors that would otherwise reach the user.
