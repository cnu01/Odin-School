from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

EXPECTED_COLS = {
    "creator_id": "string",
    "topic": "string",
    "recent_video_transcript": "string",
    "posting_cadence_days": "int64",
    "views_90d": "int64",
    "clicks": "int64",
    "leads": "int64",
    "qualified_leads": "int64",
    "refunds": "int64",
    "language": "string",
    "category_tag": "string",
}

NUMERIC_COLS = [
    "posting_cadence_days",
    "views_90d",
    "clicks",
    "leads",
    "qualified_leads",
]

EDTECH_TOPICS = [
    "Python", "Data Science", "Machine Learning", "JavaScript", "React",
    "Node.js", "SQL", "Frontend Development", "Backend Development",
    "Web Development", "Mobile Development", "DevOps", "Cloud Computing",
    "Artificial Intelligence", "Deep Learning", "Analytics", "Database",
    "Career Guidance", "Interview Preparation", "System Design"
]

VALID_LANGUAGES = ["English", "Hindi", "Telugu"]

def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def dataset_path(filename: str) -> Path:
    return project_root() / "dataset" / filename

def _coerce_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Trim/normalize string columns
    for c, dt in EXPECTED_COLS.items():
        if dt == "string" and c in df.columns:
            df[c] = df[c].astype("string").str.strip()

    df["language"] = df["language"].str.title().str.strip()
    df["topic"] = df["topic"].str.strip()
    df["category_tag"] = df["category_tag"].str.strip()
    df["creator_id"] = df["creator_id"].str.strip()
    df["recent_video_transcript"] = df["recent_video_transcript"].str.strip()

    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            if c != "posting_cadence_days":
                df[c] = df[c].fillna(0).astype(int)

    return df

def _remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    initial_rows = len(df)
    
    # Critical columns that must have valid values
    critical_checks = {
        'views_90d': lambda x: (x > 0) & (x.notna()),
        'clicks': lambda x: (x >= 0) & (x.notna()),
        'posting_cadence_days': lambda x: (x > 0) & (x.notna()),
        'recent_video_transcript': lambda x: (x.str.len() > 0) & (x.notna())
    }

    # Apply all critical checks
    valid_mask = pd.Series(True, index=df.index)
    for col, check_func in critical_checks.items():
        if col in df.columns:
            valid_mask = valid_mask & check_func(df[col])
    
    # Remove invalid rows
    df_cleaned = df[valid_mask].copy()
    
    removed_rows = initial_rows - len(df_cleaned)
    if removed_rows > 0:
        print(f"[CLEANING] Removed {removed_rows} rows with invalid data in critical columns")
        print(f"[CLEANING] Dataset size: {initial_rows} → {len(df_cleaned)} rows")
    
    return df_cleaned

def _apply_minmax_scaling(df: pd.DataFrame) -> pd.DataFrame:
    from sklearn.preprocessing import MinMaxScaler
    
    df = df.copy()
    
    cols_to_scale = [
        'posting_cadence_days', 
        'views_90d', 
        'clicks', 
        'leads', 
        'qualified_leads', 
    ]
    
    existing_cols = [col for col in cols_to_scale if col in df.columns]
    
    if existing_cols:
        print(f"[SCALING] Applying MinMax scaling to: {existing_cols}")
        
        scaler = MinMaxScaler()
        
        df[existing_cols] = scaler.fit_transform(df[existing_cols])
        
        print(f"[SCALING] MinMax scaling completed for {len(existing_cols)} columns")
    else:
        print("[SCALING] No columns found for scaling")
    
    return df

