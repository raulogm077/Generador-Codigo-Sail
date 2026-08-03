# a!toggleField — Usage Instructions

`a!toggleField` displays a toggle (on/off switch) that saves a `true` or `false` value. Works well for **activation and state changes** that take immediate effect.

> ⚠️ **Don't use toggles in forms.** Use `a!booleanCheckboxField` instead. Toggles are for things like "Enable dark mode" or "Show inactive users" — settings and filters where the change is immediate.

---

## Function signature (per official Appian docs)

```sail
a!toggleField(
  choiceLabel,            /* Text — label next to the toggle */
  helpTooltip,            /* Text — help icon tooltip, max 500 chars */
  value,                  /* Boolean — true = on, false/null = off */
  saveInto,               /* List of Save */
  showWhen,               /* Boolean, default true */
  required,               /* Boolean, default false */
  requiredMessage,        /* Text — default: "Enable the toggle to continue" */
  validations,            /* List of Text */
  validationGroup,        /* List of Text */
  disabled,               /* Boolean, default false */
  accessibilityText,      /* Text */
  marginAbove,            /* Text — "NONE" (default) | "EVEN_LESS" | "LESS" | "STANDARD" | "MORE" | "EVEN_MORE" */
  marginBelow,            /* Text — "NONE" | "EVEN_LESS" | "LESS" | "STANDARD" (default) | "MORE" | "EVEN_MORE" */
  choicePosition          /* Text — "START" (default) | "END" — toggle on left or right of choice label */
)
```

**Important: NO `label`, NO `labelPosition`, NO `instructions`.** Only `choiceLabel`. This is the same shape as `a!booleanCheckboxField`.

---

## Common patterns

### Basic toggle for a setting
```sail
a!toggleField(
  choiceLabel: "Enable email notifications",
  value: local!notificationsEnabled,
  saveInto: local!notificationsEnabled
)
```

### Toggle to filter data
```sail
a!toggleField(
  choiceLabel: "Show inactive users",
  value: local!includeInactive,
  saveInto: local!includeInactive
)
```

### Required toggle with custom message
```sail
a!toggleField(
  choiceLabel: "I accept the terms",
  value: local!acceptedTerms,
  saveInto: local!acceptedTerms,
  required: true,
  requiredMessage: "You must accept the terms to continue"
)
```

> 🚨 **But if it's a form acceptance like that, use `a!booleanCheckboxField` instead** — `a!toggleField` should not be used in forms.

---

## When to choose which boolean component

| Use case | Component |
|---|---|
| "Enable dark mode" toggle in settings | `a!toggleField` |
| "Show inactive users" filter | `a!toggleField` |
| "I agree to the terms" in a form | `a!booleanCheckboxField` |
| Single-item agreement checkbox | `a!booleanCheckboxField` |
| Toggle that triggers a workflow change | `a!toggleField` |

---

## Validation Checklist

- [ ] Used `choiceLabel` (NOT `label`)
- [ ] No `labelPosition` or `instructions` parameters
- [ ] `value` is a Boolean (not a string/number)
- [ ] `choicePosition` is `"START"` or `"END"` if set
- [ ] `marginAbove` / `marginBelow` use the standard 6-value enum
- [ ] Not used inside a `a!formLayout`'s contents — if it is, replace with `a!booleanCheckboxField`

---

## Feature compatibility (per official Appian docs)

| Feature | Compatibility |
|---|---|
| Portals | ✅ Compatible |
| Offline Mobile | ✅ Compatible |
| Process Reports | ❌ Incompatible |
| Process Events | ❌ Incompatible |
| Process Autoscaling | ❌ Incompatible |

Docs: <https://docs.appian.com/suite/help/latest/Toggle_Component.html>
