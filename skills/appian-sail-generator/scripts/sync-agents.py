#!/usr/bin/env python3
"""
Sync canonical agent instruction files from /agents/ to /.claude/agents/.

Why two directories?
- `/agents/` is the canonical location read inline by Claude.ai (instruction sheets).
- `/.claude/agents/` is where Claude Code discovers sub-agents for delegation via the Task tool.

Both must hold identical content. Edit ONLY `/agents/`, then run this script
to propagate. This script is the source of truth for keeping them in sync.

Usage (run from skill root):
    python scripts/sync-agents.py             # sync (writes if changed)
    python scripts/sync-agents.py --check     # CI mode: exit non-zero if out of sync
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path


def sync(skill_root: Path, check_only: bool) -> int:
    src = skill_root / "agents"
    dst = skill_root / ".claude" / "agents"

    if not src.is_dir():
        print(f"ERROR: source directory not found: {src}", file=sys.stderr)
        return 2

    dst.mkdir(parents=True, exist_ok=True)

    src_files = {p.name for p in src.iterdir() if p.is_file()}
    dst_files = {p.name for p in dst.iterdir() if p.is_file()}

    out_of_sync = []
    only_in_src = src_files - dst_files
    only_in_dst = dst_files - src_files
    common = src_files & dst_files

    for name in sorted(common):
        if not filecmp.cmp(src / name, dst / name, shallow=False):
            out_of_sync.append(name)

    drift = sorted(out_of_sync) + [f"+{n}" for n in sorted(only_in_src)] + [f"-{n}" for n in sorted(only_in_dst)]

    if check_only:
        if drift:
            print("OUT OF SYNC. Run `python scripts/sync-agents.py` to fix:")
            for item in drift:
                print(f"  {item}")
            return 1
        print(f"OK: {len(common)} agent files in sync.")
        return 0

    # Sync mode: copy src -> dst for any drift, and delete strays
    for name in sorted(set(out_of_sync) | only_in_src):
        shutil.copy2(src / name, dst / name)
        print(f"  copied: {name}")
    for name in sorted(only_in_dst):
        (dst / name).unlink()
        print(f"  removed (stray in dst): {name}")

    if not drift:
        print(f"Already in sync: {len(common)} files.")
    else:
        print(f"Sync complete: {len(drift)} changes applied.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="CI mode: exit 1 if out of sync, do not modify")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    return sync(skill_root, args.check)


if __name__ == "__main__":
    sys.exit(main())
