#!/usr/bin/env python3
"""Release manifests share one current version."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "6.2.1"

class ReleaseTest(unittest.TestCase):
    def test_manifests_align(self) -> None:
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        agents = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        interop = json.loads((ROOT / "interop/capabilities.json").read_text())
        self.assertEqual({claude["version"], codex["version"], market["metadata"]["version"], interop["version"]}, {VERSION})
        self.assertEqual({claude["name"], codex["name"], market["plugins"][0]["name"]}, {"personas"})
        self.assertEqual({claude["license"], codex["license"]}, {"Apache-2.0"})
        self.assertEqual(agents["interface"]["displayName"], "Personas")

if __name__ == "__main__": unittest.main(verbosity=2)
