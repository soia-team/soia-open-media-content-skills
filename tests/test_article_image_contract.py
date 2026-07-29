"""Contract tests for article-image prompt assembly and provenance boundaries."""

from __future__ import annotations

import json
import struct
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "soia-media-generate-article-image"


class ArticleImageContractTest(unittest.TestCase):
    @staticmethod
    def png_size(path: Path) -> tuple[int, int]:
        with path.open("rb") as handle:
            signature = handle.read(24)
        if signature[:8] != b"\x89PNG\r\n\x1a\n":
            raise AssertionError(f"not a PNG: {path}")
        return struct.unpack(">II", signature[16:24])

    def test_registry_declares_atomic_prompt_blocks(self) -> None:
        registry = yaml.safe_load((SKILL / "references" / "template-registry.yml").read_text(encoding="utf-8"))
        self.assertEqual(registry["schema_version"], 4)
        self.assertEqual(
            registry["prompt_blocks"]["required"],
            [
                "source_grounding",
                "primary_task",
                "composition_and_layout",
                "visual_style_and_materials",
                "exact_text",
                "aspect_and_output",
                "constraints_and_avoid",
            ],
        )

    def test_social_catalog_defaults_to_complete_direct_poster_with_exact_text_fallback(self) -> None:
        registry = yaml.safe_load((SKILL / "references" / "template-registry.yml").read_text(encoding="utf-8"))
        templates = {item["id"]: item for item in registry["templates"]}
        social = templates["social_skill_catalog"]
        self.assertEqual(social["image_type"], ["social_card", "carousel"])
        self.assertEqual(
            social["render_modes"],
            ["direct_poster", "hybrid_exact_text"],
        )
        self.assertEqual(social["default_render_mode"], "direct_poster")
        self.assertEqual(social["default_aspect"], "4:5")
        self.assertIn("skill_labels", social["deterministic_fields"])
        self.assertIn("install_command", social["deterministic_fields"])
        self.assertIn("qr_code", social["deterministic_fields"])

    def test_social_catalog_prompt_requires_a_complete_poster_prompt(self) -> None:
        content = (SKILL / "references" / "prompt-social-skill-catalog.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("每一张图都要写清楚来源、画面任务、固定空间关系", content)
        self.assertIn("direct_poster`（默认）", content)
        self.assertIn("不要只画一个孤立的 3D 主视觉", content)

    def test_input_contract_lists_registered_specialized_types(self) -> None:
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("social_card | carousel | icon", content)
        self.assertIn("social_skill_catalog | plugin_icon", content)
        self.assertIn("build_social_catalog_facts.py", content)
        self.assertIn("validate_social_catalog_delivery.py", content)

    def test_social_contract_has_mobile_platform_limits(self) -> None:
        contract = yaml.safe_load(
            (SKILL / "references" / "social-card-contract.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            contract["platforms"]["rednote"]["layout_modes"]["carousel"]["max_catalog_items_per_slide"],
            6,
        )
        self.assertEqual(
            contract["platforms"]["rednote"]["layout_modes"]["carousel"]["preferred_slide_counts"],
            [2, 3],
        )
        self.assertEqual(
            contract["platforms"]["wechat-moments"]["layout_modes"]["single"]["max_catalog_items_per_slide"],
            4,
        )
        self.assertIn("ocr_exact_match", contract["required_quality_evidence"])

    def test_cornell_template_has_no_external_source_reference(self) -> None:
        content = (SKILL / "references" / "prompt-cornell-notes-infographic.md").read_text(encoding="utf-8")
        self.assertNotIn("knowledgefxg", content)
        self.assertNotIn("来源结构参考", content)

    def test_codex_plugin_declares_valid_icon_assets(self) -> None:
        manifest_path = ROOT / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        interface = manifest["interface"]
        # 官方 validate_asset_path 以 plugin root 为基准解析，不是 manifest 所在目录；
        # 原先按 manifest_path.parent 解析，官方 validator 判「points to a missing file」。
        logo = (ROOT / interface["logo"]).resolve()
        composer = (ROOT / interface["composerIcon"]).resolve()
        self.assertEqual(self.png_size(logo), (512, 512))
        self.assertEqual(self.png_size(composer), (32, 32))


if __name__ == "__main__":
    unittest.main()
