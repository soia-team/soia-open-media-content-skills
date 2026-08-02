#!/usr/bin/env python3
"""Render deterministic SVG lockups and color variants from an approved logo spec.

The script is the second stage of ``brand_logo``. It does not invent a mark or
trace a raster image; the caller supplies approved mark/wordmark path data after
selecting a direction from imagegen. A text wordmark is allowed for preview but
is marked as needing outline conversion in the manifest. An optional accent path
keeps a secondary color from the approved direction deterministic across every
lockup and variant.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

import yaml


LOCKUPS = ("mark-only", "wordmark-only", "horizontal-lockup", "stacked-lockup", "app-icon")
VARIANTS = ("color", "monochrome", "reversed")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def load_spec(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("logo spec must be a YAML mapping")
    return value


def require_text(spec: dict[str, Any], key: str) -> str:
    value = str(spec.get(key, "")).strip()
    if not value:
        raise ValueError(f"missing required logo spec field: {key}")
    return value


def parse_viewbox(value: Any, key: str) -> tuple[float, float, float, float]:
    parts = str(value or "").replace(",", " ").split()
    if len(parts) != 4:
        raise ValueError(f"{key} must contain four viewBox numbers")
    numbers = tuple(float(part) for part in parts)
    if numbers[2] <= 0 or numbers[3] <= 0:
        raise ValueError(f"{key} width and height must be positive")
    return numbers  # type: ignore[return-value]


def color(value: Any, key: str, default: str) -> str:
    result = str(value or default)
    if not HEX_RE.fullmatch(result):
        raise ValueError(f"{key} must be a six-digit hex color")
    return result.upper()


def slug(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z-]+", "-", value).strip("-").lower() or "logo"


def variant_colors(spec: dict[str, Any], variant: str) -> tuple[str, str, str]:
    if variant == "monochrome":
        return "#000000", "#FFFFFF", "#000000"
    if variant == "reversed":
        return "#FFFFFF", color(spec.get("dark_background"), "dark_background", "#111827"), "#FFFFFF"
    primary = color(spec.get("primary_color"), "primary_color", "#1D4ED8")
    accent = color(spec.get("secondary_color"), "secondary_color", primary)
    return primary, "#FFFFFF", accent


def mark_element(
    path_data: str,
    viewbox: tuple[float, float, float, float],
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    accent_path: str = "",
    accent_fill: str | None = None,
    stroke_width: float | None = None,
) -> str:
    _, _, view_width, view_height = viewbox
    scale_x = width / view_width
    scale_y = height / view_height
    if stroke_width is not None and stroke_width > 0:
        primary_attrs = (
            f'fill="none" stroke="{fill}" stroke-width="{stroke_width:.3f}" '
            'stroke-linecap="round" stroke-linejoin="round"'
        )
    else:
        primary_attrs = f'fill="{fill}" fill-rule="evenodd" clip-rule="evenodd"'
    paths = [f'<path d="{html.escape(path_data, quote=True)}" {primary_attrs}/>']
    if accent_path:
        paths.append(
            f'<path d="{html.escape(accent_path, quote=True)}" fill="{accent_fill or fill}" '
            'fill-rule="evenodd" clip-rule="evenodd"/>'
        )
    return (
        f'<g transform="translate({x:.2f} {y:.2f}) scale({scale_x:.6f} {scale_y:.6f})">'
        + "".join(paths)
        + "</g>"
    )


def wordmark_element(spec: dict[str, Any], x: float, y: float, max_width: float, fill: str, font_size: float, anchor: str = "middle") -> tuple[str, bool]:
    wordmark_path = str(spec.get("wordmark_path", "")).strip()
    if wordmark_path:
        viewbox = parse_viewbox(spec.get("wordmark_viewbox"), "wordmark_viewbox")
        _, _, view_width, view_height = viewbox
        scale = min(max_width / view_width, (font_size * 1.1) / view_height)
        rendered_width = view_width * scale
        origin_x = x - rendered_width / 2 if anchor == "middle" else x
        return (
            f'<g transform="translate({origin_x:.2f} {y - font_size:.2f}) scale({scale:.6f} {scale:.6f})">'
            f'<path d="{html.escape(wordmark_path, quote=True)}" fill="{fill}" '
            'fill-rule="nonzero" clip-rule="nonzero"/></g>',
            True,
        )
    wordmark = html.escape(require_text(spec, "wordmark"))
    font = html.escape(str(spec.get("approved_font") or "Inter, Arial, sans-serif"), quote=True)
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-family="{font}" '
        f'font-size="{font_size:.2f}" font-weight="600" letter-spacing="0.02em" fill="{fill}">{wordmark}</text>',
        False,
    )


def layout(lockup: str) -> tuple[int, int, tuple[float, float, float, float], tuple[float, float, float, float] | None, float]:
    if lockup == "mark-only":
        return 1024, 1024, (192, 192, 640, 640), None, 1
    if lockup == "app-icon":
        return 1024, 1024, (230, 150, 564, 564), None, 1
    if lockup == "horizontal-lockup":
        return 1600, 640, (80, 100, 440, 440), (1100, 390, 820, 120), 0.92
    if lockup == "stacked-lockup":
        return 1024, 1024, (232, 80, 560, 560), (512, 790, 760, 110), 0.86
    if lockup == "wordmark-only":
        return 1600, 400, (0, 0, 0, 0), (800, 250, 1260, 112), 0.86
    raise ValueError(f"unsupported lockup: {lockup}")


def render_svg(spec: dict[str, Any], lockup: str, variant: str) -> tuple[str, bool, tuple[int, int]]:
    mark_path = require_text(spec, "mark_path")
    accent_path = str(spec.get("mark_accent_path", "")).strip()
    stroke_width_raw = spec.get("mark_stroke_width")
    stroke_width = float(stroke_width_raw) if stroke_width_raw not in (None, "") else None
    mark_viewbox = parse_viewbox(spec.get("mark_viewbox"), "mark_viewbox")
    foreground, reversed_background, accent = variant_colors(spec, variant)
    width, height, mark_box, word_box, word_scale = layout(lockup)
    elements: list[str] = []
    if lockup == "app-icon":
        elements.append(f'<rect width="{width}" height="{height}" rx="220" fill="{reversed_background}"/>')
    if mark_box[2] > 0:
        elements.append(
            mark_element(
                mark_path,
                mark_viewbox,
                *mark_box,
                foreground,
                accent_path,
                accent,
                stroke_width,
            )
        )
    outlined = True
    if word_box:
        x, y, max_width, font_size = word_box
        wordmark, outlined = wordmark_element(spec, x, y, max_width, foreground, font_size)
        elements.append(wordmark)
        tagline = str(spec.get("tagline", "")).strip()
        if tagline:
            elements.append(
                f'<text x="{x:.2f}" y="{y + font_size * 0.48:.2f}" text-anchor="middle" '
                f'font-size="{font_size * 0.24:.2f}" letter-spacing="0.08em" fill="{foreground}">{html.escape(tagline)}</text>'
            )
    label = html.escape(f"{require_text(spec, 'brand_name')} · {lockup} · {variant}")
    svg = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{label}">',
            f"  <title>{label}</title>",
            "  " + "\n  ".join(elements),
            "</svg>",
            "",
        ]
    )
    return svg, outlined, (width, height)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = load_spec(args.spec)
    lockups = [str(value) for value in (spec.get("lockups") or ["mark-only", "horizontal-lockup", "stacked-lockup"])]
    variants = [str(value) for value in (spec.get("variants") or list(VARIANTS))]
    unknown_lockups = sorted(set(lockups) - set(LOCKUPS))
    unknown_variants = sorted(set(variants) - set(VARIANTS))
    if unknown_lockups:
        raise SystemExit(f"unsupported lockups: {', '.join(unknown_lockups)}")
    if unknown_variants:
        raise SystemExit(f"unsupported variants: {', '.join(unknown_variants)}")
    args.output.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, Any]] = []
    all_outlined = True
    for lockup in lockups:
        for variant in variants:
            svg, outlined, dimensions = render_svg(spec, lockup, variant)
            all_outlined = all_outlined and outlined
            name = f"{slug(lockup)}-{slug(variant)}.svg"
            path = args.output / name
            path.write_text(svg, encoding="utf-8")
            artifacts.append({"file": name, "lockup": lockup, "variant": variant, "dimensions": list(dimensions), "wordmark_outlined": outlined})
    manifest = {
        "schema_version": 1,
        "route": "brand_logo",
        "brand_name": require_text(spec, "brand_name"),
        "status": "PASS" if all_outlined else "NEEDS_WORDMARK_OUTLINE",
        "wordmark_outlined": all_outlined,
        "mark_accent_present": bool(str(spec.get("mark_accent_path", "")).strip()),
        "mark_stroke_width": spec.get("mark_stroke_width"),
        "mark_viewbox": str(spec.get("mark_viewbox")),
        "secondary_color": spec.get("secondary_color"),
        "clear_space_ratio": spec.get("clear_space_ratio", 0.25),
        "min_size_px": spec.get("min_size_px", 24),
        "artifacts": artifacts,
    }
    (args.output / "manifest.yml").write_text(
        "# JSON-compatible YAML; parse with any YAML 1.2 loader.\n"
        + json.dumps(manifest, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
