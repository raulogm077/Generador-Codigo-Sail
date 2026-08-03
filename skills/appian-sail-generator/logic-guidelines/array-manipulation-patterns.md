# Array and Data Manipulation Patterns

> **Parent guide:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `/logic-guidelines/foreach-patterns.md` - fv! variables, iteration patterns
> - `/logic-guidelines/grid-selection-patterns.md` - Two-variable selection approach
> - `/logic-guidelines/array-type-initialization-guidelines.md` - Type-casting empty arrays

Patterns for working with arrays, maps, and deriving data in SAIL interfaces.

---

## Accessing Properties Across Arrays - Dot Notation

**The ONLY way to access a property across all items in an array of maps is using dot notation.**

### Correct: Dot Notation

```sail
local!items: {
  a!map(id: 1, name: "Item A", price: 100),
  a!map(id: 2, name: "Item B", price: 200),
  a!map(id: 3, name: "Item C", price: 300)
},

/* Access a single property across all items */
local!allNames: local!items.name,
/* Returns: {"Item A", "Item B", "Item C"} */

local!allPrices: local!items.price,
/* Returns: {100, 200, 300} */

/* Use in calculations */
local!totalPrice: sum(local!items.price),
/* Returns: 600 */

/* Use in comparisons */
local!contractTypes: intersection(local!items.type, {"Contract"}),
/* Returns all "Contract" values found */
```

### Wrong: property() Function Does NOT Exist

```sail
/* ERROR - property() is not a valid SAIL function */
local!allNames: property(local!items, "name", {}),

/* ERROR - This syntax is invalid */
sum(property(local!items, "price"))
```

### Key Rules

- Use `array.propertyName` to extract property values across all items
- Works with any array of maps (local variables with mock data)
- Returns an array of the property values in the same order
- Returns empty array `{}` if source array is empty
- Returns `null` elements for items missing that property

---

## Deriving Full Data from ID Arrays

**Common Pattern:** Grid selections store IDs only, but you need full row data for business logic.

**Solution:** Use `a!forEach() + index() + wherecontains()` to derive full objects from ID array.

### The Pattern

```sail
/* Step 1: Source data (all available items) */
local!availableItems: {
  a!map(id: 1, name: "Item A", type: "Public", price: 100),
  a!map(id: 2, name: "Item B", type: "Contract", price: 200),
  a!map(id: 3, name: "Item C", type: "Public", price: 150)
},

/* Step 2: ID array (from grid selection, user input, etc.) */
local!selectedIds: {1, 3},

/* Step 3: Derive full data using forEach + index + wherecontains */
local!selectedItems: a!forEach(
  items: local!selectedIds,
  expression: index(
    local!availableItems,
    wherecontains(fv!item, local!availableItems.id),
    null
  )
),
/* Returns: {
  a!map(id: 1, name: "Item A", type: "Public", price: 100),
  a!map(id: 3, name: "Item C", type: "Public", price: 150)
} */

/* Step 4: Use derived data for business logic */
local!totalPrice: sum(local!selectedItems.price),
/* Returns: 250 */

local!hasContractType: length(
  intersection(local!selectedItems.type, {"Contract"})
) > 0
/* Returns: false (no Contract items selected) */
```

### How It Works

1. **a!forEach(items: local!selectedIds, ...)** - Iterate over each selected ID
2. **fv!item** - Current ID being processed (e.g., 1, then 3)
3. **wherecontains(fv!item, local!availableItems.id)** - Find position of this ID in source array
   - Searches `{1, 2, 3}` (all IDs) for `fv!item` (current ID)
   - Returns array of positions: `{1}` or `{3}`
4. **index(local!availableItems, positions, null)** - Get full object at that position
   - Returns the complete `a!map(id: ..., name: ..., type: ..., price: ...)`
5. **null** - Default value if ID not found (defensive programming)

---

## Finding a Single Matching Item by ID

**Common Pattern:** You have a single ID and need to find the matching item from an array to access its fields.

### Correct: Use index() + wherecontains() + dot notation

```sail
/* Pattern: Find one item by ID and extract a field */
local!selectedOrgId: 5,
local!organizations: {
  a!map(id: 3, name: "Org A", type: "Nonprofit"),
  a!map(id: 5, name: "Org B", type: "Corporation"),
  a!map(id: 7, name: "Org C", type: "Government")
},

/* Get the organization type for the selected organization */
local!orgType: a!defaultValue(
  index(
    local!organizations,
    wherecontains(local!selectedOrgId, local!organizations.id),
    null
  ).type,  /* Use dot notation to extract the field */
  ""
)
/* Returns: "Corporation" */
```

### Wrong: Using a!forEach() creates array with nulls

```sail
/* DON'T DO THIS - Returns array like {null, "Corporation", null} */
local!orgType: a!defaultValue(
  index(
    a!forEach(
      items: local!organizations,
      expression: if(
        fv!item.id = local!selectedOrgId,
        fv!item.type,  /* Only ONE item matches */
        null  /* Everything else is null */
      )
    ),
    1,  /* ERROR: First element might be null! */
    null
  ),
  ""
)
```

**Why a!forEach() is wrong:**
- Creates an array where most elements are `null`
- `index(..., 1, null)` grabs the FIRST element, which could be `null`
- No guarantee the matching item is at position 1

### Key Rules

- Use `wherecontains(singleId, array.idField)` to find the position
- Use `index(array, position, null)` to get the matching item
- Use dot notation `.fieldName` to extract the field
- Wrap in `a!defaultValue()` to handle not-found cases

