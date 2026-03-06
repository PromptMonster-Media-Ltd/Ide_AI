"""
memory_service.py — Extract and manage user memory from conversations.
Uses Claude to analyse discovery conversations and persist reusable insights.
"""
import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user_memory import UserMemory
from app.services.ai_service import client

MEMORY_EXTRACTION_PROMPT = """Analyze this conversation and extract the user's key preferences, constraints, and insights.
Return a JSON array of objects: [{"key": "preferred_stack", "value": "React + FastAPI", "category": "preference"}, ...]
Categories: preference, constraint, style, insight
Extract 3-8 insights maximum. Focus on reusable info for future projects.
Only return the JSON array — no markdown, no extra text."""


async def extract_memories(messages: list[dict], project_name: str) -> list[dict]:
    """Use Claude to analyse a conversation and extract key user preferences/insights.

    Args:
        messages: List of {"role": ..., "content": ...} dicts from a discovery session.
        project_name: The name of the project being discussed (added to context).

    Returns:
        List of dicts with keys: key, value, category.
    """
    if not messages:
        return []

    extraction_messages = messages + [
        {"role": "user", "content": MEMORY_EXTRACTION_PROMPT},
    ]

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1024,
            system=f"You are a data extraction assistant. The conversation is about a project called '{project_name}'. Return only valid JSON.",
            messages=extraction_messages,
        )
        text = response.content[0].text.strip()
        # Handle possible markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        memories = json.loads(text)
        if not isinstance(memories, list):
            return []
        return [
            m for m in memories
            if isinstance(m, dict) and "key" in m and "value" in m
        ]
    except (json.JSONDecodeError, IndexError, KeyError, Exception):
        return []


async def save_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    memories: list[dict],
    project_name: str,
) -> list[UserMemory]:
    """Store extracted memories, deduplicating by key.

    If a memory with the same key already exists for the user, its value and
    context are updated rather than creating a duplicate.
    """
    saved = []
    for mem in memories:
        key = mem.get("key", "").strip()
        value = mem.get("value", "").strip()
        category = mem.get("category", "insight").strip()

        if not key or not value:
            continue

        # Check for existing memory with same key
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == user_id,
                UserMemory.key == key,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = value
            existing.context = project_name
            existing.category = category
            saved.append(existing)
        else:
            memory = UserMemory(
                user_id=user_id,
                key=key,
                value=value,
                context=project_name,
                category=category,
            )
            db.add(memory)
            saved.append(memory)

    await db.flush()
    return saved


async def load_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
) -> list[UserMemory]:
    """Load the most recent memories for a user.

    Returns memories ordered by creation date descending.
    """
    result = await db.execute(
        select(UserMemory)
        .where(UserMemory.user_id == user_id)
        .order_by(UserMemory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


def format_memory_context(memories: list[UserMemory]) -> str:
    """Format memories as a bullet-point context block for system prompts.

    Returns an empty string if there are no memories.
    """
    if not memories:
        return ""

    lines = ["User Context (from previous sessions):"]
    for m in memories:
        label = m.category.capitalize() if m.category else "Note"
        lines.append(f"- [{label}] {m.key}: {m.value}")
    return "\n".join(lines)
