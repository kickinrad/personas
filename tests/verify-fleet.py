#!/usr/bin/env python3
"""Validate the portable persona contract across a fleet of repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


PRIVATE_PATHS = ("user", ".claude/settings.local.json", ".codex/*.local.toml", ".mcp.json", ".env", ".env.*")
ALWAYS_LOADED_HEADINGS = re.compile(
    r"^#{1,6}\s+(?:tools?(?:\s+(?:inventory|available))?|procedures?|workflows?|rituals?|integrations?)\b",
    re.IGNORECASE | re.MULTILINE,
)


def tracked_files(repo: Path) -> set[Path]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True)
    if result.returncode == 0:
        return {repo / name for name in result.stdout.decode().split("\0") if name}
    return {path for path in repo.rglob("*") if path.is_file()}


def tracked_private_paths(repo: Path) -> list[str]:
    """Return tracked private paths, allowing user/ subpaths the persona re-includes after ignoring user/ by default."""
    result = subprocess.run(["git", "ls-files", "-z", "--", *PRIVATE_PATHS], cwd=repo, capture_output=True)
    if result.returncode:
        return []
    names = [name for name in result.stdout.decode().split("\0") if name]
    user = [name for name in names if name.startswith("user/")]
    denies_user = subprocess.run(["git", "check-ignore", "-q", "--no-index", "user/.verify-fleet-probe"], cwd=repo).returncode == 0
    if user and denies_user:
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", "-z", "--stdin"], cwd=repo, input="\0".join(user).encode(), capture_output=True
        ).stdout.decode()
        user = [name for name in user if name in set(ignored.split("\0"))]
    private = [name for name in names if not name.startswith("user/")]
    private += ["/".join(name.split("/")[:2]) + ("/" if name.count("/") > 1 else "") for name in user]
    return sorted(set(private))


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
        if required not in tracked or not required.is_file():
            errors.append(f"{name}: required tracked file missing: {required.relative_to(repo)}")

    private = tracked_private_paths(repo)
    if private:
        errors.append(f"{name}: private local context is tracked: {', '.join(private)}")

    if agents.is_file():
        always_loaded = agents.read_text(encoding="utf-8")
        if words(agents) > 300:
            errors.append(f"{name}: AGENTS.md exceeds 300 words")
        if ALWAYS_LOADED_HEADINGS.search(always_loaded):
            errors.append(f"{name}: AGENTS.md contains an always-loaded tool/procedure heading")
        if len(re.findall(r"^\s*\d+[.)]\s+", always_loaded, re.MULTILINE)) >= 4:
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

    for settings in (path for path in tracked if path.is_file() and claude_settings(path, repo)):
        try:
            json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: invalid JSON in {settings.relative_to(repo)}: {exc.msg}")
    codex = repo / ".codex/config.toml"
    if codex.is_file():
        try:
            tomllib.loads(codex.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{name}: invalid TOML in .codex/config.toml: {exc}")
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
