# Choice Field Patterns {#choice-field-patterns}

> **Parent guide:** `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `logic-guidelines/null-safety-quick-ref.md` (null checking)
> - `logic-guidelines/functions-reference.md` (function reference)

---

## ⚠️ CRITICAL: Multi-Checkbox Field Pattern

When a checkbox field has multiple choice values (multi-select), use a **single array variable** to store selections—do NOT use separate boolean variables for each choice.

### ✅ CORRECT - Single Array Variable

```sail
a!localVariables(
  local!selectedPriorities: {},  /* Single array for all selections */
  {
    a!checkboxField(
      label: "Case Priorities",
      choiceLabels: {"High", "Medium", "Low", "Critical"},
      choiceValues: {"HIGH", "MEDIUM", "LOW", "CRITICAL"},
      value: local!selectedPriorities,     /* Direct reference */
      saveInto: local!selectedPriorities,  /* Direct save */
      choiceLayout: "STACKED"
    ),
    /* Check if any selections exist */
    if(
      a!isNotNullOrEmpty(local!selectedPriorities),
      a!textField(
        label: "Filter Reason",
        value: local!filterReason,
        saveInto: local!filterReason
      ),
      {}
    ),
    /* Check if specific value is selected */
    if(
      contains(local!selectedPriorities, "CRITICAL"),
      a!textField(
        label: "Escalation Contact",
        value: local!escalationContact,
        saveInto: local!escalationContact,
        required: true
      ),
      {}
    )
  }
)
```

### ❌ WRONG - Separate Boolean Variables

```sail
a!localVariables(
  /* DON'T create separate variables for each choice */
  local!highPriority,
  local!mediumPriority,
  local!lowPriority,
  local!criticalPriority,
  {
    a!checkboxField(
      label: "Case Priorities",
      choiceLabels: {"High", "Medium", "Low", "Critical"},
      choiceValues: {"HIGH", "MEDIUM", "LOW", "CRITICAL"},
      /* DON'T reconstruct array from multiple booleans */
      value: a!flatten({
        if(a!defaultValue(local!highPriority, false), "HIGH", null),
        if(a!defaultValue(local!mediumPriority, false), "MEDIUM", null),
        if(a!defaultValue(local!lowPriority, false), "LOW", null),
        if(a!defaultValue(local!criticalPriority, false), "CRITICAL", null)
      }),
      /* DON'T reverse-map array back to separate booleans */
      saveInto: {
        a!save(local!highPriority, if(contains(save!value, "HIGH"), true, null)),
        a!save(local!mediumPriority, if(contains(save!value, "MEDIUM"), true, null)),
        a!save(local!lowPriority, if(contains(save!value, "LOW"), true, null)),
        a!save(local!criticalPriority, if(contains(save!value, "CRITICAL"), true, null))
      }
    )
  }
)
```

### Why the Wrong Pattern Fails

- **Complex and verbose**: Requires mapping logic in both `value` and `saveInto`
- **Maintenance nightmare**: Adding/removing choices requires changes in 4+ places
- **Error-prone**: Easy to miss updating one of the mappings
- **Inefficient**: Unnecessary data transformation on every interaction

### Key Rules

- ✅ Multi-select checkboxes → Single array variable
- ✅ Check selections using `contains(arrayVariable, value)`
- ✅ Check if any selected using `a!isNotNullOrEmpty(arrayVariable)`
- ✅ Get selection count using `length(arrayVariable)`
- ❌ NEVER create separate boolean variables for each checkbox choice
- ❌ NEVER use `a!flatten()` to reconstruct arrays from booleans

---

## Single Checkbox Field Pattern

### Pattern 1: Boolean Variable (Simple Toggle)

When binding a single checkbox directly to a boolean variable with no dependent logic:

```sail
/* ✅ CORRECT - Direct assignment for boolean variables */
local!enableFeature,  /* null by default */
a!checkboxField(
  label: "Options",
  choiceLabels: {"Enable Feature"},
  choiceValues: {true},
  value: local!enableFeature,
  saveInto: local!enableFeature,
  choiceLayout: "STACKED"
)
```

### Pattern 2: Local Variable with Dependent Field Clearing

When using a single checkbox with local variables that start as null or need to clear dependent fields:

**Critical: Variable Initialization for Pattern 2**

When using Pattern 2 (local variables with checkboxes), nullable boolean variables MUST be initialized to `null`, NOT `false`:

```sail
/* ✅ CORRECT - Null-initialized */
a!localVariables(
  local!caseUrgent,      /* null by default */
  local!requiresReview,  /* null by default */
  local!publicRecord,    /* null by default */
  ...
)

