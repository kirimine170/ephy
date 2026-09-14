from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from bootstrap_workspace import bootstrap, load_manifest
from validate_ecosystem import parent_cycle_errors


class WorkspaceToolTests(unittest.TestCase):
    def test_manifest_has_unique_ids_and_no_private_auto_clone(self) -> None:
        repositories = load_manifest()
        identifiers = [repository["id"] for repository in repositories]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(any(repository["id"] == "ephy-model" for repository in repositories))
        for repository in repositories:
            if repository["visibility"] != "public":
                self.assertFalse(repository["auto_clone"])

    def test_parent_cycle_detection(self) -> None:
        self.assertEqual(
            parent_cycle_errors({"ephy-a": "ephy-b", "ephy-b": "ephy-a"}),
            ["parent cycle: ephy-a -> ephy-b -> ephy-a"],
        )

    def test_dry_run_does_not_create_repositories_or_git_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            arguments = argparse.Namespace(
                include_private=False,
                include_optional=False,
                dry_run=True,
            )
            failures = bootstrap(root, load_manifest(), arguments)
            self.assertEqual(failures, 0)
            self.assertFalse((root / ".git").exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_workspace_status_is_read_only_for_empty_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "workspace_status.py"),
                    "--root",
                    temporary,
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(temporary).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
