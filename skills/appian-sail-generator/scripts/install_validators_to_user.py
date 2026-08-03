#!/usr/bin/env python3
"""
install_validators_to_user.py
─────────────────────────────────────────────────────────────────────────────
Install the skill's 6 validator/converter agents into the user's Claude Code
agent registry (`~/.claude/agents/`) so they become invocable via the Task
tool's `subagent_type` parameter.

WHY THIS EXISTS
───────────────
Claude Code discovers sub-agents from `~/.claude/agents/`, not from the
bundled skill folder. When a skill is installed via the plugin system, its
`agents/` folder is hidden inside the plugin sandbox — the validators are
NOT addressable as `subagent_type: sail-schema-validator` until they're
copied to the user's home agent registry.

Without this step, the SKILL.md Step 4 (validation) silently falls back
to Mode C (inline validation), which has been observed to miss issues
that the formal subagents catch (e.g., invalid icon aliases not in the
catalog).

WHAT IT DOES
────────────
- Locates the skill's `/agents/` folder (relative to this script).
- Creates `~/.claude/agents/` if it doesn't exist.
- Copies each `sail-*.md` validator there.
- Preserves any non-skill agents the user already has installed.
- Reports each file as installed/updated/already-current.

IDEMPOTENT
──────────
Safe to run multiple times. Won't overwrite files that haven't changed.

USAGE
─────
    python scripts/install_validators_to_user.py             # install/update
    python scripts/install_validators_to_user.py --check     # report status only
    python scripts/install_validators_to_user.py --verbose   # detailed logs
    python scripts/install_validators_to_user.py --remove    # uninstall sail-* agents

EXIT CODES
──────────
    0  success (or already installed with --check)
    1  files missing/out-of-date (only in --check mode)
    2  source agents folder not found
    3  permission denied writing to ~/.claude/agents/
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

# Force UTF-8 stdout/stderr so emoji and box-drawing characters render correctly
# on Windows consoles (default cp1252) without crashing the script.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Names of the agents this skill bundles (filter to avoid copying unrelated files).
SKILL_AGENT_PREFIXES = ("sail-",)


def _skill_root() -> Path:
    """Returns the skill root (assumes this script lives in <skill>/scripts/)."""
    return Path(__file__).resolve().parent.parent


def _user_agents_dir() -> Path:
    """Returns ~/.claude/agents/ resolved for the current OS."""
    return Path.home() / ".claude" / "agents"


def _list_skill_agents(src_dir: Path) -> list[Path]:
    """Returns the validator/converter .md files this skill ships."""
    return sorted(
        p for p in src_dir.iterdir()
        if p.is_file() and p.suffix == ".md"
        and any(p.name.startswith(prefix) for prefix in SKILL_AGENT_PREFIXES)
    )


def check(verbose: bool = False) -> int:
    """Reports installation status without modifying anything."""
    src = _skill_root() / "agents"
    dst = _user_agents_dir()

    if not src.is_dir():
        print(f"ERROR: source agents folder not found: {src}", file=sys.stderr)
        return 2

    agents = _list_skill_agents(src)
    if not agents:
        print(f"WARNING: no sail-* agents found in {src}", file=sys.stderr)
        return 2

    if not dst.exists():
        print(f"NOT INSTALLED — {dst} does not exist.")
        print(f"  Run: python scripts/install_validators_to_user.py")
        return 1

    missing, outdated, ok = [], [], []
    for agent in agents:
        target = dst / agent.name
        if not target.exists():
            missing.append(agent.name)
        elif not filecmp.cmp(agent, target, shallow=False):
            outdated.append(agent.name)
        else:
            ok.append(agent.name)

    if verbose or missing or outdated:
        print(f"Skill agents:       {len(agents)}")
        print(f"  ✅ up to date:     {len(ok)}")
        print(f"  ⚠️  out of date:    {len(outdated)} {outdated if outdated else ''}")
        print(f"  ❌ not installed:  {len(missing)} {missing if missing else ''}")
        print(f"User agents dir:    {dst}")

    if missing or outdated:
        print()
        print("Some validators are missing or out-of-date.")
        print("Run: python scripts/install_validators_to_user.py")
        return 1

    print(f"OK — all {len(agents)} validators installed at {dst}")
    return 0


def install(verbose: bool = False) -> int:
    """Copies the skill's validator agents to ~/.claude/agents/."""
    src = _skill_root() / "agents"
    dst = _user_agents_dir()

    if not src.is_dir():
        print(f"ERROR: source agents folder not found: {src}", file=sys.stderr)
        return 2

    agents = _list_skill_agents(src)
    if not agents:
        print(f"WARNING: no sail-* agents found in {src}", file=sys.stderr)
        return 2

    try:
        dst.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"ERROR: cannot create {dst} (permission denied)", file=sys.stderr)
        return 3

    installed, updated, unchanged = [], [], []
    for agent in agents:
        target = dst / agent.name
        if not target.exists():
            shutil.copy2(agent, target)
            installed.append(agent.name)
            if verbose:
                print(f"  installed: {agent.name}")
        elif not filecmp.cmp(agent, target, shallow=False):
            shutil.copy2(agent, target)
            updated.append(agent.name)
            if verbose:
                print(f"  updated:   {agent.name}")
        else:
            unchanged.append(agent.name)
            if verbose:
                print(f"  unchanged: {agent.name}")

    print()
    print(f"Installation complete at {dst}")
    print(f"  ✅ installed:  {len(installed)} {installed if installed else ''}")
    print(f"  🔄 updated:    {len(updated)} {updated if updated else ''}")
    print(f"  ➖ unchanged:  {len(unchanged)}")
    print()
    print("Next step: restart Claude Code (or run /restart) so it picks up the new sub-agents.")
    print("After restart, the validators will be invocable as:")
    for agent in agents:
        name = agent.stem
        print(f"    Task(subagent_type=\"{name}\", ...)")
    return 0


def remove(verbose: bool = False) -> int:
    """Removes the skill's validator agents from ~/.claude/agents/."""
    src = _skill_root() / "agents"
    dst = _user_agents_dir()

    agents = _list_skill_agents(src)
    if not agents:
        print(f"WARNING: no sail-* agents found in {src} (nothing to remove).")
        return 0

    if not dst.is_dir():
        print(f"Nothing to remove — {dst} does not exist.")
        return 0

    removed = []
    for agent in agents:
        target = dst / agent.name
        if target.exists():
            target.unlink()
            removed.append(agent.name)
            if verbose:
                print(f"  removed: {agent.name}")

    print(f"Removed {len(removed)} skill agents from {dst}")
    if removed:
        print("Note: this only removes sail-* agents. Other agents in that folder are preserved.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="Report status only; do not modify (exit 1 if drift detected)")
    parser.add_argument("--remove", action="store_true",
                        help="Uninstall the skill's sail-* agents from ~/.claude/agents/")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Detailed per-file logging")
    args = parser.parse_args()

    if args.check and args.remove:
        print("ERROR: --check and --remove are mutually exclusive.", file=sys.stderr)
        return 2

    if args.check:
        return check(verbose=args.verbose)
    if args.remove:
        return remove(verbose=args.verbose)
    return install(verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
