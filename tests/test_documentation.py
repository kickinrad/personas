#!/usr/bin/env python3
"""Public documentation remains small, linked, and current."""
from __future__ import annotations
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = tuple(ROOT / "docs" / name for name in ("usage.md", "troubleshooting.md", "migration.md", "rollback.md", "runtime-evidence.md"))

class DocumentationTest(unittest.TestCase):
    def test_public_docs_are_present_and_linked(self) -> None:
        for document in DOCS:
            self.assertTrue(document.is_file(), document)
            text = document.read_text(encoding="utf-8")
            self.assertNotIn("PERSONA.md", text)
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
                if "://" not in target and not target.startswith("mailto:"):
                    self.assertTrue((document.parent / target).resolve().exists(), f"{document}: {target}")

    def test_example_is_complete_and_sanitized(self) -> None:
        example = ROOT / "examples" / "atlas"
        expected = {"CLAUDE.md", "AGENTS.md", "README.md", ".gitignore", ".claude/settings.json", ".codex/config.toml", "skills/atlas-review/SKILL.md"}
        actual = {path.relative_to(example).as_posix() for path in example.rglob("*") if path.is_file()}
        self.assertEqual(actual, expected)
        text = "\n".join((example / path).read_text(encoding="utf-8") for path in expected)
        self.assertNotRegex(text, r"(?i)(password|private key|real integration)")

if __name__ == "__main__": unittest.main(verbosity=2)
