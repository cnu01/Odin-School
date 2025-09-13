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
    "Career Guidance", "Interview Preparation", "System Design", "Django",
    "Programming Fundamentals", "C++", "Statistics", "Data Structures",
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

def _extract_text_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract text-based features BEFORE label encoding.
    These are critical for qualified leads prediction.
    """
    df = df.copy()
    
    print("[TEXT_FEATURES] Extracting text-based features for qualified leads prediction...")
    
    educational_keywords = [
        "tutorial", "learn", "course", "programming", "coding", 
        "development", "algorithm", "data", "analysis", "project",
        "training", "education", "teach", "explain", "guide"
    ]
    
    def calculate_educational_score(text):
        if pd.isna(text) or not text:
            return 0.0
        text_lower = str(text).lower()
        matches = sum(1 for keyword in educational_keywords if keyword in text_lower)
        return min(matches / len(educational_keywords), 1.0)  # Cap at 1.0
    
    df["educational_transcript_score"] = df["recent_video_transcript"].apply(calculate_educational_score)
    
    df["transcript_length"] = df["recent_video_transcript"].str.len().fillna(0)
    
    df["topic_count"] = (df["topic"].str.count(";") + 1).fillna(1)
    
    def calculate_edtech_depth(topic_text):
        if pd.isna(topic_text) or not topic_text:
            return 0
        topic_lower = str(topic_text).lower()
        return sum(1 for topic in EDTECH_TOPICS if topic.lower() in topic_lower)
    
    df["edtech_topic_depth"] = df["topic"].apply(calculate_edtech_depth)
    
    print(f"[TEXT_FEATURES] Educational transcript score - avg: {df['educational_transcript_score'].mean():.3f}")
    print(f"[TEXT_FEATURES] Transcript length - avg: {df['transcript_length'].mean():.0f} chars")
    print(f"[TEXT_FEATURES] Topic count - avg: {df['topic_count'].mean():.1f} topics")
    print(f"[TEXT_FEATURES] EdTech depth - avg: {df['edtech_topic_depth'].mean():.1f} matches")
    print("[TEXT_FEATURES] Text feature extraction completed successfully")
    
    return df

def _apply_label_encoding(df: pd.DataFrame) -> pd.DataFrame:
    from sklearn.preprocessing import LabelEncoder
    
    df = df.copy()
    
    categorical_columns = ['topic', 'language', 'category_tag']
    
    existing_cat_cols = [col for col in categorical_columns if col in df.columns]
    
    if not existing_cat_cols:
        print("[ENCODING] No categorical columns found for label encoding")
        return df
    
    print(f"[ENCODING] Applying label encoding to: {existing_cat_cols}")
    
    label_encoders = {}
    for col in existing_cat_cols:
        if df[col].notna().sum() > 0:  # Only if column has non-null values
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le
            
            print(f"[ENCODING] '{col}': {len(le.classes_)} unique categories encoded")
            print(f"[ENCODING] '{col}' categories: {le.classes_[:5]}...")  # Show first 5 categories
    
    print(f"[ENCODING] Label encoding completed for {len(existing_cat_cols)} columns")
    
    return df

def _apply_minmax_scaling(df: pd.DataFrame) -> pd.DataFrame:
    from sklearn.preprocessing import MinMaxScaler
    
    df = df.copy()
    
    cols_to_scale = [
        'posting_cadence_days', 
        'views_90d', 
        'clicks', 
        'leads', 
        'qualified_leads',
        'educational_transcript_score',
        'transcript_length',
        'topic_count',
        'edtech_topic_depth'
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
        df['views_90d'] = df['views_90d'].clip(lower=100)
        df["views_90d"] = df["views_90d"].clip(lower=5000, upper=2000000)
    
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
        
        df.loc[~has_edtech_topic, "topic"] = "Other"
        print(f"[BUSINESS] Replaced {non_edtech_count} non-EdTech topics with 'Other'")
    
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

    if null_report.sum() > 0:
        print(f"[INFO] Found null values before imputation:")
        for col, count in null_report[null_report > 0].items():
            print(f"  - {col}: {count} null values")

    dup_creators = int(df.duplicated(subset=["creator_id"]).sum())

    if dup_creators:
        print(f"[INFO] Found {dup_creators} duplicate creator_id rows - removing duplicates")
        df = df.drop_duplicates(subset=["creator_id"], keep='first')
        print(f"[INFO] Dataset size after removing duplicates: {len(df)} rows")
    else:
        print("[INFO] No duplicate creator_id rows found")

    df = _impute_missing(df)
    df, fix_report = _apply_business_guards(df)
    df = _fold_rare_categories(df, cols=("topic", "category_tag"), min_count=rare_min_count)
    df = _extract_text_features(df)
    df = _apply_label_encoding(df)
    df = _apply_minmax_scaling(df)
    df = df.drop(columns=['geography', 'enrollments', 'refunds'], errors='ignore')
    
    cleaned_path = dataset_path(cleaned_filename)
    df.to_csv(cleaned_path, index=False)
 
    # Final data quality report
    final_null_count = df.isna().sum().sum()
    if final_null_count > 0:
        print(f"[WARNING] {final_null_count} null values still present after imputation!")
    else:
        print("[SUCCESS] No null values remaining after imputation")
    
    if fix_report:
        print("[INFO] Business logic fixes applied:")
        for issue, count in fix_report.items():
            if count > 0:
                print(f"  - {issue}: {count} cases")
    else:
        print("[SUCCESS] No business logic fixes needed")
    
    top_topics = df['topic'].value_counts().head(5)
    print(f"[EDTECH] Top 5 topics: {top_topics.to_dict()}")

    return df, fix_report, cleaned_path

if __name__ == "__main__":
    load_and_clean_data(rare_min_count=0)
