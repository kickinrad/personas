#!/usr/bin/env python3
"""Central source-staging contract gate for the persona framework."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
MANAGER = PLUGINS / "persona-manager"
DASHBOARD = PLUGINS / "persona-dashboard"
MESH = PLUGINS / "personas-mesh"
EXPECTED_VERSIONS = {
    "persona-manager": "2.0.1",
    "persona-dashboard": "2.0.0",
    "personas-mesh": "1.0.0",
}
def run(
    *args: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd or ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_persona(root: Path, *, local_self_improve: bool = False) -> None:
    for directory in (
        "user/memory",
        ".claude/output-styles",
        ".claude/hooks",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for relative, content in {
        "CLAUDE.md": "# Atlas\n",
        "AGENTS.md": "# Atlas for Codex\n",
        "README.md": "# Atlas\n",
        "user/profile.md": "# Profile\n",
        "user/memory/MEMORY.md": "# Memory\n",
        ".claude/output-styles/atlas.md": "---\nname: Atlas\n---\n",
        ".claude/hooks/public-repo-guard.sh": "#!/usr/bin/env bash\nexit 0\n",
        ".claude-flags": "--setting-sources project,local\n",
        ".framework-version": EXPECTED_VERSIONS["persona-manager"] + "\n",
        ".gitignore": ".mcp.json\n.claude/settings.local.json\n*.local.json\n*.local.md\n",
    }.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    write_json(
        root / ".claude/settings.json",
        {
            "sandbox": {
                "enabled": True,
                "autoAllowBashIfSandboxed": True,
                "filesystem": {
                    "denyRead": ["~/.aws", "~/.ssh", "~/.gnupg", "../"]
                },
            },
            "enabledPlugins": {"persona-manager@personas": True},
        },
    )
    write_json(
        root / ".claude/settings.local.json",
        {
            "autoMemoryDirectory": str((root / "user/memory").resolve()),
            "outputStyle": "Atlas",
        },
    )
    write_json(
        root / "hooks.json",
        {
            "hooks": {
                name: [{"type": "prompt", "prompt": "fixture"}]
                for name in (
                    "PreToolUse",
                    "SessionStart",
                    "Stop",
                    "StopFailure",
                    "PreCompact",
                    "PostCompact",
                )
            }
        },
    )
    if local_self_improve:
        path = root / ".claude/skills/self-improve/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: self-improve\n---\n", encoding="utf-8")


def rule_matches(rule: dict[str, object], prompt: str) -> bool:
    triggers = rule["promptTriggers"]
    assert isinstance(triggers, dict)
    folded = prompt.casefold()
    keywords = triggers.get("keywords", [])
    patterns = triggers.get("intentPatterns", [])
    return any(str(word).casefold() in folded for word in keywords) or any(
        re.search(str(pattern), prompt, re.IGNORECASE) for pattern in patterns
    )


class FrameworkContractTest(unittest.TestCase):
    def test_exact_release_units_and_final_versions(self) -> None:
        plugin_names = sorted(path.name for path in PLUGINS.iterdir() if path.is_dir())
        self.assertEqual(plugin_names, sorted(EXPECTED_VERSIONS))
        marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            sorted(item["name"] for item in marketplace["plugins"]), plugin_names
        )
        for name, expected in EXPECTED_VERSIONS.items():
            manifest = json.loads(
                (PLUGINS / name / ".claude-plugin/plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["version"], expected)

    def test_runtime_declarations_are_truthful(self) -> None:
        for name in EXPECTED_VERSIONS:
            capabilities = json.loads(
                (PLUGINS / name / "interop/capabilities.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(capabilities["schemaVersion"], 3)
            runtimes = capabilities["runtimes"]
            self.assertEqual(runtimes["claude-code"]["status"], "native")
            self.assertEqual(runtimes["codex"]["status"], "generated")
            for runtime in ("gemini-cli", "kimi-code"):
                self.assertEqual(runtimes[runtime]["status"], "unsupported")
                self.assertIn("reason", runtimes[runtime])

    def test_trigger_positive_controls_and_isolation(self) -> None:
        cases = {
            "create a persona named atlas": "persona-manager:persona-dev",
            "check persona drift for atlas": "persona-manager:persona-update",
            "time for a self-audit": "persona-manager:self-improve",
            "install a persona dashboard for atlas": "persona-dashboard:install",
            "bootstrap persona sync on this machine": "personas-mesh:setup",
            "show mesh status": "personas-mesh:status",
            "persona sync is broken": "personas-mesh:mesh-doctor",
        }
        rules: dict[str, dict[str, object]] = {}
        for plugin in EXPECTED_VERSIONS:
            data = json.loads(
                (PLUGINS / plugin / "skill-rules.json").read_text(encoding="utf-8")
            )
            for name, rule in data["rules"].items():
                rules[f"{plugin}:{name}"] = rule
        self.assertEqual(set(rules), set(cases.values()))
        for prompt, expected in cases.items():
            matches = [name for name, rule in rules.items() if rule_matches(rule, prompt)]
            self.assertEqual(matches, [expected], f"{prompt!r} matched {matches}")

    def test_validator_uses_fixture_home_and_rejects_local_self_improve(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            valid = base / "valid/atlas"
            invalid = base / "invalid/atlas"
            make_persona(valid)
            make_persona(invalid, local_self_improve=True)
            env = os.environ.copy()
            env["HOME"] = str(base / "home")
            validator = MANAGER / "bin/validate-persona"
            good = run(
                str(validator),
                str(valid),
                "--plugin-root",
                str(MANAGER),
                "--json",
                env=env,
            )
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertEqual(json.loads(good.stdout)["status"], "PASS")
            bad = run(
                str(validator),
                str(invalid),
                "--plugin-root",
                str(MANAGER),
                "--json",
                env=env,
            )
            self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
            self.assertIn(
                "forbidden local duplicate",
                "\n".join(json.loads(bad.stdout)["errors"]),
            )
            self.assertFalse((base / "home/.personas").exists())

    def test_framework_hook_resolves_its_own_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            persona = Path(directory)
            (persona / ".framework-version").write_text("0.0.1\n", encoding="utf-8")
            result = run(
                str(MANAGER / "hooks/framework-version.sh"),
                cwd=persona,
                env={"PATH": os.environ["PATH"], "HOME": str(persona)},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn(
                EXPECTED_VERSIONS["persona-manager"],
                payload["hookSpecificOutput"]["additionalContext"],
            )

    def test_dashboard_is_read_only_and_has_no_shadow_actions(self) -> None:
        paths = [
            DASHBOARD / "README.md",
            DASHBOARD / "skills/install/SKILL.md",
            DASHBOARD / "skills/install/assets/dashboard.html",
        ]
        content = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        for forbidden in ("TASKS.md", "task tracking", "task board", "parseTasks"):
            self.assertNotIn(forbidden, content)
        html = paths[-1].read_text(encoding="utf-8")
        self.assertEqual(html.count("fetch("), 1)
        for source in ("user/profile.md", "user/memory/MEMORY.md", "CLAUDE.md"):
            self.assertIn(source, html)

    def test_mesh_launcher_provenance_and_no_worktree_systemd(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(base / "home"),
                    "PERSONAS_MESH_INSTALL_ROOT": str(base / "install"),
                    "PERSONAS_MESH_LAUNCHER_ROOT": str(base / "launchers"),
                }
            )
            result = run(str(MESH / "bin/install-launchers"), env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            launchers = sorted((base / "launchers").iterdir())
            self.assertEqual(len(launchers), 6)
            for launcher in launchers:
                content = launcher.read_text(encoding="utf-8")
                self.assertIn("# generated-by: personas-mesh", content)
                self.assertIn(
                    f"# source-version: {EXPECTED_VERSIONS['personas-mesh']}", content
                )
                self.assertRegex(content, r"# source-sha256: [0-9a-f]{64}")
                self.assertIn(
                    f"/install/{EXPECTED_VERSIONS['personas-mesh']}/bin/", content
                )
            snapshot = base / f"install/{EXPECTED_VERSIONS['personas-mesh']}"
            snapshot_files = sorted(
                path
                for path in snapshot.rglob("*")
                if path.is_file()
            )
            before = {
                path.relative_to(snapshot): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in snapshot_files
            }
            reuse = run(str(MESH / "bin/install-launchers"), env=env)
            self.assertEqual(reuse.returncode, 0, reuse.stdout + reuse.stderr)
            after = {
                path.relative_to(snapshot): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in snapshot_files
            }
            self.assertEqual(after, before)

            tampered = snapshot / "bin/render-config"
            tampered.chmod(0o755)
            tampered.write_text("#!/usr/bin/env bash\nexit 19\n", encoding="utf-8")
            tampered.chmod(0o555)
            tampered_bytes = tampered.read_bytes()
            rejected = run(str(MESH / "bin/install-launchers"), env=env)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("digest mismatch", rejected.stderr)
            self.assertEqual(tampered.read_bytes(), tampered_bytes)

            expected_units = {
                "personas-mesh-mirror.service",
                "personas-mesh-mirror.timer",
                "personas-mesh-sync.service",
                "personas-mesh-sync.timer",
                "personas-mesh-user-sync.service",
                "personas-mesh-user-sync.timer",
            }
            self.assertEqual(
                {path.name for path in (MESH / "systemd").iterdir()},
                expected_units,
            )
            units = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (MESH / "systemd").glob("*.service")
            )
            self.assertNotIn("projects/markets/personas", units)
            self.assertNotIn("/mnt/c/Users/wilst", units)
            for legacy in ("wsl", "windows", "hetzner", "github-mirror"):
                self.assertNotIn(legacy, units.casefold())

    def test_mesh_1password_render_and_deep_merge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            stub = base / "op"
            stub.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "[ \"$1\" = inject ] || exit 2\n"
                "{\n"
                "  printf '%s\\n' \"$@\"\n"
                "  tr '\\0' '\\n' < \"/proc/$$/cmdline\"\n"
                "  tr '\\0' '\\n' < \"/proc/$PPID/cmdline\"\n"
                "} > \"${OP_TRACE_PATH:?}\"\n"
                "shift\n"
                "in_file=''\n"
                "out_file=''\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  case \"$1\" in\n"
                "    --in-file) in_file=\"$2\"; shift 2 ;;\n"
                "    --out-file) out_file=\"$2\"; shift 2 ;;\n"
                "    *) exit 3 ;;\n"
                "  esac\n"
                "done\n"
                "python3 - \"$in_file\" \"$out_file\" "
                "\"${OP_FIXTURE_SECRET_FILE:?}\" <<'PY'\n"
                "import pathlib\n"
                "import sys\n"
                "source, output, secret_file = map(pathlib.Path, sys.argv[1:])\n"
                "secret = secret_file.read_text(encoding='utf-8')\n"
                "rendered = source.read_text(encoding='utf-8').replace(\n"
                "    '{{ op://<vault>/fixture/token }}', secret\n"
                ")\n"
                "output.write_text(rendered, encoding='utf-8')\n"
                "PY\n",
                encoding="utf-8",
            )
            stub.chmod(0o755)
            template = base / "template.json"
            output = base / "output.json"
            profile = base / "profile.json"
            secret_file = base / "secret"
            trace = base / "op-trace"
            resolved_secret = "resolved-canary-71d36"
            service_token = "service-token-canary-44ad9"
            secret_file.write_text(resolved_secret, encoding="utf-8")
            write_json(
                template,
                {
                    "rendered": True,
                    "nested": {"new": 2},
                    "token": "{{ op://<vault>/fixture/token }}",
                },
            )
            write_json(output, {"preserved": True, "nested": {"old": 1}})
            write_json(profile, {"profile": True, "nested": {"new": 4, "profile": 3}})
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(base),
                    "OP_BIN": str(stub),
                    "OP_SERVICE_ACCOUNT_TOKEN": service_token,
                    "OP_FIXTURE_SECRET_FILE": str(secret_file),
                    "OP_TRACE_PATH": str(trace),
                }
            )
            result = run(
                str(MESH / "bin/render-config"),
                str(template),
                str(output),
                str(profile),
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            observable = (
                result.stdout.encode()
                + result.stderr.encode()
                + trace.read_bytes()
            )
            self.assertIn(b"inject", trace.read_bytes())
            self.assertIn(b"--in-file", trace.read_bytes())
            self.assertIn(str(template).encode(), trace.read_bytes())
            self.assertNotIn(resolved_secret.encode(), observable)
            self.assertNotIn(service_token.encode(), observable)
            rendered = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(rendered["preserved"])
            self.assertTrue(rendered["profile"])
            self.assertEqual(
                rendered["nested"], {"old": 1, "new": 4, "profile": 3}
            )
            self.assertEqual(rendered["token"], resolved_secret)
            self.assertNotIn(service_token, output.read_text(encoding="utf-8"))
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(base.glob(".render-config.*")), [])

    def test_retired_vault_projection_contract_stays_absent(self) -> None:
        self.assertFalse((ROOT / ".vault-export.yaml").exists())
        self.assertFalse((ROOT / "tests/expected-vault-export.txt").exists())

    def test_mesh_source_is_topology_neutral(self) -> None:
        forbidden = (
            "hetzner",
            "personas-mesh-wsl",
            "personas-mesh-windows",
            "personas-mesh-github-mirror",
            "node.env",
            "node-env",
            "migration-symlink-to-mesh",
            "/mnt/c/",
            "/srv/personas",
            "wils@",
        )
        for path in MESH.rglob("*"):
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8", errors="ignore").casefold()
            for needle in forbidden:
                self.assertNotIn(needle, content, str(path.relative_to(ROOT)))

    def test_no_current_source_uses_stale_personas_marketplace_path(self) -> None:
        stale = (
            "~/.claude/plugins/marketplaces/personas",
            "~/.claude/plugins/cache/personas",
        )
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or ".claude" in path.parts:
                continue
            if path.suffix not in {".md", ".json", ".sh", ""}:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            for needle in stale:
                self.assertNotIn(needle, content, str(path.relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
