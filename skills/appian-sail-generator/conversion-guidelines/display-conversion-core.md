# Display Conversion Core Module {#display-core}

> **Parent guide:** `/conversion-guidelines/CONVERSION-PRIMARY-REFERENCE.md`
>
> **Related modules:**
> - `/conversion-guidelines/display-conversion-grids.md` - Grid-specific patterns
> - `/conversion-guidelines/display-conversion-charts.md` - Chart conversion patterns
> - `/conversion-guidelines/display-conversion-kpis.md` - KPI aggregation patterns
> - `/conversion-guidelines/display-conversion-actions.md` - Record actions and buttons
> - `/conversion-guidelines/common-conversion-patterns.md` - Shared patterns (queries, relationships)
> - `/conversion-guidelines/validation-enforcement-module.md` - Post-conversion validation
>
> **Foundational rules:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`

Core patterns for identifying and converting display interfaces: interface detection, record links, and fundamental display patterns.

---

## 📑 Module Navigation {#display-core.nav}

- `{#display-core.detection}` - How to identify display interfaces
- `{#display-core.record-links}` - Converting navigation links
- `{#display-core.record-links.fv-identifier}` - fv!identifier availability rules
- `{#display-core.record-links.patterns}` - Conversion patterns for links

---

## Interface Detection {#display-core.detection}

### Display Interface Indicators

A mockup is a **Display Interface** if it contains:

| Indicator | Example |
|-----------|---------|
| Dashboard layout | KPI cards, charts, summary metrics |
| Report/Analytics | Aggregated data, trends, comparisons |
| List views | Read-only grids with filter/search |
| Detail views | Record information display (no edit) |
| Charts | Bar, line, pie, column charts |
| No submission buttons | View/filter only controls |

### Decision Tree

```
Does interface primarily display data?
├─ YES → Continue checking
│   └─ Does it have charts or KPIs?
│       ├─ YES → Use DISPLAY MODULES with chart/KPI patterns
│       └─ NO → Use DISPLAY MODULES with grid patterns
│
└─ NO (creates/updates data) → Use FORM CONVERSION MODULE
```

### Display Interface Types

| Type | Characteristics | Key Patterns |
|------|-----------------|--------------|
| Dashboard | KPIs + charts + summary grid | Aggregation queries, chart config |
| Report | Filtered data grid + export | a!recordData(), sortField rules |
| List View | Searchable/filterable grid | Filters with applyWhen |
| Detail View | Single record display | Query by ID, **empty check on .data before indexing**, relationship navigation |

---

## Record Links {#display-core.record-links}

### Converting dynamicLink to recordLink

Mockups use `a!dynamicLink()` as placeholders. Convert to `a!recordLink()` for record navigation.

### Detection

```bash
grep -n "a!dynamicLink" output/[mockup-file].sail
```

### fv!identifier Availability Rules {#display-core.record-links.fv-identifier}

**🚨 CRITICAL:** `fv!identifier` is ONLY available in specific contexts where Appian provides it.

**✅ Available Contexts:**
| Context | fv!identifier Available? |
|---------|--------------------------|
| Grid columns with `a!recordData()` | ✅ YES - provided automatically |
| Grid `recordActions` parameter | ✅ YES - for row-specific actions |

**❌ NOT Available Contexts:**
| Context | fv!identifier Available? | Use Instead |
|---------|--------------------------|-------------|
| `a!forEach()` over query `.data` | ❌ NO | `fv!item[recordType!Record.fields.primaryKey]` |
| `a!forEach()` over any array | ❌ NO | Primary key field from fv!item |
| Manual array iterations | ❌ NO | Primary key field |
| Detail view interfaces | ❌ NO | `ri!recordId` parameter |

### Conversion Patterns {#display-core.record-links.patterns}

**Grid column with record link (fv!identifier works):**
```sail
/* ❌ MOCKUP */
a!richTextItem(
  text: fv!row.caseNumber,
  link: a!dynamicLink(value: fv!row.id, saveInto: {})
)

/* ✅ FUNCTIONAL - fv!identifier provided by a!recordData() */
a!gridField(
  data: a!recordData(recordType: 'recordType!Case'),
  columns: {
    a!gridColumn(
      label: "Case Number",
      value: a!richTextDisplayField(
        value: a!richTextItem(
          text: fv!row['recordType!Case.fields.caseNumber'],
          link: a!recordLink(
            recordType: 'recordType!Case',
            identifier: fv!identifier  /* ✅ Works here */
          ),
          linkStyle: "STANDALONE"
        )
      )
    )
  }
)
```

**forEach over query results (fv!identifier does NOT work):**
```sail
/* Query results stored in local variable */
local!cases: a!queryRecordType(
  recordType: 'recordType!Case',
  fields: {
    'recordType!Case.fields.caseId',  /* MUST include primary key */
    'recordType!Case.fields.caseNumber',
    'recordType!Case.fields.title'
  },
  pagingInfo: a!pagingInfo(startIndex: 1, batchSize: 50)
).data,

/* ❌ WRONG - fv!identifier doesn't exist in a!forEach */
a!forEach(
  items: local!cases,
  expression: a!cardLayout(
    contents: {
      a!richTextItem(
        text: fv!item['recordType!Case.fields.caseNumber'],
        link: a!recordLink(
          recordType: 'recordType!Case',
          identifier: fv!identifier  /* ❌ ERROR - Not available! */
        )
      )
    }
  )
)

/* ✅ CORRECT - Use primary key field */
a!forEach(
  items: local!cases,
  expression: a!cardLayout(
    contents: {
      a!richTextItem(
        text: fv!item['recordType!Case.fields.caseNumber'],
        link: a!recordLink(
          recordType: 'recordType!Case',
          identifier: fv!item['recordType!Case.fields.caseId']  /* ✅ Use primary key */
        )
      )
    }
  )
)
```

### Key Rules for Record Links

1. **When using `a!recordData()` in grids/charts**: Use `fv!identifier`
2. **When using `a!queryRecordType().data` with `a!forEach()`**: Use the primary key field
3. **Always query the primary key field** when you need record links in `a!forEach()`
4. **Primary key fields are typically**: `id`, `caseId`, `orderId`, `employeeId`, etc.

---

## Display Core Conversion Checklist {#display-core.checklist}

**Interface Type:**
- [ ] Interface type identified (Dashboard, Report, List View, Detail View)
- [ ] Appropriate module selected for specialized patterns

**Record Links:**
- [ ] `a!dynamicLink()` converted to `a!recordLink()`
- [ ] Record link identifier matches context
- [ ] Primary key field queried when using `a!forEach()` with record links
- [ ] `fv!identifier` only used in grid columns with `a!recordData()`
