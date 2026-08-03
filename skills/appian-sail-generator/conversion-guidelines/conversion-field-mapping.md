# Field Mapping and Validation Patterns {#field-mapping-module}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/common-conversion-patterns.md` - Navigation index
> - `/conversion-guidelines/conversion-queries.md` - Query construction patterns
> - `/conversion-guidelines/conversion-relationships.md` - Relationship navigation

Patterns for record type reference syntax, dropdown conversion, data model validation, environment objects, pattern matching refactoring, and preserving mockup values.

---

## 📑 Module Navigation {#field-mapping.nav}

- `{#field-mapping.record-type-syntax}` - Record type reference patterns (UUIDs, autocomplete)
- `{#field-mapping.dropdown-all-option}` - Converting "All" filter options
- `{#field-mapping.data-model-validation}` - Validating record types, fields, relationships
- `{#field-mapping.environment-objects}` - Constants, groups, process models
- `{#field-mapping.pattern-matching}` - Refactoring nested if() to a!match()
- `{#field-mapping.preserve-mockup-values}` - Never introduce runtime generators

---

## Record Type Reference Syntax {#field-mapping.record-type-syntax}

### Quick Reference {#field-mapping.record-type-syntax.quick-ref}

| Pattern | Syntax | Example |
|---------|--------|---------|
| **Record Type** | `'recordType!RecordTypeName'` | `'recordType!Case'` |
| **Field** | `'recordType!RecordTypeName.fields.fieldName'` | `'recordType!Case.fields.title'` |
| **Relationship** | `'recordType!RecordTypeName.relationships.relationshipName'` | `'recordType!Case.relationships.assignee'` |
| **Related Field** | `'recordType!RecordTypeName.relationships.relationshipName.fields.fieldName'` | `'recordType!Case.relationships.assignee.fields.name'` |

**Key Rules:**
- Always use the FULL reference string exactly as shown
- Relationships are for navigation, fields are for values
- Use single continuous path for related fields - ONLY ONE bracket for the entire path

### ⚠️ CRITICAL: Examples vs Working Code {#field-mapping.record-type-syntax.examples-vs-code}

**In these guidelines, record types are shown with clean semantic names for readability:**

```sail
/* Example syntax (for documentation purposes): */
'recordType!Case.fields.title'
'recordType!Employee.relationships.department.fields.name'
'recordType!Task.relationships.assignee.fields.username'
```

**In actual Appian SAIL code, you MUST use fully qualified references with UUIDs:**

```sail
/* Actual Appian syntax (what you'll see in the designer): */
'recordType!{abc-123}Case.fields.{def-456}title'
'recordType!{ghi-789}Employee.relationships.{jkl-012}department.fields.{mno-345}name'
```

### How to Get Correct References in Appian Designer {#field-mapping.record-type-syntax.autocomplete}

1. **Start typing** the record type reference: `'recordType!`
2. **Press Ctrl+Space** (or Cmd+Space on Mac) to open autocomplete
3. **Select your record type** from the list (e.g., "Case")
4. **Continue typing** `.fields.` or `.relationships.`
5. **Press Ctrl+Space again** to see available fields/relationships
6. **Select the field/relationship** you need
7. **Appian automatically inserts** the correct UUIDs

### Key Points {#field-mapping.record-type-syntax.key-points}

- ✅ **Always use Appian's autocomplete** to get qualified references
- ✅ **Each UUID is unique** to your environment
- ✅ **UUIDs are auto-generated** by Appian when you create record types/fields
- ❌ **Never manually type UUIDs** or copy them between different fields
- ❌ **Never use the example syntax** directly in working code

### For Code Generation {#field-mapping.record-type-syntax.code-generation}

When generating code, use the **placeholder pattern** to indicate where developers need to substitute actual references:

```sail
/* Generated code pattern: */
ri!case['recordType!Case.fields.title']
fv!row['recordType!Employee.relationships.department.fields.name']

/* Developers replace with actual qualified references from their Appian environment */
```

This approach:
- Makes generated code readable
- Clearly shows the semantic structure
- Requires developers to use proper Appian tooling for actual references
- Prevents UUID copy-paste errors

---

## Dropdown "All" Option Conversion {#field-mapping.dropdown-all-option}

### The Problem

**NEVER use `append()` to add "All" to query results** - creates List of Variant type errors.

```sail
/* ❌ WRONG - Creates List of Variant type error */
local!typeChoiceLabels: append(
  "All Types",
  index(local!types, 'recordType!Type.fields.typeName', {})
)
```

### The Solution: Use placeholder Parameter

