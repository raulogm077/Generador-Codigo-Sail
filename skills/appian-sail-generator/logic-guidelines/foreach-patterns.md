# a!forEach() Patterns and Function Variables {#foreach-patterns}

> **Parent guide:** `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `logic-guidelines/local-variable-patterns.md` (data modeling philosophy - why Pattern A is preferred)
> - `logic-guidelines/grid-selection-patterns.md` (grid-specific iteration)
> - `logic-guidelines/functions-reference.md` (function reference)

---

## 🎯 Pattern Selection Decision Tree (READ FIRST)

When using `a!forEach()` to generate input fields, choose the correct pattern:

```
Are you collecting MULTIPLE INSTANCES of RELATED data?
(e.g., work experiences, addresses, contacts, line items, education history)
│
├─ YES → Use PATTERN A: Array of Maps (PREFERRED)
│        • local!items: {a!map(field1: null, field2: null, ...)}
│        • saveInto: fv!item.fieldName
│        • Supports add/remove items dynamically
│
└─ NO → Are you iterating a FIXED source list to collect SEPARATE data?
        (e.g., checklist items where you upload files, approval steps with comments)
        │
        ├─ YES → Use PATTERN B: Parallel Arrays (type-initialized)
        │        • local!uploads: tointeger({}), local!comments: touniformstring({}), etc.
        │        • saveInto: a!save(local!array, a!update(local!array, fv!index, save!value))
        │
        └─ NO → You may not need forEach for input fields
                • Consider single variables or other patterns
```

### Quick Reference

| Scenario | Pattern | Data Structure | Save Pattern |
|----------|---------|----------------|--------------|
| Case notes form | **A: Array of Maps** | `{a!map(noteType: null, description: null, ...)}` | `fv!item.noteType` |
| Contact list | **A: Array of Maps** | `{a!map(name: null, phone: null, ...)}` | `fv!item.name` |
| Invoice line items | **A: Array of Maps** | `{a!map(description: null, amount: null, ...)}` | `fv!item.amount` |
| Document checklist with uploads | **B: Parallel Arrays** | `local!files: tointeger({}), local!notes: touniformstring({})` | `a!update(local!files, fv!index, ...)` |
| Approval steps with comments | **B: Parallel Arrays** | `local!decisions: touniformstring({}), local!comments: touniformstring({})` | `a!update(local!decisions, fv!index, ...)` |

---

## Available Function Variables in a!forEach()

When using `a!forEach()`, Appian automatically provides these function variables within the `expression` parameter:

| Variable | Type | Description | Common Use Cases |
|----------|------|-------------|------------------|
| `fv!item` | Any | Current item value from the array | Accessing properties, creating UI components, data transformations |
| `fv!index` | Integer | Current iteration position (1-based) | Array manipulation, numbering, position-based logic |
| `fv!isFirst` | Boolean | `true` only on first iteration | Special formatting for first item, conditional headers |
| `fv!isLast` | Boolean | `true` only on last iteration | Special formatting for last item, conditional footers |
| `fv!itemCount` | Integer | Total number of items in array | Progress indicators, conditional logic based on total |

**⚠️ CRITICAL:** These variables are **ONLY** available inside `a!forEach()` expressions. They do NOT exist in grid columns, chart configurations, or other iteration functions.

---

## fv!item - Accessing Current Item

**Purpose:** Access the current item's value or properties during iteration

**SAIL-Specific Syntax:**
- **Map properties:** Use dot notation: `fv!item.title`
- **Scalar values:** Use `fv!item` directly

```sail
/* Map data with dot notation */
a!forEach(
  items: {
    a!map(title: "Overview", icon: "info-circle"),
    a!map(title: "Details", icon: "list")
  },
  expression: a!sectionLayout(
    label: fv!item.title,  /* Dot notation for maps */
    contents: {
      a!richTextIcon(icon: fv!item.icon)
    }
  )
)
```

---

## fv!index - Current Position (1-Based)

**Purpose:** Get the current iteration position for array manipulation or position-based logic

**IMPORTANT:** Appian uses 1-based indexing. First item is index 1, not 0.

### Critical Pattern: Removing Items from Arrays

```sail
/* Common pattern: Remove button for dynamic lists */
a!forEach(
  items: local!items,
  expression: a!cardLayout(
    contents: {
      a!textField(
        label: "Item " & fv!index,  /* Use for labeling */
        value: fv!item.text,
        saveInto: fv!item.text
      )
    },
    link: a!dynamicLink(
      label: "Remove",
      value: fv!index,  /* Pass index to identify which item to remove */
      saveInto: {
        a!save(
          local!items,
          remove(
            local!items,
            fv!index  /* Remove at this position */
          )
        )
      }
    )
  )
)
```

### Parallel Array Lookups (Status/Icon Mapping)

```sail
/* Map colors and icons to status values by position */
local!statuses: {"Open", "In Progress", "Completed"},
local!icons: {"folder-open", "clock", "check-circle"},
local!colors: {"#EF4444", "#F59E0B", "#10B981"},

