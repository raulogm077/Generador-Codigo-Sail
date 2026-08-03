# Form Conversion - Buttons and Actions {#form-buttons}

> **Parent guide:** `/conversion-guidelines/form-conversion-module.md`
>
> **Related modules:**
> - `/conversion-guidelines/form-conversion-ri-patterns.md` - Rule input patterns
> - `/conversion-guidelines/form-conversion-relationships.md` - Relationship patterns
> - `/conversion-guidelines/form-conversion-data-model.md` - Data model handling

---

## 📑 Section Navigation {#form-buttons.nav}

- `{#form-buttons.audit-fields}` - Managing audit fields
- `{#form-buttons.wizard-handling}` - Multi-step wizard patterns
- `{#form-buttons.action-buttons}` - Form submission buttons
- `{#form-buttons.field-setting}` - Button field-setting with status/action fields
- `{#form-buttons.cleanup}` - TODO-CONVERTER comment cleanup

---

## Audit Fields Management {#form-buttons.audit-fields}

### Purpose

Record types typically have audit fields that track creation and modification metadata. These must be set appropriately during save.

### Common Audit Fields

| Field | Type | Set On |
|-------|------|--------|
| `createdBy` | User | CREATE only |
| `createdOn` | DateTime | CREATE only |
| `modifiedBy` | User | CREATE and UPDATE |
| `modifiedOn` | DateTime | CREATE and UPDATE |

**Note:** Setting modifiedBy/modifiedOn on creation ensures these fields are never null, simplifying reporting and audit queries.

### Create Mode {#form-buttons.audit-fields.create-mode}

Set ALL audit fields when form creates a new record:

```sail
a!buttonWidget(
  label: "Submit",
  submit: true,
  style: "SOLID",
  color: "ACCENT",
  saveInto: {
    /* Set ALL audit fields on creation */
    a!save(ri!submission['recordType!Submission.fields.createdBy'], loggedInUser()),
    a!save(ri!submission['recordType!Submission.fields.createdOn'], now()),
    a!save(ri!submission['recordType!Submission.fields.modifiedBy'], loggedInUser()),
    a!save(ri!submission['recordType!Submission.fields.modifiedOn'], now())
  },
  showWhen: not(a!defaultValue(ri!isUpdate, false()))  /* Null safety: defaults to CREATE mode */
)
```

### Update Mode {#form-buttons.audit-fields.update-mode}

Set only modification audit fields when form updates existing record:

```sail
a!buttonWidget(
  label: "Save Changes",
  submit: true,
  style: "SOLID",
  color: "ACCENT",
  saveInto: {
    /* Only set modification audit fields on update */
    a!save(ri!submission['recordType!Submission.fields.modifiedBy'], loggedInUser()),
    a!save(ri!submission['recordType!Submission.fields.modifiedOn'], now())
  },
  showWhen: a!defaultValue(ri!isUpdate, false())  /* Null safety: defaults to false (hide) */
)
```

**Rationale for two separate buttons:**
- Clearer code, easier to maintain
- Different labels for each mode ("Submit" vs "Save Changes")
- No conditional logic inside saveInto
- showWhen ensures only one button is visible at a time

---

## Wizard Handling {#form-buttons.wizard-handling}

### Wizard Layout Structure

Multi-step forms use `a!wizardLayout()` with step navigation:

```sail
a!localVariables(
  local!currentStep: 1,

  a!wizardLayout(
    steps: {
      a!wizardStep(label: "Basic Information"),
      a!wizardStep(label: "Contact Details"),
      a!wizardStep(label: "Review & Submit")
    },
    currentStep: local!currentStep,
    contents: {
      /* Step 1: Basic Information */
      showWhen(local!currentStep = 1,
        a!cardLayout(
          contents: { /* Step 1 fields */ }
        )
      ),
      /* Step 2: Contact Details */
      showWhen(local!currentStep = 2,
        a!cardLayout(
          contents: { /* Step 2 fields */ }
        )
      ),
      /* Step 3: Review & Submit */
      showWhen(local!currentStep = 3,
        a!cardLayout(
          contents: { /* Review section */ }
        )
      )
    },
    buttons: a!buttonLayout(
      secondaryButtons: {
        a!buttonWidget(
          label: "Back",
          saveInto: a!save(local!currentStep, local!currentStep - 1),
          showWhen: local!currentStep > 1
        )
      },
      primaryButtons: {
        a!buttonWidget(
          label: "Next",
          saveInto: a!save(local!currentStep, local!currentStep + 1),
          showWhen: local!currentStep < 3
        ),
        a!buttonWidget(
          label: "Submit",
          submit: true,
          style: "SOLID",
          color: "ACCENT",
          showWhen: local!currentStep = 3
        )
      }
    )
  )
)
```

