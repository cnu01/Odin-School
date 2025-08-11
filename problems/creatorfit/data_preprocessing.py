# problems/creatorfit/data_preprocessing.py
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional

# --------------------------------------------------------------------------------------
# EDTECH CREATOR SCHEMA CONTRACT
# --------------------------------------------------------------------------------------
# Required columns for EdTech creator campaign data
EXPECTED_COLS = {
    "creator_id": "string",           # EDU_0001 format
    "topic": "string",                # Python;Data Science (EdTech topics only)
    "recent_video_transcript": "string", # Educational content description
    "posting_cadence_days": "int64",  # Integer days between posts (1, 2, 3...)
    "views_90d": "int64",            # 90-day view count (realistic EdTech range)
    "clicks": "int64",               # Click count from views
    "leads": "int64",                # Leads generated from clicks
    "qualified_leads": "int64",      # Qualified leads (target variable)
    "enrollments": "int64",          # Course enrollments from qualified leads
    "refunds": "int64",              # Refunds from enrollments
    "geography": "string",           # INDIA only for focused market
    "language": "string",            # English/Hindi/Telugu
    "category_tag": "string",        # Educational content categories
}

# Numeric columns for EdTech creator metrics
NUM_COLS = [
    "posting_cadence_days",  # Integer days between posts
    "views_90d",            # 90-day view count
    "clicks",               # Click-through from views
    "leads",                # Leads from clicks
    "qualified_leads",      # Qualified leads (PRIMARY TARGET)
    "enrollments",          # Course enrollments
    "refunds"               # Refunds from enrollments
]

# EdTech-specific validation rules
EDTECH_TOPICS = [
    "Python", "Data Science", "Machine Learning", "JavaScript", "React",
    "Node.js", "SQL", "Frontend Development", "Backend Development",
    "Web Development", "Mobile Development", "DevOps", "Cloud Computing",
    "Artificial Intelligence", "Deep Learning", "Analytics", "Database",
    "Career Guidance", "Interview Preparation", "System Design"
]

