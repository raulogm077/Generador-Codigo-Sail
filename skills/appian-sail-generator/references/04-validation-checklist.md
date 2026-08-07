# Universal Validation Checklist

Run through this before declaring **any** generated SAIL output done — whether it's a fresh mockup, a converted functional interface, or an edit. Output that fails any of these items goes back for fixing, not to the user.

This is a high-signal floor. Skill ships with deeper, agent-driven validation in `agents/sail-schema-validator.md`, `agents/sail-icon-validator.md`, and `agents/sail-code-reviewer.md`. Use those for thorough checks; use this list for the fast must-pass items.

---

## Quick path (when `appian-mcp-server` MCP is available)

If `mcp__appian-mcp-server__validate_sail` is in your tool list (typically when the user is on the Appian VPN), just call it on the output file. The MCP server uses the same validator Appian uses internally — fastest and most accurate option.

**Don't skip the rest of this checklist** for items the MCP doesn't catch (icon validity, requirement comments, completeness of conversion, business-logic alignment with the user's request).

---

## No-MCP paths — pick based on environment

### Path A — Claude Code with `Agent` tool (subagent delegation available)

Run the three validator agents in order via `Agent` calls, stopping at first failure:

1. **`sail-schema-validator`** — verifies every function exists, every parameter exists for that function, and every enumerated value is in the function's `validValues` list. Schemas live at `ui-guidelines/reference/schemas/*.json`. The agent is exhaustive (every single value checked, no sampling) — see `agents/sail-schema-validator.md`.

2. **`sail-icon-validator`** — verifies every `icon: "..."` value exists in `ui-guidelines/reference/rich-text-icon-aliases.md`. Inventing icon names is among the most common runtime errors. See `agents/sail-icon-validator.md`.

3. **`sail-code-reviewer`** — verifies structural and stylistic rules: nesting, null safety, `fv!` context, type handling, layout hierarchy. See `agents/sail-code-reviewer.md`.

### Path B — Claude.ai (or any env without `Agent` tool) — INLINE three-pass scan

**This is the default for Claude.ai. Do not pretend to delegate to subagents — that's a hallucinated tool call.** Read each agent file and apply its instructions yourself. Full inline protocol: `references/07-claude-ai-inline-validation.md`.

In summary, the three passes are:

1. **Schema pass** (yourself) — apply `agents/sail-schema-validator.md` instructions inline: open `ui-guidelines/reference/schemas/*.json`, scan the generated `.sail` file, verify every function name, every parameter, and every enum value.

2. **Icon pass** (yourself) — apply `agents/sail-icon-validator.md` instructions inline: grep the file for every `icon:` occurrence; verify each value against `ui-guidelines/reference/rich-text-icon-aliases.md`.

3. **Structural pass** (yourself) — apply `agents/sail-code-reviewer.md` instructions inline: walk this file's Manual scan checklist plus `references/06-common-syntax-errors.md`'s 14 categories.

Stop and fix at first failure in each pass before moving to the next.

---

## Manual scan checklist (always)

Regardless of validation path, do a quick eyeball pass for these:

### Expression structure
- [ ] Starts with `a!localVariables()`.
- [ ] Exactly one top-level layout (`a!headerContentLayout` / `a!formLayout` / `a!paneLayout` / `a!wizardLayout`) — not wrapped in `{}` when it's the sole argument.
- [ ] All braces `{}`, parens `()`, and quotes `"` matched.
- [ ] Comments use `/* ... */`, not `//`.
- [ ] Strings escape double-quotes as `""`, not `\"`.

### Syntax floor
- [ ] Operators use function form: `or(a, b)`, `and(a, b)`, `not(a)` — never `a or b`, `a and b`, `!a`.
- [ ] Pattern matching with 3+ branches on a single value uses `a!match()`, not nested `if()`.
- [ ] Empty arrays type-initialised: `tointeger({})`, `touniformstring({})`, etc. Untyped `{}` with `contains()`/`wherecontains()` is a bug.
- [ ] Date arithmetic cast: `todate(today() + 7)`, not `today() + 7`.
- [ ] No inline function defs / lambdas (`local!helper: function(x)(...)` is invalid).

### Null safety
- [ ] Comparisons with nullable values wrapped in `if(a!isNotNullOrEmpty(x), ..., default)`.
- [ ] **Never** rely on `and(a!isNotNullOrEmpty(x), x.prop = ...)` — `and()` does not short-circuit.
- [ ] Property access on nullable: `if(a!isNotNullOrEmpty(obj), obj.prop, default)`.
- [ ] Function parameters use `a!defaultValue(var, default)` for nullable inputs.
- [ ] Grid selection access: `index(local!selected, 1, null)`.

### Function variables (`fv!`)
- [ ] Inside grid `columns:`: only `fv!row`. No `fv!index`, no `fv!item`.
- [ ] Inside `a!forEach()`: `fv!item`, `fv!index`, `fv!isFirst`, `fv!isLast`. No `fv!row`.
- [ ] `save!value` only inside the `value` parameter of `a!save(target, value)`. Not in `if`/`and`/`or`, not as `target`, not outside `a!save()`.

### Layout rules
- [ ] Every `a!columnsLayout` has at least one `AUTO`-width column.
- [ ] No nested `a!sideBySideLayout`.
- [ ] No `a!columnsLayout`, `a!cardLayout`, or array of components inside any `a!sideBySideItem`.
- [ ] Inside `a!richTextDisplayField`: only `a!richTextItem` / `a!richTextIcon` / `a!richTextBulletedList` / `a!richTextNumberedList` / `a!richTextImage` / `a!richTextListItem` / `a!richTextHeader`. (`a!richTextHeader` is deprecated by Appian — prefer `a!headingField` for new code, used as a standalone component, not nested in richText.)
- [ ] No `spacing: "less"` or `spacing: "more"` (invalid values).
- [ ] Buttons are inside `a!buttonArrayLayout`, never bare.

### Mockup-only (Phase 1 output)
- [ ] No `ri!` references.
- [ ] No `recordType!` references.
- [ ] No `a!queryRecordType` / `a!recordData`.
- [ ] No runtime generators in sample data (`rand()`, `now()`, `today()` — except in `todate(today() + N)` casts inside data, which is fine if values are stable).
- [ ] Grid record-only parameters (`showSearchBox`, `userFilters`, `recordActions`) are *not* set — instead, custom search/filter UX is in place with `TODO-CONVERTER` comments.
- [ ] Control parameters initialised as `local!isUpdate: false()`, `local!cancel: false()`.

### Functional-only (Phase 2 output)
- [ ] Every `'recordType!{uuid}Foo'` and `.fields.{uuid}bar` matches an entry in `context/data-model-context.md`. UUIDs not invented.
- [ ] No leftover `local!` arrays that should be queries.
- [ ] No `TODO-CONVERTER` comments left unresolved.
- [ ] `ri!` rule inputs documented in a header comment block (name, type, purpose).
- [ ] For start forms with a `model.json`: `ri!` variable names match `model.json` `process_variables[].variable_name` *exactly*. Count of `ri!` declarations equals count of `process_variables`.
- [ ] Grid `sortField` matches the primary field in `value:`, unique per grid. Computed columns have no `sortField`.

### Parameter values
- [ ] Button `style` is one of `"OUTLINE"`, `"GHOST"`, `"LINK"`, `"SOLID"`. Not `"PRIMARY"`/`"ACCENT"`.
- [ ] Button `color` is `"ACCENT"`, `"SECONDARY"`, `"NEGATIVE"`, or a hex code.
- [ ] `richTextItem` `align` is `"LEFT"`, `"CENTER"`, or `"RIGHT"`. Not `"START"`/`"END"`.
- [ ] Hex colours are 6-char `#RRGGBB`. No HTML names (`"RED"`).
- [ ] `choiceValues` contains at least one non-null, non-empty value.

### Choice fields
- [ ] Multi-select uses one array variable, not parallel booleans.
- [ ] Single checkbox (`choiceValues: {true()}`) is uninitialised, not `false()`.
- [ ] Single checkbox `showWhen` uses `a!isNotNullOrEmpty(local!agree)`, not `contains()`.

### Variables
- [ ] No unused local variables (declared but never referenced). Either remove or mark `/* UNUSED — [reason] */`.

### Comments and requirements
- [ ] Every user-stated business rule is captured as `/* REQUIREMENT: ... */`.
- [ ] No invented business rules dressed up as `REQUIREMENT` comments — only what the user said.
- [ ] `TODO-CONVERTER` / `TODO-DATA-MODEL` / `TODO` comments are accurate and actionable.
- [ ] Mockup → output communication: any blocker (missing field, missing record type, ambiguous rule) is captured as a `TODO-DATA-MODEL` or surfaced to the user in the response.

---

## Completeness self-check (the senior-engineer test)

Before sending output to the user, ask: *"Would a senior Appian engineer approve this on review?"*

- Is every user-stated requirement reflected in the code or in a clearly-flagged TODO?
- Does it run? (When in doubt, validate with MCP or run the three agents.)
- Are the comments honest — no over-promised functionality, no glossed-over gaps?
- Are field types matched to component types (Text field → `a!textField`/`a!dropdownField`, Date field → `a!dateField`, etc.)?
- Is the file path correct (`output/<name>.sail` or `output/<name>-functional.sail`)?

If any answer is "not sure" or "no", fix before presenting.
