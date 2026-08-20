#!/usr/bin/env python3
"""Validate the portable persona contract across a fleet of repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


MODEL = "claude-opus-4-6[1m]"
DISCORD_PERSONAS = {"bob", "flora", "julia"}
ARCHIVE_PARTS = {"archive", "archives", "consumed", "history", "historical", ".git", "node_modules", "__pycache__"}
RELEASE_VERSION = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
RETIRED_REFERENCES = ("persona.md", "folder bridge", "bridgey inbox", "four-week review")
RESIDENT_HEADINGS = re.compile(
    r"^#{1,6}\s+(?:tools?(?:\s+(?:inventory|available))?|procedures?|workflows?|rituals?|integrations?)\b",
    re.IGNORECASE | re.MULTILINE,
)


def is_active(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    if any(part.lower() in ARCHIVE_PARTS for part in parts):
        return False
    return not (len(parts) >= 4 and parts[0] == "releases" and RELEASE_VERSION.fullmatch(parts[2]))


def tracked_files(repo: Path) -> set[Path]:
    result = subprocess.run(
        ("git", "ls-files", "-z"), cwd=repo, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, check=False,
    )
    if result.returncode == 0:
        return {repo / name for name in result.stdout.decode().split("\0") if name}
    return {path for path in repo.rglob("*") if path.is_file()}


def persona_roots(fleet_root: Path) -> list[Path]:
    roots = [path for path in fleet_root.iterdir() if path.is_dir() and (path / "AGENTS.md").is_file()]
    return sorted(roots, key=lambda path: path.name)


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def claude_settings(path: Path, repo: Path) -> bool:
    relative = path.relative_to(repo)
    return len(relative.parts) >= 2 and relative.parts[0] == ".claude" and path.name.startswith("settings") and path.suffix == ".json"


def verify_persona(repo: Path) -> list[str]:
    errors: list[str] = []
    name = repo.name
    tracked = tracked_files(repo)
    agents, claude = repo / "AGENTS.md", repo / "CLAUDE.md"

    for required in (agents, claude, repo / ".claude/settings.json"):
        if required not in tracked:
            errors.append(f"{name}: required tracked file missing: {required.relative_to(repo)}")

    if agents.is_file():
        resident = agents.read_text(encoding="utf-8")
        if words(agents) > 300:
            errors.append(f"{name}: AGENTS.md exceeds 300 words")
        if RESIDENT_HEADINGS.search(resident):
            errors.append(f"{name}: AGENTS.md contains a resident tool/procedure heading")
        if len(re.findall(r"^\s*\d+[.)]\s+", resident, re.MULTILINE)) >= 4:
            errors.append(f"{name}: AGENTS.md contains procedural bulk (four or more numbered steps)")

    if claude.is_file():
        if words(claude) > 80:
            errors.append(f"{name}: CLAUDE.md exceeds 80 words")
        nonempty = [line.strip() for line in claude.read_text(encoding="utf-8").splitlines() if line.strip()]
        if nonempty[-1:] != ["@AGENTS.md"] or any(not line.startswith("#") for line in nonempty[:-1]):
            errors.append(f"{name}: CLAUDE.md may contain only an optional title and the @AGENTS.md import")

    for skill in repo.glob("skills/**/SKILL.md"):
        if skill in tracked and words(skill) > 500:
            errors.append(f"{name}: {skill.relative_to(repo)} exceeds 500 words")

    for settings in (path for path in tracked if claude_settings(path, repo)):
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: invalid JSON in {settings.relative_to(repo)}: {exc.msg}")
            continue
        if data.get("model") != MODEL:
            errors.append(f"{name}: {settings.relative_to(repo)} model must be {MODEL}")

    runtime_files = [
        path for path in tracked
        if path.is_file() and (path.name == ".claude-flags" or claude_settings(path, repo))
    ]
    discord_enabled = any("discord@claude-plugins-official" in path.read_text(encoding="utf-8") for path in runtime_files)
    if discord_enabled and name not in DISCORD_PERSONAS:
        errors.append(f"{name}: Discord is only permitted for Bob, Flora, and Julia")

    for path in (path for path in repo.rglob("*") if path.is_file()):
        if not is_active(path, repo):
            continue
        relative = path.relative_to(repo)
        lowered_parts = {part.lower() for part in relative.parts}
        if path.name == "PERSONA.md":
            errors.append(f"{name}: active legacy persona definition: {relative}")
        if "output-styles" in lowered_parts:
            errors.append(f"{name}: active legacy output style: {relative}")
        if path.suffix.lower() not in {".md", ".json", ".toml", ".txt", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for retired in RETIRED_REFERENCES:
            if retired in text:
                errors.append(f"{name}: active retired reference '{retired}' in {relative}")

    return errors


def verify(fleet_root: Path) -> list[str]:
    if not fleet_root.is_dir():
        return [f"fleet root does not exist: {fleet_root}"]
    roots = persona_roots(fleet_root)
    if not roots:
        return [f"no persona folders with AGENTS.md under: {fleet_root}"]
    return [error for root in roots for error in verify_persona(root)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="directory containing persona folders")
    args = parser.parse_args()
    errors = verify(args.root.resolve())
    if errors:
        print("Fleet contract failed:", file=sys.stderr)
        print(*(f"- {error}" for error in errors), sep="\n", file=sys.stderr)
        return 1
    print(f"Fleet contract passed: {len(persona_roots(args.root.resolve()))} personas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
