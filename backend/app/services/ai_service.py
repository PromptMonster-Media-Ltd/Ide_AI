"""
ai_service.py — Claude API wrapper and prompt builder.
All AI calls go through this service for centralized prompt management.
"""
from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, AsyncGenerator

import anthropic

from app.core.config import settings

if TYPE_CHECKING:
    from app.pathways.base import PathwayConfig

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_KEY)



def _get_pathway(pathway: PathwayConfig | None = None) -> PathwayConfig:
    """Resolve a pathway, falling back to software_product."""
    if pathway is not None:
        return pathway
    from app.pathways import PathwayRegistry
    return PathwayRegistry.get("software_product")


# ---------------------------------------------------------------------------
# Software-product-specific platform prerequisites (used when pathway has
# platform-based context injection).  Kept here because it's consumed by
# build_system_prompt for the software pathway.
# ---------------------------------------------------------------------------
PLATFORM_PREREQUISITES: dict[str, dict] = {
    "mobile": {
        "summary": "Mobile app (iOS / Android)",
        "languages": "Swift or Kotlin (native), Dart (Flutter), JavaScript/TypeScript (React Native / Expo)",
        "sdks": "Xcode + iOS SDK, Android Studio + Android SDK, Flutter SDK, Expo / React Native CLI",
        "build": "Requires compilation. iOS requires macOS + Xcode. Android uses Gradle.",
        "distribution": "Apple App Store / Google Play Store. Needs signing certificates and store accounts.",
        "notes": "Cross-platform (Flutter, RN) reduces effort but may limit native API access. Push notifications require platform-specific setup (APNs, FCM).",
    },
    "web": {
        "summary": "Full-stack web application",
        "languages": "JavaScript/TypeScript (frontend), Python / Node.js / Go (backend)",
        "sdks": "React / Vue / Svelte (frontend), Express / FastAPI / Next.js (full-stack)",
        "build": "Frontend bundled with Vite or Webpack. Backend runs as server process. No compilation for interpreted stacks.",
        "distribution": "Deploy to Vercel, Railway, AWS, etc. Accessible via browser — no install.",
        "notes": "Lowest friction to ship. Consider SSR/SSG for SEO. PWA for offline.",
    },
    "desktop": {
        "summary": "Native desktop application (Windows / Mac / Linux)",
        "languages": "C++ or C# (native), JavaScript/TypeScript (Electron), Rust + JS (Tauri), Swift (macOS)",
        "sdks": "Electron, Tauri, .NET MAUI, Qt (C++), SwiftUI (macOS only)",
        "build": "REQUIRES COMPILATION for native builds. Electron/Tauri bundle web tech into desktop binaries.",
        "distribution": "Direct download, Microsoft Store, Mac App Store. Code signing required for trusted installs.",
        "notes": "Electron is quickest but heavy (~150 MB). Tauri is lighter (~5 MB) but uses Rust. Native C++/C# gives best performance but longest dev time.",
    },
    "browser-extension": {
        "summary": "Browser extension (Chrome / Firefox / Edge)",
        "languages": "JavaScript / TypeScript",
        "sdks": "Chrome Extensions API (Manifest V3), WebExtensions API (Firefox cross-compat)",
        "build": "Bundled with Webpack or Vite. No compilation. Manifest V3 required for Chrome.",
        "distribution": "Chrome Web Store, Firefox Add-ons, Edge Add-ons. Review process required.",
        "notes": "Limited to browser context. Service workers replace background pages in MV3. Content scripts run in page context.",
    },
    "vst/vsti-plug-in": {
        "summary": "Audio DSP plug-in loaded inside a DAW (Digital Audio Workstation)",
        "languages": "C++ (industry standard via JUCE framework), Rust (emerging via nih-plug), Python bridge (experimental — user has a custom toolchain in progress)",
        "sdks": "JUCE 8 (C++ — most widely used), iPlug2 (C++), nih-plug (Rust), DPF (DISTRHO Plugin Framework)",
        "build": "REQUIRES C++ COMPILATION via CMake or Projucer. Outputs VST3, AU, AAX, and CLAP binaries. Must be compiled per-platform (Win/Mac/Linux).",
        "distribution": "Direct download from developer website, or marketplaces (Plugin Boutique, KVR). No app store — users install to DAW plug-in folder.",
        "notes": "Strict real-time audio constraints: NO memory allocation, NO blocking calls in processBlock(). DSP knowledge required (filters, oscillators, FFT). Audio buffer sizes 64–2048 samples. Must support multiple sample rates (44.1k, 48k, 96k). UI is typically custom-drawn, not native OS widgets. The user is building a Python-to-VST bridge — keep this in mind for pipeline suggestions.",
    },
    "bubble": {
        "summary": "Bubble no-code web app",
        "languages": "No-code (visual programming in Bubble editor)",
        "sdks": "Bubble visual editor, Bubble API Connector for external integrations",
        "build": "No compilation. Apps built entirely in the visual editor.",
        "distribution": "Hosted on Bubble infrastructure. Custom domains available.",
        "notes": "Great for MVPs. Limited by Bubble's constraints for complex custom logic. Responsive design requires manual breakpoint configuration.",
    },
    "webflow": {
        "summary": "Webflow visual web design and CMS",
        "languages": "No-code (visual design). Optional custom code embeds (HTML/CSS/JS).",
        "sdks": "Webflow Designer, Webflow CMS, Webflow Logic (automation)",
        "build": "No compilation. Visual design published directly.",
        "distribution": "Hosted on Webflow or exported as static HTML.",
        "notes": "Best for marketing sites and content-driven apps. CMS is built-in. E-commerce available. Complex dynamic apps may outgrow Webflow.",
    },
    "flutterflow": {
        "summary": "FlutterFlow visual app builder (generates Flutter/Dart)",
        "languages": "Visual builder generates Dart / Flutter code. Custom functions in Dart.",
        "sdks": "FlutterFlow editor, Flutter SDK (for code export), Firebase (default backend)",
        "build": "Visual builder compiles to Flutter. Code can be exported and compiled locally.",
        "distribution": "Web deploy from FlutterFlow. App Store / Play Store via Flutter build.",
        "notes": "Generates real Flutter code that can be exported. Firebase deeply integrated. Supabase also supported.",
    },
    "bolt": {
        "summary": "Bolt AI-powered full-stack app builder",
        "languages": "JavaScript / TypeScript (generated by AI)",
        "sdks": "React (frontend), Node.js (backend) — AI picks stack based on prompt",
        "build": "AI generates and deploys code. No manual compilation needed.",
        "distribution": "Deployed directly from Bolt. Exportable source code.",
        "notes": "AI generates the full app from a prompt. Best for rapid prototyping. May need manual refinement for production.",
    },
    "lovable": {
        "summary": "Lovable AI app builder (formerly GPT Engineer)",
        "languages": "TypeScript / React (AI-generated)",
        "sdks": "React + Vite (frontend), Supabase (backend/database)",
        "build": "AI generates complete app. Supabase handles backend automatically.",
        "distribution": "Deployed to Lovable hosting or exported as source.",
        "notes": "AI-first development. Supabase deeply integrated for auth, database, storage. Good for MVPs and internal tools.",
    },
    "claude-code": {
        "summary": "Claude Code AI-assisted development",
        "languages": "Any — Claude Code supports all major languages",
        "sdks": "Whatever the project requires — Claude Code assists with any stack",
        "build": "Depends on chosen tech stack. Claude Code helps write and debug.",
        "distribution": "Depends on chosen deployment target.",
        "notes": "AI-assisted coding tool. The user writes code with Claude's help. No platform constraints — suggest the best stack for the user's needs.",
    },
    "cursor": {
        "summary": "Cursor AI-powered code editor",
        "languages": "Any — Cursor supports all major languages",
        "sdks": "Whatever the project requires — Cursor assists with any stack",
        "build": "Depends on chosen tech stack.",
        "distribution": "Depends on chosen deployment target.",
        "notes": "AI-assisted IDE. The user writes code with AI help. Recommend the best stack for their specific product needs.",
    },
    "replit": {
        "summary": "Replit cloud development and hosting",
        "languages": "Python, JavaScript/TypeScript, Go, Rust, and many more",
        "sdks": "Any — Replit supports most package managers (pip, npm, cargo, etc.)",
        "build": "Cloud-based. No local setup needed. Auto-builds on run.",
        "distribution": "Hosted on Replit. Custom domains available. Deployments included.",
        "notes": "Great for collaboration and fast prototyping. Cloud-only — no local dev environment needed. Database (PostgreSQL) and secrets management built-in.",
    },
    "n8n": {
        "summary": "n8n workflow automation platform",
        "languages": "JavaScript / TypeScript (for custom nodes). No-code for built-in nodes.",
        "sdks": "n8n SDK for custom node development",
        "build": "No compilation for standard workflows. Custom nodes require npm packaging.",
        "distribution": "Self-hosted (Docker) or n8n Cloud.",
        "notes": "Visual workflow builder for automation and integrations. 400+ built-in integrations. Custom nodes extend functionality. Webhook triggers available.",
    },
    "custom": {
        "summary": "Custom or unspecified platform",
        "languages": "Depends on the user's target",
        "sdks": "Depends on the user's target",
        "build": "Varies by platform.",
        "distribution": "Varies by platform.",
        "notes": "Ask the user to clarify their target platform so you can give specific guidance on language, SDK, build, and distribution requirements.",
    },
}


