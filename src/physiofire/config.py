"""Load the project configuration (config/config.yaml)."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config" / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    """Return the configuration as a dict, with entries in `paths` resolved to absolute Paths."""
    path = Path(path) if path is not None else DEFAULT_CONFIG
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["paths"] = {k: (REPO_ROOT / v).resolve() for k, v in cfg.get("paths", {}).items()}
    return cfg
