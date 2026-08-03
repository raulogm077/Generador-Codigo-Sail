# Grid Selection Patterns {#grid-selection-patterns}

> **Parent guide:** `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `logic-guidelines/foreach-patterns.md` (iteration patterns)
> - `logic-guidelines/null-safety-quick-ref.md` (null checking)

---

## ⚠️ CRITICAL: selectionValue Contains Identifiers, NOT Full Objects

**MOST COMMON MISTAKE**: Assuming `selectionValue` contains full row data

```sail
❌ WRONG:
a!gridField(
  data: local!courses,
  selectable: true,
  selectionValue: local!selectedCourses,
  selectionSaveInto: local!selectedCourses
)

/* Later... */
a!forEach(
  items: local!selectedCourses,  /* This is selectionValue from a grid */
  expression: fv!item.name        /* ❌ ERROR: fv!item is an integer, not an object! */
)

✅ RIGHT:
a!forEach(
  items: local!selectedCourses,
  expression: a!localVariables(
    local!course: index(local!courses, fv!item, a!map()),  /* Look up full object */
    local!course.name  /* ✅ Now we can access properties */
  )
)
```

**Error you'll see if you get this wrong:**
```
Expression evaluation error: Invalid index: Cannot index property 'name' of type Text into type Number (Integer)
```

---

## Key Rules

- Grid `selectionValue` contains **identifiers** (integers for static data, positions in array)
- `selectionValue` does NOT contain full row objects with properties
- Use `index(dataArray, identifier, defaultValue)` to retrieve full objects

**Before writing code with grid selections, ask:**
1. "Is this variable from a grid's selectionValue?" → YES = need index() lookup
2. "Am I accessing properties on fv!item?" → Must verify fv!item is an object, not an ID
3. "Did I use index() to look up the full object first?" → If NO, you'll get a runtime error

---

## 🚨 MANDATORY: Variable Naming Conventions

### The Naming Problem

Grid `selectionValue` stores **ONLY identifiers** (Integer Array or Text Array), NOT full row objects. Variables that store these IDs MUST use naming conventions that make this clear.

### ❌ WRONG - Ambiguous Names That Suggest Full Objects
```sail
local!selectedCases: {},      /* ❌ WRONG: Suggests full case objects */
local!selectedTasks: {},      /* ❌ WRONG: Suggests full task objects */
local!selectedEmployees: {},  /* ❌ WRONG: Suggests full employee objects */
local!chosenItems: {},        /* ❌ WRONG: Suggests full item data */
```

**Why this is dangerous:**
- Code readers assume these variables contain full objects
- Leads to property access errors like `local!selectedCases.title` (ERROR: trying to access .title on integer array)
- Runtime error: "Cannot index property 'title' of type Text into type Number (Integer)"

### ✅ CORRECT - Clear Names That Indicate ID Arrays
```sail
/* Option 1: "Ids" suffix (recommended for primary keys) */
local!selectedCaseIds: {},       /* ✅ CLEAR: Integer array of case IDs */
local!selectedTaskIds: {},       /* ✅ CLEAR: Integer array of task IDs */
local!selectedEmployeeIds: {},   /* ✅ CLEAR: Integer array of employee IDs */

/* Option 2: "Keys" suffix (recommended for text identifiers) */
local!selectedStatusKeys: {},    /* ✅ CLEAR: Text array of status keys */
local!selectedCategoryKeys: {},  /* ✅ CLEAR: Text array of category keys */

/* Option 3: "Indexes" suffix (recommended for positional selection) */
local!selectedRowIndexes: {},    /* ✅ CLEAR: Integer array of row positions */
```

### Naming Convention Rules

**MANDATORY naming pattern for grid selection ID arrays:**

1. **For Integer IDs** (most common):
   - ✅ Use suffix: `Ids`
   - Examples: `local!selectedCaseIds`, `local!selectedTaskIds`, `local!chosenEmployeeIds`

2. **For Text Keys**:
   - ✅ Use suffix: `Keys`
   - Examples: `local!selectedStatusKeys`, `local!selectedCategoryKeys`

3. **For Array Indexes**:
   - ✅ Use suffix: `Indexes`
   - Examples: `local!selectedRowIndexes`

4. **Computed Variables** (full data derived from IDs):
   - ✅ Use descriptive name WITHOUT suffix
   - Examples: `local!selectedCases`, `local!selectedTasks`, `local!selectedEmployees`

---

## 🚨 CRITICAL: Two-Variable Approach Implementation

### The Core Problem

Grid `selectionValue` stores **ONLY identifiers** (Integer Array or Text Array), NOT full row data. Trying to access row properties directly from `selectionValue` will cause runtime errors.

### ❌ WRONG Pattern - Single Variable (Common Mistake)
```sail
local!selectedItems: {},  /* ❌ Trying to use one variable for both selection and data */

