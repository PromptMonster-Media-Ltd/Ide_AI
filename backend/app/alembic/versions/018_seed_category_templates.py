"""Seed additional category templates (business, creative, education, marketing, personal).

Revision ID: 018
Revises: 017
Create Date: 2026-03-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Re-categorise the existing 10 templates from migration 017 as "software"
# Then add 10 templates for each of the 5 new categories.

RECATEGORISE = [
    ("SaaS MVP", "software"),
    ("Mobile App", "software"),
    ("E-Commerce Store", "software"),
    ("Content Platform", "software"),
    ("AI-Powered Tool", "software"),
    ("Community Platform", "software"),
    ("Creative Portfolio", "software"),
    ("API / Developer Tool", "software"),
    ("Marketplace", "software"),
    ("Blank Canvas", "software"),
]

TEMPLATES = [
    # ── Business ──
    ("Startup Pitch Deck", "Craft a compelling pitch deck with problem/solution, market size, traction, and financials.", "📊", "business", '{"deliverable":"pitch_deck","audience":"investors"}'),
    ("Business Plan", "Develop a comprehensive business plan with executive summary, market analysis, and projections.", "📋", "business", '{"deliverable":"business_plan","audience":"stakeholders"}'),
    ("Lean Canvas", "Map your business model on a single page — problem, solution, channels, revenue streams.", "🎯", "business", '{"deliverable":"lean_canvas","audience":"founders"}'),
    ("Competitive Analysis", "Research and document competitor landscape, positioning, strengths, and gaps.", "🔍", "business", '{"deliverable":"competitive_report","audience":"strategy_team"}'),
    ("Product Roadmap", "Plan quarterly milestones, feature priorities, and resource allocation.", "🗺️", "business", '{"deliverable":"roadmap","audience":"product_team"}'),
    ("Financial Model", "Build revenue forecasts, unit economics, and scenario planning spreadsheets.", "💰", "business", '{"deliverable":"financial_model","audience":"cfo_investors"}'),
    ("Partnership Proposal", "Design a co-marketing or integration partnership pitch with mutual value props.", "🤝", "business", '{"deliverable":"partnership_deck","audience":"potential_partners"}'),
    ("Customer Persona", "Define ideal customer profiles with demographics, pain points, and buying behavior.", "👤", "business", '{"deliverable":"persona_docs","audience":"marketing_sales"}'),
    ("OKR Framework", "Set quarterly objectives and key results aligned to company strategy.", "🎯", "business", '{"deliverable":"okr_template","audience":"leadership"}'),
    ("Investor Update", "Monthly/quarterly investor newsletter with KPIs, wins, asks, and runway.", "📈", "business", '{"deliverable":"investor_update","audience":"investors"}'),

    # ── Creative ──
    ("Brand Identity Kit", "Design a complete brand system — logo concepts, color palette, typography, and guidelines.", "🎨", "creative", '{"deliverable":"brand_kit","medium":"visual_design"}'),
    ("YouTube Channel", "Plan a YouTube content strategy with niche, format, thumbnails, and upload schedule.", "📺", "creative", '{"deliverable":"channel_plan","medium":"video"}'),
    ("Podcast Launch", "Design your podcast from concept to launch — format, episodes, artwork, and distribution.", "🎙️", "creative", '{"deliverable":"podcast_plan","medium":"audio"}'),
    ("Short Film", "Develop a short film concept with script outline, shot list, and production schedule.", "🎬", "creative", '{"deliverable":"film_concept","medium":"video"}'),
    ("Photography Project", "Plan a themed photo series with mood board, shot list, and editing style guide.", "📸", "creative", '{"deliverable":"photo_brief","medium":"photography"}'),
    ("Music Album", "Structure an album release with track listing, artwork direction, and rollout timeline.", "🎵", "creative", '{"deliverable":"album_plan","medium":"audio"}'),
    ("Newsletter / Zine", "Design a recurring publication with editorial calendar, layout, and subscriber strategy.", "📰", "creative", '{"deliverable":"publication_plan","medium":"editorial"}'),
    ("Game Concept", "Outline a game design document with mechanics, narrative, art direction, and MVP scope.", "🎮", "creative", '{"deliverable":"game_design_doc","medium":"interactive"}'),
    ("UI/UX Redesign", "Audit and redesign an existing product with wireframes, user flows, and design system.", "✏️", "creative", '{"deliverable":"design_spec","medium":"digital_design"}'),
    ("Animation Project", "Plan a motion graphics or animation piece — storyboard, style frames, and timeline.", "🎞️", "creative", '{"deliverable":"animation_brief","medium":"motion"}'),

    # ── Education ──
    ("Online Course", "Structure an online course with modules, lessons, quizzes, and completion certificates.", "🎓", "education", '{"deliverable":"course_outline","format":"self_paced"}'),
    ("Workshop Series", "Design a multi-session workshop with activities, handouts, and facilitator guides.", "🏫", "education", '{"deliverable":"workshop_plan","format":"live_sessions"}'),
    ("Study Guide", "Create a comprehensive study resource with summaries, flashcards, and practice problems.", "📚", "education", '{"deliverable":"study_guide","format":"reference"}'),
    ("Coding Bootcamp", "Plan a coding bootcamp curriculum with projects, assessments, and career prep.", "💻", "education", '{"deliverable":"bootcamp_curriculum","format":"cohort"}'),
    ("Research Paper", "Outline and structure a research paper with literature review, methodology, and analysis.", "🔬", "education", '{"deliverable":"research_outline","format":"academic"}'),
    ("Training Program", "Build an employee training program with onboarding modules and skill assessments.", "🏋️", "education", '{"deliverable":"training_plan","format":"corporate"}'),
    ("Tutorial Series", "Plan a step-by-step tutorial series with progressive difficulty and code examples.", "📝", "education", '{"deliverable":"tutorial_outline","format":"blog_video"}'),
    ("Language Course", "Structure a language learning program with vocabulary, grammar, and conversation practice.", "🌍", "education", '{"deliverable":"language_curriculum","format":"self_paced"}'),
    ("Certification Prep", "Create a certification exam prep kit with practice tests, study schedule, and key topics.", "🏆", "education", '{"deliverable":"cert_prep_kit","format":"self_study"}'),
    ("Kids Learning App", "Design an educational app for children with gamified lessons and parental controls.", "🧒", "education", '{"deliverable":"app_concept","format":"interactive"}'),

    # ── Marketing ──
    ("Product Launch Campaign", "Plan a full product launch with teaser, launch day, and post-launch engagement.", "🚀", "marketing", '{"deliverable":"launch_plan","channel":"multi_channel"}'),
    ("Social Media Strategy", "Build a social media calendar with content pillars, posting schedule, and KPIs.", "📱", "marketing", '{"deliverable":"social_strategy","channel":"social"}'),
    ("Email Drip Campaign", "Design an automated email sequence for onboarding, nurturing, or re-engagement.", "📧", "marketing", '{"deliverable":"email_sequence","channel":"email"}'),
    ("SEO Content Plan", "Create a keyword-driven content calendar with topic clusters and link strategy.", "🔎", "marketing", '{"deliverable":"seo_plan","channel":"organic_search"}'),
    ("Landing Page", "Design a high-converting landing page with copy, layout, and A/B test variants.", "🖥️", "marketing", '{"deliverable":"landing_page","channel":"web"}'),
    ("Brand Story", "Craft your brand narrative — origin, mission, values, and voice guidelines.", "📖", "marketing", '{"deliverable":"brand_story","channel":"all"}'),
    ("Influencer Campaign", "Plan an influencer partnership strategy with outreach, briefs, and tracking.", "⭐", "marketing", '{"deliverable":"influencer_plan","channel":"social"}'),
    ("Event Marketing", "Organize a virtual or in-person event with promotion, logistics, and follow-up.", "🎪", "marketing", '{"deliverable":"event_plan","channel":"events"}'),
    ("Referral Program", "Design a referral/affiliate program with incentives, tracking, and growth loops.", "🔗", "marketing", '{"deliverable":"referral_program","channel":"word_of_mouth"}'),
    ("PR / Press Kit", "Create a press kit with company overview, founder bios, media assets, and pitch angles.", "📰", "marketing", '{"deliverable":"press_kit","channel":"media"}'),

    # ── Personal ──
    ("Side Project", "Plan a personal passion project with goals, milestones, and a realistic timeline.", "🛠️", "personal", '{"deliverable":"project_plan","scope":"personal"}'),
    ("Habit Tracker", "Design a habit-building system with daily tracking, streaks, and accountability.", "✅", "personal", '{"deliverable":"habit_system","scope":"self_improvement"}'),
    ("Travel Planner", "Plan a trip with itinerary, budget, packing list, and booking checklist.", "✈️", "personal", '{"deliverable":"travel_plan","scope":"travel"}'),
    ("Fitness Program", "Structure a workout and nutrition plan with progressive overload and meal prep.", "💪", "personal", '{"deliverable":"fitness_plan","scope":"health"}'),
    ("Book / Writing Project", "Outline a book or writing project with chapters, research, and writing schedule.", "✍️", "personal", '{"deliverable":"book_outline","scope":"creative"}'),
    ("Personal Finance", "Build a budgeting and savings plan with expense tracking and investment goals.", "🏦", "personal", '{"deliverable":"finance_plan","scope":"financial"}'),
    ("Career Transition", "Plan a career change with skills gap analysis, learning path, and networking strategy.", "🔄", "personal", '{"deliverable":"career_plan","scope":"professional"}'),
    ("Home Renovation", "Plan a renovation project with budget, timeline, materials, and contractor coordination.", "🏠", "personal", '{"deliverable":"renovation_plan","scope":"home"}'),
    ("Wedding Planner", "Organize a wedding with venue, vendors, budget, timeline, and guest management.", "💍", "personal", '{"deliverable":"wedding_plan","scope":"event"}'),
    ("Life Goals Roadmap", "Map 1-year, 5-year, and 10-year goals across career, health, relationships, and finance.", "🌟", "personal", '{"deliverable":"life_roadmap","scope":"holistic"}'),
]


def upgrade() -> None:
    # Re-categorise existing templates to "software"
    for name, category in RECATEGORISE:
        op.execute(
            sa.text(
                "UPDATE project_templates SET category = :category WHERE name = :name AND is_system = true"
            ).bindparams(name=name, category=category)
        )

    # Insert new category templates
    for name, description, icon, category, concept_sheet in TEMPLATES:
        op.execute(
            sa.text(
                "INSERT INTO project_templates (id, name, description, icon, category, concept_sheet, is_system, created_at) "
                "VALUES (gen_random_uuid(), :name, :description, :icon, :category, CAST(:cs AS jsonb), true, now()) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(
                name=name,
                description=description,
                icon=icon,
                category=category,
                cs=concept_sheet,
            )
        )


def downgrade() -> None:
    op.execute(sa.text(
        "DELETE FROM project_templates WHERE is_system = true AND category IN "
        "('business', 'creative', 'education', 'marketing', 'personal')"
    ))