VALID_LANGUAGES = ["English", "Hindi", "Telugu"]
VALID_GEOGRAPHY = ["INDIA"]

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
    EdTech-specific data cleaning and normalization:
    - Validate creator IDs follow EDU_XXXX format
    - Ensure geography is INDIA only
    - Validate languages are English/Hindi/Telugu
    - Clean and validate EdTech topics
    - Coerce all metrics to proper integer types
    """
    df = df.copy()

    # Trim/normalize string columns
    for c, dt in EXPECTED_COLS.items():
        if dt == "string" and c in df.columns:
            df[c] = df[c].astype("string").str.strip()

    # EdTech-specific normalization
    # 1. Geography: Should only be INDIA for focused market
    df["geography"] = df["geography"].str.upper().str.strip()
    
    # 2. Language: Standardize to Title case
    df["language"] = df["language"].str.title().str.strip()
    
    # 3. Topics: Clean and validate EdTech topics
    df["topic"] = df["topic"].str.strip()
    
    # 4. Category tags: Clean educational content categories
    df["category_tag"] = df["category_tag"].str.strip()
    
    # 5. Creator ID: Should follow EDU_XXXX format
    df["creator_id"] = df["creator_id"].str.strip()
    
    # 6. Transcript: Clean educational content descriptions
    df["recent_video_transcript"] = df["recent_video_transcript"].str.strip()

    # Coerce numeric columns to proper types
    for c in NUM_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            # Ensure integers for count columns
            if c != "posting_cadence_days":  # Keep cadence as float initially
                df[c] = df[c].fillna(0).astype(int)

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
    Apply EdTech-specific business logic and validation:
    - Enforce funnel constraints: views → clicks → leads → qualified → enrollments
    - Validate EdTech-specific ranges and metrics
    - Flag data quality issues for educational platform
    - Ensure geographic and language consistency
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

    def validate_range(col: str, min_val: int, max_val: int, key: str):
        """Validate column values are within reasonable range."""
        if col in df.columns:
            before_count = len(df)
            df[col] = df[col].clip(lower=min_val, upper=max_val)
            fix_counts[key] = before_count - len(df)

    # 1. FUNNEL CONSTRAINTS (Critical for EdTech business logic)
    clip_le("leads", "clicks", "leads>clicks")
    clip_le("qualified_leads", "leads", "qualified_leads>leads")
    clip_le("enrollments", "qualified_leads", "enrollments>qualified_leads")
    clip_le("refunds", "enrollments", "refunds>enrollments")

    # 2. EDTECH-SPECIFIC RANGES
    # Posting cadence: 1-14 days (educational content requires consistency)
    if "posting_cadence_days" in df.columns:
        df["posting_cadence_days"] = df["posting_cadence_days"].astype(int)  # Force integer
        df["posting_cadence_days"] = df["posting_cadence_days"].clip(lower=1, upper=14)
    
    # Views: Realistic range for reputed EdTech (1K to 2M)
    validate_range("views_90d", 1000, 2000000, "views_out_of_range")
    
    # Clicks: Should be reasonable percentage of views (0.1% to 10%)
    if "clicks" in df.columns and "views_90d" in df.columns:
        max_clicks = (df["views_90d"] * 0.1).astype(int)  # Max 10% CTR
        df["clicks"] = np.minimum(df["clicks"], max_clicks)
    
    # 3. GEOGRAPHY & LANGUAGE VALIDATION
    invalid_geo = ~df["geography"].isin(VALID_GEOGRAPHY)
    if invalid_geo.any():
        fix_counts["invalid_geography"] = int(invalid_geo.sum())
        df.loc[invalid_geo, "geography"] = "INDIA"  # Default to INDIA
    
    invalid_lang = ~df["language"].isin(VALID_LANGUAGES)
    if invalid_lang.any():
        fix_counts["invalid_language"] = int(invalid_lang.sum())
        df.loc[invalid_lang, "language"] = "English"  # Default to English
    
    # 4. TOPIC VALIDATION (Flag non-EdTech content)
    has_edtech_topic = df["topic"].str.contains("|".join(EDTECH_TOPICS), case=False, na=False)
    non_edtech_count = int((~has_edtech_topic).sum())
    if non_edtech_count > 0:
        fix_counts["non_edtech_topics"] = non_edtech_count
        # Don't auto-fix topics, just flag for review
    
    # 5. ENSURE NON-NEGATIVE VALUES
    for c in ["views_90d", "clicks", "leads", "qualified_leads", "enrollments", "refunds"]:
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

# --------------------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# --------------------------------------------------------------------------------------
def load_and_clean_data(
    raw_filename: str = "creator_campaign_audience_EDTECH.csv",
    cleaned_filename: str = "creator_campaign_audience_EDTECH.cleaned.csv",
    *,
    rare_min_count: int = 0,  # set to e.g. 5 for EdTech topic consolidation
) -> Tuple[pd.DataFrame, Dict[str, int], Path]:
    """
    Load and clean EdTech creator campaign data with business-specific validation.
    
    EdTech-specific cleaning includes:
    - Validate creator IDs follow EDU_XXXX format
    - Ensure geography is INDIA only (focused market)
    - Validate languages are English/Hindi/Telugu
    - Check topics are educational (Python, Data Science, etc.)
    - Enforce funnel constraints (views → clicks → leads → enrollments)
    - Validate realistic ranges for reputed EdTech platform

    Returns:
      clean_df:     cleaned DataFrame with EdTech validations
      fix_report:   dict of data quality issues found and fixed
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

    # EdTech-specific console summary
    print(f"[EDTECH] Raw shape: {df_raw.shape} -> Cleaned: {df.shape}")
    print(f"[EDTECH] Cleaned dataset saved to: {cleaned_path}")
    
    # EdTech validation summary
    edtech_creators = len(df)
    india_creators = (df["geography"] == "INDIA").sum()
    valid_languages = df["language"].isin(VALID_LANGUAGES).sum()
    
    print(f"[EDTECH] Geographic focus: {india_creators}/{edtech_creators} creators in INDIA ({india_creators/edtech_creators*100:.1f}%)")
    print(f"[EDTECH] Language distribution: {df['language'].value_counts().to_dict()}")
    print(f"[EDTECH] Valid languages: {valid_languages}/{edtech_creators} ({valid_languages/edtech_creators*100:.1f}%)")
    
    if null_report.sum() > 0:
        print("[INFO] Data quality issues found and fixed:")
        for issue, count in fix_report.items():
            if count > 0:
                print(f"  - {issue}: {count} cases")
    else:
        print("[EDTECH] ✅ No data quality issues found - dataset is clean!")
    
    # Show topic distribution for EdTech validation
    top_topics = df['topic'].value_counts().head(5)
    print(f"[EDTECH] Top 5 topics: {top_topics.to_dict()}")

    return df, fix_report, cleaned_path

# Allow running this module directly for a quick cleaning pass
if __name__ == "__main__":
    # Example: enable rare-category folding at threshold 10
    load_and_clean_data(rare_min_count=0)
