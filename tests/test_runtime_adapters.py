#!/usr/bin/env python3
"""The generated folder gives Claude and Codex equivalent persona behavior."""

from __future__ import annotations

import json
import tempfile
import tomllib
import unittest
from pathlib import Path


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
            self.assertEqual(claude.splitlines()[-1], "@AGENTS.md")
            self.assertIn("## Role and authority", agents)
            self.assertIn("vault:curator", agents)
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
            self.assertEqual(claude["model"], "claude-opus-4-6[1m]")
            self.assertNotIn("hooks", claude)
            self.assertEqual(codex["sandbox_mode"], "workspace-write")
            self.assertFalse(codex["sandbox_workspace_write"]["network_access"])
            self.assertFalse((home / ".codex/hooks.json").exists())

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

    def test_capability_claims_name_executable_parity_evidence(self) -> None:
        capabilities = json.loads((ROOT / "interop/capabilities.json").read_text(encoding="utf-8"))
        self.assertEqual(capabilities["portableAuthority"], "AGENTS.md")
        self.assertEqual(capabilities["runtimes"]["claude-code"]["imports"], ["AGENTS.md"])
        self.assertEqual(capabilities["runtimes"]["codex"]["status"], "native")
        for runtime in ("claude-code", "codex"):
            probes = capabilities["runtimes"][runtime]["acceptanceProbes"]
            self.assertEqual(
                set(probes),
                {"identity", "voice", "boundary", "skill", "profile", "explicit-memory"},
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
