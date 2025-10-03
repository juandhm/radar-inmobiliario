"""Core base interfaces for the ETL pipeline.

These abstract base classes define the contracts for platform-specific
extractors and transformers, as well as for output loaders. Keep these
interfaces minimal and implementation-agnostic to maintain simplicity.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Sequence


class BaseExtractor(ABC):
    """Abstract base class for data extractors.

    Implementations should read platform-specific raw data and return a list of
    dictionaries with a consistent structure per platform.
    """

    @abstractmethod
    def extract(self, input_path: str) -> List[Dict[str, Any]]:
        """Read platform-specific raw data and return a list of dicts.

        Parameters
        ----------
        input_path: str
            Path to the platform raw data file (e.g., JSON file).
        """


class BaseTransformer(ABC):
    """Abstract base class for data transformers.

    Implementations should map raw dictionaries to the standardized model.
    """

    @abstractmethod
    def transform(self, raw_items: List[Dict[str, Any]]) -> Sequence["Listing"]:
        """Map raw items to the standardized Listing model.

        Parameters
        ----------
        raw_items: List[Dict[str, Any]]
            Items produced by a platform extractor.
        """


class BaseLoader(ABC):
    """Abstract base class for output loaders.

    Implementations should persist standardized items to a target (e.g., JSON,
    CSV, database).
    """

    @abstractmethod
    def load(self, items: Sequence["Listing"], output_stem: str) -> str:
        """Persist items and return the generated artifact path.

        Parameters
        ----------
        items: Sequence[Listing]
            Standardized items to be persisted.
        output_stem: str
            Output path without extension. Loader will append its own extension.
        """


