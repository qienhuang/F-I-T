from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
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

def train_logreg(
    X: pd.DataFrame,
    y: np.ndarray,
    standardize: bool,
    impute_strategy: str,
    params: Dict[str, Any],
) -> TrainedModel:
    steps = [("imputer", SimpleImputer(strategy=impute_strategy))]
    if standardize:
        steps.append(("scaler", StandardScaler()))
    steps.append(("clf", LogisticRegression(**params)))
    pipe = Pipeline(steps)
    pipe.fit(X.to_numpy(), y)
    return TrainedModel(pipeline=pipe, feature_names=list(X.columns))

def predict_proba(model: TrainedModel, X: pd.DataFrame) -> np.ndarray:
    return model.pipeline.predict_proba(X.to_numpy())[:, 1]

def coefficients(model: TrainedModel) -> Optional[Dict[str, float]]:
    try:
        clf = model.pipeline.named_steps["clf"]
        coef = clf.coef_.reshape(-1)
        return {n: float(c) for n, c in zip(model.feature_names, coef)}
    except Exception:
        return None