def _get_stage_prompt(pathway: PathwayConfig, stage: str) -> str:
    """Look up the system_prompt for a stage within the pathway's stages list."""
    for s in pathway.stages:
        if s.id == stage:
            return s.system_prompt
    # Fallback: first stage
    return pathway.stages[0].system_prompt if pathway.stages else ""


def _build_platform_block(platform: str) -> str | None:
    """Build platform-specific context block for software pathway."""
    prereqs = PLATFORM_PREREQUISITES.get(platform, PLATFORM_PREREQUISITES.get("custom", {}))
    if not prereqs:
        return f"\nThe user is targeting the {platform} platform. Keep recommendations relevant to this platform's capabilities and constraints."
    block = [f"\n## TARGET PLATFORM: {prereqs.get('summary', platform)}"]
    if prereqs.get("languages"):
        block.append(f"Languages: {prereqs['languages']}")
    if prereqs.get("sdks"):
        block.append(f"SDKs/Frameworks: {prereqs['sdks']}")
    if prereqs.get("build"):
        block.append(f"Build: {prereqs['build']}")
    if prereqs.get("distribution"):
        block.append(f"Distribution: {prereqs['distribution']}")
    if prereqs.get("notes"):
        block.append(f"Notes: {prereqs['notes']}")
    block.append("Keep ALL recommendations aligned with these platform requirements. If the user's idea conflicts with platform constraints, flag it proactively.")
    return "\n".join(block)


