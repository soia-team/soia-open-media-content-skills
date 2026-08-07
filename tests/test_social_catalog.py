"""Tests for source-grounded social skill-catalog cards."""

from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "soia-media-generate-article-image"


def load_script(name: str, relative: str):
    path = SKILL / "scripts" / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FACTS = load_script("social_catalog_facts", "build_social_catalog_facts.py")
VALIDATOR = load_script("social_catalog_validator", "validate_social_catalog_delivery.py")
CONTRACT = yaml.safe_load(
    (SKILL / "references" / "social-card-contract.yml").read_text(encoding="utf-8")
)


class SocialCatalogTest(unittest.TestCase):
    def make_repo(self, root: Path, count: int = 2, name: str = "repo") -> Path:
        repo = root / name
        for index in range(1, count + 1):
            skill = repo / "skills" / f"soia-media-test-skill-{index}"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                f"name: soia-media-test-skill-{index}\n"
                f"description: Test skill {index}.\n"
                "version: 1.0.0\n"
                "---\n\n# Test\n",
                encoding="utf-8",
            )
        plugin = repo / ".codex-plugin"
        plugin.mkdir(parents=True)
        (plugin / "plugin.json").write_text('{"version":"2.4.0"}\n', encoding="utf-8")
        return repo

    def make_facts(self, root: Path, count: int = 2, **kwargs):
        repo = self.make_repo(root, count=count)
        return FACTS.build_manifest(
            repo_root=repo,
            repository="soia-team/example-skills",
            as_of_date="2026-07-29",
            **kwargs,
        )

    def make_delivery(self, facts: dict, *, platform: str = "rednote", mode: str = "carousel") -> dict:
        skills = [item["name"] for item in facts["catalog"]["displayed_skills"]]
        if mode == "carousel":
            slides = [
                {"role": "cover", "displayed_skills": []},
                {"role": "catalog", "displayed_skills": skills},
                {"role": "highlight", "displayed_skills": []},
                {"role": "cta", "displayed_skills": []},
            ]
        else:
            slides = [
                {"roles": ["cover", "catalog", "cta"], "displayed_skills": skills},
            ]
        expected_text = {
            "claim": facts["catalog"]["claim_text"],
            "skill_labels": [
                item["display_label"] for item in facts["catalog"]["displayed_skills"]
            ],
            "install_command": facts["cta"]["install_command"],
            "repository_url": facts["cta"]["repository_url"],
        }
        return {
            "schema_version": 1,
            "source": {
                "repository": facts["source"]["repository"],
                "package_version": facts["source"]["package_version"],
                "content_fingerprint": facts["content_fingerprint"],
            },
            "presentation": {
                "platform": platform,
                "layout_mode": mode,
                # 契约按平台取比例：rednote 3:4，wechat-moments 4:5
                "aspect": CONTRACT["platforms"][platform]["layout_modes"][mode]["aspect"],
                "slides": slides,
            },
            "cta": {
                "install_command": facts["cta"]["install_command"],
                "repository_url": facts["cta"]["repository_url"],
                "qr_target": facts["cta"]["repository_url"],
            },
            "observed": {"exact_text": expected_text},
            "quality": {
                "renderer": "deterministic-compositor",
                "deterministic_text": True,
                "ocr_exact_match": True,
                "approved_brand_assets": True,
                "mobile_preview": True,
                "view_image": True,
                "hero_art_reviewed": True,
                "semantic_density_review": True,
                "source_claim_traceability": True,
                "hallucinated_evidence_scan": True,
                "qr_decoded_target": facts["cta"]["repository_url"],
            },
        }

    def test_total_facts_are_compiled_from_skill_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=3)
        self.assertEqual(facts["catalog"]["total_skill_count"], 3)
        self.assertEqual(facts["catalog"]["displayed_skill_count"], 3)
        self.assertEqual(facts["catalog"]["claim_text"], "当前已提供 3 个技能")
        self.assertEqual(
            facts["cta"]["install_command"],
            "npx skills add soia-team/example-skills -g -a '*' -y",
        )
        self.assertEqual(len(facts["content_fingerprint"]), 64)

    def test_forward_fixture_uses_the_real_media_catalog(self) -> None:
        facts = FACTS.build_manifest(
            repo_root=ROOT,
            repository="soia-team/soia-open-media-content-skills",
            as_of_date="2026-07-29",
        )
        self.assertEqual(facts["catalog"]["total_skill_count"], 6)
        self.assertIn(
            "soia-media-generate-article-image",
            [item["name"] for item in facts["catalog"]["displayed_skills"]],
        )
        delivery = self.make_delivery(facts)
        self.assertEqual(VALIDATOR.validate_delivery(facts, delivery, CONTRACT), [])

    def test_featured_claim_and_cta_use_published_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(
                Path(temp),
                claim_mode="featured",
                featured_skills=["soia-media-test-skill-2"],
                cta_mode="featured",
            )
        self.assertEqual(facts["catalog"]["claim_text"], "精选 1 个技能")
        self.assertIn("-s soia-media-test-skill-2", facts["cta"]["install_command"])

    def test_validated_label_map_supports_short_social_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(
                Path(temp),
                label_map={"soia-media-test-skill-1": "文章草稿"},
            )
        labels = [item["display_label"] for item in facts["catalog"]["displayed_skills"]]
        self.assertEqual(labels[0], "文章草稿")

    def test_label_map_rejects_unpublished_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "unpublished skills"):
                self.make_facts(
                    Path(temp),
                    label_map={"soia-media-missing-skill": "不存在"},
                )

    def test_label_map_rejects_duplicate_display_labels(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "must be unique"):
                self.make_facts(
                    Path(temp),
                    label_map={
                        "soia-media-test-skill-1": "文章工具",
                        "soia-media-test-skill-2": "文章工具",
                    },
                )

    def test_batch_scope_compiles_included_and_excluded_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            included = self.make_repo(root, count=2, name="included")
            self.make_repo(root, count=1, name="excluded")
            spec_path = root / "batch.yml"
            output_path = root / "batch-facts.yml"
            spec_path.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": 1,
                        "series_id": "open-skills-launch",
                        "platform": "rednote",
                        "slide_count": 3,
                        "as_of_date": "2026-07-29",
                        "include": [
                            {
                                "repo": str(included),
                                "repository": "soia-team/included-skills",
                            }
                        ],
                        "exclude": ["soia-team/excluded-skills"],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL / "scripts" / "build_social_catalog_batch.py"),
                    "--spec",
                    str(spec_path),
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            batch = yaml.safe_load(output_path.read_text(encoding="utf-8"))
        self.assertEqual(batch["included_repositories"], ["soia-team/included-skills"])
        self.assertEqual(batch["excluded_repositories"], ["soia-team/excluded-skills"])
        self.assertEqual(batch["repository_count"], 1)
        self.assertEqual(batch["total_skill_count"], 2)
        self.assertEqual(len(batch["batch_fingerprint"]), 64)

    def test_batch_scope_rejects_repository_in_both_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            included = self.make_repo(root, count=1)
            spec_path = root / "batch.yml"
            spec_path.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": 1,
                        "series_id": "invalid-series",
                        "include": [
                            {
                                "repo": str(included),
                                "repository": "soia-team/same-skills",
                            }
                        ],
                        "exclude": ["soia-team/same-skills"],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL / "scripts" / "build_social_catalog_batch.py"),
                    "--spec",
                    str(spec_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("both included and excluded", result.stderr)

    def test_unknown_featured_skill_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "not published"):
                self.make_facts(
                    Path(temp),
                    claim_mode="featured",
                    featured_skills=["soia-media-missing-skill"],
                )

    def test_delivery_matching_facts_and_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=6)
        delivery = self.make_delivery(facts)
        self.assertEqual(VALIDATOR.validate_delivery(facts, delivery, CONTRACT), [])

    def test_two_slide_deck_can_combine_semantic_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=6)
        delivery = self.make_delivery(facts)
        skills = [item["name"] for item in facts["catalog"]["displayed_skills"]]
        delivery["presentation"]["slides"] = [
            {"roles": ["cover", "catalog"], "displayed_skills": skills[:3]},
            {"roles": ["catalog", "highlight", "cta"], "displayed_skills": skills[3:]},
        ]
        self.assertEqual(VALIDATOR.validate_delivery(facts, delivery, CONTRACT), [])

    def test_three_slide_deck_passes_without_forcing_four_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=6)
        delivery = self.make_delivery(facts)
        skills = [item["name"] for item in facts["catalog"]["displayed_skills"]]
        delivery["presentation"]["slides"] = [
            {"role": "cover", "displayed_skills": []},
            {"role": "catalog", "displayed_skills": skills},
            {"roles": ["highlight", "cta"], "displayed_skills": []},
        ]
        self.assertEqual(VALIDATOR.validate_delivery(facts, delivery, CONTRACT), [])

    def test_single_card_combines_all_required_roles_on_one_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=4)
        delivery = self.make_delivery(facts, platform="wechat-moments", mode="single")
        self.assertEqual(len(delivery["presentation"]["slides"]), 1)
        self.assertEqual(VALIDATOR.validate_delivery(facts, delivery, CONTRACT), [])

    def test_single_mode_rejects_a_second_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=4)
        delivery = self.make_delivery(facts, platform="wechat-moments", mode="single")
        delivery["presentation"]["slides"].append(
            {"role": "highlight", "displayed_skills": []}
        )
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertTrue(any("1..1 slides" in item for item in errors))

    def test_stale_claim_and_cta_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp))
        delivery = self.make_delivery(facts)
        delivery["observed"]["exact_text"]["claim"] = "当前已提供 1 个技能"
        delivery["cta"]["install_command"] = "npx skills add wrong/repo -y"
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertTrue(any("exact_text" in item for item in errors))
        self.assertTrue(any("CTA install command" in item for item in errors))

    def test_density_and_qr_decode_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=7)
        delivery = self.make_delivery(facts)
        delivery["quality"]["qr_decoded_target"] = "https://example.invalid"
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertTrue(any("maximum is 6" in item for item in errors))
        self.assertTrue(any("QR decoder" in item for item in errors))

    def test_missing_visual_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp))
        delivery = self.make_delivery(facts)
        delivery["quality"]["view_image"] = False
        delivery["quality"]["renderer"] = "imagegen-only"
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertIn("quality.view_image must be true", errors)
        self.assertIn("quality.renderer must be deterministic-compositor", errors)

    def test_missing_semantic_density_review_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp))
        delivery = self.make_delivery(facts)
        delivery["quality"]["semantic_density_review"] = False
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertIn("quality.semantic_density_review must be true", errors)

    def test_repository_feature_pair_requires_two_sourced_role_complete_slides(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp), count=2)
        delivery = self.make_delivery(facts)
        skills = [item["name"] for item in facts["catalog"]["displayed_skills"]]
        pair = CONTRACT["narrative_modes"]["repository_feature_pair"]
        delivery["presentation"]["narrative_mode"] = "repository_feature_pair"
        delivery["presentation"]["slides"] = [
            {
                "roles": ["repository_recommendation", "cover", "catalog"],
                "sections": list(pair["slides"][0]["required_sections"]),
                "displayed_skills": skills,
            },
            {
                "roles": ["featured_skill_deep_dive", "highlight", "cta"],
                "sections": list(pair["slides"][1]["required_sections"]),
                "displayed_skills": [],
            },
        ]
        delivery["source"]["evidence"] = {
            name: True for name in pair["required_sources"]
        }
        self.assertEqual(VALIDATOR.validate_delivery(facts, delivery, CONTRACT), [])

        delivery["presentation"]["slides"][1]["sections"].remove("validation")
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertTrue(any("missing required sections: validation" in item for item in errors))

    def test_duplicate_skill_on_two_slides_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            facts = self.make_facts(Path(temp))
        delivery = self.make_delivery(facts)
        duplicate = copy.deepcopy(delivery["presentation"]["slides"][1])
        delivery["presentation"]["slides"].insert(2, duplicate)
        errors = VALIDATOR.validate_delivery(facts, delivery, CONTRACT)
        self.assertTrue(any("more than one catalog slide" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
