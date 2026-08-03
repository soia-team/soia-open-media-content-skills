#!/usr/bin/env python3
"""Choose a source-grounded 1–6 page plan for a Cornell Notes image series."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


MAX_PAGES = 6
TARGET_MODULES_PER_PAGE = 10
MIN_MODULES_PER_DENSE_PAGE = 6
CJK_CHARS_PER_PAGE = 3_200
LATIN_WORDS_PER_PAGE = 550
SECTIONS_PER_PAGE = 8


def _ceil_div(value: int, divisor: int) -> int:
    return max(1, math.ceil(value / divisor))


def infer_metrics(text: str) -> dict[str, int]:
    """Infer conservative density signals from Markdown without inventing content."""

    headings = len(re.findall(r"(?m)^\s{0,3}#{1,6}\s+\S+", text))
    bullets = len(re.findall(r"(?m)^\s*(?:[-*+] |\d+[.)] )\S+", text))
    cjk_chars = len(re.findall(r"[\u3400-\u9fff]", text))
    latin_words = len(re.findall(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*", text))
    inferred_modules = max(
        1,
        headings,
        _ceil_div(bullets, 3) if bullets else 0,
        _ceil_div(cjk_chars, 600) if cjk_chars else 0,
        _ceil_div(latin_words, 120) if latin_words else 0,
    )
    return {
        "section_count": headings,
        "bullet_count": bullets,
        "cjk_chars": cjk_chars,
        "latin_words": latin_words,
        "module_count": inferred_modules,
    }


def auto_page_count(
    *,
    module_count: int,
    cjk_chars: int,
    latin_words: int,
    section_count: int,
) -> int:
    """Return the smallest content-fitting count, capped at six pages."""

    signals = [
        _ceil_div(module_count, TARGET_MODULES_PER_PAGE),
        _ceil_div(cjk_chars, CJK_CHARS_PER_PAGE) if cjk_chars else 1,
        _ceil_div(latin_words, LATIN_WORDS_PER_PAGE) if latin_words else 1,
        _ceil_div(section_count, SECTIONS_PER_PAGE) if section_count else 1,
    ]
    candidate = min(MAX_PAGES, max(1, max(signals)))

    # Preserve the approved dense Cornell card: a concise set of up to ten
    # modules stays on one page instead of becoming a sparse two-page series.
    if module_count <= TARGET_MODULES_PER_PAGE:
        return 1

    # For larger series, do not create pages that would average fewer than six
    # complete cue/note modules. This is a density guard, not filler generation.
    dense_page_cap = max(1, module_count // MIN_MODULES_PER_DENSE_PAGE)
    return min(candidate, dense_page_cap)


def plan_cornell_pages(
    text: str = "",
    *,
    requested_pages: int | None = None,
    module_count: int | None = None,
    section_count: int | None = None,
) -> dict[str, Any]:
    """Build a manifest-ready page plan with an explicit top-left marker contract."""

    metrics = infer_metrics(text)
    if module_count is not None:
        if module_count < 1:
            raise ValueError("module_count must be at least 1")
        metrics["module_count"] = module_count
    if section_count is not None:
        if section_count < 0:
            raise ValueError("section_count cannot be negative")
        metrics["section_count"] = section_count

    automatic = auto_page_count(
        module_count=metrics["module_count"],
        cjk_chars=metrics["cjk_chars"],
        latin_words=metrics["latin_words"],
        section_count=metrics["section_count"],
    )
    assumptions: list[str] = []
    if requested_pages is not None:
        if requested_pages < 1:
            raise ValueError("requested_pages must be at least 1")
        requested = min(MAX_PAGES, requested_pages)
        if requested_pages > MAX_PAGES:
            assumptions.append(f"requested_pages capped from {requested_pages} to {MAX_PAGES}")
        page_count = min(requested, automatic)
        if requested > automatic:
            assumptions.append(
                f"requested {requested} pages exceeded estimated content capacity; reduced to {automatic}"
            )
        else:
            assumptions.append(f"explicit page count honored: {page_count}")
    else:
        page_count = automatic
        assumptions.append("page count estimated from modules, source length, headings and bullets")

    if metrics["module_count"] <= TARGET_MODULES_PER_PAGE:
        assumptions.append("dense Cornell baseline retained: up to 10 source-grounded modules stay on one page")
    else:
        assumptions.append("dense Cornell baseline targets 6–10 complete modules per page; sparse pages are merged")

    pages = [
        {
            "page_number": number,
            "page_count": page_count,
            "page_label": f"{number:02d}/{page_count:02d}",
            "page_marker": "top_left",
            "page_role": "summary" if number == page_count else "content",
        }
        for number in range(1, page_count + 1)
    ]
    return {
        "preset": "cornell_notes",
        "page_count": page_count,
        "page_marker": "top_left",
        "density_profile": "dense_cornell_v1",
        "target_modules_per_page": TARGET_MODULES_PER_PAGE,
        "min_modules_per_page": MIN_MODULES_PER_DENSE_PAGE,
        "source_metrics": metrics,
        "assumptions": assumptions,
        "pages": pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", type=Path, help="Markdown/text source used for density estimation")
    parser.add_argument("--module-count", type=int, help="Optional extracted knowledge-module count")
    parser.add_argument("--section-count", type=int, help="Optional extracted section count")
    parser.add_argument("--requested-pages", type=int, help="Optional customer request; hard-capped at six")
    parser.add_argument("--json", action="store_true", help="Emit a manifest-ready JSON plan")
    args = parser.parse_args()

    text = args.text_file.read_text(encoding="utf-8") if args.text_file else ""
    if not text and args.module_count is None and args.section_count is None:
        parser.error("provide --text-file or a module/section count")
    plan = plan_cornell_pages(
        text,
        requested_pages=args.requested_pages,
        module_count=args.module_count,
        section_count=args.section_count,
    )
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(f"preset={plan['preset']} page_count={plan['page_count']} page_marker={plan['page_marker']}")
        print("labels=" + ", ".join(page["page_label"] for page in plan["pages"]))
        print("assumptions=" + "；".join(plan["assumptions"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
