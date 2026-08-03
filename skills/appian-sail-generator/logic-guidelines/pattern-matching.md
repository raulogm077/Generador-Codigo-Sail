# Pattern Matching with a!match() {#pattern-matching}

> **Parent guide:** `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `logic-guidelines/short-circuit-evaluation.md` (short-circuit rules)
> - `logic-guidelines/functions-reference.md` (function reference)

---

## Using a!match() for Status-Based Lookups {#amatch-status-lookups}

**When to use `a!match()` instead of parallel arrays:**
- Single value compared against multiple options (status, category, priority, etc.)
- Cleaner and more maintainable than nested `if()` statements
- Short-circuits like `if()` - safe for conditional logic

---

## Pattern: Status to Icon/Color Mapping

```sail
/* ❌ OLD PATTERN - Parallel arrays with wherecontains */
local!statuses: {"Open", "In Progress", "Completed", "Cancelled"},
local!icons: {"folder-open", "clock", "check-circle", "times-circle"},
local!colors: {"#3B82F6", "#F59E0B", "#10B981", "#EF4444"},

local!icon: index(
  local!icons,
  wherecontains(fv!item.status, local!statuses),
  "file"
)

/* ✅ NEW PATTERN - a!match() (cleaner, more readable) */
local!icon: a!match(
  value: fv!item.status,
  equals: "Open",
  then: "folder-open",
  equals: "In Progress",
  then: "clock",
  equals: "Completed",
  then: "check-circle",
  equals: "Cancelled",
  then: "times-circle",
  default: "file"
)
```

---

## Pattern: Dynamic Styling with a!match()

```sail
/* Stamp field with status-based colors */
a!stampField(
  icon: a!match(
    value: fv!item.priority,
    equals: "Critical",
    then: "exclamation-triangle",
    equals: "High",
    then: "arrow-up",
    equals: "Medium",
    then: "minus",
    equals: "Low",
    then: "arrow-down",
    default: "info-circle"
  ),
  backgroundColor: a!match(
    value: fv!item.priority,
    equals: "Critical",
    then: "#DC2626",
    equals: "High",
    then: "#F59E0B",
    equals: "Medium",
    then: "#3B82F6",
    equals: "Low",
    then: "#6B7280",
    default: "#9CA3AF"
  ),
  contentColor: "#FFFFFF",
  size: "TINY",
  shape: "ROUNDED",
  labelPosition: "COLLAPSED"
)
```

---

## Pattern: Grid Column Conditional Background Colors

```sail
a!gridField(
  data: local!tasks,
  columns: {
    a!gridColumn(
      label: "Status",
      value: fv!row.status,
      backgroundColor: a!match(
        value: fv!row.status,
        equals: "Completed",
        then: "#D1FAE5",
        equals: "In Progress",
        then: "#FEF3C7",
        equals: "Blocked",
        then: "#FEE2E2",
        default: "TRANSPARENT"
      )
    )
  }
)
```

---

## Pattern: Range-Based Comparisons with whenTrue {#whentrue-ranges}

**Use `whenTrue` instead of `equals` for:**
- Numeric ranges (scores, percentages, amounts)
- Date/time intervals (days elapsed, time since event)
- Any comparison operators (>, <, >=, <=)

### ❌ AVOID - Nested if() for Ranges

```sail
backgroundColor: if(
  fv!row.performance >= 110,
  "#059669",
  if(
    fv!row.performance >= 90,
    "#FCD34D",
    "#DC2626"
  )
)
```

### ✅ PREFER - a!match() with whenTrue

```sail
backgroundColor: a!match(
  value: fv!row.performance,
  whenTrue: fv!value >= 110, then: "#059669",
  whenTrue: fv!value >= 90, then: "#FCD34D",
  default: "#DC2626"
)
```

### Pattern: Date Elapsed Ranges

```sail
/* Display message based on days since case creation */
a!match(
  value: tointeger(today() - local!caseCreatedOn),
  whenTrue: fv!value <= 30, then: "Less than 30 days",
  whenTrue: fv!value <= 60, then: "30-60 days",
  whenTrue: fv!value <= 90, then: "60-90 days",
  default: "More than 90 days"
)
```

### Pattern: Percentage Thresholds (Heatmaps, KPIs)

```sail
/* Color-code performance percentage */
a!match(
  value: local!percentComplete,
  whenTrue: fv!value >= 100, then: "POSITIVE",
  whenTrue: fv!value >= 75, then: "ACCENT",
  whenTrue: fv!value >= 50, then: "#F59E0B",
  default: "NEGATIVE"
)
```

### Pattern: Currency/Amount Tiers

```sail
/* Assign tier based on order amount */
a!match(
  value: fv!row.orderTotal,
  whenTrue: fv!value >= 10000, then: "Platinum",
  whenTrue: fv!value >= 5000, then: "Gold",
  whenTrue: fv!value >= 1000, then: "Silver",
  default: "Bronze"
)
```

### Pattern: Mixed equals + whenTrue

You can combine `equals` (exact matches) and `whenTrue` (ranges) in the same expression:

```sail
a!match(
  value: local!itemCount,
  equals: 0, then: "Empty cart",
  equals: 1, then: "1 item in cart",
  whenTrue: fv!value > 1, then: fv!value & " items in cart",
  default: "Unknown"
)
```

### Key Rules for whenTrue

1. **`fv!value`** references the `value` parameter in `whenTrue`, `then`, and `default`
2. **Order matters** - conditions evaluate top-to-bottom, first match wins
3. **No upper bounds needed** when using descending order (>= 110, >= 90, default)
4. **Keywords required** - always use `equals:`, `whenTrue:`, `then:`, `default:`
5. **Can mix patterns** - combine `equals` and `whenTrue` in same expression

---

## When to Keep Parallel Arrays

- Need to iterate over all statuses/options (e.g., generate filter options)
- Building dropdown choices programmatically
- Multiple lookups from the same set of values
- Need the arrays themselves for other logic

---

## ✅ Best Practice: PREFER a!match() Over Nested if()

**When you have a single value to compare against 3+ options, ALWAYS use `a!match()` instead of nested `if()` statements.**

### Comparison: Nested if() vs a!match()

**❌ AVOID - Nested if() (Hard to Read, Error-Prone):**
```sail
backgroundColor: if(
  statusCode = "INTEGRATED",
  "POSITIVE",
  if(
    or(statusCode = "SUBMITTED", statusCode = "VALIDATED"),
    "ACCENT",
    if(
      statusCode = "DRAFT",
      "#F59E0B",
      "SECONDARY"
    )
  )
)
```

**Problems:**
- Deeply nested parentheses (easy to mismatch)
- Hard to scan visually
- Difficult to add/remove cases
- More error-prone during edits

**✅ PREFER - a!match() (Clean, Maintainable):**
```sail
backgroundColor: a!match(
  value: statusCode,
  equals: "INTEGRATED", then: "POSITIVE",
  equals: "SUBMITTED", then: "ACCENT",
  equals: "VALIDATED", then: "ACCENT",
  equals: "DRAFT", then: "#F59E0B",
  default: "SECONDARY"
)
```

**Benefits:**
- Flat structure - no nesting hell
- Clear value→result mapping
- Easy to add/remove cases
- Self-documenting code
- Less error-prone

---

## When to Use a!match()

### Use `equals` for:
- ✅ **Exact value matching**: status codes, categories, types
- ✅ **Enumerated values**: "Open", "Closed", "Pending"
- ✅ **String/ID comparisons**: Known discrete values

### Use `whenTrue` for:
- ✅ **Numeric ranges**: scores, percentages, amounts, counts
- ✅ **Date/time intervals**: days elapsed, time since event
- ✅ **Threshold logic**: >=, <=, between X and Y
- ✅ **Any comparison operators**: <, >, <=, >=, <>

### General rule:
- ✅ **3+ conditions on single value** → Use a!match() (either pattern)
- ✅ **Equality checks** → Use `equals`
- ✅ **Range/threshold checks** → Use `whenTrue`

---

## When Nested if() is Still Needed

- Multiple different variables in the condition
- Complex boolean expressions (not just equality checks)
- Computed logic that can't be reduced to pattern matching

**Example - Multiple Variables (Use if()):**
```sail
showWhen: if(
  and(local!userRole = "Manager", local!department = "Sales"),
  local!salesAmount > 10000,
  false
)
```
This checks TWO variables with AND logic - can't use `a!match()`.

---

## MANDATORY: Use a!match() for These Common Cases

### With `equals` (exact matching):
1. **Status-based colors/icons** (Open, Closed, Pending, etc.)
2. **Priority levels** (Low, Medium, High, Critical)
3. **Category mappings** (Type A→Icon 1, Type B→Icon 2, etc.)
4. **Approval states** (Draft, Submitted, Approved, Rejected)
5. **Any enumerated field with 3+ possible values**

### With `whenTrue` (ranges/thresholds):
6. **Numeric thresholds** (>=100 green, >=75 yellow, <75 red)
7. **Date ranges** (< 30 days, 30-60 days, > 60 days)
8. **Performance heatmaps** (exceeds, meets, below target)
9. **Amount tiers** (Platinum >=10k, Gold >=5k, Silver >=1k, Bronze)

---

## Short-Circuit Behavior

`a!match()` short-circuits like `if()` - it only evaluates the matched branch:

| Function | Short-Circuits? | Use For |
|----------|----------------|---------|
| `if()` | ✅ Yes - Only evaluates returned branch | Null-safe property access, conditional logic, binary conditions |
| `and()` | ❌ No - Evaluates all arguments | Independent boolean conditions only (never for null safety) |
| `or()` | ❌ No - Evaluates all arguments | Independent boolean conditions only (never for null safety) |
| `a!match()` | ✅ Yes - Only evaluates matched branch | Pattern matching - single value against 3+ options (status, category, priority) |

This makes `a!match()` safe for conditional logic where you need to avoid evaluating certain expressions.

---

## Best Practices Summary

### ✅ DO:
- **Use a!match()** for single value against 3+ options
- **Use for enumerated values** (status, category, priority, type)
- **Use for display logic** (colors, icons, labels)
- **Keep equals/then pairs on same line** for readability
- **Always provide a default** value

### ❌ DON'T:
- **Don't use nested if()** for simple pattern matching
- **Don't use for complex boolean logic** with multiple variables
- **Don't use for null-safe property access** (use nested if() instead)
- **Don't forget the default** value
