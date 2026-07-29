#!/usr/bin/env python3
"""Public documentation stays executable, current, and privacy-honest."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
TROUBLESHOOTING = ROOT / "TROUBLESHOOTING.md"
EXAMPLE = ROOT / "examples/atlas-sanitized/README.md"
DOCS = (
    README, ROOT / "CONTRIBUTING.md", TROUBLESHOOTING, EXAMPLE,
    ROOT / "CHANGELOG.md", ROOT / "MIGRATION.md", ROOT / "ROLLBACK.md",
    ROOT / "SUPPORT.md", ROOT / "RELEASE.md",
)


class DocumentationTest(unittest.TestCase):
    def test_first_screen_explains_problem_outcome_support_and_install(self) -> None:
        first_screen = README.read_text(encoding="utf-8")[:2400].casefold()
        for phrase in (
            "re-explaining",
            "durable collaborator",
            "claude code local",
            "claude code cloud",
            "codex",
            "/plugin marketplace add kickinrad/personas-framework",
        ):
            self.assertIn(phrase, first_screen)

    def test_quickstarts_and_verification_use_current_interfaces(self) -> None:
        text = README.read_text(encoding="utf-8")
        for heading in ("## Quickstart: Claude Code local", "## Quickstart: Claude Code Cloud", "## Quickstart: Codex"):
            self.assertIn(heading, text)
        self.assertIn("bin/personas verify", text)
        self.assertIn("bin/personas create", text)
        self.assertNotIn("bin/validate-persona", text)
        self.assertNotIn("plugins/" + "persona-manager", text)

    def test_active_docs_do_not_advertise_retired_validation_command(self) -> None:
        active = (
            README, ROOT / "CLAUDE.md", ROOT / "ACTIVATION.md", ROOT / "CONTRIBUTING.md",
            TROUBLESHOOTING, ROOT / "CHANGELOG.md", ROOT / "MIGRATION.md",
            ROOT / "ROLLBACK.md", ROOT / "SUPPORT.md", ROOT / "RELEASE.md",
        )
        for document in active:
            self.assertNotIn("bin/validate-persona", document.read_text(encoding="utf-8"), document)

    def test_cloud_safety_and_remediation_are_prominent(self) -> None:
        text = README.read_text(encoding="utf-8")
        for phrase in (
            "exactly `PRIVATE`",
            "creation",
            "verification",
            "CI",
            "SessionStart",
            "public",
            "internal",
            "unknown",
            "unavailable",
            "ambiguous",
            "credentials",
            "framework repository may be public",
            "personalized Cloud persona repository is private",
            "GH_TOKEN",
            "not pre-installed",
            "least-privilege",
        ):
            self.assertIn(phrase, text)
        self.assertIn("Cloud environment", (ROOT / "SUPPORT.md").read_text(encoding="utf-8"))

    def test_support_covers_expected_recovery_boundaries(self) -> None:
        text = TROUBLESHOOTING.read_text(encoding="utf-8").casefold()
        for phrase in (
            "cancel", "permission", "offline", "collision", "partial", "staging",
            "verification", "unsupported", "recovery",
        ):
            self.assertIn(phrase, text)

    def test_create_quickstart_does_not_claim_the_closed_gap(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("atomically renames", text)
        self.assertIn("writes neither final nor staging", text)
        self.assertIn("gh repo view OWNER/REPO --json visibility --jq .visibility", text)
        self.assertIn(".persona-cloud-repository", text)
        self.assertNotIn("Current gap: creation is skill-driven", text)

    def test_sanitized_example_and_local_links_are_safe(self) -> None:
        example = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("Sanitized", example)
        self.assertNotRegex(example, r"(?i)(token|password|private profile|real integration)")
        for document in DOCS:
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
                if "://" in target or target.startswith("mailto:"):
                    continue
                self.assertTrue((document.parent / target).resolve().exists(), f"{document}: {target}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
