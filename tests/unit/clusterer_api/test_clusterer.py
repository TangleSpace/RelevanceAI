"""
    Testing dataset
"""

import pandas as pd
from relevanceai.http_client import Dataset, Client


def test_cluster(test_client: Client, test_sample_vector_dataset: Dataset):
    df = test_client.Dataset(test_sample_vector_dataset)
    from relevanceai.clusterer.kmeans_clusterer import KMeansModel

    vector_field = "sample_1_vector_"
    alias = "test_alias"

    model = KMeansModel()

    df.cluster(model=model, alias=alias, vector_fields=[vector_field], overwrite=True)
    assert f"_cluster_.{vector_field}.{alias}" in df.schema


def test_centroids(test_client, test_clustered_dataset):
    df = test_client.Dataset(test_clustered_dataset)
    closest = df.centroids(["sample_1_vector_"], "kmeans_10").closest()
    furthest = df.centroids(["sample_1_vector_"], "kmeans_10").furthest()
    agg = df.centroids(["sample_1_vector_"], "kmeans_10").agg({"sample_2_label": "avg"})
    groupby_agg = (
        df.centroids(["sample_1_vector_"], "kmeans_10")
        .groupby(["sample_3_description"])
        .agg({"sample_2_label": "avg"})
    )
    assert True
