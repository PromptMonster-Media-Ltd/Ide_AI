"""
ai_service.py — Claude API wrapper and prompt builder.
All AI calls go through this service for centralized prompt management.
"""
import json
from typing import AsyncGenerator

import anthropic

from app.core.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

BASE_PERSONA = """You are Ide/AI, an expert product design assistant. Your role is to guide users through a structured discovery process to transform rough product ideas into comprehensive, actionable design kits.

You are warm, encouraging, and ask sharp clarifying questions. You think like a product strategist and speak like a mentor. You never overwhelm — you guide one step at a time."""

STAGE_PROMPTS = {
    "greeting": """You are in the GREETING stage. The user just started a new project.
Warmly welcome them and ask them to describe their product idea in their own words.
Keep it brief and encouraging. Ask ONE clear question about what they want to build.""",

    "problem": """You are in the PROBLEM stage. Help the user articulate the core problem their product solves.
Ask probing questions like: Who has this problem? How do they currently solve it? What makes this painful?
Extract: the problem statement and target audience hints.""",

    "audience": """You are in the AUDIENCE stage. Help define the target audience precisely.
Ask about: demographics, behaviors, tech comfort level, willingness to pay.
Extract: audience description, platform hints.""",

    "features": """You are in the FEATURES stage. Help the user define their MVP feature set.
Ask about: must-have features, nice-to-haves, what's the ONE thing the app must do well?
Extract: feature list, MVP scope, effort estimates.""",

    "constraints": """You are in the CONSTRAINTS stage. Understand technical and business constraints.
Ask about: budget, timeline, team size, existing tech preferences, integrations needed.
Extract: tech constraints, success metrics, platform preference.""",

    "confirm": """You are in the CONFIRM stage. Summarize everything discovered so far into a concise design brief.
Present: Problem, Audience, MVP Features, Platform, Constraints, and Success Metrics.
Ask the user to confirm or suggest changes. Be concise and structured.""",
}

EXTRACTION_PROMPT = """Based on the conversation so far, extract any design sheet fields you can identify.
Return a JSON object with ONLY the fields you can confidently extract. Use these field names:
- problem: string (the core problem being solved)
- audience: string (target audience description)
- mvp: string (MVP scope description)
- features: array of objects with {name: string, description: string, priority: "mvp"|"v2"}
- tone: string (app tone/style)
- platform: string (target platform)
- tech_constraints: string (technical constraints)
- success_metric: string (how success is measured)

Only include fields where you have clear information. Return valid JSON only, no markdown."""


async def build_system_prompt(platform: str, stage: str, sheet_context: dict | None = None) -> str:
    """Build a dynamic system prompt from project context and discovery stage."""
    parts = [BASE_PERSONA]

    if platform and platform != "custom":
        parts.append(f"\nThe user is targeting the {platform} platform. Keep recommendations relevant to this platform's capabilities and constraints.")

    stage_prompt = STAGE_PROMPTS.get(stage, STAGE_PROMPTS["greeting"])
    parts.append(f"\n{stage_prompt}")

    if sheet_context:
        filled = {k: v for k, v in sheet_context.items() if v}
        if filled:
            parts.append(f"\nDesign sheet so far: {json.dumps(filled, indent=2)}")

    parts.append("\nAfter your response, suggest 2-3 quick reply options the user might want to say next. Format them on the last line as: [CHIPS: option1 | option2 | option3]")

    return "\n".join(parts)


async def stream_response(messages: list, system_prompt: str) -> AsyncGenerator[str, None]:
    """Stream Claude API response tokens as an async generator."""
    async with client.messages.stream(
        model=settings.CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def extract_sheet_fields(messages: list) -> dict:
    """Extract design sheet fields from conversation using Claude."""
    extraction_messages = messages + [
        {"role": "user", "content": EXTRACTION_PROMPT}
    ]

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=1024,
        system="You are a data extraction assistant. Return only valid JSON.",
        messages=extraction_messages,
    )

    try:
        text = response.content[0].text.strip()
        # Handle possible markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except (json.JSONDecodeError, IndexError, KeyError):
        return {}


async def generate_quick_chips(ai_response: str) -> list[str]:
    """Parse quick reply chips from AI response. Returns list of chip strings."""
    chips = []
    for line in ai_response.split("\n"):
        if line.strip().startswith("[CHIPS:") and line.strip().endswith("]"):
            inner = line.strip()[7:-1]  # Remove [CHIPS: and ]
            chips = [c.strip() for c in inner.split("|") if c.strip()]
            break
    return chips or ["Tell me more", "Let's move on", "I'm not sure yet"]
