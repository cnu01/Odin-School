from __future__ import annotations

from typing import Tuple, Dict, List, Optional, Iterable

import numpy as np
import pandas as pd

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] SentenceTransformers not available: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_MODEL_CACHE: Dict[str, any] = {}

EDTECH_TOPICS = [
    "Python", "Data Science", "Machine Learning", "JavaScript", "React",
    "Node.js", "SQL", "Frontend Development", "Backend Development", 
    "Web Development", "Mobile Development", "DevOps", "Cloud Computing",
    "Artificial Intelligence", "Deep Learning", "Analytics", "Database",
    "Career Guidance", "Interview Preparation", "System Design"
]

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

def _normalize_text_series(s: pd.Series) -> pd.Series:
    """
    Basic cleanup for transcript text.
    """
    return s.fillna("").astype(str).str.strip()


def add_audience_and_exposure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add EdTech-specific audience and exposure features:
      - creator_tier: Established/Growing/Emerging based on views
      - language_diversity: Multi-language creators (English+Hindi+Telugu)
      - india_focused: All creators are INDIA-focused (always 1)
      - log_views_90d: stabilized exposure (log1p of views_90d)
    """
    df = df.copy()

    def classify_creator_tier(views):
        if views >= 100000:
            return "Established"
        elif views >= 25000:
            return "Growing"
        else:
            return "Emerging"
    
    df["creator_tier"] = df["views_90d"].apply(classify_creator_tier)
    
    df["india_focused"] = 1
    
    language_scores = {"English": 1.0, "Hindi": 0.8, "Telugu": 0.7}
    df["language_score"] = df["language"].map(language_scores).fillna(0.5)
    
    # Stabilized view metrics for ML (log-transform reduces skewness)
    df["log_views_90d"] = np.log1p(df["views_90d"].clip(lower=0))

    return df

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

    texts = _normalize_text_series(df["recent_video_transcript"])

    emb = model or _get_emb_model(emb_model_name)

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


def build_features(
    df_clean: pd.DataFrame,
    program_type: str = "data_science",
    emb_model_name: str = DEFAULT_EMBEDDING_MODEL,
    model = None,
) -> Tuple[pd.DataFrame, pd.Series, Dict[str, List[str]]]:
    """
    Build EdTech-specific features for predicting qualified leads.
    
    EdTech CreatorFit features:
      - Content-program fit score (semantic similarity with APEX AI programs)
      - Creator tier classification (Established/Growing/Emerging)  
      - Language scoring (English premium, Hindi/Telugu regional)
      - Educational content validation
      - Posting consistency and engagement metrics

    Returns pre-booking features only (no data leakage).
    """
    df = add_audience_and_exposure(df_clean)

    if program_type not in ODIN_SCHOOL_PROGRAMS:
        program_type = "data_science"  # Default fallback
    program_text = ODIN_SCHOOL_PROGRAMS[program_type]

    df["fit_score"] = compute_fit_scores(
        df=df,
        program_text=program_text,
        emb_model_name=emb_model_name,
        model=model,
        to_unit_interval=True,
    )
    
    # EdTech-specific features for CPL optimization
    # Educational content validation (using our specific topics)
    edtech_pattern = "|".join(EDTECH_TOPICS)
    df["is_educational"] = df["topic"].str.contains(
        edtech_pattern, case=False, na=False
    ).astype(int)
    
    # Content quality and depth indicators
    df["transcript_length"] = df["recent_video_transcript"].str.len()
    df["topic_count"] = df["topic"].str.count(";") + 1  # Multi-topic expertise
    df["category_count"] = df["category_tag"].str.count(";") + 1
    
    df["posting_frequency_score"] = 1.0 / (df["posting_cadence_days"] + 0.1)
    
    df["edtech_topic_depth"] = df["topic"].apply(
        lambda x: sum(1 for topic in EDTECH_TOPICS if topic.lower() in x.lower())
    )

    # Define EdTech feature contract (pre-booking signals only)
    numeric = [
        "fit_score",          
        "posting_cadence_days",  
        "views_90d",             
        "log_views_90d",         
        "india_focused",         
        "language_score",        
        "is_educational",         
        "transcript_length",      
        "topic_count",            
        "category_count",         
        "posting_frequency_score",
        "edtech_topic_depth"      # Topic expertise depth
    ]
    categorical = ["topic", "category_tag", "creator_tier", "language"]
    target = "qualified_leads"

    leakage_cols = {"clicks", "leads", "qualified_leads", "enrollments", "refunds", 
                   "click_rate", "lead_rate", "qualification_rate", "enrollment_rate"}
    feature_cols = set(numeric + categorical)
    if feature_cols & leakage_cols:
        raise ValueError(f"Data leakage detected! Features overlap with outcomes: {feature_cols & leakage_cols}")

    # Build final feature matrix
    X = df[numeric + categorical].copy()
    y = df[target].astype(float).copy()

    # Quality checks
    if X.isna().any().any():
        nan_cols = X.columns[X.isna().any()].tolist()
        raise ValueError(f"Missing values in features: {nan_cols}")

    meta = {"numeric": numeric, "categorical": categorical, "target": target}
    return X, y, meta
