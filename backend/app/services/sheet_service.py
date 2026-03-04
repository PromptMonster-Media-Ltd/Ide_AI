"""
sheet_service.py — Design sheet auto-fill and block generation logic.
Extracts structured data from AI responses and generates feature blocks.
"""
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.block import Block
from app.models.design_sheet import DesignSheet
from app.services.ai_service import client

BLOCK_GENERATION_PROMPT = """Based on this design sheet, generate a list of feature blocks for the product.

Design Sheet:
- Problem: {problem}
- Audience: {audience}
- MVP Scope: {mvp}
- Features: {features}
- Platform: {platform}
- Tone: {tone}

Generate 8-12 feature blocks. For each block, provide:
- name: short feature name (2-4 words)
- description: one sentence explaining what it does
- category: one of [core, ux, data, integration, admin]
- priority: "mvp" or "v2"
- effort: "S" (1-2 days), "M" (3-5 days), or "L" (1-2 weeks)

Return as a JSON array. No markdown, just valid JSON."""


async def generate_blocks(db: AsyncSession, sheet: DesignSheet, project_id: uuid.UUID) -> list[Block]:
    """Generate feature blocks from a completed design sheet using Claude."""
    prompt = BLOCK_GENERATION_PROMPT.format(
        problem=sheet.problem or "Not specified",
        audience=sheet.audience or "Not specified",
        mvp=sheet.mvp or "Not specified",
        features=json.dumps(sheet.features or []),
        platform=sheet.platform or "Not specified",
        tone=sheet.tone or "Not specified",
    )

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=2048,
        system="You are a product feature generator. Return only valid JSON arrays.",
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        block_data = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        block_data = []

    blocks = []
    for i, bd in enumerate(block_data):
        block = Block(
            project_id=project_id,
            name=bd.get("name", f"Feature {i+1}"),
            description=bd.get("description", ""),
            category=bd.get("category", "core"),
            priority=bd.get("priority", "mvp"),
            effort=bd.get("effort", "M"),
            order=i,
            is_mvp=bd.get("priority", "mvp") == "mvp",
        )
        db.add(block)
        blocks.append(block)

    await db.flush()
    return blocks


def extract_fields(ai_response: str) -> dict:
    """Extract design sheet fields from a single AI response message.
    This is a lightweight local extraction (no API call)."""
    fields = {}
    lower = ai_response.lower()

    # Simple heuristic extraction for common patterns
    if "problem" in lower and ":" in ai_response:
        # Look for structured output patterns
        pass

    return fields
