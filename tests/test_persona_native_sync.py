#!/usr/bin/env python3
"""Behavioral tests for the opt-in persona-native adapter generator."""
from __future__ import annotations

import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/persona-dev/scripts/persona-native-sync.py"

class PersonaNativeSyncTest(unittest.TestCase):
    def fixture(self, directory: Path, mcp: dict | None = None) -> Path:
        persona = directory / "atlas-review"
        persona.mkdir()
        (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 Reviews small changes carefully.\n", encoding="utf-8")
        if mcp is not None: (persona / ".mcp.json").write_text(json.dumps({"mcpServers": mcp}), encoding="utf-8")
        return persona

    def invoke(self, persona: Path, claude: Path, codex: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(("python3", str(SCRIPT), "--persona", str(persona), "--claude-home", str(claude), "--codex-home", str(codex), *args), text=True, capture_output=True, check=False)

    def test_reports_then_generates_live_source_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); persona = self.fixture(root); claude = root / "claude"; codex = root / "codex"
            check = self.invoke(persona, claude, codex)
            self.assertEqual(check.returncode, 0, check.stderr); self.assertIn("drift", check.stdout); self.assertFalse(claude.exists())
            applied = self.invoke(persona, claude, codex, "--apply")
            self.assertEqual(applied.returncode, 0, applied.stderr)
            agent = (claude / "agents/atlas-review.md").read_text(encoding="utf-8")
            self.assertIn(str((persona / "AGENTS.md").resolve()), agent); self.assertNotIn("# Atlas Review", agent)
            parsed = tomllib.loads((codex / "agents/atlas-review.toml").read_text(encoding="utf-8"))
            self.assertEqual(parsed["name"], "atlas-review")
            self.assertEqual(parsed["description"], "🧭 Reviews small changes carefully.")
            self.assertEqual(tomllib.loads((codex / "persona-atlas-review.config.toml").read_text(encoding="utf-8")), {})

    def test_mcp_translation_and_collision_protection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, {"local": {"command": "tool", "args": ["serve"], "env": {"TOKEN": "${LOCAL_TOKEN}"}}, "remote": {"type": "streamable-http", "url": "https://example.test/mcp"}})
            result = self.invoke(persona, claude, codex, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            config = tomllib.loads((codex / "persona-atlas-review.config.toml").read_text(encoding="utf-8"))
            self.assertEqual(config["mcp_servers"]["local"]["command"], "tool")
            self.assertEqual(config["mcp_servers"]["local"]["env"]["TOKEN"], "${LOCAL_TOKEN}")
            agent = tomllib.loads((codex / "agents/atlas-review.toml").read_text(encoding="utf-8"))
            self.assertEqual(agent["mcp_servers"], config["mcp_servers"])
            target = claude / "agents/atlas-review.md"; target.write_text("manual", encoding="utf-8")
            self.assertEqual(self.invoke(persona, claude, codex, "--apply").returncode, 2)

    def test_rejects_unsupported_mcp_and_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, {"bad": {"type": "sse", "url": "https://example.test"}})
            self.assertEqual(self.invoke(persona, claude, codex).returncode, 2)
            (persona / ".mcp.json").write_text(json.dumps({"mcpServers": {"bad": {"command": "tool", "env": {"TOKEN": "literal"}}}}), encoding="utf-8")
            self.assertEqual(self.invoke(persona, claude, codex).returncode, 2)

if __name__ == "__main__": unittest.main(verbosity=2)
