#!/usr/bin/env python3
"""Contract tests for publishability, offline scaffolding, and Cloud preflight."""

from __future__ import annotations

import os
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts/public-repo-guard.sh"
FIXTURES = ROOT / "tests/fixtures/security"


def run(*args: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )


class PrivacySafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "persona"
        self.repo.mkdir()
        run("git", "init", "-q", cwd=self.repo)
        run("git", "config", "user.email", "test@example.invalid", cwd=self.repo)
        run("git", "config", "user.name", "Privacy Test", cwd=self.repo)
        run("git", "remote", "add", "origin", "https://github.com/owner/private-persona.git", cwd=self.repo)
        (self.repo / ".persona-cloud-repository").write_text("owner/private-persona\n", encoding="utf-8")
        shutil.copy(FIXTURES / "clean-public/CLAUDE.md", self.repo / "CLAUDE.md")
        (self.repo / ".gitignore").write_text((ROOT / "skills/persona-dev/assets/gitignore-template").read_text(), encoding="utf-8")
        run("git", "add", "CLAUDE.md", ".gitignore", cwd=self.repo)
        committed = run("git", "-c", "commit.gpgSign=false", "commit", "-qm", "clean publishable definition", cwd=self.repo)
        self.assertEqual(committed.returncode, 0, committed.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def guard(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return run(str(GUARD), *args, cwd=self.repo, env=env)

    def stage_fixture(self, source: str, destination: str) -> None:
        destination_path = self.repo / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(FIXTURES / source, destination_path)
        run("git", "add", "-f", destination, cwd=self.repo)

    def staged_tree(self) -> str:
        result = run("git", "write-tree", cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_clean_public_definition_passes_offline(self) -> None:
        self.assertEqual(self.guard("--check-repository").returncode, 0)
        self.assertEqual(self.guard("--check-tree", self.staged_tree()).returncode, 0)
        # A local profile remains untracked; the guard needs no GitHub or network client.
        (self.repo / "user").mkdir()
        shutil.copy(FIXTURES / "pii-like/profile.md", self.repo / "user/profile.md")
        self.assertNotIn("user/profile.md", run("git", "status", "--porcelain", cwd=self.repo).stdout)
        self.assertEqual(self.guard("--check-staged").returncode, 0)

    def test_repository_check_fails_closed_without_a_committed_head(self) -> None:
        orphan = Path(self.temp.name) / "orphan"
        orphan.mkdir()
        run("git", "init", "-q", cwd=orphan)
        result = run(str(GUARD), "--check-repository", cwd=orphan)
        self.assertEqual(result.returncode, 2)
        self.assertIn("HEAD tree is unavailable", result.stderr)

    def test_tracked_profile_memory_and_runtime_state_fail(self) -> None:
        for fixture, destination in (
            ("pii-like/profile.md", "user/profile.md"),
            ("tracked-user-state/MEMORY.md", "user/memory/MEMORY.md"),
            ("runtime-settings/private-runtime-state.json", ".claude/settings.local.json"),
        ):
            with self.subTest(destination=destination):
                run("git", "reset", "--quiet", cwd=self.repo)
                self.stage_fixture(fixture, destination)
                result = self.guard("--check-staged")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("blocked private path", result.stderr)

    def test_credentials_fail_even_when_visibility_is_private(self) -> None:
        self.stage_fixture("secrets/api-key.md", "docs/procedure.md")
        result = self.guard("--check-staged")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("credential-like content", result.stderr)

    def test_noninteractive_and_alternate_git_forms_cannot_bypass_gate(self) -> None:
        self.stage_fixture("pii-like/profile.md", "user/profile.md")
        # The release seam examines the index itself, not a parsed `git commit` command.
        result = self.guard("--check-staged")
        self.assertEqual(result.returncode, 2, result.stderr)
        tree_result = self.guard("--check-tree", self.staged_tree())
        self.assertEqual(tree_result.returncode, 2, tree_result.stderr)

    def test_unusual_private_filenames_are_blocked_in_staged_tree_and_head_checks(self) -> None:
        names = (
            "user/new\nline.md",
            "user/tab\tname.md",
            "user/quote'and\\backslash name.md",
            "user/space name.md",
            "-private.env",
        )
        for name in names:
            with self.subTest(name=repr(name)):
                path = self.repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("private fixture\n", encoding="utf-8")
                added = run("git", "add", "-f", "--", name, cwd=self.repo)
                self.assertEqual(added.returncode, 0, added.stderr)
                staged = self.guard("--check-staged")
                self.assertEqual(staged.returncode, 2, staged.stderr)
                self.assertIn("blocked private path", staged.stderr)
                tree = self.guard("--check-tree", self.staged_tree())
                self.assertEqual(tree.returncode, 2, tree.stderr)
                committed = run("git", "-c", "commit.gpgSign=false", "commit", "-qm", "add unusual private filename", cwd=self.repo)
                self.assertEqual(committed.returncode, 0, committed.stderr)
                repository = self.guard("--check-repository")
                self.assertEqual(repository.returncode, 2, repository.stderr)

    def test_cloud_preflight_accepts_only_exact_private_evidence(self) -> None:
        fake_gh = self.repo / "fake-gh"
        fake_gh.write_text("#!/usr/bin/env bash\nprintf '%s\\n' \"${FAKE_VISIBILITY:-}\"\n", encoding="utf-8")
        fake_gh.chmod(0o755)
        base = os.environ | {"PERSONA_GITHUB_CLI": str(fake_gh)}
        for visibility, expected in (
            ("PRIVATE", 0), ("PUBLIC", 2), ("INTERNAL", 2), ("", 2), ("private", 2),
        ):
            with self.subTest(visibility=visibility or "unknown"):
                result = self.guard("--cloud-preflight", "owner/private-persona", env=base | {"FAKE_VISIBILITY": visibility})
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_cloud_preflight_rejects_a_repository_binding_mismatch(self) -> None:
        fake_gh = self.repo / "fake-gh"
        fake_gh.write_text("#!/usr/bin/env bash\nprintf 'PRIVATE\\n'\n", encoding="utf-8")
        fake_gh.chmod(0o755)
        (self.repo / ".persona-cloud-repository").write_text("owner/other-persona\n", encoding="utf-8")
        result = self.guard("--cloud-preflight", env=os.environ | {"PERSONA_GITHUB_CLI": str(fake_gh)})
        self.assertEqual(result.returncode, 2)
        self.assertIn("binding marker does not match origin", result.stderr)

    def test_templates_document_local_writes_and_cloud_ordering(self) -> None:
        ignore = (ROOT / "skills/persona-dev/assets/gitignore-template").read_text(encoding="utf-8")
        readme = (ROOT / "skills/persona-dev/assets/readme-template.md").read_text(encoding="utf-8")
        hooks = (ROOT / "skills/persona-dev/assets/hooks-template.json").read_text(encoding="utf-8")
        self.assertIn("user/", ignore)
        self.assertIn(".claude/settings.local.json", ignore)
        self.assertIn("never enter Git", readme)
        self.assertIn("before writing or committing any personalized context", readme)
        self.assertIn("advisory only", hooks)
        self.assertIn("--cloud-preflight", hooks)

    def test_session_start_context_is_truthful_for_local_and_cloud(self) -> None:
        command = json.loads(
            (ROOT / "skills/persona-dev/assets/hooks-template.json").read_text(encoding="utf-8")
        )["hooks"]["SessionStart"][0]["command"]
        guard = self.repo / ".claude/hooks/public-repo-guard.sh"
        guard.parent.mkdir(parents=True)
        guard.write_text(
            "#!/usr/bin/env bash\n[ \"${GUARD_RESULT:-pass}\" = pass ] || exit 2\n",
            encoding="utf-8",
        )
        guard.chmod(0o755)

        (self.repo / ".persona-cloud-repository").unlink()
        local = run("bash", "-c", command, cwd=self.repo, env=os.environ)
        self.assertEqual(local.returncode, 0, local.stderr)
        self.assertIn("Local persona session", json.loads(local.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertNotIn("visibility was proven", local.stdout)

        (self.repo / ".persona-cloud-repository").write_text("owner/private-persona\n", encoding="utf-8")
        cloud = run("bash", "-c", command, cwd=self.repo, env=os.environ)
        self.assertEqual(cloud.returncode, 0, cloud.stderr)
        self.assertIn("visibility was proven", json.loads(cloud.stdout)["hookSpecificOutput"]["additionalContext"])

        rejected = run(
            "bash", "-c", command,
            cwd=self.repo,
            env=os.environ | {"GUARD_RESULT": "fail"},
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertNotIn("visibility was proven", rejected.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
