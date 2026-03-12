"""
categorization_service.py — AI-powered project categorization into 16 concept categories.
Uses Claude to analyze the completed concept sheet and assigns primary + optional secondary category.
Falls back to keyword-based matching if AI confidence is low.
"""
from __future__ import annotations

import json
from pathlib import Path

import anthropic

from app.core.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_KEY)

# Load categories from seed file
_SEED_PATH = Path(__file__).resolve().parents[3] / "concept_categories.seed.json"
_categories: list[dict] | None = None


def _load_categories() -> list[dict]:
    global _categories
    if _categories is None:
        with open(_SEED_PATH, "r", encoding="utf-8") as f:
            _categories = json.load(f)
    return _categories


def get_all_categories() -> list[dict]:
    """Return all 16 concept categories with their metadata."""
    return _load_categories()


def get_category(category_id: str) -> dict | None:
    """Look up a single category by ID."""
    for cat in _load_categories():
        if cat["id"] == category_id:
            return cat
    return None


VALID_CATEGORY_IDS = frozenset([
    "software_tech", "physical_product", "built_environment", "business_startup",
    "creative_writing", "research_academic", "art_visual", "music_audio",
    "film_video", "food_hospitality", "fashion_apparel", "education_training",
    "event_experience", "health_wellness", "social_impact", "finance_investment",
])


# --- Keyword fallback ---

_KEYWORD_MAP: dict[str, list[str]] = {
    "software_tech": ["app", "saas", "api", "software", "plugin", "website", "platform", "tool", "dashboard", "bot"],
    "physical_product": ["product", "hardware", "gadget", "device", "manufacturing", "physical", "consumer goods"],
    "built_environment": ["house", "building", "interior", "renovation", "architecture", "landscape", "room", "floor plan"],
    "business_startup": ["business", "startup", "venture", "franchise", "service", "company", "revenue"],
    "creative_writing": ["novel", "screenplay", "script", "story", "book", "comic", "fiction", "writing", "chapter"],
    "research_academic": ["research", "study", "paper", "theory", "experiment", "hypothesis", "formula", "academic"],
    "art_visual": ["art", "painting", "installation", "graphic", "photography", "visual", "illustration", "gallery"],
    "music_audio": ["music", "album", "song", "composition", "podcast", "sound", "audio", "live show", "concert"],
    "film_video": ["film", "movie", "documentary", "video", "youtube", "commercial", "animation", "short film"],
    "food_hospitality": ["restaurant", "cafe", "food", "menu", "catering", "hospitality", "recipe", "kitchen"],
    "fashion_apparel": ["fashion", "clothing", "apparel", "brand", "collection", "accessory", "textile", "designer"],
    "education_training": ["course", "curriculum", "workshop", "training", "education", "coaching", "learning", "lesson"],
    "event_experience": ["event", "conference", "festival", "exhibition", "pop-up", "activation", "concert venue"],
    "health_wellness": ["health", "wellness", "fitness", "clinic", "therapy", "mental health", "medical", "gym"],
    "social_impact": ["nonprofit", "charity", "community", "advocacy", "ngo", "social impact", "volunteer", "donation"],
    "finance_investment": ["finance", "investment", "fund", "fintech", "trading", "banking", "portfolio", "stock"],
}


def _keyword_fallback(concept_text: str) -> dict:
    """Simple keyword matching as fallback categorization."""
    text = concept_text.lower()
    scores: dict[str, int] = {}
    for cat_id, keywords in _KEYWORD_MAP.items():
        scores[cat_id] = sum(1 for kw in keywords if kw in text)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if ranked[0][1] == 0:
        return {
            "primary_category": "software_tech",
            "secondary_category": None,
            "confidence": 0.3,
            "reasoning": "No strong keyword signals — defaulting to software & tech.",
        }

    primary = ranked[0]
    secondary = ranked[1] if len(ranked) > 1 and ranked[1][1] > 0 else None

    return {
        "primary_category": primary[0],
        "secondary_category": secondary[0] if secondary else None,
        "confidence": min(primary[1] / 5.0, 1.0),
        "reasoning": f"Keyword match: {primary[1]} signals for {primary[0]}.",
    }


async def categorize_project(
    concept_sheet: dict,
    project_name: str = "",
    project_description: str = "",
) -> dict:
    """
    Categorize a project based on its concept sheet, name, and description.

    The project name and description are the most reliable signals (set at
    creation time), so they're always included even if concept sheet fields
    are sparse after a short discovery session.

    Returns:
        {"primary_category": str, "secondary_category": str|None, "confidence": float, "reasoning": str}
    """
    categories = _load_categories()
    options = "\n".join(
        f'- "{c["id"]}": {c["label"]} — examples: {", ".join(c["examples"])}'
        for c in categories
    )

    # Build a text summary — start with the always-available project info
    parts = []
    if project_name:
        parts.append(f"project_name: {project_name}")
    if project_description:
        parts.append(f"project_description: {project_description}")

    # Add structured concept sheet fields
    for key in ["problem", "audience", "mvp", "tone", "platform", "tech_constraints", "success_metric"]:
        val = concept_sheet.get(key)
        if val:
            parts.append(f"{key}: {val}")
    features = concept_sheet.get("features", [])
    if features:
        feat_names = [f.get("name", "") for f in features if isinstance(f, dict)]
        parts.append(f"features: {', '.join(feat_names)}")
    fields_data = concept_sheet.get("fields_data", {})
    if fields_data:
        for k, v in fields_data.items():
            parts.append(f"{k}: {v}")

    concept_text = "\n".join(parts)
    if not concept_text.strip():
        return _keyword_fallback("")

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=256,
            system=(
                "You are a project categorizer. Analyze the concept sheet and assign:\n"
                "1. A PRIMARY category (required)\n"
                "2. A SECONDARY category (optional — only if the project genuinely spans two domains)\n\n"
                f"Available categories:\n{options}\n\n"
                "Respond with ONLY valid JSON:\n"
                '{"primary_category": "<id>", "secondary_category": "<id>|null", '
                '"confidence": <0.0-1.0>, "reasoning": "<brief reason>"}'
            ),
            messages=[{
                "role": "user",
                "content": f"Categorize this project:\n\n{concept_text[:1000]}",
            }],
        )

        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)

        primary = result.get("primary_category", "software_tech")
        secondary = result.get("secondary_category")

        # Validate IDs
        if primary not in VALID_CATEGORY_IDS:
            primary = "software_tech"
        if secondary and secondary not in VALID_CATEGORY_IDS:
            secondary = None
        if secondary == primary:
            secondary = None

        confidence = float(result.get("confidence", 0.5))

        # If AI confidence is too low, try keyword fallback with all text
        if confidence < 0.4:
            return _keyword_fallback(concept_text)

        return {
            "primary_category": primary,
            "secondary_category": secondary,
            "confidence": confidence,
            "reasoning": result.get("reasoning", ""),
        }
    except Exception:
        return _keyword_fallback(concept_text)
