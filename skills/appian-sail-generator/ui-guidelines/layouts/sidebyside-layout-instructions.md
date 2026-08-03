# SAIL SideBySideLayout Usage Instructions

## Overview
SideBySideLayout arranges components (not layouts) horizontally. Use for component-level arrangements like icon+text, stamp+description, label+value.

## ⚠️ CRITICAL RULE: Never Nest SideBySideLayouts
If you need nested horizontal arrangements, use columnsLayout instead or flatten into a single sideBySideLayout.

---

## ⚠️ CRITICAL: Width Values for SideBySideItem

### ✅ VALID Width Values (ONLY These)
```
"AUTO"      - Fill remaining space (default)
"MINIMIZE"  - Shrink to fit content
"1X" to "10X" - Proportional widths
```

### ❌ INVALID Width Values (Runtime Errors)
**These are for a!columnLayout ONLY:**
```
"NARROW", "NARROW_PLUS", "MEDIUM", "MEDIUM_PLUS",
"WIDE", "WIDE_PLUS", "EXTRA_NARROW"  ❌ ALL WRONG
```

**Common Mistake:**
```sail
/* ❌ WRONG */
a!sideBySideItem(
  item: a!dropdownField(...),
  width: "NARROW"  /* ERROR */
)

/* ✅ CORRECT */
a!sideBySideItem(
  item: a!dropdownField(...),
  width: "MINIMIZE"
)
```

---

## Critical Restrictions

### ❌ NEVER:
- Nest sideBySideLayouts
- Put layouts (cardLayout, columnsLayout) in sideBySideItems
- Put arrays of components in sideBySideItems
- Use in grid columns

### ✅ ONLY:
- Single components in each sideBySideItem
- Use for component-level arrangements

---

## Quick Reference

### Width Selection
- Icons/stamps: `"MINIMIZE"`
- Labels/short text: `"MINIMIZE"`
- Main content: `"AUTO"`
- Equal columns: `"1X"`, `"2X"`, etc.

### Vertical Alignment
- `"TOP"` (default), `"MIDDLE"`, `"BOTTOM"`

### Spacing
- `"STANDARD"` (default), `"NONE"`, `"DENSE"`, `"SPARSE"`
- ❌ Don't use `"less"` or `"more"`

---

## Common Patterns

### Icon + Text
```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: a!richTextIcon(icon: "check", color: "POSITIVE"),
        labelPosition: "COLLAPSED"
      ),
      width: "MINIMIZE"
    ),
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: "Task completed",
        labelPosition: "COLLAPSED"
      ),
      width: "AUTO"
    )
  },
  alignVertical: "MIDDLE"
)
```

### Stamp + Description
```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!stampField(
        icon: "user",
        backgroundColor: "#3B82F6",
        size: "TINY",
        labelPosition: "COLLAPSED"
      ),
      width: "MINIMIZE"
    ),
    a!sideBySideItem(
      item: a!richTextDisplayField(
        labelPosition: "COLLAPSED",
        value: {
          a!richTextItem(text: "John Doe", style: "STRONG"),
          char(10),
          "Software Engineer"
        }
      ),
      width: "AUTO"
    )
  },
  alignVertical: "MIDDLE"
)
```

### Label + Value
```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!richTextDisplayField(
        labelPosition: "COLLAPSED",
        value: a!richTextItem(text: "Status:", style: "STRONG")
      ),
      width: "MINIMIZE"
    ),
    a!sideBySideItem(
      item: a!tagField(
        labelPosition: "COLLAPSED",
        tags: a!tagItem(text: "Active", backgroundColor: "POSITIVE")
      ),
      width: "AUTO"
    )
  },
  alignVertical: "MIDDLE"
)
```

### Proportional Fields
```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!textField(label: "First Name", value: local!firstName),
      width: "3X"
    ),
    a!sideBySideItem(
      item: a!textField(label: "M.I.", value: local!mi),
      width: "1X"
    ),
    a!sideBySideItem(
      item: a!textField(label: "Last Name", value: local!lastName),
      width: "3X"
    )
  }
)
```

---

## When to Use What

### Use SideBySideLayout:
- Icon next to text
- Stamp with description
- Label and value pairs
- Small related UI elements

### Use ColumnsLayout:
- Main page structure
- Content sections with margins
- Fixed-width columns
- Nested layouts

---

## VALIDATION CHECKLIST
- [ ] ⚠️ Width is `"AUTO"`, `"MINIMIZE"`, or `"1X"`-`"10X"` ONLY
- [ ] ❌ NOT using `"NARROW"`, `"MEDIUM"`, `"WIDE"` (columnLayout widths)
- [ ] ⚠️ Spacing is `"STANDARD"`, `"NONE"`, `"DENSE"`, or `"SPARSE"`
- [ ] ❌ NOT using `"less"` or `"more"` for spacing
- [ ] Single component per sideBySideItem (no arrays)
- [ ] No layouts in sideBySideItems
- [ ] No nested sideBySideLayouts
