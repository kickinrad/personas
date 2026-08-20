#!/usr/bin/env python3
"""Focused behavior tests for the reusable fleet contract verifier."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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
        (persona / ".claude/settings.json").write_text(json.dumps({"model": VERIFIER.MODEL}), encoding="utf-8")
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
            (persona / ".claude/settings.json").write_text(json.dumps({"model": "other"}), encoding="utf-8")
            (persona / "PERSONA.md").write_text("legacy", encoding="utf-8")
            (persona / "notes.md").write_text("Folder Bridge and four-week review", encoding="utf-8")
            (persona / ".claude-flags").write_text("--channels plugin:discord@claude-plugins-official", encoding="utf-8")
            errors = "\n".join(VERIFIER.verify(root))
            for expected in ("exceeds 300", "resident tool/procedure", "may contain only", "exceeds 500", "model must", "legacy persona", "folder bridge", "four-week review", "Discord is only"):
                self.assertIn(expected, errors)

    def test_archive_is_not_active_residue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            archive = persona / "docs/archive"
            archive.mkdir(parents=True)
            (archive / "old.md").write_text("PERSONA.md, Folder Bridge, and four-week review", encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])

    def test_versioned_release_is_history_but_other_active_files_are_not(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            release = persona / "releases/component/2.15.4"
            release.mkdir(parents=True)
            (release / "RELEASE.md").write_text("Folder Bridge recovery artifact", encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])
            (persona / "user/memory/MEMORY.md").parent.mkdir(parents=True)
            (persona / "user/memory/MEMORY.md").write_text("Folder Bridge", encoding="utf-8")
            self.assertIn("user/memory/MEMORY.md", "\n".join(VERIFIER.verify(root)))

    def test_only_named_personas_may_enable_discord(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root, "julia")
            (persona / ".claude-flags").write_text("--channels plugin:discord@claude-plugins-official", encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])

    def test_deleted_optional_runtime_file_does_not_crash_current_tree_scan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            deleted = persona / ".claude-flags"
            tracked = {path for path in persona.rglob("*") if path.is_file()} | {deleted}
            with patch.object(VERIFIER, "tracked_files", return_value=tracked):
                self.assertEqual(VERIFIER.verify(root), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
