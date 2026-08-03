# Data Model Context — PLACEHOLDER

This file is a placeholder. The real data-model context of each project does NOT
live inside the plugin: it is created in the project's working directory
(`<project>/context/data-model-context.md`) during Phase 2 setup, or at the path
configured via `data_model_context` in `.claude/appian-toolkit.local.md`.

- Expected format: `references/03-data-model-context-format.md`
- Complete worked example (OTIEC training application): `examples/data-model-context-example.md`
- Auto-generation from `recordTypeHaul` exports:

```bash
# Single XML
python scripts/xml_to_appian_recordtype_md.py path/to/record.xml -o context/data-model-context.md

# Directory of XMLs or a zipped Appian application export
python scripts/map_xml_to_appian_recordtype_md.py path/to/recordtype-xml-folder/
```

⛔ Rule: if this file is still a placeholder and the request is functional/dynamic,
STOP and ask the user for the data model (Hard STOP #1 in SKILL.md). Never invent UUIDs.