def _impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Text/categorical: fill with empty string / 'Unknown'
    - Numeric: fill with median (robust to outliers vs. mean)
    """
    df = df.copy()

    df["recent_video_transcript"] = df["recent_video_transcript"].fillna("")
    for c in ["topic", "language", "category_tag"]:
        df[c] = df[c].fillna("Unknown")

    creator_metrics = [
        "leads",
        "qualified_leads",
    ]
    
    for c in creator_metrics:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())

    return df

def _apply_business_guards(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    df = df.copy()
    fix_counts: Dict[str, int] = {}

    def clip_le(a: str, b: str, key: str):
        """Ensure column a <= column b by clipping a down to b where violated."""
        mask = df[a] > df[b]
        n = int(mask.sum())
        if n:
            df.loc[mask, a] = df.loc[mask, b]
        fix_counts[key] = n

    clip_le("leads", "clicks", "leads>clicks")
    clip_le("qualified_leads", "leads", "qualified_leads>leads")

    if "posting_cadence_days" in df.columns:
        df["posting_cadence_days"] = df["posting_cadence_days"].astype(int)
        df["posting_cadence_days"] = df["posting_cadence_days"].clip(lower=1, upper=14)
    
    if "views_90d" in df.columns:
        df["views_90d"] = df["views_90d"].clip(lower=1000, upper=2000000)
    
    if "clicks" in df.columns and "views_90d" in df.columns:
        max_clicks = (df["views_90d"] * 0.1).astype(int)
        df["clicks"] = np.minimum(df["clicks"], max_clicks)
    
    invalid_lang = ~df["language"].isin(VALID_LANGUAGES)
    
    if invalid_lang.any():
        fix_counts["invalid_language"] = int(invalid_lang.sum())
        df.loc[invalid_lang, "language"] = "Unknown"
    
    has_edtech_topic = df["topic"].str.contains("|".join(EDTECH_TOPICS), case=False, na=False)
    
    non_edtech_count = int((~has_edtech_topic).sum())
    if non_edtech_count > 0:
        fix_counts["non_edtech_topics"] = non_edtech_count
    
    for c in ["views_90d", "clicks", "leads", "qualified_leads"]:
        if c in df.columns:
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

def load_and_clean_data(
    raw_filename: str = "creator_campaign_audience.csv",
    cleaned_filename: str = "creator_campaign_audience.cleaned.csv",
    *,
    rare_min_count: int = 0,
) -> Tuple[pd.DataFrame, Dict[str, int], Path]:
    raw_path = dataset_path(raw_filename)

    if not raw_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {raw_path}")

    df_raw = pd.read_csv(raw_path)

    missing = [c for c in EXPECTED_COLS if c not in df_raw.columns]

    extra = [c for c in df_raw.columns if c not in EXPECTED_COLS]

    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")
    if extra:
        print(f"[WARN] Unexpected columns present (kept as-is): {extra}")

    df = _coerce_and_normalize(df_raw)

    df = _remove_invalid_rows(df)

    null_report = df.isna().sum().sort_values(ascending=False)

    dup_creators = int(df.duplicated(subset=["creator_id"]).sum())
    if dup_creators:
        print(f"[INFO] Duplicate creator_id rows: {dup_creators} (OK if multiple rows per creator)")

    df = _impute_missing(df)

    df, fix_report = _apply_business_guards(df)

    df = _fold_rare_categories(df, cols=("topic", "category_tag"), min_count=rare_min_count)

    df = _apply_minmax_scaling(df)

    df = df.drop(columns=['geography', 'creator_id'], errors='ignore')
    
    cleaned_path = dataset_path(cleaned_filename)
    df.to_csv(cleaned_path, index=False)
 
    if null_report.sum() > 0:
        print("[INFO] Data quality issues found and fixed:")
        for issue, count in fix_report.items():
            if count > 0:
                print(f"  - {issue}: {count} cases")
    else:
        print("[EDTECH] - No data quality issues found - dataset is clean!")
    
    top_topics = df['topic'].value_counts().head(5)
    print(f"[EDTECH] Top 5 topics: {top_topics.to_dict()}")

    return df, fix_report, cleaned_path

if __name__ == "__main__":
    load_and_clean_data(rare_min_count=0)
