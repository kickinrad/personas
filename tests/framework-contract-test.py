#!/usr/bin/env python3
"""Contract tests for the small, folder-first personas product."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "4.0.0"
ASSETS = ROOT / "skills/persona-dev/assets"


class FrameworkContractTest(unittest.TestCase):
    def test_release_is_one_versioned_root_plugin(self) -> None:
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual({claude["version"], codex["version"], market["metadata"]["version"]}, {VERSION})
        self.assertEqual({claude["name"], codex["name"], market["plugins"][0]["name"]}, {"personas"})
        self.assertEqual(market["metadata"]["pluginRoot"], ".")
        self.assertEqual(codex["skills"], "./skills/")
        self.assertFalse((ROOT / "plugins").exists())

    def test_persona_assets_define_one_portable_folder(self) -> None:
        expected = {
            "agents-template.md",
            "claude-md-template.md",
            "codex-config-template.toml",
            "gitignore-template",
            "memory-template.md",
            "persona-template.md",
            "profile-template.md",
            "readme-template.md",
            "settings-template.json",
        }
        self.assertEqual({path.name for path in ASSETS.iterdir() if path.is_file()}, expected)
        persona = (ASSETS / "persona-template.md").read_text(encoding="utf-8")
        self.assertIn("# {PersonaName}", persona)
        self.assertIn("## Voice", persona)
        self.assertIn("## Boundaries", persona)
        for adapter in ("claude-md-template.md", "agents-template.md"):
            text = (ASSETS / adapter).read_text(encoding="utf-8")
            self.assertIn("PERSONA.md", text)
            self.assertIn("user/profile.md", text)
            self.assertIn("user/memory/MEMORY.md", text)

    def test_no_runtime_or_cli_enforcement_product_remains(self) -> None:
        for relative in (
            "bin/personas",
            "scripts/public-repo-guard.sh",
            "hooks/framework-version.sh",
            "hooks/hooks.json",
        ):
            self.assertFalse((ROOT / relative).exists(), relative)
        source = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for parent in (ROOT / "skills", ROOT / "interop")
            for path in parent.rglob("*")
            if path.is_file()
        )
        for retired in (
            ".persona-cloud-repository",
            "PERSONAS_GITHUB_VISIBILITY_ADAPTER",
            "bin/personas create",
            "bin/personas verify",
        ):
            self.assertNotIn(retired, source)

    def test_shared_skills_are_the_only_plugin_workflows(self) -> None:
        names = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(names, {"persona-dev", "persona-update", "self-improve"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
