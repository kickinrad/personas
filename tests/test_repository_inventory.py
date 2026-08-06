#!/usr/bin/env python3
"""Inventory policy for the deliberately small published framework source."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked() -> set[str]:
    result = subprocess.run(
        ("git", "ls-files"),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        return set(result.stdout.splitlines())
    # A source export intentionally has no Git metadata.  Its complete file
    # inventory is the closest equivalent for validating release contents.
    return {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


class RepositoryInventoryTest(unittest.TestCase):
    def test_no_retired_or_maintainer_residue_is_tracked(self) -> None:
        banned_prefixes = (
            ".claude/handoffs/",
            "tests/evals/",
            "tests/scenarios/",
            "plugins/",
        )
        banned_parts = {".generated", "__pycache__", ".pytest_cache", "runs"}
        banned_files = {"personas.md", "skill-rules.json"}
        for path in tracked():
            self.assertFalse(path.startswith(banned_prefixes), path)
            self.assertFalse(any(part in banned_parts for part in Path(path).parts), path)
            self.assertNotIn(path, banned_files)
        for retired in ("tests/evals", "tests/scenarios"):
            self.assertFalse((ROOT / retired).exists(), retired)

    def test_only_documented_public_asset_is_retained(self) -> None:
        assets = {path for path in tracked() if path.startswith("assets/")}
        self.assertEqual(assets, {"assets/banner.svg"})
        self.assertIn('src="assets/banner.svg"', (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_current_plan_and_evidence_are_the_only_claude_records(self) -> None:
        records = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / ".claude").rglob("*")
            if path.is_file()
        }
        self.assertIn(".claude/plans/personas-core-renewal.md", records)
        self.assertTrue(
            all(path.startswith(".claude/plans/") or path.startswith(".claude/evidence/") for path in records),
            records,
        )

    def test_json_sources_are_parseable(self) -> None:
        for relative in tracked():
            path = ROOT / relative
            if path.suffix == ".json" and path.is_file():
                with self.subTest(path=relative):
                    json.loads(path.read_text(encoding="utf-8"))

    def test_central_gate_and_ci_share_one_verdict(self) -> None:
        gate = (ROOT / "tests/run-tests.sh").read_text(encoding="utf-8")
        for test in (
            "personas-test.sh",
            "framework-contract-test.py",
            "test_runtime_adapters.py",
            "test_documentation.py",
            "test_repository_inventory.py",
            "test_release.py",
            "bash -n",
            "diff --check",
        ):
            self.assertIn(test, gate)
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("bash tests/run-tests.sh"), 1)
        self.assertNotIn("validate-json:", workflow)
        self.assertNotIn("check-secrets:", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
