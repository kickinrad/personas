#!/usr/bin/env python3
"""Public-interface contract tests for `bin/personas verify`."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "bin/personas"
FIXTURE_MATRIX = ROOT / "tests/fixtures/contracts/matrix.json"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (str(PERSONAS), *args),
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_home(root: Path, *, version: str = "3.0.0") -> Path:
    for directory in ("user/memory", ".claude/output-styles", ".claude/hooks"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    files = {
        "CLAUDE.md": "# Atlas\n",
        "AGENTS.md": "# Atlas\n",
        "README.md": "# Atlas\n",
        "user/profile.md": "# Profile\n",
        "user/memory/MEMORY.md": "# Memory\n",
        ".claude/output-styles/atlas.md": "---\nname: Atlas\n---\n",
        ".gitignore": ".mcp.json\n.claude/settings.local.json\n",
        ".framework-version": version + "\n",
        ".claude-flags": "--setting-sources project,local\n",
        ".claude/hooks/public-repo-guard.sh": "#!/usr/bin/env bash\nexit 0\n",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    write_json(
        root / ".claude/settings.json",
        {
            "sandbox": {
                "enabled": True,
                "autoAllowBashIfSandboxed": True,
                "filesystem": {"denyRead": ["~/.aws", "~/.ssh", "~/.gnupg", "../"]},
            },
            "enabledPlugins": {"persona-manager@personas": True},
            "hooks": json.loads(
                (ROOT / "skills/persona-dev/assets/hooks-template.json").read_text(encoding="utf-8")
            )["hooks"],
        },
    )
    write_json(
        root / ".claude/settings.local.json",
        {"autoMemoryDirectory": str((root / "user/memory").resolve())},
    )
    return root


def make_visibility_adapter(root: Path, payload: object, *, exit_code: int = 0) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    adapter = root / "github-visibility-adapter"
    adapter.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"print(json.dumps({payload!r}))\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    adapter.chmod(0o755)
    return adapter


class PersonaVerifyTest(unittest.TestCase):
    def test_matrix_fixture_declares_expected_contract_outcomes(self) -> None:
        matrix = json.loads(FIXTURE_MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(matrix["cases"]["valid"], "PASS")
        self.assertEqual(matrix["cloudVisibility"]["accepted"], "PRIVATE")

    def test_shared_and_runtime_profiles_are_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = make_home(Path(directory) / "atlas")
            (home / ".claude/settings.json").unlink()
            codex = run("verify", str(home), "--profile", "codex", "--json")
            self.assertEqual(codex.returncode, 0, codex.stderr)
            self.assertEqual(json.loads(codex.stdout)["status"], "PASS")
            claude = run("verify", str(home), "--profile", "claude-local", "--json")
            self.assertEqual(claude.returncode, 1)
            self.assertIn(".claude/settings.json", "\n".join(json.loads(claude.stdout)["errors"]))

    def test_matrix_for_absent_malformed_stale_unsafe_and_legacy_homes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            absent = run("verify", str(base / "absent"), "--json")
            self.assertEqual(absent.returncode, 1)
            self.assertIn("persona directory does not exist", json.loads(absent.stdout)["errors"])

            malformed_home = make_home(base / "malformed")
            (malformed_home / ".claude/settings.json").write_text("{bad", encoding="utf-8")
            malformed = run("verify", str(malformed_home), "--profile", "claude-local", "--json")
            self.assertEqual(malformed.returncode, 1)
            self.assertIn(".claude/settings.json: invalid JSON", "\n".join(json.loads(malformed.stdout)["errors"]))

            stale = run("verify", str(make_home(base / "stale", version="1.0.0")), "--json")
            self.assertEqual(stale.returncode, 0)
            self.assertEqual(json.loads(stale.stdout)["status"], "WARN")

            unsafe_home = make_home(base / "unsafe")
            (unsafe_home / "user/profile.md").write_text("token=sk-abcdefghijklmnopqrst\n", encoding="utf-8")
            unsafe = run("verify", str(unsafe_home), "--json")
            self.assertEqual(unsafe.returncode, 1)
            self.assertIn("user/profile.md: secret-like value detected", json.loads(unsafe.stdout)["errors"])

            legacy_home = make_home(base / "legacy")
            legacy = legacy_home / ".claude/skills/self-improve/SKILL.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("---\nname: self-improve\n---\n", encoding="utf-8")
            before = legacy.read_bytes()
            result = run("verify", str(legacy_home), "--json")
            self.assertEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "WARN")
            self.assertIn("legacy local duplicate", "\n".join(report["warnings"]))
            self.assertEqual(legacy.read_bytes(), before)

    def test_unsupported_profile_is_structured_usage_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run("verify", str(make_home(Path(directory) / "atlas")), "--profile", "unknown", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "FAIL")
            self.assertIn("unsupported profile", "\n".join(json.loads(result.stdout)["errors"]))

    def test_cloud_requires_private_authenticated_visibility_evidence(self) -> None:
        cases = {
            "PRIVATE": ({"authenticated": True, "visibility": "PRIVATE"}, 0, "PASS"),
            "PUBLIC": ({"authenticated": True, "visibility": "PUBLIC"}, 1, "FAIL"),
            "INTERNAL": ({"authenticated": True, "visibility": "INTERNAL"}, 1, "FAIL"),
            "UNKNOWN": ({"authenticated": True, "visibility": "UNKNOWN"}, 1, "FAIL"),
            "UNAUTHENTICATED": ({"authenticated": False, "visibility": "PRIVATE"}, 1, "FAIL"),
        }
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            home = make_home(base / "atlas")
            subprocess.run(("git", "init", "-q", str(home)), check=True)
            subprocess.run(("git", "-C", str(home), "remote", "add", "origin", "https://github.com/example/atlas.git"), check=True)
            (home / ".persona-cloud-repository").write_text("example/atlas\n", encoding="utf-8")
            for name, (payload, exit_code, expected) in cases.items():
                adapter = make_visibility_adapter(base / name, payload)
                env = os.environ.copy()
                env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(adapter)
                result = run("verify", str(home), "--profile", "claude-cloud", "--json", env=env)
                self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], expected)

    def test_cloud_fails_closed_for_ambiguous_unavailable_and_unreachable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            no_remote = make_home(base / "no-remote")
            ambiguous = run("verify", str(no_remote), "--profile", "claude-cloud", "--json")
            self.assertEqual(ambiguous.returncode, 1)
            self.assertIn("repository is ambiguous", "\n".join(json.loads(ambiguous.stdout)["errors"]))

            home = make_home(base / "atlas")
            subprocess.run(("git", "init", "-q", str(home)), check=True)
            subprocess.run(("git", "-C", str(home), "remote", "add", "origin", "git@github.com:example/atlas.git"), check=True)
            (home / ".persona-cloud-repository").write_text("example/atlas\n", encoding="utf-8")
            unavailable = run("verify", str(home), "--profile", "claude-cloud", "--json", env=os.environ | {"PERSONAS_GITHUB_VISIBILITY_ADAPTER": str(base / "missing-adapter")})
            self.assertEqual(unavailable.returncode, 1)
            self.assertIn("adapter is unreachable", "\n".join(json.loads(unavailable.stdout)["errors"]))

            adapter = make_visibility_adapter(base / "unreachable", {"authenticated": True, "visibility": "PRIVATE"}, exit_code=9)
            env = os.environ.copy()
            env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(adapter)
            unreachable = run("verify", str(home), "--profile", "claude-cloud", "--json", env=env)
            self.assertEqual(unreachable.returncode, 1)
            self.assertIn("adapter is unreachable", "\n".join(json.loads(unreachable.stdout)["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
