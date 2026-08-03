# By-Index Choice Fields and Multiple Dropdown — Usage Instructions

This file covers the choice components whose names follow the `*FieldByIndex` pattern. They save the **1-based index** of the selected choice(s) instead of the value, which is useful when the choice list is dynamic and you want to avoid stale value references.

> ⚠️ The naming convention is `XFieldByIndex` (e.g. `a!checkboxFieldByIndex`), **not** `XByIndexField`. Common mistake.

Components in this file:
- `a!dropdownFieldByIndex` — pick one, save its index
- `a!multipleDropdownFieldByIndex` — pick many, save their indices
- `a!radioButtonFieldByIndex` — pick one, save its index
- `a!checkboxFieldByIndex` — pick many, save their indices
- `a!multipleDropdownField` — pick many, save the *values* (NOT by-index, but related)

> 💡 **Choice index numbers start at 1.** They cannot be less than 1 or greater than the length of the `choiceLabels` array.

---

## a!dropdownFieldByIndex

Pick one item from a dropdown, save the index.

```sail
a!dropdownFieldByIndex(
  label, labelPosition, instructions,
  required, disabled,
  choiceLabels,           /* List of Text — REQUIRED, cannot be null */
  placeholder,            /* Text — shown when value is null */
  value,                  /* Number (Integer) — selected index, 1-based */
  validations, saveInto, validationGroup, requiredMessage,
  helpTooltip, accessibilityText, showWhen,
  searchDisplay           /* "AUTO" (default) | "ON" | "OFF" — AUTO shows search if >11 options */
)
```

### Example
```sail
a!localVariables(
  local!languageIndex: 1,
  a!dropdownFieldByIndex(
    label: "Language",
    choiceLabels: {"English", "Spanish", "French", "German"},
    value: local!languageIndex,
    saveInto: local!languageIndex
  )
)
```

---

## a!multipleDropdownFieldByIndex

Pick several items, save their indices.

```sail
a!multipleDropdownFieldByIndex(
  label, labelPosition, instructions,
  required, disabled,
  placeholder, choiceLabels,
  value,                  /* List of Number (Integer) — selected indices */
  validations, saveInto, validationGroup, requiredMessage,
  helpTooltip, accessibilityText, showWhen,
  searchDisplay           /* "AUTO" (default) | "ON" | "OFF" */
)
```

### Example
```sail
a!localVariables(
  local!languages: {1, 3},   /* English + French */
  a!multipleDropdownFieldByIndex(
    label: "Languages spoken",
    choiceLabels: {"English", "Spanish", "French", "German"},
    value: local!languages,
    saveInto: local!languages
  )
)
```

> If a list is passed to `value`, it **cannot contain a null**. Pass `null` to clear all selections, not `{null}`.

---

## a!radioButtonFieldByIndex

Pick exactly one from a set of radio buttons, save the index.

```sail
a!radioButtonFieldByIndex(
  label, instructions, required, disabled,
  choiceLabels,           /* REQUIRED */
  value,                  /* Number (Integer) — selected index, 1-based */
  validations, saveInto, validationGroup, requiredMessage,
  labelPosition,
  choiceLayout,           /* "STACKED" (default) | "COMPACT" */
  helpTooltip, accessibilityText, showWhen,
  choiceStyle             /* "STANDARD" (default) | "CARDS" */
)
```

### Example
```sail
a!radioButtonFieldByIndex(
  label: "Severity",
  choiceLabels: {"Low", "Medium", "High", "Critical"},
  value: local!severityIndex,
  saveInto: local!severityIndex,
  choiceLayout: "COMPACT",
  required: true
)
```

> `"COMPACT"` is only for **short labels** (e.g. "Yes", "No", "Maybe"). Labels >2 lines get truncated in COMPACT mode.

---

## a!checkboxFieldByIndex

Pick none/one/many, save their indices.

