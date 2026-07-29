#!/usr/bin/env python3
"""Build a source-grounded facts manifest for a skill-catalog social card."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = 1


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing YAML frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"unterminated YAML frontmatter: {path}")
    value = yaml.safe_load(text[4:end]) or {}
    if not isinstance(value, dict):
        raise ValueError(f"frontmatter must be a mapping: {path}")
    return value


def discover_skills(repo_root: Path) -> list[dict[str, str]]:
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        raise ValueError(f"skills directory not found: {skills_root}")
    records: list[dict[str, str]] = []
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        data = load_frontmatter(skill_file)
        name = str(data.get("name", "")).strip()
        description = str(data.get("description", "")).strip()
        version = str(data.get("version", "")).strip()
        display_label = name
        agent_metadata = skill_file.parent / "agents" / "openai.yaml"
        if agent_metadata.is_file():
            agent_value = yaml.safe_load(agent_metadata.read_text(encoding="utf-8")) or {}
            if isinstance(agent_value, dict):
                interface = agent_value.get("interface", {})
                if isinstance(interface, dict):
                    candidate = str(interface.get("display_name", "")).strip()
                    if candidate:
                        display_label = candidate
        if not name:
            raise ValueError(f"skill name missing: {skill_file}")
        records.append(
            {
                "name": name,
                "display_label": display_label,
                "description": description,
                "version": version,
            }
        )
    if not records:
        raise ValueError(f"no publishable skills found under: {skills_root}")
    return records


def git_output(repo_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def normalize_repository(value: str) -> str:
    repository = value.strip()
    patterns = (
        r"^https?://github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^([^/\s]+/[^/\s]+)$",
    )
    for pattern in patterns:
        match = re.match(pattern, repository)
        if match:
            return match.group(1).removesuffix(".git")
    raise ValueError(
        "repository must be a GitHub owner/name slug or a supported GitHub remote URL"
    )


def detect_repository(repo_root: Path, explicit: str | None) -> str:
    candidate = explicit or git_output(repo_root, "remote", "get-url", "origin")
    if not candidate:
        raise ValueError("cannot determine repository; pass --repository <owner/name>")
    return normalize_repository(candidate)


def detect_package_version(repo_root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        path = repo_root / relative
        if not path.is_file():
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        version = str(value.get("version", "")).strip()
        if version:
            return version
    return "unversioned"


def install_command(repository: str, cta_mode: str, featured_skill: str | None) -> str:
    base = f"npx skills add {repository} -g -a '*'"
    if cta_mode == "featured":
        if not featured_skill:
            raise ValueError("cta_mode=featured requires exactly one featured skill")
        return f"{base} -s {featured_skill} -y"
    return f"{base} -y"


def canonical_fingerprint(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_manifest(
    *,
    repo_root: Path,
    repository: str | None = None,
    package_version: str | None = None,
    claim_mode: str = "total",
    featured_skills: list[str] | None = None,
    cta_mode: str = "all",
    cta_featured_skill: str | None = None,
    label_map: dict[str, str] | None = None,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    all_skills = discover_skills(root)
    skill_names = [item["name"] for item in all_skills]
    labels = label_map or {}
    unknown_labels = sorted(set(labels) - set(skill_names))
    if unknown_labels:
        raise ValueError(f"label map contains unpublished skills: {', '.join(unknown_labels)}")
    for item in all_skills:
        if item["name"] in labels:
            label = str(labels[item["name"]]).strip()
            if not label:
                raise ValueError(f"display label cannot be empty: {item['name']}")
            item["display_label"] = label
    featured = list(dict.fromkeys(featured_skills or []))
    unknown = sorted(set(featured) - set(skill_names))
    if unknown:
        raise ValueError(f"featured skills are not published by this repo: {', '.join(unknown)}")
    if claim_mode == "featured" and not featured:
        raise ValueError("claim_mode=featured requires at least one --featured skill")

    displayed_names = skill_names if claim_mode == "total" else featured
    displayed_set = set(displayed_names)
    displayed_records = [dict(item) for item in all_skills if item["name"] in displayed_set]
    displayed_labels = [item["display_label"] for item in displayed_records]
    if len(displayed_labels) != len(set(displayed_labels)):
        raise ValueError("display labels must be unique within one catalog")
    repository_slug = detect_repository(root, repository)
    featured_cta = cta_featured_skill
    if cta_mode == "featured":
        featured_cta = featured_cta or (featured[0] if len(featured) == 1 else None)
        if featured_cta not in skill_names:
            raise ValueError("featured CTA skill must be published by this repo")
    command = install_command(repository_slug, cta_mode, featured_cta)

    source = {
        "repository": repository_slug,
        "repository_url": f"https://github.com/{repository_slug}",
        "package_version": detect_package_version(root, package_version),
        "commit": git_output(root, "rev-parse", "--short=12", "HEAD") or "unknown",
        "as_of_date": as_of_date or date.today().isoformat(),
    }
    catalog = {
        "claim_mode": claim_mode,
        "total_skill_count": len(all_skills),
        "displayed_skill_count": len(displayed_records),
        "claim_text": (
            f"当前已提供 {len(all_skills)} 个技能"
            if claim_mode == "total"
            else f"精选 {len(displayed_records)} 个技能"
        ),
        "all_skills": all_skills,
        "displayed_skills": displayed_records,
    }
    cta = {
        "mode": cta_mode,
        "featured_skill": featured_cta,
        "install_command": command,
        "repository_url": source["repository_url"],
    }
    fingerprint_input = {"source": source, "catalog": catalog, "cta": cta}
    return {
        "schema_version": SCHEMA_VERSION,
        **fingerprint_input,
        "content_fingerprint": canonical_fingerprint(fingerprint_input),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Skill repository root.")
    parser.add_argument("--repository", help="GitHub owner/name; otherwise detect origin.")
    parser.add_argument("--package-version", help="Override the package/plugin version.")
    parser.add_argument("--claim-mode", choices=("total", "featured"), default="total")
    parser.add_argument("--featured", action="append", default=[], help="Featured skill; repeatable.")
    parser.add_argument("--cta-mode", choices=("all", "featured"), default="all")
    parser.add_argument("--cta-featured-skill", help="Skill installed by a featured CTA.")
    parser.add_argument("--label-map", type=Path, help="Optional YAML mapping: skill name -> display label.")
    parser.add_argument("--as-of-date", help="Explicit YYYY-MM-DD source date.")
    parser.add_argument("--output", type=Path, help="Write YAML here; stdout when omitted.")
    args = parser.parse_args()

    try:
        label_map: dict[str, str] | None = None
        if args.label_map:
            raw_labels = yaml.safe_load(args.label_map.read_text(encoding="utf-8")) or {}
            if not isinstance(raw_labels, dict):
                raise ValueError("label map must be a YAML mapping")
            label_map = {str(key): str(value) for key, value in raw_labels.items()}
        manifest = build_manifest(
            repo_root=args.repo,
            repository=args.repository,
            package_version=args.package_version,
            claim_mode=args.claim_mode,
            featured_skills=args.featured,
            cta_mode=args.cta_mode,
            cta_featured_skill=args.cta_featured_skill,
            label_map=label_map,
            as_of_date=args.as_of_date,
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rendered = yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=4096)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
