"""
RelevanceAI Operations wrappers for use from a Dataset object

.. code-block::

    from relevanceai import Client

    client = Client()

    dataset = client.Dataset()

    dataset.vectorize_text(*args, **kwargs)

    dataset.reduce_dims(*args, **kwargs)

    dataset.cluster(*args **kwarsgs)
"""
from tqdm.auto import tqdm
from typing import Any, Dict, List, Optional

from relevanceai.dataset.write import Write
from relevanceai.utils.decorators.analytics import track
from relevanceai.constants import EXPLORER_APP_LINK


class Operations(Write):
    @track
    def reduce_dims(
        self,
        vector_fields: List[str],
        n_components: int = 3,
        batched: bool = False,
        model: Optional[Any] = None,
        model_kwargs: Optional[dict] = None,
        alias: Optional[str] = None,
        filters: Optional[list] = None,
        chunksize: Optional[int] = 100,
        output_field: str = None,
    ):
        """It takes a list of fields, a list of models, a list of filters, and a chunksize, and then runs
        the DimReductionOps class on the documents in the dataset

        Parameters
        ----------
        fields : List[str]
            List[str]
        models : Optional[List[Any]]
            List[Any] = None,
        filters : Optional[List[Dict[str, Any]]]
            A list of dictionaries, each dictionary containing a filter.
        chunksize : int, optional
            The number of documents to process at a time.

        Returns
        -------
            Nothing is being returned.

        """
        from relevanceai.operations_new.dr.ops import DimReductionOps

        model = "pca" if model is None else model

        ops = DimReductionOps(
            credentials=self.credentials,
            vector_fields=vector_fields,
            n_components=n_components,
            model=model,
            model_kwargs=model_kwargs,
            alias=alias,
            output_field=output_field,
        )

        res = ops.run(
            dataset=self,
            select_fields=vector_fields,
            chunksize=chunksize,
            filters=filters,
            batched=batched,
        )

        return ops

    @track
    def vectorize_text(
        self,
        fields: List[str],
        batched: bool = True,
        models: Optional[List[Any]] = None,
        filters: Optional[list] = None,
        chunksize: Optional[int] = 20,
        output_fields: list = None,
    ):
        """It takes a list of fields, a list of models, a list of filters, and a chunksize, and then it runs
        the VectorizeOps function on the documents in the database

        Parameters
        ----------
        fields : List[str]
            List[str]
        models : List[Any]
            List[Any]
        filters : List[Dict[str, Any]]
            List[Dict[str, Any]]
        chunksize : int, optional
            int = 100,

        Returns
        -------
            Nothing

        """
        from relevanceai.operations_new.vectorize.text.ops import VectorizeTextOps

        models = ["all-mpnet-base-v2"] if models is None else models

        ops = VectorizeTextOps(
            credentials=self.credentials,
            fields=fields,
            models=models,
            output_fields=output_fields,
        )

        filters = [] if filters is None else filters
        filters += ops._get_base_filters()
        res = ops.run(
            dataset=self,
            select_fields=fields,
            filters=filters,
            batched=batched,
            chunksize=chunksize,
        )

        return ops

    @track
    def vectorize_image(
        self,
        fields: List[str],
        models: Optional[List[Any]] = None,
        batched: Optional[bool] = True,
        filters: Optional[list] = None,
        chunksize: Optional[int] = 20,
    ):
        """It takes a list of fields, a list of models, a list of filters, and a chunksize, and then it runs
        the VectorizeOps function on the documents in the database

        Parameters
        ----------
        fields : List[str]
            List[str]
        models : List[Any]
            List[Any]
        filters : List[Dict[str, Any]]
            List[Dict[str, Any]]
        chunksize : int, optional
            int = 100,

        Returns
        -------
            Nothing

        """
        from relevanceai.operations_new.vectorize.image.ops import VectorizeImageOps

        models = ["clip"] if models is None else models

        ops = VectorizeImageOps(
            credentials=self.credentials,
            fields=fields,
            models=models,
        )

        filters = [] if filters is None else filters
        filters += ops._get_base_filters()

        res = ops.run(
            dataset=self,
            select_fields=fields,
            filters=filters,
            batched=batched,
            chunksize=chunksize,
        )

        return ops

    @track
    def label(
        self,
        vector_fields: List[str],
        label_documents: List[Any],
        expanded: bool = True,
        max_number_of_labels: int = 1,
        similarity_metric: str = "cosine",
        similarity_threshold: float = 0,
        label_field: str = "label",
        label_vector_field: str = "label_vector_",
        batched: bool = True,
        filters: Optional[list] = None,
        chunksize: Optional[int] = 100,
        output_field: str = None,
        **kwargs,
    ):
        """This function takes a list of documents, a list of vector fields, and a list of label documents,
        and then it labels the documents with the label documents

        Parameters
        ----------
        vector_fields : List[str]
            List[str]
        label_documents : List[Any]
            List[Any]
        expanded, optional
            If True, the label_vector_field will be a list of vectors. If False, the label_vector_field
        will be a single vector.
        max_number_of_labels : int, optional
            int = 1,
        similarity_metric : str, optional
            str = "cosine",
        filters : Optional[list]
            A list of filters to apply to the documents.
        chunksize : int, optional
            The number of documents to process at a time.
        similarity_threshold : float, optional
            float = 0,
        label_field : str, optional
            The name of the field that will contain the label.
        label_vector_field, optional
            The field that will be added to the documents that contain the label vector.

        Returns
        -------
            The return value is a list of documents.

        """

        from relevanceai.operations_new.label.ops import LabelOps

        if len(vector_fields) > 1:
            raise ValueError(
                "We currently do not support on more than 1 vector length."
            )

        # self.datasets.create(
        #     dataset_id=self.dataset_id, schema={output_field: "chunks"}
        # )

        ops = LabelOps(
            credentials=self.credentials,
            label_documents=label_documents,
            vector_field=vector_fields[0],
            expanded=expanded,
            max_number_of_labels=max_number_of_labels,
            similarity_metric=similarity_metric,
            similarity_threshold=similarity_threshold,
            label_field=label_field,
            label_vector_field=label_vector_field,
            output_field=output_field,
        )
        # Add an exists filter
        if filters is None:
            filters = []

        filters += [
            {
                "field": vector_fields[0],
                "filter_type": "exists",
                "condition": "==",
                "condition_value": " ",
            }
        ]
        # Check if output field already exists
        res = ops.run(
            dataset=self,
            filters=filters,
            batched=batched,
            chunksize=chunksize,
            select_fields=vector_fields,
            **kwargs,
        )

        return ops

    @track
    def label_from_dataset(
        self,
        vector_fields: list,
        label_dataset,
        max_number_of_labels: int = 1,
        label_vector_field="label_vector_",
        expanded: bool = False,
        similarity_metric: str = "cosine",
        label_field: str = "label",
        batched: bool = True,
        filters: list = None,
        similarity_threshold=0.1,
        chunksize: int = 100,
        output_field: str = None,
        **kwargs,
    ):
        """
        Label from another dataset
        """
        if output_field is None:
            output_field = "_label_." + label_dataset.dataset_id + "." + label_field
        label_documents = label_dataset.get_all_documents()
        return self.label(
            vector_fields=vector_fields,
            label_documents=label_documents,
            expanded=expanded,
            output_field=output_field,
            max_number_of_labels=max_number_of_labels,
            similarity_metric=similarity_metric,
            similarity_threshold=similarity_threshold,
            label_field=label_field,
            label_vector_field=label_vector_field,
            batched=batched,
            filters=filters,
            chunksize=chunksize,
            **kwargs,
        )

    @track
    def split_sentences(
        self,
        text_fields: List[str],
        output_field="_splittextchunk_",
        language: str = "en",
        inplace: bool = True,
        batched: bool = False,
        filters: Optional[list] = None,
        chunksize: Optional[int] = 100,
    ):
        """
        This function splits the text in the `text_field` into sentences and stores the sentences in
        the `output_field`

        Parameters
        ----------
        text_field : str
            The field in the documents that contains the text to be split into sentences.
        output_field, optional
            The name of the field that will contain the split sentences.
        language : str, optional
            The language of the text. This is used to determine the sentence splitting rules.

        """
        from relevanceai.operations_new.processing.text.sentence_splitting.ops import (
            SentenceSplitterOps,
        )

        ops = SentenceSplitterOps(
            credentials=self.credentials,
            text_fields=text_fields,
            language=language,
            inplace=inplace,
            output_field=output_field,
        )

        res = ops.run(
            dataset=self,
            select_fields=text_fields,
            batched=batched,
            filters=filters,
            chunksize=chunksize,
        )

        return ops

    @track
    def cluster(
        self,
        vector_fields: List[str],
        model: Optional[Any] = None,
        alias: Optional[str] = None,
        model_kwargs: Optional[Dict[str, Any]] = None,
        chunksize: Optional[int] = 100,
        filters: Optional[list] = None,
        batched: Optional[bool] = False,
        include_cluster_report: bool = True,
        **kwargs,
    ):
        """`cluster` is a function that takes in a list of vector fields, a model, an alias, a list of
        filters, a boolean value, a dictionary of model keyword arguments, and a list of keyword
        arguments. It returns an object of type `ClusterOps`

        Example
        ----------
        .. code-block::

            from sklearn.cluster import KMeans
            model = KMeans()

            from relevanceai import Client
            client = Client()
            ds = client.Dataset("sample")
            cluster_ops = ds.cluster(
                model=model, vector_fields=["sample_vector_"],
                alias="kmeans-8"
            )

        Parameters
        ----------
        vector_fields : List[str]
            A list of possible vector fields
        model : Optional[Any]
            The clustering model to use. Currently, we support KMeans and MiniBatchKMeans.
        alias : Optional[str]
            The name of the cluster model.
        filters : Optional[list]
            Optional[list] = None,
        include_cluster_report : bool, optional
            bool = True
        model_kwargs : Optional[Dict[str, Any]]
            The cluster config to use
            You can change the number of clusters for kmeans using:
            `cluster_config={"n_clusters": 10}`. For a full list of
            possible parameters for different models, simply check how
            the cluster models are instantiated.

        Returns
        -------
            The cluster object

        """

        from relevanceai.operations_new.cluster.ops import ClusterOps

        model = "kmeans" if model is None else model
        model_kwargs = {} if model_kwargs is None else model_kwargs

        ops = ClusterOps(
            model=model,
            alias=alias,  # type: ignore
            vector_fields=vector_fields,  # type: ignore
            verbose=False,
            credentials=self.credentials,
            dataset_id=self.dataset_id,
            model_kwargs=model_kwargs,
            **kwargs,
        )

        if filters is not None:
            filters = ops._get_filters(filters, vector_fields)

        # Create the cluster report
        ops.run(
            dataset=self,
            select_fields=vector_fields,
            batched=batched,
            chunksize=chunksize,
            filters=filters,
        )

        print(
            f"""You can now utilise the ClusterOps object using the below:

    cluster_ops = client.ClusterOps(
        alias='{ops.alias}',
        vector_fields={ops.vector_fields},
        dataset_id='{self.dataset_id}'
    )"""
        )

        print("Configure your new cluster app below:")
        print()
        print(EXPLORER_APP_LINK.format(self.dataset_id))
        return ops

    def _get_alias(self, alias: Any) -> str:
        # Auto-generates alias here
        if alias is None:
            if hasattr(self.model, "n_clusters"):
                n_clusters = (
                    self.n_clusters
                    if self.n_clusters is not None
                    else self.model.n_clusters
                )
                alias = f"{self.model_name}-{n_clusters}"

            elif hasattr(self.model, "k"):
                n_clusters = (
                    self.n_clusters if self.n_clusters is not None else self.model.k
                )
                alias = f"{self.model_name}-{n_clusters}"

            else:
                alias = self.model_name

            Warning.MISSING_ALIAS.format(alias=alias)  # type: ignore

        if self.verbose:
            print(f"The alias is `{alias.lower()}`.")
        return alias.lower()

    @track
    def batch_cluster(
        self,
        vector_fields: List[str],
        model: Any = None,
        alias: Optional[str] = None,
        filters: Optional[list] = None,
        include_cluster_report: bool = True,
        model_kwargs: dict = None,
        **kwargs,
    ):
        from relevanceai.operations_new.cluster.batch.ops import BatchClusterOps

        cluster_ops = BatchClusterOps(
            model=model,
            alias=alias,
            vector_fields=vector_fields,
            model_kwargs=model_kwargs,
            **kwargs,
        )

        if filters is not None:
            filters = cluster_ops._get_filters(filters, vector_fields)

        cluster_ops.run(self, filters=filters)

        return cluster_ops

    def extract_sentiment(
        self,
        text_fields: List[str],
        model_name: str = "cardiffnlp/twitter-roberta-base-sentiment",
        highlight: bool = False,
        max_number_of_shap_documents: int = 1,
        min_abs_score: float = 0.1,
        sensitivity: float = 0,
        filters: Optional[list] = None,
        output_fields: list = None,
        chunksize: int = 100,
        batched: bool = True,
    ):
        """
        Extract sentiment from the dataset

        If you are dealing with news sources, you will want
        more sensitivity, as more news sources are likely to be neutral

        """
        from relevanceai.operations_new.sentiment.ops import SentimentOps

        ops = SentimentOps(
            text_fields=text_fields,
            model_name=model_name,
            highlight=highlight,
            max_number_of_shap_documents=max_number_of_shap_documents,
            min_abs_score=min_abs_score,
            output_fields=output_fields,
            sensitivity=sensitivity,
        )
        return ops.run(
            self,
            filters=filters,
            select_fields=text_fields,
            chunksize=chunksize,
            batched=batched,
        )

    def extract_emotion(
        self,
        text_fields: list,
        model_name="joeddav/distilbert-base-uncased-go-emotions-student",
        filters: list = None,
        chunksize: int = 100,
        output_fields: list = None,
        min_score: float = 0.3,
        batched: bool = True,
    ):
        """
        Extract an emotion.

        .. code-block::

            from relevanceai import Client
            client = Client()
            ds = client.Dataset("sample")
            ds.extract_emotion(
                text_fields=["sample_1_label"],
            )

        """
        from relevanceai.operations_new.emotion.ops import EmotionOps

        ops = EmotionOps(
            credentials=self.credentials,
            text_fields=text_fields,
            model_name=model_name,
            output_fields=output_fields,
            min_score=min_score,
        )
        return ops.run(
            self,
            filters=filters,
            select_fields=text_fields,
            chunksize=chunksize,
            batched=batched,
        )

    def apply_transformers_pipeline(
        self,
        text_fields: list,
        pipeline,
        output_field: Optional[str] = None,
        filters: Optional[list] = None,
    ):
        """
        Apply a transformers pipeline generically.

        .. code-block::

            from transformers import pipeline
            pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h", device=0)
            ds.apply_transformers_pipeline(
                text_fields, pipeline
            )

        """
        from relevanceai.operations_new.processing.transformers.ops import (
            TransformersPipelineOps,
        )

        ops = TransformersPipelineOps(
            text_fields=text_fields,
            pipeline=pipeline,
            output_field=output_field,
        )
        return ops.run(self, filters=filters, select_fields=text_fields)

    def subcluster(
        self,
        vector_fields: List[str],
        alias: str,
        parent_field: str,
        model: Any = "kmeans",
        cluster_field: str = "_cluster_",
        model_kwargs: Optional[dict] = None,
        filters: Optional[list] = None,
        cluster_ids: Optional[list] = None,
        min_parent_cluster_size: int = 0,
        **kwargs,
    ):
        from relevanceai.operations_new.cluster.sub.ops import SubClusterOps

        ops = SubClusterOps(
            model=model,
            alias=alias,
            vector_fields=vector_fields,
            parent_field=parent_field,
            model_kwargs=model_kwargs,
            cluster_field=cluster_field,
            credentials=self.credentials,
            dataset_id=self.dataset_id,
            cluster_ids=cluster_ids,
            min_parent_cluster_size=min_parent_cluster_size,
            **kwargs,
        )

        # Building an infinitely hackable SDK

        # Add filters and select fields
        select_fields = vector_fields + [parent_field]
        if filters is None:
            filters = []

        if cluster_ids is not None:
            filters += [
                {
                    "field": parent_field,
                    "filter_type": "exact_match",
                    "condition": "==",
                    "condition_value": cluster_id,
                }
                for cluster_id in cluster_ids
            ]
        filters += [
            {
                "field": vf,
                "filter_type": "exists",
                "condition": ">=",
                "condition_value": " ",
            }
            for vf in vector_fields
        ]
        filters += [
            {
                "field": parent_field,
                "filter_type": "exists",
                "condition": ">=",
                "condition_value": " ",
            }
        ]

        ops.run(
            self,
            filters=filters,
            select_fields=select_fields,
        )
        print(
            f"""You can now utilise the ClusterOps object based on subclustering.

    cluster_ops = client.ClusterOps(
        alias='{ops.alias}',
        vector_fields={ops.vector_fields},
        dataset_id='{self.dataset_id}'
    )"""
        )

        from relevanceai.operations_new.cluster.ops import ClusterOps

        model = "kmeans" if model is None else model
        model_kwargs = {} if model_kwargs is None else model_kwargs

        ops = ClusterOps(
            model=model,
            alias=alias,  # type: ignore
            vector_fields=vector_fields,  # type: ignore
            verbose=False,
            credentials=self.credentials,
            dataset_id=self.dataset_id,
            model_kwargs=model_kwargs,
            **kwargs,
        )
        return ops

    def byo_cluster(
        self,
        vector_fields: list,
        alias: str,
        byo_cluster_field: str,
        centroids: list = None,
    ):
        """
        Bring your own clusters and we can calculate the centroids for you.

        Example
        =========

        .. code-block::

            dataset = client.Dataset("retail_reviews")
            cluster_ops = dataset.byo_cluster(
                vector_fields=['reviews.title_mpnet_vector_'],
                alias="manufacturer_two",
                byo_cluster_field="manufacturer"
            )

        """
        from relevanceai.operations_new.cluster.ops import ClusterOps

        ops = ClusterOps(
            model=None,
            alias=alias,
            verbose=False,
            vector_fields=vector_fields,
            credentials=self.credentials,
            dataset_id=self.dataset_id,
            byo_cluster_field=byo_cluster_field,
        )
        # here we create the centroids for the clusters
        if centroids is None:
            results = ops.create_centroids()
        else:
            results = self.datasets.cluster.centroids.insert(
                dataset_id=self.dataset_id,
                cluster_centers=centroids,
                vector_fields=vector_fields,
                alias=alias,
            )
        return ops

    def clean_text(
        self,
        text_fields: list,
        output_fields: list = None,
        remove_html_tags: bool = True,
        lower=False,
        remove_punctuation=True,
        remove_digits=True,
        remove_stopwords: list = None,
        lemmatize: bool = False,
        filters: list = None,
        replace_words: dict = None,
    ):
        """
        Cleans text for you!
        """
        from relevanceai.operations_new.processing.text.clean.ops import CleanTextOps

        if output_fields is None:
            output_fields = [t + "_clean" for t in text_fields]
            print(f"The output fields are {output_fields}.")

        ops = CleanTextOps(
            text_fields=text_fields,
            output_fields=output_fields,
            remove_html_tags=remove_html_tags,
            lower=lower,
            remove_punctuation=remove_punctuation,
            remove_digits=remove_digits,
            remove_stopword=remove_stopwords,
            lemmatize=lemmatize,
            replace_words=replace_words,
        )

        print("🥸 A clean house is a sign of no Internet connection.")
        ops.run(
            self,
            filters=filters,
            select_fields=text_fields,
            batched=True,
            output_fields=output_fields,
        )

        return ops

    def count_text(
        self,
        text_fields: list,
        count_words: bool = True,
        count_characters: bool = True,
        count_sentences: bool = True,
        filters: list = None,
        chunksize: int = 1000,
    ):
        from relevanceai.operations_new.processing.text.count.ops import CountTextOps

        ops = CountTextOps(
            text_fields=text_fields,
            include_char_count=count_characters,
            include_word_count=count_words,
            include_sentence_count=count_sentences,
        )
        res = ops.run(
            dataset=self,
            select_fields=text_fields,
            chunksize=chunksize,
            filters=filters,
            batched=True,
        )
        return ops

    def analyze_text(
        self,
        fields: list,
        vector_fields: list = None,
        vectorize=True,
        vectorize_models: list = None,
        cluster: bool = True,
        cluster_model=None,
        cluster_alias: str = None,
        subcluster: bool = True,
        subcluster_model=None,
        subcluster_alias: str = None,
        subcluster_parent_field: str = None,
        extract_sentiment: bool = True,
        extract_emotion: bool = False,
        count: bool = True,
        verbose: bool = False,
        filters: list = None,
    ):
        # is it worth separating
        # analyze text and analyze text vectors?
        if verbose:
            print("⚛️ Why can't you trust atoms?")
            print("Because they make up everything!")

        if vectorize:
            if vector_fields is None:
                vector_fields = [text_field + "_vector_" for text_field in fields]
                print(f"Outputting to: {vector_fields}")
            self.vectorize_text(
                fields=fields,
                models=vectorize_models,
                filters=filters,
                output_fields=vector_fields,
            )

        try:
            # Runs clustering and subclustering first
            self.analyze_vectors(
                vector_fields=vector_fields,
                cluster=cluster,
                cluster_model=cluster_model,
                cluster_alias=cluster_alias,
                subcluster=subcluster,
                subcluster_alias=subcluster_alias,
                subcluster_parent_field=subcluster_parent_field,
                subcluster_model=subcluster_model,
                filters=filters,
            )
        except:
            pass

        if extract_emotion:
            try:
                print("Extracting emotion...")
                raise NotImplementedError("Have not implemented emotion yet")
            except:
                pass

        if extract_sentiment:
            print("Extracting sentiment...")
            try:
                self.extract_sentiment(text_fields=fields, filters=filters)
            except:
                pass

        if count:
            try:
                print("Extracting count...")
                self.count_text(
                    text_fields=fields,
                    count_words=True,
                    count_characters=True,
                    count_sentences=True,
                    filters=filters,
                )
            except:
                pass
        # TODO:
        # Launch an explorer app with the right settings
        return

    def analyze_vectors(
        self,
        vector_fields: list = None,  # These vector fields will be used throughout
        cluster: bool = False,
        cluster_model=None,
        cluster_alias: str = None,
        subcluster: bool = False,
        subcluster_alias: str = None,
        subcluster_parent_field: str = None,
        subcluster_model=None,
        filters: list = None,
    ):
        # is it worth separating
        # analyze text and analyze text vectors?
        if cluster:
            if vector_fields is None or cluster_model is None:
                raise ValueError(
                    "Vector fields and cluster_models need to not be None."
                )
            self.cluster(
                vector_fields=vector_fields,
                model=cluster_model,
                filters=filters,
                alias=cluster_alias,
            )

        if subcluster:
            # How do I get the cluster parent field
            # TODO - how do you set the alias and parent field?
            if (
                vector_fields is None
                or subcluster_alias is None
                or subcluster_parent_field is None
                or subcluster_model is None
            ):
                raise ValueError(
                    "Vector fields and subcluster_models and subcluster_parent_field and subcluster_alias need to not be None."
                )
            self.subcluster(
                vector_fields=vector_fields,
                alias=subcluster_alias,
                parent_field=subcluster_parent_field,
                model=subcluster_model,
                filters=filters,
            )

    def extract_keywords(
        self,
        fields: list,
        model_name: str = "all-mpnet-base-v2",
        output_fields: list = None,
        lower_bound: int = 0,
        upper_bound: int = 3,
        chunksize: int = 200,
        max_keywords: int = 1,
        stop_words: list = None,
        filters: list = None,
        batched: bool = True,
    ):
        """
        Extract the keyphrases of a text field and output and store it into
        a separate field. This can be used to better explain sentiment,
        label and identify why certain things were clustered together!
        """
        from relevanceai.operations_new.processing.text.keywords.ops import KeyWordOps

        ops = KeyWordOps(
            credentials=self.credentials,
            fields=fields,
            model_name=model_name,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            output_fields=output_fields,
            stop_words=stop_words,
            max_keywords=max_keywords,
        )
        ops.run(
            self,
            batched=batched,
            chunksize=chunksize,
            filters=filters,
            select_fields=fields,
            output_fields=output_fields,
        )
        return ops

    def deduplicate(
        self, fields, amount_to_deduplicate: int = 100, filters: list = None
    ):
        """
        You can deduplicate values in your dataset here.

        .. code-block::

            from relevanceai import Client
            client = Client()
            ds.deduplicate("text_field")

        """
        results = self.aggregate(
            aggregation_query=dict(
                groupby=[
                    {
                        "field": field,
                        "agg": "category",
                        "name": field,
                        "group_size": amount_to_deduplicate,
                        "select_fields": ["_id"],
                    }
                    for field in fields
                ]
            ),
            filters=filters,
            page_size=amount_to_deduplicate,
        )

        for r in tqdm(results["results"]):
            all_ids = [d["_id"] for d in r["documents"]]
            self.datasets.documents.bulk_delete(self.dataset_id, ids=all_ids[1:])
        print("Finished deduplicating!")
