# Conversion Guidelines Navigation Index

Quick navigation index for functional interface conversion. Use this to find the right module and anchor for your task.

---

## 📁 Modules by Interface Type

### Navigation Index Files (Load First)
These files serve as entry points and navigation guides:

**Form Interfaces (CREATE/UPDATE):**
- `/conversion-guidelines/form-conversion-module.md` - Navigation index for form conversion modules
  - Links to focused modules: ri-patterns, relationships, buttons-actions, data-model

**Display Interfaces (READ-ONLY):**
- `/conversion-guidelines/display-conversion-module.md` - Navigation index for display conversion modules
  - Links to focused modules: core, grids, charts, kpis, actions

**Common Patterns (All Interface Types):**
- `/conversion-guidelines/common-conversion-patterns.md` - Navigation index for common patterns
  - Links to focused modules: queries, relationships, field-mapping

**Validation (Always Required):**
- `/conversion-guidelines/validation-enforcement-module.md` - Validation steps (not split)

---

### Form Focused Modules (Load Based on Features)

**Core Pattern (Always Load):**
- `/conversion-guidelines/form-conversion-ri-patterns.md` - ri! patterns, detection, mapping
  - Key sections: `{#form.ri-pattern}`, `{#form.ri-pattern.comment-format}`, `{#form.ri-pattern.variable-mapping}`, `{#form.ri-pattern.detection}`

**Relationships (Load If Needed):**
- `/conversion-guidelines/form-conversion-relationships.md` - Relationship access in forms
  - Key sections: `{#form.relationship-access}`, `{#form.relationship-access.many-to-one}`, `{#form.one-to-many}`, `{#form.record-constructors}`

**Buttons/Actions (Load If Needed):**
- `/conversion-guidelines/form-conversion-buttons-actions.md` - Buttons, wizard handling, audit fields
  - Key sections: `{#form.button-field-setting}`, `{#form.button-field-setting.cleanup}`, `{#form.audit-fields}`, `{#form.wizard-handling}`, `{#form.multi-type-entry}`, `{#form.parameter-validation}`

**Data Model Issues (Load If Needed):**
- `/conversion-guidelines/form-conversion-data-model.md` - Data model mismatches, validation blockers
  - Key sections: `{#form.data-model-mismatch}`, `{#form.encrypted-field-limitation}`

---

### Display Focused Modules (Load Based on Features)

**Core Pattern (Always Load):**
- `/conversion-guidelines/display-conversion-core.md` - Detection, record links
  - Key sections: `{#display.record-links}`, `{#display.record-links.fv-identifier}`

**Grids (Load If Needed):**
- `/conversion-guidelines/display-conversion-grids.md` - Grid patterns, search/filter conversion
  - Key sections: `{#display.grid-patterns}`, `{#display.grid-patterns.sortfield-rules}`, `{#display.grid-search-filter}`, `{#display.grid-refresh-after}`

**Charts (Load If Needed):**
- `/conversion-guidelines/display-conversion-charts.md` - Chart refactoring, grouping
  - Key sections: `{#display.chart-refactoring}`, `{#display.chart-refactoring.grouping-fields}`, `{#display.chart-components}`, `{#display.chart-components.stacking}`, `{#display.chart-components.intervals}`

**KPIs (Load If Needed):**
- `/conversion-guidelines/display-conversion-kpis.md` - KPI/aggregation calculations
  - Key sections: `{#display.kpi-aggregation}`

**Action Buttons (Load If Needed):**
- `/conversion-guidelines/display-conversion-actions.md` - Action buttons, toolbar actions
  - Key sections: `{#display.action-type-rules}`, `{#display.action-type-rules.identification}`, `{#display.action-type-rules.primary-key}`, `{#display.action-type-rules.placement}`, `{#display.action-buttons}`, `{#display.action-buttons.view}`, `{#display.action-buttons.finding}`, `{#display.action-buttons.matching}`, `{#display.action-buttons.checklist}`, `{#display.grid-toolbar-actions}`, `{#display.grid-toolbar-actions.checklist}`

---

### Common Focused Modules (Load Based on Features)

**Query Construction (Always Load):**
- `/conversion-guidelines/conversion-queries.md` - Query construction, result structures
  - Key sections: `{#common.query-construction}`, `{#common.query-result-structures}`, `{#common.dropdown-all-option}`
  - Single record by id → `{#queries.query-by-identifier}` (`a!queryRecordByIdentifier`, 250 related rows, composite keys 26.3+)
  - Native KPIs → `/conversion-guidelines/display-conversion-kpis.md` § Pattern 0 (`a!kpiField`, records-only)

