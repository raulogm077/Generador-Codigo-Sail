# Display Conversion - Action Patterns {#display-actions}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/display-conversion-core.md` - Interface detection
> - `/conversion-guidelines/display-conversion-grids.md` - Grid conversion patterns
> - `/conversion-guidelines/common-conversion-patterns.md` - Query patterns
> - `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

Patterns for converting action buttons to record actions, including action type rules, placement guidelines, and toolbar configuration.

---

## 📑 Module Navigation {#display-actions.nav}

- `{#display-actions.type-rules}` - Record List Actions vs Related Actions
- `{#display-actions.type-rules.primary-key}` - Primary key identification
- `{#display-actions.type-rules.identification}` - How to identify action type
- `{#display-actions.type-rules.placement}` - Valid placement rules
- `{#display-actions.type-rules.mistakes}` - Common mistakes to avoid
- `{#display-actions.buttons}` - Action buttons in grids
- `{#display-actions.toolbar-actions}` - Grid toolbar actions
- `{#display-actions.refresh-after}` - refreshAfter parameter usage

---

## Action Type Rules {#display-actions.type-rules}

**🚨 CRITICAL: Understand the two types of record actions before converting.**

### Action Type Definitions {#display-actions.type-rules.definitions}

| Type | Purpose | Identifier Required? | Valid Locations |
|------|---------|---------------------|-----------------|
| **Record List Actions** | Create new records (no existing record context) | ❌ NO identifier | Header buttons, grid `recordActions` parameter |
| **Related Actions** | Operate on existing records (edit, delete, approve) | ✅ YES - `fv!row['recordType!Type.fields.primaryKey']` | Grid columns only (inside `a!recordActionField()`) |

### Primary Key Identification {#display-actions.type-rules.primary-key}

**Before adding related actions, identify the primary key field from data-model-context.md:**

1. Find the record type's Fields section
2. Look for the field where **Primary Key** column = "Yes"
3. Copy the full field reference from the **Field Reference** column
4. Use in identifier: `fv!row['recordType!Type.fields.primaryKeyName']`

**Example from data-model-context.md:**
```markdown
### CASE

**Fields**:

| **Field Name** | **Data Type** | **Primary Key** | **Field Reference** |
|----------------|---------------|-----------------|---------------------|
| caseId | Integer | Yes | `'recordType!CASE.fields.caseId'` |
| caseNumber | Text | No | `'recordType!CASE.fields.caseNumber'` |
| assignedTo | User | No | `'recordType!CASE.fields.assignedTo'` |
```

**Usage in grid column:**
```sail
identifier: fv!row['recordType!CASE.fields.caseId']
```

### How to Identify Action Type in data-model-context.md {#display-actions.type-rules.identification}

The **Record Actions** section uses an **Action Type** column to distinguish between action types:

```markdown
**Record Actions**:

| **Action Name** | **Action Type** | **Action Reference** |
|----------------|-----------------|---------------------|
| createCase (New Case) | Record List | `'recordType!CASE.actions.createCase'` |
| editCase (Edit Case) | Related | `'recordType!CASE.actions.editCase'` |
| closeCase (Close Case) | Related | `'recordType!CASE.actions.closeCase'` |
```

**How to read this table:**
- **Action Type = "Record List"** → Use in header OR `recordActions` parameter, NO identifier
- **Action Type = "Related"** → Use in grid columns, REQUIRE `identifier: fv!row['recordType!Type.fields.primaryKey']`

### Valid Placement Rules {#display-actions.type-rules.placement}

```
RECORD LIST ACTIONS (create new):
├─ ✅ Header → a!recordActionField() with NO identifier
├─ ✅ Grid toolbar → recordActions parameter with NO identifier
└─ ❌ NEVER in grid columns (no record context to create against)

RELATED ACTIONS (operate on existing):
├─ ✅ Grid columns → a!recordActionField() with identifier: fv!row['recordType!Type.fields.primaryKey']
└─ ❌ NEVER in header/toolbar without identifier (which record to operate on?)
```

### 🚨 Common Mistakes to Avoid {#display-actions.type-rules.mistakes}

**Mistake 1: Using Record List Action in grid column**
```sail
/* ❌ WRONG - Record List Action inside grid column */
a!gridColumn(
  label: "Actions",
  value: a!recordActionField(
    actions: {
      a!recordActionItem(
        action: 'recordType!CASE.actions.createCase',  /* This is a Record List Action! */
        identifier: fv!row['recordType!CASE.fields.caseId']  /* Doesn't make sense - creates new, not edits existing */
      )
    }
  )
)

/* ✅ CORRECT - Related Action inside grid column */
a!gridColumn(
  label: "Actions",
  value: a!recordActionField(
    actions: {
      a!recordActionItem(
        action: 'recordType!CASE.actions.editCase',  /* This is a Related Action */
        identifier: fv!row['recordType!CASE.fields.caseId']  /* Required - identifies which record to edit */
      )
    }
  )
)
```

**Mistake 2: Adding identifier to Record List Action**
```sail
/* ❌ WRONG - identifier on create action */
recordActions: {
  a!recordActionItem(
    action: 'recordType!CASE.actions.createCase',
    identifier: fv!row['recordType!CASE.fields.caseId']  /* WRONG - create doesn't need existing record */
  )
}

/* ✅ CORRECT - no identifier on create action */
recordActions: {
  a!recordActionItem(
    action: 'recordType!CASE.actions.createCase'
    /* NO identifier - creates new record */
  )
}
```

**Mistake 3: Omitting identifier from Related Action**
```sail
/* ❌ WRONG - missing identifier on edit action */
a!recordActionItem(
  action: 'recordType!CASE.actions.editCase'
  /* Missing identifier - which record to edit? */
)

/* ✅ CORRECT - identifier required (use primary key field) */
a!recordActionItem(
  action: 'recordType!CASE.actions.editCase',
  identifier: fv!row['recordType!CASE.fields.caseId']
)
```

### Action Type Checklist {#display-actions.type-rules.checklist}

Before adding any record action:
- [ ] Identify action type from data-model-context.md (Record List vs Related)
- [ ] Identify primary key field from data-model-context.md Fields section
- [ ] Record List Actions → Place in header OR `recordActions` parameter, NO identifier
- [ ] Related Actions → Place in grid columns, REQUIRE `identifier: fv!row['recordType!Type.fields.primaryKey']`
- [ ] ❌ NEVER put Record List Actions in grid columns
- [ ] ❌ NEVER put Related Actions in header/toolbar without context
- [ ] ❌ NEVER add identifier to Record List Actions
- [ ] ❌ NEVER omit identifier from Related Actions in grid columns

---

## Action Buttons in Grids {#display-actions.buttons}

### Decision Tree for Grid Action Columns {#display-actions.buttons.decision-tree}

When a mockup has an "Actions" column with buttons (View, Edit, Delete, etc.):

```
1. Is this a "View" or "Open" action?
   └─ YES → Convert to a!recordLink() in a grid column (NOT a related action)
   └─ NO → Continue to step 2

2. Is this a "Create" or "New" action?
   └─ YES → Move OUTSIDE the grid (toolbar/header) - doesn't apply to existing rows
   └─ NO → Continue to step 3

3. Check data-model-context.md for Related Actions on the grid's record type
   └─ Related actions FOUND → Match mockup buttons to available actions
   └─ NO related actions → Use placeholder pattern with TODO
```

### View/Open Actions → Use a!recordLink() {#display-actions.buttons.view}

**NEVER use related actions for View/Open.** Convert to `a!recordLink()` in a grid column:

```sail
/* ❌ MOCKUP - View button */
a!buttonWidget(
  label: "View",
  icon: "eye",
  saveInto: {}
)

/* ✅ FUNCTIONAL - recordLink in rich text */
a!gridColumn(
  label: "Application ID",
  value: a!richTextDisplayField(
    labelPosition: "COLLAPSED",
    value: a!richTextItem(
      text: fv!row['recordType!Case.fields.caseNumber'],
      link: a!recordLink(
        recordType: 'recordType!Case',
        identifier: fv!identifier
      ),
      linkStyle: "STANDALONE"
    )
  )
)
```

If the mockup has BOTH a clickable ID column AND a separate View button, remove the View button (redundant).

### Finding Related Actions in Data Model {#display-actions.buttons.finding}

**Step 1: Identify the grid's record type**
```sail
/* From the grid's data parameter */
data: a!recordData(
  recordType: 'recordType!PREREQUISITE_VERIFICATION'  /* ← This record type */
)
```

**Step 2: Search data-model-context.md**

Look for the record type section and find the **Record Actions** table:

```markdown
## CASE

**Record Actions**:

| **Action Name** | **Action Type** | **Action Reference** |
|----------------|-----------------|---------------------|
| createCase (New Case) | Record List | `'recordType!CASE.actions.createCase'` |
| editCase (Edit Case) | Related | `'recordType!CASE.actions.editCase'` |
| closeCase (Close Case) | Related | `'recordType!CASE.actions.closeCase'` |
```

**Action Type determines usage:**
- `Record List` → Header/toolbar only, no identifier
- `Related` → Grid columns only, requires identifier

**Step 3: Match mockup buttons to actions** (see matching table below)

**Step 4: If no actions with Action Type = "Related" exist** → Use placeholder pattern with TODO

### Edit/Delete/Other Actions → Related Actions {#display-actions.buttons.related}

**When Related Actions EXIST → Match and Convert:**

```sail
/* ❌ MOCKUP */
a!gridColumn(
  label: "Actions",
  value: a!buttonArrayLayout(
    buttons: {
      a!buttonWidget(label: "Edit", icon: "pencil", saveInto: {})
    }
  )
)

/* ✅ FUNCTIONAL - Single related action */
a!gridColumn(
  label: "Actions",
  value: a!recordActionField(
    actions: {
      a!recordActionItem(
        action: 'recordType!CASE.actions.editCase',
        identifier: fv!row['recordType!CASE.fields.caseId']
      )
    },
    style: "SIDEBAR",  /* Single action */
    display: "LABEL"
  ),
  width: "NARROW"
)

/* ✅ FUNCTIONAL - Multiple related actions */
a!gridColumn(
  label: "Actions",
  value: a!recordActionField(
    actions: {
      a!recordActionItem(
        action: 'recordType!CASE.actions.editCase',
        identifier: fv!row['recordType!CASE.fields.caseId']
      ),
      a!recordActionItem(
        action: 'recordType!CASE.actions.closeCase',
        identifier: fv!row['recordType!CASE.fields.caseId']
      )
    },
    style: "MENU",  /* Multiple actions */
    display: "LABEL"
  ),
  width: "NARROW"
)
```

**When NO Related Actions in data model → Placeholder with TODO:**

```sail
/* ✅ FUNCTIONAL - No related actions available */
a!gridColumn(
  label: "Actions",
  value: a!recordActionField(
    actions: {},
    style: "MENU"
    /* TODO: Add related actions to record type for: Edit, Delete
     * Once created, add a!recordActionItem() entries with identifier: fv!row['recordType!Type.fields.primaryKey'] */
  ),
  width: "ICON"
)
```

### Action Matching Guidelines {#display-actions.buttons.matching}

| Mockup Button Label | Look For Related Action Named |
|---------------------|-------------------------------|
| Edit, Edit/Resubmit, Update | edit*, update*, modify* |
| Delete, Remove | delete*, remove* |
| Submit, Resubmit | submit*, resubmit* |
| Approve, Reject | approve*, reject*, review* |
| Continue | edit* (for draft records) |

**Matching rules:**
- Case-insensitive matching
- Partial match is acceptable (e.g., "Edit" matches "editApplication")
- If no match found, include unmatched actions in TODO comment

### Create/New Actions → Outside Grid {#display-actions.buttons.create}

Create actions don't apply to existing rows. Place in page header or toolbar:

```sail
/* In header or above grid - NO identifier needed */
a!recordActionField(
  actions: {
    a!recordActionItem(
      action: 'recordType!Type.actions.createApplication'
      /* NO identifier - creates new record */
    )
  },
  style: "TOOLBAR_PRIMARY",
  display: "LABEL_AND_ICON"
)
```

### Style Mapping {#display-actions.buttons.style-mapping}

**Grid Action Column Styles (based on action count):**

| Actions in Column | Style | Rationale |
|-------------------|-------|-----------|
| Single action | `style: "SIDEBAR"` | Opens action in sidebar panel |
| Multiple actions | `style: "MENU"` | Dropdown menu consolidates actions |
| No actions (placeholder) | `style: "MENU"` | Consistent appearance for future actions |

**Toolbar/Header Action Styles:**

| Mockup Button Style | Record Action Style |
|---------------------|---------------------|
| `style: "SOLID", color: "ACCENT"` | `style: "TOOLBAR_PRIMARY"` |
| `style: "SOLID", color: "SECONDARY"` | `style: "TOOLBAR"` |
| `style: "OUTLINE"` | `style: "TOOLBAR"` |
| `style: "LINK"` | `style: "LINKS"` |

### Action Conversion Checklist {#display-actions.buttons.checklist}

- [ ] View/Open buttons converted to `a!recordLink()` (NOT related actions)
- [ ] Create/New buttons moved outside grid (no identifier)
- [ ] Grid's record type identified from `data:` parameter
- [ ] Primary key field identified from `data-model-context.md` Fields section
- [ ] `data-model-context.md` checked for Related Actions section
- [ ] Mockup button labels matched to available related actions
- [ ] Unmatched actions documented in TODO comments
- [ ] All related actions include `identifier: fv!row['recordType!Type.fields.primaryKey']`
- [ ] Action references copied exactly from data model (with UUIDs)

---

## Grid Toolbar Actions {#display-actions.toolbar-actions}

The `recordActions` parameter on `a!gridField()` provides a built-in toolbar for record actions above the grid. This is distinct from row-level actions in columns.

**Decision Matrix: Header vs Grid Toolbar**

| Mockup State | Action |
|--------------|--------|
| **Button in header** | Preserve in header → Convert to `a!recordActionField()` |
| **Button near grid (not in header)** | Move to grid's `recordActions` parameter |
| **No button exists** | Add to grid's `recordActions` parameter |

**🚨 CRITICAL: Preserve mockup UX placement.** If the mockup has a Create/New button in the header, keep it there. The header placement is an intentional UX decision.

**Example 1: Button in Header → Keep in Header**

```sail
/* ❌ MOCKUP - Create button in header */
a!headerContentLayout(
  header: {
    a!sideBySideLayout(
      items: {
        a!sideBySideItem(item: a!richTextDisplayField(...)),
        a!sideBySideItem(
          item: a!buttonArrayLayout(
            buttons: a!buttonWidget(
              label: "New Case",
              icon: "plus",
              style: "SOLID",
              color: "ACCENT",
              saveInto: {}
            )
          ),
          width: "MINIMIZE"
        )
      }
    )
  },
  contents: {
    a!gridField(data: local!data, columns: {...})
  }
)

/* ✅ FUNCTIONAL - Keep action in header, convert to a!recordActionField() */
a!headerContentLayout(
  header: {
    a!sideBySideLayout(
      items: {
        a!sideBySideItem(item: a!richTextDisplayField(...)),
        a!sideBySideItem(
          item: a!recordActionField(
            actions: {
              a!recordActionItem(
                action: 'recordType!CASE.actions.createCase'
                /* NO identifier - creates new record */
              )
            },
            style: "TOOLBAR_PRIMARY",
            display: "LABEL_AND_ICON"
          ),
          width: "MINIMIZE"
        )
      }
    )
  },
  contents: {
    a!gridField(
      data: a!recordData(recordType: 'recordType!CASE'),
      columns: {...},
      /* No recordActions - action is in header */
      refreshAfter: "RECORD_ACTION",
      showSearchBox: true
    )
  }
)
```

**Example 2: No Button in Mockup → Add to Grid Toolbar**

```sail
/* ❌ MOCKUP - No create button exists */
a!headerContentLayout(
  header: {
    a!richTextDisplayField(...)  /* Header has no action button */
  },
  contents: {
    a!gridField(data: local!data, columns: {...})
  }
)

/* ✅ FUNCTIONAL - Add create action to grid's recordActions */
a!headerContentLayout(
  header: {
    a!richTextDisplayField(...)
  },
  contents: {
    a!gridField(
      data: a!recordData(recordType: 'recordType!CASE'),
      columns: {...},
      recordActions: {
        a!recordActionItem(
          action: 'recordType!CASE.actions.createCase'
          /* NO identifier - creates new record */
        )
      },
      refreshAfter: "RECORD_ACTION",
      showSearchBox: true
    )
  }
)
```

---

## refreshAfter Parameter {#display-actions.refresh-after}

**Add `refreshAfter: "RECORD_ACTION"`** when the grid has ANY record actions that modify data:

| Record Actions Location | Add refreshAfter? |
|------------------------|-------------------|
| `recordActions` parameter (toolbar) | ✅ Yes |
| `a!recordActionField()` in column | ✅ Yes |
| `a!recordActionField()` in header | ✅ Yes |
| Both toolbar AND column actions | ✅ Yes |
| No record actions (only recordLinks) | ❌ No |

```sail
a!gridField(
  data: a!recordData(recordType: 'recordType!Case'),
  columns: {
    /* ... other columns ... */
    a!gridColumn(
      label: "Actions",
      value: a!recordActionField(
        actions: {
          a!recordActionItem(
            action: 'recordType!Case.actions.editCase',
            identifier: fv!identifier
          )
        },
        style: "SIDEBAR",
        display: "LABEL"
      )
    )
  },
  refreshAfter: "RECORD_ACTION"  /* Grid refreshes after Edit action completes */
)
```

### Grid Toolbar Action Checklist {#display-actions.toolbar-actions.checklist}

- [ ] Identify Create/New buttons in mockup
- [ ] **If button is in header** → Keep in header, convert to `a!recordActionField()`
- [ ] **If button is near grid (not header)** → Move to `recordActions` parameter
- [ ] **If no button exists** → Add to `recordActions` parameter
- [ ] Add `refreshAfter: "RECORD_ACTION"` when ANY record actions exist (header, toolbar, or column)
- [ ] Remove custom `a!buttonWidget` placeholders after conversion

---

## Action Conversion Checklist {#display-actions.checklist}

**Action Type:**
- [ ] **Action type identified** (Record List Action vs Related Action) from data-model-context.md
- [ ] **Primary key field identified** from data-model-context.md Fields section
- [ ] **Record List Actions** → Header OR `recordActions` parameter, NO identifier
- [ ] **Related Actions** → Grid columns ONLY, REQUIRE `identifier: fv!row['recordType!Type.fields.primaryKey']`
- [ ] ❌ NO Record List Actions in grid columns
- [ ] ❌ NO Related Actions in header/toolbar without record context

**Grid Actions:**
- [ ] Row-level actions converted to `a!recordActionField()` in columns
- [ ] Create/New buttons preserve mockup UX placement (header stays in header)
- [ ] `refreshAfter: "RECORD_ACTION"` added when ANY record actions exist
- [ ] Action references from data-model-context.md (with UUIDs)