```sail
a!checkboxFieldByIndex(
  label, instructions, required, disabled,
  choiceLabels,           /* REQUIRED */
  value,                  /* List of Number (Integer) — selected indices */
  validations, saveInto, validationGroup, requiredMessage,
  align,                  /* "LEFT" | "CENTER" | "RIGHT" — recommended only in Grid Layout */
  labelPosition,
  helpTooltip,
  choiceLayout,           /* "STACKED" (default) | "COMPACT" */
  accessibilityText, showWhen,
  choiceStyle,            /* "STANDARD" (default) | "CARDS" */
  choicePosition          /* "START" | "END" — auto: START for STANDARD, END for CARDS */
)
```

### Example
```sail
a!checkboxFieldByIndex(
  label: "Notification channels",
  choiceLabels: {"Email", "SMS", "Push", "Slack"},
  value: local!channelIndices,
  saveInto: local!channelIndices,
  choiceLayout: "COMPACT"
)
```

> `a!checkboxFieldByIndex` is **not available from the design view component picker** — only configurable via expression.

---

## a!multipleDropdownField (saves values, not indices)

For completeness — this is the "save values" sibling of `a!multipleDropdownFieldByIndex`.

```sail
a!multipleDropdownField(
  label, instructions, required, disabled,
  placeholder, choiceLabels, choiceValues,
  value,                  /* List of Any — selected values */
  validations, saveInto, validationGroup, requiredMessage,
  labelPosition, helpTooltip, accessibilityText, showWhen,
  searchDisplay,          /* "AUTO" (default) | "ON" | "OFF" */
  data,                   /* Record data alternative to choiceLabels/choiceValues */
  sort,                   /* a!sortInfo() */
  marginAbove, marginBelow
)
```

### Example (with explicit labels/values)
```sail
a!multipleDropdownField(
  label: "Tags",
  choiceLabels: {"Bug", "Feature", "Question", "Docs"},
  choiceValues: {"bug", "feat", "q", "docs"},
  value: local!selectedTags,
  saveInto: local!selectedTags
)
```

### Example (record-backed)
```sail
a!multipleDropdownField(
  label: "Assigned tags",
  data: a!recordData(recordType: recordType!Tag),
  choiceLabels: fv!data[recordType!Tag.fields.name],
  choiceValues: fv!data[recordType!Tag.fields.id],
  value: local!tagIds,
  saveInto: local!tagIds,
  searchDisplay: "ON"
)
```

---

## Choosing between by-index and by-value

| Scenario | Use |
|---|---|
| Choice list is **static** in code, you want the actual value saved | `a!checkboxField` / `a!dropdownField` / etc. |
| Choice list comes from a **record query** and you want the record ID | `a!multipleDropdownField` with `data:` |
| Choice list might **change order** between sessions and you want stability | `*FieldByIndex` variants |
| You **already store indices** in your data model | `*FieldByIndex` variants |

---

## Validation Checklist

- [ ] Function name is `*FieldByIndex` (NOT `*ByIndexField`)
- [ ] `choiceLabels` is provided (cannot be null)
- [ ] `value` is a 1-based index (or a list of them for multi)
- [ ] No index in `value` is `< 1` or `> length(choiceLabels)`
- [ ] `choiceLayout` is `"STACKED"` or `"COMPACT"` if set
- [ ] `choiceStyle` is `"STANDARD"` or `"CARDS"` if set
- [ ] `searchDisplay` is `"AUTO"`/`"ON"`/`"OFF"` if set
- [ ] `align` only used inside a Grid Layout (for `checkboxFieldByIndex`)
- [ ] For multi variants: `value` list does not contain null

Docs:
- <https://docs.appian.com/suite/help/latest/Dropdown_By_Index_Component.html>
- <https://docs.appian.com/suite/help/latest/Multiple_Dropdown_By_Index_Component.html>
- <https://docs.appian.com/suite/help/latest/Radio_Button_By_Index_Component.html>
- <https://docs.appian.com/suite/help/latest/Checkbox_By_Index_Component.html>
- <https://docs.appian.com/suite/help/latest/Multiple_Dropdown_Component.html>
