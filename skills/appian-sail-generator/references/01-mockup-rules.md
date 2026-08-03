# Mockup Generation Rules (Phase 1) — Condensed Quick Reference

Phase 1 produces a **static SAIL mockup** that pastes cleanly into Appian Interface Designer for visual review. Phase 2 (a separate step) makes it functional.

For exhaustive guidance, the canonical sources inside this skill are:
- `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` (navigation index for dynamic-data patterns)
- `ui-guidelines/reference/schemas/*.json` (allowed parameters and values per component)
- `ui-guidelines/layouts/*.md` and `ui-guidelines/components/*.md` (templates, patterns, checklists)

This file is the floor — the rules that, when violated, almost always produce broken output.

---

## 1. Mockup boundaries — what's in, what's out

**Always in mockups:**
- `a!localVariables()` as the outermost wrapper.
- `local!` variables holding sample data via `a!map(...)` (lists of maps for entities).
- Static, hard-coded sample values (e.g. `"CASE-2024-5847"`, `date(2025, 1, 15)`, `"High"`).
- Simple property access (`fv!row.status`, not `fv!row['recordType!Case.fields.status']`).
- Control parameters initialised as locals: `local!isUpdate: false()`, `local!cancel: false()`.
- Custom search / filter UX (text fields, dropdowns) with `/* TODO-CONVERTER: ... */` comments so Phase 2 can convert them to native record-grid features.

**Never in mockups:**
- `ri!` rule inputs — they get introduced in Phase 2 conversion.
- `recordType!Foo`, `'recordType!{uuid}Foo.fields.{uuid}bar'` — Phase 2 only.
- `a!queryRecordType(...)`, `a!recordData(...)` — Phase 2 only.
- Grid record-only parameters: `showSearchBox`, `userFilters`, `recordActions` (they runtime-error with local data — use custom UX + `TODO-CONVERTER`).
- Runtime generators in sample data: `rand()`, `now()`, `today()` (the values change on every re-evaluation, making the mockup unstable — hard-code instead).
- `rule!` or `cons!` references unless the user named a specific one.
- Inline function definitions / lambdas: `local!helper: function(x)(...)` is **not valid SAIL syntax**. For repeated logic, duplicate it inline and leave a `/* TODO: Extract to expression rule */` comment when the pattern repeats 3+ times.

---

## 2. Layout selection

| Top-level layout | Use when | Read |
|---|---|---|
| `a!formLayout` | Single-step create/update form | `ui-guidelines/layouts/form-layout-instructions.md` |
| `a!wizardLayout` | Multi-step form with per-step validations | `ui-guidelines/layouts/wizard-layout-instructions.md` |
| `a!paneLayout` | Full-height (100vh) split view where panes scroll independently | `ui-guidelines/layouts/pane-layout-instructions.md` |
| `a!headerContentLayout` | Everything else — dashboards, list pages, detail pages | `ui-guidelines/layouts/header-content-layout-instructions.md` |

Inside the top-level layout:
- `a!columnsLayout` for major sections. **Every `a!columnsLayout` needs at least one `AUTO`-width column.**
- `a!sideBySideLayout` *only* for icon-plus-text or label-plus-value rows. **Never nest `a!sideBySideLayout` inside another, never put `a!columnsLayout`/`a!cardLayout`/arrays inside `a!sideBySideItem`.** Each `a!sideBySideItem` holds exactly one component.
- `a!cardLayout` for content blocks — but don't wrap `a!cardGroupLayout` or lists of cards in an outer card. Place card collections directly on the page background.

---

## 3. Components — quick rules

**Form inputs** (read `ui-guidelines/reference/schemas/input-components-schema.json`):
- Short list of options → `a!radioButtonField` or `a!checkboxField`; or `a!cardChoiceField` for a more visual feel.
- Longer list of options → `a!dropdownField`.
- Free-form rich text → `a!styledTextEditorField`.
- Email validation has no regex in SAIL — use the pattern from `logic-guidelines/functions-reference.md#email-validation-pattern`. Do not improvise.

**List display**:
- Default to `a!gridField` for tabular data.
- Use the custom tabular pattern (`ui-guidelines/components/tabular-data-display-pattern.md`) only when cells need multiple components.
- Use `a!cardGroupLayout` for a responsive grid of cards, one per list item — more visually engaging than a grid.

