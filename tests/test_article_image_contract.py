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
        self.assertEqual(registry["schema_version"], 2)
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
