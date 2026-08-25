#!/usr/bin/env python3
"""Validate repository identities and direct relationships across the workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence

from bootstrap_workspace import load_manifest, resolve_workspace_root, validate_entry


def parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith(('"', '[')) or raw in {"null", "true", "false"}:
        return json.loads(raw)
    return raw


def parse_metadata(path: Path) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        section = re.fullmatch(r"([a-z_]+):\s*", line)
        if section:
            current = section.group(1)
            sections.setdefault(current, {})
            continue
        field = re.fullmatch(r"  ([a-z_]+):\s*(.+)", line)
        if field and current:
            sections[current][field.group(1)] = parse_value(field.group(2))
    return sections


def normalize_github_remote(remote: str) -> str | None:
    patterns = (
        r"https://github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, remote.strip())
        if match:
            return match.group(1)
    return None


def git_remote(path: Path) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=path,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def parent_cycle_errors(parents: Mapping[str, str | None]) -> list[str]:
    errors: list[str] = []
    visited: set[str] = set()
    for start in sorted(parents):
        if start in visited:
            continue
        path: list[str] = []
        positions: dict[str, int] = {}
        current: str | None = start
        while current is not None and current in parents:
            if current in positions:
                cycle = path[positions[current]:] + [current]
                errors.append("parent cycle: " + " -> ".join(cycle))
                break
            if current in visited:
                break
            positions[current] = len(path)
            path.append(current)
            current = parents[current]
        visited.update(path)
    return errors


def run_repository_validator(path: Path) -> str | None:
    validator = path / "scripts" / "validate_repository.py"
    if not validator.is_file():
        return None
    result = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--root",
            str(path),
            "--check-sensitive-patterns",
        ],
        cwd=path,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return None
    detail = result.stderr.strip() or result.stdout.strip()
    return detail


def validate(root: Path, repositories: Sequence[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    manifest_ids: set[str] = set()
    manifest_directories: set[str] = set()
    metadata_ids: dict[str, str] = {}
    parents: dict[str, str | None] = {}
    relations_by_project: dict[str, list[str]] = {}

    for repository in repositories:
        try:
            validate_entry(repository)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        project_id = repository["id"]
        directory = repository["directory"]
        if project_id in manifest_ids:
            errors.append(f"duplicate manifest project ID: {project_id}")
        if directory in manifest_directories:
            errors.append(f"duplicate local directory: {directory}")
        manifest_ids.add(project_id)
        manifest_directories.add(directory)
        if repository["visibility"] != "public" and repository["auto_clone"]:
            errors.append(f"private repository is auto-clone enabled: {project_id}")

    for repository in repositories:
        path = root / repository["directory"]
        if not path.exists():
            if repository["required"]:
                errors.append(f"required repository is missing: {repository['id']}")
            continue
        if not (path / ".git").exists():
            errors.append(f"not a Git repository: {repository['id']}")
            continue
        actual_remote = normalize_github_remote(git_remote(path))
        if actual_remote is None or actual_remote.casefold() != repository["github"].casefold():
            errors.append(
                f"remote mismatch for {repository['id']}: "
                f"expected {repository['github']}，found {actual_remote or 'unrecognized'}"
            )

        metadata_path = path / ".ephy" / "project.yaml"
        if not metadata_path.is_file():
            if str(repository["id"]).startswith("ephy"):
                errors.append(f"missing project metadata: {repository['id']}")
            continue
        metadata = parse_metadata(metadata_path)
        project = metadata.get("project", {})
        relations = metadata.get("relations", {})
        declared_id = project.get("id")
        if declared_id != repository["id"]:
            errors.append(
                f"canonical ID mismatch for {repository['id']}: {declared_id!r}"
            )
        if isinstance(declared_id, str):
            if declared_id in metadata_ids:
                errors.append(
                    f"duplicate metadata project ID {declared_id}: "
                    f"{metadata_ids[declared_id]} and {repository['directory']}"
                )
            metadata_ids[declared_id] = repository["directory"]
            parent = relations.get("parent")
            parents[declared_id] = parent if isinstance(parent, str) else None
            direct_relations: list[str] = []
            if isinstance(parent, str):
                direct_relations.append(parent)
                if parent == declared_id:
                    errors.append(f"self-parent: {declared_id}")
            for field in ("depends_on", "integrates_with", "runs_on"):
                value = relations.get(field, [])
                if isinstance(value, list):
                    direct_relations.extend(
                        relation for relation in value if isinstance(relation, str)
                    )
            relations_by_project[declared_id] = direct_relations

        validator_error = run_repository_validator(path)
        if validator_error:
            errors.append(f"repository validator failed for {repository['id']}:\n{validator_error}")

    for project_id, relations in sorted(relations_by_project.items()):
        for relation in relations:
            if relation not in manifest_ids:
                errors.append(f"unresolved relation: {project_id} -> {relation}")
    errors.extend(parent_cycle_errors(parents))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="workspace root; defaults to the parent of ephy")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = resolve_workspace_root(args.root)
        errors = validate(root, load_manifest())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ecosystem validation failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Ephy ecosystem validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Ephy ecosystem validation passed．")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
