#!/usr/bin/env python3
"""Resolve the C-class deliverable directory for article image generation."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any


SKILL_NAME = "soia-media-generate-article-image"
LEGACY_SUFFIX = Path("soia-open-media-content-skills") / "soia-media" / SKILL_NAME
CONFIG_ENV = "SOIA_MEDIA_ARTICLE_IMAGE_CONFIG_FILE"
OUTPUT_ENV = "SOIA_MEDIA_ARTICLE_IMAGE_OUTPUT_DIR"
PRODUCT_OUTPUT_ENV = "SOIA_DERIVED_OUTPUT_DIR"


def configured_root(env: Mapping[str, str], name: str) -> Path | None:
    value = usable_path(env.get(name))
    return Path(value).expanduser() if value else None


def storage_roots(
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
    temp_root: Path | None = None,
) -> dict[str, Path]:
    """Return portable config/state/cache/temp roots without creating them."""

    values = os.environ if env is None else env
    user_home = Path.home() if home is None else home
    platform_id = sys.platform if platform_name is None else platform_name
    is_windows = platform_id.startswith("win")
    is_macos = platform_id == "darwin"

    config_base = configured_root(values, "SOIA_SKILLS_CONFIG_HOME")
    if config_base is None:
        if is_windows:
            config_base = Path(values.get("APPDATA", user_home / "AppData" / "Roaming")) / "soia-skills"
        else:
            config_base = Path(values.get("XDG_CONFIG_HOME", user_home / ".config")) / "soia-skills"

    state_base = configured_root(values, "SOIA_SKILLS_STATE_HOME")
    if state_base is None:
        if is_windows:
            state_base = Path(values.get("LOCALAPPDATA", user_home / "AppData" / "Local")) / "soia-skills" / "state"
        else:
            state_base = Path(values.get("XDG_STATE_HOME", user_home / ".local" / "state")) / "soia-skills"

    cache_base = configured_root(values, "SOIA_SKILLS_CACHE_HOME")
    if cache_base is None:
        if is_windows:
            cache_base = Path(values.get("LOCALAPPDATA", user_home / "AppData" / "Local")) / "soia-skills" / "Cache"
        elif is_macos:
            cache_base = user_home / "Library" / "Caches" / "soia-skills"
        else:
            cache_base = Path(values.get("XDG_CACHE_HOME", user_home / ".cache")) / "soia-skills"

    suffix = Path(SKILL_NAME)
    temporary_base = Path(tempfile.gettempdir()) if temp_root is None else temp_root
    return {
        "config": config_base / suffix,
        "state": state_base / suffix,
        "cache": cache_base / suffix,
        "temp": temporary_base / "soia-skills" / suffix,
    }


def config_home(env: Mapping[str, str], home: Path, platform_name: str) -> Path:
    return storage_roots(env=env, home=home, platform_name=platform_name)["config"]


def config_candidates(
    env: Mapping[str, str], home: Path, platform_name: str
) -> list[Path]:
    candidates: list[Path] = []
    if env.get(CONFIG_ENV):
        candidates.append(Path(env[CONFIG_ENV]).expanduser())
    root = config_home(env, home, platform_name)
    candidates.extend(root / name for name in ("config.yml", "config.yaml"))
    legacy_root = root.parent / LEGACY_SUFFIX
    candidates.extend(legacy_root / name for name in ("config.yml", "config.yaml"))
    return candidates


def load_yaml_config(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "PyYAML is required only when a YAML config file is used; "
            "install it or pass --output-dir / set the output environment variable."
        ) from exc
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("config must be a YAML mapping")
    return value


def usable_path(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped or stripped.startswith("<") or stripped.lower() in {"null", "none", "auto"}:
        return None
    return stripped


def source_stem(source: str | None) -> str:
    if not source:
        return "article"
    stem = Path(source).stem or "article"
    cleaned = re.sub(r"[^\w\-\u4e00-\u9fff]+", "-", stem, flags=re.UNICODE).strip("-_")
    return cleaned[:96] or "article"


def resolve_output_dir(
    *,
    source: str | None = None,
    cli_output_dir: str | None = None,
    config_file: Path | None = None,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> tuple[Path, str, Path | None]:
    values = os.environ if env is None else env
    user_home = Path.home() if home is None else home
    platform_id = sys.platform if platform_name is None else platform_name

    selected_config = config_file
    if selected_config is None:
        selected_config = next(
            (path for path in config_candidates(values, user_home, platform_id) if path.is_file()),
            None,
        )
    config = load_yaml_config(selected_config)
    paths = config.get("paths", {}) if isinstance(config.get("paths", {}), dict) else {}

    candidates = (
        ("cli", usable_path(cli_output_dir)),
        ("env", usable_path(values.get(OUTPUT_ENV))),
        ("config", usable_path(paths.get("output_dir"))),
        ("product", usable_path(values.get(PRODUCT_OUTPUT_ENV))),
    )
    for origin, value in candidates:
        if value:
            return Path(value).expanduser().resolve(strict=False), origin, selected_config

    fallback = user_home / "Downloads" / SKILL_NAME / source_stem(source)
    return fallback.resolve(strict=False), "downloads-default", selected_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Article path or source identifier used for the fallback folder name.")
    parser.add_argument("--output-dir", help="Explicit deliverable directory; highest priority.")
    parser.add_argument("--config-file", type=Path, help="Optional private YAML config path.")
    parser.add_argument("--create", action="store_true", help="Create the resolved directory.")
    parser.add_argument("--json", action="store_true", help="Print a JSON receipt.")
    args = parser.parse_args()

    output, origin, config = resolve_output_dir(
        source=args.source,
        cli_output_dir=args.output_dir,
        config_file=args.config_file,
    )
    if args.create:
        output.mkdir(parents=True, exist_ok=True)

    result = {
        "output_dir": str(output),
        "origin": origin,
        "config_file": str(config) if config else None,
        "created": bool(args.create),
        "storage_roots": {
            name: str(path) for name, path in storage_roots().items()
        },
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"output_dir: {output}")
        print(f"origin: {origin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
