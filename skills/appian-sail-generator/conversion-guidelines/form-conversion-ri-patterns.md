# Form Conversion - Rule Input Patterns {#form-ri}

> **Parent guide:** `/conversion-guidelines/form-conversion-module.md`
>
> **Related modules:**
> - `/conversion-guidelines/form-conversion-relationships.md` - Relationship access patterns
> - `/conversion-guidelines/form-conversion-buttons-actions.md` - Button field-setting and actions
> - `/conversion-guidelines/form-conversion-data-model.md` - Data model mismatch strategies

---

## 📑 Section Navigation {#form-ri.nav}

- `{#form-ri.detection}` - How to identify form interfaces
- `{#form-ri.pattern}` - Rule input pattern overview
- `{#form-ri.names}` - Mandatory rule input naming
- `{#form-ri.comment-format}` - Structured comment format
- `{#form-ri.variable-mapping}` - Mapping mockup variables to ri!

---

## Interface Detection {#form-ri.detection}

### Form Interface Indicators

A mockup is a **Form Interface** if it contains:

| Indicator | Example |
|-----------|---------|
| Submission buttons | "Submit", "Save", "Create", "Update" |
| Create/Update intent | "New Case Form", "Edit Employee" |
| Wizard layout | `a!wizardLayout()` with step progression |
| Form layout with buttons | `a!formLayout()` with primary/secondary buttons |
| Editable fields with submit | textFields with corresponding save action |

### Decision Tree

```
Does interface have submission buttons?
├─ YES → Continue checking
│   └─ Does it create/update a record?
│       ├─ YES → Use FORM CONVERSION MODULE (ri! pattern)
│       └─ NO (just triggers process) → May use query pattern + a!startProcess()
│
└─ NO → Use DISPLAY CONVERSION MODULE
```

### NOT a Form Interface

These are **NOT** form interfaces (use display module instead):
- Filter dropdowns that filter a grid
- Search inputs that query data
- Read-only detail views (even if they have action buttons that launch separate forms)
- Dashboards with navigation controls

---

## Rule Input Pattern {#form-ri.pattern}

### Purpose

Form interfaces receive their data as **rule inputs (ri!)** from the calling context (process model, record action, related action). This allows forms to create or update record data.

### 🚨 MANDATORY Rule Input Names {#form-ri.names}

**BEFORE beginning form conversion, check your task prompt for "🚨 CRITICAL: This interface is a START FORM" section.**

#### If START FORM section exists (model.json available):

Rule input names come from the process model specification in model.json.

**How to get the correct names:**

1. Task prompt contains "🚨 CRITICAL: This interface is a START FORM" section
2. **Read ../../model.json** to find the process model
3. **Extract process_variables** where `start_form_interface` matches this interface
4. **Use EXACT variable_name** from each process variable as `ri!{variable_name}`

**Example:**

Process model in model.json contains:
```json
"process_variables": [
  {
    "variable_name": "submission",
    "variable_type": "Record Type: BOARD_COMMITTEE_SUBMISSION"
  }
]
```

→ **Must use:** `ri!submission` (NOT `ri!record`, NOT `ri!boardCommitteeSubmission`)

**Standard Pattern (with model.json):**

| Rule Input | Type | Purpose | Source |
|------------|------|---------|--------|
| `ri!{entityName}` | Record Type | The record being created/updated (e.g., `ri!submission`, `ri!case`) | From process_variables `variable_name` where type starts with "Record Type:" |
| `ri!isUpdate` | Boolean | Mode flag - `true` = update, `false` = create | From process_variables (standard variable) |
| `ri!cancel` | Boolean | Cancellation signal for process model | From process_variables (standard variable) |

**Rules (with model.json):**
- ✅ Read exact names from process model in model.json
- ✅ Use `ri!{variable_name}` exactly as specified
- ❌ DO NOT infer from entity name
- ❌ DO NOT use generic names like `ri!record`

#### If NO START FORM section (no model.json available):

Use standard Appian naming pattern by inferring from the mockup.

**How to get the names:**

1. Task prompt does NOT contain "🚨 CRITICAL: This interface is a START FORM" section
2. **Identify the primary record variable** in the mockup (e.g., `local!case`, `local!submission`)
3. **Convert:** `local!{recordName}` → `ri!{recordName}`
4. **Add standard variables:** `ri!isUpdate`, `ri!cancel`

**Example:**

Mockup contains:
```sail
local!case,
a!textField(
  label: "Case Title",
  value: local!case['recordType!Case.fields.title']
)
```

→ **Must use:** `ri!case` (inferred from `local!case`)

**Standard Pattern (without model.json):**

| Rule Input | Type | Purpose | Derivation |
|------------|------|---------|------------|
| `ri!{recordName}` | Record Type | The record being created/updated | Inferred from mockup's `local!{recordName}` |
| `ri!isUpdate` | Boolean | Mode flag - `true` = update, `false` = create | Standard variable (always include) |
| `ri!cancel` | Boolean | Cancellation signal | Standard variable (always include) |

**Common Conversions:**
- `local!case` → `ri!case`
- `local!submission` → `ri!submission`
- `local!ticket` → `ri!ticket`
- `local!order` → `ri!order`

**Universal Rules (both scenarios):**
- ❌ WRONG: `ri!isEditMode`, `ri!isEdit`, `ri!editMode`, `ri!cancelled`
- ✅ CORRECT: `ri!isUpdate`, `ri!cancel`

