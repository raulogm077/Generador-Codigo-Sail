# Validation Enforcement Module {#validation-module}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - **Form modules:** `/conversion-guidelines/form-conversion-module.md` (navigation index)
>   - Focused modules: `form-conversion-ri-patterns.md`, `form-conversion-relationships.md`, `form-conversion-buttons-actions.md`, `form-conversion-data-model.md`
> - **Display modules:** `/conversion-guidelines/display-conversion-module.md` (navigation index)
>   - Focused modules: `display-conversion-core.md`, `display-conversion-grids.md`, `display-conversion-charts.md`, `display-conversion-kpis.md`, `display-conversion-actions.md`
> - **Common modules:** `/conversion-guidelines/common-conversion-patterns.md` (navigation index)
>   - Focused modules: `conversion-queries.md`, `conversion-relationships.md`, `conversion-field-mapping.md`
>
> **Null safety details:** `/logic-guidelines/null-safety-quick-ref.md`

Post-conversion validation and cleanup steps. **Always executed** regardless of interface type. These steps ensure code quality before output.

---

## 📑 Module Navigation {#validation.nav}

- `{#validation.unused-variables}` - Detect and remove/document unused variables
  - `{#validation.unused-variables.decision}` - Removal vs documentation decision tree
  - `{#validation.unused-variables.template}` - UNUSED comment template
  - `{#validation.unused-variables.categories}` - Categories with examples
  - `{#validation.unused-variables.performance}` - Performance warning rules
- `{#validation.null-safety}` - Enforce null safety patterns
- `{#validation.type-matching}` - Verify query filter type compatibility
- `{#validation.query-result-handling}` - Handle empty query results (DataSubset)
  - `{#validation.query-result-handling.multiple}` - Multiple records pattern
  - `{#validation.query-result-handling.single}` - Single record pattern
  - `{#validation.query-result-handling.checklist}` - Query result checklist
- `{#validation.pre-flight-checklist}` - Final validation before output
- `{#validation.critical-errors}` - Critical errors quick reference table

---

## Unused Variable Detection {#validation.unused-variables}

### Purpose

Mockups often have unused variables that should not carry forward to functional interfaces. Unused variables cause confusion, trigger Appian Designer warnings, and violate best practices.

### Automated Detection {#validation.unused-variables.detection}

Run this command to find all local variables and their occurrence counts:

```bash
grep -o 'local![a-zA-Z_]*' output/[filename].sail | sort | uniq -c | sort -rn
```

**Example output:**
```
  12 local!viewMode
   9 local!selectedSubmissionIds
   8 local!submissionsQuery
   1 local!dateRangeFilter          ← UNUSED (count = 1)
   1 local!selectedSubmissions      ← UNUSED (count = 1)
```

**Interpretation:** Variables with count = 1 appear ONLY in their declaration → **UNUSED**

### Removal vs Documentation Decision {#validation.unused-variables.decision}

**Decision Tree:**
```
Is the variable unused?
├─ YES → Is there a clear future use?
│   ├─ YES → Document with UNUSED comment (see template below)
│   └─ NO → REMOVE IT
└─ NO → No action needed
```

| Scenario | Action |
|----------|--------|
| No clear future use | **REMOVE** - Delete the variable declaration entirely |
| Documented future use | **KEEP** - Add UNUSED comment template |

**Quick Reference:**

| Keep & Document | Remove Immediately |
|-----------------|-------------------|
| ✅ Planned features | ❌ Debug/test code |
| ✅ Deferred work | ❌ Dead refactors |
| ✅ Alternative logic (with reason) | ❌ No clear purpose |
| ✅ Awaiting config system | ❌ Duplicate functionality |

**Common Mockup Variables to REMOVE:**
- Filter variables that weren't implemented (`local!dateRangeFilter`)
- UI state variables not needed (`local!showAdvanced`)
- Computed variables never referenced (`local!selectedSubmissions`)
- Placeholder variables from templates

### UNUSED Comment Template {#validation.unused-variables.template}

**One-Line Format:**
```sail
/* UNUSED - [Name] ([Category]): [Why not used] | [Future use or decision] */
local!variable: value,
```

### Categories & Examples {#validation.unused-variables.categories}

**Future Enhancement** - Feature planned but not built yet
```sail
/* UNUSED - caseTypes (Future): Text field used; picker planned for Phase 2 case type management */
local!caseTypes: a!queryRecordType('recordType!{...}Case Type', ...).data,
```

**Deferred** - Feature postponed
```sail
/* UNUSED - advancedFilters (Deferred): Phase 1 basic search only per ticket #1234 */
local!showAdvancedFilters: false,
local!filterDateRange,
```

**Alternative** - Different approach available
```sail
/* UNUSED - weightedSLA (Alternative): Client chose flat SLA over priority-weighted */
local!weightedSLA: sum(a!forEach(local!cases, expression: fv!item.hours * fv!item.weight)),
```

**Config** - Waiting for configuration system
```sail
/* UNUSED - pageSize (Config): User preferences not implemented; using default 25 */
local!userPageSize: 50,
```

