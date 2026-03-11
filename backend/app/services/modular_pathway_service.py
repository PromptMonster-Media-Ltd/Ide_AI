"""
modular_pathway_service.py — Assembles and manages dynamic module pathways.

Flow:
1. get_base_stack(category_id) → default modules for that category
2. run_enrichment_pass(base_stack, concept_sheet, secondary_category) → adjusted stack
3. assemble_pathway(project, primary, secondary) → full ordered module list with metadata
4. apply_user_edits(pathway, edits) → updated module list
"""
from __future__ import annotations

import json
from pathlib import Path

from app.services.categorization_service import get_category, _load_categories

# Load module library from seed file
_MODULE_SEED_PATH = Path(__file__).resolve().parents[3] / "module_library.seed.json"
_module_library: list[dict] | None = None

# Existing modules that map to existing pages (not AI-guided conversations)
EXISTING_MODULE_IDS = {
    "design_blocks_board": "Design Blocks Board",
    "pipeline_builder": "Pipeline Builder",
    "prompt_kit_generator": "Prompt Kit Generator",
    "market_analysis": "Market Analysis",
    "sprint_planner": "Sprint Planner",
    "pitch_mode": "Pitch Mode",
    "export_system": "Export System",
}

# Map existing module names in seed data to their IDs
_EXISTING_NAME_TO_ID = {
    "Design Blocks Board": "design_blocks_board",
    "Pipeline Builder": "pipeline_builder",
    "Prompt Kit Generator": "prompt_kit_generator",
    "Market Analysis": "market_analysis",
    "Sprint Planner": "sprint_planner",
    "Pitch Mode": "pitch_mode",
    "Export System": "export_system",
}


def _load_modules() -> list[dict]:
    global _module_library
    if _module_library is None:
        with open(_MODULE_SEED_PATH, "r", encoding="utf-8") as f:
            _module_library = json.load(f)
    return _module_library


def get_all_modules() -> list[dict]:
    """Return all module definitions from the library."""
    new_modules = _load_modules()
    # Add existing modules as definitions too
    existing = [
        {
            "id": mid,
            "label": name,
            "group": "Existing",
            "description": f"Existing {name} module — routes to dedicated page.",
            "estimated_time_lite": "5 min",
            "estimated_time_deep": "15 min",
            "default_mode": "lite",
        }
        for mid, name in EXISTING_MODULE_IDS.items()
    ]
    return existing + new_modules


def get_module_definition(module_id: str) -> dict | None:
    """Look up a single module by ID."""
    for m in get_all_modules():
        if m["id"] == module_id:
            return m
    return None


def get_base_stack(category_id: str) -> list[str]:
    """Return the default module stack for a category."""
    cat = get_category(category_id)
    if not cat:
        # Fallback to software_tech
        cat = get_category("software_tech")
    return list(cat.get("default_modules", []))


# --- Enrichment signals ---

_ENRICHMENT_RULES: list[dict] = [
    {
        "signal_keywords": ["investor", "fundrais", "funding", "raise capital", "vc", "angel"],
        "add": ["revenue_model_designer", "investor_deck_outline", "financial_projection_builder"],
    },
    {
        "signal_keywords": ["physical location", "space", "venue", "building", "room", "floor"],
        "add": ["space_program", "footprint_flow_diagram"],
    },
    {
        "signal_keywords": ["solo", "alone", "one person", "just me", "no team"],
        "flag_optional": ["team_resource_planner"],
    },
    {
        "signal_keywords": ["regulated", "medical", "food safety", "fda", "hipaa", "license", "legal requirement"],
        "add": ["regulatory_compliance_check"],
    },
    {
        "signal_keywords": ["brand", "identity", "logo", "visual identity", "brand voice"],
        "add": ["brand_identity_framework", "design_language_guide"],
    },
    {
        "signal_keywords": ["competi", "rival", "alternative", "market share"],
        "add": ["market_analysis"],
    },
    {
        "signal_keywords": ["deadline", "timeline", "launch date", "time pressure", "urgent"],
        "add": ["dependency_mapper", "sprint_planner"],
    },
    {
        "signal_keywords": ["content", "blog", "social media", "marketing content"],
        "add": ["content_strategy"],
    },
    {
        "signal_keywords": ["partner", "press", "influencer", "collaborat"],
        "add": ["partnership_outreach_map"],
    },
]


def run_enrichment_pass(
    base_stack: list[str],
    concept_sheet: dict,
    secondary_category: str | None = None,
) -> list[str]:
    """
    Adjust the base module stack based on concept sheet signals.
    Adds/removes modules based on detected keywords and secondary category.
    """
    stack = list(base_stack)

    # Build searchable text from concept sheet
    parts = []
    for key in ["problem", "audience", "mvp", "tone", "platform", "tech_constraints", "success_metric"]:
        val = concept_sheet.get(key)
        if val:
            parts.append(str(val))
    features = concept_sheet.get("features", [])
    for f in features:
        if isinstance(f, dict):
            parts.append(f.get("name", ""))
            parts.append(f.get("description", ""))
    fields_data = concept_sheet.get("fields_data", {})
    for v in fields_data.values():
        parts.append(str(v))

    text = " ".join(parts).lower()

    # Apply enrichment rules
    for rule in _ENRICHMENT_RULES:
        triggered = any(kw in text for kw in rule.get("signal_keywords", []))
        if triggered:
            for module_id in rule.get("add", []):
                if module_id not in stack:
                    stack.append(module_id)

    # Secondary category enrichment
    if secondary_category == "software_tech":
        for mid in ["pipeline_builder", "prompt_kit_generator"]:
            if mid not in stack:
                stack.append(mid)
    elif secondary_category == "business_startup":
        for mid in ["revenue_model_designer", "business_model_canvas"]:
            if mid not in stack:
                stack.append(mid)

    # Low confidence enrichment
    confidence = concept_sheet.get("confidence_score", 0)
    if isinstance(confidence, (int, float)) and confidence < 40:
        for mid in ["assumptions_log", "proof_of_concept_planner"]:
            if mid not in stack:
                stack.append(mid)

    return stack


def assemble_pathway(
    concept_sheet: dict,
    primary_category: str,
    secondary_category: str | None = None,
) -> dict:
    """
    Full pathway assembly: base stack + enrichment + metadata.

    Returns:
        {
            "modules": [{"module_id", "label", "description", "group", "estimated_time", "mode", "reason"}],
            "primary_category": str,
            "secondary_category": str|None,
        }
    """
    base = get_base_stack(primary_category)
    enriched = run_enrichment_pass(base, concept_sheet, secondary_category)

    modules = []
    base_set = set(base)
    for mid in enriched:
        defn = get_module_definition(mid)
        if not defn:
            continue
        mode = defn.get("default_mode", "lite")
        est_time = defn.get("estimated_time_deep" if mode == "deep" else "estimated_time_lite", "5 min")

        if mid in base_set:
            reason = f"Default module for {primary_category} projects."
        else:
            reason = "Added based on project signals detected in concept sheet."

        modules.append({
            "module_id": mid,
            "label": defn["label"],
            "description": defn["description"],
            "group": defn["group"],
            "estimated_time": est_time,
            "mode": mode,
            "reason": reason,
        })

    return {
        "modules": modules,
        "primary_category": primary_category,
        "secondary_category": secondary_category,
    }


def get_lite_deep_defaults(module_ids: list[str]) -> dict[str, str]:
    """Return default lite/deep settings for a list of module IDs."""
    settings = {}
    for mid in module_ids:
        defn = get_module_definition(mid)
        settings[mid] = defn.get("default_mode", "lite") if defn else "lite"
    return settings
