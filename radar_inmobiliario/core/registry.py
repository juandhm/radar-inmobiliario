"""Platform registry.

Simple mapping from platform name to extractor and transformer factories.
This allows adding new platforms with a single registration call.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple

from .base import BaseExtractor, BaseTransformer


ExtractorFactory = Callable[[], BaseExtractor]
TransformerFactory = Callable[[], BaseTransformer]


class PlatformRegistry:
    """In-memory registry of platform components."""

    def __init__(self) -> None:
        self._registry: Dict[str, Tuple[ExtractorFactory, TransformerFactory]] = {}

    def register(
        self,
        platform: str,
        extractor_factory: ExtractorFactory,
        transformer_factory: TransformerFactory,
    ) -> None:
        """Register a platform with its factories."""
        key = platform.strip().lower()
        self._registry[key] = (extractor_factory, transformer_factory)

    def resolve(self, platform: str) -> Tuple[BaseExtractor, BaseTransformer]:
        """Instantiate extractor and transformer for a platform."""
        key = platform.strip().lower()
        extractor_factory, transformer_factory = self._registry[key]
        return extractor_factory(), transformer_factory()


def create_default_registry() -> PlatformRegistry:
    """Create a registry preloaded with built-in platforms."""
    from ..platforms import (
        CiencuadrasExtractor,
        CiencuadrasTransformer,
        FincaRaizExtractor,
        FincaRaizTransformer,
        MetrocuadradoExtractor,
        MetrocuadradoTransformer,
    )

    registry = PlatformRegistry()
    registry.register(
        "ciencuadras",
        extractor_factory=CiencuadrasExtractor,
        transformer_factory=CiencuadrasTransformer,
    )
    registry.register(
        "fincaraiz",
        extractor_factory=FincaRaizExtractor,
        transformer_factory=FincaRaizTransformer,
    )
    registry.register(
        "metrocuadrado",
        extractor_factory=MetrocuadradoExtractor,
        transformer_factory=MetrocuadradoTransformer,
    )
    return registry


