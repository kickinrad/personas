"""Package contracts, source inventory, and their negative controls."""
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHES = {"__pycache__", ".pytest_cache"}
PRIVATE = {"user", ".mcp.json", ".env"}
SECRET = re.compile(r"eyJ[A-Za-z0-9_-]{20,}|GOCSPX-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|BEGIN PRIVATE KEY")


def inventory(root):
    if (root / ".git").exists():
        names = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
        return [root / name for name in names if name]
    return [p for p in root.rglob("*") if p.is_file() and not CACHES.intersection(p.relative_to(root).parts)]


def package_errors(root):
    errors = []
    for path in inventory(root):
        relative = path.relative_to(root)
        if CACHES.union(PRIVATE).intersection(relative.parts):
            errors.append(f"private or generated file: {relative}")
        if not path.is_file():
            continue
        if path.suffix in {".md", ".json", ".toml"}:
            text = path.read_text(encoding="utf-8")
            if SECRET.search(text):
                errors.append(f"credential-like source: {relative}")
            if path.name == "SKILL.md":
                if not re.match(r"\A---\nname: .+\ndescription: .+\n---\n", text):
                    errors.append(f"invalid skill frontmatter: {relative}")
                if len(text.split()) > 500:
                    errors.append(f"skill exceeds 500 words: {relative}")
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
    return errors


class RepositoryTest(unittest.TestCase):
    def test_native_manifests_share_one_release(self):
        def read(path):
            return json.loads((ROOT / path).read_text())
        claude = read(".claude-plugin/plugin.json")
        codex = read(".codex-plugin/plugin.json")
        market = read(".claude-plugin/marketplace.json")
        agents = read(".agents/plugins/marketplace.json")
        capabilities = read("interop/capabilities.json")
        self.assertRegex(claude["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual({codex["version"], market["metadata"]["version"], capabilities["version"]}, {claude["version"]})
        self.assertEqual({claude["name"], codex["name"], market["plugins"][0]["name"], agents["plugins"][0]["name"]}, {"personas"})
        self.assertEqual({claude["license"], codex["license"]}, {"Apache-2.0"})
        self.assertIn("Apache License", (ROOT / "LICENSE").read_text())
        self.assertEqual(market["metadata"]["pluginRoot"], ".")
        self.assertEqual(market["plugins"][0]["source"], ".")
        self.assertEqual(agents["plugins"][0]["source"]["path"], "./")
        self.assertEqual(codex["skills"], "./skills/")
        self.assertTrue(all("version" not in entry for entry in market["plugins"]))
        self.assertEqual(capabilities["portableAuthority"], "AGENTS.md")
        self.assertEqual(capabilities["runtimes"]["claude-code"]["imports"], ["AGENTS.md"])
        for runtime in ("claude-code", "codex"):
            declaration = capabilities["runtimes"][runtime]
            self.assertEqual(declaration["status"], "native")
            self.assertTrue((ROOT / declaration["personaNativeSync"]).is_file())

    def test_source_package_is_clean(self):
        self.assertEqual(package_errors(ROOT), [])
        self.assertEqual({p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}, {"persona-dev", "self-improve"})
        for retired in ("plugins", "bin/personas", "hooks", ".claude/plans", ".claude/evidence"):
            self.assertFalse(any(p.is_file() for p in (ROOT / retired).rglob("*")) if (ROOT / retired).is_dir() else (ROOT / retired).exists())

    def test_export_ignores_caches_but_git_inventory_rejects_them(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cache = root / "__pycache__/example.pyc"
            cache.parent.mkdir()
            cache.write_bytes(b"fixture")
            self.assertEqual(package_errors(root), [])
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "add", "__pycache__"], cwd=root, check=True)
            self.assertIn("private or generated", package_errors(root)[0])

    def test_removed_shell_checks_still_reject_bad_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "SKILL.md").write_text("Broken frontmatter\n")
            (root / "leak.json").write_text(json.dumps({"value": "sk-" + "x" * 24}))
            (root / "user").mkdir()
            (root / "user/profile.md").write_text("private fixture")
            errors = "\n".join(package_errors(root))
            for expected in ("frontmatter", "credential-like", "private or generated"):
                self.assertIn(expected, errors)
