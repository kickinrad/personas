#!/usr/bin/env python3
"""Clean temporary-runtime acceptance tests for the packaged adapter surface."""

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
FIXTURE = ROOT / "tests/fixtures/runtimes/acceptance.json"


def copy_product(destination: Path) -> Path:
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", ".claude", ".pytest_cache", "__pycache__"))
    return destination


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def create_persona_from_packaged_assets(product: Path, home: Path) -> None:
    assets = product / "skills/persona-dev/assets"
    for directory in ("user/memory", ".claude/output-styles", ".claude/hooks"):
        (home / directory).mkdir(parents=True, exist_ok=True)
    replacements = {"{PersonaName}": "Atlas", "{name}": "atlas", "{emoji}": "🧭", "{role description without personal facts}": "test collaborator"}
    for source_name, destination in (("claude-md-template.md", "CLAUDE.md"), ("agents-template.md", "AGENTS.md"), ("profile-template.md", "user/profile.md"), ("readme-template.md", "README.md")):
        text = (assets / source_name).read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        (home / destination).write_text(text, encoding="utf-8")
    shutil.copy2(assets / "gitignore-template", home / ".gitignore")
    shutil.copy2(product / "scripts/public-repo-guard.sh", home / ".claude/hooks/public-repo-guard.sh")
    (home / "user/memory/MEMORY.md").write_text("# Memory\n", encoding="utf-8")
    project_skill = home / "skills/atlas-brief/SKILL.md"
    project_skill.parent.mkdir(parents=True, exist_ok=True)
    project_skill.write_text(
        "---\nname: atlas-brief\ndescription: Prepare a concise Atlas role brief.\n---\n\n# Atlas brief\n",
        encoding="utf-8",
    )
    (home / ".framework-version").write_text("3.0.0\n", encoding="utf-8")
    (home / ".claude-flags").write_text("--setting-sources project,local\n", encoding="utf-8")
    write_json(home / ".claude/settings.json", json.loads((assets / "settings-template.json").read_text(encoding="utf-8")))
    write_json(home / ".claude/settings.local.json", {"autoMemoryDirectory": str((home / "user/memory").resolve())})
    write_json(home / "hooks.json", json.loads((assets / "hooks-template.json").read_text(encoding="utf-8")))
    (home / ".persona-cloud-repository").write_text("example/atlas\n", encoding="utf-8")


