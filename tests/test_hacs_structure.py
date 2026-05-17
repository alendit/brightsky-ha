import json
from pathlib import Path


def test_hacs_repo_contains_one_brightsky_integration() -> None:
    integrations = [
        path.name
        for path in Path("custom_components").iterdir()
        if path.is_dir() and not path.name.startswith("__")
    ]

    assert integrations == ["brightsky"]


def test_manifest_has_required_hacs_integration_fields() -> None:
    manifest = json.loads(
        Path("custom_components/brightsky/manifest.json").read_text()
    )

    assert manifest["domain"] == "brightsky"
    assert manifest["name"] == "Bright Sky"
    assert manifest["config_flow"] is True
    assert manifest["version"]
    assert manifest["iot_class"] == "cloud_polling"
