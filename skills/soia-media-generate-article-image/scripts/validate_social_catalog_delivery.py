#!/usr/bin/env python3
"""Validate a rendered skill-catalog social-card delivery against its facts."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = SKILL_ROOT / "references" / "social-card-contract.yml"


def load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def validate_delivery(
    facts: dict[str, Any], delivery: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if facts.get("schema_version") != 1:
        errors.append("facts.schema_version must be 1")
    if delivery.get("schema_version") != 1:
        errors.append("delivery.schema_version must be 1")

    for key in ("repository", "package_version"):
        expected = nested(facts, "source", key)
        actual = nested(delivery, "source", key)
        if actual != expected:
            errors.append(f"source.{key} mismatch: expected {expected!r}, got {actual!r}")
    expected_fingerprint = facts.get("content_fingerprint")
    if nested(delivery, "source", "content_fingerprint") != expected_fingerprint:
        errors.append("source.content_fingerprint does not match facts")

    expected_records = nested(facts, "catalog", "displayed_skills") or []
    expected_skills = [item["name"] for item in expected_records]
    expected_labels = [item["display_label"] for item in expected_records]
    slides = nested(delivery, "presentation", "slides") or []
    if not isinstance(slides, list):
        errors.append("presentation.slides must be a list")
        slides = []
    displayed: list[str] = []
    roles: list[str] = []
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            errors.append(f"presentation.slides[{index}] must be a mapping")
            continue
        role_values = slide.get("roles")
        if role_values is None:
            role_values = [slide.get("role", "")]
        if not isinstance(role_values, list):
            errors.append(f"presentation.slides[{index}].roles must be a list")
            role_values = []
        slide_roles = [str(role) for role in role_values if str(role)]
        roles.extend(slide_roles)
        skills = slide.get("displayed_skills", []) or []
        if not isinstance(skills, list):
            errors.append(f"slide {index} displayed_skills must be a list")
            continue
        displayed.extend(str(item) for item in skills)

    if Counter(displayed) != Counter(expected_skills):
        errors.append("displayed skill names/counts do not exactly match the facts manifest")
    duplicates = sorted(name for name, count in Counter(displayed).items() if count > 1)
    if duplicates:
        errors.append(f"skills appear on more than one catalog slide: {', '.join(duplicates)}")

    platform = nested(delivery, "presentation", "platform")
    layout_mode = nested(delivery, "presentation", "layout_mode")
    platform_contract = nested(contract, "platforms", str(platform))
    if not isinstance(platform_contract, dict):
        errors.append(f"unsupported platform: {platform!r}")
    else:
        modes = platform_contract.get("layout_modes", {})
        mode_contract = modes.get(layout_mode) if isinstance(modes, dict) else None
        if not isinstance(mode_contract, dict):
            errors.append(f"unsupported layout_mode {layout_mode!r} for platform {platform!r}")
        else:
            expected_aspect = mode_contract.get("aspect")
            if nested(delivery, "presentation", "aspect") != expected_aspect:
                errors.append(f"presentation.aspect must be {expected_aspect}")
            minimum_slides = int(mode_contract.get("min_slides", 1))
            maximum_slides = int(mode_contract.get("max_slides", minimum_slides))
            if not minimum_slides <= len(slides) <= maximum_slides:
                errors.append(
                    f"presentation must contain {minimum_slides}..{maximum_slides} slides; got {len(slides)}"
                )
            maximum = int(mode_contract.get("max_catalog_items_per_slide", 0))
            for index, slide in enumerate(slides, start=1):
                if not isinstance(slide, dict):
                    continue
                slide_roles = slide.get("roles") or [slide.get("role")]
                if "catalog" not in slide_roles:
                    continue
                count = len(slide.get("displayed_skills", []) or [])
                if count > maximum:
                    errors.append(
                        f"catalog slide {index} has {count} items; maximum is {maximum}"
                    )
            required_roles = mode_contract.get("required_roles", []) or []
            missing_roles = [role for role in required_roles if role not in roles]
            if missing_roles:
                errors.append(f"missing required slide roles: {', '.join(missing_roles)}")

    expected_text = {
        "claim": nested(facts, "catalog", "claim_text"),
        "skill_labels": expected_labels,
        "install_command": nested(facts, "cta", "install_command"),
        "repository_url": nested(facts, "cta", "repository_url"),
    }
    observed_text = nested(delivery, "observed", "exact_text")
    if observed_text != expected_text:
        errors.append("observed.exact_text does not exactly match source-grounded facts")

    expected_cta = nested(facts, "cta", "install_command")
    if nested(delivery, "cta", "install_command") != expected_cta:
        errors.append("CTA install command does not match facts")
    expected_url = nested(facts, "cta", "repository_url")
    if nested(delivery, "cta", "repository_url") != expected_url:
        errors.append("CTA repository URL does not match facts")
    qr_target = nested(delivery, "cta", "qr_target")
    decoded_target = nested(delivery, "quality", "qr_decoded_target")
    if qr_target and decoded_target != qr_target:
        errors.append("QR decoder result does not match cta.qr_target")

    required_quality = contract.get("required_quality_evidence", []) or []
    for key in required_quality:
        if nested(delivery, "quality", str(key)) is not True:
            errors.append(f"quality.{key} must be true")
    if nested(delivery, "quality", "renderer") != "deterministic-compositor":
        errors.append("quality.renderer must be deterministic-compositor")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--delivery", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    try:
        facts = load_mapping(args.facts)
        delivery = load_mapping(args.delivery)
        contract = load_mapping(args.contract)
        errors = validate_delivery(facts, delivery, contract)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: delivery matches facts, platform density, CTA, QR, and quality evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