def verify(product: Path, home: Path, profile: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run((str(product / "bin/personas"), "verify", str(home), "--profile", profile, "--json"), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)


def adapter(path: Path, visibility: str) -> Path:
    path.write_text("#!/usr/bin/env python3\nimport json\nprint(json.dumps({'authenticated': True, 'visibility': '" + visibility + "'}))\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def rule_matches(rule: dict[str, object], prompt: str) -> bool:
    triggers = rule["promptTriggers"]
    assert isinstance(triggers, dict)
    folded = prompt.casefold()
    return any(str(word).casefold() in folded for word in triggers["keywords"]) or any(re.search(str(pattern), prompt, re.IGNORECASE) for pattern in triggers["intentPatterns"])


class RuntimeAdapterTest(unittest.TestCase):
    def test_codex_manifest_marketplace_and_trusted_hook_contract(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["plugins"][0]["source"]["path"], fixture["codex"]["marketplacePath"])
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["skills"], "./skills/")
        capabilities = json.loads((ROOT / "interop/capabilities.json").read_text(encoding="utf-8"))
        self.assertEqual(capabilities["runtimes"]["codex"]["status"], "native")
        self.assertEqual(capabilities["runtimes"]["codex"]["hooks"]["trust"], fixture["codex"]["hookTrust"])
        command = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn("PLUGIN_ROOT", command)
        self.assertIn("CLAUDE_PLUGIN_ROOT", command)

    def test_clean_claude_local_and_codex_paths_discover_instructions_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            product = copy_product(base / "installed/persona-manager")
            home = base / "atlas"
            create_persona_from_packaged_assets(product, home)
            claude = verify(product, home, "claude-local")
            self.assertEqual(claude.returncode, 0, claude.stderr)
            codex = verify(product, home, "codex")
            self.assertEqual(codex.returncode, 0, codex.stderr)
            agents = (home / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("CLAUDE.md", agents)
            self.assertNotIn("## Role", agents)
            self.assertFalse((product / "skill-rules.json").exists())
            declared = {
                re.search(r"^name:\s*(\S+)", skill.read_text(encoding="utf-8"), re.MULTILINE).group(1)
                for skill in (product / "skills").glob("*/SKILL.md")
            }
            self.assertEqual(declared, {"persona-dev", "persona-update", "self-improve"})

    def test_trusted_hook_runs_from_the_installed_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            product = copy_product(base / "installed/persona-manager")
            home = base / "atlas"
            create_persona_from_packaged_assets(product, home)
            (home / ".framework-version").write_text("0.0.1\n", encoding="utf-8")
            command = json.loads((product / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]["SessionStart"][0]["hooks"][0]["command"]
            env = os.environ.copy()
            env.update({"PLUGIN_ROOT": str(product), "PLUGIN_DATA": str(base / "plugin-data"), "CLAUDE_PLUGIN_ROOT": str(product)})
            result = subprocess.run(("bash", "-lc", command), cwd=home, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("3.0.0", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])

    def test_cloud_private_preflight_push_recovery_and_public_stop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            bare = base / "github-fixture.git"
            subprocess.run(("git", "init", "--bare", "-q", str(bare)), check=True)
            subprocess.run(("git", "-C", str(bare), "symbolic-ref", "HEAD", "refs/heads/main"), check=True)
            seed = base / "seed"
            product = copy_product(base / "installed/persona-manager")
            create_persona_from_packaged_assets(product, seed)
            subprocess.run(("git", "init", "-q", str(seed)), check=True)
            subprocess.run(("git", "-C", str(seed), "config", "user.email", "fixture@example.invalid"), check=True)
            subprocess.run(("git", "-C", str(seed), "config", "user.name", "Fixture"), check=True)
            subprocess.run(("git", "-C", str(seed), "add", "."), check=True)
            subprocess.run(("git", "-C", str(seed), "-c", "commit.gpgSign=false", "commit", "-qm", "cloud fixture"), check=True)
            subprocess.run(("git", "-C", str(seed), "remote", "add", "fixture", str(bare)), check=True)
            subprocess.run(("git", "-C", str(seed), "push", "-q", "fixture", "HEAD:main"), check=True)
            clone = base / "clone"
            subprocess.run(("git", "clone", "-q", str(bare), str(clone)), check=True)
            subprocess.run(("git", "-C", str(clone), "remote", "rename", "origin", "fixture"), check=True)
            subprocess.run(("git", "-C", str(clone), "remote", "add", "origin", "https://github.com/example/atlas.git"), check=True)
            env = os.environ.copy()
            env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(adapter(base / "private-adapter", "PRIVATE"))
            private = verify(product, clone, "claude-cloud", env)
            self.assertEqual(private.returncode, 0, private.stdout + private.stderr)
            self.assertFalse((clone / "user/profile.md").exists())
            self.assertFalse((clone / "user/memory").exists())
            self.assertFalse((clone / ".claude/settings.local.json").exists())
            role_skill = clone / "skills/atlas-brief/SKILL.md"
            self.assertTrue(role_skill.is_file())
            self.assertIn("name: atlas-brief", role_skill.read_text(encoding="utf-8"))
            self.assertFalse((clone / ".claude/skills/self-improve").exists())
            (clone / "README.md").write_text("# Atlas recovered\n", encoding="utf-8")
            subprocess.run(("git", "-C", str(clone), "add", "README.md"), check=True)
            subprocess.run(("git", "-C", str(clone), "-c", "commit.gpgSign=false", "commit", "-qm", "recovery"), check=True)
            subprocess.run(("git", "-C", str(clone), "push", "-q", "fixture", "HEAD:main"), check=True)
            public_env = os.environ.copy()
            public_env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(adapter(base / "public-adapter", "PUBLIC"))
            before = (clone / "README.md").read_bytes()
            public = verify(product, clone, "claude-cloud", public_env)
            self.assertEqual(public.returncode, 1)
            self.assertIn("PRIVATE", "\n".join(json.loads(public.stdout)["errors"]))
            self.assertEqual((clone / "README.md").read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
