# Form Conversion - Data Model Handling {#form-data-model}

> **Parent guide:** `/conversion-guidelines/form-conversion-module.md`
>
> **Related modules:**
> - `/conversion-guidelines/form-conversion-ri-patterns.md` - Rule input patterns
> - `/conversion-guidelines/form-conversion-relationships.md` - Relationship patterns
> - `/conversion-guidelines/form-conversion-buttons-actions.md` - Button actions

---

## 📑 Section Navigation {#form-data-model.nav}

- `{#form-data-model.mismatch}` - Data model mismatch strategies
- `{#form-data-model.mistakes}` - Common form conversion mistakes
- `{#form-data-model.multi-type-entry}` - Multi-type form entry patterns
- `{#form-data-model.parameter-validation}` - Button and wizard parameter validation
- `{#form-data-model.encrypted-field}` - Encrypted text field limitation
- `{#form-data-model.checklist}` - Form conversion checklist

---

## Data Model Mismatch Strategies {#form-data-model.mismatch}

When data model fields don't match interface requirements, use these strategies:

### Strategy 1: Use Available Fields {#form-data-model.mismatch.available-fields}

**When to use:** Minor semantic differences (e.g., `firstName` + `lastName` vs `fullName`)

**How it works:**
- Use existing fields with different structure
- Add comment explaining the mapping decision
- Document in interface header

**Example:**
```sail
/* NOTE: Using firstName + lastName fields from Client instead of fullName */

a!textField(
  label: "First Name",
  value: a!defaultValue(
    ri!case['recordType!Case.relationships.client.fields.firstName'],
    ""
  ),
  saveInto: ri!case['recordType!Case.relationships.client.fields.firstName']
),
a!textField(
  label: "Last Name",
  value: a!defaultValue(
    ri!case['recordType!Case.relationships.client.fields.lastName'],
    ""
  ),
  saveInto: ri!case['recordType!Case.relationships.client.fields.lastName']
)
```

### Strategy 2: Local Variables for Reference Data {#form-data-model.mismatch.reference-data}

**When to use:** Missing reference tables (e.g., Case Status, Priority Levels, Case Types)

**How it works:**
- Define local variable with hardcoded list
- Use for dropdown choice labels and values
- Document data source in comment

**Example:**
```sail
a!localVariables(
  /* Case priorities reference data - used for dropdown options */
  local!casePriorities: {
    a!map(id: 1, label: "Low", value: "LOW"),
    a!map(id: 2, label: "Medium", value: "MEDIUM"),
    a!map(id: 3, label: "High", value: "HIGH"),
    a!map(id: 4, label: "Critical", value: "CRITICAL")
  },

  {
    a!dropdownField(
      label: "Priority",
      choiceLabels: local!casePriorities.label,
      choiceValues: local!casePriorities.value,
      value: ri!case['recordType!Case.fields.priority'],
      saveInto: ri!case['recordType!Case.fields.priority']
    )
  }
)
```

**Key Points:**
1. Use `a!map()` for reference data (NOT record type constructors)
2. Document with comment explaining this is temporary/reference data
3. Reference data stays as `local!` - only entity data uses `ri!`

---

## Common Form Conversion Mistakes {#form-data-model.mistakes}

### Mistake 1: Copying ri! to local variables

```sail
/* ❌ WRONG - Creates disconnected copy */
local!caseCopy: ri!case,
a!textField(
  value: local!caseCopy['recordType!Case.fields.title'],
  saveInto: local!caseCopy['recordType!Case.fields.title']
)
/* Saves only update local!caseCopy, not ri!case */

/* ✅ CORRECT - Direct ri! binding */
a!textField(
  value: ri!case['recordType!Case.fields.title'],
  saveInto: ri!case['recordType!Case.fields.title']
)
```

### Mistake 2: Initializing ri! inside interface

```sail
/* ❌ WRONG - Cannot initialize parameters */
ri!isUpdate: false(),

/* ✅ CORRECT - Document in comments only */
/* ri!isUpdate (Boolean) - passed from calling context */
```

### Mistake 3: Missing null checks on ri!

```sail
/* ❌ WRONG - Will crash if ri!case is null */
value: ri!case['recordType!Case.fields.title']

/* ✅ CORRECT - Safe for null ri! */
value: a!defaultValue(
  ri!case['recordType!Case.fields.title'],
  ""
)
```

