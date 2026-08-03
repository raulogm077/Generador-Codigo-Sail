# a!booleanCheckboxField — Usage Instructions

`a!booleanCheckboxField` displays a **single checkbox** that saves a `true` or `false` value. Use for **confirmations in forms**, such as agreeing to terms.

> ⚠️ **For activation/state changes outside of forms** (toggles like "Enable dark mode"), use `a!toggleField` instead. Both components have the **exact same signature** — the difference is semantic.

---

## Function signature (per official Appian docs)

```sail
a!booleanCheckboxField(
  choiceLabel,            /* Text — label next to the checkbox */
  helpTooltip,            /* Text — help icon tooltip, max 500 chars */
  value,                  /* Boolean — true = checked, false/null = unchecked */
  saveInto,               /* List of Save */
  showWhen,               /* Boolean, default true */
  required,               /* Boolean, default false */
  requiredMessage,        /* Text — default: "Select the checkbox to continue" */
  validations,            /* List of Text */
  validationGroup,        /* List of Text */
  disabled,               /* Boolean, default false */
  accessibilityText,      /* Text */
  marginAbove,            /* Text — "NONE" (default) | "EVEN_LESS" | "LESS" | "STANDARD" | "MORE" | "EVEN_MORE" */
  marginBelow,            /* Text — "NONE" | "EVEN_LESS" | "LESS" | "STANDARD" (default) | "MORE" | "EVEN_MORE" */
  choicePosition          /* Text — "START" (default) | "END" — checkbox on left or right of choice label */
)
```

**Important: NO `label`, NO `labelPosition`, NO `instructions`.** Only `choiceLabel`. Same shape as `a!toggleField`.

---

## Common patterns

### Terms-and-conditions form acceptance
```sail
a!localVariables(
  local!termsAgreed,
  {
    a!booleanCheckboxField(
      choiceLabel: "I agree to the terms and conditions",
      value: local!termsAgreed,
      saveInto: local!termsAgreed,
      required: true,
      requiredMessage: "Accept the terms to continue"
    ),
    a!buttonArrayLayout(
      buttons: {
        a!buttonWidget(label: "Submit", submit: true, style: "SOLID")
      }
    )
  }
)
```

### Multiple agreements in a form
```sail
a!sectionLayout(
  label: "Confirmations",
  contents: {
    a!booleanCheckboxField(
      choiceLabel: "I confirm the information is accurate",
      value: local!confirmAccurate,
      saveInto: local!confirmAccurate,
      required: true
    ),
    a!booleanCheckboxField(
      choiceLabel: "I authorize the processing of my data",
      value: local!confirmConsent,
      saveInto: local!confirmConsent,
      required: true
    )
  }
)
```

---

## Toggle vs Boolean Checkbox — which to use

| Scenario | Component |
|---|---|
| Form requires user confirmation | `a!booleanCheckboxField` |
| Settings page with on/off switches | `a!toggleField` |
| Filter that immediately changes visible data | `a!toggleField` |
| Multi-item selection (none/one/many) | `a!checkboxField` (NOT this component) |

---

## In editable grids

Both `a!booleanCheckboxField` and `a!toggleField` work in editable grids, **but only the checkbox/toggle shows — the `choiceLabel` is hidden.** Use the column heading to describe what the field is for.

> 💡 For **selecting rows** in an editable grid, prefer the grid's built-in row selection parameters rather than adding a boolean checkbox column.

---

## Validation Checklist

- [ ] Used `choiceLabel` (NOT `label`)
- [ ] No `labelPosition` or `instructions` parameters
- [ ] `value` is a Boolean
- [ ] If `required` is true, expect a validation message when value is `false` or `null`
- [ ] Used inside a form/task context for terms/confirmations (use `a!toggleField` for activation outside forms)

---

## Feature compatibility (per official Appian docs)

| Feature | Compatibility |
|---|---|
| Portals | ✅ Compatible |
| Offline Mobile | ✅ Compatible |
| Process Reports | ❌ Incompatible |
| Process Events | ❌ Incompatible |
| Process Autoscaling | ❌ Incompatible |

Docs: <https://docs.appian.com/suite/help/latest/Boolean_Checkbox_Component.html>
