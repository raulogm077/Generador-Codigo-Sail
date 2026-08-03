# a!signatureField — Usage Instructions

`a!signatureField` allows users to capture and save a **.png signature file** directly in Appian. It is a native component (no DocuSign required).

> ⚠️ **CRITICAL CONSTRAINT:** Only usable in **start forms or task forms**. To use it elsewhere, you must wrap submission with `a!submitUploadedFiles()` in the saveInto of a button or link.

---

## Function signature (verified against Appian 24.3 / latest docs)

```sail
a!signatureField(
  label,                  /* Text — field label */
  labelPosition,          /* Text — "ABOVE" (default) | "ADJACENT" | "JUSTIFIED" | "COLLAPSED" */
  instructions,           /* Text */
  helpTooltip,            /* Text */
  target,                 /* Document or Folder — folder where signature .png is saved */
  fileName,               /* Text — custom file name; timestamp used if not provided */
  fileDescription,        /* Text — description for the saved file */
  value,                  /* Document — the signature document */
  saveInto,               /* Save */
  required,               /* Boolean, default false */
  requiredMessage,        /* Text */
  buttonStyle,            /* Text — "PRIMARY" | "SECONDARY" (default) | "STANDARD" | "LINK" */
  buttonSize,             /* Text — "SMALL" (default) | "STANDARD" | "LARGE" */
  readOnly,               /* Boolean, default false */
  disabled,               /* Boolean, default false */
  validationGroup,        /* Text */
  accessibilityText,      /* Text */
  showWhen,               /* Boolean, default true */
  marginAbove,            /* Text — "NONE" (default) | "EVEN_LESS" | "LESS" | "STANDARD" | "MORE" | "EVEN_MORE" */
  marginBelow             /* Text — "NONE" | "EVEN_LESS" | "LESS" | "STANDARD" (default) | "MORE" | "EVEN_MORE" */
)
```

**Important:**
- ⛔ Does NOT have a `validations` parameter (use `requiredMessage` for the only built-in validation)
- ⛔ Cannot upload multiple signatures or a pre-existing signature

---

## Permissions and submission

1. **Editor permissions required.** Users must have at least **Editor** on the `target` folder/document. For portals, give the portal service account Editor permissions.
2. **Submission triggers saving.** The signature lives in a temporary folder until the submit button is clicked (`submit: true`). At that point it's moved to the `target` folder.
3. **30-day auto-delete.** If a signature is uploaded but never submitted, the temporary file is deleted after 30 days.

---

## Common patterns

### Signature in a start form or task
```sail
a!localVariables(
  local!signature,
  a!formLayout(
    label: "Approval form",
    contents: {
      a!signatureField(
        label: "Signature",
        labelPosition: "ABOVE",
        fileName: loggedInUser() & "_signature_" & today(),
        fileDescription: "Approval signature for case " & ri!caseId,
        target: cons!SIGNATURES_FOLDER,
        value: local!signature,
        saveInto: local!signature,
        required: true
      )
    },
    buttons: a!buttonLayout(
      primaryButtons: {
        a!buttonWidget(
          label: "Submit",
          style: "SOLID",
          loadingIndicator: true,
          submit: true   /* CRITICAL: signature is saved on submit */
        )
      }
    )
  )
)
```

### Signature outside a start form/task (with a!submitUploadedFiles)
```sail
a!localVariables(
  local!signature,
  local!submissionSuccessful,
  {
    a!signatureField(
      label: "Signature",
      target: cons!SIGNATURES_FOLDER,
      value: local!signature,
      saveInto: local!signature
    ),
    a!buttonArrayLayout(
      buttons: a!buttonWidget(
        label: "Submit",
        style: "SOLID",
        saveInto: a!submitUploadedFiles(
          onSuccess: a!save(local!submissionSuccessful, true),
          onError: a!save(local!submissionSuccessful, false)
        )
      )
    )
  }
)
```

---

## File-name sanitization

If any of these characters appear in the signature's file name, they're replaced by underscores:
```
\ / " ; : | ? ' < > *
```

---

## Cancel flow for forms

In start forms or tasks, the **cancel button** typically has `submit: true` too — meaning a signature would also be saved on cancel. To avoid orphan signatures, configure the **cancel flow** in your process model to delete the unnecessary file using the Delete Document smart service.

---

## Validation Checklist

- [ ] `target` is a Folder or Document reference (typically a constant)
- [ ] In a start form/task → submit button has `submit: true`
- [ ] Outside a start form/task → submit button uses `a!submitUploadedFiles()` in `saveInto`
- [ ] `buttonStyle` is one of `PRIMARY` / `SECONDARY` / `STANDARD` / `LINK`
- [ ] `buttonSize` is one of `SMALL` / `STANDARD` / `LARGE`
- [ ] No `validations` parameter used (signatureField does not support it)
- [ ] If `marginAbove` / `marginBelow` are used, values come from the standard 6-value enum
- [ ] Cancel flow handles orphan signature cleanup if needed
- [ ] User/portal service account has Editor permissions on `target`

---

## Feature compatibility

| Feature | Compatibility |
|---|---|
| Portals | ✅ Compatible (test in published portal) |
| Offline Mobile | ✅ Compatible |
| Process Reports | ❌ Incompatible |
| Process Events | ❌ Incompatible |

Docs: <https://docs.appian.com/suite/help/latest/Signature_Component.html>