**Requirements Changed** - Was needed, temporarily disabled
```sail
/* UNUSED - emailValidation (ReqChanged): Disabled for 60-day migration period */
/* NOTE: Use pattern from /logic-guidelines/functions-reference.md#email-validation-pattern */
local!isValidEmail: false(),
```

### Performance Warning {#validation.unused-variables.performance}

Add performance note if query >0.5s or >500 records:

```sail
/* UNUSED - allCases (Future): Pre-load for export feature | 5000 records, 3s load */
local!allCases: a!queryRecordType(..., batchSize: 5000).data,
```

**Rule**: If >1s and no near-term use → REMOVE

### Re-Verification {#validation.unused-variables.reverification}

After removing unused variables:

```bash
grep -o 'local![a-zA-Z_]*' output/[filename].sail | sort | uniq -c | sort -rn
```

**Pass criteria:** ALL variables must have count ≥ 2 (or have UNUSED comment)

**🛑 BLOCKING:** Cannot proceed to null safety enforcement until:
- [ ] Bash verification shows NO variables with count = 1 (except documented)
- [ ] Cleanup documented in conversion summary

---

## Null Safety Enforcement {#validation.null-safety}

### Purpose

Null reference errors cause **complete interface failures**. Users see error pages instead of functional interfaces. There is no graceful degradation.

### Automated Detection Commands {#validation.null-safety.detection}

Run ALL of these commands to find potentially vulnerable patterns:

```bash
# Find all text() calls - may crash on null
grep -n "text(" output/[filename].sail > /tmp/null_check_text.txt
echo "Found $(wc -l < /tmp/null_check_text.txt) text() calls"

# Find all user() calls - crashes on null user reference
grep -n "user(" output/[filename].sail > /tmp/null_check_user.txt
echo "Found $(wc -l < /tmp/null_check_user.txt) user() calls"

# Find all string concatenations with &
grep -n " & " output/[filename].sail > /tmp/null_check_concat.txt
echo "Found $(wc -l < /tmp/null_check_concat.txt) concatenation instances"

# Find all todate() calls on fields - may crash on null
grep -n "todate(fv!row\|todate(ri!" output/[filename].sail > /tmp/null_check_todate.txt
echo "Found $(wc -l < /tmp/null_check_todate.txt) todate() calls on fields"

# Find all queryFilters (check for applyWhen)
grep -n "a!queryFilter(" output/[filename].sail > /tmp/null_check_filters.txt
echo "Found $(wc -l < /tmp/null_check_filters.txt) queryFilter instances"

# Find all dropdownField instances
grep -n "a!dropdownField(" output/[filename].sail > /tmp/null_check_dropdown.txt
echo "Found $(wc -l < /tmp/null_check_dropdown.txt) dropdownField instances"
```

### Context-Aware Review {#validation.null-safety.review}

**CRITICAL:** Not all field references need null safety. Distinguish between:

| Context | Null Safety Required? |
|---------|----------------------|
| Display contexts (grid columns, richText, read-only fields) | ✅ YES |
| Editable input contexts (form field `value`/`saveInto`) | ❌ NO |
| Choice parameters (dropdown `choiceLabels`/`choiceValues`) | ✅ YES |

### Review text() Calls {#validation.null-safety.review-text}

For each text() call in `/tmp/null_check_text.txt`:

- [ ] **SKIP** if inside form input component (textField.value, dateField.value, etc.)
- [ ] For display contexts: Verify wrapped in `if(a!isNotNullOrEmpty(...), text(...), "N/A")`
- [ ] If NOT wrapped → Mark for correction

**Document:** "Reviewed [N] text() calls, [M] in display contexts, [P] need protection"

### Review user() Calls {#validation.null-safety.review-user}

For each user() call in `/tmp/null_check_user.txt`:

- [ ] **SKIP** if showing current user (auto-populated fields using `loggedInUser()`)
- [ ] For display contexts: Verify wrapped in `if(a!isNotNullOrEmpty(...), user(...), "N/A")`
- [ ] If NOT wrapped → Mark for correction
- [ ] **Verify property parameter uses firstName + lastName pattern:**
  - [ ] ❌ WRONG: `user(userId, "displayName")` - displayName is a nickname field and often empty
  - [ ] ✅ RIGHT: `trim(user(userId, "firstName") & " " & user(userId, "lastName"))`
  - [ ] If using displayName → Mark for correction to firstName + lastName pattern

### Review Concatenations {#validation.null-safety.review-concat}

For each `&` concatenation in `/tmp/null_check_concat.txt`:

- [ ] **SKIP** if inside form input value/saveInto
- [ ] For display contexts:
  - If concatenating with text(): Verify if() wrapping with "N/A" fallback
  - If concatenating without text(): Verify `a!defaultValue(field, "")` wrapping

### Review Date Operations {#validation.null-safety.review-todate}

For each todate() call in `/tmp/null_check_todate.txt`:

