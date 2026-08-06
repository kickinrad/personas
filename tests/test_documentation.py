#!/usr/bin/env python3
"""Public documentation explains and links the folder-first product."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
EXAMPLE = ROOT / "examples/atlas-sanitized"
DOCS = (
    README,
    ROOT / "CONTRIBUTING.md",
    ROOT / "TROUBLESHOOTING.md",
    EXAMPLE / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "MIGRATION.md",
    ROOT / "ROLLBACK.md",
    ROOT / "SUPPORT.md",
    ROOT / "RELEASE.md",
)


class DocumentationTest(unittest.TestCase):
    def test_first_screen_explains_folder_outcome_support_and_install(self) -> None:
        first_screen = README.read_text(encoding="utf-8")[:2600].casefold()
        for phrase in (
            "a persona is a folder",
            "re-explaining",
            "durable collaborator",
            "claude code local",
            "claude code cloud",
            "codex",
            "persona.md",
            "/plugin marketplace add kickinrad/personas-framework",
        ):
            self.assertIn(phrase, first_screen)

    def test_readme_uses_only_current_user_interfaces(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("personas:persona-dev", text)
        self.assertIn("personas:persona-update", text)
        self.assertIn("personas:self-improve", text)
        for retired in (
            "bin/personas create",
            "bin/personas verify",
            ".persona-cloud-repository",
            "GH_TOKEN",
            "visibility adapter",
            "plugins/" + "persona-manager",
        ):
            self.assertNotIn(retired, text)

    def test_memory_and_cloud_claims_are_plain_and_truthful(self) -> None:
        text = README.read_text(encoding="utf-8")
        for phrase in (
            "user/memory/MEMORY.md",
            "$CODEX_HOME/memories",
            "do not synchronize",
            "private repository",
            "trusts you",
            "out of Git",
        ):
            self.assertIn(phrase, text)
        support = (ROOT / "SUPPORT.md").read_text(encoding="utf-8")
        self.assertIn("behavioral canary", support)
        self.assertIn("user-managed", support)

    def test_sanitized_example_is_a_complete_persona_folder(self) -> None:
        expected = {
            "PERSONA.md",
            "CLAUDE.md",
            "AGENTS.md",
            "README.md",
            ".gitignore",
            ".claude/settings.json",
            ".codex/config.toml",
            "skills/atlas-review/SKILL.md",
        }
        actual = {path.relative_to(EXAMPLE).as_posix() for path in EXAMPLE.rglob("*") if path.is_file()}
        self.assertEqual(actual, expected)
        all_text = "\n".join((EXAMPLE / path).read_text(encoding="utf-8") for path in expected)
        self.assertNotRegex(all_text, r"(?i)(password|private key|real integration)")

    def test_local_markdown_links_resolve(self) -> None:
        for document in DOCS:
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
                if "://" in target or target.startswith("mailto:"):
                    continue
                self.assertTrue((document.parent / target).resolve().exists(), f"{document}: {target}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
