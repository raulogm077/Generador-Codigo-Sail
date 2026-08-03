# Form Conversion - Relationship Patterns {#form-relationships}

> **Parent guide:** `/conversion-guidelines/form-conversion-module.md`
>
> **Related modules:**
> - `/conversion-guidelines/form-conversion-ri-patterns.md` - Rule input patterns
> - `/conversion-guidelines/common-conversion-patterns.md` - Shared query patterns
> - `/conversion-guidelines/form-conversion-buttons-actions.md` - Button actions

---

## 📑 Section Navigation {#form-relationships.nav}

- `{#form-relationships.core}` - Core principle for relationship access
- `{#form-relationships.many-to-one}` - Many-to-one (parent/reference) access
- `{#form-relationships.decision-table}` - When to use each relationship type
- `{#form-relationships.review-pattern}` - Review section pattern
- `{#form-relationships.one-to-many}` - One-to-many (child collections) management
- `{#form-relationships.record-constructors}` - Creating record instances

---

## Relationship Access in Forms {#form-relationships.core}

### Core Principle

**Use a SINGLE rule input for the main record and access ALL related data through relationships.**

When building forms, the main record "owns" the form. Access parent/reference data (many-to-one) and child collections (one-to-many) through relationship navigation—never separate rule inputs or queries.

### Many-to-One Relationships (Parent/Reference Records) {#form-relationships.many-to-one}

Use this pattern when accessing related lookup/reference data (Customer, Status, Priority, etc.):

**✅ CORRECT - Single ri! with relationship navigation:**
```sail
/* Rule Inputs:
 *   ri!case (Case) - The case record being edited
 */

/* Access customer name through Case → Customer relationship */
a!textField(
  label: "Customer Name",
  value: ri!case['recordType!Case.relationships.refCustomer.fields.customerName'],
  saveInto: ri!case['recordType!Case.relationships.refCustomer.fields.customerName']
)

/* Access customer email through same relationship */
a!textField(
  label: "Customer Email",
  value: ri!case['recordType!Case.relationships.refCustomer.fields.email'],
  saveInto: ri!case['recordType!Case.relationships.refCustomer.fields.email']
)

/* Access status name through Case → Status relationship */
a!textField(
  label: "Status",
  value: ri!case['recordType!Case.relationships.refCaseStatus.fields.statusName'],
  readOnly: true
)
```

**❌ WRONG - Separate rule inputs for related records:**
```sail
/* DON'T DO THIS */
/* Rule Inputs:
 *   ri!case (Case) - The case record
 *   ri!customer (Customer) - The related customer  ← WRONG!
 */

a!textField(
  label: "Customer Name",
  value: ri!customer['recordType!Customer.fields.customerName'],  /* WRONG */
  saveInto: ri!customer['recordType!Customer.fields.customerName']
)
```

### When to Use Each Relationship Type {#form-relationships.decision-table}

| Relationship Type | Example | Pattern |
|-------------------|---------|---------|
| **Many-to-one (parent)** | Case → Customer | `ri!case['...relationships.refCustomer.fields.customerName']` |
| **Many-to-one (reference)** | Case → Status | `ri!case['...relationships.refCaseStatus.fields.statusName']` |
| **One-to-many (children)** | Case → Comments | `ri!case['...relationships.caseComment']` (see next section) |
| **One-to-one** | Case → Details | `ri!case['...relationships.caseDetails.fields.description']` |

### Review Section Pattern {#form-relationships.review-pattern}

When displaying read-only data for review (e.g., wizard final step), use the same relationship navigation:

