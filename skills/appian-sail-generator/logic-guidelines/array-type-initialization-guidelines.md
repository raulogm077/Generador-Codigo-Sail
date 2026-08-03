# SAIL Array Type Initialization Guidelines

> **Parent guide:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `/logic-guidelines/array-manipulation-patterns.md` - Dot notation, wherecontains()
> - `/logic-guidelines/foreach-patterns.md` - Working with arrays in loops

## 🚨 CRITICAL: Empty Array Type Declaration

**Problem:** In Appian, `{}` returns a **List of Variant** (untyped array), which causes type mismatch errors when used with typed operations.

**Impact:** Functions like `contains()`, `wherecontains()`, `union()`, `intersection()`, and `append()` require typed arrays. Appending different types to an untyped array creates a List of Variant.

**Example:**
```sail
local!test: {},
append(append(local!test, "text"), 1)  /* Returns: List of Variant (mixed types!) */
```

---

## Mandatory Type Initialization Pattern

### ✅ ALWAYS Initialize Arrays with Type Declaration

```sail
/* ❌ WRONG - Untyped arrays cause errors */
local!selectedIds: {},
local!names: {},
local!dates: {},
local!flags: {},

/* ✅ CORRECT - Type-initialized arrays */
local!selectedIds: tointeger({}),        /* List of Integer */
local!names: touniformstring({}),        /* List of Text */
local!dates: todate({}),                 /* List of Date */
local!flags: toboolean({}),              /* List of Boolean */
```

---

## Complete Type Initialization Reference

### All 9 Type Initialization Functions

| Function | Returns | Use Case |
|----------|---------|----------|
| `tointeger({})` | Empty List of Integer | IDs, counts, numeric values |
| `touniformstring({})` | Empty List of Text | Names, labels, text values |
| `toboolean({})` | Empty List of Boolean | Flags, checkboxes, yes/no |
| `todate({})` | Empty List of Date | Date values (no time) |
| `todatetime({})` | Empty List of DateTime | Timestamps, date+time |
| `todecimal({})` | Empty List of Decimal | Currency, percentages, precise numbers |
| `totime({})` | Empty List of Time | Time values (no date) |
| `touser({})` | Empty List of User | User references |
| `togroup({})` | Empty List of Group | Group references |

---

## 🚨 CRITICAL: tostring() vs touniformstring()

**DO NOT use `tostring({})` for array initialization!**

### The Critical Difference

```sail
/* ❌ WRONG - tostring() merges array to single text string */
tostring({1, 2})        /* Returns: "1; 2" (one string, NOT an array!) */
tostring({})            /* Returns: "" (empty string, NOT empty array!) */

/* ✅ CORRECT - touniformstring() preserves array structure */
touniformstring({1, 2}) /* Returns: {"1", "2"} (array of strings) */
touniformstring({})     /* Returns: Empty List of Text */
```

### When to Use Each

- **`tostring()`** - Converts array TO a single merged string
  - Use when you want to concatenate array values into one string
  - Example: Display multiple values as comma-separated text

- **`touniformstring()`** - Converts array elements TO strings (preserves array)
  - Use for initializing text arrays
  - Use when you need an array of text values

---

## Common Error Scenarios & Solutions

### Error 1: contains() with Untyped Array

**❌ WRONG:**
```sail
local!selectedCourseIds: {},

/* Later in code... */
contains(local!selectedCourseIds, fv!item.id)  /* ERROR: Variant vs Integer */
```

**✅ CORRECT:**
```sail
local!selectedCourseIds: tointeger({}),

/* Later in code... */
contains(local!selectedCourseIds, fv!item.id)  /* ✓ Both Integer type */
```

---

### Error 2: wherecontains() with Untyped Array

**❌ WRONG:**
```sail
local!filterValues: {},

wherecontains(local!filterValues, local!dataArray)  /* ERROR: Type mismatch */
```

**✅ CORRECT:**
```sail
local!filterValues: touniformstring({}),

wherecontains(local!filterValues, local!dataArray)  /* ✓ Typed array */
```

---

### Error 3: Mixed-Type Append Creates List of Variant

**❌ WRONG:**
```sail
local!items: {},

/* Appending different types creates List of Variant */
a!save(local!items, append(local!items, "text"))
a!save(local!items, append(local!items, 123))  /* Now List of Variant! */
```

