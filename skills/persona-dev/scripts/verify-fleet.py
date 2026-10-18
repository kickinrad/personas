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
    if result.returncode:  # Not a Git checkout, such as a source export: everything present ships.
        return sorted({str(path.relative_to(repo)) for pattern in PRIVATE_PATHS for path in repo.glob(pattern)})
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


REQUIRED = ("AGENTS.md", "PERSONAS.md", ".claude/settings.json")
SHARED = Path(__file__).resolve().parent.parent / "assets" / "PERSONAS.md"
TEMPLATE = SHARED.with_name("agents-template.md")
# Any of these in a persona or above it stops Claude Code from reading AGENTS.md.
CLAUDE_FILES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")


def persona_roots(fleet_root: Path) -> list[Path]:
    """Any folder holding a required file is a persona, so a missing one is reported, not skipped."""
    roots = [path for path in fleet_root.iterdir() if path.is_dir() and any((path / name).exists() for name in REQUIRED)]
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
    agents = repo / "AGENTS.md"

    for required in (repo / file for file in REQUIRED):
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
        craft = re.search(r"^## Craft\b(.*?)(?=^## |\Z)", always_loaded, re.MULTILINE | re.DOTALL)
        if not craft or not all(re.search(rf"\*\*{entry}:\*\*[^\n]*\w", craft.group(1)) for entry in ("Instruments", "Crew", "Proof")):
            errors.append(f"{name}: AGENTS.md needs a Craft section with Instruments, Crew, and Proof")
        flat = " ".join(always_loaded.split())
        if any(" ".join(slot.split()) in flat for slot in re.findall(r"\{[^{}]+\}", TEMPLATE.read_text(encoding="utf-8"))):
            errors.append(f"{name}: AGENTS.md still contains a template placeholder")
        if not re.search(r"@PERSONAS\.md\s*$", always_loaded, re.MULTILINE):
            errors.append(f"{name}: AGENTS.md must import the shared rules with a line ending in @PERSONAS.md")
    shared = repo / "PERSONAS.md"
    if shared.is_file() and shared.read_text(encoding="utf-8") != SHARED.read_text(encoding="utf-8"):
        errors.append(f"{name}: PERSONAS.md drifted from the plugin; run persona-native-sync.py --apply")

    errors += [f"{name}: delete {file}; it stops Claude Code from reading AGENTS.md" for file in CLAUDE_FILES if (repo / file).exists()]

    for skill in repo.glob("skills/**/SKILL.md"):
        if skill in tracked and words(skill) > 500:
            errors.append(f"{name}: {skill.relative_to(repo)} exceeds 500 words")

    for settings in (path for path in tracked if path.is_file() and claude_settings(path, repo)):
        try:
            json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: invalid JSON in {settings.relative_to(repo)}: {exc.msg}")
    allowlist = repo / ".agent-mcp.json"
    try:
        names = json.loads(allowlist.read_text(encoding="utf-8")) if allowlist.is_file() else []
        if not (isinstance(names, list) and all(isinstance(n, str) and re.fullmatch(r"[A-Za-z0-9_-]+", n) for n in names) and len(names) == len(set(names))):
            errors.append(f"{name}: .agent-mcp.json must be a list of unique server names")
    except json.JSONDecodeError as exc:
        errors.append(f"{name}: invalid JSON in agent MCP config: {exc.msg}")
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
        return [f"no persona folders under: {fleet_root}"]
    # Claude Code checks ancestors too. Above the fleet root, .claude/CLAUDE.md is skipped because
    # the user-level ~/.claude/CLAUDE.md is exempt and looks the same.
    blocking = [fleet_root / file for file in CLAUDE_FILES]
    blocking += [directory / file for directory in fleet_root.parents for file in ("CLAUDE.md", "CLAUDE.local.md")]
    errors = [f"delete {path}; it stops Claude Code from reading AGENTS.md" for path in blocking if path.exists()]
    if (fleet_root / "AGENTS.md").exists():
        errors.append(f"remove {fleet_root / 'AGENTS.md'}; Claude Code would load it into every persona")
    return errors + [error for root in roots for error in verify_persona(root)]


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
