# Null Safety - Quick Pattern Lookup

> **Related documentation:**
> - `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` → Short-circuit evaluation rules
> - `logic-guidelines/short-circuit-evaluation.md` → Detailed short-circuit patterns
> - `conversion-guidelines/validation-enforcement-module.md` → Null safety enforcement workflow

## Detection Commands

Run these to find vulnerable patterns:

```bash
# Find all text() calls
grep -n "text(" output/interface.sail

# Find all user() calls
grep -n "user(" output/interface.sail

# Find all string concatenations
grep -n " & " output/interface.sail

# Find all todate() on fields
grep -n "todate(fv!row\|todate(ri!" output/interface.sail

# Find queryFilters without applyWhen
grep -B5 "a!queryFilter(" output/interface.sail | grep -v "applyWhen"
```

## Standard Patterns

| **Scenario** | **Protected Pattern** | **Fallback** |
|-------------|----------------------|-------------|
| **Display - Integer** | `if(a!isNotNullOrEmpty(field), field, "N/A")` | "N/A" |
| **Display - Decimal** | `if(a!isNotNullOrEmpty(field), field, "N/A")` | "N/A" |
| **Display - Text** | `if(a!isNotNullOrEmpty(field), field, "N/A")` | "N/A" |
| **Display - Date** | `if(a!isNotNullOrEmpty(field), text(todate(field), "MMM d, yyyy"), "N/A")` | "N/A" |
| **Display - DateTime** | `if(a!isNotNullOrEmpty(field), text(field, "MMM d, yyyy h:mm a"), "N/A")` | "N/A" |
| **Display - Time** | `if(a!isNotNullOrEmpty(field), text(field, "h:mm a"), "N/A")` | "N/A" |
| **user() function** | `if(a!isNotNullOrEmpty(userId), trim(user(userId, "firstName") & " " & user(userId, "lastName")), "N/A")` | "N/A" |
| **Concat - with field** | `"PREFIX-" & if(a!isNotNullOrEmpty(field), field, "N/A")` | "N/A" |
| **Concat - without formatting** | `a!defaultValue(field1, "") & " " & a!defaultValue(field2, "")` | "" |
| **Date arithmetic** | `if(a!isNotNullOrEmpty(field), todate(field + 30), null)` | null |
| **Date comparison** | `if(if(a!isNotNullOrEmpty(field), todate(field + 30) < today(), false), ...)` | false |
| **a!queryFilter (ri!/local!)** | `a!queryFilter(..., value: local!var, applyWhen: a!isNotNullOrEmpty(local!var))` | Filter skipped |
| **a!queryFilter (literal)** | `a!queryFilter(..., value: "Active")` - NO applyWhen needed | N/A |
| **Display field** | `a!defaultValue(field, "N/A")` | "N/A" |
| **Editable field** | `field` (direct - no a!defaultValue) | N/A |
| **not() function** | `not(a!defaultValue(var, false()))` | false() |
| **ri!isUpdate (showWhen)** | `showWhen: not(a!defaultValue(ri!isUpdate, false()))` | false() (CREATE mode) |
| **ri!isUpdate (if/logic)** | `if(a!defaultValue(ri!isUpdate, false()), ..., ...)` | false() (CREATE mode) |
| **ri!cancel (if/logic)** | `if(a!defaultValue(ri!cancel, false()), ..., ...)` | false() (not cancelled) |

**Note:** For editable fields (textField, integerField, dateField, etc.), use the variable/rule input directly in both `value` and `saveInto` parameters. Do NOT use a!defaultValue(). Appian handles null values automatically in form fields.

**Special Rule - Boolean Rule Inputs:** Rule inputs like `ri!isUpdate` and `ri!cancel` may be null when not explicitly passed by the process model. Always wrap in `a!defaultValue(ri!isUpdate, false())` before using with `not()`, `if()`, or `and()`/`or()` functions.

## Form Input Components - Special Rules

**Editable form input components (textField, dateField, dropdownField, etc.) handle null automatically. Do NOT add null checking to `value` or `saveInto` parameters.**

