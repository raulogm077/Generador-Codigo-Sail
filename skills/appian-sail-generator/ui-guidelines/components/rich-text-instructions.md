# SAIL Rich Text Usage Instructions

## ⚠️ CRITICAL: Icon Validation
**BEFORE using `a!richTextIcon()` with ANY icon:**
- [ ] Read `/ui-guidelines/reference/rich-text-icon-aliases.md` to verify icon name exists
- [ ] NEVER guess icon names - always look up first

---

## Overview
Rich text components in SAIL provide formatted text display with styling, icons, images, links, and lists. They're essential for creating visually appealing and semantic text content in interfaces.

## Core Rich Text Components

### a!richTextDisplayField
Primary container for displaying formatted text content.

```sail
a!richTextDisplayField(
  value: {
    a!richTextItem(text: "Hello ", style: "STRONG"),
    a!richTextItem(text: "World", color: "ACCENT")
  },
  align: "LEFT"
)
```

**Key Parameters:**
- `value`: Array of valid rich text children (see list below)
- `align`: Text alignment (LEFT, CENTER, RIGHT) — not available when the value contains a bulleted or numbered list
- `preventWrapping`: Single line with truncation (default: false)
- `tooltip`: Mouseover text

**Valid children of `value`** (any other component or plain string causes a runtime error):
- `a!richTextItem` — styled text segment (most common)
- `a!richTextIcon` — inline icon
- `a!richTextBulletedList` — bullet list container
- `a!richTextNumberedList` — numbered list container
- `a!richTextListItem` — nested list item (inside the two list components above)
- `a!richTextImage` — inline icon-sized image (wraps `a!documentImage` / `a!userImage` / `a!webImage`)
- `a!richTextHeader` — header text **(deprecated by Appian — prefer `a!headingField` outside richText)**
- Plain text strings are also allowed inline

### a!richTextItem
Individual styled text element within rich text displays.

**Key Parameters:**
- `text`: Text content or nested rich text items
- `style`: Text styling (PLAIN, EMPHASIS, STRONG, UNDERLINE, STRIKETHROUGH)
- `size`: Text size (SMALL through EXTRA_LARGE)
- `color`: Text color (STANDARD, ACCENT, POSITIVE, NEGATIVE, SECONDARY, or hex)
- `link`: Makes text clickable
- `linkStyle`: Link appearance (INLINE - underlined, STANDALONE - not underlined)

## Rich Text Size Reference
```sail
/* Size hierarchy with pixel equivalents */
- SMALL: 12px
- STANDARD: 14px (default)
- MEDIUM: 17px
- MEDIUM_PLUS: 24px /* the best size for most section headings */
- LARGE: 32px /* the best size for most page titles */
- LARGE_PLUS: 52px
- EXTRA_LARGE: 72px
```

## When to Use Rich Text vs Alternatives

### ✅ Use a!richTextDisplayField For:
- **Any read-only text** - for display text that's not user-editable
- **Formatted text content** - Multiple styles, colors, sizes in one block
- **Mixed content** - Text + icons + links together
- **Headings and descriptions** - When you need styling control
- **Status messages** - Colored text for success/error states
- **Lists** - Bulleted or numbered lists
- **Complex labels** - When basic field labels aren't enough

### ❌ Use Alternatives Instead:
- **Accessible section headings** → `a!headingField()`

## Common Rich Text Patterns

### 1. Status Messages
```sail
a!richTextDisplayField(
  value: {
    a!richTextIcon(
      icon: "check-circle",
      color: "POSITIVE",
      size: "MEDIUM"
    ),
    " ",
    a!richTextItem(
      text: "Task completed successfully",
      color: "POSITIVE",
      style: "STRONG"
    )
  },
  align: "LEFT"
)
```

### 2. Icon with Text
```sail
a!richTextDisplayField(
  value: {
    a!richTextIcon(
      icon: "user",
      color: "#3B82F6"
    ),
    " ",
    a!richTextItem(
      text: "John Doe",
      style: "STRONG"
    ),
    char(10),
    a!richTextItem(
      text: "Software Engineer",
      color: "SECONDARY",
      size: "SMALL"
    )
  }
)
```

### 3. Linked Text
```sail
a!richTextDisplayField(
  value: {
    "Read more about ",
    a!richTextItem(
      text: "our policies",
      link: a!safeLink(
        uri: "https://example.com/policies",
        label: "our policies"
      ),
      linkStyle: "INLINE"
    ),
    " for detailed information."
  }
)
```

### 4. Multi-Level Information
```sail
a!richTextDisplayField(
  value: {
    a!richTextItem(
      text: "Order #12345",
      size: "MEDIUM",
      style: "STRONG"
    ),
    char(10),
    a!richTextItem(
      text: "Shipped: ",
      style: "STRONG"
    ),
    "March 15, 2024",
    char(10),
    a!richTextItem(
      text: "Status: ",
      style: "STRONG"
    ),
    a!richTextItem(
      text: "In Transit",
      color: "ACCENT"
    )
  }
)
```

