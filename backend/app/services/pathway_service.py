"""
pathway_service.py — AI-powered pathway detection.
Classifies a project description into the most appropriate concept pathway.
"""
from __future__ import annotations

import anthropic

from app.core.config import settings
from app.pathways import PathwayRegistry

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_KEY)

DEFAULT_PATHWAY = "software_product"


async def detect_pathway(description: str) -> dict:
    """
    Classify a project description into a pathway ID using Claude.

    Returns {"pathway_id": str, "confidence": float, "reasoning": str}.
    Falls back to software_product on any error.
    """
    pathways = PathwayRegistry.all()
    if len(pathways) <= 1:
        pw = pathways[0] if pathways else None
        return {
            "pathway_id": pw.id if pw else DEFAULT_PATHWAY,
            "confidence": 1.0,
            "reasoning": "Only one pathway available.",
        }

    # Build the classification options dynamically
    options = "\n".join(
        f'- "{p.id}": {p.name} — {p.description}'
        for p in pathways
    )

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=256,
            system=(
                "You are a project classifier. Given a project description, "
                "determine which creative pathway best fits.\n\n"
                "Available pathways:\n"
                f"{options}\n\n"
                "Respond with ONLY valid JSON: "
                '{"pathway_id": "<id>", "confidence": <0.0-1.0>, "reasoning": "<brief reason>"}'
            ),
            messages=[{
                "role": "user",
                "content": f"Classify this project:\n\n{description[:500]}",
            }],
        )

        import json
        text = response.content[0].text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)

        # Validate pathway_id exists
        pid = result.get("pathway_id", DEFAULT_PATHWAY)
        if pid not in PathwayRegistry.ids():
            pid = DEFAULT_PATHWAY

        return {
            "pathway_id": pid,
            "confidence": float(result.get("confidence", 0.5)),
            "reasoning": result.get("reasoning", ""),
        }
    except Exception:
        return {
            "pathway_id": DEFAULT_PATHWAY,
            "confidence": 0.5,
            "reasoning": "Classification failed — defaulting to software product.",
        }
