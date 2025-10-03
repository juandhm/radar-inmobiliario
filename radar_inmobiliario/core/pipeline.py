"""ETL pipeline orchestrator.

The Pipeline class composes an extractor, a transformer, and one or many
loaders to run a simple Extract -> Transform -> Load process.
"""

from __future__ import annotations

from typing import List, Sequence

from .base import BaseExtractor, BaseTransformer, BaseLoader
from .models import Listing


class Pipeline:
    """Simple ETL pipeline orchestrator."""

    def __init__(
        self,
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        loaders: Sequence[BaseLoader],
    ) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loaders = list(loaders)

    def run(self, input_path: str, output_stem: str) -> List[str]:
        """Run the ETL pipeline and return generated artifact paths."""
        raw_items = self.extractor.extract(input_path)
        standardized = self.transformer.transform(raw_items)
        artifacts: List[str] = []
        for loader in self.loaders:
            artifacts.append(loader.load(standardized, output_stem))
        return artifacts

    def process_only(self, input_path: str) -> Sequence[Listing]:
        """Process input and return standardized items without writing outputs."""
        raw_items = self.extractor.extract(input_path)
        standardized = self.transformer.transform(raw_items)
        return standardized


