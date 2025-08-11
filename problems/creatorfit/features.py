# problems/creatorfit/features.py
from __future__ import annotations

from typing import Tuple, Dict, List, Optional, Iterable

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# --------------------------------------------------------------------------------------
# EMBEDDING MODEL CONFIG
# --------------------------------------------------------------------------------------
# Reusable default model (good quality + fast). You can override from train.py if needed.
DEFAULT_EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Simple in-process cache so repeated calls don’t re-load the model from disk/network.
# This avoids slowdowns when you run train.py multiple times.
_MODEL_CACHE: Dict[str, SentenceTransformer] = {}


def _get_emb_model(name: str) -> SentenceTransformer:
    """Return a cached SentenceTransformer instance for the given model name."""
    if name not in _MODEL_CACHE:
        _MODEL_CACHE[name] = SentenceTransformer(name)
    return _MODEL_CACHE[name]


# --------------------------------------------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------------------------------------------
def _normalize_text_series(s: pd.Series) -> pd.Series:
    """
    Basic, idempotent cleanup for transcript text.
    Keep it intentionally light — MiniLM handles raw text well.
    """
    return s.fillna("").astype(str).str.strip()


# --------------------------------------------------------------------------------------
# AUDIENCE & EXPOSURE FEATURES
# --------------------------------------------------------------------------------------
def add_audience_and_exposure(
    df: pd.DataFrame,
    target_geo: str,
    target_lang: str,
) -> pd.DataFrame:
    """
    Adds ONLY pre-booking signals:
      - geo_match (0/1): creator's geography equals campaign target
      - lang_match (0/1): creator's language equals campaign target
      - log_views_90d: stabilized exposure (log1p of views_90d)
    NOTE: assumes df is already cleaned in preprocessing.
    """
    df = df.copy()

    # Equality checks use normalized cases (done in preprocessing),
    # but we guard again for safety if a different cleaner is used.
    df["geo_match"] = (df["geography"].str.upper() == target_geo.upper()).astype(int)
    df["lang_match"] = (df["language"].str.title() == target_lang.title()).astype(int)

    # Keep raw views_90d (for the model) AND add a log-stabilized version for skew robustness.
    df["log_views_90d"] = np.log1p(df["views_90d"].clip(lower=0))

    return df


# --------------------------------------------------------------------------------------
# EMBEDDING HELPERS
# --------------------------------------------------------------------------------------
def _encode_texts(
    texts: Iterable[str],
    model: SentenceTransformer,
    batch_size: int = 256,
    normalize: bool = True,
) -> np.ndarray:
    """
    Encode texts in batches (SentenceTransformer handles batching internally).
    Returns an array of shape (N, d).
    """
    return model.encode(
        list(texts),
        batch_size=batch_size,
        normalize_embeddings=normalize,   # if True, vectors are L2-normalized
        show_progress_bar=False,
    )


def compute_fit_scores(
    df: pd.DataFrame,
    program_text: str,
    emb_model_name: str = DEFAULT_EMB_MODEL,
    model: Optional[SentenceTransformer] = None,
    batch_size: int = 256,
    to_unit_interval: bool = True,
) -> pd.Series:
    """
    Compute semantic Fit Score between each creator transcript and the program description.
    Implementation: cosine similarity of embeddings.
      - If embeddings are normalized, dot product == cosine similarity.
      - Optionally map cosine from [-1, 1] to [0, 1] for friendlier scale.

    Returns
    -------
    pd.Series named 'fit_score' aligned to df.index
    """
    if not isinstance(program_text, str) or not program_text.strip():
        raise ValueError("program_text must be a non-empty string.")

    # Prepare texts
    texts = _normalize_text_series(df["recent_video_transcript"])

    # Get embedding model (cached by name unless a model is explicitly provided)
    emb = model or _get_emb_model(emb_model_name)

    # Encode target program and all creator transcripts
    prog_vec = _encode_texts([program_text], emb, batch_size=1, normalize=True)         # (1, d)
    creator_mat = _encode_texts(texts, emb, batch_size=batch_size, normalize=True)      # (N, d)

    # Cosine similarity via dot (since both are normalized)
    cos = (creator_mat @ prog_vec.T).ravel()  # shape: (N,)

    # Optional: map cosine [-1, 1] -> [0, 1]
    if to_unit_interval:
        cos = 0.5 * (cos + 1.0)

    # Defensive clamp (rare numerical drift)
    cos = np.clip(cos, 0.0, 1.0)

    return pd.Series(cos, index=df.index, name="fit_score")


# --------------------------------------------------------------------------------------
# MAIN FEATURE BUILDER
# --------------------------------------------------------------------------------------
def build_features(
    df_clean: pd.DataFrame,
    program_text: str,
    target_geo: str,
    target_lang: str,
    emb_model_name: str = DEFAULT_EMB_MODEL,
    model: Optional[SentenceTransformer] = None,
) -> Tuple[pd.DataFrame, pd.Series, Dict[str, List[str]]]:
    """
    Build the pre-booking feature matrix X and the label y.

    Uses ONLY signals available before a campaign runs:
      - Fit score (semantic match between transcripts and program text)
      - Audience match flags (geo/lang)
      - Exposure & cadence
      - Topic/category (categorical, to be encoded by a downstream ColumnTransformer)

    Returns
    -------
    X : pd.DataFrame
        numeric + raw categorical columns (categoricals will be encoded later)
    y : pd.Series
        qualified_leads as float
    meta : dict
        {'numeric': [...], 'categorical': [...], 'target': 'qualified_leads'}
    """
    # 1) Add audience & exposure features
    df = add_audience_and_exposure(df_clean, target_geo, target_lang)

    # 2) Compute Fit Score with sentence-transformers (cached model to save time)
    df["fit_score"] = compute_fit_scores(
        df=df,
        program_text=program_text,
        emb_model_name=emb_model_name,
        model=model,
        to_unit_interval=True,  # 0..1 scale is intuitive for feature importance & dashboards
    )

    # 3) Define the feature contract (pre-booking only)
    numeric = [
        "fit_score",
        "posting_cadence_days",
        "views_90d",
        "log_views_90d",
        "geo_match",
        "lang_match",
    ]
    categorical = ["topic", "category_tag"]
    target = "qualified_leads"

    # 4) Safety checks: make sure we don't accidentally include outcome columns
    leakage_cols = {"clicks", "leads", "qualified_leads", "enrollments", "refunds"}
    assert not (set(numeric + categorical) & leakage_cols), "Leakage risk: outcomes in features!"

    # 5) Build X and y
    X = df[numeric + categorical].copy()
    y = df[target].astype(float).copy()

    # 6) Defensive guard against missing values (should be handled in preprocessing)
    if X.isna().any().any():
        nan_cols = X.columns[X.isna().any()].tolist()
        raise ValueError(f"NaNs found in features: {nan_cols}. Check preprocessing step.")

    meta = {"numeric": numeric, "categorical": categorical, "target": target}
    return X, y, meta
