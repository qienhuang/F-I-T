from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

@dataclass(frozen=True)
class TrainedModel:
    pipeline: Pipeline
    feature_names: list[str]
    trained: bool
    note: str

def train_logreg_safe(
    X: pd.DataFrame,
    y: np.ndarray,
    standardize: bool,
    impute_strategy: str,
    params: Dict[str, Any],
    min_labeled: int,
) -> TrainedModel:
    # Guard: need enough examples and both classes
    if len(y) < int(min_labeled):
        return TrainedModel(pipeline=_dummy_pipeline(), feature_names=list(X.columns), trained=False, note="too_few_labels")
    if len(np.unique(y)) < 2:
        return TrainedModel(pipeline=_dummy_pipeline(), feature_names=list(X.columns), trained=False, note="single_class")
    steps = [("imputer", SimpleImputer(strategy=impute_strategy))]
    if standardize:
        steps.append(("scaler", StandardScaler()))
    steps.append(("clf", LogisticRegression(**params)))
    pipe = Pipeline(steps)
    pipe.fit(X.to_numpy(), y)
    return TrainedModel(pipeline=pipe, feature_names=list(X.columns), trained=True, note="ok")

def _dummy_pipeline() -> Pipeline:
    # A dummy pipe that mimics predict_proba; we handle this in predict_proba_safe.
    return Pipeline([])

def predict_proba_safe(model: TrainedModel, X: pd.DataFrame, fallback_prob: float = 0.5) -> np.ndarray:
    if not model.trained:
        return np.full(shape=(len(X),), fill_value=float(fallback_prob), dtype=float)
    return model.pipeline.predict_proba(X.to_numpy())[:, 1]