- [ ] **SKIP** if inside form dateField.value
- [ ] For display contexts:
  - If used in arithmetic: Verify wrapped in if() before arithmetic
  - If used in comparison: Verify nested if() pattern for short-circuit

### Review Query Filters {#validation.null-safety.review-filters}

For each a!queryFilter() in `/tmp/null_check_filters.txt`:

- [ ] For filters with **variable values**: Verify has `applyWhen: a!isNotNullOrEmpty(variable)`
- [ ] For filters with **constants/functions**: No applyWhen needed
- [ ] **NO SKIPPING** - all queryFilters with variables need applyWhen

#### Common applyWhen Missing Patterns {#validation.null-safety.common-applywhen}

**These are the most frequent sources of runtime errors. Check EVERY queryFilter for these patterns:**

**Pattern 1: Missing applyWhen on ri! variable (Record ID filtering)**
```sail
/* ❌ WRONG - Missing applyWhen with ri! variable */
a!queryFilter(
  field: 'recordType!Case.fields.id',
  operator: "=",
  value: ri!recordId  /* Variable without applyWhen causes runtime error if null! */
)

/* ✅ CORRECT - Has applyWhen */
a!queryFilter(
  field: 'recordType!Case.fields.id',
  operator: "=",
  value: ri!recordId,
  applyWhen: a!isNotNullOrEmpty(ri!recordId)
)
```

**Pattern 2: Missing applyWhen on local! filter variable**
```sail
/* ❌ WRONG - Missing applyWhen with local! variable */
a!queryFilter(
  field: 'recordType!Case.fields.status',
  operator: "=",
  value: local!selectedStatus  /* Variable without applyWhen causes runtime error if null! */
)

/* ✅ CORRECT - Has applyWhen */
a!queryFilter(
  field: 'recordType!Case.fields.status',
  operator: "=",
  value: local!selectedStatus,
  applyWhen: a!isNotNullOrEmpty(local!selectedStatus)
)
```

**Pattern 3: Missing applyWhen on record field reference**
```sail
/* ❌ WRONG - Missing applyWhen with record field */
a!queryFilter(
  field: 'recordType!Document.fields.caseId',
  operator: "=",
  value: ri!case['recordType!Case.fields.caseId']  /* Field reference without applyWhen! */
)

/* ✅ CORRECT - Has applyWhen */
a!queryFilter(
  field: 'recordType!Document.fields.caseId',
  operator: "=",
  value: ri!case['recordType!Case.fields.caseId'],
  applyWhen: a!isNotNullOrEmpty(ri!case['recordType!Case.fields.caseId'])
)
```

**Rule**: ANY filter where `value` parameter uses `ri!` or `local!` MUST have `applyWhen: a!isNotNullOrEmpty()`. No exceptions.

### Review Dropdown Fields {#validation.null-safety.review-dropdown}

For each a!dropdownField() in `/tmp/null_check_dropdown.txt`:

- [ ] `choiceLabels`: Has `if(a!isNotNullOrEmpty(queryResult), queryResult['field'], {})`
- [ ] `choiceValues`: Has `if(a!isNotNullOrEmpty(queryResult), queryResult['field'], {})`
- [ ] `value`: Direct field binding (NO null check needed)
- [ ] `saveInto`: Direct field binding (NO null check needed)

### Correction Patterns {#validation.null-safety.correction}

**Correcting text() calls:**
```sail
/* ❌ BEFORE */
text: text(fv!row['recordType!...field'], "0000")

/* ✅ AFTER */
text: if(
  a!isNotNullOrEmpty(fv!row['recordType!...field']),
  text(fv!row['recordType!...field'], "0000"),
  "N/A"
)
```

**Correcting user() calls:**
```sail
/* ❌ BEFORE */
text: user(fv!row['recordType!...userId'], "username")

/* ✅ AFTER */
text: if(
  a!isNotNullOrEmpty(fv!row['recordType!...userId']),
  user(fv!row['recordType!...userId'], "username"),
  "N/A"
)
```

**Correcting concatenation with text():**
```sail
/* ❌ BEFORE */
text: "ID-" & text(field, "0000")

/* ✅ AFTER */
text: "ID-" & if(
  a!isNotNullOrEmpty(field),
  text(field, "0000"),
  "N/A"
)
```

**Correcting date arithmetic:**
```sail
/* ❌ BEFORE */
todate(fv!row['recordType!...startDate'] + 30)

/* ✅ AFTER */
if(
  a!isNotNullOrEmpty(fv!row['recordType!...startDate']),
  todate(fv!row['recordType!...startDate'] + 30),
  null
)
```

**Correcting date comparisons (nested if for short-circuit):**
```sail
/* ❌ BEFORE */
color: if(
  todate(fv!row['recordType!...date'] + 30) < today(),
  "#DC2626",
  "STANDARD"
)

/* ✅ AFTER */
color: if(
  if(
    a!isNotNullOrEmpty(fv!row['recordType!...date']),
    todate(fv!row['recordType!...date'] + 30) < today(),
    false
  ),
  "#DC2626",
  "STANDARD"
)
```

