# DYNAMIC SAIL UI EXPRESSION GUIDELINES - MOCK DATA INTERFACES

This guide covers dynamic SAIL expressions using **local variables with hardcoded/mock data** - no record types required. For record type integration patterns, see `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`.

## 📑 Quick Navigation Index {#nav-index}

**How to use this index:**
1. Find the topic you need below
2. Read the linked file directly for detailed patterns
3. This file contains only essential rules and quick references

### 📁 Topic Files by Category

**Shared Foundations (used by both mockup and functional interfaces):**
- `/logic-guidelines/local-variable-patterns.md` - Data modeling, mockup vs functional differences
- `/logic-guidelines/short-circuit-evaluation.md` - Why if() vs and()/or() for null safety
- `/logic-guidelines/null-safety-quick-ref.md` - Quick pattern lookup table
- `/logic-guidelines/functions-reference.md` - Essential functions by category
- `/logic-guidelines/datetime-handling.md` - Date/time type matching & operators

**Mockup Patterns (mock data interfaces):**
- `/logic-guidelines/foreach-patterns.md` - fv! variables, Pattern A (array of maps) vs Pattern B (parallel arrays)
- `/logic-guidelines/grid-selection-patterns.md` - Two-variable approach, naming conventions
- `/logic-guidelines/choice-field-patterns.md` - Multi-checkbox, single checkbox initialization
- `/logic-guidelines/pattern-matching.md` - a!match() for status/category lookups
- `/logic-guidelines/chart-configuration.md` - Chart components, mock data patterns
- `/logic-guidelines/array-type-initialization-guidelines.md` - Type-casting empty arrays
- `/logic-guidelines/array-manipulation-patterns.md` - Dot notation, wherecontains(), deriving data from IDs

**Documentation & Environment:**
- `/logic-guidelines/documentation-patterns.md` - Requirement comments, three-tier structure
- `/logic-guidelines/environment-placeholders.md` - Handling non-existent constants/objects
- `/logic-guidelines/internationalization.md` - Why to avoid manual language toggles

### By Task Type

| Task | Read This File |
|------|----------------|
| Structuring local variables (maps vs separate) | `/logic-guidelines/local-variable-patterns.md` |
| Documenting requirements in code | `/logic-guidelines/documentation-patterns.md` |
| Handling unused variables | This file: "Unused Variables in Mockups" section |
| Handling non-existent constants | `/logic-guidelines/environment-placeholders.md` |
| Internationalization | `/logic-guidelines/internationalization.md` |
| Initializing empty arrays | `/logic-guidelines/array-type-initialization-guidelines.md` |
| Working with arrays/loops | `/logic-guidelines/foreach-patterns.md` |
| forEach generating input fields | `/logic-guidelines/foreach-patterns.md` (Parallel Array Pattern) |
| Dot notation and derived data | `/logic-guidelines/array-manipulation-patterns.md` |
| Using wherecontains() correctly | `/logic-guidelines/array-manipulation-patterns.md` |
| Pattern matching (status, categories) | `/logic-guidelines/pattern-matching.md` |
| Managing grid selections | `/logic-guidelines/grid-selection-patterns.md` |
| Building charts with mock data | `/logic-guidelines/chart-configuration.md` |
| Working with dates and times | `/logic-guidelines/datetime-handling.md` |
| Single checkbox initialization | `/logic-guidelines/choice-field-patterns.md` |
| Multiple checkbox selections | `/logic-guidelines/choice-field-patterns.md` |

### By Error Type

| Error | Read This File |
|-------|----------------|
| "Variable not defined" | This file: "Mandatory Foundation Rules" |
| "Rule input not defined (ri!)" | This file: "Rule Inputs in Mockups" |
| "Constant not found" | `/logic-guidelines/environment-placeholders.md` |
| "Type mismatch" with contains/wherecontains | `/logic-guidelines/array-type-initialization-guidelines.md` |
| "List of Variant" errors | `/logic-guidelines/array-type-initialization-guidelines.md` |
| "tostring() returned single string" | `/logic-guidelines/array-type-initialization-guidelines.md` |
| Null reference errors | `/logic-guidelines/null-safety-quick-ref.md` |
| Short-circuit evaluation errors | `/logic-guidelines/short-circuit-evaluation.md` |
| Syntax errors (and/or, if) | This file: "Language-Specific Syntax" |
| Grid selection not working | `/logic-guidelines/grid-selection-patterns.md` |
| "Cannot index property" | `/logic-guidelines/grid-selection-patterns.md` |
| DateTime vs Date mismatch | `/logic-guidelines/datetime-handling.md` |
| Checkbox initialization errors | `/logic-guidelines/choice-field-patterns.md` |

