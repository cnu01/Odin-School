# problems/creatorfit/data_preprocessing.py
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional

# --------------------------------------------------------------------------------------
# SCHEMA CONTRACT
# --------------------------------------------------------------------------------------
# Required columns (names + intended dtypes). We don't force dtypes at read-time
# to avoid hard failures; we coerce later.
EXPECTED_COLS = {
    "creator_id": "string",
    "topic": "string",
    "recent_video_transcript": "string",
    "posting_cadence_days": "float64",
    "views_90d": "int64",
    "clicks": "int64",
    "leads": "int64",
    "qualified_leads": "int64",
    "enrollments": "int64",
    "refunds": "int64",
    "geography": "string",
    "language": "string",
    "category_tag": "string",
}

# Numeric columns we will coerce and guard
NUM_COLS = [
    "posting_cadence_days", "views_90d", "clicks", "leads",
    "qualified_leads", "enrollments", "refunds"
]

# Optional: if your incoming CSV uses different headers, map them to our contract.
# Example: {"country": "geography", "lang": "language"}
SCHEMA_ADAPTER: Dict[str, str] = {
    # "country": "geography",
    # "lang": "language",
}

# --------------------------------------------------------------------------------------
# PATH HELPERS
# --------------------------------------------------------------------------------------
def project_root() -> Path:
    """Return repo root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]

def dataset_path(filename: str) -> Path:
    """Join dataset/filename under repo root."""
    return project_root() / "dataset" / filename

# --------------------------------------------------------------------------------------
# INTERNAL HELPERS
# --------------------------------------------------------------------------------------
def _apply_schema_adapter(df: pd.DataFrame) -> pd.DataFrame:
    """
    If the incoming CSV uses alias column names (e.g., 'country' instead of 'geography'),
    rename them here once so downstream code stays stable.
    """
    if SCHEMA_ADAPTER:
        # Only rename keys that actually exist in df
        rename_map = {src: dst for src, dst in SCHEMA_ADAPTER.items() if src in df.columns}
        if rename_map:
            df = df.rename(columns=rename_map)
    return df

def _coerce_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Trim string columns
    - Normalize common categoricals (UPPER / Title case) for consistent matching
    - Coerce numerics with errors='coerce' (bad values -> NaN to be imputed)
    """
    df = df.copy()

    # Trim/normalize strings
    for c, dt in EXPECTED_COLS.items():
        if dt == "string":
            df[c] = df[c].astype("string").str.strip()

    # Standardize common categoricals for reliable equality checks later
    df["geography"]    = df["geography"].str.upper()   # 'in', 'In' -> 'IN'
    df["language"]     = df["language"].str.title()    # 'english' -> 'English'
    df["topic"]        = df["topic"].str.strip()
    df["category_tag"] = df["category_tag"].str.strip()

    # Coerce numerics; invalid strings -> NaN (we will impute below)
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

def _impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Text/categorical: fill with empty string / 'Unknown'
    - Numeric: fill with median (robust to outliers vs. mean)
    """
    df = df.copy()

    # Text/categorical fallbacks
    df["recent_video_transcript"] = df["recent_video_transcript"].fillna("")
    for c in ["topic", "geography", "language", "category_tag"]:
        df[c] = df[c].fillna("Unknown")

    # Numeric: median is safer for heavy-tailed distributions
    for c in NUM_COLS:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())

    return df

def _apply_business_guards(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Enforce business logic specific to CreatorFit problem:
      - qualified_leads <= leads <= clicks
      - enrollments <= qualified_leads  
      - refunds <= enrollments
      - Calculate CPL (Cost Per Lead) ranges for analysis
      - Flag brand safety issues
    """
    df = df.copy()
    fix_counts: Dict[str, int] = {}

    def clip_le(a: str, b: str, key: str):
        """Ensure column a <= column b by clipping a down to b where violated."""
        mask = df[a] > df[b]
        n = int(mask.sum())
        if n:
            df.loc[mask, a] = df.loc[mask, b]
        fix_counts[key] = n

    # CreatorFit specific business constraints
    clip_le("leads", "clicks", "leads>clicks")
    clip_le("qualified_leads", "leads", "qualified_leads>leads")
    clip_le("enrollments", "qualified_leads", "enrollments>qualified_leads")
    clip_le("refunds", "enrollments", "refunds>enrollments")

    # Problem statement specific: CPL ranges from ₹700 to ₹3,200
    # Add conversion rate metrics for diagnosis
    df["click_rate"] = np.where(df["views_90d"] > 0, df["clicks"] / df["views_90d"], 0)
    df["lead_rate"] = np.where(df["clicks"] > 0, df["leads"] / df["clicks"], 0)
    df["qualification_rate"] = np.where(df["leads"] > 0, df["qualified_leads"] / df["leads"], 0)
    df["enrollment_rate"] = np.where(df["qualified_leads"] > 0, df["enrollments"] / df["qualified_leads"], 0)
    
    # Reasonable ranges for creator metrics
    df["posting_cadence_days"] = df["posting_cadence_days"].clip(lower=0.5, upper=60)
    for c in ["views_90d","clicks","leads","qualified_leads","enrollments","refunds"]:
        df[c] = df[c].clip(lower=0)

    return df, fix_counts