a!forEach(
  items: local!statuses,
  expression: a!stampField(
    icon: index(local!icons, fv!index, "file"),      /* Match by position */
    backgroundColor: index(local!colors, fv!index, "#6B7280"),
    contentColor: "#FFFFFF",
    size: "MEDIUM"
  )
)
```

---

## fv!isFirst - First Iteration Detection

**Purpose:** Detect the first iteration for conditional headers or skipping separators

```sail
a!forEach(
  items: local!sections,
  expression: {
    /* Add divider before all items EXCEPT the first */
    if(
      fv!isFirst,
      {},  /* No divider for first item */
      a!columnsLayout(
        columns: {a!columnLayout(contents: {}, width: "FILL")},
        marginBelow: "STANDARD"
      )
    ),
    /* Then show the content */
    a!cardLayout(
      contents: {
        a!richTextDisplayField(value: fv!item.content)
      }
    )
  }
)
```

---

## fv!isLast - Last Iteration Detection

**Purpose:** Detect the last iteration for conditional footers, "Add" buttons, or skipping separators

### Critical Pattern: Add Button After Last Item

```sail
a!forEach(
  items: local!invoiceItems,
  expression: {
    /* Show each line item */
    a!columnsLayout(
      columns: {
        a!columnLayout(
          contents: {a!richTextDisplayField(value: fv!item.description)}
        ),
        a!columnLayout(
          contents: {a!richTextDisplayField(value: "$" & fv!item.amount)},
          width: "NARROW"
        )
      }
    ),
    /* Show "Add" button or total only after last item */
    if(
      fv!isLast,
      a!richTextDisplayField(
        value: a!richTextItem(
          text: "Total: $" & sum(local!invoiceItems.amount),
          size: "LARGE",
          style: "STRONG"
        )
      ),
      {}
    )
  }
)
```

---

## fv!itemCount - Total Item Count

**Purpose:** Access the total number of items for progress indicators or conditional logic

```sail
/* Progress indicator pattern */
a!forEach(
  items: local!uploadQueue,
  expression: a!cardLayout(
    contents: {
      a!richTextDisplayField(
        value: a!richTextItem(
          text: "Processing " & fv!index & " of " & fv!itemCount,
          style: "STRONG"
        )
      ),
      a!textField(
        label: "File",
        value: fv!item.filename,
        readOnly: true
      )
    }
  )
)
```

---

## Combining Multiple Variables

```sail
/* Dynamic remove button logic with fv!itemCount and fv!isLast */
a!forEach(
  items: local!lineItems,
  expression: a!cardLayout(
    contents: {
      a!textField(
        label: "Item " & fv!index,
        value: fv!item.name
      )
    },
    link: if(
      and(
        fv!itemCount > 1,  /* Only show remove if more than 1 item */
        not(fv!isLast)     /* Keep at least the last item */
      ),
      a!dynamicLink(
        label: "Remove",
        value: fv!index,
        saveInto: a!save(local!lineItems, remove(local!lineItems, fv!index))
      ),
      {}
    )
  )
)
```

---

## Common Mistakes

### ❌ MISTAKE: Accessing properties on scalar values

```sail
/* ❌ WRONG - fv!item is a string, not an object */
a!forEach(
  items: {"Open", "Closed"},
  expression: fv!item.status  /* ❌ ERROR */
)