### Input Field Pattern (value/saveInto)

```sail
/* ✅ CORRECT - Direct field binding */
a!textField(
  label: "Case Description",
  value: ri!submission['recordType!Case.fields.description'],
  saveInto: {
    ri!submission['recordType!Case.fields.description'],
    a!save(local!hasUnsavedChanges, true())
  },
  required: true()
)

/* ❌ WRONG - Unnecessary null checking */
a!textField(
  label: "Case Description",
  value: a!defaultValue(
    if(
      a!isNotNullOrEmpty(ri!submission),
      ri!submission['recordType!Case.fields.description'],
      null
    ),
    null
  ),
  saveInto: {
    if(
      a!isNotNullOrEmpty(ri!submission),
      a!save(ri!submission['recordType!Case.fields.description'], save!value),
      {}
    ),
    a!save(local!hasUnsavedChanges, true())
  }
)
```

**Why:** Appian form components are designed to handle null values in create/update forms. Adding null checks adds complexity without benefit.

**Applies to:** textField, integerField, dateField, dateTimeField, dropdownField, checkboxField, radioButtonField, paragraphField, fileUploadField, pickerField, etc.

### Dropdown Field Choice Parameters (choiceLabels/choiceValues)

**Exception:** For dropdownField, `choiceLabels` and `choiceValues` parameters that query data DO need null checking:

```sail
/* ✅ CORRECT - Null check for choice parameters */
a!dropdownField(
  label: "Position Type",
  choiceLabels: if(
    a!isNotNullOrEmpty(local!positionTypes),
    local!positionTypes['recordType!PositionType.fields.name'],
    {}
  ),
  choiceValues: if(
    a!isNotNullOrEmpty(local!positionTypes),
    local!positionTypes['recordType!PositionType.fields.id'],
    {}
  ),
  value: ri!submission['recordType!Case.fields.positionTypeId'],
  saveInto: {
    ri!submission['recordType!Case.fields.positionTypeId'],
    a!save(local!hasUnsavedChanges, true())
  }
)
```

**Why:** `choiceLabels` and `choiceValues` are arrays extracted from query results. If the query returns null/empty, accessing fields would crash. But `value`/`saveInto` still use direct field binding.

### Single-Field Validation Pattern

**For validations that only check the current field's format/value, NO null check is needed - SAIL only evaluates validations when the field has a value:**

```sail
/* ✅ CORRECT - No null check needed for single-field validation */
validations: a!localVariables(
  local!trimmed: trim(local!email),
  if(/* validation logic */,
    "Error message",
    {}
  )
)

/* ❌ WRONG - Redundant null check */
validations: if(
  a!isNotNullOrEmpty(local!email),
  /* validation logic */,
  {}
)
```

**Why:** The `validations` parameter is only evaluated when the field's `value` is not null/empty. Adding `a!isNotNullOrEmpty()` is redundant.

### Cross-Field Validation Pattern

**For validation logic that compares two fields, simplify null checks:**

```sail
/* ✅ CORRECT - Simplified validation */
validations: if(
  and(
    a!isNotNullOrEmpty(ri!submission['recordType!Case.fields.startDate']),
    a!isNotNullOrEmpty(ri!submission['recordType!Case.fields.endDate']),
    ri!submission['recordType!Case.fields.endDate'] <= ri!submission['recordType!Case.fields.startDate']
  ),
  "End Date must be after Start Date",
  null
)

/* ❌ WRONG - Over-defensive checking */
validations: if(
  and(
    a!isNotNullOrEmpty(
      if(
        a!isNotNullOrEmpty(ri!submission),
        ri!submission['recordType!Case.fields.startDate'],
        null
      )
    ),
    a!isNotNullOrEmpty(
      if(
        a!isNotNullOrEmpty(ri!submission),
        ri!submission['recordType!Case.fields.endDate'],
        null
      )
    ),
    if(...nested checks...)
  ),
  "End Date must be after Start Date",
  null
)
```

## Nested if() Pattern (Short-Circuit)

**Use when:** Accessing properties on computed variables OR comparing dates with arithmetic