a!gridField(
  data: local!availableItems,
  columns: {...},
  selectionValue: local!selectedItems,  /* ❌ This stores IDs only! */
  selectionSaveInto: local!selectedItems
)

/* Later trying to access row data */
if(
  length(
    intersection(
      local!selectedItems.type,  /* ❌ ERROR: selectedItems contains IDs, not objects! */
      {"Contract"}
    )
  ) > 0,
  ...
)
```

**Error you'll see:**
```
Expression evaluation error: Invalid index: Cannot index property 'type' of type Text into type Number (Integer)
```

### ✅ CORRECT Pattern - Two-Variable Approach

**Step 1: Declare TWO variables**
```sail
local!availableItems: {
  a!map(id: 1, name: "Item A", type: "Public"),
  a!map(id: 2, name: "Item B", type: "Contract"),
  a!map(id: 3, name: "Item C", type: "Public")
},
local!selectedItemIds: {},  /* Stores grid selection (IDs only) */
local!selectedItems: a!forEach(  /* Computed: derives full data from IDs */
  items: local!selectedItemIds,
  expression: index(
    local!availableItems,
    wherecontains(fv!item, local!availableItems.id),
    null
  )
),
```

**How the computed variable works:**
1. `a!forEach()` iterates over each ID in `local!selectedItemIds` (e.g., {1, 3})
2. For each ID (`fv!item`), `wherecontains(fv!item, local!availableItems.id)` finds the position in the array
3. `index()` retrieves the full map at that position
4. Result: An array of complete objects for all selected IDs

**Step 2: Configure grid to use the IDs variable**
```sail
a!gridField(
  data: local!availableItems,
  columns: {
    a!gridColumn(label: "Name", value: fv!row.name),
    a!gridColumn(label: "Type", value: fv!row.type)
  },
  selectable: true,
  selectionValue: local!selectedItemIds,  /* ✅ Use IDs variable */
  selectionSaveInto: local!selectedItemIds  /* ✅ Save to IDs variable */
)
```

**Step 3: Access full data using the computed variable (with null safety)**
```sail
/* ✅ CORRECT: Use nested if() for null-safe property access */
if(
  if(
    a!isNotNullOrEmpty(local!selectedItems),
    length(
      intersection(
        local!selectedItems.type,  /* ✅ Safe: has full data */
        {"Contract"}
      )
    ) > 0,
    false  /* Return safe default when empty */
  ),
  /* Show registration code field */,
  {} /* Hide field */
)
```

**Step 4: Display selected items**
```sail
a!forEach(
  items: local!selectedItems,  /* ✅ Iterate over full data */
  expression: a!cardLayout(
    contents: {
      a!richTextDisplayField(
        value: {
          a!richTextItem(text: fv!item.name, style: "STRONG"),
          " - ",
          fv!item.type
        }
      )
    }
  )
)
```

**Step 5: Remove items (modify IDs only)**
```sail
/* Remove button in forEach */
a!buttonWidget(
  label: "Remove",
  value: fv!item.id,
  saveInto: a!save(
    local!selectedItemIds,  /* ✅ Modify IDs variable only */
    remove(local!selectedItemIds, wherecontains(fv!item.id, local!selectedItemIds))
  )
)
```

---

## Complete Enforcement Checklist

**Before writing ANY grid with selection, verify ALL of these:**

1. ✅ **Variable Naming Convention (MANDATORY)**:
   - [ ] ID array variable name ends with "Ids", "Keys", or "Indexes"
   - [ ] Computed variable name is descriptive WITHOUT suffix
   - [ ] Variable names clearly distinguish between IDs and full data
   - Example: `local!selectedCaseIds` (IDs) vs `local!selectedCases` (computed data)

2. ✅ **Two-Variable Pattern (MANDATORY)**:
   - [ ] TWO variables declared: one for IDs, one computed for full data
   - [ ] ID variable initialized as empty array: `{}`
   - [ ] Computed variable uses `a!forEach() + index() + wherecontains()` pattern
   - [ ] Both variables declared before use

3. ✅ **Grid Configuration (MANDATORY)**:
   - [ ] `selectionValue` parameter uses ID variable (with suffix)
   - [ ] `selectionSaveInto` parameter uses ID variable (with suffix)
   - [ ] Grid `selectionValue` treated as ID array, NEVER as full row data

4. ✅ **Property Access Rules (MANDATORY)**:
   - [ ] ALL property access (`.fieldName`) uses computed variable ONLY
   - [ ] NEVER attempt property access on ID array variable
   - [ ] Null checks precede all property access on computed variable

5. ✅ **Null Safety (MANDATORY)**:
   - [ ] Use nested `if()` for null-safe property access (NOT `and()`)
   - [ ] Pattern: `if(a!isNotNullOrEmpty(computed), computed.property, defaultValue)`
   - [ ] `and()` does NOT short-circuit - see Short-Circuit Evaluation Rules

6. ✅ **Data Derivation (MANDATORY)**:
   - [ ] Use `a!forEach() + index() + wherecontains()` to derive full data from IDs
   - [ ] Never use `filter()` for deriving data (requires fv!item context)
   - [ ] Never save to computed variable (it recalculates automatically)

7. ✅ **Iteration Patterns (MANDATORY)**:
   - [ ] When iterating to display data: use computed variable (full data)
   - [ ] When modifying selection: modify ID variable only
   - [ ] Never iterate over ID array expecting full objects

8. ✅ **Conditional Logic (MANDATORY)**:
   - [ ] When checking properties: use computed variable with null checks
   - [ ] Never check properties on ID array variable
   - [ ] Pattern: `if(a!isNotNullOrEmpty(computed), <property check>, false)`

9. ✅ **Selection Modifications (MANDATORY)**:
   - [ ] All `saveInto` operations modify ID array ONLY
   - [ ] Use `append()`, `remove()`, `a!save()` on ID variable
   - [ ] Computed variable updates automatically

10. ✅ **Grid Context (MANDATORY)**:
    - [ ] Grid `selectionValue` is ALWAYS a list (even with `maxSelections: 1`)
    - [ ] Use `index(selectionValue, 1, null)` to get first selection from list
    - [ ] Check `length(selectionValue) > 0` before accessing selections

11. ✅ **Code Review (MANDATORY)**:
    - [ ] Search code for ID variable name - verify NO property access attempted
    - [ ] Search code for computed variable name - verify ALL property access uses it
    - [ ] Verify naming convention followed consistently throughout interface

---

## Complete Working Example

```sail
a!localVariables(
  local!availableCourses: {
    a!map(id: 1, number: "OSHA #500", name: "Construction Safety", type: "Public"),
    a!map(id: 2, number: "OSHA #501", name: "Maritime Safety", type: "Public"),
    a!map(id: 3, number: "OSHA #5600", name: "Disaster Response", type: "Contract")
  },
  local!selectedCourseIds: {},
  local!selectedCourses: a!forEach(
    items: local!selectedCourseIds,
    expression: index(
      local!availableCourses,
      wherecontains(fv!item, local!availableCourses.id),
      null
    )
  ),
  local!registrationCode,
  {
    a!gridField(
      data: local!availableCourses,
      columns: {
        a!gridColumn(label: "Number", value: fv!row.number),
        a!gridColumn(label: "Name", value: fv!row.name),
        a!gridColumn(label: "Type", value: fv!row.type)
      },
      selectable: true,
      selectionValue: local!selectedCourseIds,
      selectionSaveInto: local!selectedCourseIds
    ),
    /* Show registration code field if contract course selected */
    if(
      if(
        a!isNotNullOrEmpty(local!selectedCourses),
        length(
          intersection(
            local!selectedCourses.type,
            {"Contract"}
          )
        ) > 0,
        false
      ),
      a!textField(
        label: "Registration Code",
        value: local!registrationCode,
        saveInto: local!registrationCode,
        required: true
      ),
      {}
    )
  }
)
```

---

## 🚨 CRITICAL ANTI-PATTERNS

### Anti-Pattern 1: Property Access on ID Array Variable

**THE ERROR:**
```sail
a!localVariables(
  local!allTasks: {
    a!map(id: 1, title: "Review contract", status: "Open"),
    a!map(id: 2, title: "Update case file", status: "Closed"),
    a!map(id: 3, title: "Schedule hearing", status: "Open")
  },

  /* ❌ WRONG: Variable name suggests objects but stores IDs */
  local!selectedTasks: {},

  a!gridField(
    data: local!allTasks,
    columns: {
      a!gridColumn(label: "Title", value: fv!row.title),
      a!gridColumn(label: "Status", value: fv!row.status)
    },
    selectable: true,
    selectionValue: local!selectedTasks,  /* Stores integers {1, 3}, NOT objects! */
    selectionSaveInto: local!selectedTasks
  ),

  /* ❌ WRONG: Trying to access .status property on integer array */
  a!textField(
    label: "Selected Task Status",
    value: local!selectedTasks.status,  /* ERROR: Cannot access .status on {1, 3}! */
    readOnly: true
  )
)
```

**Runtime Error:**
```
Expression evaluation error: Invalid index: Cannot index property 'status' of type Text into type Number (Integer)
```

**THE FIX:**
```sail
a!localVariables(
  local!allTasks: {
    a!map(id: 1, title: "Review contract", status: "Open"),
    a!map(id: 2, title: "Update case file", status: "Closed"),
    a!map(id: 3, title: "Schedule hearing", status: "Open")
  },

  /* ✅ CORRECT: Clear naming - stores IDs only */
  local!selectedTaskIds: {},

  /* ✅ CORRECT: Computed variable derives full data */
  local!selectedTasks: a!forEach(
    items: local!selectedTaskIds,
    expression: index(
      local!allTasks,
      wherecontains(fv!item, local!allTasks.id),
      null
    )
  ),

  a!gridField(
    data: local!allTasks,
    columns: {
      a!gridColumn(label: "Title", value: fv!row.title),
      a!gridColumn(label: "Status", value: fv!row.status)
    },
    selectable: true,
    selectionValue: local!selectedTaskIds,  /* ✅ Use ID variable */
    selectionSaveInto: local!selectedTaskIds
  ),

  /* ✅ CORRECT: Access properties on computed variable */
  a!textField(
    label: "Selected Task Status",
    value: joinarray(local!selectedTasks.status, ", "),  /* ✅ Works! */
    readOnly: true
  )
)
```

### Anti-Pattern 2: Using forEach on ID Array Without Lookup

**THE ERROR:**
```sail
/* ❌ WRONG: Iterating over IDs as if they were objects */
a!forEach(
  items: local!selectedEmployees,  /* This is {101, 103}, NOT employee objects! */
  expression: a!richTextDisplayField(
    value: a!richTextItem(
      text: fv!item.name  /* ERROR: fv!item is 101, not an object! */
    )
  )
)
```

**THE FIX:**
```sail
/* ✅ CORRECT: Iterate over computed variable with full data */
a!forEach(
  items: local!selectedEmployees,  /* Full employee objects */
  expression: a!richTextDisplayField(
    value: a!richTextItem(
      text: fv!item.name  /* ✅ Works! fv!item is now a complete employee object */
    )
  )
)
```

### Anti-Pattern 3: Conditional Logic on ID Array Properties

**THE ERROR:**
```sail
/* ❌ WRONG: Trying to filter/check properties on ID array */
showWhen: length(
  a!forEach(
    items: local!selectedCases,  /* IDs: {1, 3} */
    expression: if(fv!item.isUrgent, fv!item, null)  /* ERROR: fv!item is integer! */
  )
) > 0
```

**THE FIX:**
```sail
/* ✅ CORRECT: Check properties on computed variable with null safety */
showWhen: if(
  a!isNotNullOrEmpty(local!selectedCases),  /* Null check first */
  length(
    intersection(
      local!selectedCases.isUrgent,  /* ✅ Access property on full data */
      {true}
    )
  ) > 0,
  false
)
```

---

## Key Takeaways

**Every anti-pattern shares these root causes:**
1. ❌ Ambiguous variable naming (no "Ids"/"Keys"/"Indexes" suffix)
2. ❌ Only ONE variable created (missing computed variable)
3. ❌ Property access attempted on ID array

**Every fix requires:**
1. ✅ Clear variable naming with suffix for IDs
2. ✅ TWO variables (IDs + computed)
3. ✅ Property access ONLY on computed variable
4. ✅ Null checking before property access
