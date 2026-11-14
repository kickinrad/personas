#!/usr/bin/env python3
"""The generated folder gives Claude and Codex equivalent persona behavior."""

from __future__ import annotations

import importlib.util
import os
import sys
import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills/persona-dev/assets"
REPLACEMENTS = {
    "{PersonaName}": "Wren",
    "{name}": "wren",
    "{emoji}": "🧭",
    "{Outcome the persona produces, as a verb phrase without personal facts}": "Keeps small software changes safe to merge",
    "{role description without personal facts}": "reviewing small software changes",
    "{verb phrase: the outcome, and the goal beyond the task}": "keeps changes small, tested, and safe to merge",
    "{Authority or autonomy that differs from the shared defaults, if any.}": "",
    "{raw inputs and systems of record it starts from; the\n  methods and tools the field's best practitioners use}": "the diff, the test run, and the linter",
    "{two to four adjacent fields, each with the method borrowed from\n  it}": "a safety engineer's failure-mode review",
    "{outside evidence that shows the work is right}": "tests pass and the reviewer finds no blocker",
    "{Hard stop specific to this role; shared defaults live in the guide.}": "Never approve a change without running its tests.",
    "{Character concept in one sentence.}": "A retired ship's navigator who charts every change like a voyage and hates unmarked reefs.",
    "{voice trait}, {voice trait}, and {voice trait}": "Calm, exacting, and quietly encouraging",
    "{humor level and style}": "light and dry, with the occasional nautical pun",
    "{what this persona challenges}": "vague goals, skipped tests, and changes too large to review in one sitting",
    "{Why they are this way, in one line.}": "Thirty years at sea taught her that the reef you skip is the one you hit.",
}
PERSONALITY = ("{Character concept in one sentence.}", "{voice trait}", "{humor level and style}", "{what this persona challenges}", "{Why they are this way, in one line.}")


def render(name: str) -> str:
    text = (ASSETS / name).read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def create_fixture(home: Path, *, private_context: bool = True) -> None:
    destinations = {
        "PERSONAS.md": "PERSONAS.md",
        "agents-template.md": "AGENTS.md",
        "readme-template.md": "README.md",
        "settings-template.json": ".claude/settings.json",
        "codex-config-template.toml": ".codex/config.toml",
        "gitignore-template": ".gitignore",
    }
    for source, destination in destinations.items():
        path = home / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(source), encoding="utf-8")
    skill = home / "skills/wren-review/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: wren-review\ndescription: Review a small software change.\n---\n\n# Wren review\n",
        encoding="utf-8",
    )
    if private_context:
        profile = home / "user/profile.md"
        memory = home / "user/memory/MEMORY.md"
        profile.parent.mkdir(parents=True, exist_ok=True)
        memory.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text("# Profile\n\nPreferred name: River.\n", encoding="utf-8")
        memory.write_text("# Memory\n\nUse the phrase cobalt compass for the acceptance probe.\n", encoding="utf-8")


