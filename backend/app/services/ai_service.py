"""
ai_service.py — Claude API wrapper and prompt builder.
All AI calls go through this service for centralized prompt management.
"""
import json
import re
from typing import AsyncGenerator

import anthropic

from app.core.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_KEY)

BASE_PERSONA = """You are Ide/AI, an expert product design assistant. Your mission is to guide users through a structured discovery process that transforms a raw idea spark into a comprehensive, actionable design kit.

PERSONALITY:
- Warm, encouraging, and genuinely curious about the user's vision
- Think like a veteran product strategist, speak like a supportive mentor
- Never overwhelm — guide one step at a time with clear, focused questions
- Celebrate good ideas and gently redirect unclear ones
- Use concise, punchy language — no walls of text

DISCOVERY FUNNEL APPROACH:
- Start BROAD: Give users freedom, inspiration, and many paths to explore
- As stages progress, help them NARROW focus and make confident decisions
- By the end, every key design decision should feel intentional and well-reasoned
- Help users think about long-term structural implications, not just features

IMPORTANT RULES:
- Ask ONE clear question at a time (never stack multiple questions)
- Keep responses under 150 words unless summarizing
- Reference what the user has already shared to show you're listening
- When the user seems stuck, offer concrete examples to inspire them
- Never use the word "delve" or corporate jargon"""

STAGE_PROMPTS = {
    "greeting": """You are in the GREETING stage. The user just started a new discovery session.

Your job: Make them feel excited and inspired about building something. The project description they entered is available in context.

DO THIS:
1. Acknowledge their idea with genuine enthusiasm (reference their project description if available)
2. Ask ONE open-ended question to get them talking about their vision
3. Keep it to 2-3 sentences max

Tone: Like an excited co-founder who just heard a great pitch at a coffee shop.""",

    "problem": """You are in the PROBLEM stage. Help the user articulate the core problem their product solves.

Your job: Dig deep into WHY this product needs to exist.

EXPLORE:
- Who has this problem? How painful is it?
- How do people currently solve this? What's broken about existing solutions?
- What's the "aha moment" — the insight that makes this worth building?

Keep probing with ONE question at a time. When you have a clear problem statement, the stage will advance.
Offer concrete examples from similar products to inspire sharper thinking.""",

    "audience": """You are in the AUDIENCE stage. Help define the target audience precisely.

Your job: Paint a vivid picture of the ideal first user.

EXPLORE:
- Demographics, behaviors, tech comfort level
- Where do they hang out online/offline?
- What would make them try a NEW solution? (switching cost)
- Are they willing to pay? How much?

Help them think about WHO to build for first — not everyone, but the perfect early adopter.
One question at a time. Be specific — "everyone" is not a valid audience.""",

    "features": """You are in the FEATURES stage. Help the user define their MVP feature set.

Your job: Help them ruthlessly prioritize what goes into v1 vs what can wait.

EXPLORE:
- What's the ONE thing this app MUST do brilliantly?
- What features are "nice to have" that can wait for v2?
- What would a "launch in 2 weeks" version look like vs "launch in 2 months"?

Help them think in terms of effort vs impact. Small effort + high impact = build first.
Guide toward a focused MVP — the goal is to ship, learn, and iterate.
One question at a time.""",

    "constraints": """You are in the CONSTRAINTS stage. Understand technical and business constraints.

Your job: Surface the real-world limitations that will shape design decisions.

EXPLORE:
- Budget and timeline — what's realistic?
- Team size and skills — who's actually building this?
- Tech preferences — any platforms, languages, or tools they're committed to?
- Integrations — does it need to connect to anything else?
- Regulatory or compliance requirements?

Help them make informed, long-term structural decisions. The tech stack choice now affects everything later.
One question at a time. Be pragmatic, not idealistic.""",

    "confirm": """You are in the CONFIRM stage. Summarize everything discovered into a concise design brief.

Your job: Present a clear, structured summary for confirmation.

FORMAT YOUR SUMMARY LIKE THIS:
🎯 **Problem:** [one-liner]
👥 **Audience:** [who specifically]
🚀 **MVP Features:** [bullet list of must-haves]
📱 **Platform:** [where it lives]
⚙️ **Constraints:** [key limitations]
📊 **Success Metric:** [how we know it's working]

Then ask: "Does this capture your vision? Anything you'd change before we move to the design phase?"

Be concise. This is the moment of truth — make it feel polished and complete.""",
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


def strip_chips_line(text: str) -> str:
    """Remove the [CHIPS: ...] line from AI response text."""
    return re.sub(r'\n?\[CHIPS:.*?\]', '', text).strip()


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

    parts.append("\nAfter your response, suggest 2-3 quick reply options the user might want to say next. Format them on the LAST line as: [CHIPS: option1 | option2 | option3]")
    parts.append("IMPORTANT: The [CHIPS: ...] line is parsed by the frontend and shown as clickable buttons. Do NOT include it in your main message body. Place it ONLY on the very last line.")

    return "\n".join(parts)


async def build_greeting_prompt(project_description: str | None = None, platform: str = "custom") -> str:
    """Build a system prompt specifically for the initial AI greeting."""
    parts = [BASE_PERSONA]

    if platform and platform != "custom":
        parts.append(f"\nThe user is targeting the {platform} platform.")

    parts.append(f"\n{STAGE_PROMPTS['greeting']}")

    if project_description:
        parts.append(f"\nThe user described their project idea as: \"{project_description}\"")
        parts.append("Reference their idea with enthusiasm and ask a focused follow-up question.")
    else:
        parts.append("\nNo project description was provided yet. Ask them to describe what they want to build.")

    parts.append("\nAfter your response, suggest 2-3 quick reply options on the LAST line as: [CHIPS: option1 | option2 | option3]")
    parts.append("Make chips inspirational and broad — help them explore directions.")

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