**Decorative**:
- `a!stampField` for initials / icons in a circle (see `ui-guidelines/components/stamp-field-instructions.md`).
- `a!tagField` for chip-style status labels.
- `a!richTextDisplayField` for styled text — **only `a!richTextItem` and `a!richTextIcon` are allowed inside**.

**Buttons**:
- `style` is one of `"OUTLINE"`, `"GHOST"`, `"LINK"`, `"SOLID"`. Not `"PRIMARY"`, not `"ACCENT"`.
- `color` is one of `"ACCENT"`, `"SECONDARY"`, `"NEGATIVE"`, or a hex code.
- Primary action = `style: "SOLID"` + `color: "ACCENT"`.
- A `a!buttonWidget` is always wrapped in `a!buttonArrayLayout`.

**Icons**:
- Every `icon: "..."` value must be a valid alias. Grep `ui-guidelines/reference/rich-text-icon-aliases.md` to verify before writing it. Inventing icon names is one of the most common failure modes.

---

## 4. Logic rules — the must-knows

These appear in nearly every non-trivial mockup. Pull the topic file when needed; this is the floor.

**Operators are functions, not keywords**:
- `or(a, b)` — not `a or b`.
- `and(a, b)` — not `a and b`.
- `not(a)` — not `!a`.

**Comments use `/* ... */`** — not `//`.

**Strings use double quotes**, escape with `""` not `\"`.

**Null safety** (full reference: `logic-guidelines/null-safety-quick-ref.md`):
- Comparison with a nullable: `if(a!isNotNullOrEmpty(var), comparison, false())`.
- Property access: `if(a!isNotNullOrEmpty(obj), obj.prop, default)`.
- Function parameter: `function(a!defaultValue(var, default))`.
- Grid selection: `index(local!selected, 1, null)`.
- Boolean `not()`: `not(a!defaultValue(var, false()))`.
- **Use `if()` for short-circuit, never `and()`**. `and(a!isNotNullOrEmpty(x), x.foo = "y")` *crashes* when `x` is null, because `and()` evaluates all arguments.

**Pattern matching** — 3+ branches on a single value:
- Use `a!match(value: X, equals: "A", then: ..., equals: "B", then: ..., default: ...)`.
- Use `whenTrue:` instead of `equals:` for ranges/thresholds.
- Don't write chained `if(or(equals(x,"A"), equals(x,"B")), ...)`.

**Empty arrays must be type-initialised**:
- `tointeger({})` for integers and IDs.
- `touniformstring({})` for text arrays — **not `tostring({})`**, which produces a single string instead of an empty list.
- `toboolean({})`, `todate({})`, `todatetime({})`, `todecimal({})`, `totime({})`, `touser({})`, `togroup({})`.

**Date arithmetic**:
- Cast results: `todate(today() + 1)`, not `today() + 1`.
- Compare interval to integer: `tointeger(now() - timestamp) < 1`.
- Date field uses `today()`; DateTime field uses `now()`.

**Function variables (`fv!`) are context-specific**:
- Inside grid columns (`columns:` of `a!gridLayout` / `a!gridField`): **only `fv!row`**. `fv!index`, `fv!item` do not exist in this context.
- Inside `a!forEach(...)`: `fv!item`, `fv!index`, `fv!isFirst`, `fv!isLast`.
- `fv!item` outside `a!forEach()` is invalid.

**`save!value`**:
- Valid **only** inside the `value` parameter of `a!save(target, value)`.
- Never in `if`/`and`/`or` conditions, never as the `target`, never outside `a!save()`.

**Local variables**:
- Maps (`a!map`) for entity data: `local!case: a!map(id: 1, title: "Foo", status: "Open")`.
- Separate variables for transient UI state: `local!searchText`, `local!selectedTab`, `local!isUpdate`.
- No unused variables. Either remove or mark `/* UNUSED — [reason] */`.

**Choice fields**:
- `choiceValues` must contain at least one non-null, non-empty value.
- For single-checkbox (`choiceValues: {true()}`), leave the local variable uninitialised (means "unchecked") — **don't initialise to `false()`**.
- Check with `a!isNotNullOrEmpty(local!agree)` in `showWhen`, not `contains()`.
- Multi-select uses one array variable, not a parallel list of booleans.