**Correcting a!queryFilter:**
```sail
/* ❌ BEFORE */
a!queryFilter(
  field: 'recordType!X.fields.name',
  operator: "includes",
  value: local!searchText
)

/* ✅ AFTER */
a!queryFilter(
  field: 'recordType!X.fields.name',
  operator: "includes",
  value: local!searchText,
  applyWhen: a!isNotNullOrEmpty(local!searchText)
)
```

**Correcting form inputs (REMOVE over-defensive null checks):**

For editable form input components:
- [ ] Remove `a!defaultValue()` wrapper from `value` parameter
- [ ] Remove `if(a!isNotNullOrEmpty(ri!))` wrapper from `saveInto`
- [ ] Simplify cross-field validations
- [ ] KEEP null checks for `choiceLabels`/`choiceValues` (query results)

### Re-Verification {#validation.null-safety.reverification}

After applying corrections, re-run detection:

```bash
# Re-run all detection commands
grep -n "text(" output/[filename].sail > /tmp/null_check_text_v2.txt
grep -n "user(" output/[filename].sail > /tmp/null_check_user_v2.txt
# ... etc

# Manually review each instance
# Verify ALL match protected patterns
```

**Document summary:**
```
Null Safety Enforcement Summary:
- Protected [N] text() calls (all verified)
- Protected [M] user() calls (all verified)
- Protected [P] concatenations (all verified)
- Protected [Q] todate() calls (all verified)
- Added applyWhen to [R] queryFilters (all verified)
- Total corrections: [N+M+P+Q+R]
```

**🛑 BLOCKING:** Cannot proceed to type matching until:
- [ ] All detection commands executed and counts documented
- [ ] Manual review completed for ALL instances found
- [ ] All corrections applied using patterns above
- [ ] Re-verification confirms 100% pattern compliance

---

## Query Filter Type Matching {#validation.type-matching}

### Purpose

Field type in `a!queryFilter()` MUST match value type. Mismatches cause runtime errors.

### Automated Detection System {#validation.type-matching.detection}

**Step 1: Extract all queryFilter instances**

```bash
# Extract filters with line numbers and context
grep -n -A 3 "a!queryFilter(" output/[filename].sail > /tmp/all_filters.txt
echo "Found $(grep -c "a!queryFilter(" output/[filename].sail) filters to validate"
```

**Step 2: Detect Date function usage in filters**

```bash
# Find filters using Date-returning functions
grep -n "a!queryFilter(" output/[filename].sail | \
  grep -E "(today|todate|date\(|datevalue|eomonth|edate)" \
  > /tmp/date_function_filters.txt

echo "Found $(wc -l < /tmp/date_function_filters.txt) filters using Date functions"
cat /tmp/date_function_filters.txt
```

**Step 3: Detect DateTime function usage in filters**

```bash
# Find filters using DateTime-returning functions
grep -n "a!queryFilter(" output/[filename].sail | \
  grep -E "(now\(\)|todatetime|datetime\(|subtractDateTime|addDateTime|userdatetime)" \
  > /tmp/datetime_function_filters.txt

echo "Found $(wc -l < /tmp/datetime_function_filters.txt) filters using DateTime functions"
cat /tmp/datetime_function_filters.txt
```

**Step 4: Manual field type verification**

For each filter found in Steps 2-3:

1. **Extract field UUID** from the filter
2. **Look up field type** in `data-model-context.md`:
   - Search for field UUID
   - Find "Data Type" column value
3. **Apply correction if mismatched:**

| Filter Uses | Field Type in data-model-context.md | Action |
|-------------|-------------------------------------|--------|
| Date function (today, eomonth, edate, etc.) | **Date and Time** (DateTime) | ❌ MISMATCH - Wrap value in `todatetime()` |
| Date function | **Date** | ✅ OK - No change |
| DateTime function (now, a!addDateTime, etc.) | **Date** | ❌ MISMATCH - Wrap value in `todate()` |
| DateTime function | **Date and Time** (DateTime) | ✅ OK - No change |

### Correction Patterns {#validation.type-matching.corrections}

**Pattern A: Date function → DateTime field (Most Common)**

```sail
/* ❌ BEFORE - Runtime error */
a!queryFilter(
  field: 'recordType!X.fields.submissionDate',  /* DateTime field */
  operator: ">=",
  value: eomonth(today(), -1) + 1  /* Returns Date */
)

/* ✅ AFTER - Wrap entire expression in todatetime() */
a!queryFilter(
  field: 'recordType!X.fields.submissionDate',  /* DateTime field */
  operator: ">=",
  value: todatetime(eomonth(today(), -1) + 1)  /* Now returns DateTime */
)
```

**Pattern B: DateTime function → Date field (Less Common)**

```sail
/* ❌ BEFORE - Runtime error */
a!queryFilter(
  field: 'recordType!X.fields.dueDate',  /* Date field */
  operator: ">=",
  value: a!subtractDateTime(startDateTime: now(), days: 30)  /* Returns DateTime */
)

/* ✅ AFTER - Wrap entire expression in todate() */
a!queryFilter(
  field: 'recordType!X.fields.dueDate',  /* Date field */
  operator: ">=",
  value: todate(a!subtractDateTime(startDateTime: now(), days: 30))  /* Now returns Date */
)
```

