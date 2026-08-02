#!/usr/bin/env python3
"""Compile a bounded X-profile Prompt Deck into image-skill evolution layers.

This is an import/compile step, not an image generator. It verifies the public
source bundle, separates the reusable visual base from topic seasoning and
series variables, and emits image-skill-ready prompts plus a manifest. It never
fetches X, reads cookies, or silently repairs missing source evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVOLUTION = ROOT / "references" / "x-profile-prompt-evolution.yml"
REQUIRED_AXES = (
    "family",
    "use_case",
    "information_structure",
    "visual_mechanism",
    "aesthetic_system",
    "text_strategy",
    "model_adapter",
    "batch_strategy",
    "aspect",
)
REQUIRED_BLOCKS = (
    "source_grounding",
    "primary_task",
    "composition_and_layout",
    "visual_style_and_materials",
    "exact_text",
    "aspect_and_output",
    "constraints_and_avoid",
)
SERIES_AXIS_FIELDS = (
    "information_structure",
    "visual_mechanism",
    "aesthetic_system",
    "text_strategy",
    "batch_strategy",
    "aspect",
)
HEADING_RE = re.compile(r"^##\s+([^\n]+)\s*$", re.MULTILINE)


def load_yaml(path: Path) -> Any:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing input: {path}") from exc
    if value is None:
        raise ValueError(f"empty YAML: {path}")
    return value


def write_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# JSON-compatible YAML; parse with any YAML 1.2 loader.\n"
        + json.dumps(value, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def slugify(value: str, limit: int = 72) -> str:
    value = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", str(value)).strip("-")
    return (value or "x-post")[:limit]


def parse_prompt_blocks(path: Path) -> dict[str, str]:
    """Read the seven canonical blocks from a Prompt Deck markdown file."""
    content = path.read_text(encoding="utf-8")
    headings = list(HEADING_RE.finditer(content))
    blocks: dict[str, str] = {}
    for index, match in enumerate(headings):
        heading = match.group(1).strip()
        key = heading if heading in REQUIRED_BLOCKS else None
        if not key:
            continue
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
        body = content[start:end].strip()
        blocks[key] = body
    return blocks


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def source_selection(data: dict[str, Any]) -> dict[str, Any]:
    selection = data.get("selection")
    return selection if isinstance(selection, dict) else {}


def validate_source_manifest(data: dict[str, Any], deck_root: Path) -> tuple[dict[str, Any], list[str]]:
    """Verify the adjacent X-profile run manifest before compiling prompts."""
    errors: list[str] = []
    manifest_path = deck_root / "manifest.yml"
    try:
        manifest = load_yaml(manifest_path)
    except ValueError as exc:
        return {}, [str(exc)]
    if not isinstance(manifest, dict):
        return {}, ["manifest.yml must contain a mapping"]
    if manifest.get("skill") != "soia-pkm-clip-x-profile":
        errors.append("manifest.yml: skill must be soia-pkm-clip-x-profile")
    if manifest.get("source") and manifest.get("source") != data.get("source_profile"):
        errors.append("manifest.yml: source does not match image-prompts.yml.source_profile")
    selection = source_selection(data)
    filters = selection.get("filters")
    request = manifest.get("request")
    manifest_filters = request.get("filters") if isinstance(request, dict) else None
    if not isinstance(filters, dict):
        errors.append("image-prompts.yml: selection.filters is required")
    elif manifest_filters != filters:
        errors.append("manifest.yml: request.filters does not match image-prompts.yml.selection.filters")
    coverage = manifest.get("coverage")
    selected = selection.get("selected")
    if not isinstance(coverage, dict):
        errors.append("manifest.yml: coverage is required")
    elif isinstance(selected, int) and coverage.get("selected") != selected:
        errors.append("manifest.yml: coverage.selected does not match image-prompts.yml.selection.selected")
    return manifest, errors


def validate_item(item: dict[str, Any], deck_root: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    item_id = as_text(item.get("source_status_id")) or "missing-status-id"
    for field in ("source_status_id", "source_url", "prompt_file", "source_prompt"):
        if not as_text(item.get(field)):
            errors.append(f"{item_id}: missing {field}")
    axes = item.get("composition_axes")
    if not isinstance(axes, dict):
        errors.append(f"{item_id}: missing composition_axes")
        axes = {}
    for axis in REQUIRED_AXES:
        if not as_text(axes.get(axis)) or axes.get(axis) == "auto":
            errors.append(f"{item_id}: missing composition_axes.{axis}")
    prompt_file = deck_root / as_text(item.get("prompt_file"))
    if not prompt_file.is_file():
        errors.append(f"{item_id}: missing prompt file {item.get('prompt_file')}")
        return {}, errors
    blocks = parse_prompt_blocks(prompt_file)
    for block in REQUIRED_BLOCKS:
        if not as_text(blocks.get(block)):
            errors.append(f"{item_id}: missing prompt block {block}")
    return blocks, errors


def family_definition(evolution: dict[str, Any], family: str) -> dict[str, Any]:
    families = evolution.get("observed_families") or {}
    value = families.get(family)
    if isinstance(value, dict):
        return value
    fallback = evolution.get("fallback_family")
    return fallback if isinstance(fallback, dict) else {}


def bullet_lines(values: Any) -> str:
    if isinstance(values, list):
        return "\n".join(f"- {as_text(value)}" for value in values if as_text(value))
    return f"- {as_text(values)}" if as_text(values) else "- 未提供"


def axis_counts(items: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Return deterministic per-family axis counts instead of treating the first item as canonical."""
    result: dict[str, dict[str, int]] = {}
    for axis in SERIES_AXIS_FIELDS:
        counts = Counter(as_text(item["composition_axes"].get(axis)) for item in items)
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


