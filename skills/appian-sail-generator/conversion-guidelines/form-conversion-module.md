# Form Conversion Module {#form-module}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/common-conversion-patterns.md` - Shared patterns (queries, relationships)
> - `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

Patterns for converting CREATE/UPDATE form interfaces that use rule inputs (ri!) to bind form data.

---

## 📑 Module Navigation {#form.nav}

### 📄 Focused Module Files

This module is split into four focused files for easier navigation:

#### 1. Rule Input Patterns
**File:** `/conversion-guidelines/form-conversion-ri-patterns.md`

**Contents:**
- Interface detection and decision tree
- Rule input pattern overview
- Mandatory naming rules (with/without model.json)
- Structured comment format
- Variable mapping (local! → ri!)

**When to read:** Start here for all form conversions to understand rule input setup.

---

#### 2. Relationship Patterns
**File:** `/conversion-guidelines/form-conversion-relationships.md`

**Contents:**
- Many-to-one relationship access (parent/reference records)
- One-to-many relationship management (child collections)
- Creating record instances with record type constructors
- Review section patterns

**When to read:** When form accesses related data or manages child records.

---

#### 3. Buttons and Actions
**File:** `/conversion-guidelines/form-conversion-buttons-actions.md`

**Contents:**
- Audit fields management (create vs update mode)
- Wizard handling and step navigation
- Form action buttons (submit, cancel, save draft)
- Button field-setting with status/action fields
- TODO-CONVERTER comment cleanup

**When to read:** When implementing form submission buttons or handling status transitions.

---

#### 4. Data Model Handling
**File:** `/conversion-guidelines/form-conversion-data-model.md`

**Contents:**
- Data model mismatch strategies
- Common form conversion mistakes
- Multi-type form entry pattern
- Button and wizard parameter validation
- Encrypted text field limitation
- Form conversion checklist

**When to read:** When data model doesn't match mockup, or for final validation before completion.

---

## 🎯 Quick Reference: When to Use Each Module

| Your Task | Read This File First |
|-----------|---------------------|
| Starting a form conversion | `form-conversion-ri-patterns.md` → Rule Input Patterns |
| Form accesses customer/status data | `form-conversion-relationships.md` → Many-to-One section |
| Form manages child records (notes, contacts) | `form-conversion-relationships.md` → One-to-Many section |
| Implementing submit/cancel buttons | `form-conversion-buttons-actions.md` → Action Buttons section |
| Buttons change status/fields | `form-conversion-buttons-actions.md` → Field-Setting section |
| Multi-step wizard | `form-conversion-buttons-actions.md` → Wizard Handling section |
| Data model mismatch | `form-conversion-data-model.md` → Mismatch Strategies section |
| Final validation | `form-conversion-data-model.md` → Checklist section |

---

## 🔄 Form Conversion Workflow

**Recommended reading order:**

1. **Start:** Read `form-conversion-ri-patterns.md` sections:
   - Interface Detection → Confirm this is a form interface
   - Rule Input Names → Get correct ri! variable names
   - Comment Format → Set up header documentation

2. **Field Conversion:** Read as needed:
   - `form-conversion-relationships.md` → If form accesses related records
   - `form-conversion-data-model.md` (Mismatch section) → If fields don't align

3. **Button Implementation:** Read `form-conversion-buttons-actions.md` sections:
   - Audit Fields → Set up create/update audit pattern
   - Action Buttons → Implement submit/cancel buttons
   - Field-Setting → If buttons set status/action fields
   - Wizard Handling → If multi-step form

4. **Validation:** Read `form-conversion-data-model.md`:
   - Common Mistakes → Avoid typical errors
   - Checklist → Verify all requirements met

---

## 📖 Cross-Module Patterns

Some patterns span multiple files. Here's where to find complete guidance:

### Pattern: Create/Update Form with Relationships

**Read in order:**
1. `form-conversion-ri-patterns.md` → Get ri! setup
2. `form-conversion-relationships.md` → Access parent/reference data
3. `form-conversion-buttons-actions.md` → Implement audit fields

### Pattern: Form with Child Record Management

**Read in order:**
1. `form-conversion-ri-patterns.md` → Get ri! setup
2. `form-conversion-relationships.md` → One-to-many section for add/remove
3. `form-conversion-buttons-actions.md` → Submit button with audit

### Pattern: Approval Form with Status Changes

**Read in order:**
1. `form-conversion-ri-patterns.md` → Get ri! setup
2. `form-conversion-buttons-actions.md` → Field-setting section
3. `form-conversion-data-model.md` → Check for ID field mapping

### Pattern: Multi-Step Wizard

**Read in order:**
1. `form-conversion-ri-patterns.md` → Get ri! setup
2. `form-conversion-buttons-actions.md` → Wizard handling
3. `form-conversion-relationships.md` → If wizard has review step

---

## 🚨 Critical Rules (All Forms)

Before beginning ANY form conversion, review these rules:

1. **Rule Input Names** - Read model.json if available, otherwise infer from mockup
2. **No Local Copies** - Bind directly to ri!, never copy to local!
3. **Null Safety** - Always use a!defaultValue() or if() checks on ri! access
4. **Audit Fields** - Create mode sets all 4, update mode sets 2
5. **Record Constructors** - Use 'recordType!Type'() NOT a!map()

**See individual module files for detailed guidance on each rule.**

---

## 🔗 Related Conversion Modules

| Module | Purpose | When to Use |
|--------|---------|-------------|
| `/conversion-guidelines/display-conversion-module.md` | Display interfaces (dashboards, reports) | NOT for forms with submit buttons |
| `/conversion-guidelines/common-conversion-patterns.md` | Shared patterns (queries, aggregation) | Reference as needed from form modules |
| `/conversion-guidelines/validation-enforcement-module.md` | Post-conversion validation | After form conversion complete |

---

## 📝 Comment Prefix Reference

Form conversions may encounter multiple comment types:

| Prefix | Use In Forms? | Handled By |
|--------|---------------|------------|
| `TODO-CONVERTER:` | Yes - Field-setting instructions | Form converter (this module) |
| `TODO:` | Yes - Process model activities | External configuration |
| `TODO-DATA-MODEL:` | Yes - Missing fields | Database/CDT changes |
| `REQUIREMENT:` | Yes - Business rules | Documentation only |

**See `form-conversion-buttons-actions.md` (Cleanup section) for detailed guidance.**
