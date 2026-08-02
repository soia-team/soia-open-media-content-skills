from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "soia-media-generate-article-image" / "scripts" / "render_brand_logo_svg.py"


class BrandLogoRendererTest(unittest.TestCase):
    def test_logo_axis_references_live_inside_skill_reference_directory(self) -> None:
        reference_dir = ROOT / "skills" / "soia-media-generate-article-image" / "references"
        for name in (
            "prompt-aesthetic-brand-system.md",
            "prompt-text-logo-wordmark.md",
            "prompt-visual-mechanism-geometric-mark.md",
        ):
            self.assertTrue((reference_dir / name).is_file(), name)
            self.assertFalse((ROOT / "references" / name).exists(), name)

    def run_renderer(self, root: Path, spec: dict[str, object]) -> tuple[subprocess.CompletedProcess[str], Path]:
        spec_path = root / "logo.yml"
        output_path = root / "vector"
        spec_path.write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--spec", str(spec_path), "--output", str(output_path)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        return result, output_path

    def test_renders_lockups_and_variants_with_outlined_wordmark(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec = {
                "brand_name": "Example",
                "mark_viewbox": "0 0 100 100",
                "mark_path": "M10 50 A40 40 0 1 0 90 50 A40 40 0 1 0 10 50 Z",
                "wordmark": "Example",
                "wordmark_viewbox": "0 0 100 20",
                "wordmark_path": "M0 0 H100 V20 H0 Z",
                "primary_color": "#1D4ED8",
                "dark_background": "#111827",
                "lockups": ["mark-only", "horizontal-lockup"],
                "variants": ["color", "monochrome", "reversed"],
            }
            result, output = self.run_renderer(Path(temp), spec)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "manifest.yml").read_text(encoding="utf-8").split("\n", 1)[1])
            self.assertEqual(manifest["status"], "PASS")
            self.assertEqual(len(manifest["artifacts"]), 6)
            for artifact in manifest["artifacts"]:
                svg = (output / artifact["file"]).read_text(encoding="utf-8")
                self.assertIn("<svg", svg)
                self.assertIn("viewBox=", svg)
                self.assertNotIn("<image", svg)

    def test_text_wordmark_is_explicitly_marked_for_outline_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec = {
                "brand_name": "Preview",
                "mark_viewbox": "0 0 10 10",
                "mark_path": "M0 0 H10 V10 H0 Z",
                "wordmark": "Preview",
                "primary_color": "#000000",
                "lockups": ["horizontal-lockup"],
                "variants": ["color"],
            }
            result, output = self.run_renderer(Path(temp), spec)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "manifest.yml").read_text(encoding="utf-8").split("\n", 1)[1])
            self.assertEqual(manifest["status"], "NEEDS_WORDMARK_OUTLINE")
            self.assertFalse(manifest["wordmark_outlined"])


if __name__ == "__main__":
    unittest.main()