def extract_source_layers(source_prompt: str) -> dict[str, Any]:
    """Extract bounded evidence slices without treating the source as a final prompt."""
    fenced = re.findall(r"```(?:yaml|text)?\s*(.*?)```", source_prompt, flags=re.IGNORECASE | re.DOTALL)
    base_excerpt = (fenced[0] if fenced else source_prompt[:1400]).strip()
    remainder = source_prompt
    if fenced:
        first = fenced[0].strip()
        position = source_prompt.find(first)
        if position >= 0:
            remainder = source_prompt[position + len(first) :]
    segments = [part.strip() for part in re.split(r"(?:——————|—{4,}|\n\s*---+\s*\n)", remainder) if part.strip()]
    focused_segments = [
        segment
        for segment in segments
        if re.search(r"^\s*(?:做成|主题\s*[:：]|用途\s*[:：])", segment, flags=re.IGNORECASE)
    ]
    if not focused_segments:
        focused_segments = [
            segment
            for segment in segments
            if re.search(r"比例|画幅|一共\s*\d+", segment, flags=re.IGNORECASE)
        ]
    seasoning_segments = [segment.replace("```", "").strip()[:900] for segment in focused_segments[:3]]
    return {
        "base_excerpt": base_excerpt[:1800],
        "seasoning_excerpts": seasoning_segments,
        "base_detected": bool(fenced),
        "seasoning_segment_count": len(seasoning_segments),
    }