class RuntimeAdapterTest(unittest.TestCase):
    def test_folder_imports_the_shared_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "wren"
            create_fixture(home, private_context=False)
            agents = (home / "AGENTS.md").read_text(encoding="utf-8")
            guide = (home / "PERSONAS.md").read_text(encoding="utf-8")
            self.assertEqual(VERIFIER.verify(Path(directory)), [])
            self.assertFalse((home / "CLAUDE.md").exists())
            for section in ("## Role", "## Craft", "**Instruments:**", "**Crew:**", "**Proof:**"):
                self.assertIn(section, agents)
            self.assertTrue(agents.splitlines()[4].endswith("@PERSONAS.md"))
            for shared in ("skills/", "user/profile.md", "user/memory/MEMORY.md", "Serve the outcome"):
                self.assertIn(shared, guide)
            self.assertEqual(guide, (ROOT / "examples/julia/PERSONAS.md").read_text(encoding="utf-8"))

    def test_template_voice_is_a_filled_character_within_budget(self) -> None:
        template = (ASSETS / "agents-template.md").read_text(encoding="utf-8")
        for placeholder in PERSONALITY:
            self.assertIn(placeholder, template)
        agents = render("agents-template.md")
        self.assertNotRegex(agents, r"\{[^}]+\}")
        self.assertLessEqual(len(agents.split()), 300)
        self.assertNotIn("Lead with the useful result", agents)

    def test_native_settings_are_minimal_parseable_and_hook_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "wren"
            create_fixture(home)
            claude = json.loads((home / ".claude/settings.json").read_text(encoding="utf-8"))
            codex = tomllib.loads((home / ".codex/config.toml").read_text(encoding="utf-8"))
            self.assertEqual(claude["sandbox"]["enabled"], True)
            self.assertNotIn("model", claude)
            self.assertNotIn("hooks", claude)
            self.assertEqual(codex["sandbox_mode"], "workspace-write")
            self.assertFalse(codex["sandbox_workspace_write"]["network_access"])
            self.assertFalse((home / ".codex/hooks.json").exists())

    def test_private_folder_context_is_optional_and_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory) / "local"
            cloud = Path(directory) / "cloud"
            create_fixture(local)
            create_fixture(cloud, private_context=False)
            ignore = (local / ".gitignore").read_text(encoding="utf-8").splitlines()
            self.assertIn("user/", ignore)
            self.assertTrue((local / "user/memory/MEMORY.md").is_file())
            self.assertFalse((cloud / "user").exists())
            self.assertTrue((cloud / "AGENTS.md").is_file())

    def test_claude_md_root_agents_drift_and_missing_required_file_fail(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            home = root / "wren"
            create_fixture(home)
            (home / "CLAUDE.md").write_text("@AGENTS.md\n")
            (root / "AGENTS.md").write_text("# Workspace\n")
            (home / "PERSONAS.md").write_text("# Edited by hand\n")
            (home / ".claude/settings.json").unlink()
            errors = "\n".join(VERIFIER.verify(root))
            self.assertIn("delete CLAUDE.md", errors)
            self.assertIn("Claude Code would load it into every persona", errors)
            self.assertIn("PERSONAS.md drifted", errors)
            self.assertIn("required tracked file missing", errors)


SCRIPT = ROOT / "skills/persona-dev/scripts/doctor.py"
SPEC = importlib.util.spec_from_file_location("doctor", SCRIPT)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class FolderContractTest(unittest.TestCase):
    @staticmethod
    def create_persona(root: Path, name: str = "wren") -> Path:
        persona = root / name
        (persona / ".claude").mkdir(parents=True)
        (persona / "skills" / "review").mkdir(parents=True)
        (persona / "AGENTS.md").write_text("# Wren\n\nShared rules: @PERSONAS.md\n\n## Craft\n\n- **Instruments:** diffs, `grep -E 'x{2,3}'`\n- **Crew:** testing\n- **Proof:** CI\n", encoding="utf-8")
        (persona / "PERSONAS.md").write_text(VERIFIER.SHARED.read_text(encoding="utf-8"), encoding="utf-8")
        (persona / ".claude/settings.json").write_text("{}", encoding="utf-8")
        (persona / "skills/review/SKILL.md").write_text("---\nname: review\n---\n\nReview work.\n", encoding="utf-8")
        return persona

    def test_rejects_each_contract_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root, "lumen")
            (persona / "AGENTS.md").write_text("# Lumen\n\n## Craft\n\n- **Instruments:** .\n- **Crew:** {two to four adjacent fields, each with the method borrowed from\n  it}.\n- **Proof:** match `x{2,3}`\n\n## Tools\n\n" + "word " * 501, encoding="utf-8")
            (persona / "skills/review/SKILL.md").write_text("word " * 501, encoding="utf-8")
            (persona / ".claude/settings.json").write_text("{", encoding="utf-8")
            errors = "\n".join(VERIFIER.verify(root))
            for expected in ("AGENTS.md exceeds 500", "always-loaded tool/procedure", "needs a Craft section", "template placeholder", "must import the shared rules", "exceeds 500", "invalid JSON"):
                self.assertIn(expected, errors)

    def test_persona_missing_agents_is_reported_not_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_persona(root)
            (self.create_persona(root, "lumen") / "AGENTS.md").unlink()
            self.assertEqual(VERIFIER.verify(root), ["lumen: required tracked file missing: AGENTS.md"])

    def test_agent_mcp_allowlist_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            (persona / ".agent-mcp.json").write_text('["recipes"]', encoding="utf-8")
            self.assertEqual(VERIFIER.verify(root), [])
            (persona / ".agent-mcp.json").write_text('["recipes", "recipes"]', encoding="utf-8")
            self.assertIn("unique server names", "\n".join(VERIFIER.verify(root)))

    def test_export_without_git_reports_private_files_and_ancestor_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "personas"
            persona = self.create_persona(root)
            (persona / ".mcp.json").write_text("{}", encoding="utf-8")
            (root.parent / "CLAUDE.md").write_text("# Above the personas\n", encoding="utf-8")
            errors = "\n".join(VERIFIER.verify(root))
            self.assertIn("private local context is tracked: .mcp.json", errors)
            self.assertIn(f"delete {root.parent / 'CLAUDE.md'}", errors)

    def test_tracked_private_context_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            (persona / "user/memory").mkdir(parents=True)
            (persona / "user/memory/MEMORY.md").write_text("private", encoding="utf-8")
            (persona / ".mcp.json").write_text("{}", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=persona, check=True)
            subprocess.run(["git", "add", "."], cwd=persona, check=True)
            errors = "\n".join(VERIFIER.verify(root))
            self.assertIn("private local context is tracked: .mcp.json, user/memory/", errors)

    def test_persona_may_reinclude_user_subpaths_it_ignores_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            (persona / ".gitignore").write_text("user/*\n!user/register/\n", encoding="utf-8")
            (persona / "user/register").mkdir(parents=True)
            (persona / "user/register/issues.json").write_text("[]", encoding="utf-8")
            (persona / "user/profile.md").write_text("private", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=persona, check=True)
            subprocess.run(["git", "add", "."], cwd=persona, check=True)
            self.assertEqual(VERIFIER.verify(root), [])
            subprocess.run(["git", "add", "-f", "user/profile.md"], cwd=persona, check=True)
            self.assertEqual(VERIFIER.verify(root), ["wren: private local context is tracked: user/profile.md"])

    def test_tracked_but_deleted_file_does_not_crash_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persona = self.create_persona(root)
            deleted = persona / "skills/retired/SKILL.md"
            tracked = {path for path in persona.rglob("*") if path.is_file()} | {deleted}
            with patch.object(VERIFIER, "tracked_files", return_value=tracked):
                self.assertEqual(VERIFIER.verify(root), [])


