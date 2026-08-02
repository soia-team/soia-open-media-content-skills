#!/usr/bin/env python3
"""Audit a bounded X-profile Prompt Deck against the image composition catalog.

This is a local comparison step, not an X collector and not an image generator.
It reports coverage, unsupported composition values, per-family axis drift, and
source-evidence coverage without copying source posts into the public checkout.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "references" / "prompt-composition-index.yml"
AXIS_FIELDS = (
    "family",
    "use_case",
    "information_structure",
    "visual_mechanism",
    "aesthetic_system",
    "text_strategy",
    "model_adapter",
    "batch_strategy",
    "aspect",
    "render_mode",
)
SERIES_AXIS_FIELDS = (
    "information_structure",
    "visual_mechanism",
    "aesthetic_system",
    "text_strategy",
    "batch_strategy",
    "aspect",
)
ALT_RE = re.compile(r"含 ALT 提示词：\s*(\d+)\s*条")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def axis_values(index: dict[str, Any], axis: str) -> set[str]:
    if axis == "family":
        return {
            text(item.get("id"))
            for item in index.get("support_catalog", {}).get("supported_families", [])
            if isinstance(item, dict) and text(item.get("id"))
        }
    options = index.get("axes", {}).get(axis, {}).get("options", {})
    return {text(value) for value in options if text(value)}


def axis_counts(items: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for axis in SERIES_AXIS_FIELDS:
        counts = Counter(text((item.get("composition_axes") or {}).get(axis)) for item in items)
        result[axis] = {value: counts[value] for value in sorted(counts) if value}
    return result


def stable_and_variant_axes(items: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, dict[str, int]]]:
    observations = axis_counts(items)
    stable = {
        axis: next(iter(values))
        for axis, values in observations.items()
        if len(values) == 1
    }
    variants = {
        axis: values
        for axis, values in observations.items()
        if len(values) > 1
    }
    return stable, variants


def prompt_alt_count(deck_root: Path, item: dict[str, Any]) -> int:
    prompt_file = deck_root / text(item.get("prompt_file"))
    if not prompt_file.is_file():
        return 0
    match = ALT_RE.search(prompt_file.read_text(encoding="utf-8"))
    return int(match.group(1)) if match else 0


def audit(deck: dict[str, Any], index: dict[str, Any], manifest: dict[str, Any] | None, deck_root: Path) -> dict[str, Any]:
    items = [item for item in deck.get("items", []) if isinstance(item, dict)]
    unsupported: dict[str, dict[str, int]] = {}
    value_counts: dict[str, dict[str, int]] = {}
    for axis in AXIS_FIELDS:
        counts = Counter(text((item.get("composition_axes") or {}).get(axis)) for item in items)
        value_counts[axis] = {value: counts[value] for value in sorted(counts) if value}
        supported = axis_values(index, axis)
        if not supported:
            continue
        unsupported[axis] = {
            value: count for value, count in value_counts[axis].items() if value not in supported
        }
        if not unsupported[axis]:
            unsupported.pop(axis)

    by_family: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        family = text((item.get("composition_axes") or {}).get("family")) or text(item.get("family")) or "unknown"
        by_family.setdefault(family, []).append(item)
    family_drift: dict[str, dict[str, Any]] = {}
    for family, family_items in sorted(by_family.items()):
        stable, variants = stable_and_variant_axes(family_items)
        family_drift[family] = {
            "count": len(family_items),
            "stable_axes": stable,
            "variant_axes": variants,
            "axis_drift": {axis: sorted(values) for axis, values in variants.items()},
        }

    manifest_coverage = manifest.get("coverage", {}) if isinstance(manifest, dict) else {}
    alt_items = sum(1 for item in items if prompt_alt_count(deck_root, item) > 0)
    alt_count = sum(prompt_alt_count(deck_root, item) for item in items)
    gpt2_items = sum(1 for item in items if item.get("is_gpt2") is True)
    complete = manifest_coverage.get("complete") if isinstance(manifest_coverage, dict) else None
    status = "PASS" if not unsupported else "GAP"
    if complete is not True and status == "PASS":
        status = "PASS_WITH_COVERAGE_LIMIT"
    return {
        "schema_version": 1,
        "status": status,
        "source_profile": deck.get("source_profile"),
        "source_skill": deck.get("source_skill"),
        "image_skill": deck.get("image_skill"),
        "boundary": {
            "provider": manifest.get("provider") if isinstance(manifest, dict) else None,
            "requested_latest": manifest_coverage.get("requested_latest"),
            "fetched": manifest_coverage.get("fetched"),
            "selected": manifest_coverage.get("selected"),
            "complete": complete,
        },
        "coverage": {
            "deck_items": len(items),
            "gpt2_items": gpt2_items,
            "family_counts": {family: len(values) for family, values in sorted(by_family.items())},
            "axis_counts": value_counts,
            "image_alt_items": alt_items,
            "image_alt_count": alt_count,
            "body_only_items": len(items) - alt_items,
        },
        "unsupported_axes": unsupported,
        "family_drift": family_drift,
        "catalog": {
            "prompt_families": len(index.get("support_catalog", {}).get("supported_families", [])),
            "prompt_source_routes": len(index.get("support_catalog", {}).get("prompt_source_routes", [])),
        },
    }


def markdown(report: dict[str, Any]) -> str:
    boundary = report["boundary"]
    coverage = report["coverage"]
    lines = [
        "# X Prompt Deck → image 技能差距审计",
        "",
        f"- 状态：`{report['status']}`",
        f"- 账号：`{report.get('source_profile')}`",
        f"- provider：`{boundary.get('provider') or '未提供'}`",
        f"- 边界：抓取 {boundary.get('fetched') or '未知'} 条，筛选 {boundary.get('selected') or coverage['deck_items']} 条；complete=`{boundary.get('complete')}`",
        "",
        "## 覆盖",
        "",
        f"- Prompt Deck 项目：{coverage['deck_items']}；GPT2 命中：{coverage['gpt2_items']}",
        f"- 图片 ALT 证据：{coverage['image_alt_items']} 条帖子 / {coverage['image_alt_count']} 条媒体；正文证据：{coverage['body_only_items']} 条帖子",
        f"- 家族：{len(coverage['family_counts'])} 个；当前目录登记家族：{report['catalog']['prompt_families']} 个；外部导入路线：{report['catalog']['prompt_source_routes']} 条",
        "",
        "### 家族数量",
        "",
    ]
    for family, count in coverage["family_counts"].items():
        lines.append(f"- `{family}`：{count}")
    lines.extend(["", "## 未支持组合轴", ""])
    if report["unsupported_axes"]:
        for axis, values in report["unsupported_axes"].items():
            lines.append(f"- `{axis}`：{values}")
    else:
        lines.append("- 无；当前筛选集的组合轴均可由 image 技能索引表达。")
    lines.extend(["", "## 家族内轴漂移", ""])
    drift_count = 0
    for family, data in report["family_drift"].items():
        if not data["variant_axes"]:
            continue
        drift_count += 1
        lines.append(f"- `{family}`（{data['count']} 条）：{json.dumps(data['axis_drift'], ensure_ascii=False, sort_keys=True)}")
    if not drift_count:
        lines.append("- 无明显漂移。")
    lines.extend([
        "",
        "## 结论",
        "",
        "- GPT2 是来源模型标签，不新增 GPT2 专属 preset；应沿用 family + 组合轴 + Prompt Deck 导入路线。",
        "- `complete=false` 时只能描述 provider 返回窗口，不能宣称账号历史全量。",
        "- 有轴漂移的家族必须按单条记录选择 variant，不能拿第一条记录覆盖整个系列。",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="source image-prompts.yml")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--output", type=Path, help="write Markdown report; omit to print JSON")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    deck = load_yaml(args.input)
    index = load_yaml(args.index)
    if not isinstance(deck, dict) or deck.get("source_skill") != "soia-pkm-clip-x-profile":
        parser.error("input must be a soia-pkm-clip-x-profile image-prompts.yml")
    if not isinstance(index, dict):
        parser.error("index must be a YAML mapping")
    manifest_path = args.input.parent / "manifest.yml"
    manifest = load_yaml(manifest_path) if manifest_path.is_file() else None
    report = audit(deck, index, manifest, args.input.parent)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown(report), encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