def compile_item(
    item: dict[str, Any],
    blocks: dict[str, str],
    selection: dict[str, Any],
    evolution: dict[str, Any],
) -> dict[str, Any]:
    axes = dict(item["composition_axes"])
    family = as_text(axes.get("family")) or "poster_type_stage"
    family_def = family_definition(evolution, family)
    source_prompt = as_text(item.get("source_prompt"))
    source_layers = extract_source_layers(source_prompt)
    visible_title = as_text(item.get("visible_title")) or f"X post {item['source_status_id']}"
    is_model_label = bool(item.get("is_gpt2")) or axes.get("model_adapter") == "external_gpt_image_label"
    base_visual_system = family_def.get("base_visual_system") or evolution["fallback_family"]["base_visual_system"]
    topic_seasoning = family_def.get("topic_seasoning") or evolution["fallback_family"]["topic_seasoning"]
    series_variables = family_def.get("series_variables") or evolution["fallback_family"]["series_variables"]
    render_mode = as_text(axes.get("render_mode")) or "hybrid_exact_text"
    image_type = "carousel" if axes.get("output_mode") in {"carousel", "campaign_pack"} else "poster"
    output_mode = as_text(axes.get("output_mode")) or image_type

    render_prompt = "\n".join(
        [
            f"Create a source-grounded {family} {image_type} from the selected X Prompt Deck item.",
            "",
            "SOURCE GROUNDING",
            f"- Source profile selection: {json.dumps(selection, ensure_ascii=False, sort_keys=True)}",
            f"- Source URL: {as_text(item.get('source_url'))}",
            f"- Visible topic title: {visible_title}",
            f"- Model label policy: {'GPT2 is provenance only; do not draw it unless exact_text requires it.' if is_model_label else 'No model dependency is implied.'}",
            "",
            "BASE VISUAL SYSTEM (stable across the family/series)",
            bullet_lines(base_visual_system),
            "",
            "TOPIC SEASONING (derived from the selected source item)",
            bullet_lines(topic_seasoning),
            "- Interpret only the bounded source seasoning evidence below; do not copy author wording or invent facts:",
            bullet_lines(source_layers["seasoning_excerpts"] or [visible_title]),
            "",
            "SOURCE EVIDENCE POLICY",
            "- Raw source prompt evidence is retained in source_visual_evidence/source_prompt_evidence; do not paste it into the execution prompt.",
            "",
            "SERIES VARIABLES",
            bullet_lines(series_variables),
            "- Keep the base system fixed and change no more than 2–4 variables for a comparable series.",
            "",
            "CANONICAL IMAGE-SKILL BLOCKS",
            blocks["source_grounding"],
            blocks["primary_task"],
            blocks["composition_and_layout"],
            blocks["visual_style_and_materials"],
            blocks["exact_text"],
            blocks["aspect_and_output"],
            blocks["constraints_and_avoid"],
            "",
            "RENDER MODE",
            f"Use {render_mode}. Save a real PNG/JPG and run view_image, exact-text checks, and mobile thumbnail review.",
        ]
    )
    return {
        "source_status_id": as_text(item["source_status_id"]),
        "source_url": as_text(item["source_url"]),
        "visible_title": visible_title,
        "source_prompt": source_prompt,
        "selection": selection,
        "composition_axes": axes,
        "layers": {
            "base_visual_system": base_visual_system,
            "topic_seasoning": topic_seasoning,
            "series_variables": series_variables,
            "source_base_evidence": source_layers["base_excerpt"],
            "source_seasoning_evidence": source_layers["seasoning_excerpts"],
            "source_parse": {
                "base_detected": source_layers["base_detected"],
                "seasoning_segment_count": source_layers["seasoning_segment_count"],
            },
        },
        "prompt_blocks": blocks,
        "render_plan": {
            "source": "x-profile-export",
            "image_type": image_type,
            "output_mode": output_mode,
            "render_mode": render_mode,
            "model_label_is_provenance": is_model_label,
            "source_evidence_artifact": "source_visual_evidence + source_prompt_evidence",
            "raw_source_evidence_in_execution_prompt": False,
            "max_variant_changes": 4,
            "requires_view_image": True,
        },
        "render_prompt": render_prompt,
    }


