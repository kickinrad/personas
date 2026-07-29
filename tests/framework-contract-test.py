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
MANAGER = ROOT
EXPECTED_VERSIONS = {
    "persona-manager": "3.0.0",
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
            "hooks": json.loads(
                (ROOT / "skills/persona-dev/assets/hooks-template.json").read_text(encoding="utf-8")
            )["hooks"],
        },
    )
    write_json(
        root / ".claude/settings.local.json",
        {
            "autoMemoryDirectory": str((root / "user/memory").resolve()),
            "outputStyle": "Atlas",
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
        self.assertFalse((ROOT / "plugins").exists())
        marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["metadata"]["pluginRoot"], ".")
        self.assertEqual(marketplace["metadata"]["version"], EXPECTED_VERSIONS["persona-manager"])
        self.assertEqual(marketplace["plugins"], [{
            "name": "persona-manager",
            "source": ".",
            "description": "Create and verify privacy-first Claude Code and Codex personas",
            "category": "developer-tools",
        }])
        manifest = json.loads(
            (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["version"], EXPECTED_VERSIONS["persona-manager"])
        self.assertEqual(manifest["license"], "Apache-2.0")
        codex_marketplace = json.loads(
            (ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(codex_marketplace["plugins"][0]["source"]["path"], "./")
        codex_manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(codex_manifest["name"], "persona-manager")
        self.assertEqual(codex_manifest["skills"], "./skills/")
        self.assertEqual(codex_manifest["version"], EXPECTED_VERSIONS["persona-manager"])
        self.assertEqual(codex_manifest["license"], "Apache-2.0")

    def test_runtime_declarations_are_truthful(self) -> None:
        capabilities = json.loads(
            (MANAGER / "interop/capabilities.json").read_text(encoding="utf-8")
        )
        self.assertEqual(capabilities["schemaVersion"], 3)
        runtimes = capabilities["runtimes"]
        self.assertEqual(runtimes["claude-code"]["status"], "native")
        self.assertEqual(runtimes["claude-code"]["profiles"]["cloud"], "preview-private-repository-only")
        self.assertEqual(runtimes["codex"]["status"], "native")
        self.assertEqual(runtimes["codex"]["hooks"]["trust"], "required")
        for runtime in ("gemini-cli", "kimi-code"):
            self.assertEqual(runtimes[runtime]["status"], "unsupported")
            self.assertIn("reason", runtimes[runtime])

    def test_trigger_positive_controls_and_isolation(self) -> None:
        # Runtime discovery is declarative: both manifests expose the canonical
        # skills tree and SKILL frontmatter supplies each callable identity.
        # The retired routing table was test-only, never a runtime input.
        self.assertFalse((ROOT / "skill-rules.json").exists())
        names = set()
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            frontmatter = skill.read_text(encoding="utf-8").split("---", 2)[1]
            match = re.search(r"^name:\s*(\S+)", frontmatter, re.MULTILINE)
            self.assertIsNotNone(match, skill)
            names.add(match.group(1))
        self.assertEqual(names, {"persona-dev", "persona-update", "self-improve"})

    def test_verify_uses_fixture_home_and_reports_legacy_self_improve(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            valid = base / "valid/atlas"
            invalid = base / "invalid/atlas"
            make_persona(valid)
            make_persona(invalid, local_self_improve=True)
            env = os.environ.copy()
            env["HOME"] = str(base / "home")
            verifier = MANAGER / "bin/personas"
            good = run(
                str(verifier),
                "verify",
                str(valid),
                "--profile",
                "claude-local",
                "--json",
                env=env,
            )
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertEqual(json.loads(good.stdout)["status"], "PASS")
            bad = run(
                str(verifier),
                "verify",
                str(invalid),
                "--profile",
                "claude-local",
                "--json",
                env=env,
            )
            self.assertEqual(bad.returncode, 0, bad.stdout + bad.stderr)
            self.assertIn(
                "legacy local duplicate",
                "\n".join(json.loads(bad.stdout)["warnings"]),
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

    def test_verifier_works_from_installed_and_relocated_product_copies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            persona = base / "persona/atlas"
            make_persona(persona)
            for name in ("installed", "relocated"):
                product = base / name / "persona-manager"
                shutil.copytree(
                    ROOT,
                    product,
                    ignore=shutil.ignore_patterns(".git", ".claude", ".pytest_cache"),
                )
                verifier = product / "bin/personas"
                env = os.environ.copy()
                env.update({"HOME": str(base / f"{name}-home"), "CLAUDE_PLUGIN_ROOT": str(product)})
                result = run(
                    str(verifier),
                    "verify",
                    str(persona),
                    "--profile",
                    "claude-local",
                    "--json",
                    env=env,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["frameworkSource"], str(product.resolve()))

    def test_root_has_no_generated_skill_tree_or_nested_forwarders(self) -> None:
        self.assertFalse((ROOT / "interop/generate.py").exists())
        self.assertFalse(any(path.is_dir() for path in ROOT.rglob(".generated")))
        self.assertFalse((ROOT / "plugins/persona-manager").exists())
        self.assertFalse((ROOT / "bin/validate-persona").exists())
        for manifest in (
            ROOT / ".claude-plugin/marketplace.json",
            ROOT / ".agents/plugins/marketplace.json",
        ):
            self.assertNotIn("plugins/", manifest.read_text(encoding="utf-8"))

    def test_retired_vault_projection_contract_stays_absent(self) -> None:
        self.assertFalse((ROOT / ".vault-export.yaml").exists())
        self.assertFalse((ROOT / "tests/expected-vault-export.txt").exists())

    def test_no_current_source_uses_retired_product_paths(self) -> None:
        text_suffixes = {"", ".json", ".md", ".py", ".sh", ".toml", ".yaml", ".yml"}
        stale = (
            "~/.claude/plugins/marketplaces/personas",
            "~/.claude/plugins/cache/personas",
            "plugins/persona-dashboard",
            "plugins/personas-mesh",
            "persona-dashboard@personas",
            "personas-mesh@personas",
            "plugins/persona-manager",
            "persona-manager/.generated",
        )
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if (
                not path.is_file()
                or ".git" in path.parts
                or ".claude" in path.parts
                or relative == Path("tests/framework-contract-test.py")
                or relative in {Path("MIGRATION.md"), Path("CHANGELOG.md")}
            ):
                continue
            if path.suffix not in text_suffixes:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            for needle in stale:
                self.assertNotIn(needle, content, str(relative))


if __name__ == "__main__":
    unittest.main(verbosity=2)
