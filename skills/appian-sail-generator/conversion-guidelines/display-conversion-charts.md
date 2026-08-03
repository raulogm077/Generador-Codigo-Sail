# Display Conversion - Chart Patterns {#display-charts}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/display-conversion-core.md` - Interface detection
> - `/conversion-guidelines/common-conversion-patterns.md` - Query patterns
> - `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

Patterns for converting chart components from static mockup data to dynamic record queries, including grouping field validation and interval configuration.

---

## 📑 Module Navigation {#display-charts.nav}

- `{#display-charts.refactoring}` - Mandatory chart pattern conversion
- `{#display-charts.grouping-fields}` - Grouping field validation
- `{#display-charts.integer-fix}` - Integer/Decimal grouping field fixes
- `{#display-charts.intervals}` - Date/DateTime grouping with intervals
- `{#display-charts.components}` - Chart components reference
- `{#display-charts.components.intervals}` - Valid interval values

---

## Chart Pattern Refactoring {#display-charts.refactoring}

### MANDATORY Refactoring

**All charts with record data MUST use the data + config pattern, NOT the categories + series pattern.**

### Mockup vs Record Data Pattern {#display-charts.mockup-to-record}

```sail
/* ❌ MOCKUP PATTERN - Works with hardcoded data */
a!columnChartField(
  categories: {"Q1", "Q2", "Q3", "Q4"},
  series: {
    a!chartSeries(
      label: "Revenue",
      data: {100000, 125000, 150000, 175000}
    )
  }
)

/* ✅ RECORD DATA PATTERN - Required for live data */
a!columnChartField(
  data: a!recordData(
    recordType: 'recordType!Sale',
    filters: a!queryFilter(
      field: 'recordType!Sale.fields.year',
      operator: "=",
      value: 2024
    )
  ),
  config: a!columnChartConfig(
    primaryGrouping: a!grouping(
      field: 'recordType!Sale.fields.quarter',
      alias: "quarter"
    ),
    measures: {
      a!measure(
        function: "SUM",
        field: 'recordType!Sale.fields.amount',
        alias: "totalRevenue"
      )
    }
  )
)
```

### Chart Config Functions {#display-charts.config-functions}

| Chart Type | Config Function |
|------------|-----------------|
| Column chart | `a!columnChartConfig()` |
| Bar chart | `a!barChartConfig()` |
| Line chart | `a!lineChartConfig()` |
| Pie chart | `a!pieChartConfig()` |
| Area chart | `a!areaChartConfig()` |

### Config Function Parameters

```sail
a!columnChartConfig(
  primaryGrouping: a!grouping(
    field: 'recordType!Record.fields.categoryField',
    alias: "category"
  ),
  secondaryGrouping: a!grouping(  /* Optional - for stacked/grouped charts */
    field: 'recordType!Record.fields.seriesField',
    alias: "series"
  ),
  measures: {
    a!measure(
      function: "COUNT",  /* or "SUM", "AVG", "MIN", "MAX", "DISTINCT_COUNT" */
      field: 'recordType!Record.fields.measureField',  /* Required for SUM/AVG/MIN/MAX */
      alias: "count"
    )
  },
  sort: {
    a!chartSort(field: "category", ascending: true)
  }
)
```

---

## Grouping Field Validation {#display-charts.grouping-fields}

**🚨 BLOCKING GATE** - Cannot write chart code until grouping fields are validated.

**Rule:** Grouping fields MUST be Text, Date, DateTime, or Boolean. Integer/Decimal fields require relationship navigation to Text.

| Field Data Type | Action |
|-----------------|--------|
| **Text** | ✅ Use directly |
| **Date/DateTime** | ✅ Use with `interval` parameter |
| **Boolean** | ✅ Use directly |
| **Integer/Decimal** | ❌ STOP - Find Text alternative |

### Integer/Decimal Grouping Field Fix {#display-charts.integer-fix}

When grouping field is Integer (e.g., foreign key ID):

**Step 1:** Find the relationship in data-model-context.md
```
Field: organizationTypeId (Integer)
Relationship: organizationType → ORGANIZATION_TYPE record type
```

**Step 2:** Find Text field in target record type
```
ORGANIZATION_TYPE Fields:
- typeId (Integer) - primary key
- typeName (Text) ← USE THIS
```

**Step 3:** Use relationship navigation
```sail
/* ❌ WRONG - Integer field */
primaryGrouping: a!grouping(
  field: 'recordType!Submission.fields.organizationTypeId',
  alias: "type"
)

/* ✅ CORRECT - Navigate to Text field */
primaryGrouping: a!grouping(
  field: 'recordType!Submission.relationships.organizationType.fields.typeName',
  alias: "type"
)
```

### Date/DateTime Grouping with Intervals {#display-charts.intervals}

When grouping by Date or DateTime:

```sail
a!grouping(
  field: 'recordType!Sale.fields.saleDate',
  alias: "period",
  interval: "MONTH_SHORT_TEXT"  /* or "YEAR", "DATE_TEXT", "MONTH_OF_YEAR_NUMBER" */
)
```

**Common interval values:**
| Interval | Example Output |
|----------|----------------|
| `"MONTH_SHORT_TEXT"` | "Jan", "Feb", "Mar" |
| `"MONTH_TEXT"` | "January", "February" |
| `"YEAR"` | "2024", "2025" |
| `"DATE_TEXT"` | "Jan 15, 2024" |
| `"MONTH_OF_YEAR_NUMBER"` | 1, 2, 3 |

---

## Chart Components Reference {#display-charts.components}

### Available Chart Functions {#display-charts.components.functions}

1. `a!areaChartField()` - Filled areas under lines for trends and cumulative values
2. `a!barChartField()` - Horizontal bars for comparing categories
3. `a!columnChartField()` - Vertical bars for comparing values across categories
4. `a!lineChartField()` - Connected points for trends over time
5. `a!pieChartField()` - Pie slices for part-to-whole relationships
6. `a!scatterChartField()` - Points on X/Y axes for correlations (record data only)

### Parameters Shared by All Chart Types {#display-charts.components.parameters}

- `label`, `labelPosition` (usually "COLLAPSED"), `instructions`
- `height` - Values vary by type:
  - Column/Line/Area/Bar: "MICRO", "SHORT", "MEDIUM", "TALL" (Bar also has "AUTO")
  - Pie/Scatter: "SHORT", "MEDIUM", "TALL"
- `showWhen`, `accessibilityText`
- `xAxisTitle`, `yAxisTitle` (not available for pie charts)
- `showLegend` (column, line, bar, area only - NOT pie)
- `showDataLabels`, `colorScheme`

### 🚨 Stacking Property Rules {#display-charts.components.stacking}

**ONLY these chart types have a `stacking` property:**
- `a!areaChartField()`
- `a!barChartField()`
- `a!columnChartField()`

**The `stacking` property is on the CHART FIELD, NOT in the config:**
```sail
/* ✅ CORRECT - stacking on chart field */
a!columnChartField(
  data: a!recordData(...),
  config: a!columnChartConfig(...),
  stacking: "NORMAL"  /* On chart field level */
)

/* ❌ WRONG - stacking in config (parameter doesn't exist there) */
a!columnChartField(
  data: a!recordData(...),
  config: a!columnChartConfig(
    stacking: "NORMAL"  /* INVALID - not a config parameter */
  )
)
```

**Valid stacking values:** "NONE" (default), "NORMAL", "PERCENT_TO_TOTAL"

### Two Data Approaches for Charts {#display-charts.components.data-approaches}

**Approach 1: Static Mockup Data** (categories + series)
- Use for: Column, Line, Bar, Area, Pie charts with hardcoded sample data
- Structure:
```sail
a!columnChartField(
  categories: {"Q1", "Q2", "Q3", "Q4"},
  series: {
    a!chartSeries(label: "Sales", data: {100, 120, 115, 140}, color: "#3B82F6")
  }
)
```

**Approach 2: Record Data** (data + config)
- Use for: ALL charts when connecting to live record data
- ⚠️ Scatter charts ONLY work with this approach
- Structure:
```sail
a!columnChartField(
  data: a!recordData(...),
  config: a!columnChartConfig(
    primaryGrouping: a!grouping(...),
    measures: {a!measure(...)}
  )
)
```

❌ **NEVER mix approaches:** Don't use `categories` + `series` with record data
❌ **NEVER use scatter charts with static mockup data** - they require record data

### Chart Config Parameters {#display-charts.components.config-params}

**Valid Parameters for Chart Config Functions:**
- `primaryGrouping` - a!grouping() for main data grouping
- `secondaryGrouping` - a!grouping() for multi-series charts
- `measures` - Array of a!measure() for aggregations
- `sort` - a!sortInfo() for ordering results
- `dataLimit` - Maximum number of data points
- `link` - Dynamic link for click actions
- `showIntervalsWithNoData` - Boolean for showing empty intervals

**❌ INVALID Parameters (Don't Use):**
- `stacking` - This is on the chart field, NOT in config
- `aggregations` - Use `measures` instead
- `aggregationFields` - Use `measures` instead

### 🚨 Valid Interval Values for a!grouping() {#display-charts.components.intervals}

**The `interval` parameter in a!grouping() can ONLY be used with Date/DateTime/Time fields.**

**Valid interval values:**
- "AUTO" (default), "YEAR"
- "MONTH_OF_YEAR", "MONTH_OF_YEAR_SHORT_TEXT", "MONTH_OF_YEAR_TEXT"
- "MONTH_TEXT", "MONTH_SHORT_TEXT", "MONTH_DATE"
- "DATE", "DATE_SHORT_TEXT", "DATE_TEXT"
- "DAY_OF_MONTH"
- "HOUR_OF_DAY", "HOUR"
- "MINUTE_OF_HOUR", "MINUTE"

```sail
/* ✅ CORRECT - Valid interval values */
a!grouping(
  field: 'recordType!Case.fields.createdOn',
  alias: "month_grouping",
  interval: "MONTH_SHORT_TEXT"  /* Valid - shows "Jan", "Feb", etc. */
)

/* ❌ WRONG - Invalid interval values */
a!grouping(
  field: 'recordType!Case.fields.createdOn',
  alias: "month_grouping",
  interval: "MONTH"  /* INVALID - not in allowed list */
)

a!grouping(
  field: 'recordType!Case.fields.modifiedOn',
  alias: "week_grouping",
  interval: "WEEK"  /* INVALID - not in allowed list */
)
```

**Rule**: Only use interval values from the documented list above. For weekly groupings, use "DATE_SHORT_TEXT" or "DATE" instead.

### Complete Record Data Chart Example {#display-charts.components.complete-example}

```sail
a!columnChartField(
  labelPosition: "COLLAPSED",
  data: a!recordData(
    recordType: 'recordType!Case',
    filters: a!queryFilter(
      field: 'recordType!Case.fields.isActive',
      operator: "=",
      value: true
    )
  ),
  config: a!columnChartConfig(
    primaryGrouping: a!grouping(
      field: 'recordType!Case.relationships.status.fields.value',
      alias: "status_grouping"
    ),
    measures: {
      a!measure(
        function: "COUNT",
        field: 'recordType!Case.fields.id',
        alias: "case_count"
      )
    },
    dataLimit: 20
  ),
  xAxisTitle: "Status",
  yAxisTitle: "Number of Cases",
  showDataLabels: true,
  height: "MEDIUM"
)
```

### Chart Data Extraction Rules {#display-charts.components.extraction}

**CRITICAL**: Charts are display-only components
- **Cannot extract data from chart components** - Only from queries
- **Use separate aggregation queries for KPIs** - Don't try to read chart data

---

## Chart Conversion Checklist {#display-charts.checklist}

**Charts:**
- [ ] All charts use data + config pattern (NOT categories + series)
- [ ] Chart config function matches chart type
- [ ] All grouping fields validated (Text, Date, DateTime, Boolean - no Integer)
- [ ] Integer FK groupings converted to relationship navigation to Text
- [ ] Date groupings have appropriate interval parameter
- [ ] Interval values from valid list only
- [ ] Stacking property (if used) is on chart field, not in config
- [ ] Scatter charts use record data (not mockup data)