**✅ CORRECT:**
```sail
/* Option 1: Use consistent types with type initialization */
local!items: touniformstring({}),
a!save(local!items, append(local!items, "text"))
a!save(local!items, append(local!items, tostring(123)))  /* Convert to text */

/* Option 2: Use separate typed arrays */
local!textItems: touniformstring({}),
local!numericItems: tointeger({}),
```

---

### Error 4: Parallel Arrays with Different Types

**❌ WRONG:**
```sail
/* Untyped parallel arrays */
local!prerequisiteCompletionDates: {},
local!prerequisiteIssuingCenters: {},
local!prerequisiteDocuments: {},
```

**✅ CORRECT:**
```sail
/* Type-initialized parallel arrays */
local!prerequisiteCompletionDates: todate({}),           /* List of Date */
local!prerequisiteIssuingCenters: touniformstring({}),   /* List of Text */
local!prerequisiteDocuments: tointeger({}),              /* List of Integer (document IDs) */
```

---

## When Type Initialization is NOT Needed

### Arrays Initialized with Data

```sail
/* ✅ Type inferred from source data */
local!courseIds: local!availableCourses.id,        /* Already List of Integer */
local!courseNames: local!availableCourses.name,    /* Already List of Text */

/* ✅ Type inferred from literal array */
local!statuses: {"Open", "In Progress", "Closed"}, /* Already List of Text */
local!counts: {0, 5, 10, 15},                      /* Already List of Integer */
```

### Arrays That Will Be Fully Replaced

```sail
/* ✅ Acceptable if never used before replacement */
local!tempData: {},

/* Immediately replaced with typed data */
local!tempData: a!queryRecordType(...)['recordType!Case.fields.id']
```

---

## Complex Types: Maps and CDTs

### Arrays of Maps (Dictionary Type)

```sail
/* ❌ WRONG - Cannot type-cast a!map() arrays */
local!employers: tointeger({}),  /* Error: a!map is not Integer */

/* ✅ CORRECT - Initialize with empty map structure */
local!employers: {
  a!map(
    employerName: null,
    jobTitle: null,
    startDate: null,
    endDate: null
  )
}

/* ✅ ALTERNATIVE - If truly empty, use {} but document type */
/* Array of Map (employer records) - will be populated dynamically */
local!employers: {},
```

**Why:** `a!map()` creates a **Dictionary** type, which doesn't have a direct type-casting function. Initialize with a sample structure instead.

### Arrays of CDTs (Custom Data Types)

```sail
/* ✅ Type inferred from CDT constructor */
local!submissions: {},  /* Will hold CDT instances */

/* Type established on first assignment */
local!submissions: append(
  local!submissions,
  type!SubmissionCDT(title: "First", status: "Draft")
)

/* ✅ BETTER - Initialize with CDT type if known */
local!submissions: cast(type!SubmissionCDT, {})
```

---

## Type Selection Decision Tree

```
What type of data will the array store?

1. Numeric whole numbers (IDs, counts, quantities)?
   → Use tointeger({})

2. Text strings (names, labels, descriptions)?
   → Use touniformstring({})  ⚠️ NOT tostring()!

3. Boolean values (flags, checkboxes, yes/no)?
   → Use toboolean({})

4. Dates (no time component)?
   → Use todate({})

5. Dates with time (timestamps)?
   → Use todatetime({})

6. Decimal numbers (currency, percentages, measurements)?
   → Use todecimal({})

7. Time only (no date component)?
   → Use totime({})

8. User references?
   → Use touser({})

9. Group references?
   → Use togroup({})

10. Complex types (maps, CDTs)?
    → Initialize with sample structure or document type
    → NO type conversion functions available for these
```

---

## Common Use Case Patterns

### Multi-Select Grid Pattern (IDs)
```sail
/* Grid selection with typed array */
local!selectedRecordIds: tointeger({}),

a!gridField(
  data: local!records,
  selectionValue: local!selectedRecordIds,
  selectionSaveInto: local!selectedRecordIds
)
```

### Dynamic Form Fields (Parallel Arrays)
```sail
/* Parallel arrays for forEach-generated inputs */
local!fieldValues: touniformstring({}),
local!fieldDates: todate({}),
local!fieldFlags: toboolean({}),

a!forEach(
  items: local!fieldDefinitions,
  expression: a!textField(
    value: index(local!fieldValues, fv!index, null),
    saveInto: a!save(
      local!fieldValues,
      a!update(data: local!fieldValues, index: fv!index, value: save!value)
    )
  )
)
```

### Filter/Search Pattern
```sail
/* Filter values with typed array */
local!filterStatusValues: touniformstring({}),

wherecontains(local!filterStatusValues, local!allCases.status)
```

