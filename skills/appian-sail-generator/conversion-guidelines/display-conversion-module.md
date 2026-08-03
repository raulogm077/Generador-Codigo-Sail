# Display Conversion Module {#display-module}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

**NAVIGATION INDEX** - This module has been split into focused sub-modules for efficient loading. Use the index below to find the specific pattern you need.

---

## 📑 Module Structure

### Core Patterns
**File:** [`display-conversion-core.md`](display-conversion-core.md)
**Load when:** Starting any display conversion, need interface detection or record links
**Contains:**
- Interface type identification (Dashboard, Report, List View, Detail View)
- Record link conversion (dynamicLink → recordLink)
- fv!identifier availability rules

### Grid Patterns
**File:** [`display-conversion-grids.md`](display-conversion-grids.md)
**Load when:** Converting grids with record data
**Contains:**
- Read-only grid with a!recordData()
- sortField validation rules
- Related record data (one-to-many)
- Custom search/filter → built-in features conversion

### Chart Patterns
**File:** [`display-conversion-charts.md`](display-conversion-charts.md)
**Load when:** Converting charts from mockup data to record queries
**Contains:**
- Mandatory chart refactoring (categories/series → data/config)
- Grouping field validation (Text/Date/DateTime/Boolean only)
- Integer FK grouping fixes (relationship navigation)
- Valid interval values for date groupings
- Chart component reference

### KPI Patterns
**File:** [`display-conversion-kpis.md`](display-conversion-kpis.md)
**Load when:** Converting KPI metrics to aggregation queries
**Contains:**
- Related KPIs (shared grouping) pattern
- Unrelated KPIs (different filters) pattern
- Value extraction from aggregation results
- Null safety for aggregation data

### Action Patterns
**File:** [`display-conversion-actions.md`](display-conversion-actions.md)
**Load when:** Converting action buttons or adding record actions
**Contains:**
- Action type rules (Record List vs Related)
- Primary key identification for Related Actions
- Grid action button conversion
- Toolbar action placement (header vs recordActions)
- refreshAfter parameter usage

---

## Quick Decision Tree

```
What are you converting?

├─ Grid with data
│  └─ Load: display-conversion-core.md + display-conversion-grids.md
│
├─ Chart with mockup data
│  └─ Load: display-conversion-core.md + display-conversion-charts.md
│
├─ KPI cards with metrics
│  └─ Load: display-conversion-core.md + display-conversion-kpis.md
│
├─ Action buttons (Create, Edit, Delete)
│  └─ Load: display-conversion-core.md + display-conversion-actions.md
│
├─ Dashboard (KPIs + Charts + Grid)
│  └─ Load: All modules
│
└─ Report (Grid with filters)
   └─ Load: display-conversion-core.md + display-conversion-grids.md
```

---

## Loading Strategy

**Always load:**
1. `display-conversion-core.md` - Foundation for all display conversions

**Then load specific modules based on interface components:**
- Has grids? → Add `display-conversion-grids.md`
- Has charts? → Add `display-conversion-charts.md`
- Has KPIs? → Add `display-conversion-kpis.md`
- Has action buttons? → Add `display-conversion-actions.md`

**Also load:**
- `/conversion-guidelines/common-conversion-patterns.md` - Query patterns, relationship navigation
- `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation

---

## Anchor Link Reference

For backward compatibility, here are the major anchor links mapped to their new locations:

| Old Anchor | New Location |
|------------|--------------|
| `{#display.detection}` | `display-conversion-core.md{#display-core.detection}` |
| `{#display.chart-refactoring}` | `display-conversion-charts.md{#display-charts.refactoring}` |
| `{#display.chart-refactoring.grouping-fields}` | `display-conversion-charts.md{#display-charts.grouping-fields}` |
| `{#display.kpi-aggregation}` | `display-conversion-kpis.md{#display-kpis.aggregation}` |
| `{#display.kpi-aggregation.grouped}` | `display-conversion-kpis.md{#display-kpis.aggregation.grouped}` |
| `{#display.kpi-aggregation.single}` | `display-conversion-kpis.md{#display-kpis.aggregation.single}` |
| `{#display.grid-patterns}` | `display-conversion-grids.md{#display-grids.patterns}` |
| `{#display.grid-patterns.sortfield-rules}` | `display-conversion-grids.md{#display-grids.sortfield-rules}` |
| `{#display.grid-search-filter}` | `display-conversion-grids.md{#display-grids.search-filter}` |
| `{#display.record-links}` | `display-conversion-core.md{#display-core.record-links}` |
| `{#display.record-links.fv-identifier}` | `display-conversion-core.md{#display-core.record-links.fv-identifier}` |
| `{#display.action-type-rules}` | `display-conversion-actions.md{#display-actions.type-rules}` |
| `{#display.action-type-rules.primary-key}` | `display-conversion-actions.md{#display-actions.type-rules.primary-key}` |
| `{#display.action-buttons}` | `display-conversion-actions.md{#display-actions.buttons}` |
| `{#display.grid-toolbar-actions}` | `display-conversion-actions.md{#display-actions.toolbar-actions}` |
| `{#display.grid-refresh-after}` | `display-conversion-actions.md{#display-actions.refresh-after}` |
| `{#display.chart-components}` | `display-conversion-charts.md{#display-charts.components}` |
| `{#display.chart-components.intervals}` | `display-conversion-charts.md{#display-charts.components.intervals}` |