```sail
/* ✅ CORRECT - Nested if() for short-circuit behavior */
if(
  if(
    a!isNotNullOrEmpty(variable),
    variable.property = "value",  /* OR: todate(variable + 30) < today() */
    false
  ),
  /* Then branch - condition is true */,
  /* Else branch - condition is false or variable is null */
)
```

**Why nested if():** SAIL's `and()` function does NOT short-circuit - it evaluates ALL arguments even if the first is false. This causes crashes when accessing properties on null/empty variables.

**Common scenarios requiring nested if():**
- Grid selections: `local!selectedItems.type = "Contract"`
- Filtered arrays: `local!activeUsers.role`
- Date comparisons with arithmetic: `todate(field + 30) < today()`
- Any property access on computed/derived variables

## Date/Time Field Handling

**Critical:** Date and DateTime fields require different functions. Always check field type in data model.

### Date Fields (type: Date)
```sail
/* ✅ Display Date field */
text: if(
  a!isNotNullOrEmpty(fv!row['recordType!...dateField']),
  text(todate(fv!row['recordType!...dateField']), "MMM d, yyyy"),
  "N/A"
)

/* ✅ Date arithmetic */
if(
  a!isNotNullOrEmpty(fv!row['recordType!...dateField']),
  todate(fv!row['recordType!...dateField'] + 30),
  null
)

/* ✅ Date filter */
a!queryFilter(
  field: 'recordType!X.fields.dateField',
  operator: ">=",
  value: today() - 30,  /* Use today(), date arithmetic */
  applyWhen: a!isNotNullOrEmpty('recordType!X.fields.dateField')
)
```

### DateTime Fields (type: DateTime)
```sail
/* ✅ Display DateTime field */
text: if(
  a!isNotNullOrEmpty(fv!row['recordType!...dateTimeField']),
  text(fv!row['recordType!...dateTimeField'], "MMM d, yyyy h:mm a"),
  "N/A"
)

/* ✅ DateTime arithmetic */
if(
  a!isNotNullOrEmpty(fv!row['recordType!...dateTimeField']),
  a!addDateTime(
    startDateTime: fv!row['recordType!...dateTimeField'],
    days: 30
  ),
  null
)

/* ✅ DateTime filter */
a!queryFilter(
  field: 'recordType!X.fields.dateTimeField',
  operator: ">=",
  value: a!subtractDateTime(startDateTime: now(), days: 30),  /* Use now(), a!subtractDateTime() */
  applyWhen: a!isNotNullOrEmpty('recordType!X.fields.dateTimeField')
)
```

### Time Fields (type: Time)
```sail
/* ✅ Display Time field */
text: if(
  a!isNotNullOrEmpty(fv!row['recordType!...timeField']),
  text(fv!row['recordType!...timeField'], "h:mm a"),
  "N/A"
)

/* ✅ Time filter */
a!queryFilter(
  field: 'recordType!X.fields.timeField',
  operator: ">=",
  value: time(9, 0, 0),  /* 9:00 AM */
  applyWhen: a!isNotNullOrEmpty('recordType!X.fields.timeField')
)
```

**Key Functions:**
- **Date fields:** `today()`, `todate()`, `date()`, date arithmetic (`today() - 30`)
- **DateTime fields:** `now()`, `dateTime()`, `a!subtractDateTime()`, `a!addDateTime()`
- **Time fields:** `time()`, `a!subtractTime()`, `a!addTime()`

**Reference:** See `logic-guidelines/datetime-handling.md` for complete date/time type handling rules.

## Functions That Reject Null

**Some functions fail even with `a!defaultValue()` and require `if()` checks BEFORE calling:**

| Function Category | Functions | Why They Fail |
|-------------------|-----------|---------------|
| **User/Group** | `user(userId, property)`, `group(groupId, property)` | Cannot accept null ID |
| **Formatting** | `text(value, format)` | Cannot format null dates/numbers |
| **String manipulation** | `upper()`, `lower()`, `left()`, `right()`, `find()` | Fail on null input |
| **Logical** | `not()` | Cannot accept null value |

