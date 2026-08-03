# Display Conversion - Grid Patterns {#display-grids}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/display-conversion-core.md` - Interface detection and record links
> - `/conversion-guidelines/display-conversion-actions.md` - Grid action buttons and toolbar
> - `/conversion-guidelines/common-conversion-patterns.md` - Query patterns
> - `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

Patterns for converting read-only grids with record data, including sortField rules, search/filter conversion, and related record data.

---

## 📑 Module Navigation {#display-grids.nav}

- `{#display-grids.patterns}` - Basic grid conversion patterns
- `{#display-grids.sortfield-rules}` - Grid column sorting rules
- `{#display-grids.related-data}` - One-to-many relationship data in grids
- `{#display-grids.search-filter}` - Converting custom search/filter UX to built-in features

---

## Grid Patterns {#display-grids.patterns}

### Read-Only Grid with a!recordData()

```sail
a!gridField(
  label: "Active Cases",
  data: a!recordData(
    recordType: 'recordType!Case',
    filters: a!queryLogicalExpression(
      operator: "AND",
      filters: {
        a!queryFilter(
          field: 'recordType!Case.fields.status',
          operator: "=",
          value: "Open"
        )
      }
    )
  ),
  columns: {
    a!gridColumn(
      label: "Case Number",
      value: fv!row['recordType!Case.fields.caseNumber'],
      sortField: 'recordType!Case.fields.caseNumber'
    ),
    a!gridColumn(
      label: "Subject",
      value: fv!row['recordType!Case.fields.subject'],
      sortField: 'recordType!Case.fields.subject'
    ),
    a!gridColumn(
      label: "Status",
      value: fv!row['recordType!Case.fields.status'],
      sortField: 'recordType!Case.fields.status'
    )
  },
  pageSize: 20,
  showSearchBox: true,
  showRefreshButton: true
)
```

### sortField Rules {#display-grids.sortfield-rules}

**🚨 BLOCKING GATE** - sortField MUST end with `.fields.fieldName`

| sortField Pattern | Valid? | Fix |
|-------------------|--------|-----|
| `...fields.fieldName` | ✅ | Direct field - valid |
| `...relationships.rel.fields.fieldName` | ✅ | Related field (many-to-one) - valid |
| `...relationships.rel` | ❌ | Missing field - append `.fields.fieldName` |
| No `.fields.` anywhere | ❌ | Invalid - use proper field path |

**Common mistake:**
```sail
/* ❌ WRONG - Relationship only, no field */
sortField: 'recordType!Case.relationships.status'

/* ✅ CORRECT - Navigate to sortable field */
sortField: 'recordType!Case.relationships.status.fields.statusName'
```

**Computed columns:** If column value uses `if()`, `a!match()`, or `&` (concatenation), omit `sortField`. Only columns displaying raw field values should be sortable. Each field can only be used as sortField once across all grid columns.

### Grid with Related Record Data {#display-grids.related-data}

For grids needing one-to-many relationship data:

```sail
a!gridField(
  data: a!recordData(
    recordType: 'recordType!Case',
    relatedRecordData: {
      a!relatedRecordData(
        relationship: 'recordType!Case.relationships.comments',
        limit: 1,
        sort: a!sortInfo(
          field: 'recordType!Comment.fields.createdOn',
          ascending: false
        )
      )
    }
  ),
  columns: {
    /* Access latest comment through relationship */
    a!gridColumn(
      label: "Latest Comment",
      value: if(
        a!isNotNullOrEmpty(fv!row['recordType!Case.relationships.comments']),
        index(fv!row['recordType!Case.relationships.comments'], 1, null)['recordType!Comment.fields.text'],
        "No comments"
      )
    )
  }
)
```

---

## Grid Search and Filter Conversion {#display-grids.search-filter}

When converting mockups to functional interfaces, replace custom search/filter UX with built-in grid features.

**Detection: Find Custom Search/Filter Sections**

Look for patterns like:
- `local!searchText` with `a!textField` for search
- `local!filterStatus` with `a!dropdownField` for list filters
- `local!filterDateFrom`/`local!filterDateTo` with `a!dateField` pairs for date range filters
- Card sections labeled "Search & Filters" or similar

**🚨 CRITICAL CLARIFICATIONS:**

1. **Field-specific text searches** (e.g., "Search by Organization Name") → Convert to generic `showSearchBox: true`
   - Yes, this loses field specificity
   - Document the change in TODO comment: "Changed from field-specific (organizationName) to generic search"

2. **ALL custom filters for single-grid scenarios must be removed**, even if no user filters exist
   - Don't keep custom filters just because user filters aren't available
   - Remove custom UX and add TODO requesting user filter creation

**Decision Tree: Convert or Keep?**

```
Does the custom filter apply to ONLY ONE grid?
├─ YES → Convert to built-in features (see Decision Matrix below)
│
└─ NO (applies to multiple grids/charts) → Keep custom UX
    └─ These are dashboard-level filters, not grid-specific
```

**Step 1: Inventory Mockup Filters**

List all custom filters in the mockup:
```
Mockup Filters:
- Search (text field)
- Status (dropdown)
- Type (dropdown)
- Date Range (date fields)
```

**Step 2: Inventory Available User Filters**

Check `data-model-context.md` for the record type's User Filters section:
```
Available User Filters:
- Role
- membershipType
- submissionDate
```

**Step 3: Apply Decision Matrix**

| Scenario | Action |
|----------|--------|
| **All mockup filters have matching user filters** | Add all to `userFilters`, remove all custom UX |
| **Some match, some don't** | Add matching filters to `userFilters`, remove ALL custom UX, add TODO listing removed filters and request to create missing user filters |
| **None match but user filters exist** | Add ALL available user filters to `userFilters`, remove ALL custom UX, add TODO listing removed filters and note that available filters were added to demonstrate capability |
| **No user filters exist at all** | Remove custom UX, add TODO requesting user filter creation for all mockup filter needs |

**🚨 CRITICAL: ALWAYS remove custom filter UX for single-grid filters.** Never leave both custom filters AND built-in filters.

**Step 4: Match Mockup Filters to User Filters**

| Mockup Filter Type | Likely User Filter Match |
|--------------------|--------------------------|
| Status dropdown | *status*, *isActive*, *state* |
| Type/Category dropdown | *type*, *category*, *membershipType* |
| Priority dropdown | *priority*, *urgency* |
| Date/Date Range | *Date*, *createdDate*, *submissionDate* |
| Role dropdown | *role*, *Role* |
| Search text field | `showSearchBox: true` (always available) |

**TODO Comment Format**

Use this consistent format for user filter gaps:
```sail
/* TODO: User Filter Conversion
 * - REMOVED from mockup: [list of removed filters with specifics]
 *   - Field-specific text search (organizationName) → Converted to generic showSearchBox
 *   - Date range filters (startDate/endDate) → Need date range user filters
 * - ADDED from available: [list of added filters, or "none" if no user filters exist]
 * - ACTION NEEDED: Create user filters for [list] on [RecordType] record type
 *   - organizationName (text filter)
 *   - startDate/endDate (date range filter) */
```

**Conversion Examples**

**Example 1: All Filters Match**
```sail
/* Mockup had: search, status dropdown, type dropdown
   Available: status, membershipType user filters */

a!gridField(
  data: a!recordData(recordType: 'recordType!Submission'),
  columns: {...},
  showSearchBox: true,
  userFilters: {
    'recordType!Submission.filters.status',
    'recordType!Submission.filters.membershipType'
  }
)
/* Custom filter section REMOVED - all filters converted to built-in */
```

**Example 2: Partial Match**
```sail
/* Mockup had: search, status dropdown, priority dropdown, assignee dropdown
   Available: status, priority user filters (no assignee) */

a!gridField(
  data: a!recordData(recordType: 'recordType!Case'),
  columns: {...},
  showSearchBox: true,
  userFilters: {
    'recordType!Case.filters.status',
    'recordType!Case.filters.priority'
  }
  /* TODO: User Filter Conversion
   * - REMOVED from mockup: assignee filter (no matching user filter)
   * - ADDED from available: status, priority
   * - ACTION NEEDED: Create user filter for 'assignee' on Case record type */
)
/* Custom filter section REMOVED */
```

**Example 3: No Match But Filters Available**
```sail
/* Mockup had: search, department dropdown, location dropdown
   Available: status, createdDate user filters (neither matches mockup) */

a!gridField(
  data: a!recordData(recordType: 'recordType!Employee'),
  columns: {...},
  showSearchBox: true,
  userFilters: {
    'recordType!Employee.filters.status',
    'recordType!Employee.filters.createdDate'
  }
  /* TODO: User Filter Conversion
   * - REMOVED from mockup: department filter, location filter (no matching user filters)
   * - ADDED from available: status, createdDate (demonstrating user filter capability)
   * - ACTION NEEDED: Create user filters for 'department' and 'location' on Employee record type */
)
/* Custom filter section REMOVED */
```

**Example 4: No User Filters Exist**
```sail
/* Mockup had: search, status dropdown, type dropdown
   Available: (none) */

a!gridField(
  data: a!recordData(recordType: 'recordType!NewRecord'),
  columns: {...},
  showSearchBox: true
  /* TODO: User Filter Conversion
   * - REMOVED from mockup: status filter, type filter
   * - ADDED from available: none (no user filters defined for this record type)
   * - ACTION NEEDED: Create user filters for 'status' and 'type' on NewRecord record type */
)
/* Custom filter section REMOVED */
```

**Conversion Checklist**

- [ ] Inventory all custom filters in mockup
- [ ] Check `data-model-context.md` for User Filters section
- [ ] Match mockup filters to available user filters
- [ ] Add `showSearchBox: true` (always)
- [ ] Add ALL matching user filters to `userFilters` array
- [ ] Add ALL non-matching available user filters (if any exist)
- [ ] Remove ALL custom filter components
- [ ] Remove "Search & Filters" card section
- [ ] Field-specific text searches converted to `showSearchBox: true` (generic)
- [ ] TODO comment documents loss of field specificity with traceability
- [ ] Add TODO comment with consistent format documenting:
  - [ ] Which mockup filters were removed
  - [ ] Which available filters were added
  - [ ] Request to create missing user filters
- [ ] For dashboard-level filters: Keep custom UX, ensure filters are wired to all components
- [ ] Verify no duplicate search/filter UX remains

---

## Grid Conversion Checklist {#display-grids.checklist}

**Grids:**
- [ ] All sortField values end with `.fields.fieldName`
- [ ] No sortField references relationship without field
- [ ] One-to-many relationships use `a!relatedRecordData()`
- [ ] Grid columns use `fv!row` (not `fv!index` or `fv!item`)
- [ ] `showSearchBox: true` added to grids with `a!recordData()`
- [ ] Custom search/filter UX removed for single-grid filters
- [ ] `userFilters` added where available in data-model-context.md
- [ ] TODO comments added for missing user filters
- [ ] No duplicate search/filter UX (custom + built-in)
