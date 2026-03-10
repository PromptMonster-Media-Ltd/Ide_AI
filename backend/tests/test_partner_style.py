"""
Tests for the AI Partner Style system.

Covers:
    1. Partner style validation
    2. Prompt fragment selection
    3. Namesake behaviour rule in prompt composition
    4. Mid-session switching (service layer)
    5. Metadata listing
"""
import pytest

from app.services.partner_style_service import (
    DEFAULT_PARTNER_STYLE,
    VALID_PARTNER_STYLES,
    get_partner_metadata,
    get_partner_style_fragment,
    list_partner_styles,
    validate_partner_style,
)


# ── 1. Validation ─────────────────────────────────────────────────────

class TestValidation:
    def test_valid_styles_accepted(self):
        for style in VALID_PARTNER_STYLES:
            assert validate_partner_style(style) == style

    def test_none_returns_default(self):
        assert validate_partner_style(None) == DEFAULT_PARTNER_STYLE

    def test_case_insensitive(self):
        assert validate_partner_style("SKEPTIC") == "skeptic"
        assert validate_partner_style("Visionary") == "visionary"
        assert validate_partner_style("  Coach  ") == "coach"

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="Invalid partner style"):
            validate_partner_style("invalid_style")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            validate_partner_style("")


# ── 2. Prompt fragment selection ──────────────────────────────────────

class TestPromptFragments:
    def test_all_styles_have_fragments(self):
        for style in VALID_PARTNER_STYLES:
            fragment = get_partner_style_fragment(style)
            assert isinstance(fragment, str)
            assert len(fragment) > 100, f"Fragment for {style} seems too short"

    def test_fragment_contains_style_name(self):
        """Each fragment should reference its own partner name."""
        for style in VALID_PARTNER_STYLES:
            fragment = get_partner_style_fragment(style)
            # The title-cased name should appear in the fragment
            assert style.capitalize() in fragment or style.title() in fragment, (
                f"Fragment for '{style}' does not mention its own name"
            )

    def test_default_fragment_works(self):
        fragment = get_partner_style_fragment(DEFAULT_PARTNER_STYLE)
        assert "Strategist" in fragment


# ── 3. Namesake behaviour rule ────────────────────────────────────────

class TestNamesakeRule:
    """Verify that each partner fragment contains language that genuinely
    aligns with its namesake identity, not just a cosmetic label."""

    @pytest.mark.parametrize("style,expected_keywords", [
        ("creative", ["imaginative", "expressive", "originality"]),
        ("intellectual", ["coherence", "rigour", "logic"]),
        ("trailblazer", ["conventions", "bold", "differentiation"]),
        ("strategist", ["priorities", "trade-offs", "outcomes"]),
        ("architect", ["systems", "modules", "dependencies"]),
        ("coach", ["safe", "manageable", "momentum"]),
        ("skeptic", ["stress-test", "assumptions", "risks"]),
        ("visionary", ["scale", "largest", "future"]),
        ("editor", ["clarity", "sharpen", "tighten"]),
        ("scientist", ["hypotheses", "variables", "evidence"]),
    ])
    def test_fragment_contains_namesake_keywords(self, style: str, expected_keywords: list[str]):
        fragment = get_partner_style_fragment(style).lower()
        found = [kw for kw in expected_keywords if kw in fragment]
        assert len(found) >= 2, (
            f"Partner '{style}' fragment only matched {found} out of {expected_keywords}. "
            f"The partner must genuinely live up to its namesake."
        )


# ── 4. Mid-session switching ─────────────────────────────────────────

class TestMidSessionSwitching:
    """Verify that switching styles produces different prompt fragments."""

    def test_switching_styles_changes_fragment(self):
        frag_a = get_partner_style_fragment("skeptic")
        frag_b = get_partner_style_fragment("coach")
        assert frag_a != frag_b, "Different partner styles must produce different fragments"

    def test_switching_preserves_valid_style(self):
        """Validate the new style before applying."""
        style = validate_partner_style("editor")
        assert style == "editor"
        fragment = get_partner_style_fragment(style)
        assert "Editor" in fragment


# ── 5. Metadata listing ──────────────────────────────────────────────

class TestMetadata:
    def test_list_returns_all_styles(self):
        styles = list_partner_styles()
        assert len(styles) == 10
        ids = {s["id"] for s in styles}
        assert ids == VALID_PARTNER_STYLES

    def test_metadata_has_required_fields(self):
        for meta in list_partner_styles():
            assert "id" in meta
            assert "name" in meta
            assert "icon" in meta
            assert "color" in meta
            assert "description" in meta
            assert "best_for" in meta
            assert "traits" in meta
            assert len(meta["traits"]) >= 2

    def test_get_partner_metadata_returns_copy(self):
        meta = get_partner_metadata("skeptic")
        assert meta is not None
        assert meta["id"] == "skeptic"

    def test_get_partner_metadata_invalid(self):
        with pytest.raises(ValueError):
            get_partner_metadata("nonexistent")


# ── 6. Prompt composition integration ────────────────────────────────

class TestPromptComposition:
    """Verify that build_system_prompt correctly injects the partner fragment."""

    @pytest.mark.asyncio
    async def test_build_system_prompt_includes_partner_fragment(self):
        from app.services.ai_service import build_system_prompt

        prompt = await build_system_prompt(
            platform="custom",
            stage="greeting",
            ai_partner_style="skeptic",
        )
        assert "Skeptic" in prompt
        assert "stress-test" in prompt.lower()

    @pytest.mark.asyncio
    async def test_build_system_prompt_default_partner(self):
        from app.services.ai_service import build_system_prompt

        prompt = await build_system_prompt(
            platform="custom",
            stage="greeting",
        )
        # Default is strategist
        assert "Strategist" in prompt

    @pytest.mark.asyncio
    async def test_build_greeting_prompt_includes_partner(self):
        from app.services.ai_service import build_greeting_prompt

        prompt = await build_greeting_prompt(
            project_description="A mindfulness app",
            platform="web",
            ai_partner_style="coach",
        )
        assert "Coach" in prompt
        assert "momentum" in prompt.lower() or "safe" in prompt.lower()

    @pytest.mark.asyncio
    async def test_different_partners_produce_different_prompts(self):
        from app.services.ai_service import build_system_prompt

        prompt_a = await build_system_prompt("custom", "problem", ai_partner_style="visionary")
        prompt_b = await build_system_prompt("custom", "problem", ai_partner_style="editor")
        assert prompt_a != prompt_b
        assert "Visionary" in prompt_a
        assert "Editor" in prompt_b