/* ❌ WRONG - False-initialized */
a!localVariables(
  local!caseUrgent: false,      /* ERROR: false is not a valid choiceValue! */
  local!requiresReview: false,
  local!publicRecord: false,
  ...
)
```

**Why?** Single checkboxes with `choiceValues: {true}` can only represent two states:
- **Checked**: `{true}` (stored as the value `true`)
- **Unchecked**: `{}` or `null` (NOT `false`)

Since `choiceValues` can only contain `{true}`, the variable must be `null` when unchecked. Initializing to `false` creates a mismatch between the variable state and the checkbox's valid values.

**Complete Pattern 2 Example:**

```sail
/* ✅ CORRECT - Null-aware toggle pattern with dependent field clearing */
a!localVariables(
  /* Initialize checkbox variable to null, NOT false */
  local!caseUrgent,        /* null by default */
  local!assignedTo,
  local!escalationReason,
  local!previousCheckState: local!caseUrgent,  /* Track previous state for clearing logic */

  {
    a!checkboxField(
      label: "Case Priority",
      choiceLabels: {"This is an urgent case requiring immediate attention"},
      choiceValues: {true},
      value: if(a!defaultValue(local!caseUrgent, false), {true}, {}),
      saveInto: {
        /* Save the new checkbox state */
        a!save(local!caseUrgent, if(a!isNotNullOrEmpty(save!value), true, null)),
        /* Set assignedTo when checked, preserve when unchecked */
        a!save(local!assignedTo, if(a!isNotNullOrEmpty(save!value), "urgent-team@example.com", local!assignedTo)),
        /* Clear escalationReason only when transitioning from checked to unchecked */
        a!save(
          local!escalationReason,
          if(
            and(
              a!isNotNullOrEmpty(local!previousCheckState),  /* Was previously checked */
              a!isNullOrEmpty(save!value)                     /* Now unchecked */
            ),
            null,                      /* Clear the field */
            local!escalationReason     /* Otherwise preserve current value */
          )
        ),
        /* Update the state tracker for next interaction */
        a!save(local!previousCheckState, if(a!isNotNullOrEmpty(save!value), true, null))
      }
    ),
    /* Dependent fields check null state */
    a!textField(
      label: "Escalation Reason",
      value: local!escalationReason,
      saveInto: local!escalationReason,
      required: a!isNotNullOrEmpty(local!caseUrgent),
      showWhen: a!isNotNullOrEmpty(local!caseUrgent)
    )
  }
)
```

**Pattern Explanation:**
- **local!previousCheckState**: Tracks the checkbox state from before the current interaction
- **First a!save**: Updates the checkbox variable itself
- **Second a!save**: Sets a value when checking, preserves when unchecking
- **Third a!save**: Clears the dependent field ONLY when transitioning from checked→unchecked (not when already unchecked)
- **Fourth a!save**: Updates the state tracker for the next interaction

**Why This Pattern Works:**
- `save!value` is ONLY used inside `a!save()` value parameters (complies with SAIL rules)
- Uses `local!previousCheckState` to detect state transitions without referencing `save!value` in conditionals
- Prevents unnecessary clearing when checkbox is already unchecked

### Key Differences

- **Pattern 1**: Use when binding to a boolean variable with no side effects
- **Pattern 2**: Use when the checkbox state affects other fields, requires clearing dependent fields on uncheck, or needs complex side effects

---

## Common Mistakes

```sail
/* ❌ WRONG - Using conditional value binding unnecessarily */
value: if(local!caseUrgent, {true}, {})

/* ✅ RIGHT - Direct assignment */
value: local!caseUrgent

/* ❌ WRONG - Using save!value in conditional */
saveInto: {
  a!save(local!var, or(save!value = {true})),
  if(or(save!value = {true}), ...) /* ERROR: save!value not allowed here */
}

/* ✅ RIGHT - Check local variable state, not save!value */
saveInto: {
  if(a!isNullOrEmpty(local!var), ...)
}

