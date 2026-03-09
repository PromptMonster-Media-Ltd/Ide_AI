"""
sprint_service.py — AI-powered sprint planning using project blocks and pipeline.
Uses Claude to generate milestones, sprints, and Gantt timeline data.
Streams results section-by-section via SSE events.
"""
import csv
import io
import json
import uuid
from typing import Any, AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.block import Block
from app.models.pipeline_node import PipelineNode
from app.models.project import Project
from app.models.sprint_plan import SprintPlan
from app.services.ai_service import client


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SPRINT_SYSTEM = """You are a senior engineering manager and sprint planning expert. You create realistic, well-structured project roadmaps that engineering teams can actually follow. You understand software architecture dependencies, effort estimation, and iterative delivery.

IMPORTANT RULES:
- Return ONLY valid JSON — no markdown, no commentary, no code fences
- Be realistic about timelines — MVP features first, V2 features in later sprints
- Consider technical dependencies (e.g., auth before user features, database before API)
- Use 2-week sprint cadence
- Effort sizes: S = 1-2 days, M = 3-5 days, L = 1-2 weeks
- Priorities: mvp = must-ship, v2 = nice-to-have, stretch = future consideration"""


# ---------------------------------------------------------------------------
# Generation prompts for each section
# ---------------------------------------------------------------------------

MILESTONES_PROMPT = """Analyze the project blocks (features) and tech pipeline below. Generate 3-5 logical milestones that group related work.

Blocks (features):
{blocks_json}

Tech Pipeline:
{pipeline_json}

Project: {project_name}
Description: {project_description}

Return a JSON array of milestones:
[
  {{
    "id": "m1",
    "name": "Foundation",
    "description": "Core setup and infrastructure",
    "target_date": "Week 2",
    "block_ids": ["block-uuid-1", "block-uuid-2"],
    "status": "not_started"
  }}
]

Guidelines:
- First milestone should be "Foundation" — project setup, auth, database, core infrastructure
- Group related blocks logically (e.g., user features together, payment features together)
- MVP blocks should be in earlier milestones, V2 blocks in later ones
- Each milestone should have a clear deliverable
- Include block IDs from the blocks list above"""

SPRINTS_PROMPT = """Using the milestones and blocks below, break the work into 2-week sprints.

Milestones:
{milestones_json}

Blocks (features):
{blocks_json}

Tech Pipeline:
{pipeline_json}

Return a JSON array of sprints:
[
  {{
    "id": "s1",
    "name": "Sprint 1",
    "milestone_id": "m1",
    "duration_weeks": 2,
    "start_week": 1,
    "tasks": [
      {{
        "id": "t1",
        "block_id": "block-uuid",
        "block_name": "User Auth",
        "description": "Implement JWT auth with login/register",
        "effort": "M",
        "priority": "mvp",
        "status": "not_started"
      }}
    ]
  }}
]

Guidelines:
- Each sprint should be achievable in 2 weeks
- Don't overload sprints — consider effort sizes (S + S + M is reasonable for one sprint)
- Respect dependencies: infrastructure before features, auth before user-specific features
- MVP tasks in early sprints, V2 tasks in later sprints
- Task descriptions should be actionable and specific
- A single block might produce multiple tasks if it's large"""

TIMELINE_PROMPT = """Using the sprints below, generate a Gantt-chart-ready timeline dataset.

Sprints:
{sprints_json}

Return a JSON array of timeline items:
[
  {{
    "id": "t1",
    "name": "User Auth",
    "sprint": "Sprint 1",
    "start_week": 1,
    "end_week": 2,
    "effort": "M",
    "priority": "mvp",
    "dependencies": []
  }}
]

Guidelines:
- Each task from the sprints should appear as a timeline item
- start_week and end_week should reflect the sprint timing and effort size
- S tasks: 1 week span, M tasks: 1-2 week span, L tasks: 2 week span
- Add logical dependencies (e.g., "Database Setup" before "User Auth", "Auth" before "User Profile")
- Dependencies reference other timeline item IDs"""


# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------

SECTIONS = [
    ("milestones", MILESTONES_PROMPT),
    ("sprints", SPRINTS_PROMPT),
    ("timeline", TIMELINE_PROMPT),
]

