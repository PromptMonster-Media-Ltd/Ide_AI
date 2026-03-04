"""
discovery_service.py — Socratic discovery engine with state machine and confidence scoring.
Manages the 5-stage discovery flow and auto-updates the design sheet.
"""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import DiscoverySession
from app.models.design_sheet import DesignSheet
from app.models.project import Project
from app.services.ai_service import extract_sheet_fields

STAGE_ORDER = ["greeting", "problem", "audience", "features", "constraints", "confirm"]

STAGE_TRANSITIONS = {
    "greeting": "problem",
    "problem": "audience",
    "audience": "features",
    "features": "constraints",
    "constraints": "confirm",
    "confirm": "confirm",
}

# Fields that contribute to confidence, with their weights
CONFIDENCE_WEIGHTS = {
    "problem": 20,
    "audience": 20,
    "mvp": 15,
    "features": 20,
    "platform": 10,
    "tech_constraints": 5,
    "success_metric": 5,
    "tone": 5,
}


async def create_session(db: AsyncSession, project_id: uuid.UUID) -> DiscoverySession:
    """Create a new discovery session and initialize an empty design sheet."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Create session
    session = DiscoverySession(
        project_id=project_id,
        status="active",
        stage="greeting",
        messages=[],
    )
    db.add(session)

    # Create design sheet if it doesn't exist
    existing_sheet = await db.execute(
        select(DesignSheet).where(DesignSheet.project_id == project_id)
    )
    if not existing_sheet.scalar_one_or_none():
        sheet = DesignSheet(
            project_id=project_id,
            platform=project.platform,
            tone=project.tone,
        )
        db.add(sheet)

    await db.flush()
    return session


async def add_message(
    db: AsyncSession, session: DiscoverySession, role: str, content: str
) -> DiscoverySession:
    """Append a message to the session's message history."""
    messages = list(session.messages or [])
    messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    })
    session.messages = messages
    await db.flush()
    return session


def next_stage(current_stage: str, sheet: DesignSheet) -> str:
    """Determine the next discovery stage based on current state and sheet completeness."""
    if current_stage == "greeting":
        return "problem"

    if current_stage == "problem" and sheet.problem:
        return "audience"

    if current_stage == "audience" and sheet.audience:
        return "features"

    if current_stage == "features" and sheet.features:
        return "constraints"

    if current_stage == "constraints":
        return "confirm"

    # Stay on current stage if key fields aren't filled yet
    return current_stage


def compute_confidence(sheet: DesignSheet) -> int:
    """Compute confidence score (0-100) based on populated design sheet fields."""
    score = 0
    for field, weight in CONFIDENCE_WEIGHTS.items():
        value = getattr(sheet, field, None)
        if value:
            if isinstance(value, list) and len(value) > 0:
                score += weight
            elif isinstance(value, str) and len(value.strip()) > 0:
                score += weight
    return min(score, 100)


async def update_sheet_from_conversation(
    db: AsyncSession, session: DiscoverySession
) -> tuple[DesignSheet, bool]:
    """Extract fields from conversation and update the design sheet.
    Returns (updated_sheet, changed) tuple."""
    result = await db.execute(
        select(DesignSheet).where(DesignSheet.project_id == session.project_id)
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        return None, False

    # Build Claude-compatible messages for extraction
    claude_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in (session.messages or [])
    ]

    if not claude_messages:
        return sheet, False

    extracted = await extract_sheet_fields(claude_messages)
    if not extracted:
        return sheet, False

    changed = False
    updatable_fields = ["problem", "audience", "mvp", "tone", "platform", "tech_constraints", "success_metric"]

    for field in updatable_fields:
        if field in extracted and extracted[field]:
            current = getattr(sheet, field, None)
            new_val = extracted[field]
            if new_val and new_val != current:
                setattr(sheet, field, new_val)
                changed = True

    # Handle features separately (list type)
    if "features" in extracted and isinstance(extracted["features"], list) and extracted["features"]:
        sheet.features = extracted["features"]
        changed = True

    if changed:
        sheet.confidence_score = compute_confidence(sheet)
        # Check for stage advancement
        new_stage = next_stage(session.stage, sheet)
        if new_stage != session.stage:
            session.stage = new_stage

    await db.flush()
    return sheet, changed


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> DiscoverySession | None:
    """Fetch a discovery session by ID."""
    result = await db.execute(
        select(DiscoverySession).where(DiscoverySession.id == session_id)
    )
    return result.scalar_one_or_none()


async def get_sheet_for_project(db: AsyncSession, project_id: uuid.UUID) -> DesignSheet | None:
    """Fetch the design sheet for a project."""
    result = await db.execute(
        select(DesignSheet).where(DesignSheet.project_id == project_id)
    )
    return result.scalar_one_or_none()
