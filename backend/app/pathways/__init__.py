"""
Pathway Registry — central registry for Concept Pathways.
Each pathway file auto-registers at import time.
"""
from __future__ import annotations

from app.pathways.base import PathwayConfig


class PathwayRegistry:
    """Singleton registry of all available concept pathways."""

    _pathways: dict[str, PathwayConfig] = {}

    @classmethod
    def register(cls, pathway: PathwayConfig) -> None:
        cls._pathways[pathway.id] = pathway

    @classmethod
    def get(cls, pathway_id: str) -> PathwayConfig:
        if pathway_id not in cls._pathways:
            raise ValueError(f"Unknown pathway: {pathway_id}")
        return cls._pathways[pathway_id]

    @classmethod
    def get_or_default(cls, pathway_id: str | None) -> PathwayConfig:
        """Get pathway by ID, falling back to software_product."""
        if pathway_id and pathway_id in cls._pathways:
            return cls._pathways[pathway_id]
        return cls._pathways.get("software_product", next(iter(cls._pathways.values())))

    @classmethod
    def all(cls) -> list[PathwayConfig]:
        return list(cls._pathways.values())

    @classmethod
    def ids(cls) -> list[str]:
        return list(cls._pathways.keys())


def _load_pathways() -> None:
    """Import all pathway modules to trigger registration."""
    import app.pathways.software_product  # noqa: F401
    import app.pathways.marketing_campaign  # noqa: F401
    import app.pathways.creative_writing  # noqa: F401
    import app.pathways.brand_identity  # noqa: F401


_load_pathways()