---

## Common Use Cases

### Use Case 1: Grid Selection + Conditional Logic

```sail
local!selectedCourseIds: {2, 4},  /* From grid selection */
local!selectedCourses: a!forEach(
  items: local!selectedCourseIds,
  expression: index(
    local!availableCourses,
    wherecontains(fv!item, local!availableCourses.id),
    null
  )
),

/* Show field only if Contract course selected */
if(
  if(
    a!isNotNullOrEmpty(local!selectedCourses),
    length(intersection(local!selectedCourses.type, {"Contract"})) > 0,
    false
  ),
  a!textField(label: "Registration Code", ...),
  {}
)
```

### Use Case 2: Calculating Totals

```sail
local!cartItemIds: {5, 12, 8},
local!cartItems: a!forEach(
  items: local!cartItemIds,
  expression: index(
    local!productCatalog,
    wherecontains(fv!item, local!productCatalog.productId),
    null
  )
),

local!cartTotal: sum(local!cartItems.price),
local!taxableItems: length(
  wherecontains(true, local!cartItems.isTaxable)
)
```

### Use Case 3: Remove Button in Display

```sail
/* Display selected items with Remove buttons */
a!forEach(
  items: local!selectedItems,  /* Already derived from IDs */
  expression: a!cardLayout(
    contents: {
      a!richTextDisplayField(value: fv!item.name),
      a!buttonArrayLayout(
        buttons: {
          a!buttonWidget(
            label: "Remove",
            value: fv!item.id,
            saveInto: {
              a!save(
                local!selectedIds,
                remove(local!selectedIds, wherecontains(fv!item.id, local!selectedIds))
              )
            }
          )
        }
      )
    }
  )
)
```

---

## Combining Different Data Types

```sail
/* WRONG - append() expects compatible types */
local!kpiMap: a!map(name: "Total", count: 100),
local!kpiArray: {a!map(...), a!map(...)},
local!combined: append(local!kpiMap, local!kpiArray)  /* ERROR: Can't append map to array */

/* RIGHT - Use a!update() to insert at position */
local!kpiMap: a!map(name: "Total", count: 100),
local!kpiArray: {a!map(...), a!map(...)},
local!combined: a!update(data: local!kpiArray, index: 1, value: local!kpiMap)

/* ALTERNATIVE - Use insert() */
local!combined: insert(local!kpiArray, local!kpiMap, 1)

/* CORRECT - append() with arrays */
local!array1: {1, 2, 3},
local!array2: {4, 5, 6},
local!combined: append(local!array1, local!array2)  /* Returns {1, 2, 3, 4, 5, 6} */
```

### Key Rules

- `append(array, value)` - Both parameters must be arrays or compatible scalar/array combinations
- `a!update(data: array, index: position, value: newValue)` - Insert or replace at any position
- `insert(array, value, index)` - Insert value at specific position (pushes existing items down)

---

## Using wherecontains() Correctly

**Function Signature:** `wherecontains(valuesToFind, arrayToSearchIn)`
- **Returns:** Array of indices (1-based) where values are found
- **Always returns an array**, even if only one match

```sail
/* WRONG - wherecontains() only takes 2 parameters */
icon: wherecontains(value, statusArray, iconArray)  /* INVALID - 3 params */

/* RIGHT - Use nested index() for lookups */
local!statusConfig: a!forEach(
  items: {"Open", "Closed", "Pending"},
  expression: a!map(
    status: fv!item,
    icon: index({"folder-open", "check-circle", "clock"}, fv!index, "file"),
    color: index({"#059669", "#6B7280", "#F59E0B"}, fv!index, "#000000")
  )
),

/* Extract matching config */
icon: index(
  index(
    local!statusConfig,
    wherecontains("Open", local!statusConfig.status),
    {}
  ).icon,
  1,
  "file"
)

/* How it works:
1. wherecontains("Open", local!statusConfig.status) -> {1}
2. index(local!statusConfig, {1}, {}) -> {a!map(status: "Open", icon: "folder-open", ...)}
3. .icon -> {"folder-open"}
4. index(..., 1, "file") -> "folder-open"
*/
```

### Common Pattern for Lookups

```sail
/* Find value from parallel arrays */
local!statuses: {"Open", "Closed", "Pending"},
local!colors: {"#059669", "#6B7280", "#F59E0B"},

local!color: index(
  local!colors,
  wherecontains("Open", local!statuses),
  "#000000"  /* Default color */
)
/* Returns: "#059669" (first element of colors array) */
```

---

## Array Modification Functions Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `append(array, value)` | Add to end | `append({1,2}, 3)` → `{1,2,3}` |
| `insert(array, value, index)` | Insert at position | `insert({1,3}, 2, 2)` → `{1,2,3}` |
| `remove(array, index)` | Remove at position | `remove({1,2,3}, 2)` → `{1,3}` |
| `a!update(data, index, value)` | Replace at position | `a!update({1,2,3}, 2, 5)` → `{1,5,3}` |
| `wherecontains(val, array)` | Find positions | `wherecontains(2, {1,2,3})` → `{2}` |
| `index(array, pos, default)` | Get at position | `index({1,2,3}, 2, 0)` → `2` |

---

## Related Documentation

- `/logic-guidelines/foreach-patterns.md` - fv! variables, Pattern A vs Pattern B
- `/logic-guidelines/grid-selection-patterns.md` - Two-variable approach for selections
- `/logic-guidelines/array-type-initialization-guidelines.md` - Type-casting empty arrays