### Wizard Conversion Considerations

| Mockup Element | Conversion Action |
|----------------|-------------------|
| Step content with local! | Convert field bindings to ri! |
| Step count | Keep same structure |
| Navigation buttons | Keep local!currentStep for UI state |
| Submit button | Add audit field saves, bind to ri! |
| Step validations | Convert to use ri! field paths |

---

## Form Action Buttons {#form-buttons.action-buttons}

### Create Button Pattern {#form-buttons.action-buttons.create}

Use for new record creation (when `ri!isUpdate` is false):

```sail
a!buttonWidget(
  label: "Submit",
  submit: true,
  style: "SOLID",
  color: "ACCENT",
  validate: true,
  saveInto: {
    /* Set ALL audit fields on creation */
    a!save(ri!submission['recordType!Submission.fields.createdBy'], loggedInUser()),
    a!save(ri!submission['recordType!Submission.fields.createdOn'], now()),
    a!save(ri!submission['recordType!Submission.fields.modifiedBy'], loggedInUser()),
    a!save(ri!submission['recordType!Submission.fields.modifiedOn'], now())
  },
  showWhen: not(a!defaultValue(ri!isUpdate, false()))  /* Null safety: defaults to CREATE mode */
)
```

### Update Button Pattern {#form-buttons.action-buttons.update}

Use for existing record updates (when `ri!isUpdate` is true):

```sail
a!buttonWidget(
  label: "Save Changes",
  submit: true,
  style: "SOLID",
  color: "ACCENT",
  validate: true,
  saveInto: {
    /* Only set modification audit fields on update */
    a!save(ri!submission['recordType!Submission.fields.modifiedBy'], loggedInUser()),
    a!save(ri!submission['recordType!Submission.fields.modifiedOn'], now())
  },
  showWhen: a!defaultValue(ri!isUpdate, false())  /* Null safety: defaults to false (hide) */
)
```

**Key Differences:**

| Aspect | Create Button | Update Button |
|--------|---------------|---------------|
| Label | "Submit" | "Save Changes" |
| Audit Fields | All 4 (createdBy, createdOn, modifiedBy, modifiedOn) | Only 2 (modifiedBy, modifiedOn) |
| showWhen | `not(a!defaultValue(ri!isUpdate, false()))` | `a!defaultValue(ri!isUpdate, false())` |

**Rationale:**
- **Create mode sets all 4 fields**: Ensures modifiedBy/modifiedOn are never null on new records, simplifying reporting and audit queries
- **Update mode only sets 2 fields**: Preserves original creation metadata while tracking the latest modification

### Cancel Button Pattern

```sail
a!buttonWidget(
  label: "Cancel",
  style: "OUTLINE",
  color: "SECONDARY",
  submit: true,           /* Submits form to return control to process model */
  validate: false,        /* Skip validation on cancel */
  saveInto: {
    a!save(ri!cancel, true)  /* Signal cancellation to process model */
  }
)
```

**Why `submit: true` instead of `cancel: true`?**
- Using `cancel: true` discards all form data and does not pass values back to the process model
- Using `submit: true` with `ri!cancel: true` allows the process model to receive the cancellation signal and take a different path (e.g., skip record creation, show confirmation, etc.)

### Save Draft Pattern

```sail
a!buttonWidget(
  label: "Save Draft",
  style: "OUTLINE",
  color: "ACCENT",
  validate: false,        /* Don't validate - allow incomplete data */
  saveInto: {
    a!save(ri!submission['recordType!Submission.fields.status'], "Draft")
  }
)
```