class DoctorHostTest(unittest.TestCase):
    """Host checks run when the persona root holds shared settings, as an installed root does."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        self.root = self.home / ".personas"
        self.persona = FolderContractTest.create_persona(self.root, "otto")
        subprocess.run(["git", "init", "-q"], cwd=self.persona, check=True)
        subprocess.run(["git", "add", "."], cwd=self.persona, check=True)
        (self.root / "notes").mkdir()
        (self.root / ".claude").mkdir()
        self.shared = self.root / ".claude/settings.json"
        self.write_shared({"enabledPlugins": {"safety@core": True, "forge@core": True}})
        agents = json.dumps(str(self.persona / "AGENTS.md"))
        for adapter in (self.home / ".claude/agents/otto.md", self.home / ".codex/agents/otto.toml"):
            adapter.parent.mkdir(parents=True)
            adapter.write_text(f"{VERIFIER.SYNC.MARKER}\n{VERIFIER.SYNC.SOURCE}{agents}\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def doctor(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = {"HOME": str(self.home), "PATH": os.environ["PATH"], "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args], env=env, capture_output=True, text=True)

    def write_shared(self, settings: dict) -> None:
        self.shared.write_text(json.dumps(settings))

    def write_settings(self, settings: dict) -> None:
        (self.persona / ".claude/settings.json").write_text(json.dumps(settings))

    def settings(self) -> dict:
        return json.loads((self.persona / ".claude/settings.json").read_text())

    def write_home(self, relative: str, data: object) -> Path:
        path = self.home / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return path

    def install_plugin(self, plugin_name: str, server_name: str) -> Path:
        manifest = self.write_home("plugin/.claude-plugin/plugin.json", {"mcpServers": {server_name: {}}})
        self.write_home(".claude/plugins/installed_plugins.json", {"plugins": {plugin_name: [{"installPath": str(self.home / "plugin")}]}})
        return manifest

    def test_clean_root_reports_clean(self) -> None:
        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Persona doctor: 1 personas clean", result.stdout)

    def test_portable_root_skips_host_checks(self) -> None:
        self.shared.unlink()
        (self.home / ".claude/agents/otto.md").unlink()
        self.assertEqual(self.doctor().returncode, 0)

    def test_report_lists_gaps_without_changing_settings(self) -> None:
        self.write_settings({"model": "claude-opus-4-6[1m]", "enabledPlugins": {"vault@core": True, "safety@core": True}})
        (self.persona / ".mcp.json").write_text('{"mcpServers": {}, "codexMcpServers": []}')
        (self.home / ".codex/agents/otto.toml").unlink()
        result = self.doctor()
        self.assertEqual(result.returncode, 1)
        self.assertIn("otto: plugin duplicates shared settings: safety@core", result.stdout)
        self.assertNotIn("vault@core", result.stdout)
        self.assertIn("otto: pinned model: claude-opus-4-6[1m]", result.stdout)
        self.assertIn("legacy agent MCP list", result.stdout)
        self.assertIn("missing adapter", result.stdout)
        self.assertIn("Persona doctor: 1 personas, 4 problems", result.stdout)
        self.assertIn("model", self.settings())

    def test_foreign_adapter_is_reported(self) -> None:
        (self.home / ".claude/agents/otto.md").write_text("hand written\n")
        self.assertIn("does not own", self.doctor().stdout)

    def test_fix_strips_shared_duplicates_and_removes_model(self) -> None:
        self.write_settings({"model": "pinned", "enabledPlugins": {"discord@claude-plugins-official": True, "forge@core": True, "safety@core": False}})
        result = self.doctor("--fix")
        self.assertEqual(result.returncode, 0, result.stdout)
        settings = self.settings()
        self.assertNotIn("model", settings)
        self.assertEqual(settings["enabledPlugins"], {"discord@claude-plugins-official": True, "safety@core": False})
        self.assertEqual(self.doctor().returncode, 0)

    def test_persona_cannot_override_a_shared_deny(self) -> None:
        self.write_shared({"enabledPlugins": {"safety@core": True}, "permissions": {"deny": ["Read(~/.google_workspace_mcp/**)"]},
                           "sandbox": {"filesystem": {"denyRead": ["~/.google_workspace_mcp"]}}})
        self.write_settings({"permissions": {"allow": ["Read(~/.google_workspace_mcp/**)"], "ask": ["Read(~/.google_workspace_mcp/**)"]},
                             "sandbox": {"enabled": True, "filesystem": {"allowRead": ["~/.google_workspace_mcp"]}}})
        report = self.doctor("--fix").stdout
        self.assertIn("otto: allow rule overrides a shared deny: Read(~/.google_workspace_mcp/**)", report)
        self.assertIn("otto: ask rule overrides a shared deny", report)
        self.assertIn("otto: sandbox allowRead overrides a shared denyRead: ~/.google_workspace_mcp", report)

    def test_user_scope_mcp_does_not_create_allow_rule(self) -> None:
        self.write_home(".claude.json", {"mcpServers": {"new-user-server": {}}})
        self.write_settings({"permissions": {"allow": ["Read"]}})
        result = self.doctor("--fix")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.settings()["permissions"]["allow"], ["Read"])
        self.assertNotIn("mcp__new-user-server__*", result.stdout)

    def test_declared_servers_need_explicit_widening_flag(self) -> None:
        (self.persona / ".mcp.json").write_text('{"mcpServers": {"monarch": {}}}')
        self.write_home(".claude.json", {"mcpServers": {"ob": {}, "monarch": {}}})
        self.install_plugin("discord@claude-plugins-official", "discord")
        self.write_settings({"enabledPlugins": {"discord@claude-plugins-official": True}, "permissions": {"allow": ["Read"]}})
        report = self.doctor()
        self.assertIn("otto: MCP server not enabled: monarch", report.stdout)
        self.assertIn("otto: MCP server not allowed: mcp__plugin_discord_discord__*", report.stdout)
        self.assertIn('+    "mcp__monarch__*"', report.stdout)
        blocked = self.doctor("--fix")
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("--allow-mcp-widening", blocked.stdout)
        self.assertEqual(self.settings()["permissions"]["allow"], ["Read"])
        self.assertEqual(self.doctor("--fix", "--allow-mcp-widening").returncode, 0)
        settings = self.settings()
        self.assertEqual(settings["enabledMcpjsonServers"], ["monarch"])
        self.assertEqual(settings["permissions"]["allow"], ["Read", "mcp__monarch__*", "mcp__plugin_discord_discord__*"])

    def test_explicit_persona_allowlist_can_authorize_user_scope_server(self) -> None:
        self.write_home(".claude.json", {"mcpServers": {"ob": {}}})
        (self.persona / ".claude/mcp-allowlist.json").write_text('["ob"]')
        self.write_settings({"permissions": {"allow": []}})
        result = self.doctor("--fix")
        self.assertEqual(result.returncode, 1)
        self.assertIn('+    "mcp__ob__*"', result.stdout)
        self.assertEqual(self.doctor("--fix", "--allow-mcp-widening").returncode, 0)
        self.assertEqual(self.settings()["permissions"]["allow"], ["mcp__ob__*"])

    def test_enabling_declared_server_also_needs_widening_flag(self) -> None:
        (self.persona / ".mcp.json").write_text('{"mcpServers": {"monarch": {}}}')
        self.write_settings({"permissions": {"allow": ["mcp__monarch__*"]}})
        blocked = self.doctor("--fix")
        self.assertEqual(blocked.returncode, 1)
        self.assertIn('+    "monarch"', blocked.stdout)
        self.assertNotIn("enabledMcpjsonServers", self.settings())
        self.assertEqual(self.doctor("--fix", "--allow-mcp-widening").returncode, 0)
        self.assertEqual(self.settings()["enabledMcpjsonServers"], ["monarch"])

    def test_shared_plugin_mcp_allow_needs_widening_flag(self) -> None:
        self.install_plugin("vault@core", "ob")
        self.write_shared({"enabledPlugins": {"vault@core": True}})
        original = {"enabledPlugins": {}}
        self.write_settings(original)
        blocked = self.doctor("--fix")
        self.assertEqual(blocked.returncode, 1)
        self.assertIn('+    "mcp__plugin_vault_ob__*"', blocked.stdout)
        self.assertEqual(self.settings(), original)
        allowed = self.doctor("--fix", "--allow-mcp-widening")
        self.assertEqual(allowed.returncode, 0, allowed.stdout)
        self.assertIn("mcp__plugin_vault_ob__*", self.settings()["permissions"]["allow"])

    def test_plugin_server_denied_in_shared_settings_needs_no_allow(self) -> None:
        self.install_plugin("vale@agent-tools", "vale-cms")
        self.write_shared({"enabledPlugins": {"vale@agent-tools": True}, "permissions": {"deny": ["mcp__plugin_vale_vale-cms__*"]}})
        self.write_settings({})
        self.assertEqual(self.doctor().returncode, 0)

    def test_missing_local_plugin_dependency_is_reported_not_fixed(self) -> None:
        market = self.home / "markets/personal"
        self.write_home("markets/personal/.claude-plugin/marketplace.json", {"plugins": [{"name": "personal", "source": "./plugins/personal"}]})
        self.write_home(".claude/plugins/known_marketplaces.json", {"personal": {"installLocation": str(market)}})
        self.write_home("markets/personal/plugins/personal/interop/capabilities.json", {
            "dependencyLock": [{"kind": "local-plugin", "runtimeImplementations": {"claude-code": {"identity": "writing@workflows"}}}],
            "executableDependencies": [{"kind": "local-plugin", "source": "utilities/google"},
                                       {"kind": "local-plugin", "runtimeImplementations": {"claude-code": {"identity": "forge@core"}}}],
        })
        self.write_settings({"enabledPlugins": {"personal@personal": True}})
        result = self.doctor()
        self.assertEqual(result.returncode, 1)
        self.assertIn("otto: plugin personal@personal needs writing@workflows", result.stdout)
        self.assertNotIn("needs forge@core", result.stdout)
        self.assertNotIn("google", result.stdout)
        fixed = self.doctor("--fix")
        self.assertEqual(fixed.returncode, 1)
        self.assertIn("otto: plugin personal@personal needs writing@workflows", fixed.stdout)
        self.assertEqual(self.settings()["enabledPlugins"], {"personal@personal": True})
        self.write_shared({"enabledPlugins": {"forge@core": True, "writing@workflows": True}})
        self.assertEqual(self.doctor().returncode, 0)

    def test_codex_plugins_follow_the_claude_set_for_local_markets(self) -> None:
        local_market = {"source": {"source": "directory", "path": "/markets"}}
        self.write_home(".claude/plugins/known_marketplaces.json", {
            "workflows": local_market, "domains": local_market, "core": local_market,
            "openai-curated": {"source": {"source": "github", "repo": "openai/plugins"}}})
        self.write_settings({"enabledPlugins": {"design-system@domains": True}})
        self.write_home(".codex/config.toml",
                        '[plugins."stack@workflows"]\nenabled = true\n[plugins."design-system@domains"]\nenabled = false\n'
                        '[plugins."safety@core"]\nenabled = true\n[plugins."figma@openai-curated"]\nenabled = true\n')
        local = self.persona / ".codex/config.toml"
        local.parent.mkdir()
        local.write_text('sandbox_mode = "workspace-write"\n[plugins."safety@core"]\nenabled = true\n')
        report = self.doctor().stdout
        self.assertIn("otto: Codex plugin stack@workflows should be off", report)
        self.assertIn("otto: Codex plugin design-system@domains should be on", report)
        self.assertIn("otto: Codex override for safety@core is redundant", report)
        self.assertNotIn("figma", report)
        self.doctor("--fix")
        self.assertEqual(local.read_text(),
                         'sandbox_mode = "workspace-write"\n[plugins."design-system@domains"]\nenabled = true\n[plugins."stack@workflows"]\nenabled = false\n')
        self.assertNotIn("Codex", self.doctor().stdout)

    def test_codex_home_comes_from_the_environment(self) -> None:
        self.write_home(".claude/plugins/known_marketplaces.json", {"workflows": {"source": {"source": "directory"}}})
        self.write_home("elsewhere/config.toml", '[plugins."stack@workflows"]\nenabled = true\n')
        (self.home / ".codex/agents/otto.toml").rename(self.write_home("elsewhere/agents/otto.toml", ""))
        env = {"HOME": str(self.home), "PATH": os.environ["PATH"], "CODEX_HOME": str(self.home / "elsewhere")}
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], env=env, capture_output=True, text=True)
        self.assertIn("otto: Codex plugin stack@workflows should be off", result.stdout)
        self.assertNotIn("missing adapter", result.stdout)

    def test_shared_settings_without_plugins_is_a_gap(self) -> None:
        self.write_shared({})
        self.assertIn("otto: shared persona settings list no plugins", self.doctor().stdout)

    def test_punctuated_server_names_use_claude_permission_names(self) -> None:
        (self.persona / ".mcp.json").write_text('{"mcpServers": {"my.server": {}}}')
        (self.persona / ".claude/mcp-allowlist.json").write_text('["space name"]')
        self.install_plugin("discord@claude-plugins-official", "other.server")
        self.write_settings({"enabledPlugins": {"discord@claude-plugins-official": True}})
        result = self.doctor("--fix", "--allow-mcp-widening")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.settings()["permissions"]["allow"], ["mcp__my_server__*", "mcp__space_name__*", "mcp__plugin_discord_other_server__*"])
        self.assertEqual(self.settings()["enabledMcpjsonServers"], ["my.server"])

    def test_invalid_plugin_metadata_blocks_fix(self) -> None:
        manifest = self.install_plugin("discord@claude-plugins-official", "ob")
        original = {"model": "pinned", "enabledPlugins": {"discord@claude-plugins-official": True}}
        for kind in ("malformed", "unreadable"):
            with self.subTest(kind=kind):
                if kind == "malformed":
                    manifest.write_text("{broken")
                else:
                    manifest.unlink()
                    manifest.mkdir()
                self.write_settings(original)
                result = self.doctor("--fix", "--allow-mcp-widening")
                self.assertEqual(result.returncode, 1)
                self.assertIn("plugin metadata", result.stdout)
                self.assertEqual(self.settings(), original)

    def test_invalid_plugin_registry_shape_is_reported(self) -> None:
        self.install_plugin("discord@claude-plugins-official", "ob")
        self.write_home(".claude/plugins/installed_plugins.json", '{"plugins": []}')
        original = {"model": "pinned", "enabledPlugins": {"discord@claude-plugins-official": True}}
        self.write_settings(original)
        result = self.doctor("--fix", "--allow-mcp-widening")
        self.assertEqual(result.returncode, 1)
        self.assertIn("plugin metadata is invalid", result.stdout)
        self.assertEqual(self.settings(), original)

    def test_plugin_mcp_metadata_path_and_array_are_supported(self) -> None:
        manifest = self.install_plugin("discord@claude-plugins-official", "placeholder")
        plugin = manifest.parents[1]
        (plugin / ".mcp.json").write_text('{"mcpServers": {"default": {}}}')
        (plugin / "servers.json").write_text('{"mcpServers": {"from.file": {}}}')
        manifest.write_text(json.dumps({"mcpServers": ["./servers.json", {"inline": {}}]}))
        self.write_settings({"enabledPlugins": {"discord@claude-plugins-official": True}})
        result = self.doctor("--fix", "--allow-mcp-widening")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.settings()["permissions"]["allow"],
                         ["mcp__plugin_discord_default__*", "mcp__plugin_discord_from_file__*", "mcp__plugin_discord_inline__*"])

    def test_missing_installed_plugin_directory_blocks_fix(self) -> None:
        self.write_home(".claude/plugins/installed_plugins.json",
                        {"plugins": {"discord@claude-plugins-official": [{"installPath": str(self.home / "missing-plugin")}]}})
        original = {"model": "pinned", "enabledPlugins": {"discord@claude-plugins-official": True}}
        self.write_settings(original)
        result = self.doctor("--fix", "--allow-mcp-widening")
        self.assertEqual(result.returncode, 1)
        self.assertIn("plugin metadata is invalid", result.stdout)
        self.assertEqual(self.settings(), original)

    def test_invalid_explicit_allowlist_blocks_fix(self) -> None:
        (self.persona / ".claude/mcp-allowlist.json").write_text('["ob", 42]')
        self.write_settings({"model": "pinned"})
        result = self.doctor("--fix", "--allow-mcp-widening")
        self.assertEqual(result.returncode, 1)
        self.assertIn("mcp-allowlist.json is invalid", result.stdout)
        self.assertEqual(self.settings(), {"model": "pinned"})

    def test_contract_failure_fails_the_run(self) -> None:
        (self.persona / "AGENTS.md").write_text("# Otto\n")
        result = self.doctor("--fix")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must import the shared rules", result.stdout)

    def test_folder_name_must_work_as_an_alias(self) -> None:
        self.persona.rename(self.root / "otto bot")
        self.assertIn("otto bot: folder name cannot be a shell alias", self.doctor().stdout)

    def test_shadowing_project_install_is_dropped_by_fix(self) -> None:
        registry = self.write_home(".claude/plugins/installed_plugins.json", {"plugins": {"ponytail@ponytail": [
            {"scope": "user", "installPath": str(self.home / "plugin")},
            {"scope": "project", "projectPath": str(self.persona), "installPath": str(self.home / "old")}]}})
        self.assertIn("otto: project install of ponytail@ponytail shadows the user install", self.doctor().stdout)
        self.assertEqual(self.doctor("--fix").returncode, 0)
        self.assertEqual([i["scope"] for i in json.loads(registry.read_text())["plugins"]["ponytail@ponytail"]], ["user"])