**Mockup Pattern (static data with hardcoded "All"):**
```sail
local!filterType: "All",  /* Initialized to "All" */
a!dropdownField(
  choiceLabels: {"All Types", "Board", "Committee"},
  choiceValues: {"All", "Board", "Committee"},
  value: local!filterType,
  saveInto: local!filterType
)

/* Filter logic checks for "All" */
a!queryFilter(
  field: 'recordType!...typeId',
  operator: "=",
  value: local!selectedTypeId,
  applyWhen: local!filterType <> "All"
)
```

**Functional Pattern (query data with placeholder):**
```sail
local!filterType,  /* Uninitialized = null = placeholder shows */

/* Query for dropdown options */
local!types: a!queryRecordType(
  recordType: 'recordType!Type',
  fields: {
    'recordType!Type.fields.typeId',
    'recordType!Type.fields.typeName'
  },
  pagingInfo: a!pagingInfo(startIndex: 1, batchSize: 100)
).data,

a!dropdownField(
  choiceLabels: index(local!types, 'recordType!Type.fields.typeName', {}),
  choiceValues: index(local!types, 'recordType!Type.fields.typeName', {}),
  value: local!filterType,
  saveInto: local!filterType,
  placeholder: "All Types"  /* Replaces the hardcoded "All" option */
)

/* Filter logic checks for null (placeholder selected) */
a!queryFilter(
  field: 'recordType!...typeId',
  operator: "=",
  value: local!selectedTypeId,
  applyWhen: a!isNotNullOrEmpty(local!filterType)  /* Changed from <> "All" */
)
```

### Conversion Checklist {#field-mapping.dropdown-all-option.checklist}

- [ ] Remove "All" from choiceLabels/choiceValues - Don't append or prepend
- [ ] Add `placeholder: "All Types"` parameter - Replaces the hardcoded option
- [ ] Leave filter variable uninitialized - `local!filterType,` (no value)
- [ ] Update filter applyWhen logic - Change `<> "All"` to `a!isNotNullOrEmpty()`

---

## Data Model Validation {#field-mapping.data-model-validation}

### Purpose

**NEVER invent record types, fields, relationships, or UUIDs** - ONLY use what exists in `context/data-model-context.md`.

### Relationship Target Validation {#field-mapping.data-model-validation.relationships}

For EVERY relationship you plan to navigate:

**Step 1: Find relationship in source record type**
```
Source: Case
Relationship: assignedTo
Reference: 'recordType!Case.relationships.assignedTo'
Type: many-to-one
```

**Step 2: Find target record type definition**
- Search `data-model-context.md` for the target record type section
- Example: Relationship "assignedTo" → Search for "### Employee"

**Step 3: Decision Tree**

| Scenario | Action |
|----------|--------|
| Target record type IS defined | ✅ Proceed - use fields from target's Fields table |
| Target record type NOT defined | ⚠️ Check for foreign key fallback (Step 3A below) |

### Foreign Key Fallback Pattern {#field-mapping.data-model-validation.fk-fallback}

When relationship target is NOT found in data-model-context.md:

**Step 3A.1: Check for foreign key ID field**
- Go to source record type's Fields table
- Look for ID field matching relationship name:
  - Relationship: `caseType` → Look for: `caseTypeId` (Integer)
  - Relationship: `assignedTo` → Look for: `assignedToUser` (User)

**Step 3A.2: Decision**

| Found | Action |
|-------|--------|
| Foreign key ID field exists | Use direct field instead of relationship navigation |
| No foreign key found | Revert to mockup data pattern (preserve UX) |

**Example - Using foreign key fallback:**
```sail
/* TODO: Target record type for relationship 'caseType' not found
 * Cannot navigate: Case.relationships.caseType.fields.typeName
 * WORKAROUND: Using foreign key ID field 'caseTypeId' instead */
local!typeId: local!case['recordType!Case.fields.caseTypeId'],

value: if(
  a!isNullOrEmpty(local!typeId),
  "[Type not available]",
  "Type ID: " & local!typeId
)
```

**Example - Mockup data fallback (preserve UX):**
```sail
/* MOCKUP DATA - Client Profile View (Data Model Limitation):
 * Client record type not available in context/data-model-context.md
 * Using hardcoded sample data to preserve UX flow
 *
 * TODO: Add Client record type to enable live data */
local!clientCases: {
  a!map(caseNumber: "CASE-001", subject: "Sample Case", status: "Open"),
  a!map(caseNumber: "CASE-002", subject: "Another Sample", status: "Closed")
},

/* Visual indicator in UI */
a!richTextItem(text: "(Sample Data)", size: "SMALL", color: "#6B7280")
```

### Field Access Validation {#field-mapping.data-model-validation.fields}

For EVERY field you plan to access:

**Step 1:** Locate record type in `data-model-context.md`

**Step 2:** Verify correct Fields table (for relationships, use TARGET record type)

**Step 3:** Decision Tree

| Scenario | Action |
|----------|--------|
| Exact field name exists | ✅ Use field reference from table |
| Similar field exists | ✅ Use with ASSUMPTION comment |
| No match found | ❌ Use placeholder with TODO comment |