SECTION_LABELS = {
    "milestones": "Milestones & Grouping",
    "sprints": "Sprint Breakdown",
    "timeline": "Timeline & Dependencies",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_blocks_context(blocks: list[Block]) -> list[dict]:
    """Serialize blocks for the AI prompt."""
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "description": b.description or "",
            "category": b.category,
            "priority": b.priority,
            "effort": b.effort,
            "is_mvp": b.is_mvp,
        }
        for b in blocks
    ]


def _build_pipeline_context(nodes: list[PipelineNode]) -> list[dict]:
    """Serialize pipeline nodes for the AI prompt."""
    return [
        {
            "layer": n.layer,
            "selected_tool": n.selected_tool,
            "config": n.config,
        }
        for n in nodes
    ]


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def get_sprint_plan(db: AsyncSession, project_id: uuid.UUID) -> SprintPlan | None:
    """Fetch the sprint plan for a project."""
    result = await db.execute(
        select(SprintPlan).where(SprintPlan.project_id == project_id)
    )
    return result.scalar_one_or_none()


async def update_sprint_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
    updates: dict[str, Any],
) -> SprintPlan | None:
    """Apply manual edits to a sprint plan (task status, sprint assignments, etc.)."""
    result = await db.execute(
        select(SprintPlan).where(SprintPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return None

    for field in ("milestones", "sprints", "timeline", "status"):
        if field in updates:
            setattr(plan, field, updates[field])

    await db.flush()
    return plan


async def delete_sprint_plan(db: AsyncSession, project_id: uuid.UUID) -> bool:
    """Delete the sprint plan for a project."""
    plan = await get_sprint_plan(db, project_id)
    if not plan:
        return False
    await db.delete(plan)
    await db.flush()
    return True


def export_as_csv(plan: SprintPlan, project_name: str) -> str:
    """Export sprint plan as Linear-compatible CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Description", "Priority", "Estimate", "Status", "Sprint", "Milestone"])

    sprints = plan.sprints or []
    milestones = plan.milestones or []

    # Build milestone lookup
    milestone_map = {m["id"]: m["name"] for m in milestones}

    for sprint in sprints:
        sprint_name = sprint.get("name", "")
        milestone_name = milestone_map.get(sprint.get("milestone_id", ""), "")
        for task in sprint.get("tasks", []):
            effort_map = {"S": "Small", "M": "Medium", "L": "Large"}
            priority_map = {"mvp": "Urgent", "v2": "Medium", "stretch": "Low"}
            status_map = {"not_started": "Todo", "in_progress": "In Progress", "done": "Done"}

            writer.writerow([
                task.get("block_name", task.get("description", "")),
                task.get("description", ""),
                priority_map.get(task.get("priority", "mvp"), "Medium"),
                effort_map.get(task.get("effort", "M"), "Medium"),
                status_map.get(task.get("status", "not_started"), "Todo"),
                sprint_name,
                milestone_name,
            ])

    return output.getvalue()


async def generate_sprint_plan(
    db: AsyncSession,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    force_regenerate: bool = False,
) -> AsyncGenerator[str, None]:
    """Generate a full sprint plan, streaming progress via SSE events.

    Yields SSE-formatted strings: ``data: {json}\\n\\n``

    Event types:
    - plan_start: {type, message}
    - plan_progress: {type, section, label, progress}
    - section_complete: {type, section, data, progress}
    - plan_complete: {type, progress}
    - error: {type, message}
    """
    # Fetch project
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_result.scalar_one_or_none()
    if not project:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Project not found'})}\n\n"
        return

    # Fetch blocks
    blocks_result = await db.execute(
        select(Block).where(Block.project_id == project_id).order_by(Block.order)
    )
    blocks = list(blocks_result.scalars().all())
    if not blocks:
        yield f"data: {json.dumps({'type': 'error', 'message': 'No blocks found. Add feature blocks first.'})}\n\n"
        return

    # Fetch pipeline nodes
    pipeline_result = await db.execute(
        select(PipelineNode).where(PipelineNode.project_id == project_id)
    )
    pipeline_nodes = list(pipeline_result.scalars().all())

    # Get or create plan record
    plan = await get_sprint_plan(db, project_id)
    if plan and not force_regenerate:
        if plan.status == "complete":
            yield f"data: {json.dumps({'type': 'error', 'message': 'Sprint plan already exists. Use force_regenerate=true to regenerate.'})}\n\n"
            return

    if not plan:
        plan = SprintPlan(
            project_id=project_id,
            user_id=user_id,
            status="generating",
        )
        db.add(plan)
        await db.flush()
    else:
        # Reset for regeneration
        plan.status = "generating"
        plan.error_message = None
        plan.milestones = None
        plan.sprints = None
        plan.timeline = None
        await db.flush()

    # Build context
    blocks_json = json.dumps(_build_blocks_context(blocks), indent=2)
    pipeline_json = json.dumps(_build_pipeline_context(pipeline_nodes), indent=2)

    yield f"data: {json.dumps({'type': 'plan_start', 'message': 'Analyzing project blocks and pipeline...'})}\n\n"

    # Generate each section sequentially
    total_sections = len(SECTIONS)
    generated_data: dict[str, Any] = {}

    for idx, (section_key, prompt_template) in enumerate(SECTIONS):
        label = SECTION_LABELS[section_key]
        yield f"data: {json.dumps({'type': 'plan_progress', 'section': section_key, 'label': label, 'progress': idx / total_sections})}\n\n"

        try:
            # Build the prompt with context
            format_kwargs: dict[str, str] = {
                "blocks_json": blocks_json,
                "pipeline_json": pipeline_json,
                "project_name": project.name,
                "project_description": project.description or "",
            }

            # For sprints prompt, inject milestones
            if section_key == "sprints" and "milestones" in generated_data:
                format_kwargs["milestones_json"] = json.dumps(generated_data["milestones"], indent=2)

            # For timeline prompt, inject sprints
            if section_key == "timeline" and "sprints" in generated_data:
                format_kwargs["sprints_json"] = json.dumps(generated_data["sprints"], indent=2)

            prompt = prompt_template.format(**format_kwargs)

            # Stream tokens for this section
            full_text: list[str] = []

            async with client.messages.stream(
                model=settings.CLAUDE_MODEL,
                max_tokens=4096,
                system=SPRINT_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for token in stream.text_stream:
                    full_text.append(token)

            # Parse the completed section
            text = "".join(full_text).strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            section_data = json.loads(text)

            # Claude sometimes wraps the array in an object:
            #   {"milestones": [...]} instead of [...]
            # Unwrap so we always store a plain list.
            if isinstance(section_data, dict):
                if section_key in section_data and isinstance(section_data[section_key], list):
                    section_data = section_data[section_key]
                elif len(section_data) == 1:
                    only_val = next(iter(section_data.values()))
                    if isinstance(only_val, list):
                        section_data = only_val

            generated_data[section_key] = section_data

            # Store in database
            setattr(plan, section_key, section_data)
            await db.flush()

            yield f"data: {json.dumps({'type': 'section_complete', 'section': section_key, 'data': section_data, 'progress': (idx + 1) / total_sections})}\n\n"

        except json.JSONDecodeError as e:
            # If JSON parsing fails, store fallback
            fallback = {"raw": "".join(full_text).strip(), "parse_error": str(e)}
            setattr(plan, section_key, fallback)
            generated_data[section_key] = fallback
            await db.flush()
            yield f"data: {json.dumps({'type': 'section_complete', 'section': section_key, 'data': fallback, 'progress': (idx + 1) / total_sections})}\n\n"

        except Exception as e:
            plan.status = "error"
            plan.error_message = f"Failed generating {label}: {str(e)}"
            await db.flush()
            await db.commit()
            yield f"data: {json.dumps({'type': 'error', 'message': plan.error_message})}\n\n"
            return

    # Mark complete
    plan.status = "complete"
    await db.flush()
    await db.commit()

    # Include the assembled plan data so the frontend can render immediately
    plan_payload = {
        "id": str(plan.id),
        "project_id": str(plan.project_id),
        "milestones": plan.milestones,
        "sprints": plan.sprints,
        "timeline": plan.timeline,
        "status": plan.status,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
    }

    yield f"data: {json.dumps({'type': 'plan_complete', 'progress': 1.0, 'plan': plan_payload})}\n\n"