**Relationships (Load If Needed):**
- `/conversion-guidelines/conversion-relationships.md` - Relationship navigation
  - Key sections: `{#common.relationship-navigation}`, `{#common.related-record-data}`

**Field Mapping (Load If Needed):**
- `/conversion-guidelines/conversion-field-mapping.md` - Record type syntax, validation
  - Key sections: `{#common.record-type-syntax}`, `{#common.data-model-validation}`, `{#common.environment-objects}`, `{#common.environment-objects.group-access-control}`, `{#common.pattern-matching}`

---

## 📋 By Task Type

**Form Conversion Tasks:**
- Building forms/wizards that create records → `form-conversion-ri-patterns.md` `{#form.ri-pattern}`
- ri! comment format and documentation → `form-conversion-ri-patterns.md` `{#form.ri-pattern.comment-format}`
- Relationship access in forms (overview) → `form-conversion-relationships.md` `{#form.relationship-access}`
- Many-to-one relationship access (parent/ref) → `form-conversion-relationships.md` `{#form.relationship-access.many-to-one}`
- One-to-many relationship handling in forms → `form-conversion-relationships.md` `{#form.one-to-many}`
- Creating record instances (constructors vs a!map) → `form-conversion-relationships.md` `{#form.record-constructors}`
- Managing audit fields (createdBy, modifiedOn) → `form-conversion-buttons-actions.md` `{#form.audit-fields}`
- Button field-setting conversion → `form-conversion-buttons-actions.md` `{#form.button-field-setting}`
- Button comment cleanup → `form-conversion-buttons-actions.md` `{#form.button-field-setting.cleanup}`
- Wizard step handling → `form-conversion-buttons-actions.md` `{#form.wizard-handling}`
- Multi-type form entry patterns → `form-conversion-buttons-actions.md` `{#form.multi-type-entry}`
- Button/wizard parameter validation → `form-conversion-buttons-actions.md` `{#form.parameter-validation}`
- Data model mismatch strategies → `form-conversion-data-model.md` `{#form.data-model-mismatch}`
- Encrypted text field limitation → `form-conversion-data-model.md` `{#form.encrypted-field-limitation}`

**Display Conversion Tasks:**
- Record link conversion → `display-conversion-core.md` `{#display.record-links}`
- fv!identifier usage rules → `display-conversion-core.md` `{#display.record-links.fv-identifier}`
- Grid patterns and construction → `display-conversion-grids.md` `{#display.grid-patterns}`
- Grid sortField validation → `display-conversion-grids.md` `{#display.grid-patterns.sortfield-rules}`
- Grid search/filter conversion → `display-conversion-grids.md` `{#display.grid-search-filter}`
- refreshAfter parameter usage → `display-conversion-grids.md` `{#display.grid-refresh-after}`
- Chart pattern refactoring (mockup → record data) → `display-conversion-charts.md` `{#display.chart-refactoring}`
- Chart grouping field selection → `display-conversion-charts.md` `{#display.chart-refactoring.grouping-fields}`
- Chart components reference → `display-conversion-charts.md` `{#display.chart-components}`
- Chart stacking property rules → `display-conversion-charts.md` `{#display.chart-components.stacking}`
- Valid interval values for groupings → `display-conversion-charts.md` `{#display.chart-components.intervals}`
- KPI/aggregation calculations → `display-conversion-kpis.md` `{#display.kpi-aggregation}`
- **Record List Actions vs Related Actions** → `display-conversion-actions.md` `{#display.action-type-rules}`
- Action type identification → `display-conversion-actions.md` `{#display.action-type-rules.identification}`
- Primary key identification for actions → `display-conversion-actions.md` `{#display.action-type-rules.primary-key}`
- Valid action placement rules → `display-conversion-actions.md` `{#display.action-type-rules.placement}`
- Grid action column conversion → `display-conversion-actions.md` `{#display.action-buttons}`
- View button to recordLink → `display-conversion-actions.md` `{#display.action-buttons.view}`
- Finding related actions in data model → `display-conversion-actions.md` `{#display.action-buttons.finding}`
- Related action matching → `display-conversion-actions.md` `{#display.action-buttons.matching}`
- Action conversion checklist → `display-conversion-actions.md` `{#display.action-buttons.checklist}`
- Grid toolbar actions conversion → `display-conversion-actions.md` `{#display.grid-toolbar-actions}`
- Grid toolbar action checklist → `display-conversion-actions.md` `{#display.grid-toolbar-actions.checklist}`

