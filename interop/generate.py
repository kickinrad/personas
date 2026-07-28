#!/usr/bin/env python3
"""Generate deterministic Codex projections from Personas source."""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "persona-manager": ("Persona Manager", "Create and evolve cross-harness personas", "Developer Tools", ["Interactive", "Write"]),
    "persona-dashboard": ("Persona Dashboard", "Install a read-only persona viewer", "Productivity", ["Interactive", "Write"]),
    "personas-mesh": ("Personas Mesh", "Operate profile-driven persona synchronization", "Developer Tools", ["Interactive", "Write"]),
}


def equal(left: Path, right: Path) -> bool:
    comparison = filecmp.dircmp(left, right)
    return not (
        comparison.left_only
        or comparison.right_only
        or comparison.funny_files
        or comparison.diff_files
        or any(not equal(left / name, right / name) for name in comparison.common_dirs)
    )


def portable_text(text: str) -> str:
    return (
        text.replace("${CLAUDE_PLUGIN_ROOT}", "the installed plugin root")
        .replace("persona-manager@personas", "the runtime's `persona-manager` plugin")
        .replace("persona-manager:self-improve", "the `persona-manager:self-improve` skill")
    )


def copy_portable_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target)
    for path in target.rglob("*.md"):
        path.write_text(portable_text(path.read_text(encoding="utf-8")), encoding="utf-8")


def generate(name: str, output: Path) -> None:
    plugin = ROOT / "plugins" / name
    caps = json.loads((plugin / "interop/capabilities.json").read_text(encoding="utf-8"))
    declared = sorted(caps["portableSkills"])
    actual = sorted(path.parent.name for path in (plugin / "skills").glob("*/SKILL.md"))
    if declared != actual:
        raise ValueError(f"{name}: portable skill declaration drift")

    copy_portable_tree(plugin / "skills", output / "skills")
    for directory in ("bin", "scripts", "templates", "systemd"):
        source = plugin / directory
        if source.is_dir():
            shutil.copytree(source, output / directory)
    shutil.copy2(plugin / "interop/capabilities.json", output / "capabilities.json")

    manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    display, short, category, capabilities = SPECS[name]
    manifest["skills"] = "./skills/"
    manifest["interface"] = {
        "displayName": display,
        "shortDescription": short,
        "longDescription": manifest["description"],
        "developerName": "Wils",
        "category": category,
        "capabilities": capabilities,
        "defaultPrompt": [f"Use {display} for this request."],
    }
    target = output / ".codex-plugin"
    target.mkdir()
    (target / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", action="append", choices=sorted(SPECS))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name in args.plugin or sorted(SPECS):
        destination = ROOT / "plugins" / name / ".generated" / name
        with tempfile.TemporaryDirectory(prefix=f"{name}-interop-") as temporary:
            staged = Path(temporary) / name
            generate(name, staged)
            if args.check:
                if not destination.is_dir() or not equal(staged, destination):
                    return 1
            else:
                if destination.exists():
                    shutil.rmtree(destination)
                shutil.copytree(staged, destination)
                print(f"generated Codex {name} plugin at {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