def strip_chips_line(text: str) -> str:
    """Remove the [CHIPS: ...] line from AI response text."""
    return re.sub(r'\n?\[CHIPS:.*?\]', '', text).strip()


async def build_system_prompt(
    platform: str,
    stage: str,
    sheet_context: dict | None = None,
    user_name: str | None = None,
    memories: str | None = None,
    *,
    pathway: PathwayConfig | None = None,
    ai_partner_style: str | None = None,
) -> str:
    """Build a 3-layer system prompt: base + partner fragment + session context.

    Layer 1 — Base discovery prompt:
        App role, safety, extraction, stage logic, formatting.
    Layer 2 — Partner style fragment:
        Behaviour, tone, questioning style, guardrails.
    Layer 3 — Session context:
        Platform, stage, known fields, user info, memories.

    Args:
        platform: Target platform string (e.g. 'bubble', 'custom').
        stage: Current discovery stage name.
        sheet_context: Partial design sheet dict for context injection.
        user_name: If provided, address the user by name in the greeting.
        memories: Formatted memory context block from memory_service.format_memory_context().
        pathway: PathwayConfig to use. Falls back to software_product if None.
        ai_partner_style: Partner collaboration style (e.g. 'skeptic', 'coach').
    """
    from app.services.partner_style_service import get_partner_style_fragment, DEFAULT_PARTNER_STYLE

    pw = _get_pathway(pathway)

    # ── Layer 1: Base discovery persona ──
    parts = [pw.base_persona]

    # ── Layer 2: Partner style fragment ──
    style = ai_partner_style or DEFAULT_PARTNER_STYLE
    partner_fragment = get_partner_style_fragment(style)
    parts.append(f"\n{partner_fragment}")

    # ── Layer 3: Session context ──
    if user_name:
        parts.append(f"\nThe user's name is {user_name}. Address them by name where natural — especially in greetings.")

    if memories:
        parts.append(f"\n{memories}")

    # Platform context injection (software pathway only — has PLATFORM_PREREQUISITES)
    if platform and pw.id == "software_product":
        platform_block = _build_platform_block(platform)
        if platform_block:
            parts.append(platform_block)

    stage_prompt = _get_stage_prompt(pw, stage)
    parts.append(f"\n{stage_prompt}")

    if sheet_context:
        filled = {k: v for k, v in sheet_context.items() if v}
        if filled:
            parts.append(f"\nDesign sheet so far: {json.dumps(filled, indent=2)}")

    parts.append("\nAfter your response, suggest 2-3 quick reply options the user might want to say next. Format them on the LAST line as: [CHIPS: option1 | option2 | option3]")
    parts.append("IMPORTANT: The [CHIPS: ...] line is parsed by the frontend and shown as clickable buttons. Do NOT include it in your main message body. Place it ONLY on the very last line.")

    return "\n".join(parts)


