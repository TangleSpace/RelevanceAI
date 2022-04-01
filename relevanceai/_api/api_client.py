# -*- coding: utf-8 -*-
"""Batch client to allow for batch insertions/retrieval and encoding
"""
from typing import Callable

from relevanceai._api.batch.insert import BatchInsertClient
from relevanceai._api.batch.insert_async import BatchInsertAsyncClient


class APIClient(BatchInsertClient, BatchInsertAsyncClient):
    """Batch API client"""

    def batch_insert(self):
        raise NotImplemented

    def batch_get_and_edit(self, dataset_id: str, chunk_size: int, bulk_edit: Callable):
        """Batch get the documents and return the documents"""
        raise NotImplemented

    @property
    def base_url(self):
        return self.config.get_field("api.base_url", self.config.config)

    @base_url.setter
    def base_url(self, value):
        if value.endswith("/"):
            value = value[:-1]
        self.config.set_option("api.base_url", value)

    @property
    def base_ingest_url(self):
        return self.config.get_field("api.base_ingest_url", self.config.config)

    @base_ingest_url.setter
    def base_ingest_url(self, value):
        if value.endswith("/"):
            value = value[:-1]
        self.config.set_option("api.base_ingest_url", value)
