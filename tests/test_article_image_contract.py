"""Contract tests for article-image prompt assembly and provenance boundaries."""

from __future__ import annotations

import json
import runpy
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
        self.assertEqual(registry["schema_version"], 7)
        self.assertIn("narrative_mode", registry["selection_order"])
        for axis in ("family", "information_structure", "asset_role", "visual_mechanism", "aesthetic_system", "text_strategy", "model_adapter"):
            self.assertIn(axis, registry["selection_order"])
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

    def test_editorial_research_minimal_is_registered_for_covers_and_summaries(self) -> None:
        registry = yaml.safe_load((SKILL / "references" / "template-registry.yml").read_text(encoding="utf-8"))
        templates = {item["id"]: item for item in registry["templates"]}
        template = templates["editorial_research_minimal"]
        self.assertEqual(template["image_type"], ["cover", "summary_card"])
        self.assertEqual(template["reference"], "prompt-editorial-research-minimal.md")
        prompt = (SKILL / "references" / template["reference"]).read_text(encoding="utf-8")
        for block in (
            "source_grounding",
            "primary_task",
            "composition_and_layout",
            "visual_style_and_materials",
            "exact_text",
            "aspect_and_output",
            "constraints_and_avoid",
        ):
            self.assertIn(block, prompt)
        self.assertIn("基础视觉系统", prompt)
        self.assertIn("主题佐料", prompt)

    def test_composition_index_is_axis_based_not_a_new_preset(self) -> None:
        registry = yaml.safe_load((SKILL / "references" / "template-registry.yml").read_text(encoding="utf-8"))
        templates = {item["id"]: item for item in registry["templates"]}
        self.assertNotIn("editorial_typographic_mask_batch", templates)
        self.assertEqual(registry["composition_index"], "prompt-composition-index.yml")
        index = yaml.safe_load((SKILL / "references" / registry["composition_index"]).read_text(encoding="utf-8"))
        self.assertEqual(index["schema_version"], 2)
        self.assertIn("family", index["axes"])
        self.assertIn("information_structure", index["axes"])
        self.assertIn("asset_role", index["axes"])
        self.assertIn("text_strategy", index["axes"])
        self.assertIn("model_adapter", index["axes"])
        self.assertIn("use_case", index["axes"])
        self.assertIn("visual_mechanism", index["axes"])
        self.assertIn("aesthetic_system", index["axes"])
        self.assertEqual(
            index["examples"][0]["normalized"]["visual_mechanism"],
            "typographic_mask",
        )
        self.assertIn("GPT2", index["examples"][0]["query"])
        self.assertEqual(index["family_catalog"], "prompt-family-catalog.md")
        support = index["support_catalog"]
        self.assertEqual(support["counts"]["delivery_presets"], 6)
        registry_presets = {
            item["id"]
            for item in registry["templates"]
        }
        catalog_presets = {
            item["id"]
            for item in support["supported_delivery_presets"]
        }
        self.assertEqual(len(catalog_presets), support["counts"]["delivery_presets"])
        self.assertEqual(catalog_presets, registry_presets)
        self.assertEqual(support["delivery_presets_source"], "template-registry.yml#templates")
        self.assertEqual(support["counts"]["prompt_families"], 10)
        self.assertEqual(len(support["supported_families"]), support["counts"]["prompt_families"])
        self.assertEqual(support["counts"]["information_structures"], len(index["axes"]["information_structure"]["options"]))
        self.assertEqual(support["counts"]["visual_mechanisms"], len(index["axes"]["visual_mechanism"]["options"]))
        self.assertEqual(support["counts"]["aesthetic_systems"], len(index["axes"]["aesthetic_system"]["options"]))
        self.assertEqual(support["counts"]["text_strategies"], len(index["axes"]["text_strategy"]["options"]))
        self.assertEqual(support["counts"]["asset_roles"], len(index["axes"]["asset_role"]["options"]))
        self.assertIn("ambiguous_when", support["selection_policy"])
        self.assertIn("first_response", support["selection_policy"])
        family_catalog = (SKILL / "references" / index["family_catalog"]).read_text(encoding="utf-8")
        for family_id in (
            "morning_city",
            "presentation_grid",
            "portrait_identity",
            "celebration_ceremony",
            "archival_print",
        ):
            self.assertIn(family_id, family_catalog)
        mechanism = (SKILL / "references" / "prompt-visual-mechanism-typographic-mask.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("不是独立 preset", mechanism)

    def test_prompt_composition_resolver_maps_multiple_observed_families(self) -> None:
        resolver = runpy.run_path(
            str(SKILL / "scripts" / "resolve_prompt_composition.py")
        )
        index = yaml.safe_load((SKILL / "references" / "prompt-composition-index.yml").read_text(encoding="utf-8"))
        morning = resolver["resolve_query"]("GPT2 x 早安 x 字体蒙版 x 美学提示词", index)
        self.assertEqual(morning["normalized"]["family"], "morning_city")
        self.assertEqual(morning["normalized"]["visual_mechanism"], "typographic_mask")
        self.assertEqual(morning["normalized"]["information_structure"], "knowledge_card")
        wedding = resolver["resolve_query"]("GPT2 x 婚礼 x 请柬 x 婚纱 x 美学提示词", index)
        self.assertEqual(wedding["normalized"]["family"], "celebration_ceremony")
        self.assertEqual(wedding["normalized"]["use_case"], "wedding")
        self.assertEqual(wedding["normalized"]["batch_strategy"], "campaign_pack")
        self.assertIn(
            {"axis": "visual_mechanism", "value": "mirror_reflection"},
            wedding["defaulted"],
        )
        self.assertIn("prompt-structure-campaign-pack.md", wedding["references"])
        self.assertIn("prompt-visual-mechanism-mirror-reflection.md", wedding["references"])
        self.assertIn("prompt-aesthetic-ceremonial-soft-system.md", wedding["references"])
        self.assertNotIn("aesthetic_system", {item["axis"] for item in wedding["matched"]})
        self.assertNotIn("use_case", {item["axis"] for item in wedding["defaulted"]})
        self.assertNotIn("model_adapter", {item["axis"] for item in wedding["defaulted"]})
        archival = resolver["resolve_query"]("GPT2 x 票据 x 拓印 x 古籍气质", index)
        self.assertEqual(archival["normalized"]["family"], "archival_print")
        self.assertEqual(archival["normalized"]["visual_mechanism"], "archival_collage")

    def test_social_catalog_prompt_requires_a_complete_poster_prompt(self) -> None:
        content = (SKILL / "references" / "prompt-social-skill-catalog.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("每一张图都要写清楚来源、画面任务、固定空间关系", content)
        self.assertIn("direct_poster`（默认）", content)
        self.assertIn("不要只画一个孤立的 3D 主视觉", content)
        self.assertIn("repository_feature_pair", content)
        self.assertIn("信息密度指“每一块都帮助读者做判断”", content)
        self.assertIn("content-facts.yml", content)
        self.assertIn("结构示意", content)

    def test_repository_feature_pair_prompt_deck_is_explicit_and_complete(self) -> None:
        content = (SKILL / "references" / "prompt-social-skill-catalog.md").read_text(
            encoding="utf-8"
        )
        for filename in (
            "00-series-bible.md",
            "01-repository-recommendation.md",
            "02-featured-skill-deep-dive.md",
        ):
            self.assertIn(filename, content)
        self.assertIn("基础视觉系统", content)
        self.assertIn("主题佐料", content)
        for reference in (
            "prompt-social-series-bible.md",
            "prompt-social-repository-recommendation.md",
            "prompt-social-featured-skill-deep-dive.md",
        ):
            self.assertTrue((SKILL / "references" / reference).is_file(), reference)

    def test_repository_feature_pair_contract_requires_semantic_density_and_sources(self) -> None:
        contract = yaml.safe_load(
            (SKILL / "references" / "social-card-contract.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["schema_version"], 2)
        pair = contract["narrative_modes"]["repository_feature_pair"]
        self.assertEqual(pair["default_slide_count"], 2)
        self.assertEqual(
            [slide["role"] for slide in pair["slides"]],
            ["repository_recommendation", "featured_skill_deep_dive"],
        )
        self.assertIn("featured_skill_md", pair["required_sources"])
        self.assertIn("content_facts_yml", pair["required_sources"])
        self.assertTrue(pair["forbid_abstract_extra_slide_without_real_evidence"])
        self.assertIn("semantic_density_review", contract["required_quality_evidence"])
        self.assertIn("hallucinated_evidence_scan", contract["required_quality_evidence"])
        self.assertEqual(
            pair["prompt_deck"]["required_files"],
            [
                "00-series-bible.md",
                "01-repository-recommendation.md",
                "02-featured-skill-deep-dive.md",
            ],
        )
        self.assertTrue(pair["prompt_deck"]["each_slide_must_be_complete"])

    def test_skill_forbids_ad_hoc_delivery_roots(self) -> None:
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("resolve_output_dir.py --source <source> --json", content)
        self.assertIn("<topic>-delivery-<date>", content)
        self.assertIn("output_dir_origin", content)

    def test_input_contract_lists_registered_specialized_types(self) -> None:
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("social_card | carousel | icon", content)
        self.assertIn("social_skill_catalog | plugin_icon", content)
        self.assertIn("editorial_research_minimal", content)
        self.assertIn("visual_mechanism", content)
        self.assertIn("aesthetic_system", content)
        self.assertIn("information_structure", content)
        self.assertIn("text_strategy", content)
        self.assertIn("prompt-family-catalog.md", content)
        self.assertIn("model_adapter", content)
        self.assertIn("渐进式选择与加载", content)
        self.assertIn("--list-supported", content)
        self.assertIn("L0：支持目录", content)
        self.assertIn("6 个交付模板和 10 个 Prompt 家族", content)
        self.assertIn("L3：生成与验收", content)
        self.assertIn("prompt-composition-index.yml", content)
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
        self.assertTrue(logo.is_file(), logo)
        self.assertTrue(composer.is_file(), composer)
        # 本仓原先自成一套（logo 512、composerIcon 32px PNG），是全生态唯一的例外。
        # 图标已收敛到元仓 scripts/generate_icons.py 的单一配色表统一派生：
        # composerIcon 用矢量母版（官方要求 SVG，PNG 是当时的将就），logo 用 1024 位图。
        self.assertEqual(composer.suffix, ".svg")
        self.assertEqual(self.png_size(logo), (1024, 1024))


if __name__ == "__main__":
    unittest.main()
