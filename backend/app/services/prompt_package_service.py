"""
prompt_package_service.py — Generates platform-specific prompt packages.
Creates a series of AI-ready prompts tailored to the user's project and chosen build platform,
bundled as a downloadable ZIP with instructions.
"""
import io
import json
import re
import zipfile

import anthropic

from app.core.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_KEY)

SUPPORTED_PLATFORMS = {
    "cursor": "Cursor (VS Code AI)",
    "bolt": "Bolt.new",
    "lovable": "Lovable",
    "replit": "Replit Agent",
    "claude-code": "Claude Code (CLI)",
    "chatgpt": "ChatGPT / GPT-4",
    "generic": "Generic (platform-agnostic)",
}

PLATFORM_INSTRUCTIONS = {
    "cursor": (
        "These prompts are formatted for Cursor's Composer feature. "
        "Open Cursor, press Cmd+I (or Ctrl+I) to open Composer, and paste each prompt in order. "
        "Cursor works best when you give it full context about your project structure, "
        "so include file paths and be specific about where code should go."
    ),
    "bolt": (
        "These prompts are formatted for Bolt.new's interface. "
        "Go to bolt.new, start a new project, and paste each prompt into the chat. "
        "Bolt excels at generating full-stack apps from detailed descriptions. "
        "Paste prompts one at a time and let Bolt finish generating before moving to the next."
    ),
    "lovable": (
        "These prompts are formatted for Lovable's chat interface. "
        "Go to lovable.dev, create a new project, and paste each prompt sequentially. "
        "Lovable is great at building beautiful UIs from descriptions. "
        "Wait for each generation to complete before sending the next prompt."
    ),
    "replit": (
        "These prompts are formatted for Replit Agent. "
        "Open Replit, start a new project, and use the Agent feature to paste each prompt. "
        "Replit Agent can handle full project setup including dependencies and deployment. "
        "Let the agent complete each step before moving on."
    ),
    "claude-code": (
        "These prompts are formatted as CLI instructions for Claude Code. "
        "Open your terminal, navigate to your project directory, and use `claude` to start a session. "
        "Paste each prompt as a message. Claude Code can create files, run commands, and iterate. "
        "Review generated files after each prompt before proceeding."
    ),
    "chatgpt": (
        "These prompts are formatted for ChatGPT (GPT-4 or later). "
        "Open ChatGPT, start a new conversation, and paste each prompt in sequence. "
        "Copy the generated code into your project manually after each response. "
        "If a response is cut off, say 'continue' to get the rest."
    ),
    "generic": (
        "These prompts are platform-agnostic and can be used with any AI coding assistant. "
        "Paste each prompt in order into your preferred AI tool. "
        "Adapt the instructions to match your tool's interface and capabilities."
    ),
}

GENERATION_SYSTEM_PROMPT = """You are an expert software architect and prompt engineer. Your job is to generate a complete series of AI-ready prompts that will guide a user through building their application from scratch using an AI coding assistant.

You will be given:
1. A project design sheet with problem, audience, features, and technical decisions
2. A target AI platform (e.g., Cursor, Bolt.new, Lovable, Replit, Claude Code, ChatGPT, Generic)

Generate a JSON object with the following structure:
{
  "project_summary": "A 2-3 paragraph human-readable summary of the project",
  "prompts": [
    {
      "number": 1,
      "title": "Project Setup",
      "filename": "01_project_setup.md",
      "prompt": "The full prompt text the user should paste into their AI tool"
    },
    ...
  ]
}

RULES FOR PROMPT GENERATION:
1. Generate 10-15 prompts that progressively build the entire application
2. Each prompt should be self-contained but reference the overall project context
3. Prompts should be specific to the TARGET PLATFORM's interface and capabilities
4. Include specific file paths, component names, and technical details from the design sheet
5. Each prompt should be 200-500 words — detailed enough to produce quality output
6. The sequence should follow a logical build order:
   - Project initialization and setup
   - Data models / database schema
   - Core backend logic / API routes
   - Authentication (if applicable)
   - Main UI layout and navigation
   - Core feature pages/components (one prompt per major feature)
   - Styling and theme
   - Testing
   - Deployment preparation
   - Final polish and optimization
7. Reference the user's actual feature names, tech stack choices, and design decisions
8. For platform-specific prompts, use the platform's conventions (e.g., Cursor uses @file references, Bolt prefers full-stack descriptions, etc.)

PLATFORM-SPECIFIC FORMATTING:
- Cursor: Use @file references, be explicit about file paths, use Composer-style instructions
- Bolt.new: Describe the full desired output, mention framework preferences, describe UI in detail
- Lovable: Focus on UI/UX descriptions, be visual, describe layouts and interactions
- Replit: Include dependency setup, be explicit about project structure, mention deployment
- Claude Code: Use CLI-style instructions, reference terminal commands, mention file creation
- ChatGPT: Be very detailed since code must be copied manually, include file names clearly
- Generic: Use clear markdown structure, be tool-agnostic

Return ONLY valid JSON. No markdown code fences, no extra text."""


