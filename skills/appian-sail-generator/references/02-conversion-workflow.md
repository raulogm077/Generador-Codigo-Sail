# Phase 2 — Functional Conversion Workflow

Phase 2 takes a Phase 1 mockup and turns it into a data-driven interface that queries live record-type data and accepts `ri!` rule inputs. This file is the high-level decision playbook; the canonical, exhaustive guidance is `conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md` (the navigation index that points at focused modules per topic).

The actual conversion work is performed by the `sail-dynamic-converter` agent — see `agents/sail-dynamic-converter.md`. **Don't attempt conversion without invoking that agent** (or, in environments without sub-agent delegation, without reading and following its instructions fully). Make-up UUIDs or field references are not acceptable failure modes.

---

## Preconditions

Before invoking the converter, verify all four:

1. ✅ **A mockup file exists** at `output/<name>.sail` (Phase 1 output). The converter reads from disk — it does not generate from scratch.
2. ✅ **A data-model-context.md file exists** at `context/data-model-context.md` describing every record type the interface will use (UUIDs, fields with UUIDs and data types, relationships with UUIDs, actions). See `references/03-data-model-context-format.md` for the format and how to generate it from XML.
3. ✅ **The user has explicitly asked for a functional interface** — verbs like "make this functional", "convert to record queries", "connect to our Cases", "make it dynamic". A mockup request alone does not authorise Phase 2.
4. ✅ **(Forms only) — is this a start form for a process model?** If yes, check whether a `model.json` is available describing `process_variables`. If yes, the `ri!` variable names must match `process_variables[].variable_name` *exactly*. The `sail-dynamic-converter` agent file has the precise protocol for this case.

If any precondition is missing, stop and ask the user to provide what's missing. Don't fabricate.

---

## Conversion decision tree

The converter's job changes meaningfully depending on what kind of interface the mockup is. Identify the type before delegating, so you can give the agent the right context.

```
Is the mockup a form (has a!formLayout or a!wizardLayout with submit buttons)?
├── YES → Form conversion path
│   ├── Is it a CREATE form, an UPDATE form, or both?
│   ├── Is it a start form for a process model (has model.json)?
│   ├── Which fields map to which record-type fields?
│   ├── Are there relationships involved (e.g. selecting a parent record)?
│   └── See: conversion-guidelines/form-conversion-module.md (nav index)
│
└── NO  → Display conversion path
    ├── Grids → conversion-guidelines/display-conversion-grids.md
    ├── Charts → conversion-guidelines/display-conversion-charts.md
    ├── KPIs/aggregations → conversion-guidelines/display-conversion-kpis.md
    ├── Action buttons → conversion-guidelines/display-conversion-actions.md
    └── Record links → conversion-guidelines/display-conversion-core.md
```

Across both paths, you almost always also need:
- `conversion-guidelines/conversion-queries.md` — how to build `a!queryRecordType()` / `a!recordData()`.
- `conversion-guidelines/conversion-field-mapping.md` — record-type syntax (`'recordType!{uuid}Foo.fields.{uuid}bar'`).
- `conversion-guidelines/conversion-relationships.md` — relationship navigation (`[relationship].fields.{uuid}fieldName`).
- `conversion-guidelines/validation-enforcement-module.md` — post-conversion validation.

---

## What the converter changes

### Mockup → functional transformations

| Mockup pattern | Functional pattern |
|---|---|
| `local!cases: {a!map(id: 1, title: "A"), ...}` | `local!cases: a!queryRecordType(recordType: 'recordType!{uuid}Case', fields: {...}, ...).data` — *or* `a!recordData(recordType: 'recordType!{uuid}Case', filters: ...)` for grids |
| `fv!row.status` | `fv!row['recordType!{uuid}Case.fields.{uuid}status']` |
| `local!isUpdate: false()` | `ri!isUpdate` (with rule input declared in the interface definition) |
| `local!cancel: false()` | `ri!cancel` |
| Custom text-field "Search" with `local!searchText` + `TODO-CONVERTER` comment | Grid `showSearchBox: true()` |
| Custom dropdown filter with `TODO-CONVERTER` comment | Grid `userFilters: {'recordType!...filters.{uuid}MyFilter'}` (if the filter exists in the record type) |
| `/* TODO-CONVERTER: Set status to "Approved" */` on a button | `saveInto: { a!save(ri!case['recordType!...status'], "Approved"), ... }` |

### Form button field-setting

A canonical pattern in forms:

```sail
/* TODO-CONVERTER: Set status to "Approved" */
/* TODO-CONVERTER: Set approvedBy to current user */
/* TODO-CONVERTER: Set approvedDate to current timestamp */
a!buttonWidget(
  label: "Approve",
  submit: true(),
  style: "SOLID",
  color: "ACCENT"
  /* In mockup: saveInto: a!save(local!status, "Approved") */
)
```

becomes:

```sail
a!buttonWidget(
  label: "Approve",
  submit: true(),
  style: "SOLID",
  color: "ACCENT",
  saveInto: {
    a!save(ri!case['recordType!{uuid}Case.fields.{uuid}status'], "Approved"),
    a!save(ri!case['recordType!{uuid}Case.fields.{uuid}approvedBy'], loggedInUser()),
    a!save(ri!case['recordType!{uuid}Case.fields.{uuid}approvedDate'], now())
  }
)
```

The converter resolves each `TODO-CONVERTER: Set X to Y` into a `a!save()` in the button's `saveInto`.

### Completeness requirement

The converter must convert **every** mockup data binding — every step of a wizard, every section of a form, every grid column, every chart series. Partial conversions are bugs. Before declaring done, scan the output for any remaining `local!` arrays that should have become queries.

---

## Validation after conversion

Run the same validators as for mockups (see `references/04-validation-checklist.md`), plus these conversion-specific checks:

- [ ] Every `'recordType!{uuid}Foo'` and field reference matches an entry in `context/data-model-context.md` — UUIDs are not invented.
- [ ] Field types match the way fields are used (e.g. Text field on `a!dropdownField`, Date field on `a!dateField`, not the reverse).
- [ ] Null-safe access used for nullable relationship fields: `if(a!isNotNullOrEmpty(local!case), local!case['recordType!...parent'].fields.{...}name, "")`.
- [ ] Grid `sortField` matches the *primary* field displayed in the column's `value` and is unique across columns.
- [ ] Computed columns (`if`/`a!match`/`concat`) have **no** `sortField`.
- [ ] Form `ri!` inputs are documented in a header comment block listing name, type, and purpose (and, for start forms, matching `model.json` `process_variables` exactly).
- [ ] No mockup-only patterns left over: no `local!` arrays that should be queries, no `TODO-CONVERTER` comments that should have been resolved.

For start forms specifically, see the "Process Variable Matching for Start Forms" section at the top of `agents/sail-dynamic-converter.md`. The protocol there is precise and must be followed exactly.

---

## Output

- The converted interface goes to `output/<name>-functional.sail`.
- Keep the original `output/<name>.sail` mockup intact for reference and re-runs.
- Tell the user where the file is, what the `ri!` inputs are (name, type, purpose), and any `TODO:` (process-model) or `TODO-DATA-MODEL:` comments that remain.