/* ✅ RIGHT */
a!forEach(
  items: {"Open", "Closed"},
  expression: a!tagField(text: fv!item)  /* ✅ fv!item IS the value */
)
```

---

## Best Practices Summary

### ✅ DO:
- **Understand fv!item type** - Scalar, map, or object?
- **Use fv!index for array manipulation** - `remove()`, `insert()`, `a!update()`
- **Use fv!isFirst/isLast for conditional rendering** - Headers, footers, dividers
- **Remember fv!index is 1-based** - Matches Appian's `index()` function
- **Combine variables for complex logic** - e.g., `and(fv!itemCount > 1, not(fv!isLast))`

### ❌ DON'T:
- **Don't access properties on scalar fv!item** - Check your data type first
- **Don't use 0-based indexing** - Appian is 1-based throughout
- **Don't use fv! variables outside a!forEach()** - They don't exist in other contexts
- **Don't forget null checks on fv!item properties** - Map fields can be null

---

## PATTERN A: Array of Maps (PREFERRED for Multi-Instance Data Entry)

Use this pattern when collecting **multiple instances of related data** such as work experiences, addresses, contacts, education history, or line items. The forEach items ARE the data being edited.

**Why this is preferred:** Map structure mirrors record types, making mockup → functional conversion straightforward. See `local-variable-patterns.md` for the full data modeling philosophy.

**Key characteristics:**
- User can add/remove entries dynamically
- All fields for one entry are grouped together in a map
- Direct property saving: `saveInto: fv!item.propertyName`
- Structure converts cleanly to record type instances

When updating individual properties of items in a forEach loop, save directly to the property—do NOT reconstruct the entire map.

### ✅ CORRECT - Direct Property Save

```sail
a!forEach(
  items: local!employers,
  expression: a!textField(
    label: "Employer Name",
    value: a!defaultValue(fv!item.employerName, ""),
    saveInto: fv!item.employerName,  /* Directly updates just this property */
    required: true()
  )
)
```

### ❌ WRONG - Full Map Reconstruction

```sail
a!forEach(
  items: local!employers,
  expression: a!textField(
    label: "Employer Name",
    value: a!defaultValue(fv!item.employerName, ""),
    saveInto: a!save(
      local!employers,
      a!update(
        local!employers,
        fv!index,
        a!map(
          employerName: save!value,
          jobTitle: fv!item.jobTitle,
          contactName: fv!item.contactName,
          /* ...reconstructing all fields is inefficient and verbose... */
        )
      )
    )
  )
)
```

### When to Use Multi-Save Pattern

Use the multi-save pattern ONLY when a field update must trigger dependent calculations:

```sail
a!dateField(
  label: "Start Date",
  value: fv!item.startDate,
  saveInto: {
    fv!item.startDate,           /* Save the date */
    a!save(                       /* Calculate dependent field */
      fv!item.experienceYears,
      if(
        and(
          a!isNotNullOrEmpty(save!value),
          a!isNotNullOrEmpty(fv!item.endDate)
        ),
        fixed(tointeger(fv!item.endDate - save!value) / 365, 1),
        0
      )
    )
  }
)
```

### Key Rules
- ✅ Simple field updates → `saveInto: fv!item.propertyName`
- ✅ Dependent calculations → Use multi-save with direct property updates
- ❌ NEVER reconstruct the entire map for a single field change

---

## PATTERN B: Parallel Arrays (for Fixed Source List with Separate Data Collection)

Use this pattern when iterating over a **fixed source list** (like a checklist or approval steps) to collect **separate data** that doesn't belong to the source items. The forEach items are NOT the data being edited—they're a reference list.

**Key characteristics:**
- Source list is fixed (e.g., required documents, approval steps)
- Collected data (files, comments, dates) is stored separately from source
- Index-based saving: `saveInto: a!save(local!array, a!update(local!array, fv!index, save!value))`

When using forEach to generate multiple input fields (textField, dateField, fileUploadField, etc.) against a fixed source list, each field MUST save to a specific position in an array using `fv!index`.

### Pattern: Parallel Arrays for Fixed Source Lists

```sail
/* Initialize parallel arrays - type-initialized per data type (see array-type-initialization-guidelines.md) */
local!uploadedFiles: tointeger({}),       /* Document IDs */
local!completionDates: todate({}),        /* Date values */
local!notes: touniformstring({}),         /* Text values */

