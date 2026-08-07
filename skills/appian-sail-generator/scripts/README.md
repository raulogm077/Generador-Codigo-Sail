# Scripts

This folder ships four utilities:

- **`install_validators_to_user.py`** ⭐ NEW in v2.2 — installs the skill's validator subagents into `~/.claude/agents/` so Claude Code can invoke them via the `Agent` tool. **Run once per Claude Code installation** (the skill's Step 0.4 invokes it automatically when needed).
- **`sync-agents.py`** — keeps the skill's own `/agents/` and `/.claude/agents/` in lockstep (skill maintenance, for editors of the skill).
- **`xml_to_appian_recordtype_md.py`** — converts a single `recordTypeHaul` XML to data-model-context markdown (Phase 2 prep).
- **`map_xml_to_appian_recordtype_md.py`** — same conversion at scale (folder of XMLs or zipped application export).

---

## `install_validators_to_user.py` — register validator subagents with Claude Code

Claude Code discovers sub-agents from the user's `~/.claude/agents/` directory, NOT from inside a plugin's bundle. When this skill is installed via the plugin system, its `agents/*.md` files are not addressable as `subagent_type: sail-schema-validator` until they're copied to the user-level registry.

This script does that copy. It's idempotent, cross-platform (Windows / macOS / Linux), and only touches files prefixed with `sail-` so the user's other custom agents are preserved.

```bash
# Install / update (default action)
python scripts/install_validators_to_user.py

# Just check status, don't modify anything
python scripts/install_validators_to_user.py --check --verbose

# Uninstall (removes only sail-* files; leaves the user's other agents alone)
python scripts/install_validators_to_user.py --remove
```

**After install, the user MUST restart Claude Code** (or run `/restart`) for the new sub-agents to appear in the runtime's subagent registry.

**The skill's `SKILL.md` Step 0.4 invokes this script automatically on first SAIL generation in a fresh environment.** If you're hand-editing or testing the skill, run it once manually.

Exit codes:
- `0` — installed/up-to-date (or status OK in `--check` mode)
- `1` — drift detected (only in `--check` mode)
- `2` — source agents folder missing
- `3` — permission denied writing to `~/.claude/agents/`

---

## `sync-agents.py` — keep duplicated agent files in sync (skill maintenance)

The skill keeps two copies of every agent instruction file:
- `/agents/*.md` — the canonical location (read inline by Claude.ai).
- `/.claude/agents/*.md` — discovery location inside the skill bundle (NOT the same as the user-level `~/.claude/agents/`, which is what `install_validators_to_user.py` populates).

**Edit only `/agents/`, then run this script to propagate.**

```bash
# Sync (writes if changed)
python scripts/sync-agents.py

# CI / pre-commit check (exits non-zero if out of sync; does not modify)
python scripts/sync-agents.py --check
```

The script is cross-platform (no symlinks; works on Windows). Exit codes:
- `0` — in sync (or sync applied successfully)
- `1` — out of sync (only in `--check` mode)
- `2` — missing source directory

---

## XML → data-model-context.md conversion scripts

Two Python scripts from [`raulogm077/data-model-context`](https://github.com/raulogm077/data-model-context)
that convert Appian `recordTypeHaul` XML exports into the markdown context that
Phase 2 (functional conversion) needs.

## When to use

Use these scripts **before** running Phase 2 conversion, to produce the
`context/data-model-context.md` file that the `sail-dynamic-converter` agent
reads. Skip them if you already have a hand-crafted `context/data-model-context.md`.

## `xml_to_appian_recordtype_md.py` — single XML → single MD

```bash
python xml_to_appian_recordtype_md.py path/to/record.xml [-o OUTPUT.md] [--title "Custom Title"]
```

Options:
- `-o`, `--out` — output path (defaults to `<input>.md`).
- `--title` — H1 title override (defaults to `<RecordName> Record Type Context Reference`).

Example:
```bash
python xml_to_appian_recordtype_md.py recordtype-xml/Case.xml -o ../context/data-model-context.md
```

## `map_xml_to_appian_recordtype_md.py` — many XMLs or a zip → many MDs

Accepts a directory of XMLs or a zipped Appian application export.

```bash
# Directory
python map_xml_to_appian_recordtype_md.py recordtype-xml/

# Zipped Appian application export
python map_xml_to_appian_recordtype_md.py application-export.zip
```

Options:
- `-o`, `--output_dir` — output directory (defaults to the input directory for
  folder input, or the current directory for zip input).
- `-f`, `--folder` — when input is a zip, the folder path inside the zip to
  scan for record-type XMLs.

Output filenames follow the pattern `data-model-context-<record_name_snake_case>.md`,
one file per record type.

## Folder convention

- `recordtype-xml/` — drop the raw XMLs here (this folder is a convention from
  the original repo; the scripts accept any path).
- The output goes wherever `-o` or `--output_dir` points; for the skill workflow,
  the canonical destination is `../context/data-model-context.md` (one combined
  file) or `../context/` (one file per record type).

## Combining multiple per-record markdowns into one context file

If `map_*` produced multiple files and your interface uses several record types,
combine them under a single `<available_record_types>` wrapper. See
`references/03-data-model-context-format.md` § "Concatenating multiple record
types into one context file" for the shell snippet.

## Data type and relationship normalisation

The scripts normalise Appian types to a small canonical set:
- `Int`, `Integer`, `Long` → `Integer`
- `Text`, `Boolean`, `Date`, `Datetime`, `User`, `Document` → unchanged
- `Guid` → `Text`
- `CollaborationDocument` → unchanged

Relationship types become lowercase hyphenated forms:
- `ONE_TO_MANY` → `one-to-many`
- `MANY_TO_ONE` → `many-to-one`
- `ONE_TO_ONE` → `one-to-one`
- `MANY_TO_MANY` → `many-to-many`

## Origin

These scripts come from <https://github.com/raulogm077/data-model-context>,
based on the original by [Jordan Loftis](https://github.com/tokyojordan)
(`tokyojordan/data-model-context`).
