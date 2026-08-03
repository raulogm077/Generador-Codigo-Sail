# Short-Circuit Evaluation Rules {#short-circuit-rules}

> **Related documentation:**
> - `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` (mock data interfaces)
> - `logic-guidelines/null-safety-quick-ref.md` (quick pattern lookup)

---

**SAIL's `and()` and `or()` functions DO NOT short-circuit** - they evaluate ALL arguments even if the result is already determined.

## The Problem

```sail
/* ❌ ERROR - and() evaluates BOTH arguments */
/* If local!computedData is empty, the second argument still evaluates */
/* This causes: "Invalid index: Cannot index property 'type' of Null" */
and(
  a!isNotNullOrEmpty(local!computedData),
  local!computedData.type = "Contract"  /* CRASHES if computedData is empty */
)
```

## The Solution: Nested if()

```sail
/* ✅ if() short-circuits - only evaluates the returned branch */
if(
  if(
    a!isNotNullOrEmpty(local!computedData),
    local!computedData.type = "Contract",  /* Only evaluated when not empty */
    false
  ),
  /* Then branch - show registration code field */,
  /* Else branch - hide field */
)
```

---

## When to Use Nested if() vs and()

### Use nested if() when:
- Checking null/empty before property access on computed variables
- Any scenario where the second condition CANNOT be safely evaluated if the first is false
- Accessing properties on variables that could be empty arrays or null

### Use and() when:
- All conditions are independent and can be safely evaluated in any order
- All variables involved are guaranteed to have values (not null, not empty)
- Simple boolean combinations without property access

---

## Quick Reference Table

| Function | Short-Circuits? | Use For |
|----------|----------------|---------|
| `if()` | ✅ Yes - Only evaluates returned branch | Null-safe property access, conditional logic, binary conditions |
| `and()` | ❌ No - Evaluates all arguments | Independent boolean conditions only (never for null safety) |
| `or()` | ❌ No - Evaluates all arguments | Independent boolean conditions only (never for null safety) |
| `a!match()` | ✅ Yes - Only evaluates matched branch | Pattern matching - single value against 3+ options (status, category, priority) |

---

## Common Scenarios Requiring Nested if()

### Scenario 1: Computed Variables from Grid Selections

```sail
/* Grid selection derives full data */
local!selectedItems: a!forEach(
  items: local!selectedIds,
  expression: index(...)
),

/* ❌ WRONG - Crashes when no items selected */
showWhen: and(
  length(local!selectedItems) > 0,
  local!selectedItems.type = "Contract"  /* ERROR if empty */
)

/* ✅ RIGHT - Nested if() prevents crash */
showWhen: if(
  if(
    a!isNotNullOrEmpty(local!selectedItems),
    length(intersection(local!selectedItems.type, {"Contract"})) > 0,
    false
  ),
  true,
  false
)
```

### Scenario 2: Array Property Access

```sail
/* ❌ WRONG - Crashes if items array is empty */
and(
  length(local!items) > 0,
  local!items.price > 100  /* ERROR if items is {} */
)

/* ✅ RIGHT */
if(
  if(
    a!isNotNullOrEmpty(local!items),
    length(where(local!items.price > 100)) > 0,
    false
  ),
  /* Then branch */,
  /* Else branch */
)
```

### Scenario 3: Filtered or Derived Arrays

```sail
local!activeUsers: a!forEach(
  items: local!allUsers,
  expression: if(fv!item.status = "Active", fv!item, null)
),

/* ✅ Checking properties with nested if() */
if(
  if(
    a!isNotNullOrEmpty(local!activeUsers),
    wherecontains("ADMIN", local!activeUsers.role),
    false
  ),
  /* Show admin panel */,
  {}
)
```

---

## The Pattern for Null-Safe Property Access

**Always use nested if() pattern when accessing properties on computed variables:**

```sail
if(
  if(
    a!isNotNullOrEmpty(local!variable),
    /* Safe to access properties here - variable is guaranteed not empty */
    local!variable.propertyName = "expectedValue",
    /* Return safe default - false, null, or {} depending on context */
    false
  ),
  /* Then branch */,
  /* Else branch */
)
```
