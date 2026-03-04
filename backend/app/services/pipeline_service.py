"""
pipeline_service.py — Tech stack recommendation engine.
Provides curated tool options, cost estimation, and compatibility checking.
"""
import json
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.design_sheet import DesignSheet
from app.models.pipeline_node import PipelineNode
from app.services.ai_service import client

LAYER_OPTIONS = {
    "frontend": {
        "tools": ["Bubble", "Webflow", "FlutterFlow", "React", "Next.js", "Bolt", "Lovable", "Replit"],
        "costs": {"Bubble": (29, 119), "Webflow": (14, 39), "FlutterFlow": (30, 70), "React": (0, 0), "Next.js": (0, 20), "Bolt": (10, 30), "Lovable": (10, 30), "Replit": (7, 20)},
    },
    "backend": {
        "tools": ["Bubble Backend", "Xano", "Supabase", "Firebase", "FastAPI", "Node.js", "n8n"],
        "costs": {"Bubble Backend": (0, 0), "Xano": (0, 85), "Supabase": (0, 25), "Firebase": (0, 25), "FastAPI": (0, 0), "Node.js": (0, 0), "n8n": (0, 20)},
    },
    "database": {
        "tools": ["Bubble DB", "Supabase Postgres", "Firebase Firestore", "PlanetScale", "MongoDB Atlas", "Xano DB"],
        "costs": {"Bubble DB": (0, 0), "Supabase Postgres": (0, 25), "Firebase Firestore": (0, 25), "PlanetScale": (0, 29), "MongoDB Atlas": (0, 57), "Xano DB": (0, 0)},
    },
    "automations": {
        "tools": ["n8n", "Make (Integromat)", "Zapier", "Bubble Workflows", "Custom Code"],
        "costs": {"n8n": (0, 20), "Make (Integromat)": (9, 29), "Zapier": (20, 49), "Bubble Workflows": (0, 0), "Custom Code": (0, 0)},
    },
    "ai_agents": {
        "tools": ["Claude API", "OpenAI API", "Langchain", "None"],
        "costs": {"Claude API": (5, 50), "OpenAI API": (5, 50), "Langchain": (0, 0), "None": (0, 0)},
    },
    "analytics": {
        "tools": ["Mixpanel", "PostHog", "Google Analytics", "Amplitude", "None"],
        "costs": {"Mixpanel": (0, 25), "PostHog": (0, 0), "Google Analytics": (0, 0), "Amplitude": (0, 25), "None": (0, 0)},
    },
    "deployment": {
        "tools": ["Vercel", "Netlify", "Railway", "Fly.io", "AWS", "Bubble Hosting", "Replit Hosting"],
        "costs": {"Vercel": (0, 20), "Netlify": (0, 19), "Railway": (5, 20), "Fly.io": (0, 15), "AWS": (5, 100), "Bubble Hosting": (0, 0), "Replit Hosting": (0, 0)},
    },
}

RECOMMENDATION_PROMPT = """Based on this product design, recommend the best tech stack.

Design Sheet:
- Problem: {problem}
- Audience: {audience}
- Platform preference: {platform}
- Complexity: {complexity}
- Features: {features}

Available layers and tools:
{layer_options}

For each layer, pick the best tool and explain why in 1 sentence.
Return as JSON array: [{{"layer": "...", "selected_tool": "...", "reason": "..."}}]
Only return valid JSON, no markdown."""


async def recommend_pipeline(
    db: AsyncSession, sheet: DesignSheet, project_id: uuid.UUID, complexity: str = "medium"
) -> tuple[list[PipelineNode], list[str], dict]:
    """Recommend a tech pipeline based on design sheet analysis.
    Returns (nodes, reasoning_bullets, cost_estimate)."""
    features_str = json.dumps(sheet.features or [])
    layer_str = "\n".join(
        f"- {layer}: {', '.join(info['tools'])}"
        for layer, info in LAYER_OPTIONS.items()
    )

    prompt = RECOMMENDATION_PROMPT.format(
        problem=sheet.problem or "Not specified",
        audience=sheet.audience or "Not specified",
        platform=sheet.platform or "Not specified",
        complexity=complexity,
        features=features_str,
        layer_options=layer_str,
    )

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=2048,
        system="You are a tech stack advisor. Return only valid JSON arrays.",
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        recommendations = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        recommendations = [
            {"layer": layer, "selected_tool": info["tools"][0], "reason": "Default recommendation"}
            for layer, info in LAYER_OPTIONS.items()
        ]

    # Delete existing nodes
    await db.execute(delete(PipelineNode).where(PipelineNode.project_id == project_id))

    # Create nodes
    nodes = []
    reasoning = []
    for rec in recommendations:
        layer = rec.get("layer", "")
        tool = rec.get("selected_tool", "")
        reason = rec.get("reason", "")

        if layer in LAYER_OPTIONS:
            node = PipelineNode(
                project_id=project_id,
                layer=layer,
                selected_tool=tool,
                config={"reason": reason},
            )
            db.add(node)
            nodes.append(node)
            reasoning.append(f"{layer}: {tool} — {reason}")

    await db.flush()

    cost_est = estimate_cost_from_nodes(nodes)
    return nodes, reasoning, cost_est


def estimate_cost(pipeline_nodes: list[PipelineNode]) -> dict:
    """Estimate monthly cost range for a pipeline configuration."""
    return estimate_cost_from_nodes(pipeline_nodes)


def estimate_cost_from_nodes(nodes: list[PipelineNode]) -> dict:
    """Calculate cost estimates from pipeline nodes."""
    total_min = 0
    total_max = 0
    breakdown = []

    for node in nodes:
        layer_info = LAYER_OPTIONS.get(node.layer, {})
        costs = layer_info.get("costs", {})
        tool_cost = costs.get(node.selected_tool, (0, 50))
        total_min += tool_cost[0]
        total_max += tool_cost[1]
        breakdown.append({
            "layer": node.layer,
            "tool": node.selected_tool,
            "min": tool_cost[0],
            "max": tool_cost[1],
        })

    return {
        "monthly_min": total_min,
        "monthly_max": total_max,
        "breakdown": breakdown,
    }


def check_compatibility(nodes: list[PipelineNode]) -> list[str]:
    """Check compatibility between selected pipeline tools."""
    warnings = []
    tools = {n.layer: n.selected_tool for n in nodes}

    # Check known incompatibilities
    if tools.get("frontend") == "Bubble" and tools.get("backend") not in ("Bubble Backend", None):
        warnings.append("Bubble works best with its built-in backend. External backend adds complexity.")

    if tools.get("database") == "Firebase Firestore" and tools.get("backend") == "FastAPI":
        warnings.append("Firebase Firestore has limited Python support. Consider Supabase Postgres instead.")

    return warnings