def _fold_rare_categories(
    df: pd.DataFrame,
    cols: Tuple[str, ...] = ("topic", "category_tag"),
    min_count: int = 0,
) -> pd.DataFrame:
    """
    (Optional) Consolidate very rare categories to 'Other' to reduce modeling noise.
    Disabled by default (min_count=0). Set, e.g., min_count=10 to enable.
    """
    if min_count <= 0:
        return df

    df = df.copy()
    for col in cols:
        vc = df[col].value_counts(dropna=False)
        rare = vc[vc < min_count].index
        if len(rare) > 0:
            df[col] = df[col].where(~df[col].isin(rare), other="Other")
    return df

# --------------------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# --------------------------------------------------------------------------------------
def load_and_clean_data(
    raw_filename: str = "creator_campaign_audience.csv",
    cleaned_filename: str = "creator_campaign_audience.cleaned.csv",
    *,
    rare_min_count: int = 0,  # set to e.g. 10 later if you want to fold rare categories
) -> Tuple[pd.DataFrame, Dict[str, int], Path]:
    """
    Load CSV, adapt schema (optional), validate required columns, normalize, impute,
    enforce guards, optionally fold rare categories, and save a cleaned CSV.

    Returns:
      clean_df:     cleaned DataFrame
      fix_report:   dict of how many constraint fixes were applied
      cleaned_path: Path to the saved cleaned CSV
    """
    raw_path = dataset_path(raw_filename)
    if not raw_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {raw_path}")

    # Read with no dtype coercion (be forgiving first)
    df_raw = pd.read_csv(raw_path)

    # Optional one-time column renames (schema adapter)
    df_raw = _apply_schema_adapter(df_raw)

    # Check schema presence
    missing = [c for c in EXPECTED_COLS if c not in df_raw.columns]
    extra   = [c for c in df_raw.columns if c not in EXPECTED_COLS]
    if missing:
        # Hard fail if required columns are missing
        raise ValueError(f"CSV is missing required columns: {missing}")
    if extra:
        # Not fatal: keep extras, but surface them so you’re aware
        print(f"[WARN] Unexpected columns present (kept as-is): {extra}")

    # Normalize strings + coerce numerics
    df = _coerce_and_normalize(df_raw)

    # Quick health snapshot (pre-impute)
    null_report = df.isna().sum().sort_values(ascending=False)
    dup_creators = int(df.duplicated(subset=["creator_id"]).sum())
    if dup_creators:
        # Not necessarily a problem (one creator can have multiple rows),
        # but useful to know for group-aware splitting later.
        print(f"[INFO] Duplicate creator_id rows: {dup_creators} (OK if multiple rows per creator)")

    # Impute missing + apply hard guards
    df = _impute_missing(df)
    df, fix_report = _apply_business_guards(df)

    # (Optional) fold rare categories to "Other" to stabilize modeling
    df = _fold_rare_categories(df, cols=("topic", "category_tag"), min_count=rare_min_count)

    # Save cleaned artifact (idempotent)
    cleaned_path = dataset_path(cleaned_filename)
    df.to_csv(cleaned_path, index=False)

    # Console summary: helps when switching to new CSVs
    print(f"[OK] Raw shape: {df_raw.shape} -> Cleaned: {df.shape}")
    print(f"[OK] Cleaned dataset saved to: {cleaned_path}")
    if null_report.sum() > 0:
        print("[INFO] Nulls before impute (top 10):\n", null_report.head(10))
    print("[INFO] Constraint fixes:", fix_report)

    return df, fix_report, cleaned_path

# Allow running this module directly for a quick cleaning pass
if __name__ == "__main__":
    # Example: enable rare-category folding at threshold 10
    load_and_clean_data(rare_min_count=0)
