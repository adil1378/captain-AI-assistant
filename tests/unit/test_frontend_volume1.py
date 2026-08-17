"""
Unit Tests for Frontend Volume 1 — Design Foundation Implementation.
Verifies specifications, design tokens, typography hierarchy, component states, 
screen layout regions, and responsive motion principles.
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume1_specifications_exist():
    """Verify all 6 specification files for Frontend Volume 1 exist."""
    specs = [
        "volume_1_part_1a.md",
        "volume_1_part_1b.md",
        "volume_1_part_1c.md",
        "volume_1_part_1d.md",
        "volume_1_part_1e.md",
        "volume_1_part_1f.md",
    ]
    for spec_name in specs:
        spec_path = _FRONTEND_BIBLE_DIR / spec_name
        assert spec_path.exists(), f"Missing spec: {spec_name}"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec {spec_name} missing approval status"


def test_css_design_tokens_volume1():
    """Verify style.css implements Volume 1 Design Tokens & Typography Hierarchy."""
    style_path = _UI_WEB_DIR / "style.css"
    assert style_path.exists(), "style.css missing"
    css_content = style_path.read_text(encoding="utf-8")

    # Tokens check
    assert "--bg-color:" in css_content
    assert "--primary-glow:" in css_content
    assert "--font-family-sans:" in css_content
    assert "--font-size-display:" in css_content
    assert "--elevation-overlay:" in css_content
    assert "--z-captain-core:" in css_content
    assert "--motion-normal:" in css_content

    # Component States (Part 1D)
    assert ".state-default" in css_content
    assert ".state-hover" in css_content
    assert ".state-active" in css_content
    assert ".state-disabled" in css_content
    assert ".state-error" in css_content

    # Responsive Breakpoint Tiers (Part 1E)
    assert "@media (min-width: 1440px)" in css_content
    assert "@media (max-width: 1200px)" in css_content
    assert "@media (max-width: 992px)" in css_content
    assert "@media (max-width: 768px)" in css_content
    assert "@media (max-width: 480px)" in css_content

    # Reduced Motion Accessibility (Part 1F)
    assert "@media (prefers-reduced-motion: reduce)" in css_content


def test_html_layout_regions_volume1():
    """Verify index.html includes the 5 functional screen layout regions & ARIA roles."""
    html_path = _UI_WEB_DIR / "index.html"
    assert html_path.exists(), "index.html missing"
    html_content = html_path.read_text(encoding="utf-8")

    assert "region-navigation" in html_content
    assert "region-captain-core" in html_content
    assert "region-workspace" in html_content
    assert "region-utility" in html_content
    assert 'role="main"' in html_content
    assert 'role="banner"' in html_content
    assert 'aria-live="polite"' in html_content
