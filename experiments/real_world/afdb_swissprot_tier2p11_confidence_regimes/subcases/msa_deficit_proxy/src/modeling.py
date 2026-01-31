from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

@dataclass(frozen=True)
class TrainedModel:
    pipeline: Pipeline
    feature_names: list[str]

def train_ridge(
    X: pd.DataFrame,
    y: np.ndarray,
    standardize: bool,
    impute_strategy: str,
    params: Dict[str, Any],
) -> TrainedModel:
    steps = [("imputer", SimpleImputer(strategy=impute_strategy))]
    if standardize:
        steps.append(("scaler", StandardScaler()))
    steps.append(("reg", Ridge(**params)))
    pipe = Pipeline(steps)
    pipe.fit(X.to_numpy(), y)
    return TrainedModel(pipeline=pipe, feature_names=list(X.columns))

def predict(model: TrainedModel, X: pd.DataFrame) -> np.ndarray:
    return model.pipeline.predict(X.to_numpy())