### 5. Line Breaks and Spacing
```sail
a!richTextDisplayField(
  value: {
    "First line of text",
    char(10),           /* Single line break */
    "Second line of text",
    char(10),
    char(10),           /* Double line break (paragraph) */
    "Third paragraph of text"
  }
)
```

## Using Rich Text in SideBySideLayout

### Vertical Alignment of Different-Sized Items
When you need to align items of different sizes (like icons and headings), use separate `a!richTextDisplayField` components within `a!sideBySideLayout` rather than combining everything in a single rich text field.

```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: a!richTextIcon(
          icon: "check-circle",
          color: "POSITIVE",
          size: "LARGE"
        ),
        labelPosition: "COLLAPSED"
      ),
      width: "MINIMIZE"
    ),
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: a!richTextItem(
          text: "Task Completed",
          size: "MEDIUM_PLUS",
          style: "STRONG"
        ),
        labelPosition: "COLLAPSED"
      ),
      width: "AUTO"
    )
  },
  alignVertical: "MIDDLE"
)
```

### Multi-Line Content with Icon
For complex content with an icon, separate the components for better alignment control:

```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: a!richTextIcon(
          icon: "user-circle",
          color: "#3B82F6",
          size: "LARGE"
        ),
        labelPosition: "COLLAPSED"
      ),
      width: "MINIMIZE"
    ),
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: {
          a!richTextItem(
            text: "John Doe",
            size: "MEDIUM",
            style: "STRONG"
          ),
          char(10),
          a!richTextItem(
            text: "Senior Developer",
            color: "SECONDARY",
            size: "SMALL"
          ),
          char(10),
          a!richTextItem(
            text: "Last active: 2 hours ago",
            color: "SECONDARY",
            size: "SMALL"
          )
        },
        labelPosition: "COLLAPSED"
      ),
      width: "AUTO"
    )
  },
  alignVertical: "MIDDLE",
  spacing: "STANDARD"
)
```

### Button with Rich Text Label
When combining interactive elements with formatted text:

```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      item: a!richTextDisplayField(
        value: {
          a!richTextItem(
            text: "Project Status",
            size: "MEDIUM",
            style: "STRONG"
          ),
          char(10),
          a!richTextItem(
            text: "Ready for review",
            color: "POSITIVE",
            size: "SMALL"
          )
        },
        labelPosition: "COLLAPSED"
      ),
      width: "AUTO"
    ),
    a!sideBySideItem(
      item: a!buttonArrayLayout(
        buttons: a!buttonWidget(
          label: "Review",
          style: "OUTLINE",
          size: "SMALL"
        ),
        marginBelow: "NONE"
      ),
      width: "MINIMIZE"
    )
  },
  alignVertical: "MIDDLE"
)
```

### ✅ Best Practices for SideBySide Rich Text:
- Always set `labelPosition: "COLLAPSED"` on rich text fields in sideBySideLayout
- Use `alignVertical: "MIDDLE"` for consistent alignment
- Set appropriate width values (MINIMIZE for icons/buttons, AUTO for text that should take up remaining space)
- Consider spacing between items with the `spacing` parameter

### ❌ Common Mistakes:
- Forgetting `labelPosition: "COLLAPSED"` (causes alignment issues)
- Putting too much content in a single rich text field instead of separating for better alignment
- Not setting `alignVertical` when items have different heights

## Rich Text Icons

### a!richTextIcon Parameters
- `icon`: **MUST** be valid alias from `/ui-guidelines/reference/rich-text-icon-aliases.md` - DO NOT GUESS
- `color`: Icon color (STANDARD, ACCENT, POSITIVE, NEGATIVE, SECONDARY, or hex)
- `size`: Icon size (SMALL through EXTRA_LARGE)
- `altText`: Accessibility text

### Common Icon Patterns
```sail
/* Status indicators */
a!richTextIcon(icon: "check-circle", color: "POSITIVE")
a!richTextIcon(icon: "exclamation-triangle", color: "#F59E0B")
a!richTextIcon(icon: "times-circle", color: "NEGATIVE")

/* Navigation and actions */
a!richTextIcon(icon: "arrow-right", color: "ACCENT")
a!richTextIcon(icon: "external-link", color: "SECONDARY")
a!richTextIcon(icon: "download", color: "#6B7280")

/* Information and details */
a!richTextIcon(icon: "info-circle", color: "#3B82F6")
a!richTextIcon(icon: "question-circle", color: "SECONDARY")
a!richTextIcon(icon: "cog", color: "#6B7280")
```

## Rich Text Lists

### Bulleted Lists
```sail
a!richTextDisplayField(
  value: a!richTextBulletedList(
    items: {
      "First item",
      "Second item", 
      a!richTextItem(text: "Styled item", style: "STRONG")
    }
  )
)
```

