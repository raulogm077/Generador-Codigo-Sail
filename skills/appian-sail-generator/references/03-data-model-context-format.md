# Data Model Context — Format and Generation

The `context/data-model-context.md` file is the **single source of truth** for record-type identifiers used during Phase 2 (functional conversion). It tells the converter every record type, field, relationship, action, and filter that exists in the user's Appian application, along with their UUIDs.

**Without it, Phase 2 cannot run** — the converter would have to invent UUIDs, which produces broken interfaces.

This skill ships with:
- A real example at `examples/data-model-context-example.md` (the OTIEC application).
- Two Python scripts at `scripts/` that generate this file from Appian's `recordTypeHaul` XML exports.

---

## File location

The converter expects `context/data-model-context.md` to be at the **working directory** (the user's project root), **not** inside the skill. Create the `context/` directory at the working directory if it doesn't exist.

If the user provides a markdown file at a different path, either move it to `context/data-model-context.md` or pass the actual path to the converter explicitly when invoking it.

---

## Required format

The file is markdown with a specific shape that the converter can parse. Each record type is wrapped in an XML-like tag whose name is the record-type name in snake_case (e.g. `<otiec_app_employment_history>`).

```markdown
# <Application Name> Record Type Context Reference

This document provides the specific record type definitions for use when creating SAIL expressions.

<available_record_types>
## Available Record Types

<case>
### Case
**Record Type**: `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}Case'`

**Description**:
Stores case data.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| caseId | Integer | `'recordType!{3eb360f5-...}Case.fields.{d75af521-...}caseId'` |
| title | Text | `'recordType!{3eb360f5-...}Case.fields.{99316994-...}title'` |
| status | Text | `'recordType!{3eb360f5-...}Case.fields.{c3f9c5c1-...}status'` |
| dueDate | Date | `'recordType!{3eb360f5-...}Case.fields.{64715049-...}dueDate'` |
| assignedTo | User | `'recordType!{3eb360f5-...}Case.fields.{a62a2b70-...}assignedTo'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| customer | many-to-one | `'recordType!{3eb360f5-...}Case.relationships.{a65196c8-...}customer'` |
| comments | one-to-many | `'recordType!{3eb360f5-...}Case.relationships.{dc3410a6-...}comments'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| openOnly | `'recordType!{3eb360f5-...}Case.filters.{13ea3159-...}openOnly'` |

**Record Actions**:

| **Action Name** | **Action Reference** |
|----------------|---------------------|
| createCase | `'recordType!{3eb360f5-...}Case.actions.{abc-...}createCase'` |

</case>

</available_record_types>
```

Key things to preserve:
- The H1 title.
- The `<available_record_types>` wrapper.
- One `<snake_case_record_name>` block per record type.
- The exact `'recordType!{uuid}Name'` and `'recordType!{uuid}Name.fields.{uuid}fieldName'` syntax — single quotes, curly-braced UUIDs, no spaces.
- Data types from the canonical set: `Text`, `Integer`, `Boolean`, `Date`, `Datetime`, `User`, `CollaborationDocument`, `Document`.
- Relationship types: `one-to-many`, `many-to-one`, `one-to-one`, `many-to-many`.

If a section has no entries, write "Not available" — don't omit the section.

For a full real example, see `examples/data-model-context-example.md`.

---

## Generating from `recordTypeHaul` XML

When the user exports record types from Appian, the exports are XML files in `recordTypeHaul` format. This skill ships two scripts to convert them.

### Single XML file → one markdown file

```bash
python scripts/xml_to_appian_recordtype_md.py path/to/record.xml
```

Optional flags:
- `-o` / `--out` — output markdown path (defaults to `<input>.md`).
- `--title` — H1 title override.

Example:
```bash
python scripts/xml_to_appian_recordtype_md.py case-record.xml -o context/data-model-context.md --title "My App Record Type Context Reference"
```

### Directory of XMLs *or* zipped Appian application export → many markdown files

```bash
# Directory
python scripts/map_xml_to_appian_recordtype_md.py path/to/recordtype-xml-folder/

# Zipped Appian application export
python scripts/map_xml_to_appian_recordtype_md.py path/to/application-export.zip
```

Optional flags:
- `-o` / `--output_dir` — output directory (defaults to the input directory for directories, current directory for zips).
- `-f` / `--folder` — specific folder path inside the zip to search for `recordType` XMLs (zip input only).

Output filename pattern: `data-model-context-<record_type_name_in_snake_case>.md`. **One file per record type** — for Phase 2, you typically need to concatenate the ones the interface uses into a single `context/data-model-context.md`.

### Concatenating multiple record types into one context file

If Phase 2 uses multiple record types (e.g. Case + Customer + Comment), build a single file by:

1. Running the `map_*` script to produce `data-model-context-case.md`, `data-model-context-customer.md`, etc.
2. Concatenating them under a shared `<available_record_types>` wrapper:

```bash
# Quick concat (shell)
{
  echo "# My App Record Type Context Reference"
  echo ""
  echo "This document provides the specific record type definitions for use when creating SAIL expressions."
  echo ""
  echo "<available_record_types>"
  echo "## Available Record Types"
  echo ""
  # Strip each file's preamble + outer wrapper, keep only the per-record block
  for f in data-model-context-*.md; do
    awk '/^<[a-z_]+>$/,/^<\/[a-z_]+>$/' "$f"
    echo ""
  done
  echo "</available_record_types>"
} > context/data-model-context.md
```

(Eyeball the result — if a record block is missing the leading `<tagname>` or trailing `</tagname>`, fix it by hand.)

---

## Validating the context file

Before running Phase 2, check:

- [ ] Every UUID is in the canonical curly-brace form: `{abcd1234-...}`. No bare UUIDs, no missing braces.
- [ ] Every record-type reference uses the single-quoted form: `'recordType!{uuid}Name'`.
- [ ] Field references include both record-type UUID and field UUID: `'recordType!{rt-uuid}Name.fields.{f-uuid}fieldName'`.
- [ ] Data types are from the canonical set — anything unrecognised will show up verbatim and may break converter logic.
- [ ] Every record type the mockup needs is present in the file.
- [ ] The user is on the same Appian environment whose UUIDs are in the file (UUIDs are per-environment).

If a UUID changes (e.g. record type moved to a different environment), regenerate the context — don't hand-edit.

---

## When the user doesn't have any of this

Three scenarios in increasing order of friction:

1. **Markdown ready** → proceed to Phase 2.
2. **XML exports only** → run the script, then proceed.
3. **Nothing yet** → the user needs to either:
   - Export the relevant record types from Appian (Appian Designer → record type → Export → `recordTypeHaul` XML), then run the script; or
   - Manually paste the record-type details (names, UUIDs, fields with types and UUIDs, relationships). This is brittle and error-prone — prefer the export path.

If the user is stuck on this step, point them at the original `data-model-context` tool: <https://github.com/raulogm077/data-model-context> (the same scripts shipped in `scripts/`) or `@tokyojordan/data-model-context`.

**Never invent UUIDs to unblock conversion.** A converted interface with fake UUIDs is worse than no conversion at all — it looks valid but breaks at runtime.