**Multi-instance forms** (collecting N copies of related data — work experiences, line items, addresses):
- Preferred: array-of-maps with `saveInto: fv!item.propertyName`. See `logic-guidelines/foreach-patterns.md`.
- Alternative: parallel arrays + `index()` + `a!update()` — only when iterating a fixed source list.

---

## 5. Comments — the four prefixes

Use comments to capture intent and signal work for downstream consumers (Phase 2 converter, data-model owner, process-model owner).

| Prefix | Use for | Example |
|---|---|---|
| `/* REQUIREMENT: ... */` | User-stated business rules | `/* REQUIREMENT: Only show cases assigned to the current user */` |
| `/* TODO-CONVERTER: ... */` | Work for Phase 2 converter | `/* TODO-CONVERTER: Set status to "Approved" */` `/* TODO-CONVERTER: Transform to ri!isUpdate */` |
| `/* TODO-DATA-MODEL: ... */` | Schema changes needed | `/* TODO-DATA-MODEL: Add 'approvalDate' field to Case record */` |
| `/* TODO: ... */` | Process-model / integration work outside SAIL | `/* TODO: Configure process model to send approval email */` |

Don't add comments for obvious things (sorting a grid, formatting a date, default UI behaviour). Only capture what's user-specified or non-obvious.

Documentation pattern reference: `logic-guidelines/documentation-patterns.md`.

---

## 6. Styling defaults

If the user doesn't specify, use:

- `#F5F6F8` — page background.
- `#1C2C44` — page header bar background (optional).
- `#FFFFFF` — content card background.
- `"ACCENT"` — themed primary colour (buttons, highlights).
- `"STANDARD"` — body text, headings, `sectionLayout` `labelColor`.

When omitting a label, set `labelPosition: "COLLAPSED"` so the label space doesn't reserve.

Don't use `"less"` or `"more"` for `spacing` — those values don't exist.

---

## 7. Output discipline

- Write to `output/<descriptive-name>.sail`.
- Create `output/` at the working-directory level if needed.
- After writing, **run validation** (see `references/04-validation-checklist.md`).
- Tell the user the file path and call out any `TODO`-style comments that block real-world use.

---

## 8. Design fidelity when the user provides a reference image

Structural correctness (no syntax errors, valid schemas) is necessary but not sufficient. When the user attaches a screenshot, mockup, or any visual reference, the generated SAIL must also match the **colour palette** and **visual primitives** of that reference — otherwise the output is "technically valid but looks nothing like the design".

This rule complements `SKILL.md` Step 0.6, which is the procedural checklist; this section is the substantive rule.

### 8.1 — Never use `"ACCENT"` for elements that must match the reference's brand colour

`"ACCENT"` resolves to whatever theme colour is configured at the **Appian site / portal level**. It is not guaranteed to match the reference image. When a reference is provided, extract the brand colour as a 6-digit HEX and use it explicitly in every parameter that visually carries the brand:

```sail
/* ❌ WRONG — when reference shows a purple brand and the env theme is orange */
a!buttonWidget(label: "Submit", style: "SOLID", color: "ACCENT")
a!tagItem(text: "5% off", backgroundColor: "ACCENT")
a!tabLayout(highlightColor: "ACCENT", tabs: { ... })

/* ✅ RIGHT — explicit HEX matches the reference regardless of env theme */
a!buttonWidget(label: "Submit", style: "SOLID", color: "#7C3AED")
a!tagItem(text: "5% off", backgroundColor: "#7C3AED")
a!tabLayout(highlightColor: "#7C3AED", tabs: { ... })
```

Parameters that should switch from `"ACCENT"` to HEX when matching a reference:
- `a!buttonWidget.color` (primary/CTA buttons, selected toggle pills)
- `a!tagItem.backgroundColor` (branded badges)
- `a!tabLayout.highlightColor` (active tab underline)
- `a!cardLayout.borderColor` / `a!cardLayout.decorativeBarColor`
- `a!stampField.backgroundColor` and `a!stampField.contentColor`
- `a!richTextItem.color` (branded inline text / links)
- `a!richTextIcon.color`
- `a!gaugeField.color` / `a!progressBarField.color`
- `a!sectionLayout.labelColor`

`"ACCENT"` remains the right default when **no reference image was provided** — in that case the mockup should adapt to whatever theme the environment uses.

### 8.2 — Annotate the extracted palette at the top of the file

Capture the palette as a top-of-file comment so future iterations and the Phase 2 converter know which colours are intentional brand decisions versus arbitrary choices:

```
/* PALETTE — extracted from reference image
 *   brand:        #7C3AED   purple — used in CTA, active tab, selected pill, branded tag
 *   brand-soft:   #EDE9FE   lavender tint — chip backgrounds, hover states
 *   page-bg:      #F5F6F8   page / left-pane background
 *   text-muted:   #6B7280   secondary text, descriptions, column headers
 *   text-primary: #111827   titles, totals, primary numbers
 */
```

### 8.3 — Map non-standard visual primitives to their closest native SAIL equivalent

The reference often shows shapes or compositions that don't map 1-to-1 onto a single SAIL component. Pick the closest native equivalent **before writing**, not by trial and error.

| Reference visual | Closest native SAIL | Note |
|---|---|---|
| Primary CTA button (any corner radius) | `a!buttonWidget(style: "SOLID", color: "#HEX", width: "FILL")` inside `a!buttonArrayLayout` | Button **corner radius (sharp / rounded / pill) is configured at the Appian site / portal level**, not in SAIL. Don't try to fake a different corner radius via stamp/richText workarounds — trust the site config. |
| Circular icon stamp (non-clickable, e.g. category indicator) | `a!stampField(icon: "...", backgroundColor: "#HEX", contentColor: "#FFFFFF", shape: "ROUNDED", size: "SMALL")` | Use stamps for circular icon chips. |
| Circular icon stamp (clickable) | `a!stampField(..., link: a!dynamicLink(...))` | Stamps support `link:` natively. |
| Pure circular interactive icon (no background, just colour) | `a!richTextDisplayField(value: a!richTextIcon(icon: "...", color: "#HEX", link: a!dynamicLink(...)))` | `a!richTextIcon` supports `link:` directly. |
| Pill-shaped tag with brand fill | `a!tagItem(text: "...", backgroundColor: "#HEX")` inside `a!tagField` | Tags render as pills by default. |
| Selected / unselected toggle group | `a!buttonWidget` with `style: if(local!sel = "X", "SOLID", "LINK")` + `color: if(...)` returning HEX or `"SECONDARY"` | Inline ternary on `style:` and `color:`. |
| Edge-to-edge photo at the top of a card with padded text below | Outer `a!cardLayout(padding: "NONE")` → `a!imageField(size: "GALLERY", marginBelow: "NONE")` → inner `a!cardLayout(style: "TRANSPARENT", padding: "STANDARD")` for text | Card-in-card is the only way to mix "no padding around image" with "padding around text". |
| Small circular avatar thumbnail (e.g. order line item) | `a!imageField(images: a!webImage(source: "..."), size: "EXTRA_SMALL", style: "AVATAR")` | `style: "AVATAR"` is the documented way to get circular images. |

If a reference visual genuinely has no acceptable native equivalent, document it as `/* TODO-DESIGN: ... */` and pick the closest match — don't invent a hack.

### 8.4 — Be honest about photographs

A mockup cannot match real product photographs without `a!documentImage(document: cons!FOTO_X)` referencing Appian documents that don't exist yet. Two acceptable options:

- **Stable real URLs** (specific Unsplash photo IDs, brand asset CDN URLs) via `a!webImage(source: "https://...")` — use when you have them and they won't drift.
- **Obvious placeholders** like `https://placehold.co/600x400/D1FAE5/065F46?text=Edamame` — colour-coded boxes that clearly read as placeholders so the user knows to swap them.

Avoid the middle ground: text-on-coloured-box images that "almost look like real photos" mislead the user into thinking the mockup will look like the reference once pasted. **Always tell the user in the response summary** that images are the one element of the reference a SAIL mockup cannot match without real Appian documents.

### 8.5 — Self-check before declaring the mockup done

When a reference image was provided, the final-output gate (`SKILL.md` Step 4.5) has these additional questions:

- [ ] Did I extract a brand HEX from the reference and use it (not `"ACCENT"`) on every brand-coloured parameter?
- [ ] Is the palette annotated as a top-of-file comment?
- [ ] For every non-standard visual primitive in the reference (circular icon, edge-to-edge image, pill toggle), did I pick the documented native equivalent from § 8.3?
- [ ] Did I tell the user explicitly that photographs are the one thing the mockup can't match without real documents?

If any answer is "no", fix before sending — the mockup will look wrong even if it parses.