async def generate_prompt_package(project_data: dict, platform: str) -> dict:
    """Call Claude to generate a complete prompt package for the given platform.

    Args:
        project_data: Dictionary containing design_sheet, blocks, pipeline, market_analysis, project info.
        platform: One of the SUPPORTED_PLATFORMS keys.

    Returns:
        Parsed JSON dict with project_summary and prompts list.
    """
    platform_label = SUPPORTED_PLATFORMS.get(platform, "Generic")

    user_message = f"""Generate a complete prompt package for the following project.

TARGET PLATFORM: {platform_label}

PROJECT NAME: {project_data.get('project_name', 'Untitled Project')}
PROJECT DESCRIPTION: {project_data.get('project_description', 'No description provided')}

DESIGN SHEET:
- Problem: {project_data.get('problem', 'Not specified')}
- Target Audience: {project_data.get('audience', 'Not specified')}
- MVP Scope: {project_data.get('mvp', 'Not specified')}
- Platform: {project_data.get('platform', 'Not specified')}
- Tone: {project_data.get('tone', 'Not specified')}
- Tech Constraints: {project_data.get('tech_constraints', 'None')}
- Success Metric: {project_data.get('success_metric', 'Not specified')}

FEATURES:
{json.dumps(project_data.get('features', []), indent=2)}

FEATURE BLOCKS:
{json.dumps(project_data.get('blocks', []), indent=2)}

TECH STACK (Pipeline):
{json.dumps(project_data.get('pipeline', []), indent=2)}

MARKET ANALYSIS:
{json.dumps(project_data.get('market_analysis', {}), indent=2)}

Generate the complete prompt package as JSON."""

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=8192,
        system=GENERATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    text = response.content[0].text.strip()

    # Handle possible markdown code blocks wrapping the JSON
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        package = json.loads(text)
    except json.JSONDecodeError:
        # Attempt to extract JSON from the response with regex
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            package = json.loads(match.group())
        else:
            raise ValueError("Failed to parse prompt package from AI response")

    return package


def _build_instructions_md(platform: str, package_data: dict) -> str:
    """Build the INSTRUCTIONS.md file content."""
    platform_label = SUPPORTED_PLATFORMS.get(platform, "Generic")
    platform_guide = PLATFORM_INSTRUCTIONS.get(platform, PLATFORM_INSTRUCTIONS["generic"])
    prompts = package_data.get("prompts", [])

    lines = [
        f"# Prompt Package — {platform_label}",
        "",
        "## Overview",
        "",
        "This package contains a series of AI-ready prompts designed to walk you through "
        "building your application from scratch. Each prompt is tailored to your project's "
        "specific design decisions and optimized for your chosen platform.",
        "",
        f"## Platform: {platform_label}",
        "",
        platform_guide,
        "",
        "## How to Use",
        "",
        "1. Open your AI tool and start a new session/project.",
        "2. Begin with prompt `01` and work through each prompt in numerical order.",
        "3. Wait for each prompt to finish generating before moving to the next.",
        "4. Review the generated code after each step — make corrections if needed before proceeding.",
        "5. The `context/` folder contains your full design sheet and project summary for reference.",
        "",
        "## Prompt Sequence",
        "",
    ]

    for p in prompts:
        num = p.get("number", "?")
        title = p.get("title", "Untitled")
        lines.append(f"{num}. **{title}** — `prompts/{p.get('filename', f'{num:02d}.md')}`")

    lines.extend([
        "",
        "## Tips",
        "",
        "- If the AI tool asks for clarification, refer to the `context/project_summary.md` file.",
        "- You can modify any prompt before pasting it to better match your preferences.",
        "- If a prompt generates an error or unexpected result, re-paste it with additional context.",
        "- Save your progress frequently — commit to git after each successful prompt completion.",
        "",
        "## Context Files",
        "",
        "- `context/design_sheet.json` — The full structured design sheet from your Ide/AI project.",
        "- `context/project_summary.md` — A human-readable summary of your project for quick reference.",
        "",
        "---",
        "*Generated by Ide/AI*",
    ])

    return "\n".join(lines)


