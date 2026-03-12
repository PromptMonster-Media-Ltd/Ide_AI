"""Seed project_templates with system starter templates.

Revision ID: 017
Revises: 016
Create Date: 2026-03-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TEMPLATES = [
    ("SaaS MVP", "Launch a software-as-a-service product with subscription billing, user auth, and a landing page.", "🚀", "saas", '{"platform":"web","tech_constraints":"React, Node.js, Stripe integration","success_metric":"First 100 paying users in 90 days"}'),
    ("Mobile App", "Build a cross-platform mobile application with native feel and app store deployment.", "📱", "mobile", '{"platform":"mobile (iOS + Android)","tech_constraints":"React Native or Flutter","success_metric":"1000 downloads in first month"}'),
    ("E-Commerce Store", "Set up an online store with product catalog, cart, checkout, and order management.", "🛒", "ecommerce", '{"platform":"web","tech_constraints":"Shopify or custom, payment processing","success_metric":"First $10K in monthly revenue"}'),
    ("Content Platform", "Create a blog, newsletter, or media site with content management and audience growth tools.", "📝", "content", '{"platform":"web","tech_constraints":"CMS, SEO optimization, email capture","success_metric":"10K monthly visitors"}'),
    ("AI-Powered Tool", "Build an application leveraging AI/ML for intelligent features, automation, or content generation.", "🤖", "ai_ml", '{"platform":"web","tech_constraints":"LLM API integration, vector database","success_metric":"Product-market fit validated with 50 beta users"}'),
    ("Community Platform", "Build a community hub with forums, groups, events, and member profiles.", "👥", "social", '{"platform":"web + mobile","tech_constraints":"Real-time messaging, user-generated content moderation","success_metric":"500 active community members"}'),
    ("Creative Portfolio", "Showcase creative work with a stunning portfolio site, project galleries, and contact form.", "🎨", "creative", '{"platform":"web","tech_constraints":"Image optimization, responsive design, minimal CMS","success_metric":"Portfolio leads to 5 client inquiries per month"}'),
    ("API / Developer Tool", "Build a developer-focused API, SDK, or CLI tool with documentation and developer portal.", "⚡", "developer", '{"platform":"API / CLI","tech_constraints":"OpenAPI spec, rate limiting, API key management","success_metric":"100 API consumers within 3 months"}'),
    ("Marketplace", "Two-sided marketplace connecting buyers and sellers with listings, search, and transactions.", "🏪", "marketplace", '{"platform":"web","tech_constraints":"Search, payments, escrow, reviews system","success_metric":"100 listings and 50 transactions in first quarter"}'),
    ("Blank Canvas", "Start from scratch with a completely blank project. Define everything yourself.", "✨", "general", '{}'),
]


def upgrade() -> None:
    for name, description, icon, category, concept_sheet in TEMPLATES:
        op.execute(
            sa.text(
                "INSERT INTO project_templates (id, name, description, icon, category, concept_sheet, is_system, created_at) "
                "VALUES (gen_random_uuid(), :name, :description, :icon, :category, :concept_sheet::jsonb, true, now()) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(
                name=name,
                description=description,
                icon=icon,
                category=category,
                concept_sheet=concept_sheet,
            )
        )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM project_templates WHERE is_system = true"))
