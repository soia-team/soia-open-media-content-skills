#!/usr/bin/env python3
"""Compile and validate a multi-repository social-card series scope."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from build_social_catalog_facts import build_manifest, normalize_repository


def load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def resolve_input_path(spec_path: Path, value: object) -> Path:
    candidate = Path(str(value)).expanduser()
    if not candidate.is_absolute():
        candidate = spec_path.parent / candidate
    return candidate.resolve()


def load_label_map(spec_path: Path, value: object) -> dict[str, str] | None:
    if not value:
        return None
    mapping = load_mapping(resolve_input_path(spec_path, value))
    return {str(key): str(label) for key, label in mapping.items()}


def fingerprint(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_batch(spec_path: Path) -> dict[str, Any]:
    spec = load_mapping(spec_path)
    if spec.get("schema_version") != 1:
        raise ValueError("batch spec schema_version must be 1")
    series_id = str(spec.get("series_id", "")).strip()
    if not series_id:
        raise ValueError("batch spec requires series_id")
    include = spec.get("include", [])
    if not isinstance(include, list) or not include:
        raise ValueError("batch spec include must be a non-empty list")
    excluded = [normalize_repository(str(value)) for value in spec.get("exclude", []) or []]
    if len(excluded) != len(set(excluded)):
        raise ValueError("batch spec exclude contains duplicate repositories")
    as_of_date = str(spec["as_of_date"]) if spec.get("as_of_date") else None

    catalogs: list[dict[str, Any]] = []
    included_repositories: list[str] = []
    for index, item in enumerate(include, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"include[{index}] must be a mapping")
        repository = normalize_repository(str(item.get("repository", "")))
        if repository in excluded:
            raise ValueError(f"repository is both included and excluded: {repository}")
        if repository in included_repositories:
            raise ValueError(f"duplicate included repository: {repository}")
        repo_value = item.get("repo")
        if not repo_value:
            raise ValueError(f"include[{index}] requires repo")
        manifest = build_manifest(
            repo_root=resolve_input_path(spec_path, repo_value),
            repository=repository,
            package_version=(str(item["package_version"]) if item.get("package_version") else None),
            claim_mode=str(item.get("claim_mode", "total")),
            featured_skills=[str(value) for value in item.get("featured_skills", []) or []],
            cta_mode=str(item.get("cta_mode", "all")),
            cta_featured_skill=(
                str(item["cta_featured_skill"]) if item.get("cta_featured_skill") else None
            ),
            label_map=load_label_map(spec_path, item.get("label_map")),
            as_of_date=as_of_date,
        )
        included_repositories.append(repository)
        catalogs.append(manifest)

    batch_core = {
        "series_id": series_id,
        "platform": str(spec.get("platform", "general")),
        "slide_count": spec.get("slide_count", "auto"),
        "as_of_date": as_of_date,
        "included_repositories": included_repositories,
        "excluded_repositories": excluded,
        "repository_count": len(catalogs),
        "total_skill_count": sum(item["catalog"]["total_skill_count"] for item in catalogs),
        "catalogs": catalogs,
    }
    return {
        "schema_version": 1,
        **batch_core,
        "batch_fingerprint": fingerprint(batch_core),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Write YAML here; stdout when omitted.")
    args = parser.parse_args()
    try:
        batch = build_batch(args.spec.resolve())
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = yaml.safe_dump(batch, allow_unicode=True, sort_keys=False, width=4096)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
