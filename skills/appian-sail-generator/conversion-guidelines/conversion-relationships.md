# Relationship Navigation Patterns {#relationships-module}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/common-conversion-patterns.md` - Navigation index
> - `/conversion-guidelines/conversion-queries.md` - Query construction patterns
> - `/conversion-guidelines/conversion-field-mapping.md` - Field reference syntax

Patterns for navigating relationships, distinguishing between user fields and relationships, and using a!relatedRecordData().

---

## 📑 Module Navigation {#relationships.nav}

- `{#relationships.navigation}` - Single continuous path syntax
- `{#relationships.user-group-fields}` - User/Group fields vs relationships
- `{#relationships.related-record-data}` - a!relatedRecordData() patterns

---

## Relationship Navigation Syntax {#relationships.navigation}

### Single Continuous Path Rule {#relationships.navigation.path-rule}

When accessing fields through relationships, use a SINGLE continuous path - NOT separate bracket accesses.

```sail
/* ❌ WRONG - Double bracket syntax */
fv!row['recordType!Base.relationships.related']['recordType!Target.fields.field']

/* ✅ CORRECT - Single continuous path */
fv!row['recordType!Base.relationships.related.fields.field']
```

### Path Construction from Data Model {#relationships.navigation.construction}

Given from `data-model-context.md`:
- **Relationship:** `'recordType!Base.relationships.relationshipName'`
- **Target field:** `'recordType!Target.fields.fieldName'`

**Construct by appending `.fields.fieldName` to the relationship path:**

```
'recordType!Base.relationships.relationshipName.fields.fieldName'
```

**Key:** Drop the target record type prefix (`'recordType!Target`) - only append `.fields.fieldName`.

### Many-to-One vs One-to-Many {#relationships.navigation.types}

| Relationship Type | Navigation | Sorting | Example |
|------------------|------------|---------|---------|
| Many-to-one | Direct field access | ✅ Can sort on related fields | Case → Status lookup |
| One-to-many | Use `a!relatedRecordData()` or `length()` | ❌ Cannot sort | Case → Comments list |

**Many-to-one (direct access):**
```sail
/* No a!relatedRecordData() needed */
fv!row['recordType!Case.relationships.status.fields.statusName']
```

**One-to-many (requires special handling):**
```sail
/* Use a!relatedRecordData() for filtering/sorting/limiting */
a!gridField(
  data: a!recordData(
    recordType: 'recordType!Case',
    relatedRecordData: {
      a!relatedRecordData(
        relationship: 'recordType!Case.relationships.comments',
        limit: 5,
        sort: a!sortInfo(
          field: 'recordType!Comment.fields.createdOn',
          ascending: false
        )
      )
    }
  )
)
```

---

## User/Group Fields vs Relationships {#relationships.user-group-fields}

### The Rule

**When the data model shows BOTH a field AND a relationship for users, ALWAYS use the FIELD reference, NEVER the relationship.**

Many record types have both:
- **Field** (e.g., `assignedTo`, `createdBy`, `modifiedBy`): User type field
- **Relationship** (e.g., `assignedToUser`, `createdByUser`): many-to-one relationship to User record type

### Why This Matters

**Relationships are navigation paths, NOT scalar values:**
- **Fields** return scalar types: `User`, `Text`, `Number`, `Date`
- **Relationships** return record instances (causing type mismatches)

```sail
/* ❌ WRONG - Type mismatch: user() expects User scalar, not User Record */
user(
  fv!row['recordType!Case.relationships.assignedToUser'],  /* Returns User Record */
  "firstName"
)

/* ✅ CORRECT - Field returns User scalar */
user(
  fv!row['recordType!Case.fields.assignedTo'],  /* Returns User */
  "firstName"
)
```

### Displaying User Names {#relationships.user-group-fields.display}

```sail
/* ✅ CORRECT pattern for displaying user names */
if(
  a!isNotNullOrEmpty(fv!row['recordType!Case.fields.assignedTo']),
  trim(
    user(fv!row['recordType!Case.fields.assignedTo'], "firstName") & " " &
    user(fv!row['recordType!Case.fields.assignedTo'], "lastName")
  ),
  "–"
)
```

**Note:** Use `firstName` + `lastName` instead of `displayName` (displayName is a nickname and often empty).

### Type Compatibility Table {#relationships.user-group-fields.compatibility}

| Function | Accepts Relationships? | Use Instead |
|----------|------------------------|-------------|
| `user()` | ❌ NO | Use `fields.fieldName` (User type) |
| `text()`, `concat()` | ❌ NO | Navigate to related field |
| `a!isNullOrEmpty()` | ✅ YES | Check existence of related records |
| `a!forEach()`, `length()` | ✅ YES (one-to-many only) | Iterate relationship arrays |
| Navigation to fields | ✅ YES | `relationships.rel.fields.field` |

### Quick Decision Tree

1. **Is it a!relatedRecordData()?** → ✅ Relationship OK
2. **Is it a null check?** → ✅ Relationship OK
3. **Is it an array function AND one-to-many?** → ✅ Relationship OK
4. **Navigating further with `.fields.fieldName`?** → ✅ Relationship OK
5. **Passing relationship directly to any other function?** → ❌ Use the field instead

---

## a!relatedRecordData() Patterns {#relationships.related-record-data}

### Purpose

Use within `a!recordData()` to filter, sort, and limit records from a **one-to-many relationship**.

### Key Constraints

- **ONE-TO-MANY relationships ONLY** — Does NOT work with many-to-one
- **Default limit is 10** — Always specify limit if you need more (max 100 for grids)
- **Cannot be used in aggregations** or records-powered charts

### Pattern: Get Latest Related Record

```sail
a!relatedRecordData(
  relationship: 'recordType!Case.relationships.comments',
  sort: a!sortInfo(
    field: 'recordType!Comment.fields.createdOn',
    ascending: false
  ),
  limit: 1
)
```

### Pattern: Filter Related Records

```sail
a!relatedRecordData(
  relationship: 'recordType!Order.relationships.lineItems',
  filters: a!queryFilter(
    field: 'recordType!LineItem.fields.status',
    operator: "=",
    value: "Active"
  ),
  limit: 50
)
```

### Common Mistakes

```sail
/* ❌ WRONG - Many-to-one relationship */
a!relatedRecordData(
  relationship: 'recordType!Case.relationships.status'  /* This is many-to-one! */
)

/* ✅ CORRECT - For many-to-one, access fields directly */
fv!row['recordType!Case.relationships.status.fields.statusName']

/* ❌ WRONG - Missing limit (only returns 10 by default) */
a!relatedRecordData(
  relationship: 'recordType!Order.relationships.lineItems'
)

/* ✅ CORRECT - Specify limit */
a!relatedRecordData(
  relationship: 'recordType!Order.relationships.lineItems',
  limit: 100
)
```