### Mistake 4: Using a!map() for form data

Use record type constructors, NOT `a!map()`. See `/conversion-guidelines/form-conversion-relationships.md{#form-relationships.record-constructors}` for full details and examples.

---

## Multi-Type Form Entry Pattern {#form-data-model.multi-type-entry}

When a single relationship contains multiple types of records (e.g., Phone Contacts AND Email Contacts in one table, or Internal Notes AND External Communications in one list):

### Pattern: Use Type ID Field

**Data Model Setup:**
- Single record type: `CaseContact`
- Type field: `contactMethodTypeId` (1 = Phone, 2 = Email)
- Shared fields: `contactName`, `contactDate`, `notes`
- Phone-specific: `phoneNumber`, `callDuration`
- Email-specific: `emailAddress`, `emailSubject`

**UI Implementation:**
```sail
a!forEach(
  items: ri!case['recordType!Case.relationships.caseContacts'],
  expression: a!cardLayout(
    contents: {
      /* Card title based on type */
      a!richTextDisplayField(
        labelPosition: "COLLAPSED",
        value: a!richTextItem(
          text: if(
            fv!item['recordType!CaseContact.fields.contactMethodTypeId'] = 2,
            "Email Contact",
            "Phone Contact"
          ),
          size: "MEDIUM",
          style: "STRONG"
        )
      ),

      /* Phone contact fields - show when type = 1 */
      if(
        fv!item['recordType!CaseContact.fields.contactMethodTypeId'] = 1,
        {
          a!textField(
            label: "Phone Number",
            value: fv!item['recordType!CaseContact.fields.phoneNumber'],
            saveInto: fv!item['recordType!CaseContact.fields.phoneNumber']
          ),
          a!integerField(
            label: "Call Duration (minutes)",
            value: fv!item['recordType!CaseContact.fields.callDuration'],
            saveInto: fv!item['recordType!CaseContact.fields.callDuration']
          )
        },
        {}
      ),

      /* Email contact fields - show when type = 2 */
      if(
        fv!item['recordType!CaseContact.fields.contactMethodTypeId'] = 2,
        {
          a!textField(
            label: "Email Address",
            value: fv!item['recordType!CaseContact.fields.emailAddress'],
            saveInto: fv!item['recordType!CaseContact.fields.emailAddress']
          ),
          a!textField(
            label: "Subject Line",
            value: fv!item['recordType!CaseContact.fields.emailSubject'],
            saveInto: fv!item['recordType!CaseContact.fields.emailSubject']
          )
        },
        {}
      )
    }
  )
)
```

**Add Buttons:**
```sail
a!buttonArrayLayout(
  buttons: {
    a!buttonWidget(
      label: "Add Phone Contact",
      icon: "phone",
      style: "OUTLINE",
      saveInto: {
        a!save(
          ri!case['recordType!Case.relationships.caseContacts'],
          append(
            ri!case['recordType!Case.relationships.caseContacts'],
            'recordType!CaseContact'(
              'recordType!CaseContact.fields.contactMethodTypeId': 1,  /* Set type on creation */
              'recordType!CaseContact.fields.contactName': null,
              'recordType!CaseContact.fields.phoneNumber': null,
              'recordType!CaseContact.fields.callDuration': null
            )
          )
        )
      }
    ),
    a!buttonWidget(
      label: "Add Email Contact",
      icon: "envelope",
      style: "OUTLINE",
      saveInto: {
        a!save(
          ri!case['recordType!Case.relationships.caseContacts'],
          append(
            ri!case['recordType!Case.relationships.caseContacts'],
            'recordType!CaseContact'(
              'recordType!CaseContact.fields.contactMethodTypeId': 2,  /* Set type on creation */
              'recordType!CaseContact.fields.contactName': null,
              'recordType!CaseContact.fields.emailAddress': null,
              'recordType!CaseContact.fields.emailSubject': null
            )
          )
        )
      }
    )
  },
  align: "START"
)
```

**Key Points:**
1. **Set `typeId` immediately on record creation** - Don't rely on other field values to infer type
2. **Use `typeId` for all conditional display logic** - Check the type field, not whether specific fields are null/empty
3. **Don't use null/empty field checks for type detection** - Fields can be null for many reasons unrelated to type
4. **Each button creates the same record type** - Only difference is the `typeId` value and which fields are initialized
5. **Initialize type-specific fields to null** - Makes it clear which fields belong to which type

