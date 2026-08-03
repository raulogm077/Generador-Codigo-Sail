# Local Variable Patterns and Data Modeling

> **Parent guide:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `/logic-guidelines/foreach-patterns.md` - Pattern A vs B for forEach
> - `/logic-guidelines/array-type-initialization-guidelines.md` - Type-casting empty arrays
> - `/logic-guidelines/choice-field-patterns.md` - Checkbox initialization rules

---

## 🎯 Data Modeling Philosophy (READ FIRST)

**Use maps to group related data.** This minimizes local variables, keeps data structured, and enables clean conversion from mockup to functional interface.

### Why This Matters

Mockup structure should mirror functional interface structure:

```
MOCKUP (local variables)              FUNCTIONAL (rule inputs + queries)
────────────────────────────────────────────────────────────────────────
local!case: a!map(                    ri!case: 'recordType!Case'(
  title: "Sample Case",        →        ['recordType!Case.fields.title'],
  status: "Open",                       ['recordType!Case.fields.status'],
  priority: "High",                     ['recordType!Case.fields.priority'],
  notes: {                              ['recordType!Case.relationships.notes']
    a!map(                                (managed via a!relatedRecordData)
      description: "First note",
      createdBy: "john.doe",
      createdOn: today()
    )
  }
)

local!statusOptions: {                local!statusOptions: a!queryRecordType(
  a!map(id: 1, label: "Open"),   →      recordType: 'recordType!Status',
  a!map(id: 2, label: "Closed")         fields: {...}
}                                     ).data
```

**Benefits:**
- Mockup → Functional conversion is straightforward (replace map with record type)
- Fewer local variables to manage
- Data relationships are explicit
- Mirrors what queries return (array of records/maps)

---

## Local Variable Categories

### 1. Entity Data (Single Record)

**Use for:** Form data being created or edited

```sail
/* Single record being edited */
local!employee: a!map(
  firstName: null,
  lastName: null,
  email: null,
  department: null,
  startDate: null
),
```

**Converts to:** `ri!employee` (rule input bound to record type)

---

### 2. Entity Data (List of Records)

**Use for:** Grid data, multi-instance forms, related records

```sail
/* Grid/list data */
local!cases: {
  a!map(id: 1, title: "Case A", status: "Open", assignee: "john.doe"),
  a!map(id: 2, title: "Case B", status: "Closed", assignee: "jane.doe"),
  a!map(id: 3, title: "Case C", status: "Open", assignee: "john.doe")
},

/* Multi-instance form (user can add/remove) */
local!workExperiences: {
  a!map(company: null, role: null, startDate: null, endDate: null)
},
```

**Converts to:**
- Grid data → `a!queryRecordType(...).data` or `a!recordData()`
- Multi-instance form → `ri!relatedRecords` or nested relationship

---

### 3. Reference/Lookup Data

**Use for:** Dropdown options, status lists, priority levels

```sail
/* Reference data for dropdowns */
local!statusOptions: {
  a!map(id: 1, label: "Open"),
  a!map(id: 2, label: "In Progress"),
  a!map(id: 3, label: "Closed")
},

local!priorityOptions: {
  a!map(id: "HIGH", label: "High", color: "#EF4444"),
  a!map(id: "MEDIUM", label: "Medium", color: "#F59E0B"),
  a!map(id: "LOW", label: "Low", color: "#10B981")
},
```

**Converts to:** Query to reference record type (e.g., `'recordType!Status'`)

**Usage in components:**
```sail
a!dropdownField(
  label: "Status",
  choiceLabels: local!statusOptions.label,
  choiceValues: local!statusOptions.id,
  value: local!case.status,
  saveInto: local!case.status
)
```

---

### 4. Nested Relationships (One-to-Many)

**Use for:** Parent record with child records (e.g., Case with Notes)

```sail
local!case: a!map(
  id: 1,
  title: "Customer Complaint",
  status: "Open",
  /* Nested one-to-many relationship */
  notes: {
    a!map(
      id: 101,
      description: "Initial contact with customer",
      createdBy: "john.doe",
      createdOn: todate("01/15/2025")
    ),
    a!map(
      id: 102,
      description: "Follow-up scheduled",
      createdBy: "jane.doe",
      createdOn: todate("01/16/2025")
    )
  }
),
```

**Converts to:** Record type with relationship, managed via `a!relatedRecordData()`

---

### 5. UI State (Separate Variables)

**Use for:** Transient state that doesn't map to record fields

```sail
/* UI state - keep as separate variables */
local!isEditMode: false(),
local!activeTab: 1,
local!selectedRowId,
local!showConfirmDialog: false(),
local!searchText: "",
local!currentPage: 1,
```

**Stays as:** `local!` variables (not converted to ri!)