### Pattern Overview

```sail
/* ==========================================================================
 * RULE INPUTS (ri!) - Configure in Interface Definition
 * ==========================================================================
 * Name: ri!case
 * Type: Case
 * Description: The case record being created or updated. Pass null for create mode.
 * ----------
 * Name: ri!isUpdate
 * Type: Boolean
 * Description: Flag indicating if form is in update mode (true) or create mode (false).
 * ----------
 * Name: ri!cancel
 * Type: Boolean
 * Description: Flag set to true when user cancels the form. Allows process model
 *              to take a different path based on cancellation vs submission.
 * ==========================================================================
 */
a!localVariables(
  /* Form uses ri! directly - no local copies */
  a!formLayout(
    contents: {
      a!textField(
        label: "Subject",
        value: ri!case['recordType!Case.fields.subject'],
        saveInto: ri!case['recordType!Case.fields.subject'],
        required: true
      )
    },
    buttons: a!buttonLayout(
      primaryButtons: {
        a!buttonWidget(
          label: if(ri!isUpdate, "Update", "Create"),
          submit: true,
          style: "SOLID",
          color: "ACCENT"
        )
      }
    )
  )
)
```

### Key Principles

1. **Form fields bind directly to ri!** - No local variable copies
2. **ri! is a parameter, not a variable** - Cannot initialize inside the interface
3. **Always null-check ri! before use** - Use `a!defaultValue()` or `if(a!isNotNullOrEmpty())`
4. **Document ri! in header comment** - Not in code

---

## Comment Format {#form-ri.comment-format}

### Structured Rule Input Documentation

Every form interface MUST have a header comment documenting all rule inputs:

```sail
/* ==========================================================================
 * RULE INPUTS (ri!) - Configure in Interface Definition
 * ==========================================================================
 * Name: ri!submission
 * Type: BoardCommitteeSubmission
 * Description: The submission record being created or updated. When creating a
 *              new submission, the calling process should pass a new record instance
 *              with partnerUsername pre-populated.
 * ----------
 * Name: ri!isUpdate
 * Type: Boolean
 * Description: Flag indicating if the form is in update mode. When true, form
 *              displays existing data for editing. When false, form is for new
 *              submission creation.
 * ----------
 * Name: ri!cancel
 * Type: Boolean
 * Description: Flag set to true when user cancels the form. Allows process model
 *              to take a different path based on cancellation vs submission.
 * ----------
 * Name: ri!allowEdit
 * Type: Boolean
 * Description: Flag indicating if the current user has permission to edit this
 *              submission. Used to control field editability and button visibility.
 * ==========================================================================
 */
```

### Format Requirements

| Element | Requirement |
|---------|-------------|
| Header | `RULE INPUTS (ri!) - Configure in Interface Definition` |
| Separator | `==========` line above and below |
| Between inputs | `----------` separator |
| Name | `Name: ri!variableName` |
| Type | `Type: RecordTypeName` or `Type: Boolean/Text/Integer` |
| Description | Multi-line explanation of purpose, usage, and any mode-specific behavior |

### Description Guidelines

Good descriptions answer:
- What data does this input contain?
- Who/what provides this value?
- How does the form use this input?
- Are there mode-specific behaviors?

```sail
/* ❌ BAD - Just restates the type */
* Description: The case record.

/* ✅ GOOD - Explains purpose and usage */
* Description: The case record being created or updated. When creating a new case,
*              the calling process should pass a new record instance with caseNumber
*              pre-populated from the sequence generator.
```

---

## Variable Mapping {#form-ri.variable-mapping}

### Converting Mockup Variables to ri!

| Mockup Variable | ri! Name | Record Type Example |
|----------------|----------|---------------------|
| `local!case` | `ri!case` | Case |
| `local!customer` | `ri!customer` | Customer |
| `local!order` | `ri!order` | Order |
| `local!employee` | `ri!employee` | Employee |
| `local!submission` | `ri!submission` | BoardCommitteeSubmission |
| `local!invoice` | `ri!invoice` | Invoice |
| `local!ticket` | `ri!ticket` | SupportTicket |
| `local!project` | `ri!project` | Project |
| `local!task` | `ri!task` | Task |
| `local!document` | `ri!document` | Document |

**Pattern:** Convert `local!{recordName}` → `ri!{recordName}` where {recordName} matches the primary record being created/updated.

### What to Convert vs Keep Local

| Variable Type | Action |
|--------------|--------|
| Primary record data (`local!case`) | Convert to `ri!case` |
| Mode flags (`local!isUpdate`) | Convert to `ri!isUpdate` |
| Permission flags (`local!canEdit`) | Convert to `ri!allowEdit` |
| UI state (`local!showDetails`) | KEEP as local! |
| Computed values (`local!totalAmount`) | KEEP as local! |
| Query results (`local!statusOptions`) | KEEP as local! |
| Temporary selections (`local!selectedIds`) | KEEP as local! |

### Field Binding Conversion

```sail
/* ❌ MOCKUP - Uses local variables */
local!organizationName,
a!textField(
  label: "Organization Name",
  value: local!organizationName,
  saveInto: local!organizationName
)

/* ✅ FUNCTIONAL - Uses ri! with record type field */
a!textField(
  label: "Organization Name",
  value: ri!submission['recordType!Submission.fields.organizationName'],
  saveInto: ri!submission['recordType!Submission.fields.organizationName']
)
```
