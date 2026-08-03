# Record / User / Group Pickers — Usage Instructions

This file covers the four "picker" components that select existing records, users, or groups via an autocompleting input:

- `a!pickerFieldRecords` — select records of a specific record type
- `a!pickerFieldUsers` — select users
- `a!pickerFieldGroups` — select groups
- `a!pickerFieldUsersAndGroups` — select users and/or groups

> ⚠️ The naming convention is `pickerFieldX`, **not** `XPickerField`. Common mistake.

---

## a!pickerFieldRecords

```sail
a!pickerFieldRecords(
  label,                  /* Text */
  labelPosition,          /* "ABOVE" (default) | "ADJACENT" | "JUSTIFIED" | "COLLAPSED" */
  instructions,           /* Text */
  helpTooltip,            /* Text */
  placeholder,            /* Text */
  maxSelections,          /* Number (Integer) */
  recordType,             /* RecordType — REQUIRED */
  filters,                /* a!queryLogicalExpression() OR list of a!queryFilter() */
  value,                  /* Any Type — array of selected records */
  saveInto,               /* List of Save */
  required,               /* Boolean */
  requiredMessage,        /* Text */
  readOnly,               /* Boolean */
  disabled,               /* Boolean */
  validations,            /* List of Text */
  validationGroup,        /* Text */
  accessibilityText,      /* Text */
  showWhen,               /* Boolean */
  showRecordLinks,        /* Boolean, default true — set false for reference data */
  marginAbove,            /* NONE (default), EVEN_LESS, LESS, STANDARD, MORE, EVEN_MORE */
  marginBelow             /* NONE, EVEN_LESS, LESS, STANDARD (default), MORE, EVEN_MORE */
)
```

### Basic example
```sail
a!localVariables(
  local!selectedEmployee,
  a!pickerFieldRecords(
    label: "Choose an Employee",
    recordType: recordType!Employee,
    value: local!selectedEmployee,
    saveInto: local!selectedEmployee
  )
)
```

### With filters
```sail
a!pickerFieldRecords(
  label: "Choose an Active Engineering Employee",
  recordType: recordType!Employee,
  filters: a!queryLogicalExpression(
    operator: "AND",
    filters: {
      a!queryFilter(
        field: recordType!Employee.fields.department,
        operator: "=",
        value: "Engineering"
      ),
      a!queryFilter(
        field: recordType!Employee.fields.isActive,
        operator: "=",
        value: true
      )
    }
  ),
  value: local!selectedEmployee,
  saveInto: local!selectedEmployee
)
```

### Reference data — hide record links
```sail
a!pickerFieldRecords(
  label: "Choose a Priority",
  recordType: recordType!Priority,
  value: local!selectedPriority,
  saveInto: local!selectedPriority,
  showRecordLinks: false   /* Priority is reference data; no need to link to its summary */
)
```

### ⚠️ Caveats

- Max 25 suggestions shown.
- Only records the user has permissions to see appear.
- For **service-backed record types**, every keystroke triggers a web service call — use only when low selection counts are expected.
- ⛔ **Incompatible with Portals and Offline Mobile.**

---

## a!pickerFieldUsers

```sail
a!pickerFieldUsers(
  label, instructions, required, requiredMessage,
  readOnly, disabled, maxSelections,
  groupFilter,            /* Group — only users from this group are suggested */
  value, validations, validationGroup, saveInto,
  labelPosition, placeholder, helpTooltip,
  accessibilityText, showWhen, marginAbove, marginBelow
)
```

### Basic example
```sail
a!pickerFieldUsers(
  label: "Assign to",
  placeholder: "Type to search users",
  value: local!assignee,
  saveInto: local!assignee
)
```

### Filtered by group
```sail
a!pickerFieldUsers(
  label: "Pick a reviewer",
  groupFilter: cons!REVIEWERS_GROUP,
  value: local!reviewer,
  saveInto: local!reviewer,
  required: true
)
```

### ⚠️ Caveats

- All user members of the group are suggested when `groupFilter` is set (including indirect members and users by rule).
- The user viewing the picker must have permission to view the users passed to `value`.
- Component always saves an array.

---

## a!pickerFieldGroups

Similar shape to `a!pickerFieldUsers`. Filters and constraints work the same way.

```sail
a!pickerFieldGroups(
  label: "Select target groups",
  value: local!groups,
  saveInto: local!groups,
  maxSelections: 5
)
```

---

## a!pickerFieldUsersAndGroups

Combined picker for both users and groups.

```sail
a!pickerFieldUsersAndGroups(
  label, instructions, required, readOnly, disabled,
  maxSelections, groupFilter, value, validations,
  saveInto, validationGroup, requiredMessage,
  labelPosition, placeholder, helpTooltip,
  accessibilityText, showWhen, marginAbove, marginBelow
)
```

---

## Validation Checklist (all pickers)

- [ ] The function name is `a!pickerFieldX` (NOT `a!XPickerField`)
- [ ] `recordType` is provided for `a!pickerFieldRecords` (required)
- [ ] `value` is an array (component always saves arrays)
- [ ] `labelPosition` uses the standard 4-value enum
- [ ] `marginAbove/Below` uses the 6-value enum
- [ ] For `a!pickerFieldRecords`: filters use `a!queryLogicalExpression` or `a!queryFilter`
- [ ] For `a!pickerFieldRecords`: NOT used in a Portal or Offline Mobile context
- [ ] For user/group pickers: `groupFilter` is a Group reference, not a list

---

## When to use what

| Need | Picker |
|---|---|
| Pick records (Employees, Cases, Orders…) | `a!pickerFieldRecords` |
| Pick Appian users | `a!pickerFieldUsers` |
| Pick Appian groups | `a!pickerFieldGroups` |
| Pick a mix of users and groups | `a!pickerFieldUsersAndGroups` |
| Pick from an arbitrary in-memory list (not a record type) | `a!customPickerField` (custom picker) |

Docs:
- <https://docs.appian.com/suite/help/latest/Record_Picker_Component.html>
- <https://docs.appian.com/suite/help/latest/User_Picker_Component.html>
- <https://docs.appian.com/suite/help/latest/Group_Picker_Component.html>
- <https://docs.appian.com/suite/help/latest/User_and_Group_Picker_Component.html>