---

## Quick Reference Table

| Category | Structure | Example | Converts To |
|----------|-----------|---------|-------------|
| **Entity (single)** | `a!map(...)` | `local!employee: a!map(firstName: null, ...)` | `ri!employee` |
| **Entity (list)** | `{a!map(...)}` | `local!cases: {a!map(id: 1, ...), ...}` | Query `.data` or `ri!records` |
| **Reference data** | `{a!map(id:, label:)}` | `local!statuses: {a!map(id: 1, label: "Open")}` | Query to reference table |
| **Nested relationship** | `a!map(..., children: {a!map(...)})` | `local!case: a!map(..., notes: {a!map(...)})` | Record with relationship |
| **UI state** | Separate variables | `local!isEditMode`, `local!activeTab` | Stays as `local!` |

---

## Initialization Rules

### When to Initialize

| Scenario | Initialization | Example |
|----------|---------------|---------|
| Form field (empty start) | Properties set to `null` | `a!map(firstName: null, lastName: null)` |
| Form field (pre-populated) | Properties set to values | `a!map(status: "Open")` |
| Multi-instance (start with one) | Array with one empty map | `{a!map(field1: null, field2: null)}` |
| Display data | Properties set to sample values | `{a!map(id: 1, name: "Sample")}` |
| Checkbox (unchecked default) | Leave uninitialized | `local!agreeToTerms,` |
| Boolean (explicit state) | Set to `true()` or `false()` | `local!isEditMode: false()` |

### Empty Array Type Initialization

When using **empty arrays for primitive types** (not maps), always type-initialize:

```sail
/* ❌ WRONG - Untyped empty arrays */
local!selectedIds: {},
local!filterValues: {},

/* ✅ CORRECT - Type-initialized */
local!selectedIds: tointeger({}),
local!filterValues: touniformstring({}),
```

See `array-type-initialization-guidelines.md` for complete reference.

**Note:** Arrays of maps don't need type initialization—the map structure provides the type.

---

## Pattern Selection for forEach

When iterating with `a!forEach()` to create input fields:

| Scenario | Pattern | Why |
|----------|---------|-----|
| Multi-instance related data (contacts, notes, line items) | **Array of Maps** | Data IS the items being edited |
| Fixed source list collecting separate data (checklist uploads) | **Parallel Arrays** | Data is SEPARATE from source items |

See `foreach-patterns.md` for complete decision tree and examples.

---

## Scope Rules

### Nested a!localVariables() Blocks

Local variables must be declared at the top of `a!localVariables()`. For variables needed only within a specific context, use nested blocks:

```sail
/* ❌ WRONG - Cannot declare inline */
a!forEach(
  items: local!items,
  expression: local!temp: fv!item.value * 2,  /* Invalid! */
  a!textField(value: local!temp)
)

/* ✅ CORRECT - Nested a!localVariables() */
a!forEach(
  items: local!items,
  expression: a!localVariables(
    local!temp: fv!item.value * 2,
    a!textField(value: local!temp)
  )
)
```

---

## Mockup vs Functional Differences

### Mockups

- **Use `local!` for ALL data** (entity, reference, UI state)
- **No `ri!` rule inputs** - Mockups must be self-contained
- **Hardcode sample data** in maps

```sail
/* Mockup - all local variables */
a!localVariables(
  local!case: a!map(title: "Sample", status: "Open"),
  local!statusOptions: {a!map(id: 1, label: "Open"), ...},
  local!isEditMode: false(),
  ...
)
```

### Functional Interfaces

- **Use `ri!` for entity data** being created/updated
- **Use queries for reference data** and display lists
- **Use `local!` only for UI state**

```sail
/* Functional - ri! for entity, queries for reference, local! for UI state */
a!localVariables(
  local!statusOptions: a!queryRecordType(recordType: 'recordType!Status', ...).data,
  local!isEditMode: a!isNotNullOrEmpty(ri!case),

  a!textField(
    value: ri!case['recordType!Case.fields.title'],
    saveInto: ri!case['recordType!Case.fields.title']
  )
)
```

See `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md` for complete functional interface patterns.

---

## Summary

### ✅ DO:
- **Group related data in maps** - Mirrors record structure
- **Use array of maps for lists** - Mirrors query results
- **Nest maps for relationships** - Mirrors one-to-many
- **Keep UI state separate** - Doesn't map to records
- **Type-initialize empty primitive arrays** - Prevents type errors

### ❌ DON'T:
- **Don't use separate variables for related fields** - Hard to convert, hard to maintain
- **Don't use parallel arrays for entity data** - Use array of maps instead
- **Don't use `ri!` in mockups** - Mockups must be self-contained
- **Don't copy `ri!` to `local!` in functional interfaces** - Breaks data binding
