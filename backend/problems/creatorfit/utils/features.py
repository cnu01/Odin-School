from __future__ import annotations
import re
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

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

_MODEL_CACHE: Dict[str, any] = {}

EDTECH_TOPICS = [
    "Python", "Data Science", "Machine Learning", "JavaScript", "React",
    "Node.js", "SQL", "Frontend Development", "Backend Development", 
    "Web Development", "Mobile Development", "DevOps", "Cloud Computing",
    "Artificial Intelligence", "Deep Learning", "Analytics", "Database",
    "Career Guidance", "Interview Preparation", "System Design"
]

ODIN_SCHOOL_PROGRAMS = {
    "data_science": """
    Data science programming tutorial covering Python basics, pandas dataframes, 
    machine learning algorithms, statistics concepts, data visualization, 
    deep learning neural networks, career advice for data scientists
    """,
    "web_development": """
    Web development tutorial teaching HTML CSS basics, JavaScript programming,
    React components, Node.js backend, database integration, full-stack projects,
    frontend backend development career guidance
    """,
    "python_programming": """
    Complete Python programming bootcamp covering basics syntax variables functions,
    object-oriented programming classes inheritance, data structures lists dictionaries,
    algorithms problem solving, web frameworks Django Flask, automation scripting,
    testing debugging, project development, Python developer career advice
    """,
    "career_guidance": """
    Technical career guidance covering software engineering interview preparation,
    coding practice algorithms data structures, system design concepts,
    resume building portfolio development, job search strategies,
    salary negotiation, career progression in tech industry
    """
}

def truncate_text(text: str, max_tokens: int = 128) -> str:
    """
    Truncate text while preserving semantic integrity.
    Keeps beginning and end to maintain context.
    """
    words = text.split()
    if len(words) <= max_tokens:
        return text
    
    # Keep first 60% and last 40% to preserve context
    first_part = int(max_tokens * 0.6)
    last_part = max_tokens - first_part
    
    truncated = words[:first_part] + words[-last_part:]
    return ' '.join(truncated)

def _get_emb_model(name: str):
    """Return a cached SentenceTransformer instance for the given model name."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ValueError("SentenceTransformers library is not available.")

    if name not in _MODEL_CACHE:
        _MODEL_CACHE.clear()  # Clear the cache to avoid conflicts
        _MODEL_CACHE[name] = SentenceTransformer(name)
    else:
        print(f"[INFO] Using cached model: {name}")

    return _MODEL_CACHE[name]

def _normalize_text_series(s: pd.Series) -> pd.Series:
    """
    text preprocessing for better semantic matching.
    """
    def clean_text(text: str) -> str:
        if not text or pd.isna(text):
            return ""
        
        text = str(text).lower()
        
        text = re.sub(r'\s+', ' ', text)
        
        text = re.sub(r'\b(um|uh|like|you know|basically|actually)\b', '', text)
        
        # Remove special characters but keep punctuation for context
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
        return text.strip()
    
    return s.apply(clean_text)


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
    emb_model_name = DEFAULT_EMBEDDING_MODEL,
    model = None,
    batch_size: int = 256,
) -> pd.Series:
    """
    Compute semantic Fit Score between each creator transcript and the program description.
    """
    if not isinstance(program_text, str) or not program_text.strip():
        raise ValueError("program_text must be a non-empty string.")

    texts = _normalize_text_series(df["recent_video_transcript"])

    program_text_truncated = truncate_text(program_text, max_tokens=128)
    texts_truncated = texts.apply(lambda x: truncate_text(x, max_tokens=128))

    emb = model or _get_emb_model(emb_model_name)
    if emb is None:
        raise ValueError("Embedding model is not available.")

    # Encode program text and creator transcripts
    # prog_vec = _encode_texts([program_text], emb, batch_size=1, normalize=True)  # (1, d)
    # creator_mat = _encode_texts(texts, emb, batch_size=batch_size, normalize=True)  # (N, d)

    prog_vec = _encode_texts([program_text_truncated], emb, batch_size=1, normalize=True)
    creator_mat = _encode_texts(texts_truncated, emb, batch_size=batch_size, normalize=True)

    cos = (creator_mat @ prog_vec.T).ravel()

    actual_min, actual_max = cos.min(), cos.max()

    if actual_min < 0:
        cos = (cos - actual_min) / (actual_max - actual_min)

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
    )
    
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