---

## 🚨 MANDATORY FOUNDATION RULES

1. **All SAIL expressions must begin with `a!localVariables()`** - even if no variables are defined
2. **ALL local variables must be declared before use** - No undeclared variables allowed
3. **Use only available Appian functions** - No JavaScript equivalents exist
4. **Appian data is immutable** - Use functional approaches:
   - `append(array, value)` - Add to end of array
   - `a!update(data: array, index: position, value: newValue)` - Insert/replace at position
   - `insert(array, value, index)` - Insert at specific position
   - `remove(array, index)` - Remove value at position
5. **Always validate for null values** - Use `a!isNullOrEmpty()` and `a!isNotNullOrEmpty()`
6. **wherecontains()**: See `/logic-guidelines/array-manipulation-patterns.md` for complete usage
7. **Single checkbox variables MUST be initialized to null, NOT false()** - See `/logic-guidelines/choice-field-patterns.md`
8. **MOCKUPS NEVER use rule inputs (ri!)** - See "Rule Inputs in Mockups" section below
9. **save!value ONLY valid inside a!save() value parameter** - Never in conditionals (if/and/or) or outside a!save() - See `/logic-guidelines/choice-field-patterns.md`
10. **Empty arrays MUST be type-initialized for primitive types**:
   - `tointeger({})` for ID arrays, counts, numeric selections
   - `touniformstring({})` for text arrays (NOT tostring()!)
   - `toboolean({})` for flag arrays
   - `todate({})`, `todatetime({})`, `todecimal({})`, `totime({})`, `touser({})`, `togroup({})`
   - See `/logic-guidelines/array-type-initialization-guidelines.md` for complete reference

---

## ❌ Rule Inputs in Mockups - Common Mistake

**MOCKUPS = local variables ONLY**

See `/logic-guidelines/local-variable-patterns.md` for:
- Complete rules on mockup vs functional variable usage
- When to use `local!` vs `ri!`
- Data modeling patterns (entity data, reference data, UI state)

---

## Essential SAIL Structure

See `/logic-guidelines/local-variable-patterns.md` for complete patterns including:
- Declaration syntax (with/without initial values)
- Initialization rules by scenario
- Scope rules for nested contexts

**Quick reference:**
- **With initial values**: `local!variable: value`
- **Without initial values**: `local!variable` (no null/empty placeholders)
- **For dropdowns**: Initialize to valid `choiceValue` OR use `placeholder`
- **For booleans**: Always explicit: `true()` or `false()`

---

## 📝 Unused Variables in Mockups

**Mockups should not have unused variables.** They should be lean and self-contained. If you have unused variables:
- **Remove them** (they add confusion), or
- **Use them** to demonstrate a pattern

For production interfaces with justified unused variables, see `/conversion-guidelines/validation-enforcement-module.md` for the UNUSED comment template.

---

## ⚠️ Language-Specific Syntax Patterns

**Appian SAIL Conditional Syntax:**
```sail
/* CORRECT - Use if() function */
value: if(condition, trueValue, falseValue)

/* WRONG - Python/JavaScript ternary operator */
value: condition ? trueValue : falseValue
```

**Never use patterns from other languages:**
- ❌ Python ternary: `condition ? value1 : value2`
- ❌ JavaScript arrow functions: `() => {}`
- ❌ Java/C# syntax: `public void`, `private static`
- ✅ Always use Appian SAIL function syntax: `functionName(parameters)`

---

## 🚨 Grid Column Sorting Rules

For mock data grids: Use field name strings (`sortField: "fieldName"`) matching your data structure.

For record data grids: See `/conversion-guidelines/display-conversion-module.md` for sorting rules.

---

## 🚨 a!forEach() Function Variables Reference

> **📖 Complete Guide:** `/logic-guidelines/foreach-patterns.md`

| Variable | Description | Use For |
|----------|-------------|---------|
| `fv!item` | Current item value | Accessing properties, scalar values |
| `fv!index` | Position (1-based) | Array manipulation, numbering, remove buttons |
| `fv!isFirst` | `true` on first iteration | Conditional headers, skip first divider |
| `fv!isLast` | `true` on last iteration | Conditional footers, "Add" buttons after last item |
| `fv!itemCount` | Total items in array | Progress indicators, conditional logic |

**⚠️ CRITICAL:** These variables are **ONLY** available inside `a!forEach()` expressions. They do NOT exist in grid columns or chart configurations.

---

## 🚨 Short-Circuit Evaluation Rules

