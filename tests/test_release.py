#!/usr/bin/env python3
"""Release-preparation assertions for the root Persona Manager product."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.0"


class ReleasePreparationTest(unittest.TestCase):
    def test_semver_and_license_are_authoritative_and_aligned(self) -> None:
        self.assertIn("Apache License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual({claude["version"], codex["version"], market["metadata"]["version"]}, {VERSION})
        self.assertEqual({claude["license"], codex["license"]}, {"Apache-2.0"})
        self.assertTrue(all("version" not in entry for entry in market["plugins"]))

    def test_release_docs_cover_layout_boundary_rollback_and_deferred_work(self) -> None:
        migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
        release = (ROOT / "RELEASE.md").read_text(encoding="utf-8")
        rollback = (ROOT / "ROLLBACK.md").read_text(encoding="utf-8")
        support = (ROOT / "SUPPORT.md").read_text(encoding="utf-8")
        old_layout = "plugins/" + "persona-manager/"
        for phrase in (old_layout, "user/profile.md", "PRIVATE", "Codex", "Deferred work"):
            self.assertIn(phrase, migration)
        self.assertIn("d3a0ed1d29177f85df9cdc28f4e51378ed0da8d9", rollback)
        self.assertIn("tag", release)
        self.assertIn("Recommended GitHub topics", release)
        self.assertIn("Claude Code Cloud", support)

    def test_public_rollback_revision_resolves(self) -> None:
        if not (ROOT / ".git").exists():
            self.skipTest("source export has no Git metadata")
        result = subprocess.run(
            ("git", "rev-parse", "--verify", "d3a0ed1d29177f85df9cdc28f4e51378ed0da8d9^{commit}"),
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_maintainer_local_mesh_recovery_ref_when_available(self) -> None:
        if not (ROOT / ".git").exists():
            self.skipTest("source export has no Git metadata")
        result = subprocess.run(
            ("git", "rev-parse", "--verify", "forge/personas-mesh-extraction^{commit}"),
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if result.returncode != 0:
            self.skipTest("maintainer-local Mesh recovery ref is deliberately unpublished")
        self.assertEqual(result.stdout.strip(), "e1f504222883b0fb5823f6cbec2b2305336dbdd4")


if __name__ == "__main__":
    unittest.main(verbosity=2)