```sail
a!sectionLayout(
  label: "Case Summary",
  contents: {
    a!columnsLayout(
      columns: {
        a!columnLayout(
          contents: {
            a!richTextDisplayField(
              labelPosition: "COLLAPSED",
              value: {
                a!richTextItem(text: "Customer: ", style: "STRONG"),
                a!richTextItem(
                  text: ri!case['recordType!Case.relationships.refCustomer.fields.customerName']
                )
              }
            ),
            a!richTextDisplayField(
              labelPosition: "COLLAPSED",
              value: {
                a!richTextItem(text: "Status: ", style: "STRONG"),
                a!richTextItem(
                  text: ri!case['recordType!Case.relationships.refCaseStatus.fields.statusName']
                )
              }
            )
          }
        ),
        a!columnLayout(
          contents: {
            a!richTextDisplayField(
              labelPosition: "COLLAPSED",
              value: {
                a!richTextItem(text: "Priority: ", style: "STRONG"),
                a!richTextItem(
                  text: ri!case['recordType!Case.relationships.refPriority.fields.priorityName']
                )
              }
            ),
            a!richTextDisplayField(
              labelPosition: "COLLAPSED",
              value: {
                a!richTextItem(text: "Total Comments: ", style: "STRONG"),
                a!richTextItem(
                  text: length(ri!case['recordType!Case.relationships.caseComment'])
                )
              }
            )
          }
        )
      }
    )
  }
)
```

### Why Single ri! Pattern Is Mandatory

1. **Maintains data integrity**: Single rule input ensures all changes are coordinated
2. **Simpler interface signature**: Only one parameter instead of many
3. **Correct foreign key handling**: Appian manages the relationships automatically
4. **Easier to call**: Invoking interface only requires passing the main record
5. **Prevents orphaned data**: Related records stay properly linked to parent

**Key Principle:** One record type is the "owner" of the form → Make it the rule input → Access everything else through relationships

---

## One-to-Many Relationship Management {#form-relationships.one-to-many}

### Core Principle

**In create/update forms, the relationship field IS the data source. No queries, no copies.**

When creating or updating data in a form using the ri! pattern, manage one-to-many related records through the parent record's relationship field. NEVER query them separately or use local variables.

### ✅ CORRECT Pattern - Direct Relationship Access

#### Displaying Related Records in Forms

```sail
/* Iterate directly over the relationship - Case has many Comments */
a!forEach(
  items: ri!case['recordType!Case.relationships.caseComment'],
  expression: a!cardLayout(
    contents: {
      a!paragraphField(
        label: "Comment " & fv!index,
        /* Access fields through fv!item */
        value: fv!item['recordType!Comment.fields.description'],
        saveInto: fv!item['recordType!Comment.fields.description'],
        height: "MEDIUM"
      ),
      a!dateField(
        label: "Date",
        value: fv!item['recordType!Comment.fields.commentDate'],
        saveInto: fv!item['recordType!Comment.fields.commentDate']
      )
    }
  )
)
```

#### Adding New Related Records

```sail
a!buttonWidget(
  label: "Add Comment",
  saveInto: {
    a!save(
      ri!case['recordType!Case.relationships.caseComment'],
      append(
        ri!case['recordType!Case.relationships.caseComment'],
        'recordType!Comment'(
          'recordType!Comment.fields.commentDate': today(),
          'recordType!Comment.fields.createdBy': loggedInUser()
        )
      )
    )
  }
)
```

#### Removing Related Records

```sail
a!buttonWidget(
  label: "Remove Comment",
  icon: "trash",
  saveInto: {
    a!save(
      ri!case['recordType!Case.relationships.caseComment'],
      remove(
        ri!case['recordType!Case.relationships.caseComment'],
        fv!index  /* Remove item at current index in forEach */
      )
    )
  },
  showWhen: length(ri!case['recordType!Case.relationships.caseComment']) > 1
)
```

#### Counting and Empty State Check

```sail
/* Counting related records */
a!richTextItem(
  text: "Total Comments: " & length(
    ri!case['recordType!Case.relationships.caseComment']
  )
)

/* Checking if relationship is empty */
if(
  a!isNullOrEmpty(ri!case['recordType!Case.relationships.caseComment']),
  /* Show message when no comments */
  a!richTextDisplayField(
    value: a!richTextItem(
      text: "No comments added yet. Click 'Add Comment' to begin.",
      color: "SECONDARY"
    )
  ),
  /* Show comments when data exists */
  a!forEach(
    items: ri!case['recordType!Case.relationships.caseComment'],
    expression: ...
  )
)
```

