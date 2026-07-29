#!/usr/bin/env python3
"""Public behavior tests for deterministic staged persona creation."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "bin/personas"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run((str(PERSONAS), *args), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)


def adapter(root: Path, payload: object, *, exit_code: int = 0) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "visibility-adapter"
    path.write_text(
        "#!/usr/bin/env python3\nimport json\n"
        f"print(json.dumps({payload!r}))\nraise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def native_gh(root: Path, visibility: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "gh"
    path.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' {visibility!r}\n", encoding="utf-8")
    path.chmod(0o755)
    return path


class PersonaCreateTest(unittest.TestCase):
    def test_local_and_codex_creation_are_offline_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            marker = parent / "must-not-run"
            env = os.environ.copy()
            env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(marker)
            local = run("create", "atlas", "--destination", str(parent), "--profile", "claude-local", "--json", env=env)
            self.assertEqual(local.returncode, 0, local.stderr)
            report = json.loads(local.stdout)
            self.assertEqual(report["status"], "PASS")
            home = parent / "atlas"
            self.assertEqual(Path(report["path"]), home)
            self.assertTrue((home / "user/profile.md").is_file())
            self.assertFalse(marker.exists())
            verified = run("verify", str(home), "--profile", "claude-local", "--json")
            self.assertEqual(verified.returncode, 0, verified.stdout)

            codex = run("create", "coda", "--destination", str(parent), "--profile", "codex", "--json")
            self.assertEqual(codex.returncode, 0, codex.stderr)
            self.assertEqual(run("verify", str(parent / "coda"), "--profile", "codex", "--json").returncode, 0)

    def test_collision_and_forced_partial_failure_leave_no_final_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            existing = parent / "atlas"
            existing.mkdir()
            (existing / "keep").write_text("unchanged", encoding="utf-8")
            collision = run("create", "atlas", "--destination", str(parent), "--profile", "codex", "--json")
            self.assertEqual(collision.returncode, 1)
            self.assertIn("already exists", "\n".join(json.loads(collision.stdout)["errors"]))
            self.assertEqual((existing / "keep").read_text(encoding="utf-8"), "unchanged")

            env = os.environ.copy()
            env["PERSONAS_CREATE_FAIL_AFTER"] = "3"
            partial = run("create", "partial", "--destination", str(parent), "--profile", "claude-local", "--json", env=env)
            self.assertEqual(partial.returncode, 1)
            report = json.loads(partial.stdout)
            self.assertTrue(report["stagingCleaned"])
            self.assertFalse((parent / "partial").exists())
            self.assertFalse((parent / ".partial.personas-staging").exists())

    def test_destination_error_is_path_specific(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            blocked = Path(directory) / "not-a-directory"
            blocked.write_text("x", encoding="utf-8")
            result = run("create", "atlas", "--destination", str(blocked), "--profile", "codex", "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn(str(blocked), "\n".join(json.loads(result.stdout)["errors"]))

    def test_cloud_private_creates_ci_and_public_or_unknown_never_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            private_env = os.environ.copy()
            private_env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(adapter(parent, {"authenticated": True, "visibility": "PRIVATE"}))
            private = run("create", "cloud-atlas", "--destination", str(parent), "--profile", "claude-cloud", "--repository", "example/cloud-atlas", "--json", env=private_env)
            self.assertEqual(private.returncode, 0, private.stdout)
            home = parent / "cloud-atlas"
            ci = (home / ".github/workflows/persona-private.yml").read_text(encoding="utf-8")
            self.assertIn('"${{ github.event.repository.private }}" != "true"', ci)
            self.assertTrue((home / ".claude/hooks/public-repo-guard.sh").is_file())
            self.assertEqual((home / ".persona-cloud-repository").read_text(encoding="utf-8"), "example/cloud-atlas\n")
            self.assertEqual(
                subprocess.run(("git", "-C", str(home), "remote", "get-url", "origin"), text=True, stdout=subprocess.PIPE, check=True).stdout.strip(),
                "https://github.com/example/cloud-atlas.git",
            )
            self.assertEqual(run("verify", str(home), "--profile", "claude-cloud", "--json", env=private_env).returncode, 0)
            self.assertFalse((home / "user").exists())

            for name, payload in (("public", {"authenticated": True, "visibility": "PUBLIC"}), ("unknown", {"authenticated": True, "visibility": "UNKNOWN"})):
                env = os.environ.copy()
                env["PERSONAS_GITHUB_VISIBILITY_ADAPTER"] = str(adapter(parent / "adapters" / name, payload))
                result = run("create", name, "--destination", str(parent), "--profile", "claude-cloud", "--repository", f"example/{name}", "--json", env=env)
                self.assertEqual(result.returncode, 1)
                self.assertFalse((parent / name).exists())
                self.assertFalse((parent / f".{name}.personas-staging").exists())

    def test_cloud_uses_native_gh_and_binds_the_created_home_to_its_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            tools = parent / "tools"
            native_gh(tools, "PRIVATE")
            env = os.environ.copy()
            env["PATH"] = f"{tools}:{env['PATH']}"
            created = run("create", "atlas", "--destination", str(parent), "--profile", "claude-cloud", "--repository", "example/atlas", "--json", env=env)
            self.assertEqual(created.returncode, 0, created.stdout)
            home = parent / "atlas"
            self.assertEqual(run("verify", str(home), "--profile", "claude-cloud", "--json", env=env).returncode, 0)
            subprocess.run(("git", "-C", str(home), "remote", "set-url", "origin", "https://github.com/example/other.git"), check=True)
            mismatch = run("verify", str(home), "--profile", "claude-cloud", "--json", env=env)
            self.assertEqual(mismatch.returncode, 1)
            self.assertIn("binding marker does not match", "\n".join(json.loads(mismatch.stdout)["errors"]))
            subprocess.run(("git", "-C", str(home), "remote", "set-url", "origin", "git@github.com:example/atlas.git"), check=True)
            self.assertEqual(run("verify", str(home), "--profile", "claude-cloud", "--json", env=env).returncode, 0)

    def test_non_json_create_reports_the_created_name_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run("create", "atlas", "--destination", directory, "--profile", "codex")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS: atlas", result.stdout)

    def test_json_usage_failure_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run("create", "Bad Name", "--destination", directory, "--profile", "codex", "--json")
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertEqual(report["schemaVersion"], 1)
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("name", "\n".join(report["errors"]))

    def test_malformed_creation_environment_is_a_structured_json_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ | {"PERSONAS_CREATE_FAIL_AFTER": "not-a-number"}
            result = run("create", "atlas", "--destination", directory, "--profile", "codex", "--json", env=env)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, "")
            report = json.loads(result.stdout)
            self.assertEqual(report["schemaVersion"], 1)
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("PERSONAS_CREATE_FAIL_AFTER", "\n".join(report["errors"]))

    def test_malformed_json_invocation_is_structured_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run("create", "atlas", "--destination", directory, "--profile", "codex", "--unknown", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, "")
            report = json.loads(result.stdout)
            self.assertEqual(report["schemaVersion"], 1)
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("invocation:", "\n".join(report["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
