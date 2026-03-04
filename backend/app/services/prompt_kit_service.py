"""
prompt_kit_service.py — Platform-specific prompt kit generation.
Uses Jinja2 templates and Claude to produce structured prompts for builder platforms.
"""
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.models.design_sheet import DesignSheet
from app.models.block import Block
from app.services.ai_service import client

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "prompts"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)

PROMPT_KIT_SYSTEM = """You are a prompt engineer specializing in no-code/low-code builder platforms.
Given a product design sheet and feature blocks, generate a comprehensive, structured prompt kit
that a builder could use to implement the product on the target platform.

The prompt kit should have these sections:
1. System Context — What the app is and who it's for
2. App Description — Detailed description of the product
3. Feature List — Prioritized features with implementation notes
4. Data Model — Suggested database tables/collections
5. Constraints — Technical and design constraints
6. First Task — The recommended first build step

Make the output copy-paste ready. Use clear markdown formatting."""


async def generate_prompt_kit(
    sheet: DesignSheet,
    blocks: list[Block],
    platform: str,
) -> str:
    """Generate a platform-specific prompt kit from project artifacts."""
    # Try to use Jinja2 template first
    template_name = f"{platform.lower().replace(' ', '_').replace('-', '_')}.j2"
    try:
        template = env.get_template(template_name)
        context = _build_template_context(sheet, blocks)
        rendered = template.render(**context)
        if rendered.strip():
            return rendered
    except Exception:
        pass

    # Fallback: use Claude to generate
    block_list = [
        {"name": b.name, "description": b.description, "priority": b.priority, "effort": b.effort}
        for b in blocks
    ]

    prompt = f"""Generate a prompt kit for the platform: {platform}

Design Sheet:
- Problem: {sheet.problem or 'Not specified'}
- Audience: {sheet.audience or 'Not specified'}
- MVP Scope: {sheet.mvp or 'Not specified'}
- Features: {json.dumps(sheet.features or [])}
- Platform: {sheet.platform or platform}
- Tone: {sheet.tone or 'Not specified'}
- Constraints: {sheet.tech_constraints or 'None specified'}

Feature Blocks:
{json.dumps(block_list, indent=2)}

Generate a comprehensive, ready-to-use prompt kit with all 6 sections."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4096,
        system=PROMPT_KIT_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


def _build_template_context(sheet: DesignSheet, blocks: list[Block]) -> dict:
    """Build template context dict from sheet and blocks."""
    return {
        "problem": sheet.problem or "",
        "audience": sheet.audience or "",
        "mvp": sheet.mvp or "",
        "features": sheet.features or [],
        "platform": sheet.platform or "",
        "tone": sheet.tone or "",
        "tech_constraints": sheet.tech_constraints or "",
        "success_metric": sheet.success_metric or "",
        "blocks": [
            {
                "name": b.name,
                "description": b.description or "",
                "category": b.category,
                "priority": b.priority,
                "effort": b.effort,
                "is_mvp": b.is_mvp,
            }
            for b in blocks
        ],
    }
