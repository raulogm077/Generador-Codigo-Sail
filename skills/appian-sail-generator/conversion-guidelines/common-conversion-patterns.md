# Common Conversion Patterns - Navigation Index {#common-module}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/display-conversion-module.md` - Display-specific patterns
> - `/conversion-guidelines/form-conversion-module.md` - Form-specific patterns
> - `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

Patterns used by BOTH form and display conversions. The sail-dynamic-converter agent references these modules for every conversion regardless of interface type.

---

## 📑 Navigation Guide

This module has been split into focused topic files for easier navigation and maintenance. Use this index to find the pattern you need:

### Query Construction and Result Handling

**Module:** `/conversion-guidelines/conversion-queries.md`

Covers query function selection, parameter requirements, result data structures, and common mistakes.

**Key topics:**
- `{#queries.construction}` - Query function selection decision tree
- `{#queries.record-data}` - a!recordData() usage and restrictions
- `{#queries.query-record-type}` - a!queryRecordType() patterns
- `{#queries.result-structures}` - How query type determines property access
- `{#queries.parameters}` - fields, fetchTotalCount, applyWhen requirements

### Relationship Navigation

**Module:** `/conversion-guidelines/conversion-relationships.md`

Covers relationship navigation syntax, user/group field handling, and a!relatedRecordData() patterns.

**Key topics:**
- `{#relationships.navigation}` - Single continuous path syntax
- `{#relationships.user-group-fields}` - User/Group fields vs relationships
- `{#relationships.related-record-data}` - a!relatedRecordData() usage

### Field Mapping and Validation

**Module:** `/conversion-guidelines/conversion-field-mapping.md`

Covers record type reference syntax, dropdown conversion, data model validation, environment objects, and pattern refactoring.

**Key topics:**
- `{#field-mapping.record-type-syntax}` - Record type reference patterns (UUIDs, autocomplete)
- `{#field-mapping.dropdown-all-option}` - Converting "All" filter options
- `{#field-mapping.data-model-validation}` - Validating record types, fields, relationships
- `{#field-mapping.environment-objects}` - Constants, groups, process models
- `{#field-mapping.pattern-matching}` - Refactoring nested if() to a!match()
- `{#field-mapping.preserve-mockup-values}` - Never introduce runtime generators

---

## Quick Reference - Common Patterns by Task

| Task | Module | Anchor Link |
|------|--------|-------------|
| Choose query function | conversion-queries.md | `{#queries.construction.decision-tree}` |
| Access query results | conversion-queries.md | `{#queries.result-structures}` |
| Navigate relationships | conversion-relationships.md | `{#relationships.navigation}` |
| Display user names | conversion-relationships.md | `{#relationships.user-group-fields.display}` |
| Convert "All" dropdowns | conversion-field-mapping.md | `{#field-mapping.dropdown-all-option}` |
| Validate data model | conversion-field-mapping.md | `{#field-mapping.data-model-validation}` |
| Handle missing constants | conversion-field-mapping.md | `{#field-mapping.environment-objects}` |
| Refactor nested if() | conversion-field-mapping.md | `{#field-mapping.pattern-matching}` |

---

## Module Loading Strategy

**When converting mockups to functional interfaces, load modules based on what you're converting:**

### Always Load:
- `/conversion-guidelines/common-conversion-patterns.md` (this file - navigation index)
- Module-specific file based on interface type:
  - Display interfaces → `/conversion-guidelines/display-conversion-module.md`
  - Form interfaces → `/conversion-guidelines/form-conversion-module.md`

### Load On-Demand:
- `/conversion-guidelines/conversion-queries.md` - When working with queries (grids, KPIs, dropdowns)
- `/conversion-guidelines/conversion-relationships.md` - When navigating to related record fields
- `/conversion-guidelines/conversion-field-mapping.md` - When validating field references or handling environment objects

### Post-Conversion:
- `/conversion-guidelines/validation-enforcement-module.md` - **ALWAYS run after conversion** to validate syntax, null safety, and query patterns

---

## Pattern Categories

### Data Access Patterns
- **Query construction** - Choosing between a!recordData() and a!queryRecordType()
- **Result handling** - Extracting data from queries (record instances vs maps)
- **Relationship navigation** - Single continuous path syntax

### Data Mapping Patterns
- **Field references** - Record type syntax with UUIDs
- **Dropdown conversion** - Using placeholder instead of "All" option
- **Data model validation** - Verifying fields/relationships exist

### Code Quality Patterns
- **Environment objects** - Using TODO placeholders for constants/groups
- **Pattern matching** - Refactoring nested if() to a!match()
- **Mockup preservation** - Keeping static values during conversion

---

## Working with This Module System

**For developers using these guidelines:**

1. **Start with this navigation index** to understand the overall structure
2. **Load specific modules** as you encounter those patterns during conversion
3. **Use anchor links** to jump directly to the pattern you need
4. **Cross-reference between modules** using the Related Modules section

**For maintainers updating these guidelines:**

1. **Keep this index up-to-date** when adding new patterns
2. **Update anchor links** if section IDs change
3. **Add new modules** to the navigation index with clear descriptions
4. **Preserve cross-references** between related patterns across modules
