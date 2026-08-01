"""Static contract checks for the real forward image-generation matrix."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "soia-media-generate-article-image"


class PromptForwardMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.index = yaml.safe_load(
            (SKILL / "references" / "prompt-composition-index.yml").read_text(encoding="utf-8")
        )
        self.contract = yaml.safe_load(
            (SKILL / "references" / "prompt-block-contract.yml").read_text(encoding="utf-8")
        )
        self.matrix = yaml.safe_load(
            (SKILL / "references" / "prompt-forward-test-matrix.yml").read_text(encoding="utf-8")
        )

    def test_every_composable_axis_option_has_an_executable_contract(self) -> None:
        for axis, target in (
            ("information_structure", "information_structures"),
            ("text_strategy", "text_strategies"),
            ("visual_mechanism", "visual_mechanisms"),
            ("aesthetic_system", "aesthetic_systems"),
        ):
            for option_id, option in self.index["axes"][axis]["options"].items():
                self.assertIn(option_id, self.contract[target], f"missing contract: {axis}={option_id}")
                self.assertEqual(option["reference"], self.contract[target][option_id]["reference"])
                self.assertGreaterEqual(len(self.contract[target][option_id]["compile_fields"]), 3)
                self.assertGreaterEqual(len(self.contract[target][option_id]["acceptance"]), 2)

    def test_forward_matrix_covers_all_supported_families_and_presets(self) -> None:
        support = self.index["support_catalog"]
        delivery_presets = {item["id"] for item in support["supported_delivery_presets"]}
        matrix_presets = {item["preset"] for item in self.matrix["delivery"]}
        self.assertEqual(delivery_presets, matrix_presets)
        supported_families = {item["id"] for item in support["supported_families"]}
        matrix_families = {item["family"] for item in self.matrix["families"]}
        self.assertEqual(supported_families, matrix_families)
        self.assertEqual(self.matrix["coverage"]["prompt_families"], len(supported_families))
        self.assertEqual(self.matrix["coverage"]["generated_assets"], 18)

    def test_forward_matrix_does_not_claim_static_success_as_visual_success(self) -> None:
        self.assertEqual(self.matrix["backend"], "builtin_imagegen")
        self.assertEqual(self.matrix["visual_acceptance"], "view_image")
        self.assertIn("known_limitations", self.matrix)
        self.assertTrue(any("facts" in item for item in self.matrix["known_limitations"]))


if __name__ == "__main__":
    unittest.main()
