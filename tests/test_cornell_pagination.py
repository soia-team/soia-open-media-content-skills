"""Tests for the source-grounded Cornell Notes 1–6 page planner."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "soia-media-generate-article-image" / "scripts" / "resolve_cornell_pagination.py"
SPEC = importlib.util.spec_from_file_location("cornell_pagination", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CornellPaginationTest(unittest.TestCase):
    def test_short_article_stays_single_page_with_padded_marker(self) -> None:
        plan = MODULE.plan_cornell_pages("# 标题\n\n三个知识点。", module_count=3, section_count=1)
        self.assertEqual(plan["page_count"], 1)
        self.assertEqual(plan["page_marker"], "top_left")
        self.assertEqual(plan["density_profile"], "dense_cornell_v1")
        self.assertEqual(plan["pages"][0]["page_label"], "01/01")

    def test_ten_module_card_keeps_the_approved_dense_single_page_baseline(self) -> None:
        plan = MODULE.plan_cornell_pages(
            "# 标题\n" + ("## 模块\n内容。\n" * 10),
            module_count=10,
            section_count=10,
        )
        self.assertEqual(plan["page_count"], 1)
        self.assertTrue(any("up to 10" in item for item in plan["assumptions"]))

    def test_dense_article_auto_expands_to_multiple_pages(self) -> None:
        plan = MODULE.plan_cornell_pages(
            "# 标题\n" + ("## 章节\n内容。\n" * 18),
            module_count=18,
            section_count=18,
        )
        self.assertGreaterEqual(plan["page_count"], 2)
        self.assertLessEqual(plan["page_count"], 6)
        self.assertEqual(len(plan["pages"]), plan["page_count"])
        self.assertEqual(plan["target_modules_per_page"], 10)
        self.assertEqual(plan["min_modules_per_page"], 6)
        self.assertTrue(all(page["page_marker"] == "top_left" for page in plan["pages"]))
        self.assertEqual(plan["pages"][-1]["page_role"], "summary")

    def test_extreme_density_is_hard_capped_at_six_pages(self) -> None:
        plan = MODULE.plan_cornell_pages(
            "内容。",
            module_count=100,
            section_count=100,
        )
        self.assertEqual(plan["page_count"], 6)
        self.assertEqual(plan["pages"][0]["page_label"], "01/06")
        self.assertEqual(plan["pages"][-1]["page_label"], "06/06")

    def test_explicit_page_count_is_honored_when_content_can_support_it(self) -> None:
        plan = MODULE.plan_cornell_pages(
            "内容。",
            requested_pages=4,
            module_count=32,
            section_count=24,
        )
        self.assertEqual(plan["page_count"], 4)
        self.assertIn("explicit page count honored", plan["assumptions"][0])

    def test_explicit_page_count_does_not_fill_thin_content(self) -> None:
        plan = MODULE.plan_cornell_pages("短文。", requested_pages=4, module_count=2, section_count=1)
        self.assertEqual(plan["page_count"], 1)
        self.assertTrue(any("reduced" in item for item in plan["assumptions"]))

    def test_requested_page_count_above_limit_is_capped(self) -> None:
        plan = MODULE.plan_cornell_pages("内容。", requested_pages=9, module_count=80, section_count=48)
        self.assertEqual(plan["page_count"], 6)
        self.assertTrue(any("capped" in item for item in plan["assumptions"]))


if __name__ == "__main__":
    unittest.main()