### Form vs Display Action Buttons

| Button Purpose | In Form Module? | In Display Module? |
|----------------|-----------------|-------------------|
| Submit/Create form | ✅ Yes | ❌ No |
| Save/Update record | ✅ Yes | ❌ No |
| Cancel form | ✅ Yes | ❌ No |
| Navigate to another record | ❌ No | ✅ Yes |
| Launch create form (from list) | ❌ No | ✅ Yes |
| Launch edit form (from grid) | ❌ No | ✅ Yes |

---

## Button Field-Setting Conversion {#form-buttons.field-setting}

### When to Apply

Apply this pattern when mockup contains:
- TODO-CONVERTER comments indicating field-setting requirements
- Read-only or disabled fields displaying system-controlled values
- Action buttons with specific outcomes (Approve, Deny, Return, etc.)
- Status or enumerated fields that change based on button clicked

### Detection Steps

**Step 1: Extract TODO-CONVERTER Comments**
```bash
grep -B2 -A5 "TODO-CONVERTER:" /output/mockup.sail
```

Parse instructions:
- `Set status to "X"` → Status field = "X"
- `Set [field] to current user` → User field = loggedInUser()
- `Set [field] to current timestamp` → DateTime field = now()
- `Increment [field]` → Counter field += 1 with null safety
- `Add standard audit fields` → Use existing audit pattern `{#form-buttons.audit-fields}`
- `Set ri!cancel to true` → Use existing cancel pattern (line 886)

**Step 2: Detect Read-Only Fields**
```bash
grep -B3 "readOnly: true\|disabled: true" /output/mockup.sail
```

Fields marked readOnly/disabled need values set in button saveInto.

**Step 3: Match Button Labels to Actions**

| Button Label | Status Value | Action Fields |
|--------------|--------------|---------------|
| "Approve", "Accept" | "Approved" | approvedBy, approvedDate |
| "Deny", "Reject" | "Denied" | deniedBy, deniedDate |
| "Return", "Send Back" | "Returned" | returnedBy, returnedDate, returnCount++ |
| "Submit" (CREATE) | "Submitted" | submittedBy, submittedDate |
| "Cancel" | - | ri!cancel: true (see line 886) |

**Step 4: Check Field Types**

For each field in TODO-CONVERTER comments:
1. Verify field exists in data-model-context.md
2. Check if Text or Integer (e.g., status vs statusId)
3. If Integer ID field: Use hardcoded ID with mapping comment

### Action Button with Status Pattern

```sail
/* Status ID Mapping (if data model uses ID field):
 * 1 = Submitted
 * 2 = Pending Review
 * 3 = Approved
 * 4 = Denied
 * 5 = Returned
 */

a!buttonWidget(
  label: "Approve",
  submit: true,
  style: "SOLID",
  color: "ACCENT",
  validate: true,
  saveInto: {
    /* Set status field (use ID if statusId, text if status) */
    a!save(ri!application['recordType!Application.fields.statusId'], 3),  /* Approved */
    /* Set action-specific fields */
    a!save(ri!application['recordType!Application.fields.approvedBy'], loggedInUser()),
    a!save(ri!application['recordType!Application.fields.approvedDate'], now()),
    /* Set audit fields (from existing pattern at line 717) */
    a!save(ri!application['recordType!Application.fields.modifiedBy'], loggedInUser()),
    a!save(ri!application['recordType!Application.fields.modifiedOn'], now())
  }
)
```

### Counter Increment Pattern

When button increments a counter (e.g., returnCount, attemptNumber):

```sail
a!buttonWidget(
  label: "Return for Information",
  submit: true,
  style: "OUTLINE",
  color: "ACCENT",
  validate: false,  /* Don't validate - application may be incomplete */
  saveInto: {
    /* Status and action fields... */
    /* Increment counter with null safety */
    a!save(
      ri!application['recordType!Application.fields.returnCount'],
      a!defaultValue(ri!application['recordType!Application.fields.returnCount'], 0) + 1
    ),
    /* Audit fields... */
  }
)
```

