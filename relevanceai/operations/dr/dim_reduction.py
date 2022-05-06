from typing import Union, Any, Optional, List

from doc_utils import DocUtils

from relevanceai.client.helpers import Credentials
from relevanceai.operations.dr.base import PCA
from relevanceai.operations.dr.base import TSNE
from relevanceai.operations.dr.base import Ivis
from relevanceai.operations.dr.base import UMAP
from relevanceai.operations import BaseOps
from relevanceai._api import APIClient


class ReduceDimensionsOps(APIClient, BaseOps):
    def __init__(
        self,
        credentials: Credentials,
        n_components: int,
        model: Union[PCA, TSNE, Ivis, PCA, str, Any],
        dr_field: str = "_dr_",
        verbose: bool = True,
        dataset_id: Optional[str] = None,
        vector_fields: Optional[List] = None,
        alias: Optional[str] = None,
    ):
        if isinstance(model, str):
            algorithm = model.upper()
            if algorithm == "PCA":

                model = PCA()
            elif algorithm == "TSNE":

                model = TSNE()
            elif algorithm == "UMAP":

                model = UMAP()
            elif algorithm == "IVIS":

                model = Ivis()
            else:
                raise ValueError()

        self.model = model
        self.dr_field = dr_field
        self.verbose = verbose
        self.n_components = n_components
        self.dataset_id = dataset_id
        self.vector_fields = vector_fields
        self.alias = alias
        if len(vector_fields) > 0:
            self.vector_name = "-".join([f.replace('_vector_', '') for f in vector_fields])
        else:
            self.vector_name = vector_fields[0]

        super().__init__(credentials)

    def _insert_dr_metadata(
        self,
        dataset_id: str,
        alias: str,
        vector_fields: List[str],
    ):
        metadata = self.datasets.metadata(dataset_id=dataset_id)
        if "_dr_" not in metadata:
            metadata["_dr_"] = {}
        metadata["_dr_"][self.vector_name] = {
            "alias" : alias,
            "vector_fields" : vector_fields,
            "n_components" : self.n_components
        }
        self.datasets.post_metadata(dataset_id, metadata)

    def fit(
        self,
        dataset_id: Optional[str] = None,
        vector_fields: Optional[List[str]] = None,
        alias: Optional[str] = None,
        filters: Optional[list] = None,
        show_progress_bar: bool = True,
        verbose: bool = True,
    ):
        """
        Reduce Dimensions

        Example
        ---------


        Parameters
        -------------

        dataset_id: Optional[str]
            The dataset to run dimensionality reduction on
        vector_fields: Optional[List[str]]
            List of vector fields
        alias: Optional[str]
            Alias to store dimensionality reduction model
        show_progress_bar: bool
            If True, the progress bar can be shown

        """
        filters = [] if filters is None else filters
        if dataset_id is None:
            dataset_id = self.dataset_id
        if vector_fields is None:
            vector_fields = self.vector_fields
        if alias is None:
            alias = self.alias

        print("Retrieving all documents...")
        from relevanceai.utils.filter_helper import create_filter

        for vector_field in vector_fields:
            filters += create_filter(vector_field, filter_type="exists")
        documents = self._get_all_documents(
            dataset_id=dataset_id,
            select_fields=vector_fields,
            show_progress_bar=show_progress_bar,
            include_vector=True,
            filters=filters,
        )

        print("Predicting on all documents...")
        dr_documents = self.model.fit_transform_documents(
            vector_fields=vector_fields,  # type: ignore
            documents=documents,
            alias=alias,  # type: ignore
            dims=self.n_components,
            vector_name=self.vector_name
        )

        print("Updating dataset with reduced vectors...")
        self._update_documents(dataset_id=dataset_id, documents=dr_documents)  # type: ignore

        print("Updating dr metadata...")
        self._insert_dr_metadata(
            dataset_id=dataset_id, 
            vector_fields=vector_fields,
            alias=alias
        )

        if verbose:
            self._print_app_link()

    def _print_app_link(self):
        print("All complete")
        # link = CLUSTER_APP_LINK.format(self.dataset_id)
        # print(Messages.BUILD_HERE + link)

    def run(
        self,
        dataset_id: Optional[str] = None,
        vector_fields: Optional[List[str]] = None,
        alias: Optional[str] = None,
        filters: Optional[list] = None,
        show_progress_bar: bool = True,
        verbose: bool = True,
    ):
        """Operate the dashboard"""
        self.fit(
            dataset_id=dataset_id, vector_fields=vector_fields, alias=alias,
            filters=filters, show_progress_bar=show_progress_bar, verbose=verbose
        )