**Pattern C: Local variable type tracing**

```sail
/* Variable declaration */
local!filterDate: eomonth(today(), -1),  /* ← Type: Date (from eomonth return type) */

/* Later in filter */
a!queryFilter(
  field: '...createdOn',  /* DateTime field from data-model-context.md */
  operator: ">=",
  value: local!filterDate  /* ← Type: Date (traced from declaration) - MISMATCH! */
)

/* FIX: Wrap variable reference in todatetime() */
a!queryFilter(
  field: '...createdOn',  /* DateTime field */
  operator: ">=",
  value: todatetime(local!filterDate)  /* ✅ Now returns DateTime */
)
```

### Type Compatibility Reference {#validation.type-matching.reference}

**Quick lookup - Full matrix in `/logic-guidelines/datetime-handling.md#datetime.type-detection`**

| Field Type | Compatible Functions | Incompatible Functions |
|------------|---------------------|------------------------|
| **Date** | today(), todate(), date(), eomonth(), edate() | now(), todatetime(), a!subtractDateTime(), a!addDateTime() |
| **DateTime** | now(), todatetime(), datetime(), a!subtractDateTime(), a!addDateTime() | today(), todate(), eomonth(), edate() |
| **Text** | Text literals, concat(), tostring() | Numbers, Dates, Booleans |
| **Integer/Decimal** | Numeric literals, tointeger(), todecimal() | Text, Dates, Booleans |
| **Boolean** | true(), false() | "true" (text), 1 (integer) |
| **User** | loggedInUser(), touser() | "username" (plain text) |

### Validation Checklist {#validation.type-matching.checklist}

- [ ] **Step 1:** Run automated detection commands (Steps 1-3 above)
- [ ] **Step 2:** For each detected filter:
  - [ ] Extract field UUID
  - [ ] Look up field type in data-model-context.md
  - [ ] Determine function return type (use tables above)
  - [ ] If mismatch → Apply correction pattern
- [ ] **Step 3:** Document corrections in conversion summary
- [ ] **Step 4:** Re-run detection to confirm all mismatches resolved

**🛑 BLOCKING:** Cannot proceed until ALL detected filters verified and corrected.

---

## Query Result Handling {#validation.query-result-handling}

### DataSubset Structure

`a!queryRecordType()` returns a **DataSubset** type with these properties:

| Property | Type | When No Results |
|----------|------|-----------------|
| `startIndex` | Integer | Value from pagingInfo |
| `batchSize` | Integer | Value from pagingInfo |
| `totalCount` | Integer | `0` (if `fetchTotalCount: true`) |
| `data` | List of [Record Type] | **empty list** (e.g., empty `List of Case`) |
| `identifiers` | List of Any Type | **empty list** |

**Critical:** When no records match the query, the `data` property is an **empty list** of the queried record type. Always check before iterating or indexing.

### Pattern A: Multiple Records (Lists, Grids, ForEach) {#validation.query-result-handling.multiple}

When displaying multiple records, use the full `.data` list:

```sail
/* Query returns DataSubset */
local!casesQuery: a!queryRecordType(
  recordType: 'recordType!Case',
  fields: {
    'recordType!Case.fields.caseId',
    'recordType!Case.fields.title',
    'recordType!Case.fields.status'
  },
  filters: a!queryFilter(
    field: 'recordType!Case.fields.status',
    operator: "=",
    value: local!selectedStatus,
    applyWhen: a!isNotNullOrEmpty(local!selectedStatus)
  ),
  pagingInfo: a!pagingInfo(startIndex: 1, batchSize: 100),
  fetchTotalCount: true
),

/* Use .data directly - it's a List of Case (or empty list if no results) */
local!cases: local!casesQuery.data,

/* In UI: Check for empty list before rendering */
if(
  a!isNullOrEmpty(local!cases),
  /* Empty state */
  a!richTextDisplayField(
    labelPosition: "COLLAPSED",
    value: a!richTextItem(
      text: "No cases found.",
      color: "SECONDARY"
    )
  ),
  /* Display all records */
  a!forEach(
    items: local!cases,
    expression: a!cardLayout(
      contents: {
        a!richTextDisplayField(
          labelPosition: "COLLAPSED",
          value: a!richTextItem(
            text: fv!item['recordType!Case.fields.title'],
            style: "STRONG"
          )
        )
      }
    )
  )
)
```

### Pattern B: Single Record (Detail Views) {#validation.query-result-handling.single}

When fetching a single record by ID, extract the first element:

