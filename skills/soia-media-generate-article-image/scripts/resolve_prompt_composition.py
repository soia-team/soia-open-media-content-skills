#!/usr/bin/env python3
"""Resolve a natural-language x-separated image prompt query into composition axes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


DEFAULT_INDEX = Path(__file__).resolve().parents[1] / "references" / "prompt-composition-index.yml"


def _norm(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower())


def _alias_table(index: dict[str, Any], axis_id: str) -> list[tuple[str, str]]:
    axis = index["axes"].get(axis_id, {})
    aliases = [(str(k), str(v)) for k, v in (axis.get("aliases") or {}).items()]
    for option_id in (axis.get("options") or {}):
        aliases.append((str(option_id), str(option_id)))
    return sorted(aliases, key=lambda item: len(_norm(item[0])), reverse=True)


def _match_axis(query: str, index: dict[str, Any], axis_id: str) -> tuple[str | None, str | None]:
    normalized_query = _norm(query)
    for alias, value in _alias_table(index, axis_id):
        if _norm(alias) in normalized_query:
            return value, alias
    return None, None


def _fallbacks(result: dict[str, Any]) -> None:
    family_by_use_case = {
        "good_morning": "morning_city",
        "presentation": "presentation_grid",
        "portrait": "portrait_identity",
        "event_poster": "event_people",
        "birthday_poster": "celebration_ceremony",
        "wedding": "celebration_ceremony",
        "hospitality_poster": "hospitality_food",
        "food_beverage": "hospitality_food",
        "archival_print": "archival_print",
    }
    if result.get("family") == "auto" and result.get("use_case") in family_by_use_case:
        result["family"] = family_by_use_case[result["use_case"]]

    structure_by_family = {
        "morning_city": "knowledge_card",
        "presentation_grid": "deck_series",
        "travel_publication": "deck_series",
        "portrait_identity": "portrait_brief",
        "event_people": "campaign_pack",
        "celebration_ceremony": "campaign_pack",
        "hospitality_food": "campaign_pack",
        "archival_print": "knowledge_card",
        "pixel_play": "single_hook",
    }
    if result.get("information_structure") == "auto" and result.get("family") in structure_by_family:
        result["information_structure"] = structure_by_family[result["family"]]

    mechanism_by_family = {
        "archival_print": "archival_collage",
        "portrait_identity": "identity_lock",
        "celebration_ceremony": "mirror_reflection",
        "event_people": "commercial_stage",
        "hospitality_food": "material_closeup",
        "travel_publication": "travel_editorial_narrative",
    }
    if result.get("visual_mechanism") == "auto" and result.get("family") in mechanism_by_family:
        result["visual_mechanism"] = mechanism_by_family[result["family"]]

    aesthetic_by_family = {
        "morning_city": "editorial_aesthetic",
        "poster_type_stage": "bright_modern",
        "presentation_grid": "bright_modern",
        "travel_publication": "travel_publication",
        "archival_print": "archival_historical",
        "portrait_identity": "portrait_editorial",
        "celebration_ceremony": "ceremonial_soft",
        "event_people": "bright_modern",
        "hospitality_food": "hospitality_premium",
        "pixel_play": "playful_pixel",
    }
    if result.get("aesthetic_system") == "auto" and result.get("family") in aesthetic_by_family:
        result["aesthetic_system"] = aesthetic_by_family[result["family"]]

    strategy_by_structure = {
        "knowledge_card": "cjk_exact_text",
        "deck_page": "cjk_exact_text",
        "deck_series": "cjk_exact_text",
        "carousel_sequence": "cjk_exact_text",
        "campaign_pack": "exact_text",
        "portrait_brief": "exact_text",
        "single_hook": "hero_typography",
    }
    if result.get("text_strategy") == "auto" and result.get("information_structure") in strategy_by_structure:
        result["text_strategy"] = strategy_by_structure[result["information_structure"]]


def resolve_query(query: str, index: dict[str, Any]) -> dict[str, Any]:
    axis_ids = [
        "family",
        "model_adapter",
        "use_case",
        "information_structure",
        "asset_role",
        "visual_mechanism",
        "aesthetic_system",
        "text_strategy",
        "batch_strategy",
        "output_mode",
    ]
    result: dict[str, Any] = {
        axis: ("auto" if axis in {"batch_strategy", "output_mode"} else (index["axes"][axis].get("default") or "auto"))
        for axis in axis_ids
    }
    initial_result = dict(result)
    matched: list[dict[str, str]] = []
    matched_axes: set[str] = set()
    references: list[str] = ["prompt-composition-framework.md", index["family_catalog"]]

    for axis_id in axis_ids:
        value, alias = _match_axis(query, index, axis_id)
        if value is None:
            continue
        # “美学提示词” describes a request for an aesthetic, not a concrete
        # system. Keep the family fallback visible instead of reporting the
        # editorial system as if the customer had selected it.
        if axis_id == "aesthetic_system" and alias == "美学提示词":
            continue
        result[axis_id] = value
        matched_axes.add(axis_id)
        matched.append({"axis": axis_id, "alias": alias or "", "value": value})
        option = (index["axes"][axis_id].get("options") or {}).get(value)
        if isinstance(option, dict) and option.get("reference"):
            references.append(str(option["reference"]))

    generic_aesthetic = "美学提示词" in query
    _fallbacks(result)
    if generic_aesthetic and result.get("family") in {
        "morning_city",
        "poster_type_stage",
        "presentation_grid",
        "travel_publication",
        "portrait_identity",
        "celebration_ceremony",
        "hospitality_food",
        "archival_print",
        "pixel_play",
    }:
        # Generic wording asks for the family default; a concrete aesthetic alias wins.
        has_concrete_aesthetic = any(
            alias != "美学提示词" and _norm(alias) in _norm(query)
            for alias, _value in _alias_table(index, "aesthetic_system")
        )
        if not has_concrete_aesthetic:
            family_defaults = {
                "morning_city": "editorial_aesthetic",
                "poster_type_stage": "bright_modern",
                "presentation_grid": "bright_modern",
                "travel_publication": "travel_publication",
                "portrait_identity": "portrait_editorial",
                "celebration_ceremony": "ceremonial_soft",
                "hospitality_food": "hospitality_premium",
                "archival_print": "archival_historical",
                "pixel_play": "playful_pixel",
            }
            result["aesthetic_system"] = family_defaults[result["family"]]
    if result.get("batch_strategy") == "auto":
        if result.get("family") in {"celebration_ceremony", "event_people", "hospitality_food"}:
            result["batch_strategy"] = "campaign_pack"
        else:
            result["batch_strategy"] = "series" if any(token in _norm(query) for token in ("批量", "10张", "10个", "系列", "carousel", "轮播")) else "single"

    defaulted: list[dict[str, str]] = []
    for axis_id in axis_ids:
        value = result.get(axis_id)
        if value in {None, "auto"}:
            continue
        if axis_id not in matched_axes and initial_result.get(axis_id) != value:
            defaulted.append({"axis": axis_id, "value": str(value)})
        option = (index["axes"][axis_id].get("options") or {}).get(value)
        if isinstance(option, dict) and option.get("reference"):
            references.append(str(option["reference"]))

    tokens = [part.strip() for part in re.split(r"(?:×|\bx\b|\n|,|，|/)", query, flags=re.IGNORECASE) if part.strip()]
    known_aliases = {
        _norm(alias)
        for axis_id in axis_ids
        for alias, _value in _alias_table(index, axis_id)
    }
    unresolved = [token for token in tokens if not any(alias and alias in _norm(token) for alias in known_aliases)]
    # The query separator and generic words are not actionable prompt axes.
    unresolved = [token for token in unresolved if _norm(token) not in {"美学提示词", "美学", "提示词", "海报", "图片"}]

    return {
        "query": query,
        "normalized": result,
        "matched": matched,
        "defaulted": defaulted,
        "unresolved_tokens": unresolved,
        "references": list(dict.fromkeys(references)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="x-separated prompt query, e.g. GPT2 x 早安 x 字体蒙版")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--list-supported", action="store_true", help="show the compact customer selection catalog")
    args = parser.parse_args()

    index = yaml.safe_load(args.index.read_text(encoding="utf-8"))
    if args.list_supported:
        payload = {"support_catalog": index["support_catalog"]}
    elif args.query:
        payload = resolve_query(args.query, index)
    else:
        parser.error("provide --query or --list-supported")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.list_supported:
        catalog = payload["support_catalog"]
        print("支持入口：" + json.dumps(catalog["counts"], ensure_ascii=False))
        print("\n交付模板：")
        for item in catalog["supported_delivery_presets"]:
            types = "/".join(item["image_types"])
            print(f"- {item['id']}｜{item['label']}（{types}）：{item['choose_when']}；用法：{item['usage']}")
        print("\nPrompt 家族：")
        for item in catalog["supported_families"]:
            print(f"- {item['id']}｜{item['label']}：{item['choose_when']}；用法：{item['usage']}")
    else:
        print(" + ".join(f"{item['axis']}={item['value']}" for item in payload["matched"]))
        print("load: " + ", ".join(payload["references"]))
        if payload["unresolved_tokens"]:
            print("unresolved: " + ", ".join(payload["unresolved_tokens"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
