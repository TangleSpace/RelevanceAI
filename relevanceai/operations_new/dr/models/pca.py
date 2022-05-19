from typing import List, Union

import numpy as np

from relevanceai.operations_new.dr.models.base import DimReductionModelBase

from sklearn.decomposition import PCA


class PCAModel(DimReductionModelBase):
    def __init__(
        self,
        dims: int,
        alias: Union[str, None],
        **kwargs,
    ):
        self.model = PCA(n_components=dims, **kwargs)
        self.model_name = "pca"
        self.alias = alias

    def fit(
        self,
        vectors: Union[List[List[float]], np.ndarray],
    ) -> None:
        """It fits the model to the vectors.

        Parameters
        ----------
        vectors : Union[List[List[float]], np.ndarray]
            Union[List[List[float]], np.ndarray]

        """

        if isinstance(vectors, list):
            vectors = np.array(vectors)

        self.model.fit(vectors)

    def fit_transform(
        self,
        vectors: List[List[float]],
    ) -> List[List[float]]:
        """It takes a list of vectors, fits the model to the vectors, and then transforms the vectors

        Parameters
        ----------
        vectors : List[List[float]]
            List[List[float]]

        Returns
        -------
            A list of lists of floats.

        """

        vectors = np.array(vectors)
        reduced_vectors = self.model.fit_transform(vectors)
        return reduced_vectors.tolist()
