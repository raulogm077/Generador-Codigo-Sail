# Examples

Reference files showing "what good looks like" — Claude can read these to anchor structure and idioms before generating fresh output, and you can paste any of the `.sail` files into Appian Interface Designer to see them render.

## Files

| File | What it shows |
|---|---|
| `data-model-context-example.md` | A real `data-model-context.md` (from the OTIEC application) showing the canonical record-type / field / relationship / action / filter format that Phase 2 needs. Use as a template when handcrafting one, or as a reference for what the `xml_to_appian_recordtype_md.py` script produces. |
| `mockup-form-example.sail` | A complete Phase-1 mockup of a single-step create form (`a!formLayout`). Demonstrates: control-parameter initialisation, validations parameter (no manual flags), `a!section`/`a!columnsLayout` composition, dropdown + checkbox + dateField patterns, button field-setting via `TODO-CONVERTER` comments, null-safe defaults with `a!defaultValue`. |
| `mockup-dashboard-example.sail` | A complete Phase-1 mockup of a list page (`a!headerContentLayout`). Demonstrates: KPI strip using `a!cardLayout` styles, custom search/filter UX with `TODO-CONVERTER` comments, grid with sort-field discipline (sort on primary fields only, none on computed columns), tag colour via `a!match()` pattern matching, type-initialised empty arrays for selection, side-by-side header. |

## Why two `.sail` files

The two examples cover the two top-level layout families you'll meet most often:

- **Form-style** (`a!formLayout` / `a!wizardLayout`) — create/update interfaces with `contents:` and `buttons:`.
- **Page-style** (`a!headerContentLayout` / `a!paneLayout`) — read pages with header, content sections, and complex internal layout.

Between them they exercise around 80% of the components and patterns a typical interface needs.

## Pasting them into Appian

Both `.sail` files are mockups — they use `local!` variables and hard-coded sample data. To verify them in Appian Interface Designer:

1. Open the file in this directory.
2. Copy the entire expression.
3. Paste into a new Appian Interface Definition.
4. The interface should render immediately with the sample data visible.

If Appian flags an error after a future edit, the protocol is:

1. Copy the exact error text.
2. Paste it into Claude (with this skill active) saying "paste the Appian designer error and I'll fix it" — or simply share the error.
3. Claude scans `references/06-common-syntax-errors.md`, locates the matching pattern, and fixes the file in place.

## What these examples are NOT

- Not Phase-2 (functional) output. They contain no `ri!` or `recordType!` references. Phase-2 examples would require a real, environment-specific `data-model-context.md` and would not be reusable as references.
- Not exhaustive. They cover the common shapes; for less-common components (charts, wizards, multi-instance forms, panes), consult the relevant `ui-guidelines/` instruction files.