**Example - Similar field substitution:**
```sail
/* ASSUMPTION: No fullName field exists in Employee record type
 * Using firstName and lastName fields instead
 * Source: context/data-model-context.md Employee Fields table */
local!assigneeName: concat(
  a!defaultValue(ri!case['recordType!Case.relationships.assignedTo.fields.firstName'], ""),
  " ",
  a!defaultValue(ri!case['recordType!Case.relationships.assignedTo.fields.lastName'], "")
)
```

---

## Environment Object Validation {#field-mapping.environment-objects}

### Purpose

**Never assume constants, process models, groups, folders, integrations, or environment-specific objects exist. Always use placeholders with TODO comments.**

This applies to ALL generated code, including:
- Group constants in `a!isUserMemberOfGroup()`
- Folder constants in `a!fileUploadField()`
- Process model constants in `a!startProcess()`
- Any `cons!` reference
- Any `rule!` reference (unless explicitly specified by user)

### Environment References to Check {#field-mapping.environment-objects.checklist}

- [ ] **Constants** (`cons!*`) - Configuration values, groups, folders
- [ ] **Process Models** - Any `processModel` parameter value
- [ ] **Document Folders** - Any `target` parameter for file uploads
- [ ] **Groups** - Any `groups` parameter in `a!isUserMemberOfGroup()`
- [ ] **Integration Objects** - External system connections
- [ ] **Expression Rules** (`rule!*`) - Unless explicitly required

### ✅ CORRECT Pattern - Placeholder with TODO {#field-mapping.environment-objects.correct}

```sail
/* Group-based security checks */
a!isUserMemberOfGroup(
  username: loggedInUser(),
  groups: null  /* TODO: Add group constant for case managers */
)

/* File upload fields */
a!fileUploadField(
  label: "Upload Supporting Document",
  target: null,  /* TODO: Add constant value for case documents folder */
  value: local!documentUpload,
  saveInto: local!documentUpload
)

/* Process model references */
a!startProcess(
  processModel: null,  /* TODO: Add constant for case submission process model */
  processParameters: {
    case: ri!case,
    submittedBy: loggedInUser()
  }
)
```

### ❌ WRONG Pattern - Assuming Objects Exist {#field-mapping.environment-objects.wrong}

```sail
/* DON'T DO THIS */
a!isUserMemberOfGroup(
  username: loggedInUser(),
  groups: cons!CASE_MANAGERS_GROUP  /* This constant may not exist! */
)

a!fileUploadField(
  target: cons!CASE_DOCUMENTS_FOLDER,  /* This constant may not exist! */
  ...
)

a!startProcess(
  processModel: cons!SUBMIT_CASE_PROCESS,  /* May not exist! */
  ...
)
```

### Handling Mockup Patterns {#field-mapping.environment-objects.handling}

**Case A: Reference exists in mockup as simple pattern**
```sail
/* Mockup had: local!userRole = "Partner" */
/* ✅ KEEP IT - Don't convert to a!isUserMemberOfGroup() with constants */
local!isPartner: local!userRole = "Partner",
```

**Case B: Reference needed but doesn't exist**
```sail
/* TODO: Configure group constant for Partners access control
 * Create: cons!PARTNERS_GROUP
 * Assign all partner users to this group */
local!isPartner: a!isUserMemberOfGroup(
  username: loggedInUser(),
  groups: null /* TODO: Add group constant */
),
```

### TODO Comment Format {#field-mapping.environment-objects.todo-format}

Use consistent TODO comments so developers can:
- **Search systematically** - Find all configuration points by searching "TODO"
- **Understand intent** - Know exactly what needs to be configured
- **Prevent runtime errors** - null placeholders allow UI testing while clearly marking incomplete code

**Templates:**
```sail
/* TODO: Add constant value for [specific purpose] */
/* TODO: Configure [object type] - [what it should reference] */
/* TODO: Add integration object for [external system] */
```

### Group-Based Access Control Pattern {#field-mapping.environment-objects.group-access-control}

When implementing role-based access control in SAIL interfaces, use Group type parameters with integer mock IDs for mockups.

**✅ CORRECT Pattern - Group Type with Mock IDs:**
```sail
/* ===== INTERFACE PARAMETERS ===== */
/* ri!currentUserGroup (Group): Group of the logged-in user for access control */
/* TODO: Replace integer group IDs with actual Group constant objects once available */

/* ===== GROUP CONSTANTS (Mock - using integers until Group constants are available) ===== */
/* TODO: Replace with cons!PARTNER_GROUP and cons!INDEPENDENCE_TEAM_GROUP */
local!PARTNER_GROUP_ID: 1,
local!INDEPENDENCE_TEAM_GROUP_ID: 2,

/* ===== CONDITIONAL DISPLAY FLAGS ===== */
/* TODO: Once Group constants are available, compare ri!currentUserGroup directly to cons!PARTNER_GROUP */
local!isPartner: a!defaultValue(ri!currentUserGroup, local!PARTNER_GROUP_ID) = local!PARTNER_GROUP_ID,
local!isIndependenceTeam: a!defaultValue(ri!currentUserGroup, local!INDEPENDENCE_TEAM_GROUP_ID) = local!INDEPENDENCE_TEAM_GROUP_ID
```

