# problems/creatorfit/features.py
from __future__ import annotations

from typing import Tuple, Dict, List, Optional, Iterable

import numpy as np
import pandas as pd

# Handle sentence transformers import gracefully
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] SentenceTransformers not available: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# --------------------------------------------------------------------------------------
# EDTECH FEATURE ENGINEERING CONFIG
# --------------------------------------------------------------------------------------
# Reusable default model (good quality + fast). You can override from train.py if needed.
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Simple in-process cache so repeated calls don't re-load the model from disk/network.
# This avoids slowdowns when you run train.py multiple times.
_MODEL_CACHE: Dict[str, any] = {}

# EdTech-specific topics for content validation (imported from data_preprocessing)
EDTECH_TOPICS = [
    "Python", "Data Science", "Machine Learning", "JavaScript", "React",
    "Node.js", "SQL", "Frontend Development", "Backend Development", 
    "Web Development", "Mobile Development", "DevOps", "Cloud Computing",
    "Artificial Intelligence", "Deep Learning", "Analytics", "Database",
    "Career Guidance", "Interview Preparation", "System Design"
]

# Odin School program descriptions for fit scoring
ODIN_SCHOOL_PROGRAMS = {
    "data_science": "Learn Python programming, statistics, machine learning, deep learning, data analysis, visualization with pandas, numpy, scikit-learn, tensorflow for data science career",
    "web_development": "Master HTML, CSS, JavaScript, React, Node.js, databases, APIs, full-stack web development for frontend backend programming career",
    "python_programming": "Complete Python programming course covering basics, advanced concepts, data structures, algorithms, web frameworks, automation, career guidance",
    "career_guidance": "Technical interview preparation, system design, coding practice, resume building, job search strategies for software engineering careers"
}


