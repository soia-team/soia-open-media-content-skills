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
SCRIPT = ROOT / "skills" / "soia-media-generate-article-image" / "scripts" / "import_x_profile_prompt_deck.py"
EVOLUTION = ROOT / "skills" / "soia-media-generate-article-image" / "references" / "x-profile-prompt-evolution.yml"


BLOCKS = (
    "source_grounding",
    "primary_task",
    "composition_and_layout",
    "visual_style_and_materials",
    "exact_text",
    "aspect_and_output",
    "constraints_and_avoid",
)


class XProfileEvolutionTest(unittest.TestCase):
    def write_deck(self, root: Path, *, missing_block: str | None = None) -> Path:
        prompt_path = root / "prompts" / "001-poster-type-stage-123.md"
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        sections = ["# 001 · 123 · poster_type_stage", "", "## composition_axes", "", "```yaml", "{}", "```", ""]
        for block in BLOCKS:
            if block == missing_block:
                continue
            sections.extend([f"## {block}", "", f"{block} fixture", ""])
        prompt_path.write_text("\n".join(sections), encoding="utf-8")
        deck = {
            "schema_version": 2,
            "source_skill": "soia-pkm-clip-x-profile",
            "image_skill": "soia-media-generate-article-image",
            "source_profile": "https://x.com/example",
            "selection": {
                "requested_latest": 1,
                "fetched": 1,
                "period_selected": 1,
                "selected": 1,
                "filters": {"month": "2026-07", "only_gpt2": True},
            },
            "items": [
                {
                    "source_status_id": "123",
                    "source_url": "https://x.com/example/status/123",
                    "visible_title": "大字 x 留白 x 色块",
                    "family": "poster_type_stage",
                    "is_gpt2": True,
                    "prompt_file": "prompts/001-poster-type-stage-123.md",
                    "source_prompt": "围绕主题对象生成编辑海报",
                    "composition_axes": {
                        "preset": "auto",
                        "family": "poster_type_stage",
                        "use_case": "foreground_story",
                        "information_structure": "single_hook",
                        "asset_role": "none",
                        "visual_mechanism": "oversized_type",
                        "aesthetic_system": "bright_modern",
                        "text_strategy": "cjk_exact_text",
                        "model_adapter": "external_gpt_image_label",
                        "batch_strategy": "single",
                        "output_mode": "poster",
                        "render_mode": "hybrid_exact_text",
                        "aspect": "4:5",
                    },
                }
            ],
        }
        input_path = root / "image-prompts.yml"
        input_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
        (root / "manifest.yml").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "skill": "soia-pkm-clip-x-profile",
                    "source": "https://x.com/example",
                    "request": {"filters": {"month": "2026-07", "only_gpt2": True}},
                    "coverage": {"selected": 1},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return input_path

    def run_import(self, input_path: Path, output_path: Path) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(input_path), "--output", str(output_path)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_import_splits_base_seasoning_and_series_layers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_path = self.write_deck(root)
            output_path = root / "evolution"
            result = self.run_import(input_path, output_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = yaml.safe_load((output_path / "manifest.yml").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "PASS")
            self.assertEqual(manifest["coverage"]["compiled_items"], 1)
            evolution = yaml.safe_load((output_path / "evolution.yml").read_text(encoding="utf-8"))
            self.assertEqual(evolution["layers"], ["base_visual_system", "topic_seasoning", "series_variables", "render_plan"])
            prompt = (output_path / "prompts" / "001-poster-type-stage-123.md").read_text(encoding="utf-8")
            self.assertIn("## base_visual_system", prompt)
            self.assertIn("## topic_seasoning", prompt)
            self.assertIn("## series_variables", prompt)
            self.assertIn("## compiled_image_prompt", prompt)
            self.assertTrue((output_path / "bibles" / "poster-type-stage.md").is_file())

    def test_import_blocks_missing_canonical_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_path = self.write_deck(root, missing_block="exact_text")
            result = self.run_import(input_path, root / "evolution")
            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED", result.stderr)

    def test_import_blocks_manifest_window_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            input_path = self.write_deck(root)
            manifest = yaml.safe_load((root / "manifest.yml").read_text(encoding="utf-8"))
            manifest["coverage"]["selected"] = 99
            (root / "manifest.yml").write_text(json.dumps(manifest), encoding="utf-8")
            result = self.run_import(input_path, root / "evolution")
            self.assertEqual(result.returncode, 2)
            self.assertIn("coverage.selected", result.stderr)

    def test_evolution_index_registers_one_source_route(self) -> None:
        index = yaml.safe_load(EVOLUTION.read_text(encoding="utf-8"))
        self.assertEqual(index["id"], "x_profile_prompt_evolution")
        self.assertEqual(index["compiler"]["variant_budget"], "每个系列单项最多改变 2–4 个变量；固定底座不可被主题佐料覆盖。")
        self.assertIn("base_visual_system", index["output_contract"]["prompt_layers"])
        self.assertIn("poster_type_stage", index["observed_families"])


if __name__ == "__main__":
    unittest.main()
