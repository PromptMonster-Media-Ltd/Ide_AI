"""
discovery.py — Discovery session router. Handles SSE streaming AI conversations.
"""
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.session import MessagePayload, SessionCreate, SessionRead
from app.schemas.design_sheet import DesignSheetRead
from app.services import discovery_service, ai_service

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/start", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def start_session(
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new discovery session for a project."""
    # Verify project ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == payload.project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    try:
        session = await discovery_service.create_session(db, payload.project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return session


@router.post("/{session_id}/init")
async def init_greeting(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate the AI's opening greeting for a discovery session. No user message needed."""
    session = await discovery_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Verify project ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == session.project_id, Project.user_id == current_user.id)
    )
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active")

    # Don't re-init if session already has messages
    if session.messages and len(session.messages) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already initialized")

    # Build greeting prompt with project context
    system_prompt = await ai_service.build_greeting_prompt(
        project_description=project.description,
        platform=project.platform or "custom",
    )

    # The AI speaks first — no user message in the history
    claude_messages = [{"role": "user", "content": f"I want to build: {project.description or project.name}"}]

    async def event_stream():
        full_response = []

        async for token in ai_service.stream_response(claude_messages, system_prompt):
            full_response.append(token)
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        ai_text = "".join(full_response)

        # Strip chips from stored message
        clean_text = ai_service.strip_chips_line(ai_text)

        # Save only the assistant message (no user message visible)
        await discovery_service.add_message(db, session, "assistant", clean_text)
        await db.commit()

        # Send completion event with chips
        chips = await ai_service.generate_quick_chips(ai_text)
        yield f"data: {json.dumps({'type': 'done', 'stage': session.stage, 'chips': chips})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{session_id}/message")
async def send_message(
    session_id: uuid.UUID,
    payload: MessagePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message in a discovery session. Returns SSE stream."""
    session = await discovery_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Verify project ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == session.project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active")

    # Add user message
    await discovery_service.add_message(db, session, "user", payload.content)
    await db.commit()

    # Get the design sheet for context
    sheet = await discovery_service.get_sheet_for_project(db, session.project_id)
    sheet_context = None
    if sheet:
        sheet_context = {
            "problem": sheet.problem,
            "audience": sheet.audience,
            "mvp": sheet.mvp,
            "platform": sheet.platform,
            "tone": sheet.tone,
        }

    # Build system prompt
    proj_result = await db.execute(select(Project).where(Project.id == session.project_id))
    project = proj_result.scalar_one_or_none()
    platform = project.platform if project else "custom"

    system_prompt = await ai_service.build_system_prompt(platform, session.stage, sheet_context)

    # Build Claude message history
    claude_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in (session.messages or [])
    ]

    async def event_stream():
        full_response = []

        async for token in ai_service.stream_response(claude_messages, system_prompt):
            full_response.append(token)
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # Assemble full response
        ai_text = "".join(full_response)

        # Strip chips annotation before storing
        clean_text = ai_service.strip_chips_line(ai_text)
        await discovery_service.add_message(db, session, "assistant", clean_text)

        # Extract and update design sheet
        sheet, changed = await discovery_service.update_sheet_from_conversation(db, session)

        await db.commit()

        # Send completion event
        chips = await ai_service.generate_quick_chips(ai_text)
        yield f"data: {json.dumps({'type': 'done', 'stage': session.stage, 'chips': chips})}\n\n"

        # Send sheet update if changed
        if changed and sheet:
            sheet_data = {
                "problem": sheet.problem,
                "audience": sheet.audience,
                "mvp": sheet.mvp,
                "features": sheet.features,
                "tone": sheet.tone,
                "platform": sheet.platform,
                "tech_constraints": sheet.tech_constraints,
                "success_metric": sheet.success_metric,
                "confidence_score": sheet.confidence_score,
            }
            yield f"data: {json.dumps({'type': 'sheet_update', 'sheet': sheet_data})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{session_id}", response_model=SessionRead)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a discovery session by ID."""
    session = await discovery_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Verify project ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == session.project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return session


@router.get("/{session_id}/sheet", response_model=DesignSheetRead)
async def get_sheet(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current design sheet state for a session."""
    session = await discovery_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Verify project ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == session.project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    sheet = await discovery_service.get_sheet_for_project(db, session.project_id)
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design sheet not found")
    return sheet