def _get_emb_model(name: str):
    """Return a cached SentenceTransformer instance for the given model name."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
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
def add_audience_and_exposure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add EdTech-specific audience and exposure features:
      - creator_tier: Established/Growing/Emerging based on views
      - language_diversity: Multi-language creators (English+Hindi+Telugu)
      - india_focused: All creators are INDIA-focused (always 1)
      - log_views_90d: stabilized exposure (log1p of views_90d)
    NOTE: assumes df is already cleaned in preprocessing with INDIA-only data.
    """
    df = df.copy()

    # EdTech creator tier classification (based on realistic view ranges)
    def classify_creator_tier(views):
        if views >= 100000:  # 1L+ views
            return "Established"
        elif views >= 25000:  # 25K-1L views  
            return "Growing"
        else:  # <25K views
            return "Emerging"
    
    df["creator_tier"] = df["views_90d"].apply(classify_creator_tier)
    
    # Geographic focus: All creators are INDIA-focused (always 1 for our EdTech dataset)
    df["india_focused"] = 1
    
    # Language diversity scoring (English is premium, Hindi/Telugu are regional)
    language_scores = {"English": 1.0, "Hindi": 0.8, "Telugu": 0.7}
    df["language_score"] = df["language"].map(language_scores).fillna(0.5)
    
    # Stabilized view metrics for ML (log-transform reduces skewness)
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
    emb_model_name: str = DEFAULT_EMBEDDING_MODEL,
    model = None,
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
    if emb is None:
        # Fallback: use simple text matching for similarity
        program_words = set(program_text.lower().split())
        cos = np.array([
            len(program_words.intersection(set(str(text).lower().split()))) / (len(program_words) + 1)
            for text in texts
        ])
    else:
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
    program_type: str = "data_science",
    emb_model_name: str = DEFAULT_EMBEDDING_MODEL,
    model = None,
) -> Tuple[pd.DataFrame, pd.Series, Dict[str, List[str]]]:
    """
    Build EdTech-specific features for predicting qualified leads.
    
    EdTech CreatorFit features:
      - Content-program fit score (semantic similarity with Odin School programs)
      - Creator tier classification (Established/Growing/Emerging)  
      - Language scoring (English premium, Hindi/Telugu regional)
      - Educational content validation
      - Posting consistency and engagement metrics

    Returns pre-booking features only (no data leakage).
    """
    # 1) Add EdTech-specific audience & exposure features
    df = add_audience_and_exposure(df_clean)

    # 2) Get Odin School program description for fit scoring
    if program_type not in ODIN_SCHOOL_PROGRAMS:
        program_type = "data_science"  # Default fallback
    program_text = ODIN_SCHOOL_PROGRAMS[program_type]

    # 3) Semantic content fit score with Odin School programs
    df["fit_score"] = compute_fit_scores(
        df=df,
        program_text=program_text,
        emb_model_name=emb_model_name,
        model=model,
        to_unit_interval=True,
    )
    
    # 4) EdTech-specific features for CPL optimization
    # Educational content validation (using our specific topics)
    edtech_pattern = "|".join(EDTECH_TOPICS)
    df["is_educational"] = df["topic"].str.contains(
        edtech_pattern, case=False, na=False
    ).astype(int)
    
    # Content quality and depth indicators
    df["transcript_length"] = df["recent_video_transcript"].str.len()
    df["topic_count"] = df["topic"].str.count(";") + 1  # Multi-topic expertise
    df["category_count"] = df["category_tag"].str.count(";") + 1
    
    # Creator consistency and activity scoring
    df["posting_frequency_score"] = 1.0 / (df["posting_cadence_days"] + 0.1)  # Higher freq = higher score
    
    # Topic expertise depth (bonus for multiple EdTech topics)
    df["edtech_topic_depth"] = df["topic"].apply(
        lambda x: sum(1 for topic in EDTECH_TOPICS if topic.lower() in x.lower())
    )

    # 5) Define EdTech feature contract (pre-booking signals only)
    numeric = [
        "fit_score",               # Content-program alignment (CORE)
        "posting_cadence_days",    # Creator consistency  
        "views_90d",              # Audience reach
        "log_views_90d",          # Stabilized reach
        "india_focused",          # Geographic focus (always 1)
        "language_score",         # Language premium scoring
        "is_educational",         # EdTech content validation
        "transcript_length",      # Content depth
        "topic_count",            # Content diversity
        "category_count",         # Category breadth
        "posting_frequency_score", # Activity level
        "edtech_topic_depth"      # Topic expertise depth
    ]
    categorical = ["topic", "category_tag", "creator_tier", "language"]
    target = "qualified_leads"

    # 6) Prevent data leakage - exclude post-campaign outcomes
    leakage_cols = {"clicks", "leads", "qualified_leads", "enrollments", "refunds", 
                   "click_rate", "lead_rate", "qualification_rate", "enrollment_rate"}
    feature_cols = set(numeric + categorical)
    if feature_cols & leakage_cols:
        raise ValueError(f"Data leakage detected! Features overlap with outcomes: {feature_cols & leakage_cols}")

    # 7) Build final feature matrix
    X = df[numeric + categorical].copy()
    y = df[target].astype(float).copy()

    # 8) Quality checks
    if X.isna().any().any():
        nan_cols = X.columns[X.isna().any()].tolist()
        raise ValueError(f"Missing values in features: {nan_cols}")

    # 9) EdTech-specific reporting
    established_creators = (df["creator_tier"] == "Established").sum()
    english_creators = (df["language"] == "English").sum()
    educational_creators = df["is_educational"].sum()
    
    print(f"[EDTECH] Built {len(numeric)} numeric + {len(categorical)} categorical features")
    print(f"[EDTECH] Creator tiers: {df['creator_tier'].value_counts().to_dict()}")
    print(f"[EDTECH] Educational content: {educational_creators}/{len(df)} ({educational_creators/len(df)*100:.1f}%)")
    print(f"[EDTECH] Language distribution: {df['language'].value_counts().to_dict()}")
    print(f"[EDTECH] Average fit score: {df['fit_score'].mean():.3f}")

    meta = {"numeric": numeric, "categorical": categorical, "target": target}
    return X, y, meta
