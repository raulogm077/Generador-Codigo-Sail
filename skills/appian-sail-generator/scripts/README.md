# Scripts

This folder ships two utilities:

- **`xml_to_appian_recordtype_md.py`** — converts a single `recordTypeHaul` XML to data-model-context markdown (Phase 2 prep).
- **`map_xml_to_appian_recordtype_md.py`** — same conversion at scale (folder of XMLs or zipped application export).

---

## Where the subagents live (no install step)

The six validator/converter subagents are **not** in this folder and need no installation.
They ship at the plugin root, in [`agents/`](../../../agents/), and Claude Code discovers
plugin agents automatically — they are addressable as `subagent_type: sail-schema-validator`
and friends as soon as the plugin loads. Verify with:

```bash
claude plugin details appian-toolkit    # should list 7 agents
```

Two scripts used to exist here for this and were removed in v2.6.0:

- `install_validators_to_user.py` copied the agents into `~/.claude/agents/`. That was
  needed when this was a standalone skill; as a plugin it is not, and running it now
  creates a second, shadowing copy of every `sail-*` agent that drifts from the plugin's.
- `sync-agents.py` mirrored `agents/` into a bundled `.claude/agents/` copy. Claude Code
  never discovered that copy, its source directory no longer existed (the script failed
  outright), and the two sets had already diverged.

If a subagent is missing from your `subagent_type` list, the fix is `/reload-plugins`
or restarting Claude Code — see `SKILL.md` Step 0.4. Never copy agent files by hand.

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