def render_bible(family: str, items: list[dict[str, Any]], evolution: dict[str, Any]) -> str:
    definition = family_definition(evolution, family)
    stable_axes, variant_axes = stable_and_variant_axes(items)
    lines = [
        f"# Series Bible · {family}",
        "",
        "> This is the stable visual base for an imported X Prompt Deck family; it is not a source-specific preset.",
        "",
        "## Stable composition axes",
        "",
        "```yaml",
        json.dumps({"family": family, **stable_axes}, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Observed axis variants",
        "",
        "```yaml",
        json.dumps(variant_axes or {"none": {}}, ensure_ascii=False, indent=2),
        "```",
        "",
        "Choose an observed variant per item; do not force the first item's aspect or information structure across the family.",
        "",
        "## Base visual system",
        "",
        bullet_lines(definition.get("base_visual_system")),
        "",
        "## Topic seasoning",
        "",
        bullet_lines(definition.get("topic_seasoning")),
        "",
        "## Series variables",
        "",
        bullet_lines(definition.get("series_variables")),
        "- Per item, change at most 2–4 variables; keep title hierarchy, safe area, and reading order stable.",
        "",
        "## Evidence rule",
        "",
        "Each item retains its own source URL, status ID, source prompt evidence, and selection filters.",
    ]
    return "\n".join(lines) + "\n"


def render_item_markdown(number: int, item: dict[str, Any]) -> str:
    axes = item["composition_axes"]
    layers = item["layers"]
    lines = [
        f"# {number:03d} · {item['source_status_id']} · {axes['family']}",
        "",
        "> Compiled by the image-skill X Prompt Evolution route. This is not a bitmap acceptance record.",
        "",
        "## composition_axes",
        "",
        "```yaml",
        json.dumps(axes, ensure_ascii=False, indent=2),
        "```",
        "",
        "## base_visual_system",
        "",
        bullet_lines(layers["base_visual_system"]),
        "",
        "## topic_seasoning",
        "",
        bullet_lines(layers["topic_seasoning"]),
        "",
        "## source_visual_evidence",
        "",
        "### base_excerpt (interpret, do not copy verbatim)",
        "",
        layers["source_base_evidence"],
        "",
        "### seasoning_excerpts",
        "",
        bullet_lines(layers["source_seasoning_evidence"]),
        "",
        "## series_variables",
        "",
        bullet_lines(layers["series_variables"]),
        "",
        "## render_plan",
        "",
        "```yaml",
        json.dumps(item["render_plan"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## compiled_image_prompt",
        "",
        item["render_prompt"],
        "",
        "## source_evidence",
        "",
        f"- URL: {item['source_url']}",
        f"- Status ID: `{item['source_status_id']}`",
        f"- Selection filters: `{json.dumps(item['selection'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "## source_prompt_evidence",
        "",
        "```text",
        item["source_prompt"],
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="source image-prompts.yml")
    parser.add_argument("--output", type=Path, required=True, help="formal image-skill evolution output directory")
    parser.add_argument("--evolution-index", type=Path, default=DEFAULT_EVOLUTION)
    parser.add_argument("--allow-blocked", action="store_true", help="emit blocked items instead of failing")
    args = parser.parse_args()

    data = load_yaml(args.input)
    if not isinstance(data, dict) or data.get("source_skill") != "soia-pkm-clip-x-profile":
        print("input must be a soia-pkm-clip-x-profile image-prompts.yml", file=sys.stderr)
        return 2
    evolution = load_yaml(args.evolution_index)
    if not isinstance(evolution, dict) or evolution.get("id") != "x_profile_prompt_evolution":
        print("invalid x-profile evolution index", file=sys.stderr)
        return 2

    selection = source_selection(data)
    items = data.get("items") if isinstance(data.get("items"), list) else []
    deck_root = args.input.parent
    source_manifest, manifest_errors = validate_source_manifest(data, deck_root)
    if not selection:
        manifest_errors.append("image-prompts.yml: selection is required")
    if not items:
        manifest_errors.append("image-prompts.yml: items must contain at least one selected prompt")
    blocked: list[dict[str, Any]] = []
    if manifest_errors:
        blocked.append({"id": "source-manifest", "errors": manifest_errors})
    if blocked and not args.allow_blocked:
        print(json.dumps({"status": "BLOCKED", "blocked": blocked}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    compiled: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            blocked.append({"id": "invalid-item", "errors": ["item is not a mapping"]})
            continue
        blocks, errors = validate_item(item, deck_root)
        if errors:
            blocked.append({"id": as_text(item.get("source_status_id")) or "missing-status-id", "errors": errors})
            continue
        compiled.append(compile_item(item, blocks, selection, evolution))

    if blocked and not args.allow_blocked:
        print(json.dumps({"status": "BLOCKED", "blocked": blocked}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    args.output.mkdir(parents=True, exist_ok=True)
    prompts_dir = args.output / "prompts"
    bibles_dir = args.output / "bibles"
    prompts_dir.mkdir(exist_ok=True)
    bibles_dir.mkdir(exist_ok=True)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, item in enumerate(compiled, 1):
        family = item["composition_axes"]["family"]
        by_family[family].append(item)
        filename = f"{index:03d}-{slugify(family)}-{slugify(item['source_status_id'])}.md"
        (prompts_dir / filename).write_text(render_item_markdown(index, item), encoding="utf-8")

    for family, family_items in sorted(by_family.items()):
        (bibles_dir / f"{slugify(family)}.md").write_text(render_bible(family, family_items, evolution), encoding="utf-8")

    family_counts = Counter(item["composition_axes"]["family"] for item in compiled)
    series_index = {
        "schema_version": 1,
        "route": "x_profile_prompt_evolution",
        "source_profile": data.get("source_profile"),
        "selection": selection,
        "families": [
            {
                "family": family,
                "count": family_counts[family],
                "bible": f"bibles/{slugify(family)}.md",
                "stable_axes": stable_and_variant_axes(family_items)[0],
                "variant_axes": stable_and_variant_axes(family_items)[1],
                "axis_drift": {
                    key: sorted(values)
                    for key, values in stable_and_variant_axes(family_items)[1].items()
                },
            }
            for family, family_items in sorted(by_family.items())
        ],
    }
    write_yaml(args.output / "series-index.yml", series_index)
    write_yaml(
        args.output / "evolution.yml",
        {
            "schema_version": 1,
            "route": "x_profile_prompt_evolution",
            "source_skill": "soia-pkm-clip-x-profile",
            "image_skill": "soia-media-generate-article-image",
            "source_profile": data.get("source_profile"),
            "source_manifest": {
                "path": "manifest.yml",
                "provider": source_manifest.get("provider"),
                "coverage": source_manifest.get("coverage"),
            },
            "selection": selection,
            "coverage": {
                "input_items": len(items),
                "compiled_items": len(compiled),
                "blocked_items": len(blocked),
                "family_counts": dict(family_counts),
            },
            "layers": ["base_visual_system", "topic_seasoning", "series_variables", "render_plan"],
            "acceptance": evolution.get("acceptance"),
            "blocked": blocked,
        },
    )
    manifest = {
        "schema_version": 1,
        "route": "x_profile_prompt_evolution",
        "source_skill": "soia-pkm-clip-x-profile",
        "image_skill": "soia-media-generate-article-image",
        "source_profile": data.get("source_profile"),
        "source_manifest": {
            "path": "manifest.yml",
            "provider": source_manifest.get("provider"),
            "coverage": source_manifest.get("coverage"),
        },
        "input": args.input.name,
        "selection": selection,
        "coverage": {
            "input_items": len(items),
            "compiled_items": len(compiled),
            "blocked_items": len(blocked),
            "family_counts": dict(family_counts),
        },
        "artifacts": [
            "evolution.yml",
            "series-index.yml",
            "bibles/",
            "prompts/",
            "manifest.yml",
        ],
        "status": "PASS" if not blocked else "PASS_WITH_BLOCKED_ITEMS",
    }
    write_yaml(args.output / "manifest.yml", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
