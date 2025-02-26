"""
    
    Add emotion.

"""
import numpy as np
import csv
from typing import Optional
from urllib.request import urlopen
from relevanceai.constants.errors import MissingPackageError
from relevanceai.operations_new.base import OperationBase


class EmotionBase(OperationBase):
    def __init__(
        self,
        text_fields: list,
        model_name="joeddav/distilbert-base-uncased-go-emotions-student",
        output_fields: list = None,
        min_score: float = 0.3,
        **kwargs,
    ):
        """
        Sentiment Ops.

        Parameters
        -------------

        model_name: str
            The name of the model

        """
        self.model_name = model_name
        self.text_fields = text_fields
        self.output_fields = output_fields
        self.min_score = min_score
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def classifier(self):
        if not hasattr(self, "_classifier"):
            import transformers

            self._classifier = transformers.pipeline(
                "sentiment-analysis", return_all_scores=False, model=self.model_name
            )
        return self._classifier

    def analyze_emotion(
        self,
        text: str,
    ):
        """
        Analyze sentiment
        """
        if text is None:
            return {}
        output = self.classifier(text, truncation=True, max_length=512)
        # [{'label': 'desire', 'score': 0.30693167448043823}]
        if output[0]["score"] > self.min_score:
            return output
        return {}

    @property
    def name(self):
        return "emotion"

    def _get_output_field(self, text_field):
        norm_name = self.model_name.replace("/", "-")
        return f"_emotion_.{text_field}.{norm_name}"

    def transform(self, documents):
        # For each document, update the field
        sentiment_docs = [{"_id": d["_id"]} for d in documents]
        for i, t in enumerate(self.text_fields):
            if self.output_fields is not None:
                output_field = self.output_fields[i]
            else:
                output_field = self._get_output_field(t)
            sentiments = [
                self.analyze_emotion(
                    self.get_field(t, doc, missing_treatment="return_empty_string"),
                )
                for doc in documents
            ]
            self.set_field_across_documents(output_field, sentiments, sentiment_docs)
        return sentiment_docs
