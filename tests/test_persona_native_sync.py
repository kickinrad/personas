#!/usr/bin/env python3
"""Behavioral tests for the opt-in persona-native adapter generator."""
from __future__ import annotations

import json
import importlib.util
import contextlib
import io
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/persona-dev/scripts/persona-native-sync.py"
SPEC = importlib.util.spec_from_file_location("native_sync", SCRIPT)
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)

class PersonaNativeSyncTest(unittest.TestCase):
    def fixture(self, directory: Path, name: str = "atlas-review", mcp: dict | None = None, codex_mcps: list[str] | None = None) -> Path:
        persona = directory / name
        persona.mkdir()
        (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 Reviews small changes carefully.\n", encoding="utf-8")
        if mcp is not None:
            payload = {"mcpServers": mcp}
            if codex_mcps is not None: payload["codexMcpServers"] = codex_mcps
            (persona / ".mcp.json").write_text(json.dumps(payload), encoding="utf-8")
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
            self.assertIn("source-agents", agent)
            self.assertNotIn("input-sha256", agent)

    def test_source_edits_do_not_cause_adapter_drift(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); persona = self.fixture(root); claude = root / "claude"; codex = root / "codex"
            self.assertEqual(self.invoke(persona, claude, codex, "--apply").returncode, 0)
            before = [(claude / "agents/atlas-review.md").read_text(), (codex / "agents/atlas-review.toml").read_text(), (codex / "persona-atlas-review.config.toml").read_text()]
            (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 Reviews small changes carefully.\n\nFresh body prose.\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.count("current"), 3)
            after = [(claude / "agents/atlas-review.md").read_text(), (codex / "agents/atlas-review.toml").read_text(), (codex / "persona-atlas-review.config.toml").read_text()]
            self.assertEqual(after, before)

    def test_description_edits_drift_agents_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); persona = self.fixture(root); claude = root / "claude"; codex = root / "codex"
            self.assertEqual(self.invoke(persona, claude, codex, "--apply").returncode, 0)
            (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 A revised description.\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.count("drift"), 2)
            self.assertEqual(result.stdout.count("current"), 1)

    def test_mcp_translation_and_collision_protection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, mcp={"local": {"command": "tool", "args": ["serve"], "env": {"TOKEN": "${LOCAL_TOKEN}"}}, "remote": {"type": "streamable-http", "url": "https://example.test/mcp"}}, codex_mcps=["local", "remote"])
            result = self.invoke(persona, claude, codex, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            config = tomllib.loads((codex / "persona-atlas-review.config.toml").read_text(encoding="utf-8"))
            self.assertEqual(config["mcp_servers"]["local"]["command"], "tool")
            self.assertEqual(config["mcp_servers"]["local"]["env"]["TOKEN"], "${LOCAL_TOKEN}")
            agent = tomllib.loads((codex / "agents/atlas-review.toml").read_text(encoding="utf-8"))
            self.assertEqual(agent["mcp_servers"], config["mcp_servers"])
            target = claude / "agents/atlas-review.md"; target.write_text("manual", encoding="utf-8")
            self.assertEqual(self.invoke(persona, claude, codex, "--apply").returncode, 2)

    def test_quotes_mcp_names_and_rejects_invalid_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, mcp={"alpha.beta": {"command": "tool", "env": {"COUNT": 3}}}, codex_mcps=["alpha.beta"])
            self.assertEqual(self.invoke(persona, claude, codex).returncode, 2)
            (persona / ".mcp.json").write_text(json.dumps({"mcpServers": {"alpha.beta": {"command": "tool", "env": {"COUNT": "3"}}}, "codexMcpServers": ["alpha.beta"]}), encoding="utf-8")
            self.assertEqual(self.invoke(persona, claude, codex, "--apply").returncode, 0)
            parsed = tomllib.loads((codex / "agents/atlas-review.toml").read_text())
            self.assertEqual(parsed["mcp_servers"]["alpha.beta"]["command"], "tool")

    def test_private_mcps_are_not_projected_without_named_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, mcp={"claude-only": {"command": "tool"}})
            result = self.invoke(persona, claude, codex, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(tomllib.loads((codex / "persona-atlas-review.config.toml").read_text()), {})
            bad = self.invoke(persona, claude, codex, "--codex-mcp", "missing")
            self.assertEqual(bad.returncode, 2)

    def test_unselected_claude_only_binding_is_not_validated_for_codex(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, mcp={
                "codex": {"command": "tool"},
                "claude-only": {"type": "sse", "url": "not-a-codex-transport"},
            }, codex_mcps=["codex"])
            result = self.invoke(persona, claude, codex, "--runtime", "codex", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            config = tomllib.loads((codex / "persona-atlas-review.config.toml").read_text())
            self.assertEqual(set(config["mcp_servers"]), {"codex"})

    def test_profile_only_never_touches_native_agent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, mcp={"local": {"command": "tool"}}, codex_mcps=["local"])
            agent = codex / "agents/atlas-review.toml"
            agent.parent.mkdir(parents=True)
            agent.write_text("manual = true\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex, "--runtime", "codex", "--codex-artifact", "profile", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agent.read_text(encoding="utf-8"), "manual = true\n")
            self.assertTrue((codex / "persona-atlas-review.config.toml").is_file())

    def test_agent_only_never_creates_profile(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root)
            result = self.invoke(persona, claude, codex, "--runtime", "codex", "--codex-artifact", "agent", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((codex / "agents/atlas-review.toml").is_file())
            self.assertFalse((codex / "persona-atlas-review.config.toml").exists())

    def test_prunes_only_marked_legacy_profile_agent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root)
            legacy = codex / "agents/persona-atlas-review.config.toml"
            legacy.parent.mkdir(parents=True)
            instruction = json.dumps(f"Read and follow {persona / 'AGENTS.md'}.")
            legacy.write_text(f"{SYNC.MARKER}\ndeveloper_instructions = {instruction}\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(legacy.exists())

    def test_preflight_prevents_partial_writes_and_cross_persona_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root)
            target = codex / "agents/atlas-review.toml"; target.parent.mkdir(parents=True); target.write_text("manual = true\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex, "--apply")
            self.assertEqual(result.returncode, 2)
            self.assertFalse((claude / "agents/atlas-review.md").exists())
            target.unlink()
            first = self.fixture(root, "Atlas Review")
            second = self.fixture(root, "atlas_review")
            self.assertEqual(self.invoke(first, claude, codex, "--runtime", "codex", "--codex-artifact", "agent", "--apply").returncode, 0)
            self.assertEqual(self.invoke(second, claude, codex, "--runtime", "codex", "--codex-artifact", "agent", "--apply").returncode, 2)

    def test_refuses_source_less_legacy_profile(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); persona = self.fixture(root); claude = root / "claude"; codex = root / "codex"
            profile = codex / "persona-atlas-review.config.toml"; profile.parent.mkdir(); profile.write_text("# Generated by Personas persona-native-sync.py\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex, "--runtime", "codex", "--codex-artifact", "profile", "--apply")
            self.assertEqual(result.returncode, 2)
            self.assertIn("move aside", result.stderr)

    def test_claude_mode_skips_codex_mcp_validation_and_legacy_pruning(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); persona = self.fixture(root, mcp={"bad": {"type": "sse", "url": "https://example.test"}}, codex_mcps=["bad"]); claude = root / "claude"; codex = root / "codex"
            legacy = codex / "agents/persona-atlas-review.config.toml"; legacy.parent.mkdir(parents=True); legacy.write_text("manual = true\n", encoding="utf-8")
            result = self.invoke(persona, claude, codex, "--runtime", "claude", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(legacy.read_text(encoding="utf-8"), "manual = true\n")

    def test_claude_mode_ignores_invalid_codex_payload(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); persona = self.fixture(root); claude = root / "claude"; codex = root / "codex"
            (persona / ".mcp.json").write_text("{", encoding="utf-8")
            self.assertEqual(self.invoke(persona, claude, codex, "--runtime", "claude", "--apply").returncode, 0)

    def test_rejects_unsupported_mcp_and_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            persona = self.fixture(root, mcp={"bad": {"type": "sse", "url": "https://example.test"}}, codex_mcps=["bad"])
            self.assertEqual(self.invoke(persona, claude, codex).returncode, 2)
            (persona / ".mcp.json").write_text(json.dumps({"mcpServers": {"bad": {"command": "tool", "env": {"TOKEN": "literal"}}}, "codexMcpServers": ["bad"]}), encoding="utf-8")
            self.assertEqual(self.invoke(persona, claude, codex).returncode, 2)

    def test_rejects_http_mcp_url_userinfo(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            for index, url in enumerate(("https://user:password@example.test/mcp", "https://user%3Apassword@example.test/mcp")):
                with self.subTest(url=url):
                    persona = self.fixture(root, f"atlas-review-{index}", {"remote": {"type": "http", "url": url}}, ["remote"])
                    result = self.invoke(persona, claude, codex)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("must not contain credentials", result.stderr)

    def test_rejects_http_mcp_credential_parameters_but_allows_ordinary_queries(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); claude = root / "claude"; codex = root / "codex"
            urls = (
                "https://example.test/mcp?token=value",
                "https://example.test/mcp?api%5Fkey=value",
                "https://example.test/mcp#secret=value",
            )
            for index, url in enumerate(urls):
                with self.subTest(url=url):
                    persona = self.fixture(
                        root,
                        f"atlas-review-{index}",
                        {"remote": {"type": "http", "url": url}},
                        ["remote"],
                    )
                    result = self.invoke(persona, claude, codex)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("must not contain credential parameters", result.stderr)
            persona = self.fixture(
                root,
                "atlas-review-query",
                {"remote": {"type": "http", "url": "https://example.test/mcp?limit=10"}},
                ["remote"],
            )
            result = self.invoke(persona, claude, codex)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_serialization_preserves_quoted_unicode_values(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            name = 'weather.雪"tool'
            persona = self.fixture(root, mcp={name: {"command": "tool", "env": {"PLAIN.KEY": "value"}}}, codex_mcps=[name])
            description = 'A reviewer: "careful" # always'
            (persona / "AGENTS.md").write_text(f"# Atlas\n\n> {description}\n")
            result = self.invoke(persona, root / "claude", root / "codex", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            claude = (root / "claude/agents/atlas-review.md").read_text()
            scalar = next(line.removeprefix("description: ") for line in claude.splitlines() if line.startswith("description: "))
            self.assertEqual(json.loads(scalar), description)
            codex = tomllib.loads((root / "codex/agents/atlas-review.toml").read_text())
            self.assertEqual(codex["mcp_servers"][name]["env"], {"PLAIN.KEY": "value"})

    def test_foreign_metadata_and_ambiguous_pruning_never_write(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona = self.fixture(root)
            agent = root / "codex/agents/atlas-review.toml"
            agent.parent.mkdir(parents=True)
            agent.write_text(f'{SYNC.MARKER}\n{SYNC.SOURCE}"/foreign/AGENTS.md"\nRead and follow {persona / "AGENTS.md"}.\n')
            self.assertEqual(self.invoke(persona, root / "claude", root / "codex", "--apply").returncode, 2)
            self.assertFalse((root / "claude").exists())
            agent.unlink()
            legacy = agent.with_name("persona-atlas-review.config.toml")
            legacy.write_text(SYNC.MARKER + "\n")
            self.assertEqual(self.invoke(persona, root / "claude", root / "codex", "--apply").returncode, 2)
            self.assertFalse((root / "claude").exists())
            result = self.invoke(persona, root / "claude", root / "codex", "--runtime", "codex", "--codex-artifact", "profile", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(legacy.exists())

    def test_failed_replace_preserves_destination_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "agent.toml"
            target.write_text("original")
            with patch.object(Path, "replace", side_effect=OSError("fixture failure")):
                with self.assertRaises(OSError):
                    SYNC.write(target, "replacement")
            self.assertEqual(target.read_text(), "original")
            self.assertEqual(list(target.parent.iterdir()), [target])

    def test_malformed_payload_returns_actionable_error(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona = self.fixture(root)
            (persona / ".mcp.json").write_text("[]")
            result = self.invoke(persona, root / "claude", root / "codex", "--apply")
            self.assertEqual(result.returncode, 2)
            self.assertIn("must be an object", result.stderr)
            self.assertFalse((root / "claude").exists())

    def test_write_failure_reports_progress_for_recovery(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona = self.fixture(root)
            original_write = SYNC.write

            def write_until_codex(target, content):
                if target.suffix == ".toml":
                    raise PermissionError("synthetic failure")
                original_write(target, content)

            arguments = [str(SCRIPT), "--persona", str(persona), "--apply",
                         "--claude-home", str(root / "claude"), "--codex-home", str(root / "codex")]
            output, errors = io.StringIO(), io.StringIO()
            with patch("sys.argv", arguments), patch.object(SYNC, "write", side_effect=write_until_codex):
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    self.assertEqual(SYNC.main(), 2)
            self.assertTrue((root / "claude/agents/atlas-review.md").is_file())
            self.assertFalse((root / "codex").exists())
            self.assertIn("completed:", errors.getvalue())
            self.assertIn("remaining:", errors.getvalue())
            self.assertIn("persona-atlas-review.config.toml", errors.getvalue())

if __name__ == "__main__": unittest.main(verbosity=2)