### ID Field Resolution

**When mockup uses text but data model has Integer ID field:**

**Preferred: Hardcoded ID mapping with comment**
```sail
/* Status ID mapping documented above button section */
a!save(ri!record['recordType!Type.fields.statusId'], 3)  /* 3 = Approved */
```

**Add mapping comment at top of button section:**
```sail
/* Status ID Mapping (verified against database/requirements):
 * 1 = Value1
 * 2 = Value2
 * 3 = Value3
 */
```

### Integration with Existing Patterns

This pattern **extends** existing form action button patterns:
- **Create Button** `{#form-buttons.action-buttons.create}` (line 832) → Add status/action fields if needed
- **Update Button** `{#form-buttons.action-buttons.update}` (line 854) → Add status/action fields if needed
- **Cancel Button** (line 886) → No changes, pattern already complete
- **Audit Fields** `{#form-buttons.audit-fields}` (line 689) → Always apply to all submit buttons

**Field-setting beyond standard audit fields:**
- Status/state transitions based on button action
- Action-specific user/timestamp fields ([action]By, [action]Date)
- Counter increments with null safety
- Any read-only field displaying system-controlled values

---

## TODO-CONVERTER Comment Cleanup {#form-buttons.cleanup}

**After implementing field-setting logic, clean up comments appropriately:**

### Rule 1: Remove Implemented Field-Setting Comments

```sail
/* ❌ MOCKUP - Before conversion */
/* TODO-CONVERTER: Set status to "Approved" */
/* TODO-CONVERTER: Set approvedBy to current user */
/* TODO-CONVERTER: Set approvedDate to current timestamp */
a!buttonWidget(
  label: "Approve",
  saveInto: { a!save(local!status, "Approved") }
)

/* ✅ FUNCTIONAL - After conversion (comments removed) */
/* Status ID Mapping: 1=Submitted, 2=Pending, 3=Approved, 4=Denied */
a!buttonWidget(
  label: "Approve",
  submit: true,
  saveInto: {
    a!save(ri!application['...statusId'], 3),  /* Approved */
    a!save(ri!application['...approvedBy'], loggedInUser()),
    a!save(ri!application['...approvedDate'], now()),
    a!save(ri!application['...modifiedBy'], loggedInUser()),
    a!save(ri!application['...modifiedOn'], now())
  }
)
```

**Why remove?** The field-setting instructions have been implemented in code. Comments would be redundant and confusing.

### Rule 2: Convert Process Model Activities to TODO

```sail
/* ❌ MOCKUP - Wrong comment type */
/* TODO-CONVERTER: Send approval email with Enrole link */
/* TODO-CONVERTER: Trigger DocuSign for signature */

/* ✅ FUNCTIONAL - Corrected to TODO (not TODO-CONVERTER) */
/* TODO: Configure process model to send approval email with Enrole link after form submission */
/* TODO: Configure process model to trigger DocuSign for approver signature */
```

**Why convert?** Process model activities are not handled by the interface converter. They require process model configuration outside the SAIL interface.

**Common process model activities:**
- Send email/notification
- Trigger DocuSign
- Start subprocess
- Call integration
- Update external system

### Rule 3: Keep Data Model Gap Comments Unchanged

```sail
/* ✅ Keep as-is - Data model enhancement needed */
/* TODO-DATA-MODEL: Add approvedBy field to OUTREACH_TRAINER */
a!save(ri!record['...approvedBy'], loggedInUser())  /* Field doesn't exist yet */
```

**Why keep?** These indicate missing database fields that must be added before the interface can function properly.

### Cleanup Checklist

After implementing button field-setting:
- [ ] All field-setting TODO-CONVERTER comments removed (Set X, Increment Y, Add audit)
- [ ] Process model activity comments converted to TODO (Send email, Trigger, Configure)
- [ ] Data model gap comments remain as TODO-DATA-MODEL
- [ ] Only unimplemented field-setting retains TODO-CONVERTER prefix
- [ ] ID mapping comments added where applicable