**❌ WRONG Pattern - Text-Based Roles:**
```sail
/* DON'T USE TEXT TYPE FOR ROLES */
/* ri!userRole (Text): "Partner" or "Independence Team" */
local!isPartner: ri!userRole = "Partner"
```

**Key Rules:**
1. **Use Group type for role-based rule inputs** - Not Text type
2. **Define mock group ID constants** - Use integers (1, 2, 3, etc.) as placeholders
3. **Add TODO comments** - Document that integers should be replaced with Group constants
4. **Use a!defaultValue() for comparisons** - Safely handle null group values
5. **Specify constant names in TODOs** - Help developers know which constants to create

**Why Use Group Type Instead of Text:**
- **Security**: Groups are managed in Appian's security model, not hardcoded strings
- **Maintainability**: Group membership changes don't require code updates
- **Type Safety**: Group type provides proper validation and prevents typos
- **Best Practice**: Aligns with Appian's security architecture

---

## Pattern Matching Refactoring {#field-mapping.pattern-matching}

### When to Refactor nested if() to a!match()

**MANDATORY when:**
- Single variable compared against 3+ distinct enumerated values
- Pattern matching for: status codes, priorities, categories, types

**DO NOT refactor when:**
- Complex conditional logic with multiple variables
- Null safety checks (keep nested if() for short-circuit)
- Computed variables with side effects

### Refactoring Example {#field-mapping.pattern-matching.example}

```sail
/* ❌ BEFORE (nested if) - OUTDATED PATTERN */
if(status = "Open", "folder-open",
  if(status = "Closed", "check-circle",
    if(status = "Pending", "clock", "file")))

/* ✅ AFTER (a!match) - MODERN PATTERN */
a!match(
  value: status,
  equals: "Open", then: "folder-open",
  equals: "Closed", then: "check-circle",
  equals: "Pending", then: "clock",
  default: "file"
)
```

### Range-Based Comparisons with whenTrue {#field-mapping.pattern-matching.ranges}

For date ranges, numeric thresholds, or complex conditions:

```sail
a!match(
  value: true,
  whenTrue: fv!row.daysOverdue > 30, then: "#DC2626",  /* Red */
  whenTrue: fv!row.daysOverdue > 14, then: "#F59E0B",  /* Amber */
  whenTrue: fv!row.daysOverdue > 0, then: "#EAB308",   /* Yellow */
  default: "#10B981"  /* Green */
)
```

**Reference:** See `/logic-guidelines/pattern-matching.md` for complete a!match() patterns.

---

## Preserving Mockup Values During Conversion {#field-mapping.preserve-mockup-values}

### Rule: Never Introduce Runtime Generators

When converting mockups to functional interfaces, **preserve static mockup values exactly as-is**. Do not add runtime generation logic.

**❌ WRONG - Adding runtime logic during conversion:**
```sail
/* Mockup had: local!caseNumber: "CASE-5847" */

/* Converter incorrectly changed to: */
local!caseNumber: "CASE-" & text(rand(10000), "0000")  /* ❌ Changes on every interaction! */
```

**✅ CORRECT - Preserve mockup value:**
```sail
/* Mockup had: local!caseNumber: "CASE-5847" */

/* Converter preserves: */
local!caseNumber: "CASE-5847",  /* TODO: Auto-generated by case management system on save */
```

### When This Applies

**For local variables that remain as `local!` after conversion:**
- Display-only computed values (auto-generated IDs, reference numbers)
- External system data not in record type (user profiles, system integrations)
- Reference data for dropdowns/choices

**Key principle:** If the mockup used a static value, the functional interface should too. Add TODO comments for data source, but don't simulate dynamic behavior.

### Valid Use of Runtime Functions

**✅ Runtime functions ARE valid when setting record fields:**
```sail
a!buttonWidget(
  label: "Submit",
  saveInto: {
    a!save(ri!case['recordType!Case.fields.createdOn'], now()),  /* ✅ Valid */
    a!save(ri!case['recordType!Case.fields.createdBy'], loggedInUser())  /* ✅ Valid */
  }
)
```

**❌ Runtime functions are NOT valid for UI display variables:**
```sail
local!displayNumber: "REF-" & text(rand(10000), "0000")  /* ❌ Wrong */
```
