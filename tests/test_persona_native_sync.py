#!/usr/bin/env python3
"""Behavioral tests for the native persona subagent generator."""
from __future__ import annotations

import importlib.util
import json
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


def frontmatter(text: str) -> dict[str, object]:
    """Parse the generator's frontmatter subset: JSON scalars and a list of single-key JSON maps."""
    result: dict[str, object] = {}
    for line in text.split("---\n")[1].splitlines():
        if line.startswith("  - "):
            key, value = line[4:].split(": ", 1)
            result["mcpServers"].append({json.loads(key): json.loads(value)})
        else:
            key, value = line.split(":", 1)
            result[key] = json.loads(value) if value.strip() else []
    return result


class PersonaNativeSyncTest(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.claude, self.codex = self.root / "claude", self.root / "codex"

    def persona(self, name: str = "atlas-review", mcp: dict | None = None) -> Path:
        persona = self.root / name
        persona.mkdir()
        (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 Reviews small changes carefully.\n", encoding="utf-8")
        if mcp is not None:
            (persona / ".mcp.json").write_text(json.dumps(mcp), encoding="utf-8")
        return persona

    def invoke(self, persona: Path, *args: str) -> subprocess.CompletedProcess[str]:
        command = ("python3", str(SCRIPT), "--persona", str(persona), "--claude-home", str(self.claude), "--codex-home", str(self.codex), *args)
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def adapters(self, slug: str = "atlas-review") -> tuple[str, dict[str, object]]:
        return (self.claude / f"agents/{slug}.md").read_text(encoding="utf-8"), tomllib.loads((self.codex / f"agents/{slug}.toml").read_text(encoding="utf-8"))

    def test_reports_then_writes_one_agent_per_runtime(self) -> None:
        persona = self.persona()
        report = self.invoke(persona)
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertEqual(report.stdout.count("drift"), 2)
        self.assertFalse(self.claude.exists() or self.codex.exists())
        self.assertEqual(self.invoke(persona, "--apply").returncode, 0)
        self.assertEqual(sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file() and persona not in p.parents),
                         ["claude/agents/atlas-review.md", "codex/agents/atlas-review.toml"])
        claude, codex = self.adapters()
        body = f"You are the persona defined in {persona / 'AGENTS.md'}. Read and follow it. Resolve its relative paths (skills/, user/, tools/) from {persona}."
        self.assertEqual(frontmatter(claude), {"name": "atlas-review", "description": "🧭 Reviews small changes carefully."})
        self.assertEqual(claude.split("---\n", 2)[2], f"\n{SYNC.MARKER}\n{SYNC.SOURCE}{json.dumps(str(persona / 'AGENTS.md'))}\n\n{body}\n")
        self.assertEqual(codex, {"name": "atlas-review", "description": "🧭 Reviews small changes carefully.", "developer_instructions": body})
        self.assertTrue((self.codex / "agents/atlas-review.toml").read_text().startswith(f"{SYNC.MARKER}\n{SYNC.SOURCE}"))
        self.assertEqual(self.invoke(persona).stdout.count("current"), 2)

    def test_body_edits_stay_current_and_description_edits_drift(self) -> None:
        persona = self.persona()
        self.invoke(persona, "--apply")
        (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 Reviews small changes carefully.\n\nFresh body prose.\n", encoding="utf-8")
        self.assertEqual(self.invoke(persona).stdout.count("current"), 2)
        (persona / "AGENTS.md").write_text("# Atlas Review\n\n> 🧭 A revised description.\n", encoding="utf-8")
        self.assertEqual(self.invoke(persona).stdout.count("drift"), 2)

    def test_color_is_validated_set_and_preserved(self) -> None:
        persona = self.persona()
        self.assertEqual(self.invoke(persona, "--color", "teal").returncode, 2)
        self.assertEqual(self.invoke(persona, "--color", "blue", "--apply").returncode, 0)
        self.assertEqual(frontmatter(self.adapters()[0])["color"], "blue")
        self.assertNotIn("color", self.adapters()[1])
        self.assertEqual(self.invoke(persona).stdout.count("current"), 2)
        self.assertEqual(self.invoke(persona, "--color", "pink", "--apply").returncode, 0)
        self.assertEqual(frontmatter(self.adapters()[0])["color"], "pink")

    def test_selected_mcp_servers_project_to_both_runtimes(self) -> None:
        servers = {
            "local": {"command": "tool", "args": ["serve"], "env": {"TOKEN": "${LOCAL_TOKEN}"}},
            "remote": {"type": "http", "url": "https://example.test/mcp?limit=10"},
            "claude-only": {"type": "sse", "url": "not-validated-unless-selected"},
        }
        persona = self.persona(mcp={"mcpServers": servers, "agentMcpServers": ["local", "remote"]})
        result = self.invoke(persona, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        claude, codex = self.adapters()
        self.assertEqual(frontmatter(claude)["mcpServers"], [
            {"local": {"type": "stdio", "command": "tool", "args": ["serve"], "env": {"TOKEN": "${LOCAL_TOKEN}"}}},
            {"remote": {"type": "http", "url": "https://example.test/mcp?limit=10"}},
        ])
        self.assertEqual(codex["mcp_servers"], {
            "local": {"command": "tool", "args": ["serve"], "env": {"TOKEN": "${LOCAL_TOKEN}"}},
            "remote": {"url": "https://example.test/mcp?limit=10"},
        })

    def test_unselected_servers_are_not_projected(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"private": {"command": "tool"}}})
        self.assertEqual(self.invoke(persona, "--apply").returncode, 0)
        claude, codex = self.adapters()
        self.assertNotIn("mcpServers", frontmatter(claude))
        self.assertNotIn("mcp_servers", codex)

    def test_serialization_preserves_quoted_unicode_values(self) -> None:
        name = 'weather.雪"tool'
        description = 'A reviewer: "careful" # always'
        persona = self.persona(mcp={"mcpServers": {name: {"command": "tool", "env": {"PLAIN.KEY": "value"}}}, "agentMcpServers": [name]})
        (persona / "AGENTS.md").write_text(f"# Atlas\n\n> {description}\n", encoding="utf-8")
        self.assertEqual(self.invoke(persona, "--apply").returncode, 0)
        claude, codex = self.adapters()
        self.assertEqual(frontmatter(claude)["description"], description)
        self.assertEqual(frontmatter(claude)["mcpServers"][0][name]["env"], {"PLAIN.KEY": "value"})
        self.assertEqual(codex["mcp_servers"][name]["env"], {"PLAIN.KEY": "value"})

    def test_rejects_invalid_mcp_declarations(self) -> None:
        cases = {
            "legacy key": {"mcpServers": {"a": {"command": "tool"}}, "codexMcpServers": ["a"]},
            "missing server": {"mcpServers": {}, "agentMcpServers": ["missing"]},
            "duplicate name": {"mcpServers": {"a": {"command": "tool"}}, "agentMcpServers": ["a", "a"]},
            "unsupported transport": {"mcpServers": {"a": {"type": "sse", "url": "https://example.test"}}, "agentMcpServers": ["a"]},
            "non-string env": {"mcpServers": {"a": {"command": "tool", "env": {"COUNT": 3}}}, "agentMcpServers": ["a"]},
            "extra field": {"mcpServers": {"a": {"command": "tool", "cwd": "/tmp"}}, "agentMcpServers": ["a"]},
            "not an object": [],
        }
        for index, (label, payload) in enumerate(cases.items()):
            with self.subTest(label):
                result = self.invoke(self.persona(f"atlas-{index}", payload), "--apply")
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr.startswith("error: "))
        self.assertFalse(self.claude.exists() or self.codex.exists())

    def test_rejects_credentials(self) -> None:
        cases = {
            "literal env": ({"command": "tool", "env": {"TOKEN": "literal"}}, "credential literal"),
            "secret key": ({"command": "tool", "env": {"SECRET_KEY": "literal"}}, "credential literal"),
            "aws secret": ({"command": "tool", "env": {"AWS_SECRET_ACCESS_KEY": "literal"}}, "credential literal"),
            "password hash": ({"command": "tool", "env": {"PASSWORD_HASH": "literal"}}, "credential literal"),
            "token-shaped arg": ({"command": "tool", "args": ["sk-" + "x" * 16]}, "credential literal"),
            "url userinfo": ({"type": "http", "url": "https://user:password@example.test/mcp"}, "must not contain credentials"),
            "encoded userinfo": ({"type": "http", "url": "https://user%3Apassword@example.test/mcp"}, "must not contain credentials"),
            "query token": ({"type": "http", "url": "https://example.test/mcp?token=value"}, "credential parameters"),
            "encoded query key": ({"type": "http", "url": "https://example.test/mcp?api%5Fkey=value"}, "credential parameters"),
            "fragment secret": ({"type": "http", "url": "https://example.test/mcp#secret=value"}, "credential parameters"),
        }
        for index, (label, (server, message)) in enumerate(cases.items()):
            with self.subTest(label):
                result = self.invoke(self.persona(f"atlas-{index}", {"mcpServers": {"a": server}, "agentMcpServers": ["a"]}))
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)

    def test_settings_that_mention_credentials_are_not_credentials(self) -> None:
        server = {"command": "tool", "env": {"REDACT_SECRETS": "true", "TOKEN_CACHE_DIR": "/tmp/cache", "API_TOKEN": "${API_TOKEN}"}}
        result = self.invoke(self.persona(mcp={"mcpServers": {"a": server}, "agentMcpServers": ["a"]}), "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_refuses_unowned_and_other_persona_files_before_writing(self) -> None:
        persona = self.persona()
        manual = self.codex / "agents/atlas-review.toml"
        manual.parent.mkdir(parents=True)
        manual.write_text("manual = true\n", encoding="utf-8")
        result = self.invoke(persona, "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("move aside", result.stderr)
        self.assertFalse(self.claude.exists())
        manual.write_text(f'{SYNC.MARKER}\n{SYNC.SOURCE}"/elsewhere/AGENTS.md"\n', encoding="utf-8")
        self.assertEqual(self.invoke(persona, "--apply").returncode, 2)
        manual.unlink()
        self.assertEqual(self.invoke(self.persona("Atlas Review"), "--apply").returncode, 0)
        self.assertEqual(self.invoke(persona, "--apply").returncode, 2)

    def test_single_runtime_touches_only_its_home(self) -> None:
        persona = self.persona()
        self.assertEqual(self.invoke(persona, "--runtime", "claude", "--apply").returncode, 0)
        self.assertFalse(self.codex.exists())
        self.assertEqual(self.invoke(persona, "--runtime", "codex", "--apply").returncode, 0)
        self.assertTrue((self.codex / "agents/atlas-review.toml").is_file())

    def test_codex_home_defaults_to_environment(self) -> None:
        persona = self.persona()
        command = ("python3", str(SCRIPT), "--persona", str(persona), "--runtime", "codex")
        result = subprocess.run(command, text=True, capture_output=True, check=False, env={"CODEX_HOME": str(self.codex), "HOME": str(self.root)})
        self.assertEqual(result.stdout.strip(), f"drift {self.codex / 'agents/atlas-review.toml'}")

    def test_failed_replace_preserves_destination_and_cleans_temporary_file(self) -> None:
        target = self.root / "agent.toml"
        target.write_text("original")
        with patch.object(Path, "replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                SYNC.write(target, "replacement")
        self.assertEqual(target.read_text(), "original")
        self.assertEqual(list(self.root.iterdir()), [target])


if __name__ == "__main__": unittest.main(verbosity=2)