```sail
/* Query for single record */
local!caseQuery: a!queryRecordType(
  recordType: 'recordType!Case',
  fields: {
    'recordType!Case.fields.caseId',
    'recordType!Case.fields.title',
    'recordType!Case.fields.status',
    'recordType!Case.fields.description'
  },
  filters: a!queryFilter(
    field: 'recordType!Case.fields.caseId',
    operator: "=",
    value: ri!caseId,
    applyWhen: a!isNotNullOrEmpty(ri!caseId)
  ),
  pagingInfo: a!pagingInfo(startIndex: 1, batchSize: 1),
  fetchTotalCount: true
),

/* Extract single record - MUST check .data before indexing */
local!case: if(
  a!isNotNullOrEmpty(local!caseQuery.data),
  local!caseQuery.data[1],
  null
),

/* In UI: Check extracted record before rendering */
if(
  a!isNullOrEmpty(local!case),
  /* Empty state - record not found */
  a!richTextDisplayField(
    labelPosition: "COLLAPSED",
    value: a!richTextItem(
      text: "Case not found.",
      color: "SECONDARY"
    )
  ),
  /* Display record details */
  a!sectionLayout(
    label: local!case['recordType!Case.fields.title'],
    contents: {
      a!richTextDisplayField(
        label: "Status",
        value: local!case['recordType!Case.fields.status']
      ),
      a!richTextDisplayField(
        label: "Description",
        value: local!case['recordType!Case.fields.description']
      )
    }
  )
)
```

### Why Empty Check Matters

```sail
/* ❌ CRASHES - Cannot index into empty list */
local!case: local!caseQuery.data[1]

/* When query returns no results:
 *   local!caseQuery.data = {} (empty List of Case)
 *   {}[1] = ERROR - index out of bounds
 */
```

### Two-Level Protection

| Level | What It Protects | Pattern |
|-------|------------------|---------|
| **Query filter** | Prevents invalid query execution | `applyWhen: a!isNotNullOrEmpty(ri!caseId)` |
| **Result handling** | Prevents indexing/iterating empty list | `if(a!isNotNullOrEmpty(query.data), ..., null)` |
| **UI rendering** | Shows appropriate empty state | `if(a!isNullOrEmpty(local!case), emptyState, normalUI)` |

### Query Result Handling Checklist {#validation.query-result-handling.checklist}

For each `a!queryRecordType()`:

- [ ] Filter on ri!/local! uses `applyWhen: a!isNotNullOrEmpty(...)`
- [ ] **Single record:** Checks `a!isNotNullOrEmpty(query.data)` before `query.data[1]`
- [ ] **Multiple records:** Checks `a!isNullOrEmpty(query.data)` before iterating
- [ ] UI shows appropriate empty state when no records found

---

## Pre-Flight Checklist {#validation.pre-flight-checklist}

**🚨 MANDATORY** - Complete ALL items before writing output file.

### Source Reading Verification {#validation.pre-flight.reading}

- [ ] Did I read the mockup file from `/output/`?
- [ ] Did I detect interface type and load correct module(s)?
- [ ] Did I read `data-model-context.md` for record types?
- [ ] Did I read `/ui-guidelines/reference/sail-api-schema.json` (the master INDEX) to route, then the relevant per-category schemas in `/ui-guidelines/reference/schemas/*.json` for actual parameters? (The master index has no parameters — only the category files do.)

### Data Model Verification {#validation.pre-flight.data-model}

- [ ] All relationships validated against `data-model-context.md`
- [ ] All target record types identified (or marked missing)
- [ ] All field access validated (or alternatives documented)
- [ ] All assumptions documented with ASSUMPTION comments
- [ ] All missing data documented with TODO comments

### Implementation Verification {#validation.pre-flight.implementation}

- [ ] All mock data replaced with queries
- [ ] All mandatory refactoring applied (nested if → a!match, charts → data+config)
- [ ] All visual design preserved (colors, spacing, heights, widths)
- [ ] All decisions documented in code comments
- [ ] Record type constructors used (not a!map) where creating/updating

### Form Interface Verification (if applicable) {#validation.pre-flight.form}

- [ ] **🚨 MANDATORY RULE INPUTS (all 3 required):**
  - [ ] `ri!{recordName}` - The record being created/updated
  - [ ] `ri!isUpdate` - Boolean flag (true=update, false=create)
  - [ ] `ri!cancel` - Boolean flag for cancellation signaling
- [ ] **DO NOT derive mode from field checks** - Use `ri!isUpdate` directly
- [ ] **REMOVE delete buttons** - Deletion handled from list views, not forms
- [ ] Used structured RULE INPUTS comment format with ALL 3 inputs documented
- [ ] Each rule input has Name/Type/Description
- [ ] Form fields bind to `ri!recordName[...]`, NOT local variables
- [ ] Create button: `showWhen: not(a!defaultValue(ri!isUpdate, false()))` with null safety, sets ALL 4 audit fields
- [ ] Update button: `showWhen: a!defaultValue(ri!isUpdate, false())` with null safety, sets only modifiedBy/modifiedOn
- [ ] Cancel button: `submit: true, validate: false, saveInto: a!save(ri!cancel, true)`
- [ ] **RUN full form checklist:** `form-conversion-module.md {#form.checklist}`

### Validation Enforcement Verification {#validation.pre-flight.validation}

