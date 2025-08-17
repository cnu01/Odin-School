from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer


def build_preprocessor(
    categorical: List[str],
    numeric: List[str],
) -> ColumnTransformer:
    """
    Returns a ColumnTransformer that:
      - One-hot encodes categorical features (handle_unknown='ignore')
      - Passes numeric features through unchanged
    """
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", ohe, categorical),
            ("num", "passthrough", numeric),
        ],
        remainder="drop",
        sparse_threshold=1.0,  # keep sparse output for efficiency
    )
    return preprocessor


def group_train_val_split(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    val_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Group-aware split so the same creator_id does NOT leak across train/val.
    Returns X_train_idx, X_val_idx, y_train_idx, y_val_idx (as index arrays).
    """
    splitter = GroupShuffleSplit(n_splits=1, test_size=val_size, random_state=random_state)
    train_idx, val_idx = next(splitter.split(X, y, groups=groups))
    return train_idx, val_idx, train_idx, val_idx
