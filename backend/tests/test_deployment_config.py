"""Guard service framework selection and same-origin API/SPA routing."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def configuration() -> dict:
    return json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))


def test_services_pin_frameworks_even_with_dockerfiles() -> None:
    config = configuration()
    assert "framework" not in config  # Services owns framework choice per service.
    assert "experimentalServices" not in config
    for name, framework in [("frontend", "vite"), ("backend", "fastapi")]:
        service = config["services"][name]
        assert service["root"] == f"{name}/"
        assert service["framework"] == framework
        assert service.get("runtime") != "container"
        assert (ROOT / service["root"] / "Dockerfile").is_file()
    assert config["services"]["backend"]["entrypoint"] == "app.main:app"


@pytest.mark.parametrize("path,service,target", [
    ("/api/v1/tasks", "backend", None),
    ("/api/v1/auth/me", "backend", None),
    ("/assets/index.js", "frontend", None),
    ("/dayflow-logo.svg", "frontend", None),
    ("/today", "frontend", "/index.html"),
    ("/login", "frontend", "/index.html"),
    ("/tasks", "frontend", "/index.html"),
])
def test_routing_preserves_api_assets_and_spa(path: str, service: str, target: str | None):
    # These project routes use plain regex patterns, with first-match semantics.
    rewrite = next(rule for rule in configuration()["rewrites"]
                   if re.fullmatch(rule["source"], path))
    assert rewrite["destination"]["service"] == service
    assert rewrite["destination"].get("path") == target
