---
name: run-appian-sail-generator
description: Validate and preview Appian SAIL output. Use when asked to validate, check, lint, render, open, or preview a .sail file produced by the appian-sail-generator skill, or after generating SAIL from natural-language requirements and wanting to see it in the browser.
---

Validates the syntax of a `.sail` file (balanced brackets, terminated
strings/comments, namespaced-identifier inventory) and renders a
dark-theme, syntax-highlighted HTML preview that opens in the default
browser.

Driver: `driver.mjs`, sitting next to this SKILL.md inside the `appian-toolkit` plugin.
Runtime: Node.js (already installed: v24+).

Because the plugin is installed at user scope, this works from **any** project
directory. The `.sail` paths you pass are resolved against your current working
directory, not against the plugin.

## Run

Define the driver path once per shell:

```bash
DRIVER=~/.claude/skills/appian-toolkit/skills/run-appian-sail-generator/driver.mjs
```

Then:

```bash
# Newest .sail in ./output/ — default path
node "$DRIVER"
```

```bash
# Specific file
node "$DRIVER" output/my-screen.sail
```

```bash
# Validate without opening the browser
node "$DRIVER" --no-open
```

```bash
# Custom HTML output location
node "$DRIVER" file.sail --out preview.html
```

Writes `<input>.preview.html` next to the source and opens it. Exit
code `0` if valid, `1` if validation errors were found (preview still
written so the failure is visible), `2` on bad invocation.