def _build_project_summary_md(project_data: dict, package_data: dict) -> str:
    """Build the context/project_summary.md file content."""
    summary_text = package_data.get("project_summary", "No summary available.")

    lines = [
        "# Project Summary",
        "",
        summary_text,
        "",
        "## Key Details",
        "",
        f"- **Problem:** {project_data.get('problem', 'Not specified')}",
        f"- **Audience:** {project_data.get('audience', 'Not specified')}",
        f"- **MVP:** {project_data.get('mvp', 'Not specified')}",
        f"- **Platform:** {project_data.get('platform', 'Not specified')}",
        f"- **Tone:** {project_data.get('tone', 'Not specified')}",
        f"- **Success Metric:** {project_data.get('success_metric', 'Not specified')}",
        "",
        "## Features",
        "",
    ]

    for feat in project_data.get("features", []):
        if isinstance(feat, dict):
            name = feat.get("name", "Unnamed")
            desc = feat.get("description", "")
            priority = feat.get("priority", "")
            lines.append(f"- **{name}** ({priority}) — {desc}")
        else:
            lines.append(f"- {feat}")

    lines.extend([
        "",
        "## Tech Stack",
        "",
    ])

    for p in project_data.get("pipeline", []):
        if isinstance(p, dict):
            lines.append(f"- **{p.get('layer', '?')}:** {p.get('tool', '?')}")

    lines.extend([
        "",
        "---",
        "*Generated by Ide/AI*",
    ])

    return "\n".join(lines)


def build_zip(package_data: dict, project_data: dict, platform: str) -> bytes:
    """Create an in-memory ZIP file from the generated prompt package.

    Args:
        package_data: The parsed JSON from Claude containing prompts and summary.
        project_data: The full project context dict.
        platform: The target platform key.

    Returns:
        ZIP file contents as bytes.
    """
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # INSTRUCTIONS.md
        instructions = _build_instructions_md(platform, package_data)
        zf.writestr("INSTRUCTIONS.md", instructions)

        # Individual prompt files
        for prompt in package_data.get("prompts", []):
            filename = prompt.get("filename", f"{prompt.get('number', 0):02d}_prompt.md")
            title = prompt.get("title", "Prompt")
            content = prompt.get("prompt", "")

            prompt_md = f"# {title}\n\n{content}\n"
            zf.writestr(f"prompts/{filename}", prompt_md)

        # context/design_sheet.json
        design_sheet_json = {
            "problem": project_data.get("problem"),
            "audience": project_data.get("audience"),
            "mvp": project_data.get("mvp"),
            "features": project_data.get("features"),
            "tone": project_data.get("tone"),
            "platform": project_data.get("platform"),
            "tech_constraints": project_data.get("tech_constraints"),
            "success_metric": project_data.get("success_metric"),
            "blocks": project_data.get("blocks"),
            "pipeline": project_data.get("pipeline"),
        }
        zf.writestr(
            "context/design_sheet.json",
            json.dumps(design_sheet_json, indent=2, default=str),
        )

        # context/project_summary.md
        summary_md = _build_project_summary_md(project_data, package_data)
        zf.writestr("context/project_summary.md", summary_md)

    return buf.getvalue()