### ❌ WRONG Pattern - Separate Queries or Local Variables

**DON'T DO THIS:**
```sail
/* ❌ WRONG - Querying related data separately */
local!caseComments: a!queryRecordType(
  recordType: 'recordType!Comment',
  filters: a!queryFilter(
    field: 'recordType!Comment.fields.caseId',
    operator: "=",
    value: ri!case['recordType!Case.fields.caseId']
  )
).data,

/* ❌ WRONG - Managing in local variable */
a!forEach(
  items: local!caseComments,  /* Don't use local variables! */
  expression: ...
)

/* ❌ WRONG - Copying relationship to local variable */
local!comments: ri!case['recordType!Case.relationships.caseComment']
/* This creates a COPY - changes won't save to the relationship */
```

### Why This Pattern Is Mandatory

1. **Automatic persistence**: Changes to relationship fields auto-save
2. **Correct foreign keys**: Appian manages the parent-child links
3. **Single source of truth**: No sync issues between copies
4. **Simpler code**: No manual save logic needed

### Pattern Summary Table

| Action | Use This Pattern |
|--------|------------------|
| **Display** | `a!forEach(items: ri!case['...relationships.caseComment'], ...)` |
| **Add** | `append(ri!case['...relationships.caseComment'], 'recordType!Comment'(...))` |
| **Remove** | `remove(ri!case['...relationships.caseComment'], fv!index)` |
| **Edit** | `fv!item['recordType!Comment.fields.description']` (in forEach) |
| **Count** | `length(ri!case['...relationships.caseComment'])` |
| **Check if empty** | `a!isNullOrEmpty(ri!case['...relationships.caseComment'])` |

---

## Creating Record Instances {#form-relationships.record-constructors}

When adding new related records in forms, you must use record type constructors—NOT `a!map()`.

### ❌ WRONG - Using a!map() for Records
```sail
/* INCORRECT - a!map() creates untyped maps, not record instances */
append(
  ri!case['recordType!Case.relationships.caseNotes'],
  a!map(
    'recordType!CaseNote.fields.noteText': "Follow up needed",
    'recordType!CaseNote.fields.noteType': "Status Update"
  )
)
```

### ✅ CORRECT - Using Record Type Constructor
```sail
/* CORRECT - Use record type constructor syntax */
append(
  ri!case['recordType!Case.relationships.caseNotes'],
  'recordType!CaseNote'(
    'recordType!CaseNote.fields.noteText': "Follow up needed",
    'recordType!CaseNote.fields.noteType': "Status Update"
  )
)
```

### Record Constructor Rules

1. **Always use the full record type reference as a function**: `'recordType!RecordTypeName'(...)`
2. **Use parentheses, not curly braces**: `'recordType!Type'()` not `'recordType!Type'{}`
3. **Field names must be fully qualified**: `'recordType!RecordType.fields.fieldName': value`
4. **This applies to all one-to-many relationships**: Case notes, contact history, document attachments, etc.

### Common Patterns

**Adding an empty record:**
```sail
append(
  ri!case.caseNotes,
  'recordType!CaseNote'()  /* Empty parentheses for default values */
)
```

**Adding a record with initial values:**
```sail
append(
  ri!case.caseNotes,
  'recordType!CaseNote'(
    'recordType!CaseNote.fields.noteTypeId': 1,
    'recordType!CaseNote.fields.noteText': null,
    'recordType!CaseNote.fields.createdDate': today()
  )
)
```

### Why This Matters

| `a!map()` | Record Constructor |
|-----------|-------------------|
| Creates untyped dictionary objects | Creates properly typed record instances |
| Type errors occur at save time (late) | Type checking at conversion time (early) |
| Relationships may fail silently | Relationships work correctly |
| No IDE validation | IDE can validate field names |