### user() Function - CRITICAL Pattern

**The user() function CANNOT accept null as the first parameter. Check for null BEFORE calling:**

```sail
/* ✅ CORRECT - Check for null BEFORE calling user() */
if(
  a!isNotNullOrEmpty(a!defaultValue(userIdField, null)),
  trim(
    user(userIdField, "firstName") & " " & user(userIdField, "lastName")
  ),
  "–"
)

/* ❌ WRONG - Checking null INSIDE user() call - user() will fail if passed null */
trim(
  user(a!defaultValue(userIdField, null), "firstName") & " " &
  user(a!defaultValue(userIdField, null), "lastName")
)
```

**Note on User Display Names:**
- Use `user(userId, "firstName") & " " & user(userId, "lastName")` instead of `displayName`
- The `displayName` field is actually a nickname and is not always populated
- Wrap in `trim()` to clean up any extra whitespace
- Use "–" (en dash) as fallback for null/empty users

### not() Function - CRITICAL Pattern

**The `not()` function cannot accept null. When using with variables or rule inputs that might be null:**

```sail
/* ❌ WRONG - Direct use of not() with potentially null value */
readOnly: not(ri!isEditable)  /* Fails if ri!isEditable is null */
disabled: not(local!allowEdits)  /* Fails if local!allowEdits is null */

/* ✅ CORRECT - Use a!defaultValue() to provide fallback */
readOnly: not(a!defaultValue(ri!isEditable, false()))  /* Returns true if null */
disabled: not(a!defaultValue(local!allowEdits, false()))  /* Returns true if null */

/* ✅ ALTERNATIVE - Use if() to check for null first */
readOnly: if(
  a!isNullOrEmpty(ri!isEditable),
  true(),  /* Default to read-only if null */
  not(ri!isEditable)
)
```

**Common scenarios requiring null protection:**
- `readOnly: not(ri!isEditable)` → Use `not(a!defaultValue(ri!isEditable, false()))`
- `disabled: not(local!allowEdits)` → Use `not(a!defaultValue(local!allowEdits, false()))`
- `showWhen: not(local!isHidden)` → Use `not(a!defaultValue(local!isHidden, false()))`

---

## Fallback Value Rules

| **Context** | **Fallback** | **Reason** |
|------------|-------------|-----------|
| Display (grid, richText, paragraph) | `"N/A"` | User-facing text |
| Editable fields (all types) | Use field directly (no wrapper) | Appian handles null automatically |
| Boolean logic (not, showWhen) | `false()` | Safe default for boolean context |

---

## Related Pattern Files

These patterns are documented in dedicated files:

| Pattern | File | Key Rule |
|---------|------|----------|
| **Choice Field Initialization** | `/logic-guidelines/choice-field-patterns.md` | Single checkbox = null-initialized, NOT false |
| **Grid Selection** | `/logic-guidelines/grid-selection-patterns.md` | Use `index(selection, 1, null)` - selectionValue is always a list |
| **Relationship Field Access** | `/conversion-guidelines/display-conversion-module.md` | Check `a!isNotNullOrEmpty()` before accessing relationship fields |

### Quick Examples

**Choice Field (Single Checkbox):**
```sail
/* ✅ Uninitialized = unchecked (null state) */
local!agreeToTerms,  /* NOT false() */

/* ❌ NEVER use null/empty in choiceValues */
choiceValues: {true()}  /* NOT: {true(), null} */
```

**Grid Selection:**
```sail
/* Grid selectionValue is ALWAYS a list, even for single-select */
local!selectedRow: index(local!selection, 1, null)  /* null if empty */

/* Check before using */
showWhen: if(a!isNotNullOrEmpty(local!selectedRow),
             local!selectedRow.id > 0,
             false())
```

**Relationship Field Access:**
```sail
/* Relationships can be null or empty arrays - check before accessing */
if(a!isNotNullOrEmpty(fv!row['recordType!Case.relationships.assignedUser']),
   fv!row['recordType!Case.relationships.assignedUser']['recordType!User.fields.firstName'],
   "Unassigned")
