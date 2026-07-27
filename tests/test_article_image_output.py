"""Output-path precedence tests for soia-media-generate-article-image."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "soia-media-generate-article-image" / "scripts" / "resolve_output_dir.py"
SPEC = importlib.util.spec_from_file_location("article_image_output", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ArticleImageOutputTest(unittest.TestCase):
    def test_storage_roots_follow_data_storage_spec_on_macos(self) -> None:
        home = Path("/Users/example")
        roots = MODULE.storage_roots(env={}, home=home, platform_name="darwin", temp_root=Path("/tmp"))
        suffix = Path(MODULE.REPO_NAME) / MODULE.SKILL_TYPE / MODULE.SKILL_NAME
        self.assertEqual(roots["config"], home / ".config" / "soia-skills" / suffix)
        self.assertEqual(roots["state"], home / ".local" / "state" / "soia-skills" / suffix)
        self.assertEqual(roots["cache"], home / "Library" / "Caches" / "soia-skills" / suffix)
        self.assertEqual(roots["temp"], Path("/tmp") / "soia-skills" / suffix)

    def test_storage_root_overrides_are_respected(self) -> None:
        roots = MODULE.storage_roots(
            env={
                "SOIA_SKILLS_CONFIG_HOME": "/cfg",
                "SOIA_SKILLS_STATE_HOME": "/state",
                "SOIA_SKILLS_CACHE_HOME": "/cache",
            },
            home=Path("/home/example"),
            platform_name="linux",
            temp_root=Path("/temp"),
        )
        suffix = Path(MODULE.REPO_NAME) / MODULE.SKILL_TYPE / MODULE.SKILL_NAME
        self.assertEqual(roots["config"], Path("/cfg") / suffix)
        self.assertEqual(roots["state"], Path("/state") / suffix)
        self.assertEqual(roots["cache"], Path("/cache") / suffix)
        self.assertEqual(roots["temp"], Path("/temp") / "soia-skills" / suffix)

    def test_cli_wins_over_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output, origin, _ = MODULE.resolve_output_dir(
                source="article.md",
                cli_output_dir=str(root / "cli"),
                env={MODULE.OUTPUT_ENV: str(root / "env")},
                home=root,
                platform_name="linux",
            )
            self.assertEqual(output, (root / "cli").resolve())
            self.assertEqual(origin, "cli")

    def test_config_wins_over_product_convention(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "config.yml"
            config.write_text(f"paths:\n  output_dir: {root / 'configured'}\n", encoding="utf-8")
            output, origin, selected = MODULE.resolve_output_dir(
                source="article.md",
                config_file=config,
                env={MODULE.PRODUCT_OUTPUT_ENV: str(root / "product")},
                home=root,
                platform_name="linux",
            )
            self.assertEqual(output, (root / "configured").resolve())
            self.assertEqual(origin, "config")
            self.assertEqual(selected, config)

    def test_portable_downloads_fallback_uses_source_stem(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output, origin, _ = MODULE.resolve_output_dir(
                source="一篇文章.md",
                env={},
                home=root,
                platform_name="darwin",
            )
            self.assertEqual(
                output,
                (root / "Downloads" / MODULE.SKILL_NAME / "一篇文章").resolve(),
            )
            self.assertEqual(origin, "downloads-default")


if __name__ == "__main__":
    unittest.main()