- [ ] Unused variable detection run (bash verification output)
- [ ] All unused variables removed or documented
- [ ] Null safety detection run (all 5+ commands)
- [ ] All null safety corrections applied
- [ ] Re-verification confirms 100% compliance
- [ ] Query filter type matching (AUTOMATED DETECTION REQUIRED):
  - [ ] Ran Date function detection: `grep -n "a!queryFilter(" ... | grep -E "(today|eomonth|edate|todate|date\(|datevalue)"`
  - [ ] Ran DateTime function detection: `grep -n "a!queryFilter(" ... | grep -E "(now|todatetime|datetime\(|subtractDateTime|addDateTime)"`
  - [ ] Verified ALL detected filters against field types in data-model-context.md
  - [ ] Applied corrections using patterns from {#validation.type-matching.corrections}
  - [ ] Re-verified: ZERO mismatches remain

### Query Construction Validation {#validation.pre-flight.queries}

- [ ] NO `a!recordData()` stored in local variables - only used directly in grid/chart data parameters ‼️
- [ ] KPIs use `a!queryRecordType()` with `a!aggregationFields()`, NOT derived from grid data ‼️
- [ ] Related KPIs (same grouping dimension) use single grouped query with dot notation extraction ‼️
- [ ] Unrelated KPIs (different filters) use separate dedicated queries ‼️
- [ ] All `a!queryRecordType()` calls include `pagingInfo`; `fetchTotalCount: true` present when (and only when) `.totalCount` is read ‼️
- [ ] Single-record-by-id fetches use `a!queryRecordByIdentifier()` instead of a!queryRecordType + PK filter ‼️
- [ ] Aggregation result extraction includes null safety checks (`a!isNotNullOrEmpty()` on `.data`) ‼️
- [ ] Grouped aggregation value extraction checks if value exists before indexing (`contains()` check) ‼️

### Visual Design Preservation Validation {#validation.pre-flight.ux-preservation}

- [ ] ALL layout structures preserved from mockup (sideBySideLayout, columnsLayout, cardLayout, sectionLayout, etc.) ‼️
- [ ] ALL visual components preserved (stampField, gaugeField, progressBarField, tagField, richTextIcon, etc.) ‼️
- [ ] ALL styling parameters preserved (colors, spacing, padding, margins, heights, widths, shape, showBorder, style) ‼️
- [ ] ALL text content preserved (labels, descriptions, helper text with exact wording and formatting) ‼️
- [ ] NO component type changes (richText → textField, card → section, stamp → icon) ‼️
- [ ] NO layout simplifications (removing sideBySideLayout, nested cards, columns) ‼️
- [ ] NO removal of decorative components (stamps, gauges, icons, tags) ‼️
- [ ] ONLY data sources transformed (local! → queries, hardcoded → record fields, computed → aggregations) ‼️
- [ ] Logic cleanup applied (unused variables, redundant if() statements, verbose expressions) ‼️
- [ ] Layout/visual structures NOT cleaned up (these are UX, not logic) ‼️

### Query Result Safety {#validation.pre-flight.query-results}

- [ ] Single-record extractions check `.data` is not empty before indexing with `[1]`
- [ ] Multi-record displays check `.data` for empty before iterating
- [ ] UI shows appropriate empty state when no records found
- [ ] Query filters with ri!/local! values have `applyWhen` protection

**Reference:** See `{#validation.query-result-handling}` for complete patterns.

### Action Conversion Verification (if applicable) {#validation.pre-flight.actions}

- [ ] Action buttons converted to `a!recordActionField()` where available
- [ ] Related Actions have `identifier` parameter
- [ ] `a!dynamicLink()` converted to `a!recordLink()` for navigation

### Universal SAIL Validation {#validation.pre-flight.universal}

- [ ] Starts with `a!localVariables()`
- [ ] All braces/parentheses matched
- [ ] All strings in double quotes, escaped with `""` not `\"`
- [ ] Comments use `/* */` not `//`
- [ ] Uses `and()`, `or()`, `not()` functions NOT operators
- [ ] No nested sideBySideLayouts
- [ ] At least one AUTO width column in each columnsLayout
- [ ] Grid columns use `fv!row` (NOT fv!index, NOT fv!item)
- [ ] Grid sortField: No sortField on computed columns (if/a!match/concat in value) ‼️
- [ ] Grid sortField: Each field used as sortField only ONCE across all grid columns ‼️
- [ ] Variables declared in dependency order (no forward references)
- [ ] `fetchTotalCount: true` present on exactly the `a!queryRecordType()` calls whose result `.totalCount` is read (not on the rest)

### Dropdown "All" Option Validation {#validation.pre-flight.dropdown-all}

For EACH dropdownField with "All/Any" filter option:
- [ ] ❌ VERIFY: choiceLabels does NOT use `append()` with query data
- [ ] ❌ VERIFY: choiceValues does NOT use `append()` with query data
- [ ] ✅ VERIFY: Uses `placeholder: "All..."` parameter instead
- [ ] ✅ VERIFY: Filter variable is uninitialized (not set to "All")
- [ ] ✅ VERIFY: Filter applyWhen uses `a!isNotNullOrEmpty()` (not `<> "All"`)

### Variable Declaration Order {#validation.pre-flight.variable-order}

- [ ] All local variables declared in dependency order
- [ ] Variables with no dependencies declared first
- [ ] Variables that reference other `local!` variables declared AFTER their dependencies
- [ ] No forward references (using a variable before it's declared)

**Common patterns requiring reordering:**
1. Date range filters: `local!selectedOption` BEFORE `local!computedDate: a!match(value: local!selectedOption)`
2. Query filters: `local!filterValue` BEFORE `local!query: a!queryRecordType(...filter: local!filterValue)`
3. Computed from queries: `local!queryResult` BEFORE `local!displayData: local!queryResult.data`

### Completeness Check {#validation.pre-flight.completeness}

- [ ] Conversion is 100% complete (ALL sections, ALL fields)
- [ ] TODO comments documented (if any)
- [ ] Wizard steps match (static vs dynamic)
- [ ] Form fields match (static vs dynamic)

**If ANY answer is "No", STOP and complete that step before writing output.**

---

## Final Output Steps {#validation.output}

After passing pre-flight checklist:

1. **Write output file:** `/output/[original-name]-functional.sail`

2. **Document conversion summary:**
   - Data sources connected (record types used)
   - Logic refactoring applied (counts)
   - Validation blockers encountered (if any)
   - Assumptions made about data model

3. **Invoke validation sub-agents:**
   - sail-schema-validator (function syntax)
   - sail-icon-validator (icon aliases)
   - sail-code-reviewer (structure, best practices)

4. **Review validation results:**
   - Fix any errors reported and re-validate

---

## Critical Errors Quick Reference {#validation.critical-errors}

Quick diagnostic table for common conversion errors. Each error links to its authoritative documentation.

### Error Lookup Table {#validation.critical-errors.table}

| Error | Problem | Solution | Details |
|-------|---------|----------|---------|
| **Dropdown init with record data** | `local!filter: "All"` when choiceValues come from records | `local!filter,` (uninitialized) + `placeholder: "All"` | `conversion-queries.md {#common.dropdown-all-option}` |
| **Query in grid/chart data** | `data: local!queryResults` | `data: a!recordData(...)` | `conversion-queries.md {#common.query-construction}` |
| **Type mismatch in filters** | DateTime field + Date value | Use matching type functions | `{#validation.type-matching}` |
| **Chart pattern errors** | `categories` + `series` with record data | `data: a!recordData()` + `config: a!*ChartConfig()` | `display-conversion-charts.md {#display.chart-components}` |
| **Invalid interval** | `interval: "MONTH"` or `"WEEK"` | Use `"MONTH_SHORT_TEXT"`, `"DATE_SHORT_TEXT"` | `display-conversion-charts.md {#display.chart-components.intervals}` |
| **Stacking in config** | `stacking` inside chart config | Move `stacking` to chart field level | `display-conversion-charts.md {#display.chart-components.stacking}` |
| **Non-existent functions** | `a!decimalField()`, `a!dateTimeValue()` | `a!floatingPointField()`, `datetime()` | `/ui-guidelines/reference/schemas/*.json` (per-category files; the master `sail-api-schema.json` is only an INDEX) |
| **Wizard validations param** | `validations` on `a!wizardLayout()` | Place on `a!buttonWidget()` or fields | `form-conversion-buttons-actions.md {#form.parameter-validation}` |
| **JS/Python syntax** | `condition ? true : false` | `if(condition, true, false)` | `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` |
| **Null in functions** | `text(nullField, "format")` | Wrap in `if(a!isNotNullOrEmpty(...))` | `{#validation.null-safety}` |
| **totalCount for KPIs** | `.totalCount` for metrics | Use aggregation queries | `display-conversion-kpis.md {#display.kpi-aggregation}` |
| **Array manipulation** | `append(map, array)` for insert | `a!update(data: array, index: 1, value: map)` | `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` |
| **Query extraction pattern** | Wrong indexing for query type | Aggregations: `query.data.alias`; Fields: `query[1]['field']` | `conversion-queries.md {#common.query-result-structures}` |

### Quick Diagnostic Questions {#validation.critical-errors.diagnostic}

1. **Is dropdown empty on load?** → Check variable initialization (`local!var,` not `local!var: "value"`) - See `conversion-queries.md {#common.dropdown-all-option}`
2. **Is chart blank?** → Check data pattern (`a!recordData` + config, not `categories` + `series`) - See `display-conversion-charts.md {#display.chart-refactoring}`
3. **Is KPI showing null?** → Check extraction pattern and null wrapping - See `display-conversion-kpis.md {#display.kpi-aggregation}`
4. **Is grid showing error?** → Check `fv!row` usage (not `fv!index` or `fv!item`) - See `display-conversion-grids.md {#display.grid-patterns}`
5. **Is filter not working?** → Check `applyWhen` and type matching - See `{#validation.type-matching}`