### User/Group Assignment
```sail
/* User selection with typed array */
local!assignedUsers: touser({}),

a!pickerFieldUsers(
  label: "Assign To",
  value: local!assignedUsers,
  saveInto: local!assignedUsers,
  maxSelections: 5
)
```

### Date Range Selection
```sail
/* Date range filter with typed array */
local!selectedDates: todate({}),

/* Filter data by date range */
if(
  a!isNotNullOrEmpty(local!selectedDates),
  wherecontains(local!selectedDates, local!data.dueDate),
  1..length(local!data)  /* All indices if no filter */
)
```

---

## Function Behavior Reference

### Complete Behavior Examples

```sail
/* Integer arrays */
tointeger({})           /* → Empty List of Integer */
tointeger({1, 2})       /* → {1, 2} List of Integer */

/* Text arrays - CRITICAL DISTINCTION */
tostring({1, 2})        /* → "1; 2" (SINGLE string - NOT an array!) */
touniformstring({1, 2}) /* → {"1", "2"} (array of strings) ✅ Use this */
touniformstring({})     /* → Empty List of Text */

/* Boolean arrays */
toboolean({})           /* → Empty List of Boolean */
toboolean({1, 0})       /* → {true, false} List of Boolean */
toboolean({"T", "F"})   /* → {true, false} (any text starting with T/t) */

/* Date/Time arrays */
todate({})              /* → Empty List of Date */
todate({"01/15/2025"})  /* → {Date(2025-01-15)} (MM/DD/YYYY format) */
todatetime({})          /* → Empty List of DateTime */
totime({})              /* → Empty List of Time */

/* Numeric arrays */
todecimal({})           /* → Empty List of Decimal */
todecimal({1, 2})       /* → {1.0, 2.0} List of Decimal */

/* User/Group arrays */
touser({})              /* → Empty List of User */
touser({"john.doe"})    /* → {User(john.doe)} */
togroup({})             /* → Empty List of Group */
```

---

## Validation Checklist

**Before generating SAIL code, verify:**

- [ ] All arrays storing IDs are initialized with `tointeger({})`
- [ ] All arrays storing names/labels are initialized with `touniformstring({})` (NOT `tostring()`)
- [ ] All arrays storing dates are initialized with `todate({})`
- [ ] All arrays storing timestamps are initialized with `todatetime({})`
- [ ] All arrays storing flags/checkboxes are initialized with `toboolean({})`
- [ ] All arrays storing decimal numbers are initialized with `todecimal({})`
- [ ] All arrays storing user references are initialized with `touser({})`
- [ ] All arrays storing group references are initialized with `togroup({})`
- [ ] Arrays of maps are initialized with sample structure or documented
- [ ] No `contains()` or `wherecontains()` calls on untyped `{}`
- [ ] No mixed-type appends that create List of Variant

---

## Quick Reference Table

| Data Type | Initialization | Example Variable |
|-----------|---------------|------------------|
| Integer IDs | `tointeger({})` | `local!selectedCourseIds: tointeger({})` |
| Text values | `touniformstring({})` | `local!registrationCodes: touniformstring({})` |
| Boolean flags | `toboolean({})` | `local!selectedFlags: toboolean({})` |
| Dates | `todate({})` | `local!dueDates: todate({})` |
| Timestamps | `todatetime({})` | `local!eventTimestamps: todatetime({})` |
| Decimals | `todecimal({})` | `local!prices: todecimal({})` |
| Times | `totime({})` | `local!scheduledTimes: totime({})` |
| Users | `touser({})` | `local!assignedUsers: touser({})` |
| Groups | `togroup({})` | `local!teams: togroup({})` |

---

## Summary

**🚨 MANDATORY RULE:**
> **ALWAYS initialize empty arrays with type-casting functions when storing primitive types (Integer, Text, Boolean, Date, DateTime, Decimal, Time, User, Group).**

**Why this matters:**
- Prevents runtime type mismatch errors
- Avoids List of Variant from mixed-type operations
- Makes code behavior predictable
- Improves code readability (type is self-documenting)
- Eliminates debugging time on cryptic type errors

**Default pattern:**
```sail
local!arrayName: to<Type>({}),  /* Type-initialized empty array */
```

**Critical distinction:**
- Use `touniformstring({})` for text arrays, NOT `tostring({})`
- `tostring()` merges arrays to a single string
- `touniformstring()` preserves array structure
