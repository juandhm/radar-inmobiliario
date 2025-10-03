"""Core package for the Radar Inmobiliario ETL.

This package contains the base interfaces, standardized models, pipeline
orchestrator, registry, IO helpers, and logging configuration utilities.
"""

from .base import BaseExtractor, BaseTransformer, BaseLoader
from .models import Listing
from .pipeline import Pipeline
from .registry import PlatformRegistry

__all__ = [
    "BaseExtractor",
    "BaseTransformer",
    "BaseLoader",
    "Listing",
    "Pipeline",
    "PlatformRegistry",
]


