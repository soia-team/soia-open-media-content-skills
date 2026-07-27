"""Storage namespace tests for newly scaffolded skills."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates" / "skill-template" / "scripts" / "resolve_storage.py"
SPEC = importlib.util.spec_from_file_location("template_storage", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StorageTemplateTest(unittest.TestCase):
    def test_skill_name_is_the_only_storage_namespace(self) -> None:
        home = Path("/Users/example")
        roots = MODULE.storage_paths(
            "soia-media",
            "soia-media-example",
            env={},
            home=home,
            platform_name="darwin",
            temp_root=Path("/tmp"),
        )
        self.assertEqual(
            roots["config"],
            home / ".config" / "soia-skills" / "soia-media-example",
        )
        self.assertEqual(
            roots["state"],
            home / ".local" / "state" / "soia-skills" / "soia-media-example",
        )
        self.assertEqual(
            roots["cache"],
            home / "Library" / "Caches" / "soia-skills" / "soia-media-example",
        )
        self.assertEqual(
            roots["temp"],
            Path("/tmp") / "soia-skills" / "soia-media-example",
        )


if __name__ == "__main__":
    unittest.main()
