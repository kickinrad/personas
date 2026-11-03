#!/usr/bin/env python3
"""Behavioral tests for the native persona subagent generator."""
from __future__ import annotations

import importlib.util
import json
import shutil
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

    def persona(self, name: str = "wren-review", mcp: dict | None = None) -> Path:
        persona = self.root / name
        persona.mkdir()
        (persona / "AGENTS.md").write_text("# Wren Review\n\n> 🧭 Reviews small changes carefully.\n", encoding="utf-8")
        if isinstance(mcp, dict) and "agentMcpServers" in mcp:
            mcp = dict(mcp)
            (persona / ".agent-mcp.json").write_text(json.dumps(mcp.pop("agentMcpServers")), encoding="utf-8")
        if mcp is not None:
            (persona / ".mcp.json").write_text(json.dumps(mcp), encoding="utf-8")
        return persona

    def invoke(self, persona: Path, *args: str) -> subprocess.CompletedProcess[str]:
        command = ("python3", str(SCRIPT), "--persona", str(persona), "--claude-home", str(self.claude), "--codex-home", str(self.codex), *args)
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def adapters(self, slug: str = "wren-review") -> tuple[str, dict[str, object]]:
        return (self.claude / f"agents/{slug}.md").read_text(encoding="utf-8"), tomllib.loads((self.codex / f"agents/{slug}.toml").read_text(encoding="utf-8"))

    def test_reports_then_writes_one_agent_per_runtime(self) -> None:
        persona = self.persona()
        report = self.invoke(persona)
        self.assertEqual(report.returncode, 1, report.stderr)
        self.assertEqual(report.stdout.count("drift"), 3)
        self.assertFalse(self.claude.exists() or self.codex.exists() or (persona / "PERSONAS.md").exists())
        self.assertEqual(self.invoke(persona, "--apply").returncode, 0)
        self.assertEqual(sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file() and persona not in p.parents),
                         ["claude/agents/wren-review.md", "codex/agents/wren-review.toml"])
        self.assertEqual((persona / "PERSONAS.md").read_text(), SYNC.SHARED.read_text())
        claude, codex = self.adapters()
        body = f"You are the persona defined in {persona / 'AGENTS.md'}. Read and follow it. Resolve its relative paths (skills/, user/, tools/) from {persona}."
        self.assertEqual(frontmatter(claude), {"name": "wren-review", "description": "🧭 Reviews small changes carefully."})
        self.assertEqual(claude.split("---\n", 2)[2], f"\n{SYNC.MARKER}\n{SYNC.SOURCE}{json.dumps(str(persona / 'AGENTS.md'))}\n\n{body}\n")
        self.assertEqual(codex, {"name": "wren-review", "description": "🧭 Reviews small changes carefully.", "developer_instructions": body})
        self.assertTrue((self.codex / "agents/wren-review.toml").read_text().startswith(f"{SYNC.MARKER}\n{SYNC.SOURCE}"))
        clean = self.invoke(persona)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertEqual(clean.stdout.count("current"), 3)

    def test_body_edits_stay_current_and_description_edits_drift(self) -> None:
        persona = self.persona()
        self.invoke(persona, "--apply")
        (persona / "AGENTS.md").write_text("# Wren Review\n\n> 🧭 Reviews small changes carefully.\n\nFresh body prose.\n", encoding="utf-8")
        self.assertEqual(self.invoke(persona).stdout.count("current"), 3)
        (persona / "AGENTS.md").write_text("# Wren Review\n\n> 🧭 A revised description.\n", encoding="utf-8")
        drift = self.invoke(persona)
        self.assertEqual(drift.returncode, 1, drift.stderr)
        self.assertEqual(drift.stdout.count("drift"), 2)

    def test_color_is_validated_set_and_preserved(self) -> None:
        persona = self.persona()
        self.assertEqual(self.invoke(persona, "--color", "teal").returncode, 2)
        self.assertEqual(self.invoke(persona, "--color", "blue", "--apply").returncode, 0)
        self.assertEqual(frontmatter(self.adapters()[0])["color"], "blue")
        self.assertNotIn("color", self.adapters()[1])
        self.assertEqual(self.invoke(persona).stdout.count("current"), 3)
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

    def test_oauth_remote_servers_project_to_claude_and_are_reported_for_codex(self) -> None:
        servers = {
            "events": {"type": "sse", "url": "https://example.test/sse", "oauth": {"clientId": "public-client", "callbackPort": 8080}},
            "portal": {"type": "http", "url": "https://example.test/mcp", "oauth": {"clientId": "public-client"}},
            "home": {"type": "http", "url": "https://example.test/home", "headersHelper": "/usr/local/bin/home-auth"},
            "plain": {"type": "http", "url": "https://example.test/plain"},
        }
        persona = self.persona(mcp={"mcpServers": servers, "agentMcpServers": list(servers)})
        result = self.invoke(persona, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skipped events for codex: sse transport is unsupported\n", result.stdout)
        self.assertIn("skipped portal for codex: oauth config is Claude-only\n", result.stdout)
        self.assertIn("skipped home for codex: headersHelper is Claude-only\n", result.stdout)
        claude, codex = self.adapters()
        self.assertEqual(frontmatter(claude)["mcpServers"], [{name: server} for name, server in servers.items()])
        self.assertEqual(codex["mcp_servers"], {"plain": {"url": "https://example.test/plain"}})
        self.assertNotIn("skipped", self.invoke(persona, "--runtime", "claude").stdout)

    def test_eval_plugin_runs_the_persona_as_main_agent_with_its_guide(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"local": {"command": "tool"}}, "agentMcpServers": ["local"]})
        (persona / "PERSONAS.md").write_text("# Hand-edited copy\n", encoding="utf-8")
        (persona / "user/memory").mkdir(parents=True)
        (persona / "user/memory/MEMORY.md").write_text("Prefers one-pan dinners.\n", encoding="utf-8")
        (persona / "skills/review").mkdir(parents=True)
        (persona / "skills/review/SKILL.md").write_text("---\nname: review\n---\n", encoding="utf-8")
        for case in ("evals/public-case", "user/evals/replay-case", "evals/results/old-run"):
            (persona / case).mkdir(parents=True)
            (persona / case / "prompt.md").write_text("Hi\n", encoding="utf-8")
        self.assertIn("drifted", self.invoke(persona, "--eval-plugin").stderr)
        (persona / "PERSONAS.md").write_text(SYNC.SHARED.read_text(encoding="utf-8"), encoding="utf-8")
        result = self.invoke(persona, "--eval-plugin")
        out = Path(result.stdout.strip())
        self.addCleanup(shutil.rmtree, out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(out.stat().st_mode & 0o777, 0o700)
        agent = (out / "agents/wren-review.md").read_text(encoding="utf-8")
        self.assertEqual(json.loads((out / "settings.json").read_text()), {"agent": "persona:wren-review"})
        self.assertEqual(json.loads((out / ".claude-plugin/plugin.json").read_text())["name"], "persona")
        self.assertLess(agent.index("# Shared persona rules"), agent.index("# Wren Review"))
        self.assertIn("Prefers one-pan dinners.", agent)
        self.assertNotIn("mcpServers", agent)
        self.assertEqual(json.loads((out / ".mcp.json").read_text()), {"mcpServers": {"local": {"type": "stdio", "command": "tool"}}})
        self.assertTrue((out / "skills/review/SKILL.md").is_file())
        self.assertTrue((out / "evals/public-case/prompt.md").is_file())
        self.assertFalse((out / "evals/private").exists())
        self.assertFalse((out / "evals/results").exists())
        private = Path(self.invoke(persona, "--eval-plugin", "--with-private").stdout.strip())
        self.addCleanup(shutil.rmtree, private)
        self.assertTrue((private / "evals/private/replay-case/prompt.md").is_file())
        self.assertFalse(self.claude.exists() or self.codex.exists())

    def test_allowlist_without_mcp_json_fails(self) -> None:
        persona = self.persona()
        (persona / ".agent-mcp.json").write_text('["local"]', encoding="utf-8")
        result = self.invoke(persona)
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing from .mcp.json: local", result.stderr)

    def test_unselected_servers_are_not_projected(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"private": {"command": "tool"}}})
        self.assertEqual(self.invoke(persona, "--apply").returncode, 0)
        claude, codex = self.adapters()
        self.assertNotIn("mcpServers", frontmatter(claude))
        self.assertNotIn("mcp_servers", codex)

    def test_serialization_preserves_quoted_values(self) -> None:
        name = "weather"
        description = 'A 雪 reviewer: "careful" # always'
        persona = self.persona(mcp={"mcpServers": {name: {"command": "tool", "env": {"PLAIN.KEY": "value"}}}, "agentMcpServers": [name]})
        (persona / "AGENTS.md").write_text(f"# Wren\n\n> {description}\n", encoding="utf-8")
        self.assertEqual(self.invoke(persona, "--apply").returncode, 0)
        claude, codex = self.adapters()
        self.assertEqual(frontmatter(claude)["description"], description)
        self.assertEqual(frontmatter(claude)["mcpServers"][0][name]["env"], {"PLAIN.KEY": "value"})
        self.assertEqual(codex["mcp_servers"][name]["env"], {"PLAIN.KEY": "value"})

    def test_rejects_invalid_mcp_declarations(self) -> None:
        cases = {
            "unknown key": {"mcpServers": {"a": {"command": "tool"}}, "codexMcpServers": ["a"]},
            "missing server": {"mcpServers": {}, "agentMcpServers": ["missing"]},
            "duplicate name": {"mcpServers": {"a": {"command": "tool"}}, "agentMcpServers": ["a", "a"]},
            "dotted name": {"mcpServers": {"a.b": {"command": "tool"}}, "agentMcpServers": ["a.b"]},
            "unsupported transport": {"mcpServers": {"a": {"type": "ws", "url": "https://example.test"}}, "agentMcpServers": ["a"]},
            "unknown oauth key": {"mcpServers": {"a": {"type": "sse", "url": "https://example.test", "oauth": {"scope": "read"}}}, "agentMcpServers": ["a"]},
            "string callback port": {"mcpServers": {"a": {"type": "http", "url": "https://example.test", "oauth": {"callbackPort": "8080"}}}, "agentMcpServers": ["a"]},
            "relative headers helper": {"mcpServers": {"a": {"type": "http", "url": "https://example.test", "headersHelper": "auth.sh"}}, "agentMcpServers": ["a"]},
            "headers helper with args": {"mcpServers": {"a": {"type": "http", "url": "https://example.test", "headersHelper": "/bin/auth --token x"}}, "agentMcpServers": ["a"]},
            "non-string env": {"mcpServers": {"a": {"command": "tool", "env": {"COUNT": 3}}}, "agentMcpServers": ["a"]},
            "extra field": {"mcpServers": {"a": {"command": "tool", "cwd": "/tmp"}}, "agentMcpServers": ["a"]},
            "not an object": [],
        }
        for index, (label, payload) in enumerate(cases.items()):
            with self.subTest(label):
                result = self.invoke(self.persona(f"wren-{index}", payload), "--apply")
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr.startswith("error: "))
        self.assertFalse(self.claude.exists() or self.codex.exists())

    def test_rejects_credentials(self) -> None:
        cases = {
            "literal env": ({"command": "tool", "env": {"TOKEN": "literal"}}, "credential literal"),
            "secret key": ({"command": "tool", "env": {"SECRET_KEY": "literal"}}, "credential literal"),
            "aws secret": ({"command": "tool", "env": {"AWS_SECRET_ACCESS_KEY": "literal"}}, "credential literal"),
            "password hash": ({"command": "tool", "env": {"PASSWORD_HASH": "literal"}}, "credential literal"),
            "numeric pin": ({"command": "tool", "env": {"SECRET_PIN": "123456"}}, "credential literal"),
            "path-shaped secret": ({"command": "tool", "env": {"TOKEN": "/c2VjcmV0"}}, "credential literal"),
            "token-shaped arg": ({"command": "tool", "args": ["sk-" + "x" * 16]}, "credential literal"),
            "url userinfo": ({"type": "http", "url": "https://user:password@example.test/mcp"}, "must not contain credentials"),
            "encoded userinfo": ({"type": "http", "url": "https://user%3Apassword@example.test/mcp"}, "must not contain credentials"),
            "query token": ({"type": "http", "url": "https://example.test/mcp?token=value"}, "credential parameters"),
            "encoded query key": ({"type": "http", "url": "https://example.test/mcp?api%5Fkey=value"}, "credential parameters"),
            "fragment secret": ({"type": "http", "url": "https://example.test/mcp#secret=value"}, "credential parameters"),
            "telegram bot token": ({"type": "http", "url": "https://api.example.test/bot123456:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw/mcp"}, "token-like path segment"),
            "letters-only token": ({"type": "http", "url": "https://example.test/mcp/AbCdEfGhIjKlMnOpQrSt"}, "token-like path segment"),
            "private path": ({"type": "http", "url": "http://192.0.2.10:9584/private_AbCdEfGhIjKlMnOp"}, "token-like path segment"),
            "lowercase token": ({"type": "http", "url": "https://example.test/s/k3j9x2m8q7w1z5v4n6b0p2r8/mcp"}, "token-like path segment"),
            "encoded path": ({"type": "http", "url": "https://example.test/mcp%2Fsecret"}, "token-like path segment"),
            "base64url path token": ({"type": "http", "url": "https://example.test/mcp/Ab1cD2eF_Gh3iJ4kL_Mn5oP6qR_St7uV8wX"}, "token-like path segment"),
            "path token in arg": ({"command": "npx", "args": ["mcp-remote", "https://example.test/s/bXpHk2LqW9vNrT4sYcZaDeFg/mcp"]}, "token-like path segment"),
            "oauth client secret": ({"type": "sse", "url": "https://example.test/sse", "oauth": {"clientId": "id", "clientSecret": "literal"}}, "clientSecret"),
            "referenced client secret": ({"type": "sse", "url": "https://example.test/sse", "oauth": {"clientSecret": "${CLIENT_SECRET}"}}, "clientSecret"),
        }
        for index, (label, (server, message)) in enumerate(cases.items()):
            with self.subTest(label):
                result = self.invoke(self.persona(f"wren-{index}", {"mcpServers": {"a": server}, "agentMcpServers": ["a"]}))
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)

    def test_readable_url_paths_are_accepted(self) -> None:
        paths = ("/streamable-http-2025-03-26", "/mcp-server-google-workspace-v2", "/sentry-mcp-2024-v2-eu1", "/mcp", "/mcp/vault", "/sse", "/", "")
        servers = {f"s{index}": {"type": "http", "url": f"https://example.test{path}"} for index, path in enumerate(paths)}
        result = self.invoke(self.persona(mcp={"mcpServers": servers, "agentMcpServers": list(servers)}), "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_settings_that_mention_credentials_are_not_credentials(self) -> None:
        server = {"command": "tool", "env": {"REDACT_SECRETS": "true", "API_TOKEN": "${API_TOKEN}"}}
        result = self.invoke(self.persona(mcp={"mcpServers": {"a": server}, "agentMcpServers": ["a"]}), "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_refuses_unowned_and_other_persona_files_before_writing(self) -> None:
        persona = self.persona()
        manual = self.codex / "agents/wren-review.toml"
        manual.parent.mkdir(parents=True)
        manual.write_text("manual = true\n", encoding="utf-8")
        result = self.invoke(persona, "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("move aside", result.stderr)
        self.assertFalse(self.claude.exists())
        manual.write_text(f'{SYNC.MARKER}\n{SYNC.SOURCE}"/elsewhere/AGENTS.md"\n', encoding="utf-8")
        self.assertEqual(self.invoke(persona, "--apply").returncode, 2)
        manual.unlink()
        self.assertEqual(self.invoke(self.persona("Wren Review"), "--apply").returncode, 0)
        self.assertEqual(self.invoke(persona, "--apply").returncode, 2)

    def test_single_runtime_touches_only_its_home(self) -> None:
        persona = self.persona()
        self.assertEqual(self.invoke(persona, "--runtime", "claude", "--apply").returncode, 0)
        self.assertFalse(self.codex.exists())
        self.assertEqual(self.invoke(persona, "--runtime", "codex", "--apply").returncode, 0)
        self.assertTrue((self.codex / "agents/wren-review.toml").is_file())

    def test_codex_home_defaults_to_environment(self) -> None:
        persona = self.persona()
        command = ("python3", str(SCRIPT), "--persona", str(persona), "--runtime", "codex")
        result = subprocess.run(command, text=True, capture_output=True, check=False, env={"CODEX_HOME": str(self.codex), "HOME": str(self.root)})
        self.assertIn(f"drift {self.codex / 'agents/wren-review.toml'}", result.stdout)

    def folder(self, persona: Path, text: str | None = None, shared: str | None = None) -> Path:
        """Write the persona's .codex/config.toml and, optionally, the global Codex config."""
        if shared is not None:
            self.codex.mkdir(parents=True, exist_ok=True)
            (self.codex / "config.toml").write_text(shared, encoding="utf-8")
        path = persona / ".codex/config.toml"
        if text is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return path

    def test_folder_codex_config_projects_allowlisted_servers_only(self) -> None:
        servers = {
            "local": {"command": "tool", "args": ["serve"]},
            "remote": {"type": "http", "url": "https://example.test/mcp"},
            "ob": {"type": "http", "url": "http://127.0.0.1:3210/mcp"},
            "unlisted": {"command": "private"},
        }
        persona = self.persona(mcp={"mcpServers": servers, "agentMcpServers": ["local", "remote", "ob"]})
        path = self.folder(persona, (
            "# Persona settings.\nsandbox_mode = \"workspace-write\"\n\n[mcp_servers]\n"
            "  [mcp_servers.stale]\n    command = \"old\"\n  [mcp_servers.ob]\n    url = \"http://old/mcp\"\n"
            "  [mcp_servers.mise]\n    command = \"mise\"\n\n# Plugins stay.\n[plugins.\"kit@market\"]\nenabled = true\n"
        ), shared='[mcp_servers.ob]\nurl = "http://127.0.0.1:3210/mcp"\n[mcp_servers.mise]\ncommand = "mise"\n')
        report = self.invoke(persona, "--runtime", "codex")
        self.assertEqual(report.returncode, 1, report.stderr)
        self.assertIn(f"drift {path}\n", report.stdout)
        self.assertIn(f"skipped ob for {path}: defined in {self.codex / 'config.toml'}\n", report.stdout)
        self.assertEqual(self.invoke(persona, "--runtime", "codex", "--apply").returncode, 0)
        text = path.read_text(encoding="utf-8")
        config = tomllib.loads(text)
        self.assertEqual(config["mcp_servers"], {"local": {"command": "tool", "args": ["serve"]}, "remote": {"url": "https://example.test/mcp"}})
        self.assertEqual(config["sandbox_mode"], "workspace-write")
        self.assertEqual(config["plugins"], {"kit@market": {"enabled": True}})
        self.assertIn("# Persona settings.", text)
        self.assertIn("# Plugins stay.\n[plugins.", text)
        self.assertIn("ob", tomllib.loads((self.codex / "agents/wren-review.toml").read_text())["mcp_servers"])
        clean = self.invoke(persona, "--runtime", "codex")
        self.assertEqual(clean.returncode, 0, clean.stdout)
        self.assertIn(f"current {path}\n", clean.stdout)

    def test_folder_codex_config_keeps_codex_variants_and_global_overrides(self) -> None:
        servers = {
            "home": {"type": "http", "url": "https://example.test/home", "headersHelper": "/usr/local/bin/home-auth"},
            "music": {"type": "http", "url": "https://example.test/music", "headersHelper": "/usr/local/bin/music-auth"},
        }
        persona = self.persona(mcp={"mcpServers": servers, "agentMcpServers": ["home"]})
        path = self.folder(persona, (
            '[mcp_servers.home]\nurl = "https://example.test/home"\nhttp_headers_helper = "/usr/local/bin/home-auth"\n'
            '[mcp_servers.home.env]\nMODE = "read"\n'
            '[mcp_servers.music]\nurl = "https://example.test/music"\nhttp_headers_helper = "/usr/local/bin/music-auth"\n'
            '[mcp_servers.mise]\nenabled = false\n[mcp_servers.stale]\ncommand = "old"\n'
        ), shared='[mcp_servers.mise]\ncommand = "mise"\n')
        self.assertEqual(self.invoke(persona, "--runtime", "codex", "--apply").returncode, 0)
        self.assertEqual(tomllib.loads(path.read_text(encoding="utf-8"))["mcp_servers"], {
            "home": {"url": "https://example.test/home", "http_headers_helper": "/usr/local/bin/home-auth", "env": {"MODE": "read"}},
            "music": {"url": "https://example.test/music", "http_headers_helper": "/usr/local/bin/music-auth"},
            "mise": {"enabled": False},
        })
        self.assertIn(f"current {path}", self.invoke(persona, "--runtime", "codex").stdout)

    def test_folder_codex_config_formatting_only_differences_are_current(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"local": {"command": "tool", "args": ["serve"]}}, "agentMcpServers": ["local"]})
        text = "sandbox_mode = 'read-only'\n\n[mcp_servers]\n  [mcp_servers.local]\n    args = [ 'serve' ]\n    command = 'tool'\n"
        path = self.folder(persona, text)
        report = self.invoke(persona, "--runtime", "codex", "--apply")
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertIn(f"current {path}\n", report.stdout)
        self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_claude_runtime_leaves_folder_codex_config_alone(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"local": {"command": "tool"}}, "agentMcpServers": ["local"]})
        text = '[mcp_servers.stale]\ncommand = "old"\n'
        path = self.folder(persona, text)
        result = self.invoke(persona, "--runtime", "claude", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(".codex", result.stdout)
        self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_folder_codex_config_refuses_url_path_secrets(self) -> None:
        tokens = ("bot123456:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw", "Ab1cD2eF_Gh3iJ4kL_Mn5oP6qR_St7uV8wX")
        for index, secret in enumerate(tokens):
            with self.subTest(secret):
                url = f"https://hooks.example.test/services/T0001/{secret}"
                persona = self.persona(f"wren-hook-{index}", {"mcpServers": {"hook": {"type": "http", "url": url}}, "agentMcpServers": ["hook"]})
                text = '[mcp_servers.stale]\ncommand = "old"\n'
                path = self.folder(persona, text)
                result = self.invoke(persona, "--apply")
                self.assertEqual(result.returncode, 2)
                self.assertIn("MCP hook: HTTP url must not contain a token-like path segment", result.stderr)
                self.assertEqual(path.read_text(encoding="utf-8"), text)
                self.assertFalse(self.claude.exists() or self.codex.exists())
                # A hand-written Codex variant with a secret in its URL path is dropped, never written back.
                variant = self.persona(f"wren-variant-{index}", {"mcpServers": {"home": {"type": "http", "url": "https://example.test/home", "headersHelper": "/bin/auth"}}})
                path = self.folder(variant, f'[mcp_servers.home]\nurl = "{url}"\n')
                result = self.invoke(variant, "--runtime", "codex", "--apply")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"skipped home for {path}: HTTP url must not contain a token-like path segment", result.stdout)
                self.assertNotIn(secret, path.read_text(encoding="utf-8"))
                shutil.rmtree(self.codex)

    def test_folder_codex_config_keeps_every_non_mcp_byte(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"local": {"command": "tool"}}, "agentMcpServers": ["local"]})
        prefix = '# Top comment\n\nsandbox_mode = "workspace-write"\n\n\n'
        mcp = '[mcp_servers.stale]\ncommand = "old"\n# Between MCP tables.\n\n[mcp_servers.local]\ncommand = "older"\n'
        suffix = '\n# Plugins stay.\n\n[plugins."kit@market"]\nenabled = true # inline\n\n# Trailing comment.\n'
        path = self.folder(persona, prefix + mcp + suffix)
        self.assertEqual(self.invoke(persona, "--runtime", "codex", "--apply").returncode, 0)
        tables = SYNC.codex_tables({"local": {"type": "stdio", "command": "tool"}})
        self.assertEqual(path.read_text(encoding="utf-8"), prefix + "# Between MCP tables.\n\n" + suffix + tables)

    def test_folder_codex_config_keeps_inline_global_overrides(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"local": {"command": "tool"}}, "agentMcpServers": ["local"]})
        path = self.folder(persona, '[mcp_servers]\nmise = { enabled = false }\nstale = { command = "old" }\n',
                           shared='[mcp_servers.mise]\ncommand = "mise"\n')
        result = self.invoke(persona, "--runtime", "codex", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("[mcp_servers]\nmise = { enabled = false }\n"))
        self.assertEqual(tomllib.loads(text)["mcp_servers"], {"mise": {"enabled": False}, "local": {"command": "tool"}})
        self.assertIn(f"current {path}", self.invoke(persona, "--runtime", "codex").stdout)

    def test_folder_codex_config_ignores_headers_inside_multiline_strings(self) -> None:
        persona = self.persona(mcp={"mcpServers": {"local": {"command": "tool"}}, "agentMcpServers": ["local"]})
        note = 'note = """\n[mcp_servers.fake]\ncommand = "x"\n"""\nliteral = \'\'\'\n[mcp_servers.other]\n\'\'\'\n'
        path = self.folder(persona, note + '[mcp_servers.stale]\ncommand = "old"\n')
        result = self.invoke(persona, "--runtime", "codex", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(note))
        config = tomllib.loads(text)
        self.assertEqual(config["note"], '[mcp_servers.fake]\ncommand = "x"\n')
        self.assertEqual(config["mcp_servers"], {"local": {"command": "tool"}})

    def test_failed_replace_preserves_destination_and_cleans_temporary_file(self) -> None:
        target = self.root / "agent.toml"
        target.write_text("original")
        with patch.object(Path, "replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                SYNC.write(target, "replacement")
        self.assertEqual(target.read_text(), "original")
        self.assertEqual(list(self.root.iterdir()), [target])


if __name__ == "__main__": unittest.main(verbosity=2)