a!forEach(
  items: local!requiredItems,
  expression: {
    a!fileUploadField(
      label: "Upload " & fv!item.name,
      value: index(local!uploadedFiles, fv!index, null),  /* ✅ Access by index */
      saveInto: a!save(
        local!uploadedFiles,
        a!update(local!uploadedFiles, fv!index, save!value)  /* ✅ Update by index */
      )
    ),
    a!dateField(
      label: "Completion Date",
      value: index(local!completionDates, fv!index, null),  /* ✅ Access by index */
      saveInto: a!save(
        local!completionDates,
        a!update(local!completionDates, fv!index, save!value)  /* ✅ Update by index */
      )
    ),
    a!textField(
      label: "Notes",
      value: index(local!notes, fv!index, null),  /* ✅ Access by index */
      saveInto: a!save(
        local!notes,
        a!update(local!notes, fv!index, save!value)  /* ✅ Update by index */
      )
    )
  }
)
```

### ❌ WRONG - Not storing user input:

```sail
a!forEach(
  items: local!requiredItems,
  expression: a!fileUploadField(
    label: "Upload " & fv!item.name,
    value: null,      /* ❌ No data access */
    saveInto: null    /* ❌ User input lost! */
  )
)
```

### ❌ WRONG - Trying to use fv!item properties:

```sail
/* This doesn't work - you can't store different values in the same property */
a!forEach(
  items: local!requiredItems,
  expression: a!fileUploadField(
    label: "Upload " & fv!item.name,
    value: fv!item.uploadedFile,        /* ❌ Can't write to fv!item */
    saveInto: fv!item.uploadedFile      /* ❌ fv!item is read-only */
  )
)
```

### ⚠️ CRITICAL: Type Safety with index() in Arithmetic Operations

The `index()` function returns a **List type**, even when accessing a single element. When using `index()` results in arithmetic operations (date calculations, numeric operations), you MUST wrap the result in a type converter.

**❌ WRONG - Direct use in date arithmetic:**

```sail
a!dateField(
  label: "Completion Date",
  value: index(local!completionDates, fv!index, null),
  saveInto: a!save(
    local!completionDates,
    a!update(local!completionDates, fv!index, save!value)
  ),
  validations: if(
    fv!item.startDate - index(local!completionDates, fv!index, today()) > 365,  /* ❌ ERROR: List type! */
    "Date too old",
    null
  )
)
```

**✅ CORRECT - Wrapped in todate():**

```sail
a!dateField(
  label: "Completion Date",
  value: index(local!completionDates, fv!index, null),
  saveInto: a!save(
    local!completionDates,
    a!update(local!completionDates, fv!index, save!value)
  ),
  validations: if(
    fv!item.startDate - todate(index(local!completionDates, fv!index, today())) > 365,  /* ✅ todate() wrapper */
    "Date too old",
    null
  )
)
```

### Required Type Converters by Operation:
- **Date/DateTime arithmetic**: Use `todate(index(...))` or `todatetime(index(...))`
- **Numeric calculations**: Use `tonumber(index(...))` or `tointeger(index(...))`
- **Text concatenation**: Use `totext(index(...))` if needed

### Key Rules:
1. **One local variable per field type** - Use parallel arrays indexed by `fv!index`
2. **Initialize as empty arrays** - `local!uploadedFiles: {}`
3. **Access pattern** - `value: index(local!array, fv!index, null)`
4. **Save pattern** - `saveInto: a!save(local!array, a!update(local!array, fv!index, save!value))`
5. **Array synchronization** - All parallel arrays maintain same index positions for same item
6. **Type safety for arithmetic** - Wrap `index()` in type converters (`todate()`, `tonumber()`) when used in calculations

### When to Use This Pattern:
- ✅ forEach generating file upload fields for multiple items
- ✅ forEach generating date fields for multiple items
- ✅ forEach generating text input fields for multiple items
- ✅ Any scenario where forEach creates input fields that need to store different values per item

### When NOT to Use This Pattern:
- ❌ forEach only displaying data (use fv!item properties directly)
- ❌ Single input field not in forEach (use regular local variable)
- ❌ Input fields where all items share one value (use single local variable)
