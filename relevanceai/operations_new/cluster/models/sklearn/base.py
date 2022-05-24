"""
Sklearn Base
"""
from typing import Any, List, Dict, Optional, Union

import numpy as np

from sklearn.base import ClusterMixin

from relevanceai.operations_new.cluster.models.base import ModelBase
from relevanceai.operations_new.cluster.models.sklearn import (
    models as sklearn_models,
)


class SklearnModelBase(ModelBase):
    """Sklearn model base"""

    def __init__(
        self,
        model: Union[ClusterMixin, str],
        model_kwargs: Optional[Dict] = None,
    ):
        if isinstance(model, str):
            assert model in sklearn_models
            model = SklearnModelBase.import_from_string(
                f"sklearn.cluster.{sklearn_models[model]}"
            )
            if model_kwargs is None:
                model_kwargs = {}

            self.model = model(**model_kwargs)
        else:
            assert model.__name__ in list(sklearn_models.values())
            self.model = model

    @staticmethod
    def import_from_string(name):
        components = name.split(".")
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def fit_predict(self, *args, **kwargs) -> List[int]:
        res: np.ndarray = self.model.fit_predict(*args, **kwargs)
        return res.tolist()

    def fit(self, *args, **kwargs) -> Any:
        return self.model.fit(*args, **kwargs)

    def predict(self, *args, **kwargs) -> List[int]:
        res: np.ndarray = self.model.predict(*args, **kwargs)
        return res.tolist()

    @property
    def name(self):
        return self.model.__name__.lower()

    @property
    def cluster_centers_(self):
        return self.model.cluster_centers_

    @property
    def alias(self):
        return self.name + str(self.model.n_clusters)
