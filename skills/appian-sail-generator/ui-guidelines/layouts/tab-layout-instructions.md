# SAIL TabLayout Usage Instructions

## Overview
`a!tabLayout` is Appian's native tab component (introduced 26.1). It renders an underlined active-tab style.

⚠️ **Loading behavior — important correction**: by default the contents of **ALL** tabs evaluate on initial page load (not just the active one). To defer expensive tabs, set `loadBehavior: "ON_TAB_SELECT"` on the specific `a!tabItem` (26.6+) or use async loading — see the loadBehavior row below for the validation caveat.

✅ Use `a!tabLayout` for any standard tab UI — content panels, settings sections, master/detail filters
❌ Do NOT use `a!cardChoiceField` to mimic tabs (it's for choice selection, not tabbed navigation)
❌ Do NOT hand-roll tabs with `a!cardLayout` + `decorativeBarPosition` unless you genuinely need styling the native component does not offer (e.g. custom per-tab colors, vertical tabs, badge-style indicators)

```sail
/* GOOD - Settings page with three sections */
a!localVariables(
  local!selectedTab: 1,
  a!tabLayout(
    tabs: {
      a!tabItem(
        label: "General",
        icon: "cog",
        contents: {
          a!textField(label: "Display name", value: local!displayName, saveInto: local!displayName)
        }
      ),
      a!tabItem(
        label: "Notifications",
        icon: "bell",
        contents: {
          a!checkboxField(
            label: "Channels",
            choiceLabels: {"Email", "Slack", "SMS"},
            choiceValues: {"email", "slack", "sms"},
            value: local!channels,
            saveInto: local!channels
          )
        }
      ),
      a!tabItem(
        label: "Security",
        icon: "lock",
        contents: {
          a!toggleField(
            choiceLabel: "Require 2FA",
            value: local!require2FA,
            saveInto: local!require2FA
          )
        }
      )
    },
    highlightColor: "ACCENT"
  )
)
```

## a!tabLayout Parameters

| Parameter | Type | Description |
|---|---|---|
| `tabs` | Array of `a!tabItem` | Required. One entry per tab. Order is left-to-right. |
| `highlightColor` | Text | Color of the active-tab underline. Use `"ACCENT"` (default) or a hex code (also supports hex with transparency). |
| `contentsPadding` | Text | Padding around the active tab's content. `"NONE"`, `"EVEN_LESS"`, `"LESS"`, `"STANDARD"` (default), `"MORE"`, `"EVEN_MORE"`. |
| `marginAbove` | Text | Space above the tab bar. Standard margin enum. |
| `marginBelow` | Text | Space below the content. Standard margin enum. |
| `showWhen` | Boolean | Hides the entire tab layout when false. |
| `selectedTab` | Text o Integer | **(26.6+)** Sets/tracks the active tab by index (1-based) or by `a!tabItem` `id`. Bind a `local!`/`ri!`; pair with a URL-parameter rule input for shareable deep links to a tab. Null → first visible tab. |
| `selectedTabSaveInto` | Save array | **(26.6+)** Updated with the active tab's index or id when the user switches tabs. |

### Controlled-tab pattern (26.6+)

```sail
a!localVariables(
  local!activeTab: "general",   /* id-based, robust when tabs hide dynamically */
  a!tabLayout(
    tabs: {
      a!tabItem(id: "general",  label: "General",  contents: {...}),
      a!tabItem(id: "security", label: "Security", contents: {...})
    },
    selectedTab: local!activeTab,
    selectedTabSaveInto: local!activeTab
  )
)
```

## a!tabItem Parameters

| Parameter | Type | Description |
|---|---|---|
| `label` | Text | Required. The tab's text label. |
| `icon` | Text | Optional icon next to the label. Must be a valid alias from `rich-text-icon-aliases.md`. |
| `contents` | Array | Components shown when this tab is active. ⚠️ Evaluates on page load by default (see `loadBehavior`). |
| `showWhen` | Boolean | Hides the tab entirely when false. ⚠️ If tabs hide dynamically, you MUST give every tab an `id` — indexes shift and `selectedTab` would point at the wrong tab. |
| `validations` | Array | Validation messages tied to this tab — Appian shows a red badge on the tab when present. |
| `validationGroup` | Text | Validation grouping (same semantics as elsewhere in SAIL). |
| `id` | Text | **(26.6+)** Stable identifier for `selectedTab`. Unique across the layout; if any tab has one, ALL must have one. |
| `loadBehavior` | Text | **(26.6+)** `"ON_LOAD"` (default) or `"ON_TAB_SELECT"` (defers evaluation until the tab is opened; contents cached until a reevaluation). ⛔ Never use `"ON_TAB_SELECT"` on tabs containing fields with `required`/`validations` — those validations are skipped on submit until the user opens the tab. |

## Where you cannot use a!tabLayout

Per Appian's documentation, `a!tabLayout` cannot be nested inside:
- Another `a!sideBySideLayout`
- An editable grid layout
- A read-only grid

If you need tab-like UX inside one of those, fall back to the custom-styled patterns in `ui-guidelines/patterns/tabs.md`.

## Common Patterns

### Tab with validation badge
When a tab has unresolved validations, Appian renders a red dot on the tab itself. Use the `validations` parameter on the `a!tabItem`:

```sail
a!tabItem(
  label: "Billing",
  contents: { /* ... */ },
  validations: if(
    a!isNullOrEmpty(local!billingAddress),
    "Billing address is required",
    null
  )
)
```

### Tab with icon
```sail
a!tabItem(
  label: "Documents",
  icon: "file-text-o",       /* must exist in rich-text-icon-aliases.md */
  contents: { /* ... */ }
)
```

### Conditionally hiding a tab
Use `showWhen` on the `a!tabItem` to hide a tab based on data. The user can't click a hidden tab.

```sail
a!tabItem(
  label: "Admin Settings",
  showWhen: contains(loggedInUser().roles, "admin"),
  contents: { /* ... */ }
)
```

## Validation Checklist

Before finalizing a `a!tabLayout`:

- [ ] Every `a!tabItem.label` is a non-empty string
- [ ] Every `icon` used appears verbatim in `rich-text-icon-aliases.md`
- [ ] The `tabLayout` is NOT nested inside `a!sideBySideLayout`, editable grid, or read-only grid
- [ ] `contentsPadding` is one of: NONE / EVEN_LESS / LESS / STANDARD / MORE / EVEN_MORE
- [ ] `highlightColor` is either `ACCENT` or a hex code (`#RRGGBB` or `#RRGGBBAA` for transparency)
- [ ] Each tab's `contents` is wrapped in `{ ... }` (an array)

## Anti-Patterns

| ❌ Don't | ✅ Do |
|---|---|
| Use `a!cardChoiceField` for tabs | Use `a!tabLayout` |
| Hand-roll a tab bar with `cardLayout + decorativeBarPosition` for standard tabs | Use `a!tabLayout` |
| Put each tab's content in `local!` and switch with `a!match` | Let `a!tabItem.contents` handle it — only the active tab evaluates |
| Nest a `tabLayout` inside a `sideBySideLayout` | Restructure as a `columnsLayout` instead |
