"""
    Run operations to get the keyphrases of this document
"""

from relevanceai.operations_new.processing.text.keywords.base import KeyWordBase
from relevanceai.operations_new.apibase import OperationAPIBase


class KeyWordOps(OperationAPIBase, KeyWordBase):
    def __init__(
        self,
        fields: list,
        model_name: str = "all-mpnet-base-v2",
        lower_bound: int = 0,
        upper_bound: int = 3,
        output_fields: list = None,
        stop_words: list = None,
        max_keywords: int = 1,
        **kwargs
    ):
        self.fields = fields
        self.model_name = model_name
        self.output_fields = output_fields
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.stop_words = stop_words
        self.max_keywords = max_keywords
        super().__init__(**kwargs)
