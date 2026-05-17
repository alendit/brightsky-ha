import json
from pathlib import Path

from PIL import Image


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


def test_brand_assets_are_present_with_expected_dimensions() -> None:
    expected_sizes = {
        "icon.png": (256, 256),
        "icon@2x.png": (512, 512),
        "dark_icon.png": (256, 256),
        "dark_icon@2x.png": (512, 512),
        "logo.png": (512, 160),
        "logo@2x.png": (1024, 320),
        "dark_logo.png": (512, 160),
        "dark_logo@2x.png": (1024, 320),
    }
    brand_dir = Path("custom_components/brightsky/brand")

    for filename, expected_size in expected_sizes.items():
        with Image.open(brand_dir / filename) as image:
            assert image.size == expected_size
            assert image.mode == "RGBA"

    assert Path("assets/brand/icon.svg").is_file()
    assert Path("assets/brand/logo.svg").is_file()
