# Chart Data Configuration {#chart-configuration}

> **Parent guide:** `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:**
> - `logic-guidelines/functions-reference.md` (function reference)
> - `/ui-guidelines/components/chart-instructions.md` (detailed chart documentation)

---

## Mock Data Charts (Prototyping)

```sail
a!barChartField(
  categories: {"Sales", "Engineering"},
  series: {
    a!chartSeries(
      label: "Employees",
      data: {25, 45}
    )
  }
)
```

---

## Chart Data Extraction Rules

**CRITICAL**: Charts are display-only components
- **Cannot extract data from chart components** - Only from queries
- **Use separate calculations for KPIs** - Don't try to read chart data

---

## Chart Components Usage

**Available Chart Functions:**
1. `a!areaChartField()` - Filled areas under lines for trends and cumulative values
2. `a!barChartField()` - Horizontal bars for comparing categories
3. `a!columnChartField()` - Vertical bars for comparing values across categories
4. `a!lineChartField()` - Connected points for trends over time
5. `a!pieChartField()` - Pie slices for part-to-whole relationships

---

## Parameters Shared by All Chart Types

- `label`, `labelPosition` (usually "COLLAPSED"), `instructions`
- `height` - Values vary by type:
  - Column/Line/Area/Bar: "MICRO", "SHORT", "MEDIUM", "TALL" (Bar also has "AUTO")
  - Pie: "SHORT", "MEDIUM", "TALL"
- `showWhen`, `accessibilityText`
- `xAxisTitle`, `yAxisTitle` (not available for pie charts)
- `showLegend` (column, line, bar, area only - NOT pie)
- `showDataLabels`, `colorScheme`

---

## 🚨 CRITICAL: Stacking Property

**ONLY these chart types have a `stacking` property:**
- `a!areaChartField()`
- `a!barChartField()`
- `a!columnChartField()`

**The `stacking` property is on the CHART FIELD, NOT in the config:**
```sail
/* ✅ CORRECT - stacking on chart field */
a!columnChartField(
  categories: {"Q1", "Q2", "Q3", "Q4"},
  series: {
    a!chartSeries(label: "Sales", data: {100, 120, 115, 140})
  },
  stacking: "NORMAL"  /* On chart field level */
)

/* ❌ WRONG - stacking doesn't exist for mock data charts with categories/series */
```

**Valid stacking values:** "NONE" (default), "NORMAL", "PERCENT_TO_TOTAL"

---

## Mock Data: Static Mockup Data

Use for: Column, Line, Bar, Area, Pie charts with hardcoded sample data

**Structure:**
```sail
a!columnChartField(
  categories: {"Q1", "Q2", "Q3", "Q4"},
  series: {
    a!chartSeries(label: "Sales", data: {100, 120, 115, 140}, color: "#3B82F6")
  }
)
```

❌ **NEVER use scatter charts with static mockup data** - they require record data

---

## Multi-Series Charts

```sail
a!columnChartField(
  categories: {"Q1", "Q2", "Q3", "Q4"},
  series: {
    a!chartSeries(label: "Sales", data: {100, 120, 115, 140}, color: "#3B82F6"),
    a!chartSeries(label: "Costs", data: {80, 90, 85, 95}, color: "#EF4444"),
    a!chartSeries(label: "Profit", data: {20, 30, 30, 45}, color: "#10B981")
  },
  showLegend: true,
  stacking: "NONE"
)
```

---

## Pie Chart Example

```sail
a!pieChartField(
  series: {
    a!chartSeries(
      label: "Distribution",
      data: {35, 25, 20, 15, 5}
    )
  },
  categories: {"Marketing", "Engineering", "Sales", "Operations", "Admin"},
  showDataLabels: true,
  height: "MEDIUM"
)
```

---

## Line Chart Example

```sail
a!lineChartField(
  categories: {"Jan", "Feb", "Mar", "Apr", "May", "Jun"},
  series: {
    a!chartSeries(label: "2023", data: {100, 110, 105, 120, 130, 125}),
    a!chartSeries(label: "2024", data: {120, 135, 130, 145, 160, 155})
  },
  xAxisTitle: "Month",
  yAxisTitle: "Revenue ($K)",
  showLegend: true,
  height: "MEDIUM"
)
```

---

## Area Chart Example

```sail
a!areaChartField(
  categories: {"Week 1", "Week 2", "Week 3", "Week 4"},
  series: {
    a!chartSeries(label: "Active Users", data: {1000, 1200, 1150, 1400})
  },
  stacking: "NORMAL",
  height: "MEDIUM"
)
```

---

## Best Practices Summary

### ✅ DO:
- **Use appropriate chart type** for the data being displayed
- **Set labelPosition to "COLLAPSED"** when label isn't needed
- **Use meaningful series labels** for legend clarity
- **Use hex colors** for consistent branding
- **Set height appropriately** for the context

### ❌ DON'T:
- **Don't try to extract data** from chart components
- **Don't use scatter charts** with static mockup data
- **Don't forget showLegend** for multi-series charts
- **Don't use pie charts** for more than 5-6 categories
- **Don't set stacking on line/pie charts** (not supported)
