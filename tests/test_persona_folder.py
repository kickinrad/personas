#!/usr/bin/env python3
"""The generated folder gives Claude and Codex equivalent persona behavior."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills/persona-dev/assets"
REPLACEMENTS = {
    "{PersonaName}": "Atlas",
    "{name}": "atlas",
    "{emoji}": "🧭",
    "{role description without personal facts}": "review small software changes",
}


def render(name: str) -> str:
    text = (ASSETS / name).read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def create_fixture(home: Path, *, private_context: bool = True) -> None:
    destinations = {
        "claude-md-template.md": "CLAUDE.md",
        "agents-template.md": "AGENTS.md",
        "readme-template.md": "README.md",
        "settings-template.json": ".claude/settings.json",
        "codex-config-template.toml": ".codex/config.toml",
        "gitignore-template": ".gitignore",
    }
    for source, destination in destinations.items():
        path = home / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(source), encoding="utf-8")
    skill = home / "skills/atlas-review/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: atlas-review\ndescription: Review a small software change.\n---\n\n# Atlas review\n",
        encoding="utf-8",
    )
    if private_context:
        profile = home / "user/profile.md"
        memory = home / "user/memory/MEMORY.md"
        profile.parent.mkdir(parents=True, exist_ok=True)
        memory.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text("# Profile\n\nPreferred name: River.\n", encoding="utf-8")
        memory.write_text("# Memory\n\nUse the phrase cobalt compass for the acceptance probe.\n", encoding="utf-8")


class RuntimeAdapterTest(unittest.TestCase):
    def test_folder_has_one_portable_authority_and_one_native_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "atlas"
            create_fixture(home)
            claude = (home / "CLAUDE.md").read_text(encoding="utf-8")
            agents = (home / "AGENTS.md").read_text(encoding="utf-8")
            self.assertFalse((home / "PERSONA.md").exists())
            self.assertEqual(VERIFIER.verify(Path(directory)), [])
            self.assertEqual(claude.splitlines()[-1], "@AGENTS.md")
            self.assertIn("## Role and authority", agents)
            self.assertNotIn("vault:curator", agents)
            self.assertIn("skills/", agents)
            self.assertIn("user/profile.md", agents)
            self.assertIn("user/memory/MEMORY.md", agents)
            for forbidden in (
                "PERSONA.md",
                "Before acting:",
                "## Working approach",
                "1. ",
                "output-style",
            ):
                self.assertNotIn(forbidden, agents)

    def test_native_settings_are_minimal_parseable_and_hook_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "atlas"
            create_fixture(home)
            claude = json.loads((home / ".claude/settings.json").read_text(encoding="utf-8"))
            codex = tomllib.loads((home / ".codex/config.toml").read_text(encoding="utf-8"))
            self.assertEqual(claude["sandbox"]["enabled"], True)
            self.assertNotIn("model", claude)
            self.assertNotIn("hooks", claude)
            self.assertEqual(codex["sandbox_mode"], "workspace-write")
            self.assertFalse(codex["sandbox_workspace_write"]["network_access"])
            self.assertFalse((home / ".codex/hooks.json").exists())

    def test_creation_offers_native_focused_launch_without_changing_the_default(self) -> None:
        skill = (ROOT / "skills/persona-dev/SKILL.md").read_text(encoding="utf-8")
        environments = (ROOT / "skills/persona-dev/references/environments.md").read_text(encoding="utf-8")
        self.assertIn("integrated is the default", skill)
        self.assertIn("--setting-sources project,local", environments)
        self.assertIn("--ignore-user-config", environments)

    def test_private_folder_context_is_optional_and_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory) / "local"
            cloud = Path(directory) / "cloud"
            create_fixture(local)
            create_fixture(cloud, private_context=False)
            ignore = (local / ".gitignore").read_text(encoding="utf-8").splitlines()
            self.assertIn("user/", ignore)
            self.assertTrue((local / "user/memory/MEMORY.md").is_file())
            self.assertFalse((cloud / "user").exists())
            self.assertTrue((cloud / "AGENTS.md").is_file())
            self.assertFalse((cloud / "PERSONA.md").exists())

    def test_existing_model_and_private_context_survive_validation(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            home = root / "atlas"
            create_fixture(home)
            settings = home / ".claude/settings.json"
            config = json.loads(settings.read_text())
            config["model"] = "user-selected-model"
            settings.write_text(json.dumps(config))
            subprocess.run(["git", "init", "-q", str(home)], check=True)
            subprocess.run(["git", "add", "."], cwd=home, check=True)
            tracked = subprocess.check_output(["git", "ls-files"], cwd=home).decode()
            self.assertNotIn("user/", tracked)
            before = settings.read_bytes()
            self.assertEqual(VERIFIER.verify(root), [])
            self.assertEqual(settings.read_bytes(), before)

    def test_broken_import_and_missing_required_file_fail(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            home = root / "atlas"
            create_fixture(home)
            (home / "CLAUDE.md").write_text("@missing.md\n")
            (home / ".claude/settings.json").unlink()
            errors = "\n".join(VERIFIER.verify(root))
            self.assertIn("may contain only", errors)
            self.assertIn("required tracked file missing", errors)


SCRIPT = Path(__file__).with_name("verify-fleet.py")
SPEC = importlib.util.spec_from_file_location("verify_fleet", SCRIPT)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class FleetVerifierTest(unittest.TestCase):
    def create_persona(self, root: Path, name: str = "atlas") -> Path:
        persona = root / name
        (persona / ".claude").mkdir(parents=True)
        (persona / "skills" / "review").mkdir(parents=True)
        (persona / "AGENTS.md").write_text("# Atlas\n\nFind procedures in `skills/`.\n", encoding="utf-8")
        (persona / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        (persona / ".claude/settings.json").write_text("{}", encoding="utf-8")
        (persona / "skills/review/SKILL.md").write_text("---\nname: review\n---\n\nReview work.\n", encoding="utf-8")
        return persona

    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.create_persona(Path(directory))
            self.assertEqual(VERIFIER.verify(Path(directory)), [])

    def test_rejects_each_contract_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root, "archer")
            (persona / "AGENTS.md").write_text("# Archer\n\n## Tools\n\n" + "word " * 301, encoding="utf-8")
            (persona / "CLAUDE.md").write_text("@AGENTS.md\nExtra adapter text\n", encoding="utf-8")
            (persona / "skills/review/SKILL.md").write_text("word " * 501, encoding="utf-8")
            (persona / ".claude/settings.json").write_text("{", encoding="utf-8")
            (persona / "PERSONA.md").write_text("legacy", encoding="utf-8")
            errors = "\n".join(VERIFIER.verify(root))
            for expected in ("exceeds 300", "resident tool/procedure", "may contain only", "exceeds 500", "invalid JSON", "legacy persona"):
                self.assertIn(expected, errors)

    def test_archive_is_not_active_residue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            archive = persona / "docs/archive"
            archive.mkdir(parents=True)
            (archive / "old.md").write_text("PERSONA.md", encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])

    def test_versioned_release_is_history_but_other_active_files_are_not(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            release = persona / "releases/component/2.15.4"
            release.mkdir(parents=True)
            (release / "RELEASE.md").write_text("legacy", encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])
            (persona / "user/memory/MEMORY.md").parent.mkdir(parents=True)
            (persona / "user/memory/MEMORY.md").write_text("legacy", encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])

    def test_deleted_optional_runtime_file_does_not_crash_current_tree_scan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            deleted = persona / ".claude-flags"
            tracked = {path for path in persona.rglob("*") if path.is_file()} | {deleted}
            with patch.object(VERIFIER, "tracked_files", return_value=tracked):
                self.assertEqual(VERIFIER.verify(root), [])