**Common Conversion Tasks:**
- Query construction (a!recordData, a!queryRecordType) → `conversion-queries.md` `{#common.query-construction}`
- Query result property access patterns → `conversion-queries.md` `{#common.query-result-structures}`
- Dropdown "All" option conversion → `conversion-queries.md` `{#common.dropdown-all-option}`
- Relationship navigation syntax → `conversion-relationships.md` `{#common.relationship-navigation}`
- Related record data (a!relatedRecordData) → `conversion-relationships.md` `{#common.related-record-data}`
- Record type reference syntax (UUIDs, autocomplete) → `conversion-field-mapping.md` `{#common.record-type-syntax}`
- Data model availability validation → `conversion-field-mapping.md` `{#common.data-model-validation}`
- Environment object validation → `conversion-field-mapping.md` `{#common.environment-objects}`
- Group-based access control patterns → `conversion-field-mapping.md` `{#common.environment-objects.group-access-control}`
- Pattern matching (nested if → a!match) → `conversion-field-mapping.md` `{#common.pattern-matching}`

**Validation Tasks:**
- Unused variable detection → `validation-enforcement-module.md` `{#validation.unused-variables}`
- Unused variable categories/examples → `validation-enforcement-module.md` `{#validation.unused-variables.categories}`
- Null safety enforcement → `validation-enforcement-module.md` `{#validation.null-safety}`
- Query filter type matching → `validation-enforcement-module.md` `{#validation.type-matching}`
- Pre-flight validation checklist → `validation-enforcement-module.md` `{#validation.pre-flight-checklist}`
- Critical errors quick reference → `validation-enforcement-module.md` `{#validation.critical-errors}`

---

## 🔧 By Error Type

**Form-Related Errors:**
- "ri! variable not defined" → `form-conversion-ri-patterns.md` `{#form.ri-pattern}`
- "Cannot save to ri!" → `form-conversion-ri-patterns.md` `{#form.ri-pattern.variable-mapping}`
- Using a!map() instead of record constructor → `form-conversion-relationships.md` `{#form.record-constructors}`
- Audit fields missing → `form-conversion-buttons-actions.md` `{#form.audit-fields}`
- Invalid button/wizard parameter → `form-conversion-buttons-actions.md` `{#form.parameter-validation}`

**Display-Related Errors:**
- Grid sort not working → `display-conversion-grids.md` `{#display.grid-patterns.sortfield-rules}`
- Duplicate search/filter UX with record grid → `display-conversion-grids.md` `{#display.grid-search-filter}`
- Missing refreshAfter on grid with actions → `display-conversion-grids.md` `{#display.grid-refresh-after}`
- Chart shows no data → `display-conversion-charts.md` `{#display.chart-refactoring}`
- Chart grouping shows IDs instead of names → `display-conversion-charts.md` `{#display.chart-refactoring.grouping-fields}`
- Invalid stacking parameter location → `display-conversion-charts.md` `{#display.chart-components.stacking}`
- Invalid interval value → `display-conversion-charts.md` `{#display.chart-components.intervals}`
- KPI shows null → `display-conversion-kpis.md` `{#display.kpi-aggregation}`
- Action buttons not converted → `display-conversion-actions.md` `{#display.action-buttons}`
- View action incorrectly as related action → `display-conversion-actions.md` `{#display.action-buttons.view}`
- **Record List Action used in grid column** → `display-conversion-actions.md` `{#display.action-type-rules.mistakes}`
- Related actions missing identifier → `display-conversion-actions.md` `{#display.action-buttons.related}`

**Query-Related Errors:**
- "Property not found" on query results → `conversion-queries.md` `{#common.query-construction}`
- Query filter nesting errors → `conversion-queries.md` `{#common.query-construction.filters-nesting}`
- "List of Variant" from append() → `conversion-queries.md` `{#common.dropdown-all-option}`
- Relationship navigation errors → `conversion-relationships.md` `{#common.relationship-navigation}`

**Validation Errors:**
- Null reference errors → `validation-enforcement-module.md` `{#validation.null-safety}`
- Date/DateTime type mismatch → `validation-enforcement-module.md` `{#validation.type-matching}`
- Unused variable warnings → `validation-enforcement-module.md` `{#validation.unused-variables}`

---

## 📚 Foundational References

These files contain patterns used by BOTH mockup generation and functional conversion:

- `/logic-guidelines/short-circuit-evaluation.md` - Why if() vs and()/or() for null safety
- `/logic-guidelines/null-safety-quick-ref.md` - Quick pattern lookup table
- `/logic-guidelines/datetime-handling.md` - Date/time type matching & operators
- `/logic-guidelines/pattern-matching.md` - a!match() for status/category lookups
- `/conversion-guidelines/common-conversion-patterns.md#common.query-parameters` - Filter patterns, valid operators
- `/conversion-guidelines/common-conversion-patterns.md#common.query-result-structures` - Property access by query type
