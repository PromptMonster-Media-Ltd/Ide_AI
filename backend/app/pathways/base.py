"""
base.py — Pathway configuration dataclasses.
Defines the complete structure of a Concept Pathway.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StageConfig:
    """One stage in the discovery flow."""
    id: str
    label: str
    icon: str
    system_prompt: str
    required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SheetFieldConfig:
    """One field on the domain-specific design sheet."""
    key: str
    label: str
    field_type: str  # "text", "textarea", "list", "tags"
    weight: int  # confidence weight (all weights should sum to ~100)
    extraction_hint: str


@dataclass(frozen=True)
class ModuleConfig:
    """One module (page) in the pathway."""
    id: str
    label: str
    icon: str
    route_suffix: str
    component_key: str
    order: int


@dataclass(frozen=True)
class BlockCategoryConfig:
    """Category definition for blocks in this pathway."""
    id: str
    label: str
    color: str


@dataclass
class PathwayConfig:
    """Complete configuration for a concept pathway."""
    id: str
    name: str
    description: str
    icon: str
    color: str

    # AI persona
    base_persona: str

    # Discovery flow
    stages: list[StageConfig]
    extraction_prompt: str

    # Design sheet
    sheet_fields: list[SheetFieldConfig]

    # Modules (pages shown in sidebar)
    modules: list[ModuleConfig]

    # Blocks
    block_categories: list[BlockCategoryConfig]
    block_generation_prompt: str
    block_priorities: list[str] = field(default_factory=lambda: ["mvp", "v2"])
    block_efforts: list[str] = field(default_factory=lambda: ["S", "M", "L"])

    # Domain-specific layers (replaces LAYER_OPTIONS for pipeline-like modules)
    domain_layers: dict[str, dict] = field(default_factory=dict)

    # Export / pitch
    pitch_sections: list[str] = field(default_factory=list)

    # Home page creation fields
    creation_presets: list[dict] = field(default_factory=list)
    creation_fields: list[dict] = field(default_factory=list)

    # Scheduling module config (shared sprint-like module adapted per domain)
    schedule_label: str = "Sprint Planner"
    schedule_icon: str = "\U0001f3c3"  # runner emoji

    def to_api_dict(self) -> dict:
        """Serialize for the /pathways API endpoint."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "stages": [{"id": s.id, "label": s.label, "icon": s.icon} for s in self.stages],
            "sheet_fields": [
                {"key": f.key, "label": f.label, "field_type": f.field_type}
                for f in self.sheet_fields
            ],
            "modules": [
                {
                    "id": m.id, "label": m.label, "icon": m.icon,
                    "route_suffix": m.route_suffix,
                    "component_key": m.component_key, "order": m.order,
                }
                for m in sorted(self.modules, key=lambda m: m.order)
            ],
            "block_categories": [
                {"id": c.id, "label": c.label, "color": c.color}
                for c in self.block_categories
            ],
            "block_priorities": self.block_priorities,
            "block_efforts": self.block_efforts,
            "creation_presets": self.creation_presets,
            "creation_fields": self.creation_fields,
            "schedule_label": self.schedule_label,
            "schedule_icon": self.schedule_icon,
        }
