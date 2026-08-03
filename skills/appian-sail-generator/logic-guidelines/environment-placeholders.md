# Handling Non-Existent Constants and Environment Objects

> **Parent guide:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `/conversion-guidelines/common-conversion-patterns.md` - Query and record patterns
> - `/conversion-guidelines/form-conversion-module.md` - Form-specific patterns

**Never assume constants, process models, or environment-specific objects exist. Always use placeholders with TODO comments.**

---

## The Problem

Generated code often references objects that don't exist in the target environment:
- Constants (`cons!FOLDER_NAME`, `cons!PROCESS_MODEL`)
- Process models (for `a!startProcess()`)
- Document folders (for file upload targets)
- Integration objects
- Expression rules

---

## Correct Pattern - Placeholder with TODO

```sail
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
    case: local!caseData,
    submittedBy: loggedInUser()
  }
)
```

---

## Wrong Pattern - Assuming Objects Exist

```sail
/* DON'T DO THIS */
a!fileUploadField(
  target: cons!CASE_DOCUMENTS_FOLDER,  /* This constant may not exist! */
  ...
)

a!startProcess(
  processModel: cons!SUBMIT_CASE_PROCESS,  /* May not exist! */
  ...
)
```

---

## TODO Comment Format

```sail
/* TODO: Add constant value for [specific purpose] */
/* TODO: Configure [object type] - [what it should reference] */
/* TODO: Add integration object for [external system] */
```

---

## Common Placeholders by Object Type

| Object Type | Placeholder | TODO Comment |
|-------------|-------------|--------------|
| Document folder | `target: null` | `/* TODO: Add constant for [folder purpose] */` |
| Process model | `processModel: null` | `/* TODO: Add constant for [process purpose] */` |
| Integration | `integration: null` | `/* TODO: Add integration object for [system] */` |
| Expression rule | Inline logic | `/* TODO: Replace with rule![ruleName] */` |
| Constant value | Hardcoded value | `/* TODO: Replace with cons![constantName] */` |

---

## Why This Matters

1. **Generated code runs immediately** for UI/UX testing
2. **Clear configuration points** - developers search for "TODO"
3. **Self-documenting** - explains what needs configuration
4. **Prevents runtime errors** from missing objects

---

## Related Documentation

- `/conversion-guidelines/common-conversion-patterns.md` - Query and record patterns
- `/conversion-guidelines/form-conversion-module.md` - Form-specific patterns