async def build_greeting_prompt(
    project_description: str | None = None,
    platform: str = "custom",
    *,
    pathway: PathwayConfig | None = None,
    ai_partner_style: str | None = None,
) -> str:
    """Build a system prompt specifically for the initial AI greeting."""
    from app.services.partner_style_service import get_partner_style_fragment, DEFAULT_PARTNER_STYLE

    pw = _get_pathway(pathway)
    parts = [pw.base_persona]

    # Partner style fragment
    style = ai_partner_style or DEFAULT_PARTNER_STYLE
    parts.append(f"\n{get_partner_style_fragment(style)}")

    # Platform context (software pathway only)
    if platform and pw.id == "software_product":
        prereqs = PLATFORM_PREREQUISITES.get(platform, PLATFORM_PREREQUISITES.get("custom", {}))
        if prereqs and prereqs.get("summary"):
            parts.append(f"\nTarget platform: {prereqs['summary']}. Languages: {prereqs.get('languages', 'TBD')}. Build: {prereqs.get('build', 'TBD')}.")
        elif platform != "custom":
            parts.append(f"\nThe user is targeting the {platform} platform.")

    greeting_prompt = _get_stage_prompt(pw, "greeting")
    parts.append(f"\n{greeting_prompt}")

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


async def extract_sheet_fields(
    messages: list,
    *,
    pathway: PathwayConfig | None = None,
) -> dict:
    """Extract design sheet fields from conversation using Claude.

    Uses the pathway's extraction_prompt to know which fields to look for.
    """
    pw = _get_pathway(pathway)
    extraction_messages = messages + [
        {"role": "user", "content": pw.extraction_prompt}
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
    """Parse quick reply chips from AI response. Returns list of chip strings.

    Searches from the END of the response (chips are always last), handles
    case-insensitive matching, and strips trailing punctuation/whitespace.
    """
    import re

    chips: list[str] = []
    # Search from the end — chips are always the last line
    for line in reversed(ai_response.split("\n")):
        stripped = line.strip()
        # Case-insensitive match; also handle trailing punctuation after ]
        match = re.match(r"\[(?:CHIPS|chips|Chips):\s*(.*?)\]\s*[.!]?\s*$", stripped)
        if match:
            inner = match.group(1)
            chips = [c.strip().strip('"').strip("'") for c in inner.split("|") if c.strip()]
            break
    return chips or ["Tell me more", "Let's move on", "I'm not sure yet"]