### Numbered Lists
```sail
a!richTextDisplayField(
  value: a!richTextNumberedList(
    items: {
      "Step one",
      "Step two",
      "Step three"
    }
  )
)
```

## Color Usage Guidelines

### Semantic Colors
- **POSITIVE**: Success states, completed actions, positive metrics
- **NEGATIVE**: Errors, warnings, failed states, critical issues
- **ACCENT**: Primary theme color, important information, CTAs
- **SECONDARY**: Muted text, subtitles, less important information
- **STANDARD**: Default text color, body content

## Validation Checklist

### Icon Validation (CRITICAL):
- [ ] **IF using `a!richTextIcon()`:** Verify icon name in `/ui-guidelines/reference/rich-text-icon-aliases.md` FIRST
- [ ] DO NOT GUESS icon names (e.g., "chart-bar" ❌ → "bar-chart" ✅)

### Syntax Validation:
- [ ] Rich text value is array of richTextItems, richTextIcons, ricrichTextBulletedList, richTextNumberedList, or plain text. No other components!
- [ ] Line breaks use char(10) function

### Parameter Validation:
- [ ] Color values are valid enums or 6-character hex codes
- [ ] Size values are from approved list (SMALL through EXTRA_LARGE)
- [ ] Style values are from approved list (PLAIN, EMPHASIS, STRONG, etc.)
- [ ] Alignment values are LEFT, RIGHT, or CENTER

Remember: Rich text display fields can only contain the following items in their value property: `a!richTextItem`, `a!richTextIcon`, `a!richTextBulletedList`, `a!richTextNumberedList`, `a!richTextListItem`, `a!richTextImage`, `a!richTextHeader`, or plain text strings.

---

## Additional Rich Text Children

### a!richTextImage — Inline image inside rich text

Use to embed an icon-sized image (typically 16–24px) inline with text. The `image` parameter must be created with `a!documentImage`, `a!userImage`, or `a!webImage`.

**Function signature** (per Appian official docs):
```
a!richTextImage(image, showWhen)
```

**When to use:**
- Inline status indicators next to text (success/warning/error icons that are images, not iconSet icons)
- Brand logos or document thumbnails embedded in a paragraph
- Avatar-style user images inline with their name

**When NOT to use:**
- For Appian's built-in icon set (`CHECK_CIRCLE`, `USER`, etc.) → use `a!richTextIcon` instead (lighter)
- For standalone images outside rich text → use `a!imageField`

```sail
a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: {
    "Status: ",
    a!richTextImage(
      image: a!documentImage(
        document: a!iconIndicator(icon: "FACE_HAPPY")
      )
    ),
    " — All systems operational"
  }
)
```

### a!richTextListItem — Nested item inside a bulleted/numbered list

Use ONLY inside the `items` parameter of `a!richTextBulletedList` or `a!richTextNumberedList`. Allows you to put a sub-list inside a list item.

**Function signature** (per Appian official docs — note the parameter is `text`, NOT `value`):
```
a!richTextListItem(text, nestedList, showWhen)
```

**When to use:**
- Multi-level lists (a sub-list inside a list)
- A list item that contains both visible text *and* deeper sub-items
- A bulleted list nested inside a numbered list (or vice versa — they can mix)

**Rule of thumb:** for a plain top-level list, just put strings or `a!richTextItem`s in the `items` array — `a!richTextListItem` is overkill. Reach for it only when you need nesting.

```sail
a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: {
    a!richTextBulletedList(
      items: {
        "Top-level item A",
        a!richTextListItem(
          text: "Top-level item B (with sub-list)",
          nestedList: a!richTextBulletedList(
            items: { "B.1", "B.2", "B.3" }
          )
        ),
        "Top-level item C"
      }
    )
  }
)
```

### a!richTextHeader — Header inside rich text (DEPRECATED)

> ⚠️ **Deprecated by Appian.** This component still works but will be removed in a future Appian release. **Prefer `a!headingField`** for new code — it has more colour and size options, font-weight control, and proper heading-tag semantics for accessibility, and is used as a standalone component (not nested inside richText).

**Function signature** (per Appian official docs):
```
a!richTextHeader(text, size, link, linkStyle, showWhen)
```

If you must use it (legacy code, or to match an existing pattern), the rules are:
- `size`: only `"SMALL"`, `"MEDIUM"` (default), or `"LARGE"`
- Used ONLY inside `a!richTextDisplayField` `value`
- Header styles do **not** render inside a grid layout — if your richText sits inside a `a!gridLayout` column, use `a!richTextItem` with `style: "STRONG"` and a larger `size` instead

```sail
/* ✅ Preferred — a!headingField, standalone */
a!headingField(
  text: "Section title",
  size: "MEDIUM",
  color: "ACCENT"
)

/* ⚠️ Deprecated — a!richTextHeader inside richText */
a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: a!richTextHeader(text: "Section title", size: "MEDIUM")
)
```