/* ❌ WRONG - Using length() on save!value */
saveInto: {
  a!save(local!var, if(length(save!value) > 0, true, null))  /* ERROR: fails when null */
}

/* ✅ RIGHT - Use a!isNotNullOrEmpty() */
saveInto: {
  a!save(local!var, if(a!isNotNullOrEmpty(save!value), true, null))
}
```

**Critical Rule:** `save!value` can ONLY be used inside the `value` parameter of `a!save(target, value)`. It cannot be used in conditionals, the target parameter, or anywhere outside `a!save()`.

---

## Selection Component Patterns

```sail
/* ✅ Single array variable with checkbox controls */
a!localVariables(
  local!visibleColumns: {"id", "title", "status"},
  {
    a!checkboxField(
      choiceValues: {"id", "title", "status"},
      value: local!visibleColumns,
      saveInto: local!visibleColumns
    ),
    a!gridColumn(
      showWhen: contains(local!visibleColumns, "id")
    )
  }
)
```

---

## Initialization Patterns Quick Reference

### Pre-Checked Checkbox
```sail
/* Use when checkbox should be checked by default (opt-out scenarios) */
local!agreeToTerms: true(),  /* Pre-checked */

a!checkboxField(
  label: "Terms and Conditions",
  choiceLabels: {"I agree to the terms and conditions"},
  choiceValues: {true},
  value: local!agreeToTerms,
  saveInto: local!agreeToTerms
)
```

### Pre-Selected Multi-Checkbox
```sail
/* Use when some options should be selected by default (default filters, saved preferences) */
local!selectedPriorities: {"HIGH", "MEDIUM"},  /* Pre-select specific options */

a!checkboxField(
  label: "Case Priorities",
  choiceLabels: {"High", "Medium", "Low", "Critical"},
  choiceValues: {"HIGH", "MEDIUM", "LOW", "CRITICAL"},
  value: local!selectedPriorities,
  saveInto: local!selectedPriorities
)
```

---

## Radio Button Patterns

Radio buttons allow selecting **one value** from multiple options (unlike checkboxes which allow multiple selections or toggle behavior).

### Unselected Radio Button
```sail
local!priority,  /* null = no selection */

a!radioButtonField(
  label: "Priority Level",
  choiceLabels: {"High", "Medium", "Low"},
  choiceValues: {"HIGH", "MEDIUM", "LOW"},
  value: local!priority,
  saveInto: local!priority
)
```

### Pre-Selected Radio Button
```sail
local!priority: "MEDIUM",  /* Pre-select Medium */

a!radioButtonField(
  label: "Priority Level",
  choiceLabels: {"High", "Medium", "Low"},
  choiceValues: {"HIGH", "MEDIUM", "LOW"},
  value: local!priority,
  saveInto: local!priority
)
```

**Key Differences from Checkboxes:**
- Radio buttons store a **single value** (not an array)
- Checkboxes with multiple choiceValues store an **array of values**
- Single checkbox with `choiceValues: {true}` stores a **boolean value**

---

## Single Checkbox showWhen Pattern

**Single-value checkbox** (`choiceValues: {true()}`):

```sail
/* ❌ WRONG - contains() crashes on null */
showWhen: contains(local!hasConflict, true())

/* ✅ CORRECT - Safe for null */
showWhen: a!isNotNullOrEmpty(local!hasConflict)
```

**Multi-value checkbox** (`choiceValues: {"a", "b", "c"}`):
```sail
/* ✅ CORRECT - Use contains() */
showWhen: contains(local!preferences, "email")
```

---

## Best Practices Summary

### ✅ DO:
- **Use single array variable** for multi-select checkboxes
- **Initialize boolean checkbox variables to null** (not false)
- **Use `a!isNotNullOrEmpty()`** to check if checkbox is checked
- **Use `contains()`** to check for specific values in multi-select
- **Use `a!isNotNullOrEmpty(save!value)`** in saveInto logic

### ❌ DON'T:
- **Don't create separate variables** for each checkbox option
- **Don't initialize to false** when using `choiceValues: {true}`
- **Don't use length()** on potentially null save!value
- **Don't use save!value** outside of a!save() value parameter
- **Don't use a!flatten()** to reconstruct checkbox arrays from booleans
