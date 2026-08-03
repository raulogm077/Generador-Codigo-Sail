# SAIL Gauge Component Usage Instructions

## Overview
`a!gaugeField` shows a circular progress indicator with a value displayed in the center. The center value (`primaryText`) can be plain text, but for the common visual styles — a fraction like "25/26", a percentage like "78%", or a status icon — Appian provides three helper sub-components: `a!gaugeFraction`, `a!gaugePercentage`, and `a!gaugeIcon`.

Use these helpers instead of building the centre text manually with `text()` and `concat()` — they handle formatting and styling automatically.

```sail
/* GOOD - Three common gauge presentations */
a!columnsLayout(
  columns: {
    a!columnLayout(contents: {
      a!gaugeField(
        label: "Completion",
        percentage: 78,
        primaryText: a!gaugePercentage(),  /* shows "78%" */
        color: "ACCENT"
      )
    }),
    a!columnLayout(contents: {
      a!gaugeField(
        label: "Tasks done",
        percentage: 25/26 * 100,
        primaryText: a!gaugeFraction(denominator: 26),  /* shows "25/26" */
        color: "POSITIVE"
      )
    }),
    a!columnLayout(contents: {
      a!gaugeField(
        label: "Health",
        percentage: 100,
        primaryText: a!gaugeIcon(icon: "check-circle"),
        color: "POSITIVE"
      )
    })
  }
)
```

## When to use each sub-component

| Goal in screenshot/request | Use this `primaryText` |
|---|---|
| Big "X / Y" inside the gauge | `a!gaugeFraction(denominator: Y)` |
| Big "X%" inside the gauge | `a!gaugePercentage()` |
| Big status icon inside the gauge | `a!gaugeIcon(icon: "...")` |
| Custom multi-line text | Plain text (rich text is **not** allowed in `primaryText`) |

## a!gaugeFraction Parameters

| Parameter | Type | Description |
|---|---|---|
| `denominator` | Number | Required. The "Y" in "X / Y". The numerator is computed automatically from the parent `a!gaugeField.percentage` (rounded). |

**Example**: To render "8 / 10", set `percentage: 80` on the gauge and `denominator: 10` on the fraction.

## a!gaugePercentage Parameters

Takes **no parameters**. Always renders the parent gauge's `percentage` value followed by `%`, rounded to the integer.

```sail
a!gaugeField(
  percentage: 67.3,
  primaryText: a!gaugePercentage()    /* shows "67%" */
)
```

## a!gaugeIcon Parameters

| Parameter | Type | Description |
|---|---|---|
| `icon` | Text | Required. Icon key from `rich-text-icon-aliases.md`. |
| `altText` | Text | Alternate text shown in hover tooltip and used by screen readers. |
| `color` | Text | Icon color. Valid values: hex color or `"ACCENT"`, `"POSITIVE"`, `"NEGATIVE"`, `"WARN"`. Defaults to the gauge field color. Use `fv!percentage` for conditional coloring. |

Note: the icon component used inside `primaryText` is **`a!gaugeIcon`**, not `a!richTextIcon`. The `primaryText` slot is plain text + gauge helpers — not richText.

### Color examples

```sail
/* Use fv!percentage to color the icon dynamically */
a!gaugeIcon(
  icon: if(fv!percentage >= 80, "check-circle", "exclamation-triangle"),
  color: if(fv!percentage >= 80, "POSITIVE", "NEGATIVE"),
  altText: "Completion status"
)
```

## Validation Checklist

Before finalizing a gauge:

- [ ] If the gauge needs to show a fraction → `primaryText` is `a!gaugeFraction(denominator: …)`, not a hand-built string
- [ ] If the gauge needs to show a percentage → `primaryText` is `a!gaugePercentage()`, not `text(percent, "0%")`
- [ ] If the gauge needs to show an icon → `primaryText` is `a!gaugeIcon(icon: …)`, not `a!richTextIcon` (which crashes)
- [ ] The `icon` alias passed to `a!gaugeIcon` exists in `rich-text-icon-aliases.md`
- [ ] The `percentage` value (on the parent gauge) is consistent with the fraction's numerator when `a!gaugeFraction` is used

## Anti-Patterns

| ❌ Don't | ✅ Do |
|---|---|
| `primaryText: text(round(local!completion / local!total * 100, 0)) & "%"` | `primaryText: a!gaugePercentage()` (and set `percentage:` correctly) |
| `primaryText: text(local!done) & "/" & text(local!total)` | `primaryText: a!gaugeFraction(denominator: local!total)` |
| `primaryText: a!richTextIcon(icon: "...")` | `primaryText: a!gaugeIcon(icon: "...")` |