> **📖 Complete Guide:** `/logic-guidelines/short-circuit-evaluation.md`

**Core Rule:** SAIL's `and()` and `or()` functions DO NOT short-circuit - they evaluate ALL arguments. Use nested `if()` for null-safe property access.

```sail
/* WRONG - and() evaluates both conditions even if first is false */
and(a!isNotNullOrEmpty(local!data), local!data.type = "Contract")  /* CRASHES if empty! */

/* CORRECT - if() short-circuits, only evaluates matched branch */
if(if(a!isNotNullOrEmpty(local!data), local!data.type = "Contract", false), ...)
```

---

## 🚨 Null Safety Implementation

> **📖 Quick Reference:** `/logic-guidelines/null-safety-quick-ref.md`

**CHECKPOINT: Before finalizing any SAIL expression, verify EVERY direct field reference uses a!defaultValue()**

- ✅ `a!defaultValue(local!variable, "")`
- ✅ `a!defaultValue(local!variable, null)`
- ✅ `a!defaultValue(local!array, {})`
- ❌ `local!variable` (naked variable reference without null safety)

**Special Case: not() with Variables:**
```sail
/* WRONG - not() cannot accept null */
readOnly: not(ri!isEditable)  /* Fails if null */

/* CORRECT - Use a!defaultValue() */
readOnly: not(a!defaultValue(ri!isEditable, false()))
```

---

## a!match() for Status-Based Lookups

> **📖 Complete Guide:** `/logic-guidelines/pattern-matching.md`

**When to use `a!match()` instead of nested if():**
- Single value compared against multiple options (3+ cases)
- Status, category, priority, type mappings

```sail
/* PREFER - a!match() (clean, maintainable) */
backgroundColor: a!match(
  value: statusCode,
  equals: "INTEGRATED", then: "POSITIVE",
  equals: "SUBMITTED", then: "ACCENT",
  equals: "DRAFT", then: "#F59E0B",
  default: "SECONDARY"
)

/* AVOID - Nested if() (hard to read) */
backgroundColor: if(statusCode = "INTEGRATED", "POSITIVE",
  if(statusCode = "SUBMITTED", "ACCENT", ...))
```

---

## ⚠️ Function Parameter Validation

**Array Functions - EXACT Parameter Counts:**
```sail
/* CORRECT */
wherecontains(value, array)           /* 2 params only */
contains(array, value)                /* 2 params only */
index(array, position)                /* 2 or 3 params */
index(array, position, default)

/* WRONG - Never add extra parameters */
wherecontains(value, array, 1)        /* Third param doesn't exist */
```

---

## Component Quick Rules

### Button Widget
**CRITICAL**: `a!buttonWidget` does NOT have a `validations` parameter. Use form-level validations.

### Dropdown Field
**CRITICAL**: Never initialize dropdown variables when using dynamic data:
```sail
/* WRONG */
local!selectedStatus: "All Statuses",  /* Value not in choiceValues */

/* CORRECT */
local!selectedStatus,  /* Starts as null, placeholder shows */
```

Use `placeholder: "All Statuses"` instead of `append("All", local!statuses)`.

### Rich Text Display Field
```sail
/* CORRECT - value takes array of rich text components */
a!richTextDisplayField(
  value: {
    a!richTextIcon(icon: "user", color: "SECONDARY"),
    a!richTextItem(text: "Display text", style: "STRONG")
  }
)
```

### Grid Selection Behavior
**selectionValue Contains Identifiers, NOT Full Objects**

See `/logic-guidelines/grid-selection-patterns.md` for the mandatory two-variable approach.

---

## Validation Checklist

### Grid Selection Pattern (Mock Data)
- [ ] Two-variable approach: ID array + computed variable
- [ ] ID variable name ends with "Ids", "Keys", or "Indexes"
- [ ] All property access uses computed variable, NOT ID array
- [ ] Computed variables have null checks with nested if()

### Null Safety & Short-Circuit
- [ ] All null checks implemented
- [ ] Computed variables protected with nested if() (NOT and())
- [ ] Property access on arrays uses nested if() when array could be empty

### Array & Property Access
- [ ] Dot notation used for property access (array.property)
- [ ] NO usage of property() function (doesn't exist)
- [ ] Single item lookup uses index() + wherecontains()
- [ ] Derived data follows a!forEach() + index() + wherecontains()

### Function Validation
- [ ] Function parameters match documented signatures
- [ ] All functions exist in Appian
- [ ] Short-circuit evaluation rules followed

### Component Patterns
- [ ] Checkbox booleans are null-initialized, NOT false-initialized
- [ ] Multi-checkbox uses single array variable