---

## Button and Wizard Parameter Validation {#form-data-model.parameter-validation}

### a!buttonWidget() Parameter Rules {#form-data-model.parameter-validation.button}

**Valid Parameters ONLY:**
- `label`, `value`, `saveInto`, `submit`, `style`, `color`, `size`, `icon`
- `disabled`, `showWhen`, `validate`, `skipValidation`
- `loadingIndicator`, `confirmMessage`, `confirmHeader`, `link`

**❌ INVALID Parameters:**
- `validations` (does NOT exist - use form-level validations instead)

**✅ Validation Placement:**
- **Form validations**: On `a!formLayout()` validations parameter
- **Field validations**: On individual field components

### a!wizardLayout() Parameter Rules {#form-data-model.parameter-validation.wizard}

**Valid Parameters:**
- `titleBar`, `isTitleBarFixed`, `showTitleBarDivider`, `backgroundColor`
- `style`, `showWhen`, `steps`, `contentsWidth`, `showStepHeadings`
- `focusOnFirstInput`, `primaryButtons`, `secondaryButtons`
- `showButtonDivider`, `isButtonFooterFixed`

**❌ INVALID Parameters:**
- `validations` (does NOT exist on wizard layout)

**✅ Validation Placement for Wizards:**
- **Form-level validations**: Place on individual `a!buttonWidget()` in `primaryButtons`
- **Field validations**: Place on individual field components within steps

---

## Encrypted Text Field Limitation {#form-data-model.encrypted-field}

**CRITICAL**: `a!encryptedTextField()` is NOT compatible with synced record types.

**Rule**: When synced record types require password or sensitive text fields:
1. Use `a!textField()` instead of `a!encryptedTextField()`
2. Add `a!messageBanner()` with `backgroundColor: "WARN"` above the field
3. Include clear message explaining the technical limitation
4. Mark as "Review required" to flag for stakeholder attention

**Example:**
```sail
a!messageBanner(
  backgroundColor: "WARN",
  message: "Note: Password field uses standard text input due to synced record type limitation. Review security requirements."
),
a!textField(
  label: "Password",
  value: ri!user['recordType!User.fields.password'],
  saveInto: ri!user['recordType!User.fields.password'],
  masked: true
)
```

---

## Form Conversion Checklist {#form-data-model.checklist}

Before completing form conversion:

- [ ] Header comment documents ALL rule inputs with Name/Type/Description (including ri!cancel)
- [ ] All form field bindings use `ri!record[field]` NOT local variables
- [ ] Create button sets ALL 4 audit fields (createdBy, createdOn, modifiedBy, modifiedOn)
- [ ] Update button sets only modifiedBy and modifiedOn
- [ ] Create button has `showWhen: not(a!defaultValue(ri!isUpdate, false()))` with null safety
- [ ] Update button has `showWhen: a!defaultValue(ri!isUpdate, false())` with null safety
- [ ] Both submit buttons have `submit: true` and `validate: true`
- [ ] Cancel button uses `submit: true` with `saveInto: a!save(ri!cancel, true)`
- [ ] All TODO-CONVERTER comments processed for field-setting instructions
- [ ] Read-only/disabled fields have values set in button saveInto
- [ ] Button labels matched to actions (Approve→"Approved", Deny→"Denied", etc.)
- [ ] Status/action fields set appropriately for each button
- [ ] Field types verified in data-model-context.md (Text vs ID fields)
- [ ] ID fields use hardcoded values with mapping comment
- [ ] Counter fields use a!defaultValue() for null safety
- [ ] Action-specific fields follow naming convention ([action]By, [action]Date)
- [ ] Mode-specific logic uses `ri!isUpdate` flag
- [ ] No `local!` copies of `ri!` variables
- [ ] All `ri!` access has null safety where needed
- [ ] One-to-many relationships use `ri!record['...relationships.related']` directly (no queries or local copies)
- [ ] Related record add/remove uses `append()`/`remove()` on the relationship field
- [ ] New related records use record type constructor `'recordType!Type'(...)` NOT `a!map()`
- [ ] Wizard step count matches mockup
- [ ] All required field validations preserved
